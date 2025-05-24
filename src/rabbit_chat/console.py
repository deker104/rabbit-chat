import asyncio
import logging
import random
from argparse import ArgumentParser
from typing import NoReturn

from prompt_toolkit import PromptSession
from prompt_toolkit.patch_stdout import patch_stdout

from .client import ChatClient

logger = logging.getLogger(__name__)


class ChatConsole:
    """Console-based interface for the RabbitMQ chat client."""

    def __init__(self, client: ChatClient):
        self.client = client
        self._running = True
        self._session = PromptSession()

    async def display_message(self, channel: str, username: str, message: str) -> None:
        """Display a chat message in the console with channel and username."""
        print(f"[{channel}] {username}: {message}")

    async def input_loop(self) -> NoReturn:
        """Process user input and handle chat commands (!switch, !quit)."""
        # Wait for client to establish connection before accepting input
        await self.client.wait_for_connection()
        print(f"Connected to chat as {self.client.username}")
        print(f"Current channel: {self.client.current_channel}")
        print("Type !switch <channel> to switch channels or !quit to exit")

        while self._running:
            try:
                # Get user input asynchronously with prompt toolkit
                message = await self._session.prompt_async("> ")
                if not message:
                    continue

                # Handle special commands
                if message.startswith("!switch "):
                    channel = message[8:].strip()
                    if not channel:
                        print("Usage: !switch <channel>")
                        continue
                    await self.client.switch_channel(channel)
                    print(f"Switched to channel: {channel}")
                elif message == "!quit":
                    self._running = False
                else:
                    # Send regular chat message
                    await self.client.send_message(message)
            except (KeyboardInterrupt, EOFError):
                # Handle user interrupts (Ctrl+C, Ctrl+D) gracefully
                self._running = False
            except Exception as e:
                logger.error(f"Error in input loop: {e}")

    async def run(self) -> None:
        """Run the console interface."""
        with patch_stdout():
            try:
                await self.client.connect()
                await self.input_loop()
            finally:
                # Ensure client connection is properly closed on exit
                await self.client.close()


def generate_random_username() -> str:
    """Generate a random username in format 'anonXXXXXX'."""
    return f"anon{random.randint(100000, 999999)}"


def main() -> None:
    """Start the chat application with command line configuration."""
    parser = ArgumentParser(description="RabbitMQ Chat Client")
    parser.add_argument(
        "--server",
        default="127.0.0.1:5672",
        help="RabbitMQ server address (default: 127.0.0.1:5672)",
    )
    parser.add_argument(
        "--channel", default="general", help="Initial chat channel (default: general)"
    )
    parser.add_argument(
        "--user",
        default=generate_random_username(),
        help="Username (default: random anon username)",
    )

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.WARNING, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Initialize client with temporary message callback
    client = ChatClient(
        server_url=args.server,
        username=args.user,
        initial_channel=args.channel,
        message_callback=lambda c, u, m: asyncio.create_task(
            ChatConsole(None).display_message(c, u, m)
        ),
    )

    # Create console and update client's message callback to use the actual console instance
    console = ChatConsole(client)
    client.message_callback = lambda c, u, m: asyncio.create_task(console.display_message(c, u, m))

    try:
        asyncio.run(console.run())
    except KeyboardInterrupt:
        pass
    except ConnectionError as e:
        print(f"\nError: {e}")
        print("Please make sure the RabbitMQ server is running and try again.")
        exit(1)


if __name__ == "__main__":
    main()
