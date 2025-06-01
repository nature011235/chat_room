from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room
from datetime import datetime
import uuid
import base64
import imghdr

app = Flask(__name__)
app.secret_key = 'simple_chat_secret_key'

# 配置 SocketIO
socketio = SocketIO(app, cors_allowed_origins="*")

# 存储在线用户和消息（内存中）
online_users = {}
chat_messages = []

ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def validate_image_data(image_data):
    """验证图片数据"""
    try:
        # 检查是否是base64编码的图片
        if not image_data.startswith('data:image/'):
            return False
        
        # 提取图片格式
        format_part = image_data.split(',')[0]
        if 'image/' not in format_part:
            return False
            
        # 提取base64数据
        base64_data = image_data.split(',')[1]
        decoded_data = base64.b64decode(base64_data)
        
        # 检查文件大小 (限制为5MB)
        if len(decoded_data) > 100 * 1024 * 1024:
            return False
            
        # 检查图片格式
        image_type = imghdr.what(None, decoded_data)
        if image_type not in ALLOWED_IMAGE_EXTENSIONS:
            return False
            
        return True
    except Exception:
        return False

@app.route('/')
def index():
    return render_template('index.html', messages=chat_messages)

@socketio.on('connect')
def handle_connect():
    print('用户连接成功')

@socketio.on('disconnect')
def handle_disconnect():
    if request.sid in online_users:
        user_info = online_users[request.sid]
        username = user_info['username']
        room = user_info.get('room', 'general')
        
        # 移除用户
        del online_users[request.sid]
        
        # 通知其他用户有用户离开
        emit('user_left', {
            'username': username,
            'message': f'{username} 離開了聊天室',
            'time': datetime.now().strftime('%H:%M:%S')
        }, room=room)
        
        # 广播更新的在线用户列表
        broadcast_online_users(room)
        
        print(f'{username} 离开了房间 {room}')
    else:
        print('用户断开连接')


@socketio.on('join')
def handle_join(data):
    username = data['username']
    room = data.get('room', 'general')
    
    # 生成用户ID
    user_id = str(uuid.uuid4())[:8]
    online_users[request.sid] = {
        'username': username,
        'user_id': user_id,
        'room': room
    }
    
    join_room(room)
    
    # 通知其他用户有新用户加入
    emit('user_joined', {
        'username': username,
        'message': f'{username} 加入了聊天室',
        'time': datetime.now().strftime('%H:%M:%S')
    }, room=room)
    broadcast_online_users(room)
    print(f'{username} 加入了房间 {room}')

def broadcast_online_users(room):
    """广播在线用户列表"""
    users_in_room = []
    for sid, user_info in online_users.items():
        if user_info.get('room') == room:
            users_in_room.append({
                'username': user_info['username'],
                'user_id': user_info['user_id']
            })
    
    socketio.emit('online_users_update', {
        'users': users_in_room,
        'count': len(users_in_room)
    }, room=room)

@socketio.on('send_message')
def handle_message(data):
    if request.sid not in online_users:
        return
    
    user_info = online_users[request.sid]
    username = user_info['username']
    room = user_info.get('room', 'general')
    message = data.get('message', '')
    message_type = data.get('type', 'text')  # 'text' 或 'image'
    
    # 创建消息对象
    msg_data = {
        'username': username,
        'message': message,
        'type': message_type,
        'time': datetime.now().strftime('%H:%M:%S'),
        'user_id': user_info['user_id']
    }
    
    # 如果是图片消息，验证图片数据
    if message_type == 'image':
        if not validate_image_data(message):
            emit('error', {'message': 'too large'})
            return
        print(f'{username} 发送了一张图片')
    else:
        print(f'{username}: {message}')
    
    # 存储消息（最多保留100条）
    chat_messages.append(msg_data)
    if len(chat_messages) > 100:
        chat_messages.pop(0)
    
    # 广播消息给房间内所有用户
    emit('receive_message', msg_data, room=room)

@socketio.on('typing')
def handle_typing(data):
    if request.sid not in online_users:
        return
        
    user_info = online_users[request.sid]
    room = user_info.get('room', 'general')
    
    emit('user_typing', {
        'username': user_info['username'],
        'is_typing': data['is_typing']
    }, room=room, include_self=False)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)