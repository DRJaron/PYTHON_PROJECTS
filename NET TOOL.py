import sys
import socket
import getopt
import threading
import subprocess
import os

#define some global variables
listen = False
command = False
upload = False
execute = ""
target = ""
upload_destination = ""
port = 0

def usage():
    print("Net Tool")
    print("\nUsage: bhpnet.py -t target_host -p port")
    print("-l --listen              - listen on [host]:[port] for incoming connections")
    print("-e --execute=file_to_run - execute the given file upon receiving a connection")
    print("-c --command             - initialize a command shell")
    print("-u --upload=destination  - upon receiving connection upload a file and write to [destination]")
    print("\nExamples:")
    print("bhpnet.py -t 192.168.0.1 -p 5555 -l -c")
    print("bhpnet.py -t 192.168.0.1 -p 5555 -l -u=c:\\target.exe")
    print("bhpnet.py -t 192.168.0.1 -p 5555 -l -e=\"cat /etc/passwd\"")
    print("echo 'ABCDEFGHI' | ./bhpnet.py -t 192.168.11.12 -p 135")
    sys.exit(0)

def main():
    global listen, port, execute, command, upload_destination, target

    if not len(sys.argv[1:]):
        usage()

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hle:t:p:cu:",
                                    ["help", "listen", "execute=", "target=", "port=", "command", "upload="])
    except getopt.GetoptError as err:
        print(str(err))
        usage()

    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
        elif o in ("-l", "--listen"):
            listen = True
        elif o in ("-e", "--execute"):
            execute = a
        elif o in ("-c", "--command"):
            command = True
        elif o in ("-u", "--upload"):
            upload_destination = a
        elif o in ("-t", "--target"):
            target = a
        elif o in ("-p", "--port"):
            port = int(a)
        else:
            assert False, "Unhandled Option"

    if not listen and len(target) and port > 0:
        buffer = sys.stdin.read()
        client_sender(buffer)

    if listen:
        server_loop()

def client_sender(buffer):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client.connect((target, port))
        if len(buffer):
            client.send(buffer.encode())

        while True:
            response = b""
            while True:
                data = client.recv(4096)
                response += data
                if len(data) < 4096:
                    break
            print(response.decode(), end="")

            buffer = input("") + "\n"
            client.send(buffer.encode())

    except Exception as e:
        print(f"[*] Exception: {e}. Exiting...")
        client.close()

def server_loop():
    global target
    if not len(target):
        target = "0.0.0.0"

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((target, port))
    server.listen(5)

    while True:
        client_socket, addr = server.accept()
        client_thread = threading.Thread(target=client_handler, args=(client_socket,))
        client_thread.start()

def run_command(command):
    command = command.rstrip()
    try:
        if command.startswith("cd "):
            path = command[3:].strip()
            os.chdir(path)
            return f"Changed directory to {os.getcwd()}\r\n".encode()
        elif command == "ls" or command == "dir":
            output = "\n".join(os.listdir(os.getcwd())).encode()
        elif command.startswith("rm "):
            os.remove(command[3:].strip())
            output = b"File deleted.\r\n"
        elif command.startswith("mkdir "):
            os.mkdir(command[6:].strip())
            output = b"Directory created.\r\n"
        elif command == "whoami":
            output = subprocess.check_output("whoami", shell=True)
        elif command.startswith("ping "):
            output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
        else:
            output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
    except subprocess.CalledProcessError:
        output = b"Failed to execute command.\r\n"
    except FileNotFoundError:
        output = b"File or directory not found.\r\n"
    return output

def client_handler(client_socket):
    global upload, execute, command

    if len(upload_destination):
        file_buffer = b""

        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            file_buffer += data

        try:
            with open(upload_destination, "wb") as f:
                f.write(file_buffer)
            client_socket.send(f"Successfully saved file to {upload_destination}\r\n".encode())
        except Exception as e:
            client_socket.send(f"Failed to save file to {upload_destination}. Error: {e}\r\n".encode())

    if len(execute):
        output = run_command(execute)
        client_socket.send(output)

    if command:
        while True:
            client_socket.send(b"<BHP:#> ")
            cmd_buffer = b""
            while b"\n" not in cmd_buffer:
                cmd_buffer += client_socket.recv(1024)
            response = run_command(cmd_buffer.decode())
            client_socket.send(response)

main()

