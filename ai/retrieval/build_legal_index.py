import json
import re
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer

ROOT = Path(__file__).resolve().parents[2]
INPUT_FILE = ROOT / "data" / "processed" / "legal_pages.jsonl"
DB_DIR = ROOT / "data" / "processed" / "chroma_db"

MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"
COLLECTION_NAME = "bangladesh_laws"
CHUNK_SIZE = 900
CHUNK_OVERLAP = 150
BATCH_SIZE = 64


def clean_text(text):
    text = text.replace("\x00", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def split_into_chunks(text, size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    text = clean_text(text)
    if not text:
        return []

    chunks = []
    start = 0

    while start < len(text):
        end = min(start + size, len(text))

        if end < len(text):
            boundary = max(
                text.rfind("।", start, end),
                text.rfind("\n", start, end),
                text.rfind(" ", start, end),
            )
            if boundary > start + size // 2:
                end = boundary + 1

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        if end >= len(text):
            break

        start = max(end - overlap, start + 1)

    return chunks


def main():
    if not INPUT_FILE.is_file():
        raise FileNotFoundError(f"Input file not found: {INPUT_FILE}")

    pages = []
    with INPUT_FILE.open("r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, 1):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as error:
                raise ValueError(
                    f"Invalid JSON on line {line_number}"
                ) from error

            if record.get("text", "").strip():
                pages.append(record)

    if not pages:
        raise ValueError("No non-empty legal page records found.")

    chunks = []
    for record in pages:
        for chunk_number, chunk_text in enumerate(
            split_into_chunks(record["text"]), 1
        ):
            chunks.append({
                "text": chunk_text,
                "metadata": {
                    "title": str(record["title"])[:500],
                    "page": int(record["page"]),
                    "source_url": str(record["source_url"]),
                    "source_page": str(record["source_page"])[:1000],
                    "chunk": chunk_number,
                },
            })

    print("Page records:", len(pages))
    print("Chunks created:", len(chunks))
    print("Loading embedding model:", MODEL_NAME)

    model = SentenceTransformer(MODEL_NAME)
    client = chromadb.PersistentClient(path=str(DB_DIR))

    # Rebuild this collection from the current source data.
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass

    collection = client.create_collection(
        name=COLLECTION_NAME,
        metadata={"description": "Page-cited Bangladesh legal documents"},
    )

    for start in range(0, len(chunks), BATCH_SIZE):
        batch = chunks[start:start + BATCH_SIZE]
        texts = [item["text"] for item in batch]
        embeddings = model.encode(
            texts,
            normalize_embeddings=True,
            show_progress_bar=False,
        ).tolist()

        ids = [
            f"law_chunk_{start + index:07d}"
            for index in range(len(batch))
        ]

        collection.add(
            ids=ids,
            documents=texts,
            metadatas=[item["metadata"] for item in batch],
            embeddings=embeddings,
        )

        print(f"Indexed {min(start + len(batch), len(chunks))}/{len(chunks)}")

    print("\nIndex build complete.")
    print("Collection:", COLLECTION_NAME)
    print("Stored chunks:", collection.count())
    print("Database:", DB_DIR)


if __name__ == "__main__":
    main()
