# Week 5 - Bookstore API
---
### Offset-based Pagination
```powershell
curl.exe "http://localhost:5000/api/v1/books?strategy=offset&limit=5&offset=0"
```

![Test Offset](test_offset.png)

---

### Cursor-based Pagination
```powershell
curl.exe "http://localhost:5000/api/v1/books?strategy=cursor&limit=5&sort=-id&cursor=eyJzb3J0IjpbIi1pZCJdLCJnZW5yZSI6bnVsbCwidmFsdWVzIjpbMTJdfQ"
```

![Test Cursor](test_cursor.png)

---

### Server Logs

![Server Logs](server.png)
