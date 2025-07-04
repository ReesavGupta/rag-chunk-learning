# RAG Chunking Strategy Visualizer

A simple web application to upload PDF documents and visualize different chunking strategies for Retrieval-Augmented Generation (RAG) systems.

## Features
- **PDF Upload & Text Extraction:** Upload a PDF and extract its text for chunking.
- **Multiple Chunking Strategies:**
  - Fixed-size (by words)
  - Sentence-based
  - Paragraph-based
  - Sliding window (by words)
  - Regex delimiter (custom pattern)
- **Strategy Explanation:** See how each strategy works and adjust parameters.
- **Chunk Visualization:** View resulting chunks with metadata (size, overlap, etc).

## Technologies Used
- **Backend:** Python, FastAPI, PyPDF2
- **Frontend:** HTML, CSS, JavaScript (vanilla)

## Setup Instructions

### 1. Install Python dependencies
From the `rag-chunk` directory:
```bash
pip install -r requirements.txt
```

### 2. Run the FastAPI server
From the `rag-chunk` directory:
```bash
uvicorn app:app --reload
```

### 3. Open the app in your browser
Go to:
```
http://127.0.0.1:8000/
```

## Usage
1. Upload a PDF file.
2. Review the extracted text.
3. Select a chunking strategy and adjust its parameters.
4. Click "Chunk & Visualize" to see the resulting chunks and their metadata.

## Chunking Strategies Explained
- **Fixed-size (by words):** Splits text into chunks of N words, with optional overlap.
- **Sentence-based:** Splits text into chunks of N sentences, with optional overlap.
- **Paragraph-based:** Splits text into chunks of N paragraphs, with optional overlap.
- **Sliding Window (by words):** Overlapping windows of N words (good for context preservation).
- **Regex Delimiter:** Splits text using a custom regex delimiter (e.g., double newlines, headings, etc).

## Customization
- Add more chunking strategies in `app.py` as needed.
- Adjust frontend UI in `static/index.html`, `static/style.css`, and `static/app.js`.

## Notes
- Handles large PDFs, but performance depends on your system and file size.
- For best results, use clear and well-formatted PDFs.

## License
MIT

---

