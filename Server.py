import socket
import threading
import tkinter as tk
from tkinter import scrolledtext

clients = []
client_names = {}  # Menyimpan nama atau ID untuk setiap klien


def handle_client(client_socket, text_area):
    # Memberikan ID unik untuk klien berdasarkan jumlah koneksi
    client_id = f"Client {len(clients)}"
    client_names[client_socket] = client_id
    update_text_area(text_area, f"{client_id} connected.")

    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if message.startswith("TYPING:"):
                # Kirim notifikasi mengetik ke semua klien
                broadcast(f"{client_names[client_socket]} is typing...", client_socket)
            else:
                # Kirim pesan ke semua klien
                broadcast(f"{client_names[client_socket]}: {message}", client_socket)
                update_text_area(text_area, f"{client_names[client_socket]}: {message}")
        except:
            # Jika ada masalah, hapus klien dari daftar
            remove(client_socket, text_area)
            break


def broadcast(message, client_socket=None):
    """Mengirim pesan ke semua klien, kecuali pengirim."""
    for client in clients:
        if client != client_socket:
            try:
                client.send(message.encode('utf-8'))
            except:
                remove(client)


def remove(client_socket, text_area):
    """Menghapus klien yang terputus dan memberi tahu semua klien lain."""
    if client_socket in clients:
        update_text_area(text_area, f"{client_names[client_socket]} disconnected.")
        clients.remove(client_socket)
        del client_names[client_socket]


def update_text_area(text_area, message):
    """Memperbarui area teks di GUI server."""
    text_area.configure(state='normal')
    text_area.insert('end', f"{message}\n")
    text_area.configure(state='disabled')
    text_area.yview('end')


def send_server_message(entry_field, text_area):
    """Mengirim pesan dari server ke semua klien."""
    message = entry_field.get()
    if message.strip():
        update_text_area(text_area, f"Server: {message}")
        broadcast(f"Server: {message}")
        entry_field.delete(0, 'end')


def insert_emoticon(entry_field, emoticon):
    """Memasukkan emotikon ke dalam field input."""
    entry_field.insert('end', emoticon)


def start_server(text_area):
    """Memulai server dan mendengarkan koneksi klien."""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('10.23.3.194', 12346))  # Ubah IP sesuai kebutuhan
    server.listen(5)
    update_text_area(text_area, "Server is listening on port 12346")

    while True:
        try:
            client_socket, addr = server.accept()
            clients.append(client_socket)
            threading.Thread(target=handle_client, args=(client_socket, text_area)).start()
        except Exception as e:
            update_text_area(text_area, f"Server error: {e}")
            break


def main():
    root = tk.Tk()
    root.title("Server Chat")

    # Area teks untuk menampilkan log server
    text_area = scrolledtext.ScrolledText(root, state='disabled', width=50, height=20)
    text_area.pack(padx=10, pady=10)

    # Field input untuk pesan server
    entry_field = tk.Entry(root, width=40)
    entry_field.pack(side='left', padx=(10, 0), pady=(0, 10))

    send_button = tk.Button(root, text="Send", command=lambda: send_server_message(entry_field, text_area))
    send_button.pack(side='right', padx=(0, 10), pady=(0, 10))

    # Frame untuk tombol emotikon
    emoticon_frame = tk.Frame(root)
    emoticon_frame.pack(pady=(10, 0))

    # Daftar emotikon
    emoticons = ['😊', '😂', '😍', '😡', '❤️']
    for emoticon in emoticons:
        button = tk.Button(emoticon_frame, text=emoticon, command=lambda e=emoticon: insert_emoticon(entry_field, e))
        button.pack(side='left', padx=5)

    # Jalankan server dalam thread terpisah
    threading.Thread(target=start_server, args=(text_area,), daemon=True).start()

    root.mainloop()


if __name__ == "__main__":
    main()
