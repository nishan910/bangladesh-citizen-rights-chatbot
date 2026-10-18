# Bangladesh Citizen Rights Chatbot

A Bangla AI-powered chatbot that helps users understand Bangladeshi laws using Retrieval-Augmented Generation (RAG), a Groq LLM, and a React frontend.

## Features

- Answers legal questions in Bengali.
- Retrieves relevant legal text from a Chroma vector database.
- Uses Groq LLM to generate responses.
- Provides a React-based chat interface.
- Includes Bengali OCR support for scanned legal PDFs.
- Built with FastAPI, Python, React, and Vite.

## Technology Stack

- **Frontend:** React, Vite
- **Backend:** Python, FastAPI
- **LLM:** Groq API
- **RAG / Vector Database:** ChromaDB
- **Embeddings:** `paraphrase-multilingual-MiniLM-L12-v2`
- **PDF Processing / OCR:** PyMuPDF, Tesseract OCR

## Requirements

- Python 3.13
- Node.js and npm
- A Groq API key
- Tesseract OCR with Bengali language data (for scanned legal PDFs)

## Setup

### 1. Clone or open the project

Open the project folder in VS Code.

### 2. Configure environment variables

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key
```

Never commit your real API key to Git.

### 3. Start the backend

Activate your virtual environment and install the project's Python dependencies if needed.

From the project root, run:

```powershell
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```

Backend API: `http://127.0.0.1:8000`

API documentation: `http://127.0.0.1:8000/docs`

### 4. Start the frontend

Open a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open the local URL shown by Vite, usually `http://localhost:5173`.

## Legal Data

The chatbot uses processed legal documents stored in `data/processed/` and a Chroma vector database in `data/processed/chroma_db/`.

The project includes Bengali OCR support for selected scanned legal documents.

## Important Notice

This chatbot provides general legal information for educational purposes. It is not a substitute for advice from a qualified lawyer. Verify important legal matters using official legal sources.

## Project Status

Core backend and frontend are working locally. Testing, documentation, and deployment are ongoing.
