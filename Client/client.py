import socket
import threading

def receive_messages(client_socket):
    while True:
        try:
            message = client_socket.recv(1024).decode()
            if message:
                print(message)
        except:
            print("[ERROR] Connection lost.")
            break

def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_ip = input("Enter server IP: ")
    server_port = 5555

    try:
        client.connect((server_ip, server_port))
        print("[CONNECTED] Connected to the server.")
    except:
        print("[ERROR] Unable to connect to the server.")
        return

    # Thread untuk menerima pesan
    thread = threading.Thread(target=receive_messages, args=(client,))
    thread.start()

    # Kirim pesan
    while True:
        message = input()
        try:
            client.send(message.encode())
        except:
            print("[ERROR] Failed to send message.")
            break

if __name__ == "__main__":
    main()
