"""Researcher agent skeleton."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.errors import StudentTodoError
from multi_agent_research_lab.core.state import ResearchState


class ResearcherAgent(BaseAgent):
    """Collects sources and creates concise research notes."""

    name = "researcher"

    def run(self, state: ResearchState) -> ResearchState:
        from multi_agent_research_lab.services.llm_client import LLMClient
        from multi_agent_research_lab.services.search_client import SearchClient
        
        search_client = SearchClient()
        sources = search_client.search(state.request.query, max_results=state.request.max_sources)
        state.sources.extend(sources)
        
        llm = LLMClient()
        sources_text = "\n".join([f"- {s.title}: {s.snippet}" for s in sources])
        prompt = f"Query: {state.request.query}\nSources:\n{sources_text}"
        
        response = llm.complete(
            system_prompt="You are a researcher. Summarize the sources into concise research notes.",
            user_prompt=prompt
        )
        state.research_notes = response.content
        state.add_trace_event("researcher", {"cost_usd": response.cost_usd})
        return state
