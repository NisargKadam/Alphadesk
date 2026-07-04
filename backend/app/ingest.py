"""Session 03: filings → chunks → Chroma.

Run from backend/:  python -m app.ingest ../data/filings

This is the offline half of RAG. The online half (search_filings in
tools.py + the retrieve node in graph.py) can only ever be as good as what
happens here — retrieval quality is decided at ingest time.
"""

import hashlib
import sys
from pathlib import Path

import chromadb
from chromadb.config import Settings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader

# ~900 chars ≈ a paragraph or two: big enough to hold one complete thought,
# small enough that a chunk stays on one topic. The 150-char overlap lets a
# sentence that straddles a boundary survive in at least one chunk. These are
# sane defaults, not truths — Session 05 compares strategies with numbers.
CHUNK_SIZE = 900
CHUNK_OVERLAP = 150

CHROMA_PATH = "./chroma_db"
COLLECTION = "filings"


def load_pages(path: Path) -> list[tuple[int, str]]:
    """Yield (page_number, text) — citations point at pages, so we keep them."""
    if path.suffix == ".pdf":
        return [(i + 1, page.extract_text() or "") for i, page in enumerate(PdfReader(path).pages)]
    # .txt files pass straight through; a form-feed (\f) marks a page break,
    # mirroring the PDF path so the sample document cites like a real filing.
    return [(i + 1, text) for i, text in enumerate(path.read_text().split("\f"))]


def main(folder: str) -> None:
    client = chromadb.PersistentClient(
        path=CHROMA_PATH, settings=Settings(anonymized_telemetry=False)
    )
    # Chroma's default embedding function runs locally (an ONNX MiniLM model,
    # downloaded on first use) — no API key, no per-chunk cost. Alternatives
    # and their trade-offs are a Session 05 discussion.
    collection = client.get_or_create_collection(COLLECTION)
    splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)

    ids, documents, metadatas = [], [], []
    for path in sorted(Path(folder).iterdir()):
        if path.suffix not in {".pdf", ".txt"} or path.name == "README.md":
            continue
        for page, text in load_pages(path):
            for chunk in splitter.split_text(text):
                # IDs derived from content make re-runs idempotent: an
                # unchanged chunk upserts onto itself instead of duplicating.
                ids.append(hashlib.sha1(f"{path.name}:{page}:{chunk}".encode()).hexdigest()[:16])
                documents.append(chunk)
                metadatas.append({"source": path.name, "page": page})
        print(f"ingested {path.name}")

    if not documents:
        sys.exit(f"No .pdf or .txt filings found in {folder}")
    collection.upsert(ids=ids, documents=documents, metadatas=metadatas)
    print(f"{len(documents)} chunks → {CHROMA_PATH} (collection '{COLLECTION}', {collection.count()} total)")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "../data/filings")
