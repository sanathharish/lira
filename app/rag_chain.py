"""
STEP 3: RAG (Retrieval-Augmented Generation)
-------------------------------------------
This module:
1. Loads text files or documents
2. Splits them into chunks
3. Generates embeddings
4. Stores vectors in ChromaDB
5. Retrieves relevant chunks
6. Feeds them into Ollama for grounded answers
"""

import os
from dotenv import load_dotenv

# Vector DB
import chromadb
from chromadb.config import Settings

# Embeddings
from sentence_transformers import SentenceTransformer

# LangChain imports
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough

load_dotenv()

# ---------------------------------------------------
# EMBEDDING MODEL (local, free)
# ---------------------------------------------------
def get_embeddings_model():
    """
    Use a free lightweight embedding model.
    Good for experimentation and RAG.
    """
    return SentenceTransformer("all-MiniLM-L6-v2")

# ---------------------------------------------------
# LLM (Ollama)
# ---------------------------------------------------
def get_llm():
    return ChatOllama(
        model="llama3.2",
        temperature=0.3
    )

# ---------------------------------------------------
# 1) Load raw documents
# ---------------------------------------------------
def load_document(path: str) -> str:
    """Load a text file."""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()
    

# ---------------------------------------------------
# 2) Chunk text into small pieces
# ---------------------------------------------------
def chunk_text(text, chunk_size=500, overlap=100):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - overlap
    return chunks


# ---------------------------------------------------
# 3) Build / load Chroma VectorDB
# ---------------------------------------------------
def get_vector_db():
    from chromadb import Client
    client = Client()  # uses new default persistent store
    return client



# ---------------------------------------------------
# 4) Embed & store vector chunks
# ---------------------------------------------------
def store_documents_in_chroma(collection_name: str, texts: list):
    client = get_vector_db()
    embedder = get_embeddings_model()

    collection = client.get_or_create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"}
    )

    embeddings = embedder.encode(texts).tolist()

    # Add embeddings to Chroma
    ids = [f"doc_{i}" for i in range(len(texts))]
    collection.add(
        documents=texts,
        embeddings=embeddings,
        ids=ids
    )

    print(f"Stored {len(texts)} chunks in Chroma collection '{collection_name}'")
    return collection


# ---------------------------------------------------
# 5) Retrieval + LLM Answering (RAG Chain)
# ---------------------------------------------------
def build_rag_chain(collection_name: str):
    client = get_vector_db()
    collection = client.get_collection(collection_name)
    llm = get_llm()

    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            "You are a helpful RAG assistant. Use ONLY the provided context. "
            "If you don't know, say 'I don't know based on the documents.'"
        ),
        (
            "human",
            "Context:\n{context}\n\n"
            "Question: {question}\n"
            "Answer using only the context above."
        )
    ])

    def retriever(query):
        """Fetch top 3 relevant chunks."""
        embedder = get_embeddings_model()
        q_emb = embedder.encode([query]).tolist()[0]

        results = collection.query(
            query_embeddings=[q_emb],
            n_results=3
        )
        return "\n\n".join(results["documents"][0])

    rag_chain = RunnableParallel(
        context=RunnablePassthrough() | retriever,
        question=RunnablePassthrough()
    ) | prompt | llm

    return rag_chain


# ---------------------------------------------------
# DEMO
# ---------------------------------------------------
def demo():
    print("\n=== STEP 3 DEMO: RAG Pipeline ===")

    # 1. Load local text file
    text = load_document("sample.txt")

    # 2. Chunk
    chunks = chunk_text(text)
    print(f"Created {len(chunks)} chunks")

    # 3. Store in Chroma
    store_documents_in_chroma("demo_collection", chunks)

    # 4. Build RAG chain
    rag_chain = build_rag_chain("demo_collection")

    # 5. Ask a question
    question = "What is the main idea of this document?"
    answer = rag_chain.invoke(question)

    print("\n=== RAG ANSWER ===\n")
    print(answer)


if __name__ == "__main__":
    demo()