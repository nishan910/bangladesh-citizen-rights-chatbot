from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.schemas import ChatRequest, ChatResponse

app = FastAPI(
    title="Bangladesh Citizen Rights Chatbot API",
    description="A Bangla chatbot for understanding Bangladesh laws and citizen rights.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "message": "Bangladesh Citizen Rights Chatbot API is running",
        "status": "ok",
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    return ChatResponse(
        answer=(
            f"আপনার প্রশ্নটি গ্রহণ করা হয়েছে: {request.question}। "
            "এটি পরীক্ষামূলক উত্তর। নির্ভরযোগ্য আইনগত তথ্য যাচাইয়ের ব্যবস্থা "
            "এখনো যুক্ত করা হয়নি।"
        ),
        sources=[],
    )
