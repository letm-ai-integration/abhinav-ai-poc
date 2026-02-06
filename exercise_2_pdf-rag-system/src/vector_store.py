import numpy as np
import faiss
import json
from pathlib import Path


class VectorStore:
    def __init__(self, dimension: int = 384):
        self.dimension = dimension
        self.index = faiss.IndexFlatIP(dimension)  # Inner product (cosine similarity for normalized vectors)
        self.documents = []  # Store document metadata
    
    def add(self, text: str, embedding: np.ndarray, metadata: dict = None) -> int:
        # Normalize for cosine similarity
        embedding = embedding / np.linalg.norm(embedding)
        embedding = embedding.reshape(1, -1).astype('float32')
        
        self.index.add(embedding)
        self.documents.append({
            "text": text,
            "metadata": metadata or {}
        })
        
        return len(self.documents) - 1
    
    def add_batch(self, texts: list[str], embeddings: np.ndarray, metadatas: list[dict] = None):
        # Normalize all embeddings
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        normalized = (embeddings / norms).astype('float32')
        
        self.index.add(normalized)
        
        metadatas = metadatas or [{}] * len(texts)
        for text, metadata in zip(texts, metadatas):
            self.documents.append({"text": text, "metadata": metadata})
    
    def search(self, query_embedding: np.ndarray, top_k: int = 5) -> list[tuple[dict, float]]:
        if self.index.ntotal == 0:
            return []
        
        # Normalize query
        query = query_embedding / np.linalg.norm(query_embedding)
        query = query.reshape(1, -1).astype('float32')
        
        scores, indices = self.index.search(query, min(top_k, self.index.ntotal))
        
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx >= 0:
                results.append((self.documents[idx], float(score)))
        
        return results
    
    def save(self, path: str):
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self.index, str(path / "index.faiss"))
        with open(path / "documents.json", "w") as f:
            json.dump(self.documents, f)
    
    def load(self, path: str):
        path = Path(path)
        self.index = faiss.read_index(str(path / "index.faiss"))
        with open(path / "documents.json", "r") as f:
            self.documents = json.load(f)
    
    def count(self):
        return len(self.documents)


if __name__ == "__main__":
    store = VectorStore(dimension=384)
    
    # Test with random vectors
    for i in range(5):
        embedding = np.random.randn(384).astype('float32')
        store.add(f"Document {i}", embedding, {"id": i})
    
    query = np.random.randn(384).astype('float32')
    results = store.search(query, top_k=3)
    
    print("Search results:")
    for doc, score in results:
        print(f"  {doc['text']}: {score:.4f}")
