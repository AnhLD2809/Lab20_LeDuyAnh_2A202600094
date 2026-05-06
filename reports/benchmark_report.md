# Benchmark Report

| Run | Latency (s) | Cost (USD) | Quality | Citation Coverage | Failure Rate | Notes |
|---|---:|---:|---:|---:|---:|---|
| Q1 Baseline | 12.77 | 0.0005 | 8.5 | 0.0% | 0.0% | Baseline run |
| Q1 Multi-Agent | 29.71 | 0.0016 | 8.5 | 0.0% | 0.0% | Multi-agent run with Critic |
| Q2 Baseline | 7.55 | 0.0004 | 8.5 | 0.0% | 0.0% | Baseline run |
| Q2 Multi-Agent | 29.63 | 0.0014 | 8.5 | 90.0% | 0.0% | Multi-agent run with Critic |
| Q3 Baseline | 4.85 | 0.0002 | 8.5 | 0.0% | 0.0% | Baseline run |
| Q3 Multi-Agent | 32.29 | 0.0015 | 8.5 | 0.0% | 0.0% | Multi-agent run with Critic |

## 2. Failure Mode và Cách Fix

**Failure Mode:**
Đôi khi API tìm kiếm trả về thông tin không liên quan, hoặc giới hạn query limit khiến Researcher không có dữ liệu. Do đó, Final Answer của Writer bị thiếu hụt hoặc phải bịa ra. Hoặc hệ thống bị rơi vào infinite loop (Researcher -> Analyst -> Researcher...) nếu Agent router đưa ra quyết định lặp lại do thiếu dữ kiện.

**Cách Fix:**
- Thêm cơ chế Fallback (dùng mock search data) nếu API fail.
- Thêm Guardrail (timeout, max iterations) trong `SupervisorAgent` để bắt buộc dừng nếu đi qua quá nhiều vòng lặp (đã implement).
- Prompts cần chặt chẽ: Dạy cho Writer biết rằng 'nếu không có thông tin từ notes, hãy nói rằng không tìm thấy, không được tự động bịa ra'.

## 3. Exit Ticket

**1. Case nào nên dùng multi-agent? Vì sao?**
Nên dùng multi-agent cho các bài toán phức tạp (complex tasks) đòi hỏi nhiều bước xử lý, phân quyền rõ ràng, và cần kết hợp nhiều công cụ hoặc vai trò chuyên biệt (như tìm kiếm thông tin chuyên sâu, phân tích dữ liệu, viết báo cáo tổng hợp). Vì mỗi agent có thể được tối ưu prompt và context riêng biệt (giảm hallucination), và dễ dàng quản lý state cũng như debug khi có lỗi ở một bước cụ thể.

**2. Case nào không nên dùng multi-agent? Vì sao?**
Không nên dùng multi-agent cho các bài toán đơn giản (như simple QA, summarization ngắn), các tác vụ tra cứu nhanh, hoặc khi hệ thống có yêu cầu nghiêm ngặt về độ trễ cực thấp (low latency). Vì hệ thống multi-agent sẽ gây ra overhead lớn về số lượng token (do phải truyền state qua lại giữa các agent), làm tăng chi phí API và kéo dài thời gian chờ (wall-clock time cao).
