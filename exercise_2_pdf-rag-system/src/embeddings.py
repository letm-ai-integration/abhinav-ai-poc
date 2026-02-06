import numpy as np
from sentence_transformers import SentenceTransformer


class EmbeddingModel:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        self.dimension = self.model.get_sentence_embedding_dimension()

    def embed(self, text: str) -> np.ndarray:
        return self.model.encode(text, convert_to_numpy=True)
    
    def embed_batch(self, texts: list[str]) -> np.ndarray:
        return self.model.encode(texts, convert_to_numpy=True, show_progress_bar=True)


if __name__ == "__main__":
    model = EmbeddingModel()
    
    texts = [
        "Tokens are the basic units that language models work with.", 
        "Tokenization is the process of converting raw text into these tokens.", 
        "Chelsea is a football club based in London."]
    embeddings = model.embed_batch(texts)
    print(f"Embedded {len(texts)} texts, shape: {embeddings.shape}")
