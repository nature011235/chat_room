# tests/test_backend.py - 后端功能测试（使用fixture版本）
import pytest
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, socketio, validate_image_data, online_users, chat_messages

class TestImageValidation:
    """图片验证测试"""
    
    def test_valid_png_image(self, sample_image_base64):
        """测试有效PNG图片"""
        assert validate_image_data(sample_image_base64) == True
    
    def test_invalid_format(self):
        """测试无效格式"""
        invalid_data = "data:text/plain;base64,SGVsbG8gV29ybGQ="
        assert validate_image_data(invalid_data) == False
    
    def test_oversized_image(self):
        """测试超大图片"""
        large_data = "data:image/jpeg;base64," + "A" * (150 * 1024 * 1024)
        assert validate_image_data(large_data) == False

class TestSocketEvents:
    """Socket事件测试"""
    
    def test_user_join(self, socketio_client, test_user_data):
        """测试用户加入"""
        client = socketio_client
        
        client.emit('join', test_user_data)
        received = client.get_received()
        
        # 验证用户加入事件
        assert len(received) >= 1
        assert any(event['name'] == 'user_joined' for event in received)
        
        # 验证用户被添加到在线列表
        assert len(online_users) == 1
    
    def test_send_message(self, socketio_client, test_user_data):
        """测试发送消息"""
        client = socketio_client
        
        # 先加入聊天室
        client.emit('join', test_user_data)
        client.get_received()  # 清空缓冲区
        
        # 发送消息
        client.emit('send_message', {
            'message': '这是测试消息',
            'type': 'text'
        })
        
        received = client.get_received()
        assert len(received) >= 1
        
        # 验证消息内容
        message_event = received[0]
        assert message_event['name'] == 'receive_message'
        assert message_event['args'][0]['message'] == '这是测试消息'
    
    def test_user_disconnect(self, socketio_client, test_user_data):
        """测试用户断开连接"""
        client = socketio_client
        
        # 加入后断开
        client.emit('join', test_user_data)
        assert len(online_users) == 1
        
        client.disconnect()
        assert len(online_users) == 0

class TestMessageStorage:
    """消息存储测试"""
    
    def test_message_limit(self, socketio_client):
        """测试消息数量限制"""
        client = socketio_client
        
        # 先加入聊天室
        client.emit('join', {'username': '限制测试用户', 'room': 'general'})
        client.get_received()  # 清空缓冲区
        
        # 通过真实的消息发送方式添加105条消息
        for i in range(105):
            client.emit('send_message', {
                'message': f'测试消息{i}',
                'type': 'text'
            })
            # 清空接收缓冲区避免堆积
            client.get_received()
        
        # 验证只保留100条消息
        assert len(chat_messages) == 100
        
        # 验证最旧的消息被删除（应该从消息5开始）
        assert chat_messages[0]['message'] == '测试消息5'
        assert chat_messages[-1]['message'] == '测试消息104'

class TestMultipleUsers:
    """多用户测试"""
    
    def test_two_users_chat(self):
        """测试双用户聊天"""
        client1 = socketio.test_client(app)
        client2 = socketio.test_client(app)
        
        # 用户1和用户2加入
        client1.emit('join', {'username': '用户1', 'room': 'general'})
        client2.emit('join', {'username': '用户2', 'room': 'general'})
        
        # 验证两个用户都在线
        assert len(online_users) == 2
        
        # 清空接收缓冲区
        client1.get_received()
        client2.get_received()
        
        # 用户1发送消息
        client1.emit('send_message', {
            'message': '来自用户1',
            'type': 'text'
        })
        
        # 验证两个用户都收到消息
        received1 = client1.get_received()
        received2 = client2.get_received()
        
        assert len(received1) >= 1
        assert len(received2) >= 1
        
        # 验证消息内容
        assert received1[0]['args'][0]['message'] == '来自用户1'
        assert received2[0]['args'][0]['message'] == '来自用户1'