from pdf_loader import load_pdf
from embeddings import EmbeddingModel
from vector_store import VectorStore
from llm import LLMClient


class RAGPipeline:
    def __init__(self):
        self.embedding_model = EmbeddingModel()
        self.vector_store = VectorStore(dimension=self.embedding_model.dimension)
        
        try:
            self.llm = LLMClient()
            self.use_llm = True
        except ValueError:
            self.llm = None
            self.use_llm = False
    
    def index_pdf(self, pdf_path: str) -> int:
        chunks = load_pdf(pdf_path)
        
        if not chunks:
            return 0
        
        texts = [c["text"] for c in chunks]
        metadatas = [{"page": c["page"], "source": c["source"]} for c in chunks]
        
        embeddings = self.embedding_model.embed_batch(texts)
        self.vector_store.add_batch(texts, embeddings, metadatas)
        
        return len(chunks)
    
    def retrieve(self, query: str, top_k: int = 3) -> list[tuple[str, dict, float]]:
        query_embedding = self.embedding_model.embed(query)
        results = self.vector_store.search(query_embedding, top_k=top_k)
        
        return [(doc["text"], doc["metadata"], score) for doc, score in results]
    
    def query(self, question: str, top_k: int = 3) -> str:
        retrieved = self.retrieve(question, top_k=top_k)
        
        if not retrieved:
            return "No relevant documents found."
        
        # Build context from retrieved chunks
        context_parts = []
        for text, metadata, score in retrieved:
            source = metadata.get("source", "unknown")
            page = metadata.get("page", "?")
            context_parts.append(f"[{source}, Page {page}]\n{text}")
        
        context = "\n\n".join(context_parts)
        
        if self.use_llm:
            return self.llm.generate_answer(question, context)
        else:
            return f"Retrieved Context:\n{'-'*40}\n{context}"
    
    def save_index(self, path: str):
        self.vector_store.save(path)
    
    def load_index(self, path: str):
        self.vector_store.load(path)


if __name__ == "__main__":
    import sys
    
    rag = RAGPipeline()
    
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
        count = rag.index_pdf(pdf_path)
        print(f"Indexed {count} chunks from {pdf_path}")
        
        # Interactive query loop
        print("\nAsk questions (type 'quit' to exit):")
        while True:
            question = input("\nQ: ").strip()
            if question.lower() in ['quit', 'exit', 'q']:
                break
            if question:
                answer = rag.query(question)
                print(f"\nA: {answer}")
    else:
        print("Usage: python rag_pipeline.py <pdf_path>")
        print("\nOr use in Python:")
        print("  rag = RAGPipeline()")
        print("  rag.index_pdf('document.pdf')")
        print("  answer = rag.query('What is this about?')")
