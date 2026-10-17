import json
from pathlib import Path

import pymupdf

ROOT = Path(__file__).resolve().parents[2]
PDF_DIR = ROOT / "data" / "raw"
OUTPUT = ROOT / "data" / "processed" / "legal_pages.jsonl"
SOURCES = ROOT / "data" / "processed" / "legal_sources.json"


def main():
    sources = json.loads(SOURCES.read_text(encoding="utf-8"))
    records = []

    for source in sources:
        pdf_name = source.get("local_pdf")
        if not pdf_name:
            continue

        pdf_path = PDF_DIR / pdf_name
        if not pdf_path.exists():
            continue

        with pymupdf.open(pdf_path) as document:
            for page_number, page in enumerate(document, start=1):
                text = page.get_text().strip()
                if not text:
                    continue

                records.append({
                    "title": source["title"],
                    "page": page_number,
                    "source_url": source["pdf_url"],
                    "source_page": source["source_page"],
                    "text": text,
                })

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", encoding="utf-8") as file:
        for record in records:
            file.write(json.dumps(record, ensure_ascii=False) + "\n")

    print("Extracted page records:", len(records))
    print("Output:", OUTPUT)


if __name__ == "__main__":
    main()
