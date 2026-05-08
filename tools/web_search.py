"""
Web Search Tool - DuckDuckGo search (free, no API key needed)
"""

from langchain.tools import tool


@tool
def search_web(query: str) -> str:
    """Search the web using DuckDuckGo and return top results.
    Use for: current information, news, how-to guides, definitions.
    Example: search_web('Python tutorial for beginners')"""
    try:
        from duckduckgo_search import DDGS
        
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=4))

        if not results:
            return f"❌ No results found for: {query}"

        output = [f"🔍 Web search results for: '{query}'\n"]
        for i, r in enumerate(results, 1):
            output.append(f"[{i}] {r['title']}")
            output.append(f"    {r['body'][:200]}...")
            output.append(f"    🔗 {r['href']}\n")

        return "\n".join(output)

    except ImportError:
        return "❌ duckduckgo-search not installed. Run: pip install duckduckgo-search"
    except Exception as e:
        return f"❌ Search error: {e}"
