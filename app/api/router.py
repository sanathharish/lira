# app/api/router.py
from unittest import result
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from sse_starlette.sse import EventSourceResponse

from .models import QueryRequest, AgentResponse
from .service import run_agent_sync, run_agent_event_stream

api_router = APIRouter()

@api_router.post("/query", response_model=AgentResponse)
def query_sync(payload: QueryRequest):
    """
    Synchronous API: run the agent and return the final aggregated response.
    """
    result = run_agent_sync(payload.query)
    if "error" in result and result["error"]:
        raise HTTPException(status_code=500, detail=result["error"])
    # map keys to response model
    return AgentResponse(
        query=result["query"],                 # ← FIXED
        plan=result.get("plan"),
        summary=result.get("summary"),
        rag_answer=result.get("rag_answer"),
        final_answer=result.get("final_answer"),
        blocked=result.get("blocked"),
        safety_note=result.get("safety_note"),
        error=result.get("error"),
    )

@api_router.post("/query/stream")
async def query_stream(request: Request, payload: QueryRequest):
    """
    Streaming API (SSE). Client connects and receives events:
      - start
      - plan
      - summary
      - rag_answer
      - final_answer
      - done
      - error
    """
    def event_generator():
        for ev in run_agent_event_stream(payload.query):
            # Client disconnected?
            if await_disconnect(request):
                break
            yield {
                "event": ev.get("event", "message"),
                "data": ev.get("data")
            }

    # EventSourceResponse wants a sync generator or async generator. We'll provide sync generator of dicts.
    async def async_gen():
        for ev in run_agent_event_stream(payload.query):
            if await_disconnect(request):
                break
            # Format SSE message as text
            yield f"event: {ev.get('event')}\n"
            data = ev.get("data")
            # Convert non-string data to string
            yield f"data: {str(data)}\n\n"

    return EventSourceResponse(async_gen())

# small helper (can't await directly inside generator)
def await_disconnect(request: Request) -> bool:
    return False  # for now no early cancellation. Could be extended to check request.client disconnect
