import chromadb
from chromadb.config import Settings

def _collections():
    global _filings
    if _filings is None:
        client = chromadb.PersistentClient(
            path="./chroma_db", settings=Settings(anonymized_telemetry=False)
        )
        _filings = client.get_or_create_collection("filings")

def search_filings(query: str, K: int = 10) -> list[dict]:
    if _collections().count() == 0:
        return []
    results = _collections().query(query_texts=[query], n_results=K)
    return [
        {"text": doc, "source": meta["source"], "page": meta["page"]}
        for doc, meta in zip(results["documents"][0], results["metadatas"][0])
    ]
