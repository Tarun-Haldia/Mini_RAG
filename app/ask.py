import os
import json
import numpy as np
from sentence_transformers import SentenceTransformer
import google.generativeai as genai
from db import supabase

# ---------------- CONFIG ----------------

EMBED_MODEL_NAME = "all-MiniLM-L6-v2"
TOP_K = 3

embed_model = SentenceTransformer(EMBED_MODEL_NAME)

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
llm = genai.GenerativeModel("models/gemini-2.5-flash")

# ---------------- ASK FUNCTION ----------------

def ask_question(question: str):

    # 1️⃣ Fetch documents from DB
    res = supabase.table("documents").select("content", "embedding").execute()

    if not res.data:
        return {
            "answer": "❌ No document present in database. Please ingest data first."
        }

    texts = []
    embeddings = []

    # 2️⃣ Load embeddings safely
    for row in res.data:
        emb = row.get("embedding")

        if emb is None:
            continue

        # JSON string → list
        if isinstance(emb, str):
            emb = json.loads(emb)

        texts.append(row["content"])
        embeddings.append(emb)

    if not embeddings:
        return {
            "answer": "❌ No valid embeddings found."
        }

    # 3️⃣ Convert to numpy
    embeddings = np.array(embeddings, dtype=np.float32)
    question_embedding = embed_model.encode(question).astype(np.float32)

    # 4️⃣ Vector similarity (dot product)
    scores = embeddings @ question_embedding

    # 5️⃣ Top-K retrieval
    top_k_idx = np.argsort(scores)[-TOP_K:][::-1]
    top_texts = [texts[i] for i in top_k_idx]
    top_k_scores = [float(scores[i]) for i in top_k_idx]

    # 6️⃣ Reranking (cross-style)
    rerank_scores = []
    for txt in top_texts:
        pair_embedding = embed_model.encode(
            f"Question: {question}\nContext: {txt}"
        ).astype(np.float32)

        rerank_scores.append(
            float(np.dot(pair_embedding, question_embedding))
        )

    # 7️⃣ Pick best context AFTER rerank
    best_idx = int(np.argmax(rerank_scores))
    best_context = top_texts[best_idx]

    # 8️⃣ LLM prompt (STRICT RAG)
    prompt = f"""
Answer the question using ONLY the context below.
Do NOT use outside knowledge.

Context:
{best_context}

Question:
{question}

If the answer is not present in the context, say "I don't know".
"""

    result = llm.generate_content(prompt)

    # 9️⃣ Final response
    return {
        "answer": result.text.strip(),
        "top_k_scores": top_k_scores,
        "rerank_scores": rerank_scores
    }
