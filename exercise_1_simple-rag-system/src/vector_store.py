import numpy as np
from dataclasses import dataclass

@dataclass
class Document:
    id: str
    text: str
    embedding: np.ndarray
    metadata: dict = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

class VectorStore:
    def __init__(self):
        self.documents: list[Document] = []
        self.next_id = 0

    def add(self, text: str, embedding: np.ndarray, metadata: dict = None) -> int:
        doc = Document(
            id=self.next_id,
            text=text,
            embedding=embedding,
            metadata=metadata or {}
        )
        self.documents.append(doc)
        self.next_id += 1
        return doc.id
    
    def search(self, query_embedding: np.ndarray, top_k: int = 3) -> list[tuple[Document, float]]:
        if not self.documents:
            return []
        
        similarities = []
        for doc in self.documents:
            sim = self._cosine_similarity(query_embedding, doc.embedding)
            similarities.append((doc, sim))

        similarities.sort(key=lambda x: x[1], reverse=True)

        return similarities[:top_k]
    
    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
if __name__ == "__main__":
    from embeddings import EmbeddingModel

    embedding_model = EmbeddingModel()
    vector_store = VectorStore()

    documents = [
        "Python is a high-level programming language known for its readability.",
        "JavaScript is widely used for web development and runs in browsers.",
        "Machine learning is a subset of artificial intelligence.",
        "Python is popular for data science and machine learning applications.",
        "React is a JavaScript library for building user interfaces.",
    ]

    for doc_text in documents:
        embedding = embedding_model.embed(doc_text)
        doc_id = vector_store.add(doc_text, embedding)

    queries = [
        "What language is good for AI?",
        "How do I build a website?",
    ]

    for query in queries:
        query_embedding = embedding_model.embed(query)
        results = vector_store.search(query_embedding, top_k=3)
        print("Top 3 most relevant documents:")
        for i, (doc, score) in enumerate(results, 1):
            print(f"  {i}. (similarity: {score:.4f})")
            print(f"     \"{doc.text}\"")