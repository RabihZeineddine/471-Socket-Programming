import socket
import threading
import os
import sys

def recv_all(sock, length):
    data = b''
    while len(data) < length:
        packet = sock.recv(length - len(data))
        if not packet:
            return None
        data += packet
    return data

def handle_client(control_conn, addr):
    print(f"Connected by {addr}")
    while True:
        cmd = control_conn.recv(1024).decode()
        if not cmd:
            break
        print(f"Command received: {cmd}")

        tokens = cmd.strip().split()
        if not tokens:
            continue

        if tokens[0] == 'quit':
            control_conn.sendall("SUCCESS: Goodbye!".encode())
            break

        elif tokens[0] == 'ls':
            # Set up data connection
            data_port = int(tokens[1])
            data_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            data_conn.connect((addr[0], data_port))

            files = os.listdir('.')
            files_list = "\n".join(files)
            data_conn.sendall(files_list.encode())
            data_conn.close()
            control_conn.sendall("SUCCESS: ls complete".encode())

        elif tokens[0] == 'get' and len(tokens) >= 2:
            filename = tokens[1]
            data_port = int(tokens[2])
            try:
                f = open(filename, 'rb')
                file_data = f.read()
                f.close()
                data_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                data_conn.connect((addr[0], data_port))
                data_conn.sendall(file_data)
                data_conn.close()
                control_conn.sendall(f"SUCCESS: Sent {filename}".encode())
            except FileNotFoundError:
                control_conn.sendall(f"FAILURE: {filename} not found".encode())

        elif tokens[0] == 'put' and len(tokens) >= 2:
            filename = tokens[1]
            data_port = int(tokens[2])
            data_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            data_conn.connect((addr[0], data_port))
            with open(filename, 'wb') as f:
                while True:
                    data = data_conn.recv(4096)
                    if not data:
                        break
                    f.write(data)
            data_conn.close()
            control_conn.sendall(f"SUCCESS: Received {filename}".encode())

        else:
            control_conn.sendall("FAILURE: Invalid command".encode())

    control_conn.close()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python serv.py <PORT>")
        sys.exit(1)

    server_port = int(sys.argv[1])
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('', server_port))
    server_socket.listen(5)
    print("Server is ready to receive")

    while True:
        conn, addr = server_socket.accept()
        client_thread = threading.Thread(target=handle_client, args=(conn, addr))
        client_thread.start()
