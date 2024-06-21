import socket
import uuid
import threading

connection_codes = {}
condition = threading.Condition()

def handle_sender(sender_conn):
    receiver_conn = None
    connection_code = None
    try:
        sender_conn.sendall(b"READY")
        if sender_conn.recv(1024).decode() != "READY":
            print("Sender did not respond with READY")
            return

        connection_code = str(uuid.uuid4())
        print(f"Generated connection code: {connection_code}")
        sender_conn.sendall(connection_code.encode())

        with condition:
            connection_codes[connection_code] = None
            sender_conn.sendall(b"READY")
            print(f"Waiting for receiver to connect with code: {connection_code}")
            while connection_codes[connection_code] is None:
                condition.wait()

            receiver_conn = connection_codes[connection_code]
            print(f"Receiver connected for code: {connection_code}")
            print(f"RECEIVER CONNECTION: {receiver_conn}")

        # Receive and forward the file name
        file_name = sender_conn.recv(1024).decode()
        receiver_conn.sendall(file_name.encode())

        print("Starting file transfer...")
        sender_conn.sendall(b"START_TRANSFER")
        while True:
            data = sender_conn.recv(1024)
            if not data or data.endswith(b"END_OF_FILE"):
                receiver_conn.sendall(data)
                break
            receiver_conn.sendall(data)

        print("File transfer completed from sender to receiver.")

    finally:
        sender_conn.close()
        if receiver_conn:
            receiver_conn.close()
        with condition:
            if connection_code and connection_code in connection_codes:
                del connection_codes[connection_code]
# HANDLE RECEIVER CONNECTION
def handle_receiver(receiver_conn):
    try:
        receiver_conn.sendall(b"READY")
        connection_code = receiver_conn.recv(1024).decode()

        print(f"Receiver connected with connection code: {connection_code}")
        print("Available connection codes: ", connection_codes)
        #
        # THREADING CONDITION + CHECK IF CODE VALID AND NOTIFY ALL THREADS
        with condition:
            if connection_code in connection_codes:
                connection_codes[connection_code] = receiver_conn

                print(f"Receiver connection = {receiver_conn} ", connection_codes[connection_code])
                condition.notify_all()
                receiver_conn.sendall(b"CONNECTION_ESTABLISHED")
                print(f"Connection established for code: {connection_code}")
            else:
                receiver_conn.sendall(b"INVALID_CODE")
                receiver_conn.close()
                print(f"Invalid connection code: {connection_code}")
                return

        # Receive the file name
        file_name = receiver_conn.recv(1024).decode()
        print(f"Receiving file: {file_name}")

        # Receive the file data
        with open(file_name, 'wb') as file:
            while True:
                data = receiver_conn.recv(1024)
                if not data:
                    break
                # Check if the file transfer is complete
                if data.endswith(b'END_OF_FILE'):
                    file.write(data[:-11])
                    break
                file.write(data)

        print("File received")

    finally:
        receiver_conn.close()

# STARTS SERVER AND LISTENS FOR CONNECTIONS
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
