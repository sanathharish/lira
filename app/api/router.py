# app/api/router.py
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from fastapi.requests import Request
from sse_starlette.sse import EventSourceResponse

from .models import QueryRequest, AgentResponse
from .service import run_agent_sync, run_agent_event_stream

api_router = APIRouter()


@api_router.post("/query", response_model=AgentResponse)
def query_sync(payload: QueryRequest):
    """
    Stable synchronous API.
    """
    result = run_agent_sync(payload.query)

    if result.get("error"):
        raise HTTPException(status_code=500, detail=result["error"])

    return AgentResponse(
        query=result["query"],
        plan=result.get("plan"),
        summary=result.get("summary"),
        rag_answer=result.get("rag_answer"),
        final_answer=result.get("final_answer"),
        blocked=result.get("blocked", False),
        safety_note=result.get("safety_note"),
        error=result.get("error"),
    )


@api_router.post("/query/stream")
async def query_stream(payload: QueryRequest):
    """
    SSE endpoint.
    """
    async def event_gen():
        for ev in run_agent_event_stream(payload.query):
            yield {
                "event": ev["event"],
                "data": str(ev.get("data", "")),
            }

    return EventSourceResponse(event_gen())
