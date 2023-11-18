import socket
import threading

# Define the server address and port
# NODE1_ADDRESS = '192.168.1.101'  # Replace this with the desired IP address of Node 1
NODE1_PORT = 5001

# Store liked counts (initially zero)
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
        
        # Inform other nodes about the change (synchronization logic needed here)

    client_socket.close()



# Rest of the code remains the same as before...
# Replace occurrences of SERVER_ADDRESS with NODE1_ADDRESS

if __name__ == "__main__":
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('localhost', NODE1_PORT))
    server.listen(5)
    print(f"Node 1 server listening on port {NODE1_PORT}")

    while True:
        client_socket, client_address = server.accept()
        print(f"Connection from {client_address}")
        client_handler = threading.Thread(target=handle_client, args=(client_socket,))
        client_handler.start()
