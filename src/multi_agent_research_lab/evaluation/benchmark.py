"""Benchmark skeleton for single-agent vs multi-agent."""

from time import perf_counter
from typing import Callable
import json

from multi_agent_research_lab.core.schemas import BenchmarkMetrics
from multi_agent_research_lab.core.state import ResearchState


Runner = Callable[[str], ResearchState]


def run_benchmark(run_name: str, query: str, runner: Runner) -> tuple[ResearchState, BenchmarkMetrics]:
    from multi_agent_research_lab.services.llm_client import LLMClient
    
    started = perf_counter()
    state = runner(query)
    latency = perf_counter() - started
    
    # Calculate real cost from trace
    total_cost = 0.0
    for event in state.trace:
        payload = event.get("payload", {})
        if "cost_usd" in payload and payload["cost_usd"]:
            total_cost += payload["cost_usd"]
            
    # LLM-as-a-judge for quality and citation coverage
    llm = LLMClient()
    judge_prompt = (
        f"Query: {query}\n"
        f"Final Answer: {state.final_answer}\n\n"
        "Evaluate the final answer based on the following criteria:\n"
        "1. Quality (0 to 10): How well does it answer the query?\n"
        "2. Citation Coverage (0.0 to 1.0): Are claims backed by citations like [1]? If many citations exist, give close to 1.0. If no citations, 0.0.\n"
        "Return JSON format: {\"quality\": 8.5, \"citation_coverage\": 0.9}\n"
    )
    
    response = llm.complete(
        system_prompt="You are an expert evaluator.",
        user_prompt=judge_prompt
    )
    
    content = response.content.strip()
    if content.startswith("```json"):
        content = content[7:-3].strip()
    elif content.startswith("```"):
        content = content[3:-3].strip()
        
    quality_score = 6.5
    citation_coverage = 0.0
    try:
        data = json.loads(content)
        quality_score = float(data.get("quality", 6.5))
        citation_coverage = float(data.get("citation_coverage", 0.0))
    except (json.JSONDecodeError, ValueError):
        pass
        
    failure_rate = 1.0 if not state.final_answer or len(state.final_answer) < 20 else 0.0
    
    metrics = BenchmarkMetrics(
        run_name=run_name, 
        latency_seconds=latency,
        estimated_cost_usd=total_cost,
        quality_score=quality_score,
        citation_coverage=citation_coverage,
        failure_rate=failure_rate
    )
    return state, metrics
