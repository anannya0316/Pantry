import os

import requests as http_requests


def tavily_search(query: str, max_results: int = 3) -> str:
    api_key = os.getenv("TAVILY_API_KEY")

    if not api_key:
        return ""

    try:
        response = http_requests.post(
            "https://api.tavily.com/search",
            json={
                "api_key": api_key,
                "query": query,
                "max_results": max_results,
                "search_depth": "basic"
            },
            timeout=10
        )

        if response.status_code != 200:
            return ""

        results = response.json().get("results", [])

        snippets = [
            r.get("content", "")
            for r in results
            if r.get("content")
        ]

        return "\n\n".join(snippets)

    except Exception as e:
        print(f"[tavily] search error: {e}")
        return ""
