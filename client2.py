import socket
import os

def send(file_name: str):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((socket.gethostname(), 8000))

    ready_signal = sock.recv(1024)
    if ready_signal != b"READY":
        print("Server is not ready")
        sock.close()
        return

    file = open('image.jpg', 'rb')
    file_size = os.path.getsize('image.jpg')

    while True:
        data = file.read(1024)
        if not data:
            break
        sock.sendall(data)

    sock.send(b"END_OF_FILE")
    print(f"File sent: {file_size} bytes")

    # CLOSE FILE AND CLIENT SOCKET
    file.close()
    sock.close()

def receive():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((socket.gethostname(), 8000))
    # sock.bind((socket.gethostname(), 8000))
    # sock.listen(1)
    # print('Listening on', sock.getsockname())
    #
    # conn, addr = sock.accept()
    # print('Connection from', addr)

    file_name = 'image_received.jpg'
    file = open(file_name, 'wb')
    # file_data = ""
    while True:
        file_data = sock.recv(1024)
        if file_data.endswith(b'END_OF_FILE'):
            file.write(file_data[:-len(b'END_OF_FILE')])
            break
        file.write(file_data)

    print(f"File {file_name} received")

    sock.close()

receive()