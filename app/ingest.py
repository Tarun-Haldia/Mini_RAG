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



# from sentence_transformers import SentenceTransformer
# from app.db import supabase
# import json
# from typing import List

# # Load embedding model once at startup
# model = SentenceTransformer("all-MiniLM-L6-v2")


# def chunk_text(text: str, chunk_size: int = 120, overlap: int = 30) -> List[str]:
#     """
#     Split text into overlapping word chunks.
#     """
#     words = text.split()
#     chunks = []
#     start = 0

#     while start < len(words):
#         end = start + chunk_size
#         chunk = " ".join(words[start:end])
#         chunks.append(chunk)
#         start += chunk_size - overlap

#     return chunks


# def ingest_text(text: str, batch_size: int = 100) -> dict:
#     """
#     Chunk text, embed chunks, and store them in Supabase.
#     """
#     print("TEXT LENGTH:", len(text))
#     print("TEXT PREVIEW:", text[:200])

#     chunks = chunk_text(text)
#     print("TOTAL CHUNKS:", len(chunks))

#     rows = []
#     total_inserted = 0

#     for i, chunk in enumerate(chunks):
#         print(f"CHUNK {i + 1} PREVIEW:", chunk[:80])

#         embedding = model.encode(chunk).tolist()

#         rows.append({
#             "content": chunk,
#             "embedding": json.dumps(embedding)
#         })

#         # Batch insert
#         if len(rows) >= batch_size:
#             supabase.table("documents").insert(rows).execute()
#             total_inserted += len(rows)
#             rows.clear()

#     # Insert remaining rows
#     if rows:
#         supabase.table("documents").insert(rows).execute()
#         total_inserted += len(rows)

#     return {
#         "status": "success",
#         "chunks_ingested": total_inserted
#     }
