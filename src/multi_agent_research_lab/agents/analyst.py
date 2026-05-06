"""Analyst agent skeleton."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.errors import StudentTodoError
from multi_agent_research_lab.core.state import ResearchState


class AnalystAgent(BaseAgent):
    """Turns research notes into structured insights."""

    name = "analyst"

    def run(self, state: ResearchState) -> ResearchState:
        from multi_agent_research_lab.services.llm_client import LLMClient
        
        llm = LLMClient()
        prompt = f"Research Notes: {state.research_notes}"
        
        response = llm.complete(
            system_prompt="You are an analyst. Extract key themes and logical connections from the research notes.",
            user_prompt=prompt
        )
        state.analysis_notes = response.content
        state.add_trace_event("analyst", {"cost_usd": response.cost_usd})
        return state
