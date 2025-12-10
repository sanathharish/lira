# app/agent/prompts.py

PLAN_PROMPT = """
You are an AI research planner. 
Your job is to break down the user query into actionable steps.

User Query:
{query}

Create a plan with 4 sections:
1. Objective — what the query is trying to achieve
2. Steps — step-by-step process (search, summarize, store, retrieve)
3. Tools Needed — list tools required (web_search, summarizer, rag)
4. Final Output Format — what the final answer should look like

Return ONLY valid JSON with keys: objective, steps, tools, output_format
"""

SUMMARIZE_PROMPT = """
You are an expert summarizer AI.
Summarize the following content into clear, concise key points.

Content:
{content}

Your summary MUST include:
- key facts
- important insights
- definitions (if needed)
- skip filler text
"""
