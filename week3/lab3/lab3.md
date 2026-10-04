# LAB 3

---

## Tests

### Test 1: Filter
  curl.exe 'localhost:5000/orders?status=paid'
![Test 1 - Filter status](test1.png)

### Test 2: Limit 
  curl.exe 'localhost:5000/orders?limit=5'
![Test 2 - Limit 5](test2.png)

### Test 3: Sparse fieldsets
  curl.exe 'localhost:5000/orders?fields=id,total'

![Test 3 - Sparse fieldsets](test3.png)

### Test 4: Broken cursor (400 Bad Request)
  curl.exe 'localhost:5000/orders?cursor=abc'

![Test 4 - Broken cursor](test4.png)
