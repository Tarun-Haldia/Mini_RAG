---
title: Mini RAG
emoji: 🏢
colorFrom: pink
colorTo: yellow
sdk: docker
pinned: false
short_description: RAG using LLM/API.
---

# Mini RAG System (FastAPI + Supabase + Gemini)

A minimal but production‑grade **Retrieval‑Augmented Generation (RAG)** system built with FastAPI. The system ingests raw text, chunks it using a clear token‑based strategy, stores embeddings in a hosted vector database (Supabase + pgvector‑style storage), retrieves and reranks relevant chunks, and generates grounded answers using an LLM with citations.

This project is intentionally simple, transparent, and interview‑friendly.


## 📸 Screenshots

### Chunking Strategy
![Chunking](screenshots/Chunking.png)

### Data Combination Before Ingestion
![Data Combine](screenshots/data_combine.png)

### Empty Data Handling
![Empty Data Handle](screenshots/empty_data_handle.png)

### Accuracy Improvement (Reranking)
![Increase Accuracy](screenshots/Inc accuracy.png)

### Model & Pipeline Definition
![ML Define](screenshots/ML define.png)

### End-to-End Test Proof
![Test Proof](screenshots/test_proof.png)


---

## 1. Architecture Overview

```
User (UI)
   │
   ▼
FastAPI Backend
   ├── /ingest  → Chunking → Embeddings → Vector DB (Supabase)
   └── /ask     → Retrieve Top‑K → Rerank → LLM (Gemini)
                          │
                          ▼
                   Grounded Answer + Sources
```

**Key principles:**

* Chunk once, embed once
* Retrieve before generation
* Generate answers strictly from retrieved context

---

## 2. Tech Stack

### Backend

* **FastAPI** – API server
* **Python 3.10+**

### Vector Database (Hosted)

* **Supabase** (Postgres‑based, hosted)
* Table: `documents`
* Stored fields:

  * `content` (text chunk)
  * `embedding` (JSON‑encoded vector)
  * `chunk_id` (integer)

### Embeddings

* **SentenceTransformers**
* Model: `all-MiniLM-L6-v2`
* Embedding dimension: **384**

### LLM

* **Google Gemini** (AI Studio)
* Model: `gemini-2.5-flash`

---

## 3. Chunking Strategy (Critical)

A clear, token‑based chunking strategy is used, as required by RAG best practices.

* **Chunk size:** 1,000 tokens
* **Overlap:** 120 tokens (~12%)
* **Why:**

  * Preserves semantic continuity across chunks
  * Fits typical LLM context windows
  * Avoids retrieval fragmentation

Chunking is implemented using **tiktoken**, ensuring token‑level (not character or word‑level) accuracy.

---

## 4. Ingestion Pipeline

1. Raw text is pasted/uploaded via the UI
2. Text is chunked using token‑based chunking
3. Each chunk is embedded using `all-MiniLM-L6-v2`
4. Embeddings + metadata are stored in Supabase

**Upsert strategy:**

* Current implementation uses simple inserts (no deduplication)
* This tradeoff keeps the system simple and transparent

---

## 5. Retrieval & Reranking

### Retrieval

* All embeddings are fetched from Supabase
* Query embedding is computed
* Similarity scoring via **dot product**
* **Top‑K = 3** chunks selected

### Reranking

* Lightweight custom reranker
* Each candidate chunk is re‑embedded with:

  ```
  Question + Context
  ```
* Highest reranked score is selected as final context

**Note:**

* A hosted reranker (Cohere / Jina / BGE) can be plugged in later
* Current approach is documented as a tradeoff

---

## 6. Answer Generation (RAG)

The LLM is prompted in **strict RAG mode**:

* Uses ONLY retrieved context
* No outside knowledge allowed
* Explicit fallback: `"I don't know"` if answer not found

This ensures grounded, auditable answers.

---

## 7. Frontend Features

* Text paste area for ingestion
* Question input box
* Answer panel
* Source snippets (retrieved chunks)
* Request latency display (ms)
* Rough token + cost estimates

The frontend communicates only with FastAPI endpoints.

---

## 8. API Endpoints

### `POST /ingest`

```json
{
  "text": "Raw document text"
}
```

Response:

```json
{
  "status": "success",
  "chunks_ingested": 4
}
```

---

### `POST /ask`

```json
{
  "question": "Your question here"
}
```

Response (simplified):

```json
{
  "answer": "Generated answer",
  "top_k_scores": [...],
  "rerank_scores": [...]
}
```

---

## 9. Environment Variables

All API keys are kept **server‑side**.

Create a `.env` file:

```
GEMINI_API_KEY=your_api_key_here
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
```

---

## 10. Running Locally

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

Open:

```
http://127.0.0.1:8000
```

---

## 11. Deployment

This project can be deployed on free tiers such as:


* Render
* HF


Supabase provides hosted persistence, so the backend remains stateless.

---

## 12. Known Tradeoffs & Remarks

* Supabase is used as a simple hosted vector store instead of a dedicated engine (Pinecone/Qdrant)
* Custom reranking is used instead of a hosted reranker
* Inline citation formatting (`[1] [2]`) can be extended further

These choices were made to keep the system minimal, inspectable, and cost‑free.

---

## 13. Future Improvements

* Inline citations with chunk IDs
* PDF upload support
* Streaming responses (SSE)
* True vector‑side similarity search
* Metadata‑aware filtering (source, section)

---

## 14. Summary

This project demonstrates a complete, working RAG pipeline with:

* Clear chunking strategy
* Hosted vector storage
* Retrieval + reranking
* Grounded LLM answering
* Simple, inspectable frontend




=======
