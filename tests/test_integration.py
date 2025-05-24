import pytest
from unittest.mock import MagicMock, patch
from rabbit_chat.client import ChatClient


@pytest.mark.asyncio
async def test_connect_and_close():
    client = ChatClient(
        server_url="amqp://localhost:5672",
        username="test_user",
        initial_channel="test_room",
        message_callback=MagicMock(),
    )

    with patch("rabbit_chat.client.AsyncioConnection") as mock_conn:
        await client.connect()
        assert mock_conn.called

        client._connection = MagicMock(is_closed=False)
        await client.close()
        client._connection.close.assert_called_once()


@pytest.mark.asyncio
async def test_end_to_end_send_and_receive():
    callback = MagicMock()
    client = ChatClient(
        server_url="amqp://localhost:5672",
        username="user",
        initial_channel="chan",
        message_callback=callback,
    )

    client._channel = MagicMock(is_open=True)

    await client.send_message("yo")
    client._channel.basic_publish.assert_called()


@pytest.mark.asyncio
async def test_switch_channel_binds_queue():
    client = ChatClient(
        server_url="amqp://localhost:5672",
        username="tester",
        initial_channel="chan",
        message_callback=MagicMock(),
    )
    client._channel = MagicMock(is_open=True)

    with patch.object(client, "_join_channel") as mock_join:
        await client.switch_channel("chan2")
        mock_join.assert_called_once_with("chan2")
