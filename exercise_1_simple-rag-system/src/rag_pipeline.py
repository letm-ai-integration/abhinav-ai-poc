"""
RAG Pipeline Module

THE RAG FLOW
------------
1. INDEXING (adding documents):
   Document → Tokenize → Embed → Store in Vector DB

2. QUERYING (answering questions):
   Question → Embed → Search Vector DB → Get relevant docs → 
   Combine with question → Send to LLM → Get answer
"""

from tokenizer import SimpleTokenizer
from embeddings import EmbeddingModel
from vector_store import VectorStore
from llm import LLMClient

class RAGPipeline:
    def __init__(self, use_llm: bool = True):
        self.tokenizer = SimpleTokenizer()
        self.embedding_model = EmbeddingModel()
        self.vector_store = VectorStore()
        
        self.use_llm = use_llm
        if use_llm:
            try:
                self.llm = LLMClient()
                print("LLM ready")
            except ValueError as e:
                print(f"LLM not available: {e}")
                print("(Pipeline will work without LLM - showing retrieved context only)")
                self.use_llm = False
                self.llm = None
        else:
            self.llm = None
            print("Skipping LLM (use_llm=False)")
    
    def add_document(self, text: str, metadata: dict = None) -> int:
        token_count = self.tokenizer.count_tokens(text)
        embedding = self.embedding_model.embed(text)
        doc_id = self.vector_store.add(
            text=text,
            embedding=embedding,
            metadata={
                **(metadata or {}),
                "token_count": token_count
            }
        )

        return doc_id
    
    def add_documents(self, texts: list[str]) -> list[int]:
        return [self.add_document(text) for text in texts]
    
    def retrieve(self, query: str, top_k: int = 3) -> list[tuple[str, float]]:
        query_embedding = self.embedding_model.embed(query)
        results = self.vector_store.search(query_embedding, top_k=top_k)
        return [(doc.text, score) for doc, score in results]
    
    def query(self, question: str, top_k: int = 3) -> str:
        retrieved = self.retrieve(question, top_k=top_k)

        if not retrieved:
            return "No relevant documents found in the knowledge base."
        
        context_parts = []
        for i, (text, score) in enumerate(retrieved, 1):
            context_parts.append(f"[Document {i} (relevance: {score:.2f})]\n{text}")
        
        context = "\n\n".join(context_parts)
        
        if self.use_llm and self.llm:
            answer = self.llm.generate_with_context(question, context)
            return answer
        else:
            return f"Retrieved Context:\n{'-' * 40}\n{context}"
        
    def show_stats(self):
        print(f"Documents in knowledge base: {self.vector_store.count()}")
        
        total_tokens = 0
        for doc in self.vector_store.get_all():
            total_tokens += doc.metadata.get("token_count", 0)
        
        print(f"Total tokens: {total_tokens}")

if __name__ == "__main__":
    rag = RAGPipeline(use_llm=True)

    documents = [
        "Python was created by Guido van Rossum and first released in 1991. It emphasizes code readability and simplicity.",
        "JavaScript was created by Brendan Eich in 1995 while he was working at Netscape. It took only 10 days to develop the first version.",
        "Python is widely used in data science, machine learning, and artificial intelligence due to its extensive libraries like NumPy, Pandas, and TensorFlow.",
        "JavaScript is the primary language for web development. It can run in browsers and on servers (via Node.js).",
        "The name 'Python' comes from Monty Python's Flying Circus, not from the snake.",
        "TypeScript is a superset of JavaScript that adds static typing. It was developed by Microsoft.",
    ]

    for doc in documents:
        doc_id = rag.add_document(doc)
        preview = doc[:60] + "..." if len(doc) > 60 else doc

    # rag.show_stats()
    
    questions = [
        "Who created Python and when?",
        "What is JavaScript used for?",
        "Where does the name Python come from?",
    ]
    
    for question in questions:
        print(f"Question: {question}")
        
        print("\nRetrieved documents:")
        retrieved = rag.retrieve(question, top_k=2)
        for i, (text, score) in enumerate(retrieved, 1):
            print(f"  {i}. (score: {score:.3f}) {text[:80]}...")
        
        print("\nAnswer:")
        answer = rag.query(question, top_k=2)
        print(answer)