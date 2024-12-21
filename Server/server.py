import socket
import threading

# Fungsi untuk menangani setiap klien
def handle_client(client_socket, addr, clients):
    print(f"[NEW CONNECTION] {addr} connected.")
    while True:
        try:
            message = client_socket.recv(1024).decode()
            if message:
                print(f"[{addr}] {message}")
                # Kirim pesan ke semua klien lain
                broadcast(message, client_socket, clients)
        except:
            print(f"[DISCONNECTED] {addr} disconnected.")
            clients.remove(client_socket)
            break

# Fungsi untuk mengirim pesan ke semua klien
def broadcast(message, sender_socket, clients):
    for client in clients:
        if client != sender_socket:
            try:
                client.send(message.encode())
            except:
                client.close()
                clients.remove(client)

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", 5555))
    server.listen(5)
    print("[SERVER STARTED] Waiting for connections...")
    clients = []
    
    while True:
        client_socket, addr = server.accept()
        clients.append(client_socket)
        thread = threading.Thread(target=handle_client, args=(client_socket, addr, clients))
        thread.start()

if __name__ == "__main__":
    main()
