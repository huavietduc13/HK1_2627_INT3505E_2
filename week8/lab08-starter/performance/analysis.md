# Lab 4 — Phân tích kết quả

| Kịch bản | Users | Spawn rate | Duration | p95 (ms) | Failure rate | RPS |
|---|---:|---:|---:|---:|---:|---:|
| A | 10 | 2 | 30s | 19 ms | 0.72% | 4.78 |
| B | 50 | 5 | 60s | 19 ms | 0.14% | 23.41 |
| C | 200 | 50 | 30s | 73 ms | 0.28% | 96.89 |

---

### 1. Kịch bản có p95 cao nhất là gì? Dùng số liệu quan sát để giải thích.

* C (p95 = 73ms)
  - **Nguyên nhân**: Flask development server là single-process và SQLite áp dụng cơ chế khóa toàn bộ file database khi ghi *POST /books*. Khi 200 users gửi request, các request phải xếp hàng chờ trong hàng đợi socket buffer, dẫn đến độ trễ p95 tăng.

---

### 2. Endpoint nào tăng failure rate? Phân biệt lỗi HTTP thực và lỗi đánh dấu trong Locust.

* **Endpoint có failure rate**: *GET /books?year=[year]*
  - Kịch bản A: 1 / 46 fails (2.17%)
  - Kịch bản B: 2 / 334 fails (0.60%)
  - Kịch bản C: 8 / 686 fails (1.17%)
* **Phân biệt lỗi HTTP thực và lỗi đánh dấu trong Locust**:
  - **Lỗi đánh dấu**: task `search_by_year` sử dụng logic `if random.random() < 0.01: response.failure(...)` để chủ động đánh dấu thất bại nhằm giả lập 1% tỷ lệ lỗi. Thực tế máy chủ Flask vẫn xử lý thành công và trả về HTTP status 200.
  - **Lỗi HTTP thực**: Là các mã lỗi 5xx thật do server quăng exception hoặc các lỗi nghẽn mạng; các phản hồi 404 hợp lệ trong `read_book` được xử lý bằng `response.success()`, không bị đánh dấu nhầm thành lỗi vận hành.

---

### 3. Với SLO giả định p95 < 300 ms, kịch bản nào đạt? Nêu giới hạn của phép đo.

* **Tất cả A, B, C đều đạt**
* **Giới hạn của phép đo**:
  - Phép đo thực hiện trên môi trường máy cá nhân qua giao diện `localhost` (loopback network), client và server dùng chung tài nguyên CPU/RAM, độ trễ mạng Internet / DNS / SSL RTT bằng 0.
  - Hệ thống chạy trên Flask dev server và SQLite, không phản ánh kiến trúc production.

---

### 4. Nếu connection pool bị giới hạn ở 5, bạn sẽ kiểm chứng ảnh hưởng như thế nào?

  1. Cấu hình giới hạn pool trong `app.py`: "pool_size": 5, "max_overflow": 0, "pool_timeout": 3
  2. Khởi động lại server Flask và chạy lại các kịch bản
  3. Quan sát kết quả trong bảng thống kê
