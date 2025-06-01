# test_chat_app.py - 后端单元测试
import pytest
import base64
import json
from app import app, socketio, validate_image_data, online_users, chat_messages
from flask_socketio import SocketIOTestClient

class TestImageValidation:
    """图片验证功能测试"""
    
    def test_valid_jpeg_image(self):
        """测试有效的JPEG图片"""
        # 创建一个最小的有效JPEG base64数据
        valid_jpeg = "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEAYABgAAD//gA7Q1JFQVRPUjogZ2QtanBlZyB2MS4wICh1c2luZyBJSkcgSlBFRyB2ODApLCBxdWFsaXR5ID0gOTAK/9sAQwADAgIDAgIDAwMDBAMDBAUIBQUEBAUKBwcGCAwKDAwLCgsLDQ4SEA0OEQ4LCxAWEBETFBUVFQwPFxgWFBgSFBUU/9sAQwEDBAQFBAUJBQUJFA0LDRQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQU/8AAEQgAAQABAwEiAAIRAQMRAf/EAB8AAAEFAQEBAQEBAAAAAAAAAAABAgMEBQYHCAkKC//EALUQAAIBAwMCBAMFBQQEAAABfQECAwAEEQUSITFBBhNRYQcicRQygZGhCCNCscEVUtHwJDNicoIJChYXGBkaJSYnKCkqNDU2Nzg5OkNERUZHSElKU1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6g4SFhoeIiYqSk5SVlpeYmZqio6Slpqeoqaqys7S1tre4ubrCw8TFxsfIycrS09TV1tfY2drh4uPk5ebn6Onq8fLz9PX29/j5+gEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoL/8QAtREAAgECBAQDBAcFBAQAAQJ3AAECAxEEBSExBhJBUQdhcRMiMoEIFEKRobHBCSMzUvAVYnLRChYkNOEl8RcYGRomJygpKjU2Nzg5OkNERUZHSElKU1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6goOEhYaHiImKkpOUlZaXmJmaoqOkpaanqKmqsrO0tba3uLm6wsPExcbHyMnK0tPU1dbX2Nna4uPk5ebn6Onq8vP09fb3+Pn6/9oADAMBAAIRAxEAPwD9/KKKKAP/2Q=="
        assert validate_image_data(valid_jpeg) == True
    
    def test_valid_png_image(self):
        """测试有效的PNG图片"""
        valid_png = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
        assert validate_image_data(valid_png) == True
    
    def test_invalid_format(self):
        """测试无效格式"""
        invalid_data = "data:text/plain;base64,SGVsbG8gV29ybGQ="
        assert validate_image_data(invalid_data) == False
    
    def test_missing_data_prefix(self):
        """测试缺少data:前缀"""
        invalid_data = "image/jpeg;base64,/9j/4AAQSkZJRg..."
        assert validate_image_data(invalid_data) == False
    
    def test_malformed_base64(self):
        """测试格式错误的base64"""
        invalid_data = "data:image/jpeg;base64,invalid_base64_data!!!"
        assert validate_image_data(invalid_data) == False
    
    def test_oversized_image(self):
        """测试超大图片（模拟）"""
        # 创建一个超过100MB的假数据
        large_data = "data:image/jpeg;base64," + "A" * (150 * 1024 * 1024)
        assert validate_image_data(large_data) == False

class TestSocketIOEvents:
    """SocketIO事件测试"""
    
    @pytest.fixture
    def client(self):
        """创建测试客户端"""
        app.config['TESTING'] = True
        return socketio.test_client(app)
    
    def test_user_connect(self, client):
        """测试用户连接"""
        received = client.get_received()
        assert client.is_connected()
    
    def test_user_join_room(self, client):
        """测试用户加入房间"""
        # 清空在线用户
        online_users.clear()
        
        # 发送加入房间事件
        client.emit('join', {
            'username': '测试用户',
            'room': 'general'
        })
        
        # 接收事件
        received = client.get_received()
        
        # 验证用户已添加到在线列表
        assert len(online_users) == 1
        
        # 验证接收到的事件
        assert len(received) >= 1
        user_joined_event = received[0]
        assert user_joined_event['name'] == 'user_joined'
        assert '测试用户' in user_joined_event['args'][0]['message']
    
    def test_send_text_message(self, client):
        """测试发送文本消息"""
        # 先加入房间
        client.emit('join', {
            'username': '测试用户',
            'room': 'general'
        })
        
        # 清空接收缓冲区
        client.get_received()
        
        # 发送消息
        client.emit('send_message', {
            'message': '这是一条测试消息',
            'type': 'text'
        })
        
        # 验证消息
        received = client.get_received()
        assert len(received) >= 1
        
        message_event = received[0]
        assert message_event['name'] == 'receive_message'
        assert message_event['args'][0]['message'] == '这是一条测试消息'
        assert message_event['args'][0]['username'] == '测试用户'
    
    def test_send_image_message(self, client):
        """测试发送图片消息"""
        # 先加入房间
        client.emit('join', {
            'username': '测试用户',
            'room': 'general'
        })
        
        client.get_received()  # 清空缓冲区
        
        # 发送有效图片
        valid_image = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
        
        client.emit('send_message', {
            'message': valid_image,
            'type': 'image'
        })
        
        received = client.get_received()
        assert len(received) >= 1
        
        message_event = received[0]
        assert message_event['name'] == 'receive_message'
        assert message_event['args'][0]['type'] == 'image'
    
    def test_typing_indicator(self, client):
        """测试输入状态提示"""
        # 先加入房间
        client.emit('join', {
            'username': '测试用户',
            'room': 'general'
        })
        
        client.get_received()  # 清空缓冲区
        
        # 发送正在输入状态
        client.emit('typing', {'is_typing': True})
        
        # 注意：typing事件不会发送给自己，所以这里不会收到消息
        received = client.get_received()
        # 对于单个客户端测试，typing事件不会返回给发送者
    
    def test_user_disconnect(self, client):
        """测试用户断开连接"""
        # 先加入房间
        client.emit('join', {
            'username': '测试用户',
            'room': 'general'
        })
        
        # 验证用户在线
        assert len(online_users) == 1
        
        # 断开连接
        client.disconnect()
        
        # 验证用户已从在线列表移除
        assert len(online_users) == 0

class TestMultipleUsers:
    """多用户测试"""
    
    @pytest.fixture
    def setup_users(self):
        """设置多个用户客户端"""
        app.config['TESTING'] = True
        online_users.clear()
        chat_messages.clear()
        
        client1 = socketio.test_client(app)
        client2 = socketio.test_client(app)
        
        # 用户1加入
        client1.emit('join', {
            'username': '用户1',
            'room': 'general'
        })
        
        # 用户2加入
        client2.emit('join', {
            'username': '用户2',
            'room': 'general'
        })
        
        # 清空接收缓冲区
        client1.get_received()
        client2.get_received()
        
        return client1, client2
    
    def test_multiple_users_chat(self, setup_users):
        """测试多用户聊天"""
        client1, client2 = setup_users
        
        # 用户1发送消息
        client1.emit('send_message', {
            'message': '来自用户1的消息',
            'type': 'text'
        })
        
        # 验证两个用户都收到消息
        received1 = client1.get_received()
        received2 = client2.get_received()
        
        assert len(received1) >= 1
        assert len(received2) >= 1
        
        # 验证消息内容
        msg1 = received1[0]['args'][0]
        msg2 = received2[0]['args'][0]
        
        assert msg1['message'] == '来自用户1的消息'
        assert msg2['message'] == '来自用户1的消息'
        assert msg1['username'] == '用户1'
        assert msg2['username'] == '用户1'
    
    def test_online_users_update(self, setup_users):
        """测试在线用户列表更新"""
        client1, client2 = setup_users
        
        # 验证有2个用户在线
        assert len(online_users) == 2
        
        # 用户1断开连接
        client1.disconnect()
        
        # 验证在线用户数量减少
        assert len(online_users) == 1

class TestMessageStorage:
    """消息存储测试"""
    
    def test_message_storage_limit(self):
        """测试消息存储限制（最多100条）"""
        # 清空消息历史
        chat_messages.clear()
        
        # 添加105条消息
        for i in range(105):
            chat_messages.append({
                'username': f'用户{i}',
                'message': f'消息{i}',
                'type': 'text',
                'time': '12:00:00',
                'user_id': f'id{i}'
            })
        
        # 验证只保留了100条消息
        assert len(chat_messages) == 100
        # 验证是最新的100条消息（应该是消息5-104）
        assert chat_messages[0]['message'] == '消息5'
        assert chat_messages[-1]['message'] == '消息104'

# 运行测试的配置
if __name__ == '__main__':
    pytest.main(['-v', __file__])