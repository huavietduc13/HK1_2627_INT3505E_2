from flask import Flask, request, jsonify, make_response

app = Flask(__name__)

# Mock Data
orders = [
    {"id": 1, "status": "paid", "customer_id": 101, "total": 250.0},
    {"id": 2, "status": "pending", "customer_id": 102, "total": 150.0},
    {"id": 3, "status": "paid", "customer_id": 103, "total": 300.0},
    {"id": 4, "status": "shipped", "customer_id": 101, "total": 450.0},
    {"id": 5, "status": "paid", "customer_id": 104, "total": 100.0},
    {"id": 6, "status": "pending", "customer_id": 102, "total": 200.0},
    {"id": 7, "status": "paid", "customer_id": 105, "total": 500.0},
    {"id": 8, "status": "shipped", "customer_id": 101, "total": 120.0},
    {"id": 9, "status": "paid", "customer_id": 106, "total": 600.0},
    {"id": 10, "status": "pending", "customer_id": 107, "total": 50.0},
]

def problem_details(status: int, title: str, detail: str):
    payload = {
        "type": "about:blank",
        "title": title,
        "status": status,
        "detail": detail,
        "instance": request.path
    }
    response = make_response(jsonify(payload), status)
    response.headers["Content-Type"] = "application/problem+json"
    return response

@app.route("/orders", methods=["GET"])
def get_orders():
    cursor = request.args.get("cursor")
    limit = request.args.get("limit", 5, type=int)
    status_filter = request.args.get("status")
    customer_id_filter = request.args.get("customer_id", type=int)
    sort_field = request.args.get("sort")
    fields_param = request.args.get("fields")

    # id là số nguyên
    if cursor is not None:
        try:
            cursor = int(cursor)
        except ValueError:
            return problem_details(400, "Bad Request", "Cursor must be an integer ID.")

    # filter
    result = orders
    if status_filter:
        result = [o for o in result if o["status"] == status_filter]
    if customer_id_filter is not None:
        result = [o for o in result if o["customer_id"] == customer_id_filter]

    # sort
    if sort_field:
        if sort_field in ["id", "status", "customer_id", "total"]:
            result = sorted(result, key=lambda x: x[sort_field])

    # cursor
    if cursor is not None:
        cursor_index = -1
        for i, o in enumerate(result):
            if o["id"] == cursor:
                cursor_index = i
                break
        
        if cursor_index == -1:
            return problem_details(400, "Bad Request", "Cursor not found.")
        else:
            result = result[cursor_index + 1:]
            
    # limit
    paginated_result = result[:limit]

    # next_cursor
    next_cursor = None
    if len(result) > limit:
        next_cursor = paginated_result[-1]["id"]

    # fields
    if fields_param:
        fields = [f.strip() for f in fields_param.split(",")]
        final_data = []
        for o in paginated_result:
            final_data.append({k: v for k, v in o.items() if k in fields})
        paginated_result = final_data

    # response
    response_body = {
        "data": paginated_result,
        "pagination": {
            "limit": limit
        }
    }
    
    if next_cursor is not None:
        response_body["pagination"]["next_cursor"] = next_cursor

    return jsonify(response_body), 200

if __name__ == "__main__":
    app.run(debug=True)
