# Retrieval-Augmented Generation (RAG)

## 1. The Problem: Why Do We Need RAG?

LLMs like GPT-4 are powerful, but they **only know what they were trained on**. They can't answer questions about your private documents, your company data, or anything after their training cutoff.

> **Think of it this way:**
> - **Without RAG:** You ask a librarian a question, but they can only answer from memory — they never look anything up.
> - **With RAG:** The librarian first searches the library for relevant books, reads the relevant pages, and then answers your question.

| Approach | How It Works | Drawback |
|----------|-------------|----------|
| **Fine-tuning** | Retrain the LLM on your data | Expensive, slow, must repeat when data changes |
| **RAG** | Retrieve relevant context at query time and feed it to the LLM | Cheaper, real-time, no retraining needed |

---

## 2. What is RAG?

RAG stands for **Retrieval-Augmented Generation**.

| Term | Meaning |
|------|---------|
| **Retrieval** | Finding relevant documents from a knowledge base |
| **Augmented** | Enhancing the LLM's input with retrieved context |
| **Generation** | The LLM generates an answer using the augmented input |

**Key takeaway:** RAG doesn't change the LLM — it changes what you *send* to the LLM by adding relevant context.

---

## 3. The RAG Pipeline

A RAG system has two phases:

### 3.1 Indexing Phase (Preparation)

```
Document → Tokenize → Embed → Store in Vector DB
```

| Step | What Happens |
|------|-------------|
| **Tokenize** | Break text into tokens (subword units) for counting |
| **Embed** | Convert text into numerical vectors |
| **Store** | Save vectors in a vector store for fast search |

### 3.2 Querying Phase (Answering Questions)

```
Question → Embed → Search Vector DB → Get relevant docs →
Combine with question → Send to LLM → Get answer
```

---

## 4. Core Components We Built

### 4.1 Tokenizer

Tokenizers convert text into **tokens** — the basic units LLMs work with. A token is roughly ¾ of a word. We use tokenization to count tokens (important for API costs and context window limits).

- We used **tiktoken** with the `cl100k_base` encoding (same as GPT-4)
- Tokenization is **not** splitting by spaces — words can be broken into subword pieces

```python
tokenizer = SimpleTokenizer()
tokenizer.count_tokens("Learning AI and LLMs")  # → 5
```

### 4.2 Embeddings

Embeddings convert text into **numerical vectors** (arrays of numbers). The key property: **similar texts produce similar vectors**.

- We used **sentence-transformers** (`all-MiniLM-L6-v2`) which produces 384-dimensional vectors
- **Cosine similarity** measures how similar two vectors are (1.0 = identical, 0.0 = unrelated)

```python
model = EmbeddingModel()
# "Python for ML" and "ML uses Python" → high similarity (~0.75)
# "Python for ML" and "Chelsea football" → low similarity (~0.10)
```

### 4.3 Vector Store

The vector store holds document embeddings and provides **similarity search** — given a query vector, find the most similar stored vectors.

- We built a simple **in-memory** store using numpy
- `top_k` controls how many results to return (typically 2–5)
- Search computes cosine similarity against every stored vector and returns the best matches

### 4.4 LLM Client

The LLM takes retrieved context + the user's question and generates a **grounded answer**.

- We used **OpenAI's GPT-4o-mini**
- The system prompt instructs the LLM to **only use the provided context** — this reduces hallucination
- Low temperature (0.3) makes responses more factual and deterministic

---

## 5. How It All Fits Together

When you call `rag.query("Who created Python?")`:

1. **Embed the question** → convert to a 384-dim vector
2. **Search the vector store** → find the most similar document vectors
3. **Retrieve top-k texts** → pull the actual text of the best matches
4. **Build a prompt** → combine context + question into a structured prompt
5. **Send to LLM** → GPT-4o-mini generates an answer grounded in the context
6. **Return the answer** → user gets a response based on real documents, not hallucination

---

## 6. Dependencies

| Package | Purpose |
|---------|---------|
| **tiktoken** | Token counting (same encoding as OpenAI models) |
| **sentence-transformers** | Pre-trained embedding models |
| **numpy** | Vector math (cosine similarity) |
| **openai** | API client for GPT models |
| **python-dotenv** | Load API keys from `.env` file |

---

## 7. Quick Reference

| Concept | What It Is |
|---------|-----------|
| **RAG** | Retrieve relevant context before generating an answer |
| **Tokenizer** | Breaks text into subword tokens for counting |
| **Embedding** | Numerical vector that captures the meaning of text |
| **Vector Store** | Database for storing and searching embeddings |
| **Cosine Similarity** | Measures how similar two vectors are (0 to 1) |
| **top_k** | Number of most relevant documents to retrieve |
| **Context Window** | Max tokens an LLM can process in one request |
| **Temperature** | Controls randomness (lower = more factual) |

---
