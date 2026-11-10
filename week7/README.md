# Week 7 - TRIỂN KHAI BACKEND SERVICE

## 1. CHẠY BẰNG DOCKER

```bash
cd week7/inclass/lab01

docker-compose up --build -d
```

---

## 2. TÀI LIỆU API & CÁC TEST CASES (REQUEST / RESPONSE)

### 2.1. Health Check APIs

#### Test Case H1: Liveness Probe (`/healthz`)
* **Mục đích**: Kiểm tra process web server còn sống hay không (không phụ thuộc DB).
* **Method**: `GET`
* **URL**: `http://localhost:5000/healthz`
* **Status**: `200 OK`
* **Response**:
```json
{
  "status": "ok"
}
```

#### Test Case H2: Readiness Probe (`/ready`)
* **Mục đích**: Kiểm tra kết nối tới Database để biết server đã sẵn sàng nhận traffic chưa.
* **Method**: `GET`
* **URL**: `http://localhost:5000/ready`
* **Status**: `200 OK` (nếu DB hoạt động bình thường) hoặc `503 Service Unavailable` (nếu mất kết nối DB)
* **Response**:
```json
{
  "checks": {
    "db": "ok"
  },
  "status": "ok"
}
```

---

### 2.2. Product APIs (Lab 1 CRUD)

#### Test Case P1: Tạo sản phẩm mới thành công
* **Method**: `POST`
* **URL**: `http://localhost:5000/api/v1/products`
* **Headers**: `Content-Type: application/json`
* **Request Body**:
```json
{
  "sku": "KB-RGB-01",
  "name": "Bàn phím cơ không dây RGB",
  "price_cents": 1250000,
  "quantity_in_stock": 15
}
```
* **Status**: `201 Created`
* **Response Body**:
```json
{
  "id": 1,
  "sku": "KB-RGB-01",
  "name": "Bàn phím cơ không dây RGB",
  "description": null,
  "price_cents": 1250000,
  "quantity_in_stock": 15,
  "archived": false
}
```

---

#### Test Case P2: Báo lỗi Validation khi dữ liệu không hợp lệ
* **Method**: `POST`
* **URL**: `http://localhost:5000/api/v1/products`
* **Request Body** (Thiếu `name`, `price_cents` bị âm):
```json
{
  "sku": "KB-02",
  "price_cents": -50000
}
```
* **Status**: `422 Unprocessable Entity`
* **Response Body**:
```json
{
  "code": "validation_error",
  "message": {
    "name": ["Missing data for required field."],
    "price_cents": ["Must be greater than or equal to 0."]
  }
}
```

---

#### Test Case P3: Báo lỗi Conflict khi trùng SKU
* **Method**: `POST`
* **URL**: `http://localhost:5000/api/v1/products`
* **Request Body** (Gửi lại mã `sku` đã tồn tại):
```json
{
  "sku": "KB-RGB-01",
  "name": "Bàn phím cơ khác",
  "price_cents": 900000
}
```
* **Status**: `409 Conflict`
* **Response Body**:
```json
{
  "code": "conflict",
  "message": "sku already exists"
}
```

---

#### Test Case P4: Lấy danh sách sản phẩm có phân trang (loại trừ bản ghi archived)
* **Method**: `GET`
* **URL**: `http://localhost:5000/api/v1/products?page=1&size=10`
* **Status**: `200 OK`
* **Response Body**:
```json
{
  "items": [
    {
      "id": 1,
      "sku": "KB-RGB-01",
      "name": "Bàn phím cơ không dây RGB",
      "description": null,
      "price_cents": 1250000,
      "quantity_in_stock": 15,
      "archived": false
    }
  ],
  "page": 1,
  "size": 10,
  "total": 1
}
```

---

#### Test Case P5: Xem chi tiết 1 sản phẩm
* **Method**: `GET`
* **URL**: `http://localhost:5000/api/v1/products/1`
* **Status**: `200 OK`
* **Response Body**:
```json
{
  "id": 1,
  "sku": "KB-RGB-01",
  "name": "Bàn phím cơ không dây RGB",
  "description": null,
  "price_cents": 1250000,
  "quantity_in_stock": 15,
  "archived": false
}
```
*(Nếu truy cập ID không tồn tại hoặc đã bị soft-delete: Trả về `404 Not Found` kèm `{"code": "not_found", "message": "Product not found"}`)*.

---

#### Test Case P6: Đặt trước sản phẩm (`/reserve`)
* **Method**: `POST`
* **URL**: `http://localhost:5000/api/v1/products/1/reserve`
* **Request Body**:
```json
{
  "quantity": 3
}
```
* **Status**: `200 OK`
* **Response Body** (Tồn kho giảm từ 15 còn 12):
```json
{
  "id": 1,
  "sku": "KB-RGB-01",
  "name": "Bàn phím cơ không dây RGB",
  "description": null,
  "price_cents": 1250000,
  "quantity_in_stock": 12,
  "archived": false
}
```
*(Nếu đặt vượt quá số lượng trong kho: Trả về `409 Conflict` kèm `{"code": "out_of_stock", "message": "Only 12 items left in stock"}`)*.

---

#### Test Case P7: Cập nhật một phần dữ liệu (PATCH)
* **Method**: `PATCH`
* **URL**: `http://localhost:5000/api/v1/products/1`
* **Request Body**:
```json
{
  "name": "Bàn phím cơ Bluetooth RGB Pro",
  "description": "Bảo hành 24 tháng chính hãng"
}
```
* **Status**: `200 OK`
* **Response Body**:
```json
{
  "id": 1,
  "sku": "KB-RGB-01",
  "name": "Bàn phím cơ Bluetooth RGB Pro",
  "description": "Bảo hành 24 tháng chính hãng",
  "price_cents": 1250000,
  "quantity_in_stock": 12,
  "archived": false
}
```

---

#### Test Case P8: Xóa mềm sản phẩm (Soft Delete)
* **Method**: `DELETE`
* **URL**: `http://localhost:5000/api/v1/products/1`
* **Status**: `204 No Content`
* **Response Body**: *(Rỗng)*
* **Kiểm chứng Soft Delete**:
  * Khi gọi `GET /api/v1/products/1`: Trả về `404 Not Found`.
  * Khi gọi `GET /api/v1/products`: Không còn xuất hiện trong danh sách (`total: 0`).
  * Trong Database: Dòng dữ liệu **vẫn còn nguyên vẹn**, chỉ có cột `archived` được gán thành `true`.

---

### 2.3. Order & OrderItem APIs

#### Test Case O1: Tạo đơn hàng thành công (Tự động trừ kho)
* **Method**: `POST`
* **URL**: `http://localhost:5000/api/v1/orders`
* **Request Body**:
```json
{
  "customer_name": "Nguyễn Văn A",
  "items": [
    {
      "product_id": 1,
      "quantity": 2
    }
  ]
}
```
* **Status**: `201 Created`
* **Response Body**:
```json
{
  "id": 1,
  "customer_name": "Nguyễn Văn A",
  "status": "pending",
  "created_at": "2026-11-10T14:30:00",
  "items": [
    {
      "id": 1,
      "product_id": 1,
      "quantity": 2,
      "price_cents": 1250000
    }
  ]
}
```
*(Số lượng tồn kho `quantity_in_stock` của sản phẩm 1 tự động bị trừ đi 2 chiếc)*.

---

#### Test Case O2: Báo lỗi khi đặt quá số lượng tồn kho
* **Method**: `POST`
* **URL**: `http://localhost:5000/api/v1/orders`
* **Request Body**:
```json
{
  "customer_name": "Trần Thị B",
  "items": [
    {
      "product_id": 1,
      "quantity": 999
    }
  ]
}
```
* **Status**: `409 Conflict`
* **Response Body**:
```json
{
  "code": "out_of_stock",
  "message": "Product 'Bàn phím cơ Bluetooth RGB Pro' only has 10 in stock"
}
```

---

#### Test Case O3: Lấy danh sách đơn hàng (Có Eager Loading)
* **Method**: `GET`
* **URL**: `http://localhost:5000/api/v1/orders`
* **Status**: `200 OK`
* **Response Body**:
```json
[
  {
    "id": 1,
    "customer_name": "Nguyễn Văn A",
    "status": "pending",
    "created_at": "2026-11-10T14:30:00",
    "items": [
      {
        "id": 1,
        "product_id": 1,
        "quantity": 2,
        "price_cents": 1250000
      }
    ]
  }
]
```

---

## 3. KIỂM THỬ TỰ ĐỘNG VỚI PYTEST & CƠ CHẾ PHÁT HIỆN N+1 QUERY

### 3.1. Cơ chế phát hiện lỗi $N+1$ Query 
* **Eager loading với `selectinload`**:
  * Query 1: Lấy toàn bộ đơn hàng:  
    `SELECT orders.id, orders.customer_name ... FROM orders`
  * Query 2: Lấy toàn bộ items của các đơn hàng trên trong 1 lần duy nhất bằng toán tử `IN`:  
    `SELECT order_items.* FROM order_items WHERE order_items.order_id IN (1, 2, 3, ...)`
  * **Tổng số truy vấn luôn cố định là đúng 2 câu lệnh SQL** bất kể có bao nhiêu đơn hàng

### 3.2. Chạy kiểm thử tự động
Dự án tích hợp class `QueryCounter` lắng nghe sự kiện `before_cursor_execute` của SQLAlchemy để tự động đếm số câu lệnh SELECT.

Chạy lệnh kiểm thử:
```bash
pytest week7/inclass/lab01/tests -v
```

### 3.3. Kết quả kiểm thử:
```text
============================= test session starts =============================
platform win32 -- Python 3.14.5, pytest-9.2.0, pluggy-1.7.0
rootdir: C:\Users\admin\OneDrive\Documents\uet\soa\HK1_2627_INT3505E_2
collected 6 items

week7/inclass/lab01/tests/test_orders.py::test_create_order_success PASSED
week7/inclass/lab01/tests/test_orders.py::test_create_order_out_of_stock PASSED
week7/inclass/lab01/tests/test_orders.py::test_get_orders_eager_loading_prevents_n_plus_one PASSED
week7/inclass/lab01/tests/test_products.py::test_create_product_success PASSED
week7/inclass/lab01/tests/test_products.py::test_create_product_duplicate_sku PASSED
week7/inclass/lab01/tests/test_products.py::test_product_soft_delete PASSED

============================== 6 passed in 0.21s ==============================
```
> **6/6 tests ĐẠT.** Xác thực thành công:
> 1. Nghiệp vụ tạo đơn, trừ kho, tính giá chính xác.
> 2. Kỹ thuật Eager Loading triệt tiêu hoàn toàn lỗi $N+1$ query (chỉ đúng 2 truy vấn SELECT cho nhiều đơn hàng).
> 3. Cơ chế Soft delete không làm mất dữ liệu vật lý trong DB.
