import numpy as np
from sentence_transformers import SentenceTransformer

class EmbeddingModel:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        self.model_name = model_name
        self.embedding_dimension = self.model.get_sentence_embedding_dimension()
        print(f"Loaded embedding model '{model_name}' with dimension {self.embedding_dimension}")

    def embed(self, text: str) -> np.ndarray:
        return self.model.encode(text, convert_to_numpy=True)
    
    def similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        dot_product = np.dot(embedding1, embedding2)
        norm1 = np.linalg.norm(embedding1)
        norm2 = np.linalg.norm(embedding2)

        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
if __name__ == "__main__":
    model = EmbeddingModel()

    # Show embedding dimensions
    sample_text = "Learning AI and LLMs"
    embedding = model.embed(sample_text)
    # print(f"Text: {sample_text}")
    # print(f"Embedding: {embedding}")
    # print(f"Embedding Dimension: {len(embedding)}")

    # Compute similarity between two texts
    text1 = "Tokens are the basic units that language models work with."
    text2 = "Tokenization is the process of converting raw text into these tokens."
    text3 = "Chelsea is a football club based in London."

    embedding1 = model.embed(text1)
    embedding2 = model.embed(text2)
    embedding3 = model.embed(text3)

    print(f"Similarity between text1 and text2: {model.similarity(embedding1, embedding2)}")
    print(f"Similarity between text1 and text3: {model.similarity(embedding1, embedding3)}")
