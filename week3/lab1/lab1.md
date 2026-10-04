#LAB 1
---

## 1. Xác định Resources

Hệ thống Blog bao gồm các thực thể cốt lõi sau:

1. **`users`**: Người dùng hệ thống kiêm tác giả viết bài.
2. **`posts`**: Bài viết trên blog.
3. **`comments`**: Bình luận của người dùng trên từng bài viết cụ thể.
4. **`tags`**: Nhãn/thẻ phân loại bài viết.
5. **`following`**: Mối quan hệ theo dõi giữa các tác giả.

---

## 2. Phân loại

Áp dụng quy ước đặt tên: chữ thường (`lowercase`), danh từ số nhiều cho collections, dùng HTTP methods thay cho động từ, và áp dụng kỹ thuật làm phẳng (*flatten*) cho tài nguyên con:

| Loại Resource | Endpoint Path | Phương thức HTTP | Chức năng nghiệp vụ |
| :--- | :--- | :--- | :--- |
| **Collection** | `/posts` | `GET` | Lấy danh sách bài viết (hỗ trợ lọc: `?tags=python`) |
| **Collection** | `/posts` | `POST` | Tạo bài viết mới |
| **Item** | `/posts/{id}` | `GET` | Xem chi tiết bài viết |
| **Item** | `/posts/{id}` | `PUT` / `PATCH` | Cập nhật toàn bộ / một phần bài viết |
| **Item** | `/posts/{id}` | `DELETE` | Xóa bài viết |
| **Sub-resource** | `/posts/{id}/comments` | `GET` | Lấy danh sách bình luận của bài viết `{id}` |
| **Sub-resource** | `/posts/{id}/comments` | `POST` | Thêm bình luận vào bài viết `{id}` |
| **Item (Flatten)** | `/comments/{id}` | `DELETE` | Xóa một bình luận cụ thể |
| **Collection** | `/users` | `GET`, `POST` | Danh sách người dùng / Đăng ký tài khoản |
| **Item** | `/users/{id}` | `GET`, `PATCH` | Xem và cập nhật hồ sơ người dùng |
| **Sub-resource** | `/users/{id}/following` | `GET` | Danh sách tác giả mà user `{id}` đang theo dõi |
| **Sub-resource** | `/users/{id}/following/{target_id}` | `PUT` | Theo dõi (Follow) tác giả `target_id` (Idempotent) |
| **Sub-resource** | `/users/{id}/following/{target_id}` | `DELETE` | Hủy theo dõi (Unfollow) tác giả `target_id` |
