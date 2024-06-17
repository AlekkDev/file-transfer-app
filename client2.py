import socket
import os
import tkinter as tk
from tkinter import filedialog, messagebox
import threading

class FileTransferApp:
    def __init__(self, root):
        self.root = root
        self.setup_main_window()
        self.server_socket = None
        self.file_to_send = None

    def setup_main_window(self):
        self.root.title("File Transfer App")
        self.root.geometry("450x560+500+200")
        self.root.configure(bg="#f4fdfe")
        self.root.resizable(False, False)

        tk.Label(self.root, text="File Transfer App", font=("Arial", 20), bg="#f4fdfe").place(x=20, y=30)
        tk.Frame(self.root, width=400, height=2, bg="black").place(x=25, y=80)

        send_image = tk.PhotoImage(file="Images/send.png")
        self.send_image = send_image
        send_button = tk.Button(self.root, image=send_image, text="Send Image", font=("Arial", 15), bg="#f4fdfe", command=self.open_send_window)
        send_button.place(x=50, y=100)

        receive_image = tk.PhotoImage(file="Images/receive.png")
        self.receive_image = receive_image
        receive_button = tk.Button(self.root, image=receive_image, text="Receive Image", font=("Arial", 15), bg="#f4fdfe", command=self.open_receive_window)
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

    def display_connection_code(self, code, send_window):
        try:
            code_entry = tk.Entry(send_window, font=("Arial", 12), bg="#f4fdfe", justify='center')
            code_entry.place(x=20, y=150, width=200)
            code_entry.insert(0, code)
            code_entry.config(state='readonly')

            copy_button = tk.Button(send_window, text="Copy", command=lambda: self.copy_code(send_window, code_entry.get()))
            copy_button.place(x=230, y=150)
        except Exception as e:
            print(f"Error: {e}")

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

        tk.Label(send_window, text="Select the file to send:", font=("Arial", 12), bg="#f4fdfe").place(x=20, y=30)
        file_path_entry = tk.Entry(send_window, width=30)
        file_path_entry.place(x=20, y=60)

        browse_button = tk.Button(send_window, text="Browse", command=lambda: self.browse_file(file_path_entry))
        browse_button.place(x=260, y=55)

        send_button = tk.Button(send_window, text="Send", command=lambda: threading.Thread(target=self.send_file, args=(file_path_entry.get(), send_window)).start())
        send_button.place(x=320, y=55)

    def send_file(self, file_path, send_window):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((socket.gethostname(), 8000))
        sock.sendall(b"SENDER")
        response = sock.recv(1024).decode()
        if response != "READY":
            print(response)
            return
        sock.sendall(b"READY")
        connection_code = sock.recv(1024).decode()

        try:
            self.display_connection_code(connection_code, send_window)

            await_ready = sock.recv(1024).decode()
            if await_ready == "READY":
                print("Waiting for receiver to be ready...")

            start_transfer = sock.recv(1024).decode()
            if start_transfer == "START_TRANSFER":
                self.send_file_data(sock, file_path)
                sock.sendall(b"END_OF_FILE")
                print(f"File sent: {os.path.getsize(file_path)} bytes")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            sock.close()

    def send_file_data(self, sock, file_path):
        try:
            with open(file_path, 'rb') as file:
                while data := file.read(1024):
                    sock.sendall(data)
        except Exception as e:
            print(f"Error: {e}")

    def copy_code(self, window, code):
        window.clipboard_clear()
        window.clipboard_append(code)

    def browse_file(self, entry):
        file_path = filedialog.askopenfilename()
        entry.delete(0, tk.END)
        entry.insert(0, file_path)

    def open_receive_window(self):
        if not self.check_server_status():
            messagebox.showerror("Error", "Server is not running")
            return

        receive_window = tk.Toplevel(self.root)
        receive_window.title("Receive Image")
        receive_window.geometry("400x300+500+200")
        receive_window.configure(bg="#f4fdfe")
        receive_window.resizable(False, False)

        tk.Label(receive_window, text="Enter Connection Code:", font=("Arial", 12), bg="#f4fdfe").place(x=20, y=30)
        code_entry = tk.Entry(receive_window, width=30)
        code_entry.place(x=20, y=60)

        receive_button = tk.Button(receive_window, text="Connect", command=lambda: self.receiver_connect(code_entry.get()))
        receive_button.place(x=320, y=55)

    def receiver_connect(self, code):
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.connect((socket.gethostname(), 8000))
            self.server_socket.sendall(b"RECEIVER")
            self.server_socket.sendall(code.encode())
            await_ready = self.server_socket.recv(1024).decode()
            if await_ready != "CONNECTION_ESTABLISHED":
                print(await_ready)
                return
            print("Connection established")

            receiver_thread = threading.Thread(target=self.receiver_thread)
            receiver_thread.start()
        except Exception as e:
            print(f"Error: {e}")

    def receiver_thread(self):
        try:
            with open('image_received.jpg', 'wb') as file:
                while True:
                    file_data = self.server_socket.recv(1024)
                    if file_data.endswith(b'END_OF_FILE'):
                        file.write(file_data[:-len(b'END_OF_FILE')])
                        break
                    file.write(file_data)
            print(f"File 'image_received.jpg' received")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            self.server_socket.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = FileTransferApp(root)
