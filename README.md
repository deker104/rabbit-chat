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

### Option 1: Install using pipx (recommended)

```bash
pipx install https://github.com/deker104/rabbit-chat.git
```

### Option 2: Install from source

1. Clone the repository:
```bash
git clone https://github.com/deker104/rabbit-chat.git
cd rabbit-chat
```

2. Install in development mode:
```bash
pip install -e .[dev]
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