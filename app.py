from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from typing import List, Dict
import os
import io
from PyPDF2 import PdfReader
import re

app = FastAPI()

# Serve static files (frontend)
app.mount("/static", StaticFiles(directory="c:/Users/REESAV/Desktop/misogi-assignments/day-8/rag-chunk/static"), name="static")

# --- PDF Extraction ---
def extract_text_from_pdf(file: UploadFile) -> str:
    reader = PdfReader(file.file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

# --- Chunking Strategies ---
def fixed_size_chunks(text: str, size: int = 500, overlap: int = 0) -> List[Dict]:
    words = text.split()
    chunks = []
    i = 0
    while i < len(words):
        chunk_words = words[i:i+size]
        chunk = " ".join(chunk_words)
        chunks.append({
            "text": chunk,
            "start": i,
            "end": i+len(chunk_words),
            "size": len(chunk_words),
            "overlap": overlap
        })
        if overlap > 0:
            i += size - overlap
        else:
            i += size
    return chunks

def sentence_chunks(text: str, size: int = 5, overlap: int = 0) -> List[Dict]:
    sentences = re.split(r'(?<=[.!?]) +', text)
    chunks = []
    i = 0
    while i < len(sentences):
        chunk_sents = sentences[i:i+size]
        chunk = " ".join(chunk_sents)
        chunks.append({
            "text": chunk,
            "start": i,
            "end": i+len(chunk_sents),
            "size": len(chunk_sents),
            "overlap": overlap
        })
        if overlap > 0:
            i += size - overlap
        else:
            i += size
    return chunks

# --- Additional Chunking Strategies ---
def paragraph_chunks(text: str, size: int = 2, overlap: int = 0) -> List[Dict]:
    paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
    chunks = []
    i = 0
    while i < len(paragraphs):
        chunk_paras = paragraphs[i:i+size]
        chunk = "\n\n".join(chunk_paras)
        chunks.append({
            "text": chunk,
            "start": i,
            "end": i+len(chunk_paras),
            "size": len(chunk_paras),
            "overlap": overlap
        })
        if overlap > 0:
            i += size - overlap
        else:
            i += size
    return chunks

def sliding_window_chunks(text: str, size: int = 100, overlap: int = 50) -> List[Dict]:
    words = text.split()
    chunks = []
    i = 0
    while i < len(words):
        chunk_words = words[i:i+size]
        chunk = " ".join(chunk_words)
        chunks.append({
            "text": chunk,
            "start": i,
            "end": i+len(chunk_words),
            "size": len(chunk_words),
            "overlap": overlap
        })
        if len(chunk_words) < size:
            break
        i += size - overlap if overlap > 0 else size
    return chunks

def regex_delimiter_chunks(text: str, pattern: str = r'\n\n+', size: int = 1, overlap: int = 0) -> List[Dict]:
    # Split by regex pattern (e.g., double newlines for paragraphs, or custom)
    splits = re.split(pattern, text)
    chunks = []
    i = 0
    while i < len(splits):
        chunk_parts = splits[i:i+size]
        chunk = "\n\n".join(chunk_parts)
        chunks.append({
            "text": chunk,
            "start": i,
            "end": i+len(chunk_parts),
            "size": len(chunk_parts),
            "overlap": overlap,
            "pattern": pattern
        })
        if overlap > 0:
            i += size - overlap
        else:
            i += size
    return chunks

STRATEGIES = {
    "fixed": {
        "name": "Fixed-size (by words)",
        "func": fixed_size_chunks,
        "explanation": "Splits text into chunks of N words, optionally with overlap.",
        "params": {"size": 500, "overlap": 0}
    },
    "sentence": {
        "name": "Sentence-based",
        "func": sentence_chunks,
        "explanation": "Splits text into chunks of N sentences, optionally with overlap.",
        "params": {"size": 5, "overlap": 0}
    },
    "paragraph": {
        "name": "Paragraph-based",
        "func": paragraph_chunks,
        "explanation": "Splits text into chunks of N paragraphs, optionally with overlap.",
        "params": {"size": 2, "overlap": 0}
    },
    "sliding_window": {
        "name": "Sliding Window (by words)",
        "func": sliding_window_chunks,
        "explanation": "Splits text into overlapping windows of N words (good for context preservation).",
        "params": {"size": 100, "overlap": 50}
    },
    "regex_delimiter": {
        "name": "Regex Delimiter",
        "func": regex_delimiter_chunks,
        "explanation": "Splits text using a custom regex delimiter (e.g., double newlines, headings, etc).",
        "params": {"pattern": r"\\n\\n+", "size": 1, "overlap": 0}
    }
}

@app.post("/api/upload")
async def upload_pdf(file: UploadFile = File(...)):
    try:
        text = extract_text_from_pdf(file)
        return {"text": text}
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": str(e)})

@app.post("/api/chunk")
async def chunk_text(
    text: str = Form(...),
    strategy: str = Form(...),
    size: int = Form(500),
    overlap: int = Form(0)
):
    if strategy not in STRATEGIES:
        return JSONResponse(status_code=400, content={"error": "Unknown strategy"})
    func = STRATEGIES[strategy]["func"]
    chunks = func(text, size=size, overlap=overlap)
    return {"chunks": chunks, "meta": {"strategy": strategy, "size": size, "overlap": overlap}}

@app.get("/api/strategies")
def get_strategies():
    return {k: {"name": v["name"], "explanation": v["explanation"], "params": v["params"]} for k, v in STRATEGIES.items()}

@app.get("/")
def index():
    with open("c:/Users/REESAV/Desktop/misogi-assignments/day-8/rag-chunk/static/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())
