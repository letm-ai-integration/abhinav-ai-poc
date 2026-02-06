# Simple RAG System

A minimal Retrieval-Augmented Generation (RAG) implementation in Python. This project demonstrates the core concepts of RAG by combining document retrieval with LLM-powered question answering.

## How It Works

### RAG Flow

**Indexing (adding documents):**
```
Document → Tokenize → Embed → Store in Vector DB
```

**Querying (answering questions):**
```
Question → Embed → Search Vector DB → Get relevant docs → Combine with question → Send to LLM → Get answer
```

## Project Structure

```
simple-RAG-system/
├── src/
│   ├── tokenizer.py      # Token counting using tiktoken
│   ├── embeddings.py     # Text embeddings using sentence-transformers
│   ├── vector_store.py   # In-memory vector store with cosine similarity
│   ├── llm.py            # OpenAI GPT integration
│   └── rag_pipeline.py   # Main RAG pipeline combining all components
├── data/
│   └── sample_documents.txt
├── requirements.txt
└── .env
```

## Components

- **Tokenizer**: Uses `tiktoken` (cl100k_base encoding) for token counting
- **Embedding Model**: Uses `sentence-transformers` (all-MiniLM-L6-v2) to convert text to 384-dimensional vectors
- **Vector Store**: Simple in-memory store with cosine similarity search
- **LLM Client**: OpenAI GPT (gpt-4o-mini) for generating context-aware answers

## Installation

1. Clone the repository

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up your OpenAI API key in `.env`:
   ```
   OPENAI_API_KEY=your-api-key-here
   ```

## Usage

```python
from src.rag_pipeline import RAGPipeline

# Initialize the pipeline
rag = RAGPipeline(use_llm=True)

# Add documents to the knowledge base
rag.add_document("Python was created by Guido van Rossum in 1991.")
rag.add_document("JavaScript was created by Brendan Eich in 1995.")

# Query the system
answer = rag.query("Who created Python?")
print(answer)
```

### Running the Demo

```bash
cd src
python rag_pipeline.py
```

This runs a demo that:
1. Adds sample documents about programming languages
2. Asks questions and retrieves relevant documents
3. Generates answers using the LLM (if configured)

## Requirements

- Python 3.10+
- sentence-transformers >= 2.2.0
- numpy >= 1.24.0
- openai >= 1.0.0
- tiktoken >= 0.5.0
- python-dotenv >= 1.0.0

## Notes

- The pipeline works without an OpenAI API key - it will show retrieved context instead of LLM-generated answers
- The vector store is in-memory and does not persist between sessions
