import asyncio
import logging
import random
from argparse import ArgumentParser
from typing import NoReturn

from aioconsole import ainput, aprint

from .client import ChatClient

logger = logging.getLogger(__name__)

class ChatConsole:
    def __init__(self, client: ChatClient):
        self.client = client
        self._running = True

    async def display_message(self, channel: str, username: str, message: str) -> None:
        await aprint(f"[{channel}] {username}: {message}")

    async def input_loop(self) -> NoReturn:
        await self.client.wait_for_connection()
        await aprint(f"Connected to chat as {self.client.username}")
        await aprint(f"Current channel: {self.client.current_channel}")
        await aprint("Type !switch <channel> to switch channels or !quit to exit")

        while self._running:
            try:
                message = await ainput("> ")
                if not message:
                    continue

                if message.startswith("!switch "):
                    channel = message[8:].strip()
                    if not channel:
                        await aprint("Usage: !switch <channel>")
                        continue
                    await self.client.switch_channel(channel)
                    await aprint(f"Switched to channel: {channel}")
                elif message == "!quit":
                    self._running = False
                else:
                    await self.client.send_message(message)
            except Exception as e:
                logger.error(f"Error in input loop: {e}")

    async def run(self) -> None:
        """Run the console interface."""
        try:
            await self.client.connect()
            await self.input_loop()
        finally:
            await self.client.close()

def generate_random_username() -> str:
    return f"anon{random.randint(100000, 999999)}"

def main() -> None:
    parser = ArgumentParser(description="RabbitMQ Chat Client")
    parser.add_argument(
        "--server",
        default="127.0.0.1:5672",
        help="RabbitMQ server address (default: 127.0.0.1:5672)"
    )
    parser.add_argument(
        "--channel",
        default="general",
        help="Initial chat channel (default: general)"
    )
    parser.add_argument(
        "--user",
        default=generate_random_username(),
        help="Username (default: random anon username)"
    )

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.WARNING,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    client = ChatClient(
        server_url=args.server,
        username=args.user,
        initial_channel=args.channel,
        message_callback=lambda c, u, m: asyncio.create_task(
            ChatConsole(None).display_message(c, u, m)
        )
    )

    console = ChatConsole(client)
    client.message_callback = lambda c, u, m: asyncio.create_task(
        console.display_message(c, u, m)
    )

    try:
        asyncio.run(console.run())
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main() 