from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    question: str = Field(
        min_length=2,
        max_length=2000,
        description="User question in Bangla or English",
    )


class ChatResponse(BaseModel):
    answer: str
    sources: list[str] = []
