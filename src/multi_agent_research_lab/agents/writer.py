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
            f"Audience: {state.request.audience}\n"
        )
        if state.critic_feedback:
            prompt += f"\nCritic Feedback on previous draft: {state.critic_feedback}\nPlease improve the draft based on this feedback."
        
        response = llm.complete(
            system_prompt="You are a writer. Synthesize a clear, final response based on the research and analysis notes.",
            user_prompt=prompt
        )
        state.final_answer = response.content
        state.critic_feedback = None  # Clear feedback after incorporating it
        state.add_trace_event("writer", {"cost_usd": response.cost_usd})
        return state
