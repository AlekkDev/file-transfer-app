import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind((socket.gethostname(), 8000))
sock.listen(1)
print('Listening on', sock.getsockname())

conn, addr = sock.accept()
print('Connection from', addr)

file_name = 'image_received.jpg'
file = open(file_name, 'wb')
# file_data = ""
while True:
    file_data = conn.recv(1024)
    if file_data.endswith(b'END_OF_FILE'):
        file.write(file_data[:-len(b'END_OF_FILE')])
        break
    file.write(file_data)

print(f"File {file_name} received")

conn.close()