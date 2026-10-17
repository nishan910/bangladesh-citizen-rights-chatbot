from pathlib import Path
import subprocess
import sys
import pymupdf

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PDF_PATH = PROJECT_ROOT / "data" / "raw" / "contract_act.pdf"
OUTPUT_DIR = PROJECT_ROOT / "data" / "processed" / "ocr"
TESSERACT = Path(r"C:\Program Files\Tesseract-OCR\tesseract.exe")
TESSDATA_DIR = Path.home() / "AppData" / "Local" / "Tesseract-OCR" / "tessdata"
DPI = 300


def main(max_pages=None):
    if not PDF_PATH.exists():
        raise FileNotFoundError(f"PDF not found: {PDF_PATH}")

    if not TESSERACT.exists():
        raise FileNotFoundError(f"Tesseract not found: {TESSERACT}")

    if not (TESSDATA_DIR / "ben.traineddata").exists():
        raise FileNotFoundError("Bengali OCR language data not found.")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with pymupdf.open(PDF_PATH) as document:
        total_pages = len(document)
        pages_to_process = min(total_pages, max_pages) if max_pages else total_pages
        print(f"PDF: {PDF_PATH.name}")
        print(f"Total pages: {total_pages}")
        print(f"Pages to process: {pages_to_process}")

        for page_number in range(1, pages_to_process + 1):
            page = document[page_number - 1]
            pixmap = page.get_pixmap(
                matrix=pymupdf.Matrix(DPI / 72, DPI / 72),
                alpha=False,
            )
            image_path = OUTPUT_DIR / f"page_{page_number:04d}.png"
            text_path = OUTPUT_DIR / f"page_{page_number:04d}.txt"

            try:
                pixmap.save(str(image_path))
                result = subprocess.run(
                    [
                        str(TESSERACT),
                        str(image_path),
                        "stdout",
                        "-l", "ben",
                        "--tessdata-dir", str(TESSDATA_DIR),
                    ],
                    check=True,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                )
                text_path.write_text(result.stdout, encoding="utf-8")
            finally:
                image_path.unlink(missing_ok=True)

            print(f"Processed page {page_number}/{pages_to_process}")

    print(f"OCR completed: {OUTPUT_DIR}")


if __name__ == "__main__":
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else None
    main(limit)
