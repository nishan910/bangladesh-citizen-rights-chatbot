import json
import re
import time
from pathlib import Path
from urllib.parse import urlparse, unquote

import requests

ROOT = Path(__file__).resolve().parents[2]
SOURCES = ROOT / "data" / "processed" / "legal_sources.json"
PDF_DIR = ROOT / "data" / "raw"
MAX_FILE_BYTES = 50 * 1024 * 1024
TIMEOUT = (15, 60)


def save_sources(data):
    temp_path = SOURCES.with_suffix(".tmp")
    temp_path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    temp_path.replace(SOURCES)


def make_filename(index, source):
    url_name = Path(unquote(urlparse(source["pdf_url"]).path)).name
    safe_name = re.sub(r"[^A-Za-z0-9._-]", "_", url_name)

    if not safe_name.lower().endswith(".pdf"):
        safe_name = f"law_{index:03d}.pdf"

    return f"law_{index:03d}_{safe_name}"


def main(limit=3):
    PDF_DIR.mkdir(parents=True, exist_ok=True)
    data = json.loads(SOURCES.read_text(encoding="utf-8"))

    session = requests.Session()
    session.headers["User-Agent"] = "BangladeshCitizenRightsChatbot/0.1"

    success = 0
    skipped = 0
    failed = 0
    attempted = 0

    for index, source in enumerate(data, start=1):
        if attempted >= limit:
            break

        existing_name = source.get("local_pdf")
        if existing_name:
            existing_path = PDF_DIR / existing_name
            if existing_path.is_file() and existing_path.stat().st_size > 0:
                print(f"SKIP {index}: already downloaded - {existing_name}")
                skipped += 1
                continue

        attempted += 1
        filename = make_filename(index, source)
        destination = PDF_DIR / filename
        temporary = destination.with_suffix(".part")

        try:
            with session.get(
                source["pdf_url"],
                stream=True,
                timeout=TIMEOUT,
            ) as response:
                response.raise_for_status()

                content_type = response.headers.get("Content-Type", "").lower()
                if "text/html" in content_type:
                    raise ValueError("Server returned HTML instead of a PDF")

                content_length = response.headers.get("Content-Length")
                if content_length and int(content_length) > MAX_FILE_BYTES:
                    raise ValueError("PDF exceeds 50 MB limit")

                total = 0
                with temporary.open("wb") as output:
                    for chunk in response.iter_content(chunk_size=64 * 1024):
                        if not chunk:
                            continue
                        total += len(chunk)
                        if total > MAX_FILE_BYTES:
                            raise ValueError("PDF exceeds 50 MB limit")
                        output.write(chunk)

            with temporary.open("rb") as downloaded:
                signature = downloaded.read(5)

            if signature != b"%PDF-":
                raise ValueError("Downloaded file is not a valid PDF signature")

            if total < 1024:
                raise ValueError("File is unexpectedly small")

            temporary.replace(destination)
            source["local_pdf"] = filename
            save_sources(data)

            success += 1
            print(f"OK {index}: {source['title']} ({total:,} bytes)")

        except (requests.RequestException, ValueError, OSError) as error:
            failed += 1
            print(f"FAILED {index}: {source['title']} - {error}")
            temporary.unlink(missing_ok=True)

        time.sleep(0.5)

    print("\nBatch summary")
    print("New downloads:", success)
    print("Already present:", skipped)
    print("Failed:", failed)
    print("Attempted:", attempted)
    print("Source records:", len(data))


if __name__ == "__main__":
    import sys

    batch_size = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    if batch_size < 1:
        raise SystemExit("Batch size must be at least 1")
    main(batch_size)
