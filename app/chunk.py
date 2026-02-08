import tiktoken
from typing import List, Dict

def chunk_text(
    text: str,
    chunk_size: int = 1000,
    overlap: int = 120,
    model: str = "gpt-4o-mini"
) -> List[Dict]:
    """
    Token-based chunking with overlap.
    Returns: [{id, content}]
    """

    encoding = tiktoken.encoding_for_model(model)
    tokens = encoding.encode(text)

    chunks = []
    start = 0
    chunk_id = 0

    while start < len(tokens):
        end = start + chunk_size
        chunk_tokens = tokens[start:end]
        chunk_text = encoding.decode(chunk_tokens)

        chunks.append({
            "id": chunk_id,
            "content": chunk_text
        })

        chunk_id += 1
        start = end - overlap  # 12% overlap

    return chunks


# def chunk_text(text, size=800, overlap=100):
#     chunks = []
#     start = 0

#     while start < len(text):
#         chunks.append(text[start:start+size])
#         start += size - overlap

#     return chunks
