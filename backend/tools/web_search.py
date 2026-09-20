import httpx
from typing import Dict, Any, List


def search_web(query: str, max_results: int = 5) -> Dict[str, Any]:
    """Execute a safe web search and return structured source results."""
    clean_query = query.strip()
    if not clean_query:
        return {
            "success": False,
            "error": "Search query cannot be empty.",
            "results": []
        }

    results: List[Dict[str, str]] = []

    # 1. Query DuckDuckGo Instant Answer API
    try:
        url = "https://api.duckduckgo.com/"
        params = {
            "q": clean_query,
            "format": "json",
            "no_html": "1",
            "skip_disambig": "1"
        }
        with httpx.Client(timeout=6.0) as client:
            resp = client.get(url, params=params)
            if resp.status_code == 200:
                data = resp.json()
                if data.get("AbstractText"):
                    results.append({
                        "title": data.get("Heading") or clean_query.title(),
                        "source": data.get("AbstractSource") or "DuckDuckGo",
                        "summary": data.get("AbstractText"),
                        "url": data.get("AbstractURL") or "https://duckduckgo.com"
                    })
                
                # Related topics
                for topic in data.get("RelatedTopics", [])[:max_results]:
                    if isinstance(topic, dict) and "Text" in topic:
                        results.append({
                            "title": topic.get("Text", "").split(" - ")[0],
                            "source": "DuckDuckGo Topic",
                            "summary": topic.get("Text", ""),
                            "url": topic.get("FirstURL", "https://duckduckgo.com")
                        })
    except Exception:
        pass

    # 2. Query Wikipedia API if results are few
    if len(results) < 2:
        try:
            wiki_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{clean_query.replace(' ', '_')}"
            with httpx.Client(timeout=6.0) as client:
                resp = client.get(wiki_url)
                if resp.status_code == 200:
                    wiki_data = resp.json()
                    if "extract" in wiki_data:
                        results.append({
                            "title": wiki_data.get("title", clean_query),
                            "source": "Wikipedia",
                            "summary": wiki_data.get("extract"),
                            "url": wiki_data.get("content_urls", {}).get("desktop", {}).get("page", "https://wikipedia.org")
                        })
        except Exception:
            pass

    # 3. Fallback educational result if offline / network disconnected
    if not results:
        results.append({
            "title": f"Information on '{clean_query}'",
            "source": "SADIE Knowledge Base",
            "summary": f"Search results for '{clean_query}'. For live internet browsing, ensure internet connectivity.",
            "url": f"https://duckduckgo.com/?q={clean_query.replace(' ', '+')}"
        })

    return {
        "success": True,
        "query": clean_query,
        "count": len(results),
        "results": results[:max_results]
    }
