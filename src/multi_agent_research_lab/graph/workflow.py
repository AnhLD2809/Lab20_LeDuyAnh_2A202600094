"""LangGraph workflow skeleton."""

from multi_agent_research_lab.core.errors import StudentTodoError
from multi_agent_research_lab.core.state import ResearchState


class MultiAgentWorkflow:
    """Builds and runs the multi-agent graph.

    Keep orchestration here; keep agent internals in `agents/`.
    """

    def build(self) -> object:
        from langgraph.graph import StateGraph, START, END
        from typing import TypedDict
        from multi_agent_research_lab.agents.supervisor import SupervisorAgent
        from multi_agent_research_lab.agents.researcher import ResearcherAgent
        from multi_agent_research_lab.agents.analyst import AnalystAgent
        from multi_agent_research_lab.agents.writer import WriterAgent
        
        class StateDict(TypedDict):
            state: ResearchState
            
        workflow = StateGraph(StateDict)
        
        def run_supervisor(data: StateDict):
            return {"state": SupervisorAgent().run(data["state"])}
        def run_researcher(data: StateDict):
            return {"state": ResearcherAgent().run(data["state"])}
        def run_analyst(data: StateDict):
            return {"state": AnalystAgent().run(data["state"])}
        def run_writer(data: StateDict):
            return {"state": WriterAgent().run(data["state"])}
            
        workflow.add_node("supervisor", run_supervisor)
        workflow.add_node("researcher", run_researcher)
        workflow.add_node("analyst", run_analyst)
        workflow.add_node("writer", run_writer)
        
        workflow.add_edge(START, "supervisor")
        
        def route(data: StateDict):
            st = data["state"]
            if not st.route_history:
                return END
            last = st.route_history[-1]
            if last == "done":
                return END
            return last
            
        workflow.add_conditional_edges("supervisor", route)
        workflow.add_edge("researcher", "supervisor")
        workflow.add_edge("analyst", "supervisor")
        workflow.add_edge("writer", "supervisor")
        
        return workflow.compile()

    def run(self, state: ResearchState) -> ResearchState:
        app = self.build()
        result = app.invoke({"state": state})
        return result["state"]
