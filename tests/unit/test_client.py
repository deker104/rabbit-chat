import pytest
from unittest.mock import MagicMock, patch
from pika.channel import Channel
from pika.spec import Basic
from rabbit_chat.client import ChatClient


@pytest.fixture
def dummy_callback():
    return MagicMock()


@pytest.fixture
def client(dummy_callback):
    return ChatClient(
        server_url="amqp://localhost:5672",
        username="tester",
        initial_channel="room",
        message_callback=dummy_callback,
    )


@pytest.mark.asyncio
@pytest.mark.timeout(5)
async def test_send_message(client):
    client._channel = MagicMock(spec=Channel)
    client._channel.is_open = True

    await client.send_message("test message")

    client._channel.basic_publish.assert_called_once()
    call_args = client._channel.basic_publish.call_args[1]
    assert call_args["exchange"] == "chat"
    assert call_args["routing_key"] == "room"


@pytest.mark.asyncio
@pytest.mark.timeout(5)
async def test_switch_channel(client):
    client._channel = MagicMock(spec=Channel)
    client._channel.is_open = True

    with patch.object(client, "_join_channel") as mock_join:
        await client.switch_channel("another_room")
        mock_join.assert_called_once_with("another_room")


@pytest.mark.timeout(2)
def test_on_message(client, dummy_callback):
    body = b'{"username": "alice", "message": "hi!"}'
    method = Basic.Deliver(routing_key="room")
    properties = MagicMock()
    channel = MagicMock(spec=Channel)

    client._on_message(channel, method, properties, body)
    dummy_callback.assert_called_once_with("room", "alice", "hi!")
