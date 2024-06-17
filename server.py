import socket
import uuid
import threading

connection_codes = {}
condition = threading.Condition()

def handle_sender(sender_conn):
    try:
        sender_conn.sendall(b"READY")
        if sender_conn.recv(1024).decode() != "READY":
            return
        connection_code = str(uuid.uuid4())
        print(f"Connection code: {connection_code}")
        sender_conn.sendall(connection_code.encode())

        with condition:
            connection_codes[connection_code] = None
            sender_conn.sendall(b"READY")

            while connection_codes[connection_code] is None:
                condition.wait()

            receiver_conn = connection_codes[connection_code]

        sender_conn.sendall(b"START_TRANSFER")

        while True:
            data = sender_conn.recv(1024)
            if not data or data.endswith(b"END_OF_FILE"):
                receiver_conn.sendall(data)
                break
            receiver_conn.sendall(data)

        print("File transfer completed from sender to receiver.")
    except Exception as e:
        print(f"Error in handle_sender: {e}")
    finally:
        sender_conn.close()
        receiver_conn.close()

        with condition:
            if connection_code in connection_codes:
                del connection_codes[connection_code]

def handle_receiver(receiver_conn):
    try:
        connection_code = receiver_conn.recv(1024).decode()
        print(f"Receiver connected with connection code: {connection_code}")

        with condition:
            if connection_code in connection_codes:
                connection_codes[connection_code] = receiver_conn
                condition.notify_all()
                receiver_conn.sendall(b"CONNECTION_ESTABLISHED")
            else:
                receiver_conn.sendall(b"INVALID_CODE")
                receiver_conn.close()
                return

        while True:
            data = receiver_conn.recv(1024)
            if not data:
                break
            # Receivers do not send data back to sender in this setup.
    except Exception as e:
        print(f"Error in handle_receiver: {e}")
    finally:
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
