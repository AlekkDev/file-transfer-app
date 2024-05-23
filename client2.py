import socket
import os
import tkinter as tk
from tkinter import filedialog, messagebox

class FileTransferApp:
    def __init__(self, root):
        self.root = root
        self.setup_main_window()

    def setup_main_window(self):
        self.root.title("File Transfer App")
        self.root.geometry("450x560+500+200")
        self.root.configure(bg="#f4fdfe")
        self.root.resizable(False, False)

        tk.Label(self.root, text="File Transfer App", font=("Arial", 20), bg="#f4fdfe").place(x=20, y=30)
        tk.Frame(self.root, width=400, height=2, bg="black").place(x=25, y=80)

        send_image = tk.PhotoImage(file="send.png")
        send_button = tk.Button(self.root, image=send_image, text="Send Image", font=("Arial", 15), bg="#f4fdfe",
                                command=self.open_send_window)
        send_button.image = send_image  # Keep a reference to the image
        send_button.place(x=50, y=100)

        receive_image = tk.PhotoImage(file="receive.png")
        receive_button = tk.Button(self.root, image=receive_image, text="Receive Image", font=("Arial", 15), bg="#f4fdfe",
                                   command=self.open_receive_window)
        receive_button.image = receive_image  # Keep a reference to the image
        receive_button.place(x=250, y=100)

        tk.Label(self.root, text="Send", font=("Arial", 15), bg="#f4fdfe").place(x=90, y=240)
        tk.Label(self.root, text="Receive", font=("Arial", 15), bg="#f4fdfe").place(x=280, y=240)

        self.root.mainloop()

    def check_server_status(self):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((socket.gethostname(), 8000))
            sock.close()
            return True
        except ConnectionRefusedError:
            return False

    def get_connection_code(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.connect((socket.gethostname(), 8000))
            sock.sendall(b"SENDER")

            # Receive the connection code from the server
            connection_code = sock.recv(1024).decode()
            print(f"Connection code: {connection_code}")
            return connection_code
        finally:
            sock.close()

    def open_send_window(self):
        if not self.check_server_status():
            messagebox.showerror("Error", "Server is not running")
            return
        send_window = tk.Toplevel(self.root)
        send_window.title("Send Image")
        send_window.geometry("400x300+500+200")
        send_window.configure(bg="#f4fdfe")
        send_window.resizable(False, False)
        send_window.wm_attributes("-topmost", 1)

        code = self.get_connection_code()
        self.enable_file_send(send_window)
        code_entry = tk.Entry(send_window, font=("Arial", 12), bg="#f4fdfe", justify='center')
        code_entry.place(x=20, y=150, width=200)
        code_entry.insert(0, code)
        code_entry.config(state='readonly')

        copy_button = tk.Button(send_window, text="Copy",
                                command=lambda: self.copy_code(send_window, code_entry.get()))
        copy_button.place(x=230, y=150)

    def send(self, file_name: str):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.connect((socket.gethostname(), 8000))
            sock.sendall(b"SENDER")

            # Receive the connection code from the server
            connection_code = sock.recv(1024).decode()
            print(f"Connection code: {connection_code}")

            # Wait for the server to signal readiness
            ready_signal = sock.recv(1024)
            if ready_signal != b"READY":
                print("Server is not ready")
                return

            with open(file_name, 'rb') as file:
                while data := file.read(1024):
                    sock.sendall(data)

            sock.sendall(b"END_OF_FILE")
            print(f"File sent: {os.path.getsize(file_name)} bytes")
        finally:
            sock.close()

    def copy_code(self, window, code):
        window.clipboard_clear()
        window.clipboard_append(code)

    def enable_file_send(self, send_window):
        tk.Label(send_window, text="Select the file to send:", font=("Arial", 12), bg="#f4fdfe").place(x=20, y=30)
        file_path_entry = tk.Entry(send_window, width=30)
        file_path_entry.place(x=20, y=60)

        browse_button = tk.Button(send_window, text="Browse", command=lambda: self.browse_file(file_path_entry))
        browse_button.place(x=260, y=55)

        send_button = tk.Button(send_window, text="Send", command=lambda: self.send(file_path_entry.get()))
        send_button.place(x=320, y=55)

    def browse_file(self, entry):
        file_path = filedialog.askopenfilename()
        entry.delete(0, tk.END)
        entry.insert(0, file_path)

    def open_receive_window(self):
        receive_window = tk.Toplevel(self.root)
        receive_window.title("Receive Image")
        receive_window.geometry("400x300+500+200")
        receive_window.configure(bg="#f4fdfe")
        receive_window.resizable(False, False)

        tk.Label(receive_window, text="Enter Connection Code:", font=("Arial", 12), bg="#f4fdfe").place(x=20, y=30)
        code_entry = tk.Entry(receive_window, width=30)
        code_entry.place(x=20, y=60)

        receive_button = tk.Button(receive_window, text="Receive", command=lambda: self.receive(code_entry.get()))
        receive_button.place(x=320, y=55)

    def receive(self, connection_code):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.connect((socket.gethostname(), 8000))
            sock.sendall(b"RECEIVER")

            # Send the connection code to the server
            sock.sendall(connection_code.encode())

            ready_signal = sock.recv(1024)
            if ready_signal != b"READY":
                messagebox.showerror("Error", "Invalid connection code")
                print("Invalid connection code")
                return

            with open('image_received.jpg', 'wb') as file:
                while True:
                    file_data = sock.recv(1024)
                    if file_data.endswith(b'END_OF_FILE'):
                        file.write(file_data[:-len(b'END_OF_FILE')])
                        break
                    file.write(file_data)

            print("File 'image_received.jpg' received")
        finally:
            sock.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = FileTransferApp(root)
