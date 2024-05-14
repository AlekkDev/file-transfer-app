import socket
import os
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox

root = tk.Tk()
root.title("File Transfer App")
root.geometry("450x560+500+200")
root.configure(bg="#f4fdfe")
root.resizable(False, False)

tk.Label(root, text="File Transfer App", font=("Arial", 20), bg="#f4fdfe").place(x=20, y=30)
tk.Frame(root, width=400, height=2, bg="black").place(x=25, y=80)


send_image = tk.PhotoImage(file="send.png")
send = tk.Button(root, image=send_image, text="Send Image", font=("Arial", 15), bg="#f4fdfe")
send.place(x=50, y=100)

receive_image = tk.PhotoImage(file="receive.png")
receive = tk.Button(root,image=receive_image, text="Receive Image", font=("Arial", 15), bg="#f4fdfe")
receive.place(x=250, y=100)

tk.Label(root, text="Send",font=("Arial", 15), bg="#f4fdfe").place(x=90, y=240)
tk.Label(root, text="Receive",font=("Arial", 15), bg="#f4fdfe").place(x=280, y=240)

root.mainloop()

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

send('image.jpg')



