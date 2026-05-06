# Design Template

## Problem

Nghiên cứu về một chủ đề công nghệ và viết bài tóm tắt chất lượng cao với các trích dẫn rõ ràng, dựa trên thông tin tìm kiếm thực tế.

## Why multi-agent?

Single-agent thường gặp khó khăn trong việc vừa tìm kiếm, vừa phân tích và viết bài dài mà không bị mất bối cảnh (context) hoặc bị ảo giác (hallucination). Multi-agent chia nhỏ tác vụ để mỗi agent chuyên biệt làm tốt một việc, dễ dàng scale và debug.

## Agent roles

| Agent | Responsibility | Input | Output | Failure mode |
|---|---|---|---|---|
| Supervisor | Router/Điều phối | Current state | Next agent | Infinite loop |
| Researcher | Tìm kiếm và thu thập | Query | Sources, Research Notes | Search API fail, timeout |
| Analyst | Phân tích thông tin | Research Notes | Analysis Notes | Bỏ sót thông tin quan trọng |
| Writer | Viết bài tổng hợp | Notes | Final Answer | Sinh nội dung không có thực |

## Shared state

- `request`: Thông tin query ban đầu và yêu cầu cấu hình.
- `route_history`: Lưu lại hành trình routing để tránh vòng lặp.
- `sources`: Danh sách nguồn thu thập được.
- `research_notes`: Bản nháp tóm tắt từ researcher.
- `analysis_notes`: Bản phân tích sâu từ analyst.
- `final_answer`: Kết quả trả về cuối cùng từ writer.

## Routing policy

Graph đơn giản:
START -> Supervisor -> (Researcher | Analyst | Writer) -> Supervisor -> END

Supervisor sẽ check nếu thiếu `research_notes` thì gọi Researcher. Nếu có rồi mà thiếu `analysis_notes` thì gọi Analyst. Có cả hai thì gọi Writer. Xong xuôi thì END.

## Guardrails

- Max iterations: 6
- Timeout: 60s
- Retry: Có sẵn trong LLM client call.
- Fallback: Trả về kết quả default/mock nếu search fail.
- Validation: Supervisor check các trường required trước khi kết thúc.

## Benchmark plan

Query: "Research GraphRAG state-of-the-art"
Metric: Latency, Cost, Quality score (1-10).
Expected outcome: Multi-agent có cost và latency cao hơn nhưng quality score tốt hơn đáng kể (ít hallucination và đầy đủ trích dẫn).
