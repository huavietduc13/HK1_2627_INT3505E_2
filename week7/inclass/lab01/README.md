# BÁO CÁO BÀI TẬP TUẦN 7: TRIỂN KHAI BACKEND SERVICE
> **Môn học**: Kiến trúc Hướng Dịch vụ (SOA) - INT3505E  
> **Chủ đề**: Từ OpenAPI Definitions đến Flask Service tích hợp Database (SQLAlchemy 2.x, Marshmallow, Docker, Pytest, Eager Loading).

---

## 📑 MỤC LỤC
1. [Tổng quan những gì đã thực hiện theo Slide 40](#1-tổng-quan-những-gì-đã-thực-hiện-theo-slide-40)
2. [Cấu trúc mã nguồn](#2-cấu-trúc-mã-nguồn)
3. [Hướng dẫn cài đặt & khởi chạy](#3-hướng-dẫn-cài-đặt--khởi-chạy)
   - [Cách 1: Chạy trực tiếp trên máy (Local)](#cách-1-chạy-trực-tiếp-trên-máy-local)
   - [Cách 2: Đóng gói Docker & Docker Compose (Khuyên dùng)](#cách-2-đóng-gói-docker--docker-compose-khuyên-dùng)
4. [Tài liệu API & Các Test Cases (Request / Response)](#4-tài-liệu-api--các-test-cases-request--response)
   - [Health Check APIs](#41-health-check-apis)
   - [Product APIs (Lab 1 CRUD)](#42-product-apis-lab-1-crud)
   - [Order & OrderItem APIs (Mục 2 Homework)](#43-order--orderitem-apis-mục-2-homework)
5. [Kiểm thử tự động với Pytest & Cơ chế phát hiện N+1 Query](#5-kiểm-thử-tự-động-với-pytest--cơ-chế-phát-hiện-n1-query)

---

## 1. TỔNG QUAN NHỮNG GÌ ĐÃ THỰC HIỆN THEO SLIDE 40

| STT | Yêu cầu trong Slide 40 | Kết quả thực hiện |
| :---: | :--- | :--- |
| **1** | **Hoàn thiện Lab 1**: Viết service Flask CRUD 6 endpoint, Application Factory, Blueprint, Marshmallow Schema, SQLAlchemy 2.x, Soft delete. |  **Hoàn thành 100%**: Đầy đủ 6 endpoints Product, phân trang, soft-delete, validation, global error handling. |
| **2** | **Thêm resource OrderItem liên kết Order và Product**: Tránh gán 1 Product duy nhất cho Order; blueprint riêng `/api/v1/orders`. |  **Hoàn thành 100%**: Model `Order` (1-N) `OrderItem` liên kết `Product`, tự động kiểm tra và trừ tồn kho khi đặt hàng. |
| **3** | **Đóng gói Dockerfile + docker-compose**: Chạy được trên máy khác mà không cần sửa code. |  **Hoàn thành 100%**: `Dockerfile` multi-stage (tách builder/runtime, non-root user `app`), `docker-compose.yml` gồm PostgreSQL 16 + Flask API với healthcheck. |
| **4** | **Thêm `/healthz` + `/ready`**: Không gộp chung. |  **Hoàn thành 100%**: `/healthz` (liveness probe), `/ready` (readiness probe kiểm tra DB kết nối). |
| **5** | **Viết pytest có eager loading & đếm query để phát hiện N+1**. |  **Hoàn thành 100%**: Dùng `selectinload(Order.items)` và `QueryCounter` (SQLAlchemy event listener), chứng minh cố định đúng 2 queries cho N đơn hàng. 6/6 test pass. |

---

## 2. CẤU TRÚC MÃ NGUỒN

```text
week7/
├── inclass/
│   └── lab01/
│       ├── app.py                # Application Factory (create_app), cấu hình 12-factor qua DB_URL
│       ├── extensions.py         # Khởi tạo SQLAlchemy instance độc lập (tránh import vòng)
│       ├── models.py             # SQLAlchemy 2.x Typed Models: Product, Order, OrderItem
│       ├── schemas.py            # Marshmallow Schemas: Input/Output validation & serialization
│       ├── errors.py             # Custom Exceptions (NotFound, Conflict, OutOfStock) & Global Error Handlers
│       ├── products.py           # Blueprint /api/v1/products (6 endpoints CRUD + Soft Delete)
│       ├── orders.py             # Blueprint /api/v1/orders (Tạo đơn, trừ kho, Eager Loading)
│       ├── health.py             # Blueprint liveness (/healthz) và readiness (/ready)
│       ├── requirements.txt      # Khai báo dependencies cho môi trường production & testing
│       ├── Dockerfile            # Dockerfile multi-stage tách Builder và Runtime
│       ├── docker-compose.yml    # Khởi chạy full stack: PostgreSQL 16 + Flask API
│       ├── .dockerignore         # Bỏ qua các file rác, .venv, *.db để tối ưu image build
│       └── tests/
│           ├── conftest.py       # Fixture app chạy trên SQLite in-memory & test_client
│           ├── test_orders.py    # Pytest POST Order & kiểm tra bẫy N+1 query bằng QueryCounter
│           └── test_products.py  # Pytest Product CRUD, trùng SKU, kiểm tra Soft Delete
└── README.md                     # Báo cáo tổng hợp
```

---

## 3. HƯỚNG DẪN CÀI ĐẶT & KHỞI CHẠY

### Cách 1: Chạy trực tiếp trên máy (Local)
Yêu cầu Python $\ge$ 3.10:

```bash
# 1. Di chuyển vào thư mục lab01
cd week7/inclass/lab01

# 2. Cài đặt thư viện
pip install -r requirements.txt pytest

# 3. Khởi chạy ứng dụng (Mặc định dùng SQLite dev.db)
python app.py
```
*Server chạy tại: `http://127.0.0.1:5000`*

---

### Cách 2: Đóng gói Docker & Docker Compose (Khuyên dùng)
Yêu cầu đã cài đặt Docker & Docker Compose:

```bash
cd week7/inclass/lab01

# Khởi chạy toàn bộ stack (PostgreSQL + API Gunicorn) ở chế độ nền
docker-compose up --build -d
```
* Sau khi chạy, Docker tự động:
  1. Kéo image `postgres:16-alpine` và khởi tạo container database.
  2. Chờ Postgres vượt qua `healthcheck` (`pg_isready`).
  3. Build image Flask service qua `Dockerfile` multi-stage và chạy 2 worker Gunicorn trên port `5000`.
  4. Tự động kết nối DB qua biến môi trường `DB_URL` và tạo toàn bộ bảng dữ liệu.

* Dừng hệ thống:
```bash
docker-compose down
```

---

## 4. TÀI LIỆU API & CÁC TEST CASES (REQUEST / RESPONSE)

### 4.1. Health Check APIs

#### 🟢 Test Case H1: Liveness Probe (`/healthz`)
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

#### 🟢 Test Case H2: Readiness Probe (`/ready`)
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

### 4.2. Product APIs (Lab 1 CRUD)

#### 🟢 Test Case P1: Tạo sản phẩm mới thành công
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

#### 🔴 Test Case P2: Báo lỗi Validation khi dữ liệu không hợp lệ
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

#### 🔴 Test Case P3: Báo lỗi Conflict khi trùng SKU
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

#### 🟢 Test Case P4: Lấy danh sách sản phẩm có phân trang (loại trừ bản ghi archived)
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

#### 🟢 Test Case P5: Xem chi tiết 1 sản phẩm
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

#### 🟢 Test Case P6: Đặt trước sản phẩm (`/reserve`)
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

#### 🟢 Test Case P7: Cập nhật một phần dữ liệu (PATCH)
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

#### 🟢 Test Case P8: Xóa mềm sản phẩm (Soft Delete)
* **Method**: `DELETE`
* **URL**: `http://localhost:5000/api/v1/products/1`
* **Status**: `204 No Content`
* **Response Body**: *(Rỗng)*
* **Kiểm chứng Soft Delete**:
  * Khi gọi `GET /api/v1/products/1`: Trả về `404 Not Found`.
  * Khi gọi `GET /api/v1/products`: Không còn xuất hiện trong danh sách (`total: 0`).
  * Trong Database: Dòng dữ liệu **vẫn còn nguyên vẹn**, chỉ có cột `archived` được gán thành `true`.

---

### 4.3. Order & OrderItem APIs (Mục 2 Homework)

#### 🟢 Test Case O1: Tạo đơn hàng thành công (Tự động trừ kho)
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

#### 🔴 Test Case O2: Báo lỗi khi đặt quá số lượng tồn kho
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

#### 🟢 Test Case O3: Lấy danh sách đơn hàng (Có Eager Loading)
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

## 5. KIỂM THỬ TỰ ĐỘNG VỚI PYTEST & CƠ CHẾ PHÁT HIỆN N+1 QUERY

### 5.1. Cơ chế phát hiện lỗi $N+1$ Query (Slide 18, 19)
Khi lấy danh sách đơn hàng kèm chi tiết từng món (`Order` $\rightarrow$ `items`):
* **Cách thông thường (Lazy loading - Dính lỗi $N+1$)**:
  * Phát 1 query lấy danh sách orders: `SELECT * FROM orders`.
  * Với mỗi đơn hàng trong vòng lặp serializer, lại phát thêm 1 query: `SELECT * FROM order_items WHERE order_id = ?`.
  * Nếu có $N = 100$ đơn hàng $\rightarrow$ Hệ thống phát sinh **$1 + 100 = 101$ queries**, gây quá tải nghiêm trọng cho Database.
* **Cách giải quyết tối ưu (Eager loading với `selectinload`)**:
  * Query 1: Lấy toàn bộ đơn hàng:  
    `SELECT orders.id, orders.customer_name ... FROM orders`
  * Query 2: Lấy toàn bộ items của các đơn hàng trên trong 1 lần duy nhất bằng toán tử `IN`:  
    `SELECT order_items.* FROM order_items WHERE order_items.order_id IN (1, 2, 3, ...)`
  * **Tổng số truy vấn luôn cố định là đúng 2 câu lệnh SQL**, bất kể có bao nhiêu đơn hàng!

### 5.2. Chạy kiểm thử tự động
Dự án tích hợp class `QueryCounter` lắng nghe sự kiện `before_cursor_execute` của SQLAlchemy để tự động đếm số câu lệnh SELECT.

Chạy lệnh kiểm thử:
```bash
pytest week7/inclass/lab01/tests -v
```

### 5.3. Kết quả kiểm thử:
```text
============================= test session starts =============================
platform win32 -- Python 3.14.5, pytest-9.2.0, pluggy-1.7.0
rootdir: C:\Users\admin\OneDrive\Documents\uet\soa\HK1_2627_INT3505E_2
collected 6 items

week7/inclass/lab01/tests/test_orders.py::test_create_order_success PASSED [ 16%]
week7/inclass/lab01/tests/test_orders.py::test_create_order_out_of_stock PASSED [ 33%]
week7/inclass/lab01/tests/test_orders.py::test_get_orders_eager_loading_prevents_n_plus_one PASSED [ 50%]
week7/inclass/lab01/tests/test_products.py::test_create_product_success PASSED [ 66%]
week7/inclass/lab01/tests/test_products.py::test_create_product_duplicate_sku PASSED [ 83%]
week7/inclass/lab01/tests/test_products.py::test_product_soft_delete PASSED [100%]

============================== 6 passed in 0.21s ==============================
```
> **100% (6/6 tests) ĐẠT.** Xác thực thành công:
> 1. Nghiệp vụ tạo đơn, trừ kho, tính giá chính xác.
> 2. Kỹ thuật Eager Loading triệt tiêu hoàn toàn lỗi $N+1$ query (chỉ đúng 2 truy vấn SELECT cho nhiều đơn hàng).
> 3. Cơ chế Soft delete không làm mất dữ liệu vật lý trong DB.
