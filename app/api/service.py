# app/api/service.py
import logging
import time
from typing import AsyncGenerator, Dict, Any

from app.agent.graph import build_graph, AgentState

logger = logging.getLogger("lira.api.service")

# Build the LangGraph workflow once at import time (fast access)
logger.info("Loading LangGraph workflow...")
workflow = build_graph()
logger.info("LangGraph workflow loaded.")

def _normalize_result(result: Any) -> Dict[str, Any]:
    """
    Normalize the output of workflow.invoke into a plain dict.
    Handles pydantic model, dict-like or custom object with attributes.
    """
    if result is None:
        return {}
    # If it's a pydantic model
    try:
        # Some StateGraph runtimes return pydantic BaseModel
        obj_to_dict = getattr(result, "dict", None)
        if callable(obj_to_dict):
            return result.dict()
    except Exception:
        pass

    # If it's a dict-like
    if isinstance(result, dict):
        return result

    # Fallback: inspect attributes
    data = {}
    for key in ("plan", "summary", "rag_answer", "final_answer", "blocked", "safety_note", "error"):
        if hasattr(result, key):
            data[key] = getattr(result, key)
    return data


def run_agent_sync(query: str) -> Dict[str, Any]:
    """
    Run the agent synchronously and return final state dict.
    """
    initial = AgentState(query=query)
    try:
        res = workflow.invoke(initial)
        normalized = _normalize_result(res)
        return normalized
    except Exception as e:
        logger.exception("Agent run failed")
        return {"error": f"{e}"}


def run_agent_event_stream(query: str):
    """
    Generator that yields intermediate events (for SSE).
    We'll yield events for plan, summary, rag_answer, final_answer, error, blocked.
    Note: the underlying workflow may run synchronously; we run it and yield stages as they appear.
    """
    initial = AgentState(query=query)

    # We'll attempt to fetch intermediate attributes after each node by invoking node-by-node.
    # If StateGraph doesn't expose node-level invocation, fall back to single-run and emit stages.
    try:
        # Try a full run and periodically emit stage updates
        # Emit initial notification
        yield {"event": "start", "data": "Agent run started"}

        res = workflow.invoke(initial)
        data = _normalize_result(res)

        # Emit plan, summary, rag_answer in order if present
        for key in ("plan", "summary", "rag_answer", "final_answer", "blocked", "safety_note", "error"):
            if key in data and data[key] is not None:
                yield {"event": key, "data": data[key]}
                # slight pause to allow client to render smoothly
                time.sleep(0.05)

        yield {"event": "done", "data": "Agent run completed"}
    except Exception as e:
        logger.exception("Error while running agent stream")
        yield {"event": "error", "data": str(e)}
