import socket
import threading
import uuid

# Dictionary to store connection codes and corresponding connections
connection_codes = {}


def handle_sender(sender_conn):
    # Generate a unique connection code
    connection_code = str(uuid.uuid4())
    print( f"Connection code: {connection_code}")
    # Send the connection code to the sender
    sender_conn.sendall(connection_code.encode())

    # Wait for the receiver to connect with the same code
    while connection_code not in connection_codes:
        pass

    receiver_conn = connection_codes[connection_code]

    sender_conn.sendall(b"READY")  # Signal sender that receiver is ready
    while True:
        data = sender_conn.recv(1024)
        if not data:
            break
        receiver_conn.sendall(data)
    receiver_conn.sendall(b"END_OF_FILE")
    sender_conn.close()
    receiver_conn.close()
    del connection_codes[connection_code]


def handle_receiver(receiver_conn):
    # Receive the connection code from the receiver
    connection_code = receiver_conn.recv(1024).decode()

    if connection_code in connection_codes:
        receiver_conn.sendall(b"READY")
        connection_codes[connection_code] = receiver_conn
    else:
        receiver_conn.sendall(b"INVALID_CODE")
        receiver_conn.close()


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
            sender_thread = threading.Thread(target=handle_sender, args=(conn,))
            sender_thread.start()
        elif client_type == "RECEIVER":
            print('Receiver connected from', addr)
            receiver_thread = threading.Thread(target=handle_receiver, args=(conn,))
            receiver_thread.start()
        else:
            conn.close()


if __name__ == "__main__":
    start_server()
