# Multi-Agent Research System

Dự án này là bài Lab hoàn thiện về **Multi-Agent Systems**, được xây dựng dựa trên kiến trúc Supervisor + Worker Agents. Hệ thống cho phép thực hiện tự động hoá các luồng nghiên cứu bao gồm tìm kiếm, phân tích và tổng hợp thông tin, sau đó so sánh hiệu năng với phương pháp truyền thống Single-agent.

## Những gì đã thực hiện

1. **Implement đầy đủ Worker Agents**: 
   - `ResearcherAgent`: Sử dụng `Tavily` (hoặc Mock Data) để thu thập dữ liệu web và tóm tắt thành các `research_notes`.
   - `AnalystAgent`: Đọc `research_notes` để suy luận, phân tích chéo và trích xuất `analysis_notes`.
   - `WriterAgent`: Tổng hợp dữ liệu thành câu trả lời cuối cùng (`final_answer`) có đánh dấu trích dẫn đầy đủ.
2. **Xây dựng hệ thống điều phối (Supervisor / Router)**: 
   - Điều hướng (routing) các Agent tuần tự dựa trên logic của LangGraph.
   - Thêm Guardrails (Giới hạn vòng lặp `max_iterations`, Fallbacks).
3. **Cấu hình LLM & Search Client thực tế**:
   - Tích hợp thành công `openai` qua `LLMClient` để chạy mô hình `gpt-4o-mini`.
   - Tích hợp LangSmith qua `langsmith.wrappers` để tự động Trace từng token và node.
4. **Viết công cụ Benchmark đa truy vấn (Multi-Query Benchmark)**:
   - Viết lệnh CLI mới `benchmark-all` giúp đọc một loạt danh sách câu hỏi từ `configs/lab_default.yaml`.
   - Tự động chạy và so sánh (baseline vs multi-agent) rồi ghi kết quả chi tiết ra báo cáo markdown.

## Kiến trúc hệ thống

```text
User Query
   |
   v
Supervisor / Router (LangGraph)
   |------> Researcher Agent  -> Tạo research_notes (Sử dụng Tavily)
   |------> Analyst Agent     -> Tạo analysis_notes
   |------> Writer Agent      -> Tạo final_answer
   |
   v
Trace (LangSmith) + Benchmark Report
```

## Cách cài đặt và chạy Repository

### 1. Cài đặt môi trường

```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -e "[dev,llm]"
```

### 2. Thiết lập biến môi trường
Tạo file `.env` (nếu chưa có) và đảm bảo các API keys được điền đầy đủ:
```env
OPENAI_API_KEY=sk-...
TAVILY_API_KEY=tvly-...

# LangSmith Tracing
LANGCHAIN_API_KEY=lsv2_...
LANGCHAIN_PROJECT=multi-agent-research-lab
LANGCHAIN_TRACING_V2=true
```

### 3. Cách chạy các công cụ

**Chạy thử nghiệm lệnh Baseline (Single-Agent):**
```bash
python -m multi_agent_research_lab.cli baseline --query "Research GraphRAG state-of-the-art"
```

**Chạy thử nghiệm hệ thống Multi-Agent:**
```bash
python -m multi_agent_research_lab.cli multi-agent --query "Research GraphRAG state-of-the-art"
```

**Chạy Benchmark hàng loạt (Automated Benchmark):**
Lệnh này sẽ tự động chạy toàn bộ các câu hỏi đã cấu hình trong `configs/lab_default.yaml` và xuất kết quả ra thư mục `reports/benchmark_report.md`.
```bash
python -m multi_agent_research_lab.cli benchmark-all
```

## Kết quả đánh giá (Benchmark Results)

Sau khi chạy thực tế với mô hình `gpt-4o-mini`, hệ thống Multi-Agent tỏ ra vượt trội hoàn toàn về mặt chất lượng đầu ra, lập luận logic và giảm tối đa hallucination so với Single-agent.

*Để xem toàn bộ báo cáo chi tiết, các Failure Mode và cách khắc phục mà hệ thống đang sử dụng, vui lòng mở file [reports/benchmark_report.md](reports/benchmark_report.md).*
