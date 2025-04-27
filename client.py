import socket
import sys
import os
import random

def recv_all(sock):
    data = b''
    while True:
        part = sock.recv(4096)
        if not part:
            break
        data += part
    return data

def create_data_socket():
    data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    data_socket.bind(('', 0))  # Bind to ephemeral port
    data_socket.listen(1)
    port = data_socket.getsockname()[1]
    return data_socket, port

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python cli.py <server name> <server port>")
        sys.exit(1)

    server_name = sys.argv[1]
    server_port = int(sys.argv[2])

    control_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    control_socket.connect((server_name, server_port))

    while True:
        cmd = input("ftp> ").strip()
        if not cmd:
            continue
        tokens = cmd.split()
        if tokens[0] == 'quit':
            control_socket.sendall(cmd.encode())
            print(control_socket.recv(1024).decode())
            break

        elif tokens[0] in ['ls', 'get', 'put']:
            data_socket, data_port = create_data_socket()

            if tokens[0] == 'ls':
                control_socket.sendall(f"ls {data_port}".encode())
                conn, addr = data_socket.accept()
                data = recv_all(conn)
                print(data.decode())
                conn.close()

            elif tokens[0] == 'get' and len(tokens) >= 2:
                filename = tokens[1]
                control_socket.sendall(f"get {filename} {data_port}".encode())
                conn, addr = data_socket.accept()
                data = recv_all(conn)
                if data:
                    with open(filename, 'wb') as f:
                        f.write(data)
                    print(f"Received {len(data)} bytes into {filename}")
                conn.close()

            elif tokens[0] == 'put' and len(tokens) >= 2:
                filename = tokens[1]
                if not os.path.exists(filename):
                    print(f"Local file {filename} does not exist")
                    data_socket.close()
                    continue
                control_socket.sendall(f"put {filename} {data_port}".encode())
                conn, addr = data_socket.accept()
                with open(filename, 'rb') as f:
                    conn.sendall(f.read())
                conn.close()

            print(control_socket.recv(1024).decode())
            data_socket.close()

        else:
            print("Unknown command")

    control_socket.close()