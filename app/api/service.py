# app/api/service.py
import logging
import time
from typing import Dict, Any

from app.agent.graph import build_graph, AgentState

logger = logging.getLogger("lira.api.service")

logger.info("Loading LangGraph workflow...")
workflow = build_graph()
logger.info("LangGraph workflow loaded.")


def _normalize_result(result: Any) -> Dict[str, Any]:
    """
    Normalize LangGraph output into a plain dict.
    """
    if result is None:
        return {}

    # Pydantic model
    if hasattr(result, "model_dump"):
        return result.model_dump()

    if hasattr(result, "dict"):
        return result.dict()

    if isinstance(result, dict):
        return result

    data = {}
    for key in (
        "query",
        "plan",
        "summary",
        "rag_answer",
        "final_answer",
        "blocked",
        "safety_note",
        "error",
    ):
        if hasattr(result, key):
            data[key] = getattr(result, key)
    return data


def run_agent_sync(query: str) -> Dict[str, Any]:
    """
    Run agent and return normalized state.
    Always includes query.
    """
    initial = AgentState(query=query)

    try:
        res = workflow.invoke(initial)
        data = _normalize_result(res)

        # 🔒 Enforce minimal contract
        data.setdefault("query", query)
        data.setdefault("blocked", False)
        data.setdefault("error", None)

        return data

    except Exception as e:
        logger.exception("Agent run failed")
        return {
            "query": query,
            "blocked": False,
            "error": str(e),
        }


def run_agent_event_stream(query: str):
    """
    Simplified SSE generator.
    """
    yield {"event": "start", "data": "Agent started"}

    try:
        res = run_agent_sync(query)

        for key in (
            "plan",
            "summary",
            "rag_answer",
            "final_answer",
            "blocked",
            "safety_note",
            "error",
        ):
            if res.get(key) is not None:
                yield {"event": key, "data": res[key]}
                time.sleep(0.05)

        yield {"event": "done", "data": "Agent completed"}

    except Exception as e:
        yield {"event": "error", "data": str(e)}
