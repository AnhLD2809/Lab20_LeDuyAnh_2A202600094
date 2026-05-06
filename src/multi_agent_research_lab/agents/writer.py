"""Writer agent skeleton."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.errors import StudentTodoError
from multi_agent_research_lab.core.state import ResearchState


class WriterAgent(BaseAgent):
    """Produces final answer from research and analysis notes."""

    name = "writer"

    def run(self, state: ResearchState) -> ResearchState:
        from multi_agent_research_lab.services.llm_client import LLMClient
        
        llm = LLMClient()
        prompt = (
            f"Query: {state.request.query}\n"
            f"Research Notes: {state.research_notes}\n"
            f"Analysis Notes: {state.analysis_notes}\n"
            f"Audience: {state.request.audience}"
        )
        
        response = llm.complete(
            system_prompt="You are a writer. Synthesize a clear, final response based on the research and analysis notes.",
            user_prompt=prompt
        )
        state.final_answer = response.content
        return state
