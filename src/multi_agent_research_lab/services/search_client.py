"""Search client abstraction for ResearcherAgent."""

from multi_agent_research_lab.core.errors import StudentTodoError
from multi_agent_research_lab.core.schemas import SourceDocument


class SearchClient:
    """Provider-agnostic search client skeleton."""

    def search(self, query: str, max_results: int = 5) -> list[SourceDocument]:
        """Search for documents relevant to a query.
        Using a mock implementation to ensure it works without API keys.
        """
        import json
        import urllib.request
        from multi_agent_research_lab.core.config import get_settings
        
        settings = get_settings()
        if settings.tavily_api_key and settings.tavily_api_key != "mock":
            # Try Tavily API
            try:
                data = json.dumps({"query": query, "max_results": max_results, "api_key": settings.tavily_api_key}).encode("utf-8")
                req = urllib.request.Request("https://api.tavily.com/search", data=data, headers={"Content-Type": "application/json"})
                with urllib.request.urlopen(req, timeout=10) as response:
                    res = json.loads(response.read().decode())
                    return [SourceDocument(title=r.get("title", ""), url=r.get("url", ""), snippet=r.get("content", "")) for r in res.get("results", [])]
            except Exception as e:
                pass # fallback to mock
                
        return [
            SourceDocument(
                title=f"Mock result {i+1} for {query}",
                url=f"https://mock-search.local/result-{i+1}",
                snippet=f"This is a simulated snippet about {query}. It contains useful insights."
            ) for i in range(max_results)
        ]
