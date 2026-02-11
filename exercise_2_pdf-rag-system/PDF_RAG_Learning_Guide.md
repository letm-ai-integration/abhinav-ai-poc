# PDF RAG System

## 1. The Problem: Why Extend RAG to PDFs?

In Exercise 1, we built RAG with plain text strings. But in the real world, knowledge lives in **PDF documents** — reports, manuals, research papers, contracts, etc.

PDFs bring new challenges:

| Challenge | Why It's Hard |
|-----------|--------------|
| **Text extraction** | PDFs are a display format, not a text format |
| **Large documents** | A single PDF can be thousands of pages — too big for one embedding |
| **Chunking** | Must split documents into smaller pieces while preserving meaning |
| **Metadata tracking** | Need to know which page and file each piece came from |
| **Scale** | Thousands of chunks need fast search and persistent storage |

> **Think of it this way:**
> - **Exercise 1:** A small notebook with a few handwritten notes.
> - **Exercise 2:** A library of books — you need an index, a catalog, and a fast way to look things up.

---

## 2. What's New in This Exercise?

| Component | Exercise 1 | Exercise 2 |
|-----------|-----------|-----------|
| **Input** | Plain text strings | PDF files |
| **Chunking** | None (whole documents) | Character-based with overlap |
| **Embeddings** | One at a time | Batch processing |
| **Vector Store** | In-memory numpy | FAISS (fast C++ library) |
| **Metadata** | Basic | Page numbers, source file |
| **Persistence** | None | Save/load index to disk |

---

## 3. Core Concepts We Built

### 3.1 PDF Loading & Chunking

We used **pdfplumber** to extract text from PDFs page by page, then split each page into overlapping chunks.

- **Chunk size (500 chars):** Small enough to be focused, large enough to carry meaning
- **Overlap (50 chars):** Chunks share text at boundaries so no information is lost at split points
- Each chunk carries **metadata** — page number and source filename

```
Without chunking:  100-page PDF → 1 huge embedding → loses detail
With chunking:     100-page PDF → 200+ focused chunks → precise retrieval
```

**Trade-offs:**
- Smaller chunks → more precise, but less context per chunk
- Larger chunks → more context, but may dilute relevance
- More overlap → better continuity, but more storage

### 3.2 Batch Embeddings

Instead of embedding one chunk at a time, **batch processing** handles all chunks in a single call — dramatically faster.

```python
# Slow: one at a time
for chunk in chunks:
    embedding = model.embed(chunk)      # ~10 seconds for 100 chunks

# Fast: all at once
embeddings = model.embed_batch(chunks)  # ~2 seconds for 100 chunks
```

### 3.3 FAISS Vector Store

**FAISS** (Facebook AI Similarity Search) replaces our simple numpy vector store. It's a C++ library designed for fast similarity search at scale.

| Feature | Exercise 1 (numpy) | Exercise 2 (FAISS) |
|---------|-------------------|-------------------|
| **Speed** | Slow (pure Python loop) | Fast (optimized C++) |
| **Scale** | Hundreds of docs | Millions of docs |
| **Persistence** | None | Save/load to disk |
| **Batch operations** | Manual loop | Native support |

**Key details:**
- We use `IndexFlatIP` (Inner Product index) — with normalized vectors, this equals cosine similarity
- Vectors are **L2-normalized** before storing so inner product = cosine similarity
- `save()` and `load()` let you index once and reuse without re-embedding

### 3.4 Source Attribution

When the LLM generates an answer, retrieved chunks include **where they came from**:

```
[company_handbook.pdf, Page 12]
Employees are entitled to 20 days of paid leave per year...
```

This lets users trace answers back to the exact source and page.

---

## 4. How the Pipeline Works

### Indexing Flow
1. **Load PDF** → pdfplumber extracts text page by page
2. **Chunk** → split into 500-char pieces with 50-char overlap
3. **Track metadata** → each chunk knows its page number and source file
4. **Batch embed** → all chunks embedded at once
5. **Store in FAISS** → normalized vectors added to the index
6. **Persist** → save index + metadata to disk

### Query Flow
1. **Embed the question** → convert to a vector
2. **FAISS search** → find the top-k most similar chunks
3. **Retrieve** → get the text and metadata for each match
4. **Build context** → format with source attribution
5. **Send to LLM** → generate an answer grounded in the context

---

## 5. Dependencies

| Package | Purpose |
|---------|---------|
| **pdfplumber** | Extract text from PDF files |
| **sentence-transformers** | Embedding models |
| **faiss-cpu** | Fast vector similarity search (use `faiss-gpu` for GPU) |
| **numpy** | Vector operations |
| **openai** | GPT API client |
| **python-dotenv** | Load API keys from `.env` |

---

## 6. Quick Reference

| Concept | What It Is |
|---------|-----------|
| **Chunking** | Splitting large documents into smaller, focused pieces |
| **Chunk Size** | Max characters per chunk (default: 500) |
| **Overlap** | Characters shared between consecutive chunks (default: 50) |
| **Batch Embedding** | Embedding multiple texts in one call for speed |
| **FAISS** | Facebook's fast vector search library (C++) |
| **IndexFlatIP** | FAISS index using inner product (cosine sim when normalized) |
| **Normalization** | Scaling vectors to unit length so inner product = cosine similarity |
| **Persistence** | Saving the index to disk for reuse without re-embedding |
| **Source Attribution** | Tracking which page/file a chunk came from |
| **pdfplumber** | Python library for extracting text from PDFs |

---
