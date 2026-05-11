"""
Web Search Tool - DDGS search (free, no API key needed)
"""

from langchain_core.tools import tool
import os
from datetime import datetime
import json
import config


@tool
def search_web(query: str) -> str:
    """Search the web using DuckDuckGo and return top results.
    Use for: current information, news, how-to guides, definitions.
    Example: search_web('Python tutorial for beginners')"""
    try:
        from ddgs import DDGS

        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=4))

        # Log tool usage
        try:
            os.makedirs(config.LOGS_DIR, exist_ok=True)
            with open(config.LOGS_DIR + "/tool_calls.log", "a", encoding="utf-8") as lf:
                lf.write(f"{datetime.utcnow().isoformat()} - search_web - {json.dumps({'query': query})}\n")
        except Exception:
            pass

        if not results:
            return f"❌ No results found for: {query}"

        output = [f"🔍 Web search results for: '{query}'\n"]
        for i, r in enumerate(results, 1):
            output.append(f"[{i}] {r['title']}")
            output.append(f"    {r['body'][:200]}...")
            output.append(f"    🔗 {r['href']}\n")

        return "\n".join(output)

    except ImportError:
        return "❌ ddgs not installed. Run: pip install ddgs"
    except Exception as e:
        return f"❌ Search error: {e}"
