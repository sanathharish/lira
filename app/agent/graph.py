# app/agent/graph.py

"""
STEP 4: Build the skeleton of our Agent using LangGraph.
--------------------------------------------------------
This will:
- Define the graph
- Define node structure
- Show how data flows
- Prepare for adding tools, RAG, LLM steps
"""

from langgraph.graph import StateGraph, END
from pydantic import BaseModel

from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate

from app.agent.prompts import PLAN_PROMPT, SUMMARIZE_PROMPT
from app.agent.tools import web_search
from app.agent.memory import store_summary, rag_retrieve
from app.agent.safety import is_query_allowed




# ---------------------------------------------------
# Agent State Definition
# ---------------------------------------------------
class AgentState(BaseModel):
    """Shared state that passes through all nodes."""
    query: str
    plan: str | None = None
    search_results: str | None = None
    summary: str | None = None
    rag_answer: str | None = None
    final_answer: str | None = None

    # NEW: safety + error fields
    blocked: bool = False
    safety_note: str | None = None
    error: str | None = None



# ---------------------------------------------------
# Node functions (we will fill them later)
# ---------------------------------------------------
def plan_node(state: AgentState):
    """Use an LLM to generate a research plan, with safety guard."""

    # 1) Safety check
    allowed, reason = is_query_allowed(state.query)
    if not allowed:
        state.blocked = True
        state.safety_note = reason
        state.plan = "Blocked by safety filter."
        # We stop here logically; other nodes will be no-ops when blocked
        return state

    # 2) Normal planning
    llm = ChatOllama(model="llama3.2", temperature=0.2)
    prompt = ChatPromptTemplate.from_template(PLAN_PROMPT)
    chain = prompt | llm

    response = chain.invoke({"query": state.query})
    state.plan = response.content if hasattr(response, "content") else str(response)
    return state




def search_node(state: AgentState):
    if state.blocked or state.error:
        return state

    print("[search_node] Searching the web...")
    try:
        results = web_search(state.query)
        state.search_results = results
    except Exception as e:
        state.error = f"[search_node] {e}"
    return state




def summarize_node(state: AgentState):
    if state.blocked or state.error:
        return state

    print("[summarize_node] Summarizing search results...")

    llm = ChatOllama(model="llama3.2", temperature=0.2)
    prompt = ChatPromptTemplate.from_template(SUMMARIZE_PROMPT)
    chain = prompt | llm

    try:
        response = chain.invoke({"content": state.search_results})
        summary_text = response.content if hasattr(response, "content") else str(response)
        state.summary = summary_text

        print("[summarize_node] Storing summary into vector memory...")
        store_summary("agent_memory", summary_text)
    except Exception as e:
        state.error = f"[summarize_node] {e}"

    return state





def rag_node(state: AgentState):
    if state.blocked or state.error:
        return state

    print("[rag_node] Retrieving memory from vector DB...")

    try:
        context = rag_retrieve("agent_memory", state.query)
    except Exception as e:
        state.error = f"[rag_node] {e}"
        return state

    if not context:
        state.rag_answer = "I don't know based on the knowledge I stored so far."
        return state

    llm = ChatOllama(model="llama3.2", temperature=0.2)
    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            "Answer using ONLY the context provided. "
            "If the context is insufficient, say you don't know."
        ),
        ("human", "Context:\n{context}\n\nQuestion: {question}")
    ])
    chain = prompt | llm

    try:
        response = chain.invoke({
            "context": context,
            "question": state.query
        })
        state.rag_answer = response.content if hasattr(response, "content") else str(response)
    except Exception as e:
        state.error = f"[rag_node LLM] {e}"

    return state




def final_node(state: AgentState):
    print("[final_node] Composing final answer...")

    # 1) Safety block
    if state.blocked:
        state.final_answer = f"""
❌ Unable to answer this query safely.

Reason:
{state.safety_note}

Your original query was:
{state.query}
""".strip()
        return state

    # 2) Technical error
    if state.error:
        state.final_answer = f"""
⚠️ I ran into a technical issue while processing your request.

Details:
{state.error}

You can try again later, or simplify the query.
""".strip()
        return state

    # 3) Normal happy path
    final_output = f"""
=========== FINAL ANSWER ===========
🎯 User Query
{state.query}

🧠 Plan
{state.plan}

🔍 Summary of Research
{state.summary}

📚 Memory-Aware RAG Answer
{state.rag_answer}

------------------------------------
This response is grounded in:
- Real web search results
- Summaries generated by the agent
- Memory stored in ChromaDB
- Context-retrieved reasoning
====================================
"""
    state.final_answer = final_output.strip()
    return state




# ---------------------------------------------------
# Build the Agent Graph
# ---------------------------------------------------
def build_graph():
    graph = StateGraph(AgentState)

    # Define execution nodes
    graph.add_node("plan", plan_node)
    graph.add_node("search", search_node)
    graph.add_node("summarize", summarize_node)
    graph.add_node("rag", rag_node)
    graph.add_node("final", final_node)

    # Node connections
    graph.set_entry_point("plan")
    graph.add_edge("plan", "search")
    graph.add_edge("search", "summarize")
    graph.add_edge("summarize", "rag")
    graph.add_edge("rag", "final")
    graph.add_edge("final", END)

    return graph.compile()



# ---------------------------------------------------
# DEMO
# ---------------------------------------------------
def demo():
    workflow = build_graph()

    initial_state = AgentState(query="Explain quantum computing in simple terms.")
    result = workflow.invoke(initial_state)

    print("\n=== AGENT RESULT ===")
    print(result["final_answer"])


if __name__ == "__main__":
    demo()
