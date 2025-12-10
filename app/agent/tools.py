# app/agent/tools.py

"""
Real web search tool using Tavily API.
"""

import os
from tavily import TavilyClient
from dotenv import load_dotenv

load_dotenv()

tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))


def web_search(query: str) -> str:
    """
    Returns search results as a clean text string for summarization.
    """
    results = tavily.search(query=query, max_results=3)

    final_text = ""

    for res in results["results"]:
        title = res.get("title", "")
        content = res.get("content", "")
        url = res.get("url", "")

        final_text += f"Title: {title}\nURL: {url}\n{content}\n\n"

    return final_text.strip()
