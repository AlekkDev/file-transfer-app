import socket
import os
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((socket.gethostname(), 8000))


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
