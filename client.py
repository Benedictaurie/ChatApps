import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox


def receive_messages(sock, text_area, typing_label):
    """Menerima pesan dari server dan menampilkan di GUI."""
    while True:
        try:
            message = sock.recv(1024).decode('utf-8')
            if not message:  # Jika server memutuskan koneksi
                raise ConnectionError

            if message.startswith("TYPING:"):
                # Menampilkan siapa yang sedang mengetik di label typing_label
                typing_label.config(text=message[7:])
            else:
                # Menghapus label mengetik saat pesan diterima
                typing_label.config(text="")
                text_area.configure(state='normal')
                text_area.insert('end', f"{message}\n", "incoming_message")
                text_area.configure(state='disabled')
                text_area.yview('end')

        except ConnectionError:
            messagebox.showerror("Error", "Connection to the server was lost.")
            sock.close()
            break
        except Exception as e:
            print(f"Error receiving message: {e}")
            break


def send_message(sock, entry_field, text_area):
    """Mengirim pesan ke server dan menampilkannya di area obrolan."""
    message = entry_field.get()
    if message.strip():
        try:
            # Tampilkan pesan di area teks sebelum mengirimnya ke server
            text_area.configure(state='normal')
            text_area.insert('end', f"You: {message}\n", "self_message")
            text_area.configure(state='disabled')
            text_area.yview('end')

            sock.send(message.encode('utf-8'))
            entry_field.delete(0, 'end')
        except Exception as e:
            print(f"Error sending message: {e}")
            messagebox.showerror("Error", "Failed to send the message. Please try again.")


def notify_typing(sock, username):
    """Memberi tahu server bahwa klien sedang mengetik."""
    try:
        sock.send(f"TYPING:{username} is typing...".encode('utf-8'))
    except Exception as e:
        print(f"Error sending typing notification: {e}")


def insert_emoticon(entry_field, emoticon):
    """Memasukkan emotikon ke dalam field input."""
    entry_field.insert('end', emoticon)


def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect(('10.23.3.194', 12346))  # Ubah IP sesuai server
    except ConnectionRefusedError:
        messagebox.showerror("Error", "Connection failed. Make sure the server is running.")
        return

    # GUI Root Window
    root = tk.Tk()
    root.title("Client Chat")
    root.geometry("400x500")

    # Area teks untuk menampilkan pesan
    text_area = scrolledtext.ScrolledText(root, state='disabled', wrap='word', width=50, height=20)
    text_area.pack(padx=10, pady=10)
    text_area.tag_config("self_message", foreground="blue")  # Tag untuk pesan sendiri
    text_area.tag_config("incoming_message", foreground="green")  # Tag untuk pesan masuk

    # Label untuk notifikasi mengetik
    typing_label = tk.Label(root, text="", fg="gray", font=("Arial", 10, "italic"))
    typing_label.pack(pady=(0, 10))

    # Frame untuk input dan tombol kirim
    input_frame = tk.Frame(root)
    input_frame.pack(pady=(0, 10))

    # Field input untuk pesan
    entry_field = tk.Entry(input_frame, width=30, font=("Arial", 12))
    entry_field.pack(side='left', padx=(10, 5))

    # Tombol Kirim
    send_button = tk.Button(input_frame, text="Send", width=10, command=lambda: send_message(client_socket, entry_field, text_area))
    send_button.pack(side='right', padx=(5, 10))

    # Mengirim notifikasi mengetik saat pengguna mengetik
    entry_field.bind("<KeyPress>", lambda e: notify_typing(client_socket, "Client"))

    # Frame untuk tombol emotikon
    emoticon_frame = tk.Frame(root)
    emoticon_frame.pack(pady=(0, 10))

    # Daftar emotikon
    emoticons = ['😊', '😂', '😡', '❤️', '🥹', '💀']
    for emoticon in emoticons:
        button = tk.Button(emoticon_frame, text=emoticon, width=3, command=lambda e=emoticon: insert_emoticon(entry_field, e))
        button.pack(side='left', padx=5)

    # Thread untuk menerima pesan dari server
    threading.Thread(target=receive_messages, args=(client_socket, text_area, typing_label), daemon=True).start()

    root.mainloop()
    client_socket.close()


if __name__ == "__main__":
    main()
