"""Command-line entrypoint for the lab starter."""

from typing import Annotated

import typer
from rich.console import Console
from rich.panel import Panel

from multi_agent_research_lab.core.config import get_settings
from multi_agent_research_lab.core.errors import StudentTodoError
from multi_agent_research_lab.core.schemas import ResearchQuery
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.graph.workflow import MultiAgentWorkflow
from multi_agent_research_lab.observability.logging import configure_logging

app = typer.Typer(help="Multi-Agent Research Lab starter CLI")
console = Console()


def _init() -> None:
    from dotenv import load_dotenv
    load_dotenv()
    settings = get_settings()
    configure_logging(settings.log_level)


@app.command()
def baseline(
    query: Annotated[str, typer.Option("--query", "-q", help="Research query")],
) -> None:
    """Run a minimal single-agent baseline placeholder."""

    _init()
    request = ResearchQuery(query=query)
    state = ResearchState(request=request)
    from multi_agent_research_lab.services.llm_client import LLMClient
    from time import perf_counter
    
    llm = LLMClient()
    t0 = perf_counter()
    response = llm.complete("You are a helpful research assistant. Answer the user query clearly.", query)
    t1 = perf_counter()
    state.final_answer = response.content
    state.add_trace_event("baseline_complete", {"latency": t1 - t0})
    console.print(Panel.fit(state.final_answer, title="Single-Agent Baseline"))


@app.command("multi-agent")
def multi_agent(
    query: Annotated[str, typer.Option("--query", "-q", help="Research query")],
) -> None:
    """Run the multi-agent workflow skeleton."""

    _init()
    state = ResearchState(request=ResearchQuery(query=query))
    workflow = MultiAgentWorkflow()
    try:
        result = workflow.run(state)
    except StudentTodoError as exc:
        console.print(Panel.fit(str(exc), title="Expected TODO", style="yellow"))
        raise typer.Exit(code=2) from exc
    console.print(result.model_dump_json(indent=2))


@app.command("benchmark-all")
def benchmark_all(
    config_path: Annotated[str, typer.Option("--config", "-c", help="Path to config yaml")] = "configs/lab_default.yaml",
) -> None:
    """Run benchmark for all queries in config and generate report."""
    import yaml
    from multi_agent_research_lab.evaluation.benchmark import run_benchmark
    from multi_agent_research_lab.evaluation.report import render_markdown_report
    from multi_agent_research_lab.services.llm_client import LLMClient
    from multi_agent_research_lab.core.schemas import BenchmarkMetrics
    
    _init()
    
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
        
    queries = config.get("benchmark", {}).get("queries", [])
    if not queries:
        console.print("[red]No queries found in config.[/red]")
        return
        
    metrics = []
    llm = LLMClient()
    workflow = MultiAgentWorkflow()
    
    for i, q in enumerate(queries):
        console.print(f"[bold cyan]Benchmarking Query {i+1}/{len(queries)}:[/bold cyan] {q}")
        
        # Baseline Runner
        def run_baseline(query_str: str) -> ResearchState:
            st = ResearchState(request=ResearchQuery(query=query_str))
            resp = llm.complete("You are a helpful research assistant. Answer the user query clearly.", query_str)
            st.final_answer = resp.content
            st.add_trace_event("baseline_call", {"cost_usd": resp.cost_usd})
            return st
            
        _, b_metrics = run_benchmark(f"Q{i+1} Baseline", q, run_baseline)
        b_metrics.notes = "Baseline run"
        metrics.append(b_metrics)
        
        # Multi-agent Runner
        def run_multi(query_str: str) -> ResearchState:
            st = ResearchState(request=ResearchQuery(query=query_str))
            return workflow.run(st)
            
        _, m_metrics = run_benchmark(f"Q{i+1} Multi-Agent", q, run_multi)
        m_metrics.notes = "Multi-agent run with Critic"
        metrics.append(m_metrics)
        
    report = render_markdown_report(metrics)
    
    # Add failure mode explanation at the end
    report += "\n## 2. Failure Mode và Cách Fix\n\n"
    report += "**Failure Mode:**\nĐôi khi API tìm kiếm trả về thông tin không liên quan, hoặc giới hạn query limit khiến Researcher không có dữ liệu. Do đó, Final Answer của Writer bị thiếu hụt hoặc phải bịa ra. Hoặc hệ thống bị rơi vào infinite loop (Researcher -> Analyst -> Researcher...) nếu Agent router đưa ra quyết định lặp lại do thiếu dữ kiện.\n\n"
    report += "**Cách Fix:**\n- Thêm cơ chế Fallback (dùng mock search data) nếu API fail.\n- Thêm Guardrail (timeout, max iterations) trong `SupervisorAgent` để bắt buộc dừng nếu đi qua quá nhiều vòng lặp (đã implement).\n- Prompts cần chặt chẽ: Dạy cho Writer biết rằng 'nếu không có thông tin từ notes, hãy nói rằng không tìm thấy, không được tự động bịa ra'.\n"

    # Add Exit Ticket answers
    report += "\n## 3. Exit Ticket\n\n"
    report += "**1. Case nào nên dùng multi-agent? Vì sao?**\n"
    report += "Nên dùng multi-agent cho các bài toán phức tạp (complex tasks) đòi hỏi nhiều bước xử lý, phân quyền rõ ràng, và cần kết hợp nhiều công cụ hoặc vai trò chuyên biệt (như tìm kiếm thông tin chuyên sâu, phân tích dữ liệu, viết báo cáo tổng hợp). Vì mỗi agent có thể được tối ưu prompt và context riêng biệt (giảm hallucination), và dễ dàng quản lý state cũng như debug khi có lỗi ở một bước cụ thể.\n\n"
    report += "**2. Case nào không nên dùng multi-agent? Vì sao?**\n"
    report += "Không nên dùng multi-agent cho các bài toán đơn giản (như simple QA, summarization ngắn), các tác vụ tra cứu nhanh, hoặc khi hệ thống có yêu cầu nghiêm ngặt về độ trễ cực thấp (low latency). Vì hệ thống multi-agent sẽ gây ra overhead lớn về số lượng token (do phải truyền state qua lại giữa các agent), làm tăng chi phí API và kéo dài thời gian chờ (wall-clock time cao).\n"
    
    with open("reports/benchmark_report.md", "w", encoding="utf-8") as f:
        f.write(report)
        
    console.print("[bold green]Benchmark complete! Report saved to reports/benchmark_report.md[/bold green]")

if __name__ == "__main__":
    app()
