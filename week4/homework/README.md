Đầy đủ trong [Git Nhóm BTVN week4](https://github.com/canknotcawh/nhom6_btvn)

# Tasks API

`GET /tasks/{taskId}`.

- Swagger UI: http://localhost:5000/docs
- OpenAPI JSON: http://localhost:5000/openapi.json
- API base URL: http://localhost:5000/v1
## Gọi API

```bash
curl http://localhost:5000/v1/tasks/00000000-0000-4000-8000-000000000001 \
  -H "Authorization: Bearer demo"
```

## Kiểm tra đặc tả

- Swagger Editor: mở https://editor.swagger.io/ và nạp `openapi.yaml`.
- Spectral: `npx @stoplight/spectral-cli lint openapi.yaml --ruleset .spectral.yaml`.
- ReDoc: `npx @redocly/cli lint openapi.yaml` và `npx @redocly/cli preview-docs openapi.yaml`.

## Quyết định thiết kế

1. **Trả 404 Not Found cho cả ID sai định dạng lẫn task không tồn tại**: Client nhận cùng một phản hồi `not_found` trong cả hai trường hợp -> API có hành vi đơn giản, nhất quán và không cần phân biệt lỗi cú pháp ID với lỗi không tìm thấy tài nguyên.

2. **Trả trực tiếp đối tượng Task khi tìm thấy**: Phản hồi 200 chứa task theo schema Task, không bọc thêm trong một trường như data -> giúp client truy cập trực tiếp các thuộc tính của task và khớp với schema được khai báo trong OpenAPI.

Swagger UI dùng CDN nên cần kết nối Internet.
