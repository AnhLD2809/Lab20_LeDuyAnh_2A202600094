import time
from multi_agent_research_lab.cli import _init
from multi_agent_research_lab.core.schemas import ResearchQuery
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.services.llm_client import LLMClient
from multi_agent_research_lab.graph.workflow import MultiAgentWorkflow

def run_all():
    _init()
    query = "Research GraphRAG state-of-the-art and write a 500-word summary"
    
    # 1. Baseline
    t0 = time.perf_counter()
    llm = LLMClient()
    resp_baseline = llm.complete("You are a helpful assistant.", query)
    t1 = time.perf_counter()
    baseline_latency = t1 - t0
    
    # 2. Multi-agent
    t0 = time.perf_counter()
    workflow = MultiAgentWorkflow()
    state = ResearchState(request=ResearchQuery(query=query))
    resp_multi = workflow.run(state)
    t1 = time.perf_counter()
    multi_latency = t1 - t0
    
    print(f"BASELINE_LATENCY={baseline_latency:.2f}")
    print(f"MULTI_LATENCY={multi_latency:.2f}")

if __name__ == "__main__":
    run_all()
