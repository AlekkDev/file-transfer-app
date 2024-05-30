import socket
import uuid
import threading

connection_codes = {}
condition = threading.Condition()

def handle_sender(sender_conn):
    connection_code = str(uuid.uuid4())
    print(f"Connection code: {connection_code}")
    sender_conn.sendall(connection_code.encode())

    with condition:
        connection_codes[connection_code] = None

        # Wait until a receiver connects
        while connection_codes[connection_code] is None:
            condition.wait()

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

    with condition:
        del connection_codes[connection_code]

def handle_receiver(receiver_conn):
    receiver_conn.sendall(b"READY")
    connection_code = receiver_conn.recv(1024).decode()
    print(f"Connection code: {connection_code}")
    print(connection_codes.keys())

    with condition:
        if connection_code in connection_codes:
            connection_codes[connection_code] = receiver_conn
            condition.notify_all()  # Notify waiting sender
            receiver_conn.sendall(b"READY")
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
            threading.Thread(target=handle_sender, args=(conn,)).start()
        elif client_type == "RECEIVER":
            print('Receiver connected from', addr)
            threading.Thread(target=handle_receiver, args=(conn,)).start()
        else:
            conn.close()

if __name__ == "__main__":
    start_server()
