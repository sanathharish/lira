from pydantic import BaseModel

class QueryRequest(BaseModel):
    query: str

class AgentResponse(BaseModel):
    query: str
    plan: str | None = None
    summary: str | None = None
    rag_answer: str | None = None
    final_answer: str | None = None

    blocked: bool = False              # ← FIXED
    safety_note: str | None = None
    error: str | None = None