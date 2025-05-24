from unittest.mock import MagicMock, ANY

import pytest
from pika.channel import Channel
from pika.spec import Basic

from rabbit_chat.client import ChatClient


@pytest.fixture
def message_callback():
    return MagicMock()


@pytest.fixture
def client(message_callback):
    return ChatClient(
        server_url="amqp://localhost:5672",
        username="test_user",
        initial_channel="test_channel",
        message_callback=message_callback,
    )


@pytest.mark.asyncio
async def test_send_message(client):
    client._channel = MagicMock(spec=Channel)
    client._channel.is_open = True

    test_message = "Hello, world!"
    await client.send_message(test_message)

    client._channel.basic_publish.assert_called_once()
    call_args = client._channel.basic_publish.call_args[1]
    assert call_args["exchange"] == "chat"
    assert call_args["routing_key"] == "test_channel"

    message_body = call_args["body"].decode()
    assert "test_user" in message_body
    assert test_message in message_body


@pytest.mark.asyncio
async def test_switch_channel(client):
    client._channel = MagicMock(spec=Channel)
    client._channel.is_open = True

    new_channel = "new_channel"
    await client.switch_channel(new_channel)

    client._channel.queue_declare.assert_called_once_with(queue="", exclusive=True, callback=ANY)


@pytest.mark.asyncio
async def test_message_callback(client, message_callback):
    channel = MagicMock(spec=Channel)
    method = Basic.Deliver(routing_key="test_channel")
    properties = MagicMock()
    body = b'{"username": "sender", "message": "test message"}'

    client._on_message(channel, method, properties, body)

    message_callback.assert_called_once_with("test_channel", "sender", "test message")


@pytest.mark.asyncio
async def test_queue_declared_callback(client):
    client._channel = MagicMock(spec=Channel)
    client._consumer_tag = None

    queue_name = "test_queue"
    channel_name = "test_channel"
    client._on_queue_declared(queue_name, channel_name)

    client._channel.queue_bind.assert_called_once_with(
        queue=queue_name, exchange="chat", routing_key=channel_name, callback=ANY
    )
