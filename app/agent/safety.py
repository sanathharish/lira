# app/agent/safety.py

"""
Safety utilities for the agent:
- Block clearly unsafe or disallowed queries
- Return simple reasons the agent refuses
"""

from typing import Tuple


BLOCKED_KEYWORDS = [
    "suicide",
    "kill myself",
    "kill him",
    "murder",
    "how to make a bomb",
    "bomb recipe",
    "child sexual",
    "csam",
    "hack wifi",
    "bypass password",
    "ddos",
]


def is_query_allowed(query: str) -> Tuple[bool, str | None]:
    """
    Very simple keyword-based safety check.
    In a real product you'd call a safety API or classifier instead.
    """
    q = query.lower()

    for word in BLOCKED_KEYWORDS:
        if word in q:
            return False, (
                "Your request touches on a topic I can't safely assist with. "
                "I’m designed to avoid helping with self-harm, violence, "
                "illegal activity, or exploitation."
            )

    # If no issues detected
    return True, None
