"""Optional critic agent skeleton for bonus work."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.errors import StudentTodoError
from multi_agent_research_lab.core.state import ResearchState


class CriticAgent(BaseAgent):
    """Optional fact-checking and safety-review agent."""

    name = "critic"

    def run(self, state: ResearchState) -> ResearchState:
        from multi_agent_research_lab.services.llm_client import LLMClient
        import json
        
        llm = LLMClient()
        prompt = (
            f"Query: {state.request.query}\n"
            f"Final Answer: {state.final_answer}\n"
        )
        
        system_prompt = (
            "You are a critic. Review the Final Answer against the original Query. "
            "Ensure the answer is accurate, well-formatted, and completely answers the query. "
            "Return a JSON object with 'is_approved' (boolean) and 'feedback' (string with suggestions or 'Looks good')."
        )
        
        response = llm.complete(
            system_prompt=system_prompt,
            user_prompt=prompt
        )
        
        content = response.content.strip()
        if content.startswith("```json"):
            content = content[7:-3].strip()
        elif content.startswith("```"):
            content = content[3:-3].strip()
            
        try:
            result = json.loads(content)
            state.is_approved = result.get("is_approved", False)
            state.critic_feedback = result.get("feedback", "No feedback provided.")
        except json.JSONDecodeError:
            state.is_approved = False
            state.critic_feedback = "Failed to parse critic feedback. Please try to refine the answer."
            
        state.add_trace_event("critic", {"cost_usd": response.cost_usd})
        return state
