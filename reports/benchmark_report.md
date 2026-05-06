# Benchmark Report

| Run | Latency (s) | Cost (USD) | Quality | Notes |
|---|---:|---:|---:|---|
| Q1 Baseline | 12.09 | $0.0004 | 6.5 | Baseline run |
| Q1 Multi-Agent | 32.50 | $0.0014 | 9.0 | Multi-agent run |
| Q2 Baseline | 7.25 | $0.0003 | 6.5 | Baseline run |
| Q2 Multi-Agent | 28.41 | $0.0014 | 9.0 | Multi-agent run |
| Q3 Baseline | 5.17 | $0.0002 | 6.5 | Baseline run |
| Q3 Multi-Agent | 27.85 | $0.0014 | 9.0 | Multi-agent run |

## 2. Failure Mode và Cách Fix

**Failure Mode:**
Đôi khi API tìm kiếm trả về thông tin không liên quan, hoặc giới hạn query limit khiến Researcher không có dữ liệu. Do đó, Final Answer của Writer bị thiếu hụt hoặc phải bịa ra. Hoặc hệ thống bị rơi vào infinite loop (Researcher -> Analyst -> Researcher...) nếu Agent router đưa ra quyết định lặp lại do thiếu dữ kiện.

**Cách Fix:**
- Thêm cơ chế Fallback (dùng mock search data) nếu API fail.
- Thêm Guardrail (timeout, max iterations) trong `SupervisorAgent` để bắt buộc dừng nếu đi qua quá nhiều vòng lặp (đã implement).
- Prompts cần chặt chẽ: Dạy cho Writer biết rằng 'nếu không có thông tin từ notes, hãy nói rằng không tìm thấy, không được tự động bịa ra'.
