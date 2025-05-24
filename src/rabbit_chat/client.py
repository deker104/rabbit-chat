import asyncio
import json
import logging
from typing import Callable, Optional

from pika.adapters.asyncio_connection import AsyncioConnection
from pika.channel import Channel
from pika.connection import URLParameters
from pika.spec import Basic, BasicProperties

logger = logging.getLogger(__name__)


class ChatClient:
    def __init__(
        self,
        server_url: str,
        username: str,
        initial_channel: str,
        message_callback: Callable[[str, str, str], None],
    ):
        """
        Initialize the chat client.

        Args:
            server_url: RabbitMQ server URL (amqp://host:port)
            username: User's name in the chat
            initial_channel: Initial chat channel to join
            message_callback: Callback function for received messages (channel, username, message)
        """
        # Ensure server URL has the correct AMQP protocol prefix
        self.server_url = server_url if server_url.startswith("amqp://") else f"amqp://{server_url}"
        self.username = username
        self.current_channel = initial_channel
        self.message_callback = message_callback

        # Internal state management
        self._connection: Optional[AsyncioConnection] = None
        self._channel: Optional[Channel] = None
        self._consumer_tag: Optional[str] = None
        # Event flags for managing asynchronous state
        self._connected = asyncio.Event()  # Indicates when client is ready to send/receive messages
        self._closing = False  # Flag to prevent reconnection attempts during intentional shutdown
        self._ready = asyncio.Event()  # Indicates when initial connection is established
        self._error = None  # Stores connection errors if they occur

    async def connect(self) -> None:
        """Connect to the RabbitMQ server."""
        parameters = URLParameters(self.server_url)
        self._connection = AsyncioConnection(
            parameters,
            on_open_callback=self._on_connection_open,
            on_open_error_callback=self._on_connection_open_error,
            on_close_callback=self._on_connection_closed,
        )
        await self._ready.wait()
        if self._error:
            raise self._error

    def _on_connection_open_error(self, connection: AsyncioConnection, reason: Exception) -> None:
        """Called when the connection fails to open."""
        self._ready.set()
        self._error = ConnectionError(f"Failed to connect to RabbitMQ server: {reason}")

    def _on_connection_open(self, connection: AsyncioConnection) -> None:
        """Called when the connection is established."""
        logger.info("Connection opened")
        self._ready.set()
        connection.channel(on_open_callback=self._on_channel_open)

    def _on_connection_closed(self, connection: AsyncioConnection, reason: Exception) -> None:
        """Called when the connection is closed."""
        logger.info(f"Connection closed: {reason}")
        self._channel = None
        if not self._closing:
            asyncio.create_task(self.connect())

    def _on_channel_open(self, channel: Channel) -> None:
        """Called when the channel is opened."""
        self._channel = channel
        channel.add_on_close_callback(self._on_channel_closed)
        channel.exchange_declare(
            exchange="chat",
            exchange_type="topic",
            callback=lambda _: self._join_channel(self.current_channel),
        )

    def _on_channel_closed(self, channel: Channel, reason: Exception) -> None:
        """Called when the channel is closed."""
        logger.info(f"Channel closed: {reason}")
        self._channel = None
        if not self._closing and self._connection and not self._connection.is_closed:
            self._connection.channel(on_open_callback=self._on_channel_open)

    def _join_channel(self, channel_name: str) -> None:
        """Join a chat channel."""
        if not self._channel:
            return

        self._channel.queue_declare(
            queue="",  # Empty name lets RabbitMQ generate a unique queue name
            exclusive=True,  # Queue will be deleted when connection closes
            callback=lambda frame: self._on_queue_declared(frame.method.queue, channel_name),
        )

    def _on_queue_declared(self, queue_name: str, channel_name: str) -> None:
        """Called when a queue is declared."""
        if not self._channel:
            return

        # Cancel existing consumer before setting up new one
        if self._consumer_tag:
            self._channel.basic_cancel(self._consumer_tag)

        self._channel.queue_bind(
            queue=queue_name,
            exchange="chat",
            routing_key=channel_name,
            callback=lambda _: self._start_consuming(queue_name),
        )
        self.current_channel = channel_name

    def _start_consuming(self, queue_name: str) -> None:
        """Start consuming messages from the queue."""
        if not self._channel:
            return

        self._consumer_tag = self._channel.basic_consume(
            queue=queue_name, on_message_callback=self._on_message, auto_ack=True
        )
        self._connected.set()

    def _on_message(
        self, channel: Channel, method: Basic.Deliver, properties: BasicProperties, body: bytes
    ) -> None:
        """Called when a message is received."""
        try:
            message_data = json.loads(body.decode())
            self.message_callback(
                self.current_channel, message_data["username"], message_data["message"]
            )
        except Exception as e:
            logger.error(f"Error processing message: {e}")

    async def switch_channel(self, channel_name: str) -> None:
        """Switch to a different chat channel."""
        if not self._channel or not self._channel.is_open:
            return
        self._join_channel(channel_name)

    async def send_message(self, message: str) -> None:
        """Send a message to the current channel."""
        if not self._channel or not self._channel.is_open:
            return

        message_data = {"username": self.username, "message": message}
        self._channel.basic_publish(
            exchange="chat",
            routing_key=self.current_channel,
            body=json.dumps(message_data).encode(),
        )

    async def wait_for_connection(self) -> None:
        """Wait for the connection to be established."""
        await self._connected.wait()

    async def close(self) -> None:
        """Close the connection."""
        self._closing = True
        if self._connection and not self._connection.is_closed:
            self._connection.close()
