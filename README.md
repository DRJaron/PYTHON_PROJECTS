# Net Tool

## Overview
Net Tool is a Python-based command-line utility for network operations. It supports various functionalities, including listening for incoming connections, executing commands remotely, uploading files, and providing a basic command shell.

## Features
- **Listen Mode**: Wait for incoming network connections.
- **Execute Commands**: Run specified commands upon connection.
- **Command Shell**: Interactive remote command execution.
- **File Upload**: Receive and save files from a client.

## Installation
Ensure you have Python 3 installed.

```bash
python3 NET_TOOL.py
```

## Usage
```
Usage: bhpnet.py -t target_host -p port [options]

Options:
  -h, --help                Show this help message and exit
  -l, --listen              Listen on [host]:[port] for incoming connections
  -e, --execute=file_to_run  Execute the specified file upon receiving a connection
  -c, --command             Initialize a command shell
  -u, --upload=destination  Upload a file and write to [destination] upon connection
```

### Examples
- Listen on port 5555 and initialize a command shell:
  ```bash
  python3 NET_TOOL.py -t 192.168.0.1 -p 5555 -l -c
  ```

- Upload a file:
  ```bash
  python3 NET_TOOL.py -t 192.168.0.1 -p 5555 -l -u=c:\target.exe
  ```

- Execute a command on connection:
  ```bash
  python3 NET_TOOL.py -t 192.168.0.1 -p 5555 -l -e="cat /etc/passwd"
  ```

## How It Works
1. **Client Mode**: Sends data from standard input to the target host.
2. **Server Mode**: Listens for incoming connections and supports:
   - File uploads
   - Command execution
   - Interactive shell sessions

## Requirements
- Python 3.x

## Security Disclaimer
Use this tool responsibly and only on systems where you have explicit permission. Unauthorized use may be illegal.

## Learning Reference
This project is part of my Python learning journey with the book *Black Hat Python*.

## License
This project is provided "as is" without warranty of any kind.

