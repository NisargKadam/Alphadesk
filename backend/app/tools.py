"""Desk tools. Session 03: filings search. Session 04 adds live market tools.

Everything the agent can *do* (beyond talking) lives in this file.
"""

import chromadb
from chromadb.config import Settings

_filings = None


def _collection():
    # Lazy singleton: the Chroma client only spins up (and loads the local
    # embedding model) the first time a filings question actually arrives.
    global _filings
    if _filings is None:
        client = chromadb.PersistentClient(
            path="./chroma_db", settings=Settings(anonymized_telemetry=False)
        )
        _filings = client.get_or_create_collection("filings")
    return _filings


def search_filings(query: str, k: int = 10) -> list[dict]:
    """Dense retrieval over the ingested filings: embed the query, return the
    k nearest chunks with the metadata a citation needs."""
    if _collection().count() == 0:
        return []  # nothing ingested yet — the caller says so, honestly
    result = _collection().query(query_texts=[query], n_results=k)
    return [
        {"text": doc, "source": meta["source"], "page": meta["page"]}
        for doc, meta in zip(result["documents"][0], result["metadatas"][0])
    ]
