import socket
import uuid

connection_codes = {}

def handle_sender(sender_conn):
    connection_code = str(uuid.uuid4())
    print(f"Connection code: {connection_code}")
    sender_conn.sendall(connection_code.encode())
    connection_codes[connection_code] = connection_code


    # while connection_code not in connection_codes:
    #     pass  # Busy-wait until a receiver connects

    receiver_conn = connection_codes[connection_code]
    sender_conn.sendall(b"READY")

    while True:
        data = sender_conn.recv(1024)
        if data.endswith(b"END_OF_FILE"):
            receiver_conn.sendall(data)
            break
        receiver_conn.sendall(data)

    sender_conn.close()
    receiver_conn.close()
    del connection_codes[connection_code]

def handle_receiver(receiver_conn):
    connection_code = receiver_conn.recv(1024).decode()
    print(f"Connection code: {connection_code}")

    if connection_code in connection_codes:
        receiver_conn.sendall(b"READY")
        connection_codes[connection_code] = receiver_conn
    else:
        receiver_conn.sendall(b"INVALID_CODE")
        receiver_conn.close()
        return

def start_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((socket.gethostname(), 8000))
    sock.listen(5)

    print('Server is listening for connections...')

    while True:
        conn, addr = sock.accept()
        client_type = conn.recv(1024).decode()

        if client_type == "SENDER":
            print('Sender connected from', addr)
            handle_sender(conn)
        elif client_type == "RECEIVER":
            print('Receiver connected from', addr)
            handle_receiver(conn)
        else:
            conn.close()

if __name__ == "__main__":
    start_server()
