# 简易聊天室

一个使用 Flask + Socket.IO 构建的简单实时聊天室，无需登录注册，无需数据库。

## 功能特点

- 🚀 实时聊天：基于 Socket.IO 的实时消息传输
- 👤 简单易用：只需输入昵称即可开始聊天
- 💬 消息提示：显示用户加入/离开和正在输入状态
- 📱 响应式设计：适配不同屏幕尺寸
- 💾 内存存储：消息临时存储在内存中（重启后清空）

## 快速开始

### 1. 進入目錄

```bash
cd project-dir
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 创建文件

将对应的代码保存到以下文件中：
- `app.py` - Flask 主应用
- `templates/index.html` - 聊天室页面  
- `static/js/chat.js` - JavaScript 代码
- `requirements.txt` - 依赖包列表

### 4. 运行应用

```bash
python app.py
```

### 5. 访问聊天室

打开浏览器访问：`http://localhost:5000`

## 项目结构

```
简易聊天室/
├── app.py              # Flask 主应用
├── requirements.txt    # 依赖包列表
├── README.md          # 使用说明
├── templates/
│   └── index.html     # 聊天室页面
└── static/
    └── js/
        └── chat.js    # 聊天室 JavaScript 代码
```

## 使用方法

1. 打开网页后输入您的昵称
2. 点击"加入聊天"按钮
3. 开始与其他在线用户聊天
4. 支持多个用户同时在线聊天

## 技术栈

- **后端**: Flask + Flask-SocketIO
- **前端**: HTML + CSS + JavaScript
- **实时通信**: Socket.IO
- **服务器**: Eventlet

## 注意事项

- 消息只存储在内存中，服务器重启后消息会丢失
- 用户离开页面后会自动断开连接
- 最多保留最近100条消息
- 昵称最长20个字符，消息最长500个字符

## 自定义配置

可以在 `app.py` 中修改以下配置：

- `host='0.0.0.0'`: 服务器监听地址
- `port=5000`: 服务器端口
- `debug=True`: 调试模式
- 消息存储上限（当前为100条）

## 扩展功能建议

如果需要更多功能，可以考虑添加：

- 多个聊天房间
- 消息持久化存储
- 用户头像上传
- 私聊功能
- 消息表情包
- 文件分享



---

## 測試在這
這個聊天室專案其實不會太簡單！雖然程式碼看起來簡潔，但有很多有趣的測試面向可以深入探討：

這個專案的測試挑戰

**🔥 高價值測試面向**

* WebSocket即時通訊測試 - 這是比一般HTTP API更複雜的測試挑戰
* 並發測試 - 多用戶同時連線、訊息競爭條件
* 狀態管理測試 - 內存中的用戶狀態、訊息歷史
* 前後端整合測試 - JavaScript + SocketIO + Flask的完整流程

**📋 可以涵蓋的測試類型**

* 單元測試 - Flask路由、事件處理函數
* 整合測試 - WebSocket連接、房間管理
* 功能測試 - 聊天流程、用戶加入/離開
* 效能測試 - 100個用戶同時在線的壓力測試
* 安全測試 - XSS攻擊、訊息注入、輸入驗證
* UI自動化測試 - Selenium測試前端互動
* API測試 - 雖然主要是WebSocket，但也有HTTP路由

**💡 進階測試場景**

* 網路中斷恢復測試
* 訊息順序一致性測試
* 記憶體洩漏測試（長時間運行）
* 跨瀏覽器兼容性測試

**🎯 實作建議**
可以分幾個階段：

* 基礎測試框架建立 - 使用pytest + Flask-Testing
* WebSocket測試工具 - 使用socketio-client進行測試
* 自動化測試 - GitHub Actions CI/CD
* 測試報告 - 覆蓋率分析、效能基準

這個專案的優點是：

* ✅ 有實際的技術挑戰（WebSocket測試）
* ✅ 功能完整但不會過於複雜
* ✅ 可以展示多種測試技術
* ✅ 有視覺化的測試結果

想要我幫你設計具體的測試計畫嗎？或是你比較想專注在哪個測試面向？


# 方式1：一键运行（推荐）
python tests/run_all_tests.py

# 方式2：快速测试
python tests/run_all_tests.py --quick

# 方式3：指定测试类型
python tests/run_all_tests.py --backend     # 后端测试
python tests/run_all_tests.py --ui          # UI测试
python tests/run_all_tests.py --performance # 性能测试
python tests/run_all_tests.py --security    # 安全测试

# 方式4：直接用pytest
pytest tests/
