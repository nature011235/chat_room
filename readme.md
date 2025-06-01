

tests 裡面是現在的測試 tests_backup是比較複雜的測試 可以去裡面找到更多測試項目 視情況可以補上去

現在tests 的測試全部都過了 看要不要加新的 

主要就4個元件

* **test_backend  /  [tests_backup] test_chat_app** \
測後端server：app.py
* **test_frontend /  [tests_backup] test_selenium_ui**\
測前端網頁
* **test_performance**\
測效能
* **test_security**\
測安全

---

我把之前有測到的問題放在 record.md

<br>

先裝套件
```bash
pip install -r requirements.txt
```
run server
```bash
python app.py
```

### 方式1：一次跑全部
```bash
python tests/run_all_tests.py
```

### 方式2：快速測試
```bash
python tests/run_all_tests.py --quick
```

### 方式3：指定測試類型
```bash
python tests/run_all_tests.py --backend     # 后端测试
python tests/run_all_tests.py --ui          # UI测试
python tests/run_all_tests.py --performance # 性能测试
python tests/run_all_tests.py --security    # 安全测试
```

---

### 方式4：直接用pytest
```bash
pytest tests/
```

### 生成覆蓋率報告
```bash
python tests/run_all_tests.py --coverage # 覆蓋率
```
