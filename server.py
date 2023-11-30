import socket
import threading
import argparse


lock = threading.Lock()
like_count = 0
LEADER_ADDRESS = ('localhost', 5001)
SERVER_PORT = 0
notification_port = 0
other_nodes = {}
live_clients = []

def handle_client(client_socket):
    global like_count
    
    while True:
        data = client_socket.recv(1024)
        if not data:
            break
        
        # Process like request
        _update_likes()
        print(f"Received like. Like count: {like_count}")
        send_notifications(other_nodes)

    client_socket.close()


# Todo: Modify the message to contain more info (timestamp, node_id)
def send_notifications(other_nodes):
    for node in other_nodes:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as node_socket:
            node_socket.connect(node)
            node_socket.sendall("Like event".encode())
            print(f"Sent notification to node {node}")


def _update_likes():
    global like_count
    with lock:
        like_count += 1


def connect_to_leader():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(LEADER_ADDRESS)
    print(f"Connected to leader node at {LEADER_ADDRESS}")

    # Inform the leader that this is a new server node
    new_node_info = f'join_request\nnew_node:localhost:{notification_port}:{SERVER_PORT}'  # Replace with appropriate node info
    client.sendall(new_node_info.encode())

    # Receive node information from the leader
    # node_info = client.recv(1024).decode()
    client.close()


def handle_notifications(other_node_socket):
    global like_count
    data = other_node_socket.recv(1024)
    if data:
        decodedData = data.decode();
        if decodedData.startswith("server_info"): # Means that a notification is coming from the leader
            handle_leader_notification(decodedData)
        elif decodedData.startswith("health_check"): # Health check message
	        respond_to_healthcheck(other_node_socket, decodedData)        
        else: # Like event
            _update_likes()
            print(f"Received notification. Liked count: {like_count}")

def respond_to_healthcheck(socket, data):
    print("Received health check from leader")
    global live_clients;
    alive_message = f'alive\nclient_count:{len(live_clients)}'
    socket.sendall(alive_message.encode())
    
def handle_leader_notification(data):
    print(f'Received notification from the leader')
    
    # Parse the node information from the message
    title, nodes_string = data.split('\n', 1)
    nodes = nodes_string.split('\n')
    for node in nodes:
        node_id, ip, port = node.split(':')
        if int(port) != notification_port:
            other_nodes[node_id] = (ip, port)

    print(f'Updated server nodes: {other_nodes}')


def handle_client_thread():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('', SERVER_PORT))
    server.listen(5) # The number 5 here is the max amount of incoming connections (clients)
    print(f"Server listening on port {SERVER_PORT}")

    while True:
        client_socket, client_address = server.accept()
        if not client_address in live_clients:
            live_clients.append(client_address)
        print(f"Connection from {client_address}")
        handle_client(client_socket)


def handle_notifications_thread():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind(('', notification_port))
        server_socket.listen(5)
        print(f"Notification server listening on port {notification_port}")

        while True:
            other_node_socket, other_node_address = server_socket.accept()
            print(f"Notification connection from {other_node_address}")
            handle_notifications(other_node_socket)
            other_node_socket.close() # Not sure if this has to be here...


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Server for handling 'like' requests and notifications")
    SERVER_PORT = int(input("Give a port number for receiving messages from clients:"))
    notification_port = int(input("Give a port number for receiving notifications:"))
    
    notification_thread = threading.Thread(target=handle_notifications_thread, args=())
    notification_thread.start()

    client_thread = threading.Thread(target=handle_client_thread, args=())
    client_thread.start()
    
    connect_to_leader()
    
