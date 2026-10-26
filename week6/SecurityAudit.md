# Homework week6: OpenAPI spec + SecurityAudit
## 5 điểm có nguy cơ bị lộ
### 1. BOLA
- Endpoint GET /posts/{id} chỉ dùng kiểm tra scope chung là `posts:read` và có ID là số nguyên tuần tự -> chỉ cần có token và có quyền đọc thì sẽ dùng script duyệt tuần tự ID
### 2. Trả Refresh Token qua JSON body
- Khi trả về như vậy, FE thường lưu vào localStorage hoặc sessionStorage -> không an toàn trước XSS
### 3. Lộ thông tin qua mã lỗi
- Ở hàm GET, có ghi response `404: Không tìm thấy bài viết với ID tương ứng`, `403: Không có quyền truy cập`
- Như vậy hacker có thể biết được ID này có bài viết hay không
### 4. Thiếu rate limit ở refresh
- Việc thiếu đi sẽ khiến hacker dùng tool để spam làm quá tải máy chủ
### 5. Lộ thông tin người dùng qua trường author_id
- Ở response của hàm GET, có trả về trường author_id -> biết được ID của user tạo ra bài viết