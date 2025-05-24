# RabbitMQ Chat

A simple console-based chat application using RabbitMQ for message routing.

## Features

- Console-based interface
- Multiple chat channels
- Asynchronous message handling
- Easy channel switching with `!switch` command
- Random anonymous usernames by default

## Prerequisites

- Python 3.12 or higher
- Docker and Docker Compose (for running RabbitMQ server)

## Installation

### Option 1: Install from PyPI (recommended)

```bash
pip install rabbit-chat
```

### Option 2: Install from source

1. Clone the repository:
```bash
git clone <repository-url>
cd rabbit-chat
```

2. Install in development mode:
```bash
pip install -e .
```

## Running the Chat Server

Start the RabbitMQ server using Docker Compose:

```bash
docker-compose up -d
```

The RabbitMQ management interface will be available at http://localhost:15672 (username: guest, password: guest)

## Running the Chat Client

Basic usage:
```bash
rchat
```

With custom settings:
```bash
rchat --server localhost:5672 --channel mychannel --user myusername
```

### Command Line Arguments

- `--server`: RabbitMQ server address (default: 127.0.0.1:5672)
- `--channel`: Initial chat channel (default: general)
- `--user`: Username (default: random anonymous username)

### Chat Commands

- Send message: Just type your message and press Enter
- Switch channel: `!switch <channel_name>`
- Quit: `!quit`

## Running Tests

```bash
pip install -e ".[dev]"  # Install development dependencies
pytest tests/
```

## Architecture

The chat system consists of two main components:

1. RabbitMQ Server
   - Handles message routing between clients
   - Uses topic exchange for channel-based message distribution
   - Runs in Docker for easy deployment

2. Python Client
   - Asynchronous design using `pika`'s async adapter
   - Clean separation between chat logic (`ChatClient`) and UI (`ChatConsole`)
   - Easily testable with mock objects
   - Support for multiple channels via RabbitMQ topic exchange

## Development

The codebase is structured for testability and maintainability:

- `src/rabbit_chat/client.py`: Core chat client implementation
- `src/rabbit_chat/console.py`: Console interface
- `tests/`: Unit tests

To add new features:
1. Add tests in `tests/`
2. Implement the feature
3. Run tests to verify functionality

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 