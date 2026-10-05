from sentence_transformers import SentenceTransformer
from db import supabase
from chunk import chunk_text
import json

model = SentenceTransformer("all-MiniLM-L6-v2")

def ingest_text(text: str, batch_size: int = 100) -> dict:

    chunks = chunk_text(text)
    print("TOTAL CHUNKS:", len(chunks))

    rows = []
    total_inserted = 0

    for chunk in chunks:
        embedding = model.encode(chunk["content"]).tolist()

        rows.append({
            "content": chunk["content"],
            "embedding": json.dumps(embedding),
            "chunk_id": chunk["id"]
        })

        if len(rows) >= batch_size:
            supabase.table("documents").insert(rows).execute()
            total_inserted += len(rows)
            rows.clear()

    if rows:
        supabase.table("documents").insert(rows).execute()
        total_inserted += len(rows)

    return {
        "status": "success",
        "chunks_ingested": total_inserted
    }
