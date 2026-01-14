#!/usr/bin/env python3
"""
Portable PDF RAG Search
Self-contained search script for Agent Skills integration
"""

import os
import sys
import json
import argparse
from pathlib import Path
from typing import List, Dict, Any, Tuple
import hashlib

# Configuration from environment or defaults
SKILL_DIR = Path(__file__).parent
VECTOR_STORE_PATH = SKILL_DIR / "vector_store.json"
OLLAMA_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "nomic-embed-text")
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "2000"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "500"))


def embed_text(text: str) -> List[float]:
    """Generate embedding using Ollama."""
    import requests

    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/embeddings",
            json={"model": OLLAMA_MODEL, "prompt": text},
            timeout=30
        )
        response.raise_for_status()
        return response.json()["embedding"]
    except Exception as e:
        print(f"Error generating embedding: {e}", file=sys.stderr)
        sys.exit(1)


def cosine_similarity(a: List[float], b: List[float]) -> float:
    """Calculate cosine similarity between two vectors."""
    dot_product = sum(x * y for x, y in zip(a, b))
    magnitude_a = sum(x * x for x in a) ** 0.5
    magnitude_b = sum(x * x for x in b) ** 0.5

    if magnitude_a == 0 or magnitude_b == 0:
        return 0.0

    return dot_product / (magnitude_a * magnitude_b)


def load_vector_store() -> Dict[str, Any]:
    """Load the vector store from JSON."""
    if not VECTOR_STORE_PATH.exists():
        return {"documents": [], "metadata": {}}

    try:
        with open(VECTOR_STORE_PATH, 'r') as f:
            data = json.load(f)

        # Handle both formats: dict of docs (old) or {documents: [], metadata: {}} (new)
        if "documents" in data:
            return data
        else:
            # Convert old format to new format
            documents = []
            for doc_id, doc_data in data.items():
                if isinstance(doc_data, dict) and "embedding" in doc_data:
                    documents.append(doc_data)

            return {
                "documents": documents,
                "metadata": {
                    "total_documents": len(documents),
                    "embedding_model": documents[0].get("metadata", {}).get("embedding_model", "unknown") if documents else "unknown"
                }
            }
    except Exception as e:
        print(f"Error loading vector store: {e}", file=sys.stderr)
        return {"documents": [], "metadata": {}}


def save_vector_store(store: Dict[str, Any]):
    """Save the vector store to JSON."""
    try:
        with open(VECTOR_STORE_PATH, 'w') as f:
            json.dump(store, f, indent=2)
    except Exception as e:
        print(f"Error saving vector store: {e}", file=sys.stderr)
        sys.exit(1)


def search(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """Search the vector store for relevant documents."""
    store = load_vector_store()

    if not store["documents"]:
        return []

    # Generate query embedding
    query_embedding = embed_text(query)

    # Calculate similarities
    results = []
    for doc in store["documents"]:
        similarity = cosine_similarity(query_embedding, doc["embedding"])
        results.append({
            "content": doc["content"],
            "source": doc["source"],
            "page": doc["page"],
            "chunk_index": doc.get("chunk_index", 0),
            "similarity": similarity,
            "metadata": doc.get("metadata", {})
        })

    # Sort by similarity and return top K
    results.sort(key=lambda x: x["similarity"], reverse=True)
    return results[:top_k]


def index_pdf(pdf_path: Path) -> Dict[str, Any]:
    """Index a PDF file into the vector store."""
    try:
        import PyPDF2
    except ImportError:
        print("Error: PyPDF2 not installed. Run: pip install PyPDF2", file=sys.stderr)
        sys.exit(1)

    if not pdf_path.exists():
        print(f"Error: PDF file not found: {pdf_path}", file=sys.stderr)
        sys.exit(1)

    # Extract text from PDF
    chunks = []
    with open(pdf_path, 'rb') as f:
        reader = PyPDF2.PdfReader(f)

        for page_num, page in enumerate(reader.pages, start=1):
            text = page.extract_text()

            # Chunk the text
            for i in range(0, len(text), CHUNK_SIZE - CHUNK_OVERLAP):
                chunk_text = text[i:i + CHUNK_SIZE]

                if len(chunk_text) < 100:  # Skip very small chunks
                    continue

                chunks.append({
                    "text": chunk_text,
                    "page": page_num,
                    "chunk_index": i // (CHUNK_SIZE - CHUNK_OVERLAP)
                })

    if not chunks:
        print(f"Warning: No text extracted from {pdf_path.name}", file=sys.stderr)
        return {"chunks_added": 0}

    # Load existing store
    store = load_vector_store()

    # Generate embeddings and add to store
    print(f"Generating embeddings for {len(chunks)} chunks from {pdf_path.name}...")

    for i, chunk in enumerate(chunks):
        if (i + 1) % 10 == 0:
            print(f"  Progress: {i + 1}/{len(chunks)}", file=sys.stderr)

        embedding = embed_text(chunk["text"])

        doc_id = hashlib.sha256(
            f"{pdf_path.name}_{chunk['page']}_{chunk['chunk_index']}".encode()
        ).hexdigest()[:16]

        store["documents"].append({
            "id": doc_id,
            "content": chunk["text"],
            "embedding": embedding,
            "source": pdf_path.name,
            "page": chunk["page"],
            "chunk_index": chunk["chunk_index"],
            "metadata": {
                "indexed_at": str(Path(__file__).stat().st_mtime),
                "embedding_model": OLLAMA_MODEL
            }
        })

    # Update metadata
    store["metadata"] = {
        "total_documents": len(store["documents"]),
        "embedding_model": OLLAMA_MODEL,
        "embedding_dimension": len(store["documents"][0]["embedding"]) if store["documents"] else 0
    }

    # Save store
    save_vector_store(store)

    return {"chunks_added": len(chunks)}


def get_stats() -> Dict[str, Any]:
    """Get statistics about the vector store."""
    store = load_vector_store()

    sources = {}
    for doc in store["documents"]:
        source = doc["source"]
        sources[source] = sources.get(source, 0) + 1

    return {
        "total_documents": len(store["documents"]),
        "sources": [{"source": k, "count": v} for k, v in sources.items()],
        "embedding_model": store["metadata"].get("embedding_model", "unknown"),
        "embedding_dimension": store["metadata"].get("embedding_dimension", 0)
    }


def main():
    parser = argparse.ArgumentParser(description="Portable PDF RAG Search")
    parser.add_argument("--search", metavar="QUERY", help="Search query")
    parser.add_argument("--index", metavar="PDF", help="PDF file to index")
    parser.add_argument("--stats", action="store_true", help="Show statistics")
    parser.add_argument("--top-k", type=int, default=5, help="Number of results")
    parser.add_argument("--clear", action="store_true", help="Clear vector store")

    args = parser.parse_args()

    if args.clear:
        if VECTOR_STORE_PATH.exists():
            VECTOR_STORE_PATH.unlink()
            print("✅ Vector store cleared")
        else:
            print("Vector store is already empty")

    elif args.stats:
        stats = get_stats()
        print("Knowledge Base Statistics:")
        print(f"  total_documents: {stats['total_documents']}")
        print(f"  sources: {stats['sources']}")
        print(f"  embedding_model: {stats['embedding_model']}")
        print(f"  embedding_dimension: {stats['embedding_dimension']}")

    elif args.index:
        pdf_path = Path(args.index)
        result = index_pdf(pdf_path)
        print(f"✅ Indexed {result['chunks_added']} chunks from {pdf_path.name}")

    elif args.search:
        results = search(args.search, top_k=args.top_k)

        if not results:
            print("No results found.")
        else:
            print(f"Found {len(results)} results:\n")
            for i, result in enumerate(results, 1):
                print(f"--- Result {i} (Similarity: {result['similarity']:.1%}) ---")
                print(f"Source: {result['source']}")
                print(f"Page: {result['page']}")
                print(f"Content: {result['content'][:300]}...")
                print()

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
