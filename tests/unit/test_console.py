import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from rabbit_chat.console import ChatConsole


@pytest.mark.asyncio
async def test_display_message():
    console = ChatConsole(client=MagicMock())
    with patch("rabbit_chat.console.aprint") as mock_aprint:
        await console.display_message("general", "user1", "hello")
        mock_aprint.assert_awaited_once_with("[general] user1: hello")


@pytest.mark.asyncio
async def test_input_loop_quit():
    client = AsyncMock()
    client.username = "test_user"
    client.current_channel = "general"
    console = ChatConsole(client=client)

    with patch("rabbit_chat.console.ainput", side_effect=["!quit"]), \
         patch("rabbit_chat.console.aprint"):
        await console.input_loop()
        assert not console._running


@pytest.mark.asyncio
async def test_input_loop_switch_channel():
    client = AsyncMock()
    client.username = "test_user"
    client.current_channel = "general"
    console = ChatConsole(client=client)

    with patch("rabbit_chat.console.ainput", side_effect=["!switch newchan", "!quit"]), \
         patch("rabbit_chat.console.aprint"):
        await console.input_loop()
        client.switch_channel.assert_awaited_with("newchan")


@pytest.mark.asyncio
async def test_input_loop_send_message():
    client = AsyncMock()
    client.username = "test_user"
    client.current_channel = "general"
    console = ChatConsole(client=client)

    with patch("rabbit_chat.console.ainput", side_effect=["hello there", "!quit"]), \
         patch("rabbit_chat.console.aprint"):
        await console.input_loop()
        client.send_message.assert_awaited_with("hello there")
