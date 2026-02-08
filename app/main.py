import time
import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from ingest import ingest_text
from ask import ask_question

app = FastAPI(title="Mini RAG System")

# ---------------- STATIC FILES ----------------
if os.path.isdir("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# ---------------- SCHEMAS ----------------
class IngestRequest(BaseModel):
    text: str

class AskRequest(BaseModel):
    question: str

# ---------------- UI ----------------
@app.get("/", response_class=HTMLResponse)
def ui():
    return """
<!DOCTYPE html>
<html>
<head>
    <title>Mini RAG System</title>
    <style>
        body {
            background: #0f172a;
            color: #e5e7eb;
            font-family: Arial;
            padding: 40px;
        }
        textarea, input {
            width: 100%;
            background: #020617;
            color: white;
            border: 1px solid #1e293b;
            padding: 12px;
            border-radius: 8px;
        }
        button {
            margin-top: 10px;
            background: #38bdf8;
            border: none;
            padding: 10px 20px;
            border-radius: 8px;
            cursor: pointer;
            font-weight: bold;
        }
        pre {
            background: #020617;
            padding: 15px;
            border-radius: 8px;
            margin-top: 20px;
        }
    </style>
</head>
<body>

<h1>🔎 Mini RAG System</h1>

<h2>📄 Ingest Text</h2>
<textarea id="ingestText" rows="6"
placeholder="Paste documents, notes, or articles here..."></textarea>
<button onclick="ingest()">Ingest</button>

<h2>❓ Ask Question</h2>
<input id="question" placeholder="Ask something..."/>
<button onclick="ask()">Ask</button>

<pre id="output"></pre>

<script>
async function ingest() {
    const text = document.getElementById("ingestText").value;
    const res = await fetch("/ingest", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ text })
    });
    document.getElementById("output").innerText = await res.text();
}

async function ask() {
    const question = document.getElementById("question").value;
    const res = await fetch("/ask", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ question })
    });
    document.getElementById("output").innerText = await res.text();
}
</script>

</body>
</html>
"""
# 🔴 HTML STRING ENDS HERE — THIS WAS THE BUG
# ---------------- ROUTES ----------------

@app.post("/ingest")
def ingest(data: IngestRequest):
    start = time.perf_counter()
    result = ingest_text(data.text)
    elapsed_ms = int((time.perf_counter() - start) * 1000)
    return {**result, "latency_ms": elapsed_ms}

@app.post("/ask")
def ask(data: AskRequest):
    start = time.perf_counter()
    result = ask_question(data.question)
    elapsed_ms = int((time.perf_counter() - start) * 1000)

    tokens = result.get("tokens", {})
    total_tokens = tokens.get("prompt", 0) + tokens.get("completion", 0)
    est_cost = round(total_tokens / 1000 * 0.01, 4)

    return {
        **result,
        "latency_ms": elapsed_ms,
        "cost_estimate_usd": est_cost,
    }
