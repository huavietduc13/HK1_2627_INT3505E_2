# Output logs

## Lab 02 — Spectral Lint (OpenAPI Contract)

![Log kết quả chạy Spectral Lint](./lab02-logs.png)

---

## Lab 03 — Newman CLI (Postman Collection)

```powershell
newman run postman/books-api.postman_collection.json -e postman/local.postman_environment.json -r 'cli,junit' --reporter-junit-export reports/junit.xml
```

![Log kết quả chạy Newman](./lab03-logs.png)