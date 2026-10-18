import json
import subprocess
import tempfile
from pathlib import Path

import pymupdf

ROOT = Path(__file__).resolve().parents[2]
PDF_DIR = ROOT / "data" / "raw"
OUTPUT = ROOT / "data" / "processed" / "legal_pages.jsonl"
SOURCES = ROOT / "data" / "processed" / "legal_sources.json"

TESSERACT = Path(r"C:\Program Files\Tesseract-OCR\tesseract.exe")
TESSDATA_DIR = Path.home() / "AppData" / "Local" / "Tesseract-OCR" / "tessdata"
OCR_FILES = {
    "law_100_domestic_violence_act_2010.pdf":
        "পারিবারিক সহিংসতা (প্রতিরোধ ও সুরক্ষা) আইন, ২০১০",
    "law_101_children_act_2013.pdf":
        "শিশু আইন, ২০১৩",
}


def ocr_page(page, image_path):
    pix = page.get_pixmap(
        matrix=pymupdf.Matrix(300 / 72, 300 / 72),
        alpha=False,
    )
    pix.save(str(image_path))
    result = subprocess.run(
        [
            str(TESSERACT), str(image_path), "stdout",
            "-l", "ben",
            "--tessdata-dir", str(TESSDATA_DIR),
            "--psm", "3",
        ],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return result.stdout.strip()


def main():
    if not TESSERACT.exists():
        raise FileNotFoundError(f"Tesseract not found: {TESSERACT}")
    if not (TESSDATA_DIR / "ben.traineddata").exists():
        raise FileNotFoundError(f"Bengali OCR data not found: {TESSDATA_DIR}")

    sources = json.loads(SOURCES.read_text(encoding="utf-8"))
    records = []
    total_ocr_pages = 0

    with tempfile.TemporaryDirectory() as temp_dir:
        image_path = Path(temp_dir) / "ocr_page.png"

        for source in sources:
            pdf_name = source.get("local_pdf")
            if not pdf_name:
                continue

            pdf_path = PDF_DIR / pdf_name
            if not pdf_path.exists():
                print("Missing PDF:", pdf_name)
                continue

            use_ocr = pdf_name in OCR_FILES
            title = OCR_FILES.get(pdf_name, source["title"])
            print(f"Processing: {title} | OCR={use_ocr}")

            with pymupdf.open(pdf_path) as document:
                for page_number, page in enumerate(document, start=1):
                    if use_ocr:
                        text = ocr_page(page, image_path)
                        total_ocr_pages += 1
                    else:
                        text = page.get_text().strip()

                    if text:
                        records.append({
                            "title": title,
                            "page": page_number,
                            "source_url": source["pdf_url"],
                            "source_page": source["source_page"],
                            "text": text,
                        })

                    if use_ocr:
                        print(
                            f"\r  OCR page {page_number}/{len(document)}",
                            end="", flush=True
                        )
                if use_ocr:
                    print()

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", encoding="utf-8") as file:
        for record in records:
            file.write(json.dumps(record, ensure_ascii=False) + "\n")

    print("\nExtraction complete.")
    print("Page records:", len(records))
    print("OCR pages processed:", total_ocr_pages)
    print("Output:", OUTPUT)


if __name__ == "__main__":
    main()
