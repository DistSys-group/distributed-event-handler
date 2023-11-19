import socket
import threading
import argparse

liked_count = 0
lock = threading.Lock()

def handle_client(client_socket):
    global liked_count
    while True:
        # Receive client request
        data = client_socket.recv(1024)
        if not data:
            break
        
        # Process like request
        with lock:
            liked_count += 1
            print(f"Received like. Liked count: {liked_count}")
            send_notifications(OTHER_PORTS, 1)

    client_socket.close()


def send_notifications(other_ports, liked_count_change):
    for port in other_ports:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as node_socket:
            node_socket.connect(('localhost', port))
            node_socket.sendall(str(liked_count_change).encode())
            print(f"Sent notification to node on port {port}")


def receive_notifications(port):
    global liked_count
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind(('localhost', port))
        server_socket.listen(5)
        print(f"Notification server listening on port {port}")

        while True:
            client_socket, client_address = server_socket.accept()
            print(f"Notification connection from {client_address}")

            data = client_socket.recv(1024)
            if data:
                with lock:
                    liked_count += int(data.decode())
                    print(f"Received notification. Liked count: {liked_count}")

            client_socket.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Server for handling 'like' requests and notifications")
    parser.add_argument('port', type=int, help="Port number for handling client requests")
    parser.add_argument('notification_port', type=int, help="Port number for receiving notifications")
    parser.add_argument('other_ports', nargs='+', type=int, help="Ports to send notifications")
    args = parser.parse_args()

    SERVER_PORT = args.port
    NOTIFICATION_PORT = args.notification_port
    OTHER_PORTS = args.other_ports

    # Start thread to listen for notifications from other nodes
    notification_thread = threading.Thread(target=receive_notifications, args=(NOTIFICATION_PORT,))
    notification_thread.start()

    # Start server to handle client requests
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('localhost', SERVER_PORT))
    server.listen(5)
    print(f"Server listening on port {SERVER_PORT}")

    while True:
        client_socket, client_address = server.accept()
        print(f"Connection from {client_address}")
        client_handler = threading.Thread(target=handle_client, args=(client_socket,))
        client_handler.start()
