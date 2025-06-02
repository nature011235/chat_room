const socket = io({
    reconnection: true,
    reconnectionAttempts: 5,
    reconnectionDelay: 1000
});
window.socket = socket;
let currentUsername = '';
let isConnected = false;
let typingTimer;

// DOM 元素
let usernameContainer;
let messageContainer;
let usernameInput;
let messageInput;
let messagesDiv;
let typingIndicator;
let sendButton;
let imageButton;
let imageInput;
let onlineCounter;
let onlineCount;
let usersPanel;
let usersPanelOverlay;
let usersList;

let onlineUsers = [];

// 初始化 DOM 元素
function initializeElements() {
    chatheader = document.getElementById('chat-header');
    usernameContainer = document.getElementById('usernameContainer');
    messageContainer = document.getElementById('messageContainer');
    usernameInput = document.getElementById('usernameInput');
    messageInput = document.getElementById('messageInput');
    messagesDiv = document.getElementById('messages');
    typingIndicator = document.getElementById('typingIndicator');
    sendButton = document.getElementById('sendButton');
    imageButton = document.getElementById('imageButton');
    imageInput = document.getElementById('imageInput');
    onlineCounter = document.getElementById('onlineCounter');
    onlineCount = document.getElementById('onlineCount');
    usersPanel = document.getElementById('usersPanel');
    usersPanelOverlay = document.getElementById('usersPanelOverlay');
    usersList = document.getElementById('usersList');
    window.chatContainer = document.querySelector('.chat-container');
    typingIndicator.style.display = 'none';
}

// 加入聊天
function joinChat() {
    const username = usernameInput.value.trim();
    if (username === '') {
        alert('请输入昵称！');
        return;
    }

    currentUsername = username;
    socket.emit('join', {
        username: username,
        room: 'general'
    });

    // 扩展聊天窗口
    console.log('开始扩展窗口');
    if (window.chatContainer) {
        window.chatContainer.classList.add('expanded');
        console.log('窗口扩展类已添加');
    } else {
        console.error('找不到聊天容器元素');
    }

    // 延迟切换界面，让扩展动画先进行
    setTimeout(() => {
        usernameContainer.classList.add('hidden');
        chatheader.classList.add('hidden');
        messageContainer.classList.remove('hidden');
        messagesDiv.classList.remove('hidden');
        onlineCounter.classList.remove('hidden');
        if (messageInput) {
            messageInput.focus();
        }
    }, 300);

    isConnected = true;
}

// 发送消息
function sendMessage() {
    const message = messageInput.value.trim();
    if (message === '' || !isConnected) return;

    socket.emit('send_message', {
        message: message,
        type: 'text'
    });
    messageInput.value = '';
    messageInput.style.height = 'auto'; // 重置高度
    messageInput.focus();
}

// 处理图片选择
function handleImageSelect() {
    imageInput.click();
}

// 压缩图片
function compressImage(file, maxWidth = 10000, maxHeight = 10000, quality = 0.8) {
    return new Promise((resolve) => {
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        const img = new Image();

        img.onload = function () {
            // 计算新的尺寸
            let { width, height } = calculateNewDimensions(img.width, img.height, maxWidth, maxHeight);

            canvas.width = width;
            canvas.height = height;

            // 绘制压缩后的图片
            ctx.drawImage(img, 0, 0, width, height);

            // 转换为base64
            const compressedDataUrl = canvas.toDataURL('image/jpeg', quality);
            resolve(compressedDataUrl);
        };

        img.src = URL.createObjectURL(file);
    });
}

// 计算新的图片尺寸
function calculateNewDimensions(originalWidth, originalHeight, maxWidth, maxHeight) {
    let width = originalWidth;
    let height = originalHeight;

    // 如果图片尺寸超过最大值，按比例缩放
    if (width > maxWidth) {
        height = (height * maxWidth) / width;
        width = maxWidth;
    }

    if (height > maxHeight) {
        width = (width * maxHeight) / height;
        height = maxHeight;
    }

    return { width: Math.round(width), height: Math.round(height) };
}

// 处理图片文件
async function handleImageFile(file) {
    // 检查文件类型
    if (!file.type.startsWith('image/')) {
        alert('please select img file');
        return;
    }

    // 检查文件大小（最大10MB）
    if (file.size > 100 * 1024 * 1024) {
        alert('img size is too large');
        return;
    }

    try {
        // 显示发送中状态
        imageButton.style.opacity = '0.5';
        imageButton.style.pointerEvents = 'none';

        // 压缩图片
        const compressedImage = await compressImage(file);

        // 发送图片消息
        socket.emit('send_message', {
            message: compressedImage,
            type: 'image'
        });

        // 重置按钮状态
        imageButton.style.opacity = '1';
        imageButton.style.pointerEvents = 'auto';

    } catch (error) {
        console.error('圖片處理失敗:', error);
        alert('圖片處理失敗，請重試！');

        // 重置按钮状态
        imageButton.style.opacity = '1';
        imageButton.style.pointerEvents = 'auto';
    }
}

// 显示消息
function displayMessage(data, isOwn = false, isSystem = false) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isOwn ? 'own' : (isSystem ? 'system' : 'other')}`;

    if (isSystem) {
        messageDiv.innerHTML = `<div class="message-content">${data.message}</div>`;
        messagesDiv.appendChild(messageDiv);
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    } else {
        const messageInfo = isOwn ? `您 ${data.time}` : `${data.username} ${data.time}`;

        // let contentHtml = '';
        // if (data.type === 'image') {
        //     contentHtml = `<img src="${data.message}" class="chat-image" onclick="openImageModal('${data.message}')" alt="聊天图片">`;
        // } else {
        //     contentHtml = `<div class="message-content">${data.message}</div>`;
        // }

        // messageDiv.innerHTML = `
        //     <div class="message-info">${messageInfo}</div>
        //     ${contentHtml}
        // `;

        if (data.type === 'image') {
            // 创建图片元素
            const img = document.createElement('img');
            img.src = data.message;
            img.className = 'chat-image';
            img.alt = '聊天圖片';
            img.onclick = () => openImageModal(data.message);

            // 先添加消息框架
            messageDiv.innerHTML = `<div class="message-info">${messageInfo}</div>`;
            messageDiv.appendChild(img);
            messagesDiv.appendChild(messageDiv);

            // 立即滚动一次（滚动到消息框架位置）
            messagesDiv.scrollTop = messagesDiv.scrollHeight;

            // 监听图片加载完成事件 - 一完成就滚动！
            img.addEventListener('load', () => {
                messagesDiv.scrollTop = messagesDiv.scrollHeight;
            });

            // 如果图片加载失败，也要滚动
            img.addEventListener('error', () => {
                messagesDiv.scrollTop = messagesDiv.scrollHeight;
            });

        } else {
            // 文字消息
            messageDiv.innerHTML = `
                <div class="message-info">${messageInfo}</div>
                <div class="message-content">${data.message}</div>
            `;
            messagesDiv.appendChild(messageDiv);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }

    }
}

// 打开图片模态框
function openImageModal(imageSrc) {
    // 创建模态框
    const modal = document.createElement('div');
    modal.className = 'image-modal';
    modal.innerHTML = `
        <div class="image-modal-content">
            <span class="image-modal-close">&times;</span>
            <img src="${imageSrc}" class="modal-image" alt="放大圖片">
        </div>
    `;

    document.body.appendChild(modal);

    // 点击关闭按钮或背景关闭模态框
    modal.onclick = function (e) {
        if (e.target === modal || e.target.className === 'image-modal-close') {
            document.body.removeChild(modal);
        }
    };
}


function updateOnlineUsers(users, count) {
    onlineUsers = users;
    onlineCount.textContent = count;

    // 更新用户列表
    usersList.innerHTML = '';
    users.forEach(user => {
        const userItem = document.createElement('div');
        userItem.className = 'user-item';

        const isCurrentUser = user.username === currentUsername;

        userItem.innerHTML = `
            <div class="user-avatar">${user.username.charAt(0).toUpperCase()}</div>
            <div class="user-info">
                <div class="user-name">${user.username}${isCurrentUser ? ' (你)' : ''}</div>
                <div class="user-status">在線中</div>
            </div>
        `;

        usersList.appendChild(userItem);
    });
}

function toggleUsersPanel() {
    const isActive = usersPanel.classList.contains('active');
    if (isActive) {
        closeUsersPanel();
    } else {
        openUsersPanel();
    }
}

// 打开用户面板
function openUsersPanel() {
    usersPanel.classList.add('active');
    usersPanelOverlay.classList.add('active');
    document.body.style.overflow = 'hidden'; // 防止背景滚动
}

// 关闭用户面板
function closeUsersPanel() {
    usersPanel.classList.remove('active');
    usersPanelOverlay.classList.remove('active');
    document.body.style.overflow = ''; // 恢复滚动
}

// 更新正在输入状态
function updateTyping() {
    clearTimeout(typingTimer);
    socket.emit('typing', { is_typing: true });

    typingTimer = setTimeout(() => {
        socket.emit('typing', { is_typing: false });
    }, 1000);
}

function autoResizeTextarea() {
    messageInput.style.height = 'auto';
    messageInput.style.height = Math.min(messageInput.scrollHeight, 120) + 'px';
}

// 绑定事件监听器
function bindEventListeners() {
    // 用户名输入框事件
    usernameInput.addEventListener('keypress', function (e) {
        if (e.key === 'Enter') {
            joinChat();
        }
    });

    // 消息输入框事件
    messageInput.addEventListener('keypress', function (e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault(); // 防止换行
            sendMessage();
        } else {
            updateTyping();
        }
    });

    // 图片选择事件
    if (imageInput) {
        imageInput.addEventListener('change', function (e) {
            const file = e.target.files[0];
            if (file) {
                handleImageFile(file);
            }
            // 清空input值，允许选择同一个文件
            e.target.value = '';
        });
    }

    // 拖拽上传事件
    if (messageContainer) {
        messageContainer.addEventListener('dragover', function (e) {
            e.preventDefault();
            messageContainer.classList.add('drag-over');
        });

        messageContainer.addEventListener('dragleave', function (e) {
            e.preventDefault();
            messageContainer.classList.remove('drag-over');
        });

        messageContainer.addEventListener('drop', function (e) {
            e.preventDefault();
            messageContainer.classList.remove('drag-over');

            const files = e.dataTransfer.files;
            if (files.length > 0) {
                const file = files[0];
                if (file.type.startsWith('image/')) {
                    handleImageFile(file);
                }
            }
        });
    }

    // 发送按钮事件 (可以通过全局函数调用)
    window.sendMessage = sendMessage;
    window.joinChat = joinChat;
    window.handleImageSelect = handleImageSelect;
    window.toggleUsersPanel = toggleUsersPanel;
    window.openUsersPanel = openUsersPanel;
    window.closeUsersPanel = closeUsersPanel;
}

// Socket.IO 事件监听
function setupSocketEvents() {
    // 连接成功
    socket.on('connect', function () {
        console.log('連接成功');
        window.socket.connected = true;
        isConnected = true;
    });

    // 用户加入通知
    socket.on('user_joined', function (data) {
        displayMessage(data, false, true);
    });

    socket.on('user_left', function (data) {
        displayMessage(data, false, true);
    });
    socket.on('online_users_update', function (data) {
        updateOnlineUsers(data.users, data.count);
    });
    // 接收消息
    socket.on('receive_message', function (data) {
        const isOwn = data.username === currentUsername;
        displayMessage(data, isOwn);
    });

    // 正在输入提示
    socket.on('user_typing', function (data) {
        if (data.is_typing) {
            typingIndicator.textContent = `${data.username} 正在输入...`;
            typingIndicator.style.display = 'block';
        } else {
            typingIndicator.style.display = 'none';
        }
    });

    // 错误处理
    socket.on('error', function (data) {
        alert(data.message);
    });

    // 连接断开
    socket.on('disconnect', function () {
        console.log('連接斷開');
        window.socket.connected = false;
        isConnected = false;
    });

    // 连接错误
    socket.on('connect_error', function (error) {
        console.error('連接錯誤:', error);
    });
}

// 初始化应用
function initializeApp() {
    initializeElements();
    bindEventListeners();
    setupSocketEvents();

    // 聚焦到用户名输入框
    if (usernameInput) {
        usernameInput.focus();
    }
}

// 页面加载完成后初始化
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeApp);
} else {
    initializeApp();
}