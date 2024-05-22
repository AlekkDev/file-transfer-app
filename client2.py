import socket
import os
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import uuid

root = tk.Tk()
root.title("File Transfer App")
root.geometry("450x560+500+200")
root.configure(bg="#f4fdfe")
root.resizable(False, False)

tk.Label(root, text="File Transfer App", font=("Arial", 20), bg="#f4fdfe").place(x=20, y=30)
tk.Frame(root, width=400, height=2, bg="black").place(x=25, y=80)

send_image = tk.PhotoImage(file="send.png")
send_button = tk.Button(root, image=send_image, text="Send Image", font=("Arial", 15), bg="#f4fdfe",
                        command=lambda: open_send_window())
send_button.place(x=50, y=100)

receive_image = tk.PhotoImage(file="receive.png")
receive_button = tk.Button(root, image=receive_image, text="Receive Image", font=("Arial", 15), bg="#f4fdfe",
                           command=lambda: open_receive_window())
receive_button.place(x=250, y=100)

tk.Label(root, text="Send", font=("Arial", 15), bg="#f4fdfe").place(x=90, y=240)
tk.Label(root, text="Receive", font=("Arial", 15), bg="#f4fdfe").place(x=280, y=240)


def open_send_window():
    send_window = tk.Toplevel(root)
    send_window.title("Send Image")
    send_window.geometry("400x300+500+200")
    send_window.configure(bg="#f4fdfe")
    send_window.resizable(False, False)
    send_window.wm_attributes("-topmost", 1)

    def send(file_name: str):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((socket.gethostname(), 8000))

        ready_signal = sock.recv(1024)
        if ready_signal != b"READY":
            print("Server is not ready")
            sock.close()
            return

        file = open(file_name, 'rb')
        file_size = os.path.getsize(file_name)

        while True:
            data = file.read(1024)
            if not data:
                break
            sock.sendall(data)

        sock.send(b"END_OF_FILE")
        print(f"File sent: {file_size} bytes")

        file.close()
        sock.close()

    def is_ready():
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((socket.gethostname(), 8000))
            ready_signal = sock.recv(1024)
            if ready_signal != b"READY":
                print("Server is not ready")
                sock.close()
                return False
            return True
        except ConnectionRefusedError:
            return False


    tk.Button(send_window, text = "Generate Connection Code", command = lambda: generate_code()).place(x=20, y=120)
    def generate_code():
        code = generate_connection_code()
        # Create a read-only Entry widget for the connection code
        code_entry = tk.Entry(send_window, font=("Arial", 12), bg="#f4fdfe", justify='center')
        code_entry.place(x=20, y=150, width=200)

        # Insert the code into the Entry widget and make it read-only
        code_entry.insert(0, code)
        code_entry.config(state='readonly')

        #CALLED FUNCTION TO COPY CONNECTION CODE
        def copy_code():
            send_window.clipboard_clear()
            send_window.clipboard_append(code_entry.get())

        # Add a button to copy the code to the clipboard
        copy_button = tk.Button(send_window, text="Copy", command=copy_code)
        copy_button.place(x=230, y=150)
        enable_file_send()
        print(is_ready())

    def enable_file_send():
        tk.Label(send_window, text="Select the file to send:", font=("Arial", 12), bg="#f4fdfe").place(x=20, y=30)
        file_path_entry = tk.Entry(send_window, width=30)
        file_path_entry.place(x=20, y=60)
        def browse_file():
            file_path = filedialog.askopenfilename()
            file_path_entry.insert(0, file_path)

        browse_button = tk.Button(send_window, text="Browse", command=browse_file)
        browse_button.place(x=260, y=55)

        send_button = tk.Button(send_window, text="Send", command=lambda: send(file_path_entry.get()))
        send_button.place(x=320, y=55)


def open_receive_window():
    receive_window = tk.Toplevel(root)
    receive_window.title("Receive Image")
    receive_window.geometry("400x300+500+200")
    receive_window.configure(bg="#f4fdfe")
    receive_window.resizable(False, False)

    def receive():
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((socket.gethostname(), 8000))
        file_name = 'image_received.jpg'
        file = open(file_name, 'wb')
        while True:
            file_data = sock.recv(1024)
            if file_data.endswith(b'END_OF_FILE'):
                file.write(file_data[:-len(b'END_OF_FILE')])
                break
            file.write(file_data)

        print(f"File {file_name} received")
        file.close()
        sock.close()

    receive_button = tk.Button(receive_window, text="Receive", command=receive)
    receive_button.place(x=160, y=100)


def generate_connection_code():
    return uuid.uuid4()



root.mainloop()
