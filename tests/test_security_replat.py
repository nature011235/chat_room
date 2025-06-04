import pytest
import socketio
import time
import uuid

@pytest.mark.security_replat
def test_replay_attack():
    sio = socketio.Client()
    received_messages = []

    @sio.on("receive_message")
    def on_message(data):
        received_messages.append(data)

    sio.connect("http://localhost:5000")
    sio.emit("join", {"username": "ReplayBot"})
    time.sleep(1)

    msg_id = str(uuid.uuid4())
    message = {
        "message": "This is a replay test",
        "type": "text",
        "message_id": msg_id
    }

    sio.emit("send_message", message)
    time.sleep(1)
    sio.emit("send_message", message)  # replay
    time.sleep(1)
    sio.disconnect()

    # 應只收到一次
    assert len(received_messages) == 1