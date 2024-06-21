import socket
import uuid
import threading
import time
import sqlite3
from datetime import datetime

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

        #### SQL DATABASE ####
        # Get the sender IP
        sender_ip = sender_conn.getpeername()[0]
        # Get the receiver IP
        receiver_ip = receiver_conn.getpeername()[0]
        # Store the transfer in the database
        log_transfer(sender_ip, receiver_ip, file_name)
        # Small delay to allow the receiver to finish writing the file, otherwise some errors occur
        time.sleep(0.5)
        view_transfer_logs()


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

        # Receive the file name from the sender (via handle_sender)
        file_name = receiver_conn.recv(1024).decode()
        print(f"Receiving file: {file_name}")



    finally:
        receiver_conn.close()

# STARTS SERVER AND LISTENS FOR CONNECTIONS
def start_server():
    initialize_database()
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

def initialize_database():
    conn = sqlite3.connect('file_transfers.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS transfers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender_ip TEXT,
        receiver_ip TEXT,
        transfer_datetime TEXT,
        filename TEXT
    )
    ''')
    conn.commit()
    conn.close()
def log_transfer(sender_ip, receiver_ip, filename):
    conn = sqlite3.connect('file_transfers.db')
    cursor = conn.cursor()
    transfer_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute('''
    INSERT INTO transfers (sender_ip, receiver_ip, transfer_datetime, filename)
    VALUES (?, ?, ?, ?)
    ''', (sender_ip, receiver_ip, transfer_datetime, filename))
    conn.commit()
    conn.close()

def view_transfer_logs():
    conn = sqlite3.connect('file_transfers.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM transfers')
    logs = cursor.fetchall()
    for log in logs:
        print(f"ID: {log[0]}, Sender: {log[1]}, Receiver: {log[2]}, DateTime: {log[3]}, Filename: {log[4]}")
    conn.close()

if __name__ == "__main__":
    start_server()