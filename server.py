import socket
import threading

def handle_sender(sender_conn, receiver_conn):
    sender_conn.sendall(b"READY") # Signal sender that receiver is ready
    while True:
        data = sender_conn.recv(1024)
        if not data:
            break
        receiver_conn.sendall(data)
    receiver_conn.sendall(b"END_OF_FILE")
    sender_conn.close()

def start_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((socket.gethostname(), 8000))
    sock.listen(2)

    print('Server is listening for sender...')
    sender_conn, sender_addr = sock.accept()
    print('Sender connected from', sender_addr)

    print('Server is listening for receiver...')
    receiver_conn, receiver_addr = sock.accept()
    print('Receiver connected from', receiver_addr)

    sender_thread = threading.Thread(target=handle_sender, args=(sender_conn, receiver_conn))
    sender_thread.start()
    sender_thread.join()

    receiver_conn.close()
    sock.close()

start_server()