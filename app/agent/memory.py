# app/agent/memory.py

"""
Memory layer for the Agent.
Stores summarized knowledge into ChromaDB and retrieves it for RAG.
"""

from chromadb import Client
from sentence_transformers import SentenceTransformer


def get_vector_client():
    """Return ChromaDB client."""
    return Client()  # new API with default persistence


def get_embedder():
    """Return embedding model."""
    return SentenceTransformer("all-MiniLM-L6-v2")


def store_summary(collection_name: str, summary_text: str):
    """Embed and store summary into Chroma."""
    client = get_vector_client()
    embedder = get_embedder()

    collection = client.get_or_create_collection(name=collection_name)

    embedding = embedder.encode([summary_text]).tolist()[0]

    _id = collection.count()  # incremental ID
    collection.add(
        ids=[str(_id)],
        documents=[summary_text],
        embeddings=[embedding],
    )


def rag_retrieve(collection_name: str, query: str) -> str:
    """Retrieve relevant memory chunks based on query."""
    client = get_vector_client()
    embedder = get_embedder()

    collection = client.get_or_create_collection(name=collection_name)

    query_emb = embedder.encode([query]).tolist()[0]

    results = collection.query(
        query_embeddings=[query_emb],
        n_results=3
    )

    if not results["documents"]:
        return ""

    docs = results["documents"][0]
    return "\n\n".join(docs)
