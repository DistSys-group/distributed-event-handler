import socket
import threading
import argparse
from server_helper import parse_my_id_from_message, send_message_to_all_nodes, send_message_to_leader_node, update_server_list, portsAreValid
from server_class import Server
import time


lock = threading.Lock()
like_count = 0
LEADER_ADDRESS = ('localhost', 5001)
SERVER_PORT = 0
NOTIFICATION_PORT = 0
other_nodes = {}
live_clients = []
my_id = 0

notifications_thread_status = "dead"
client_thread_status = "dead"

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
    message = "Like event"
    send_message_to_all_nodes(message, other_nodes)


def _update_likes():
    global like_count
    print(f"Received like notification. Liked count: {like_count}")
    with lock:
        like_count += 1


# Inform the leader that this is a new server node
def connect_to_leader():
    new_node_info = f'join_request\nnew_node:localhost:{NOTIFICATION_PORT}:{SERVER_PORT}'  # Replace with appropriate node info
    try:
        send_message_to_leader_node(new_node_info, LEADER_ADDRESS)
        print(f"Connected to leader node at {LEADER_ADDRESS}")
    except Exception as err:
        print(f"Unexpected {err=}, {type(err)=}")
    
    
def handle_notifications(other_node_socket):
    global like_count
    data = other_node_socket.recv(1024)
    if data:
        decodedData = data.decode();
        if decodedData.startswith("server_info"): # Means that a notification is coming from the leader
            handle_leader_notification(decodedData)
        elif decodedData.startswith("health_check"): # Health check message
	        respond_to_healthcheck()        
        else: # Like event
            _update_likes()


def respond_to_healthcheck():
    print("Received health check from leader")
    global live_clients
    alive_message = f'alive\nmy_node_id:{my_id}:client_count:{len(live_clients)}'
    print(f"Sending health status to leader node at {LEADER_ADDRESS}")
    try:
        send_message_to_leader_node(alive_message, LEADER_ADDRESS)
    except Exception as err:
        print(f"Unexpected {err=}, {type(err)=}")
    

def handle_leader_notification(data):
    global my_id
    global other_nodes
    print(f'Received notification from the leader')
    if "server accepted" in data:
        my_id = parse_my_id_from_message(data)
        print(f"My id is {my_id}")
    else: 
        # Parse the node information from the message
        other_nodes = update_server_list(other_nodes, data, NOTIFICATION_PORT)
        print(f'Updated server nodes:')
        for node in other_nodes: 
            print(f"{node}: {str(other_nodes[node])}")


def handle_client_thread():
    global client_thread_status
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(('', SERVER_PORT))
        server.listen(5) # The number 5 here is the max amount of incoming connections (clients)
        print(f"Server listening on port {SERVER_PORT}")
        client_thread_status = "alive"

        while True:
            client_socket, client_address = server.accept()
            # Not working, clients connects from different port each time
            if not client_address in live_clients:
                live_clients.append(client_address)
            print(f"Connection from {client_address}")
            handle_client(client_socket)
    except Exception as err:
        print("Error while creating client thread")


def handle_notifications_thread():
    global notifications_thread_status
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.bind(('', NOTIFICATION_PORT))
            server_socket.listen(5)
            print(f"Notification server listening on port {NOTIFICATION_PORT}")
            notifications_thread_status = "alive"
            while True:
                other_node_socket, other_node_address = server_socket.accept()
                print(f"Notification connection from {other_node_address}")
                handle_notifications(other_node_socket)
                other_node_socket.close() # Not sure if this has to be here...
    except Exception as err:
        print("Error")


def tryToConnect():
    global LEADER_ADDRESS, SERVER_PORT, NOTIFICATION_PORT
    if portsAreValid(LEADER_ADDRESS[1], SERVER_PORT, NOTIFICATION_PORT):
        notification_thread = threading.Thread(target=handle_notifications_thread, args=())
        notification_thread.start()
    
        client_thread = threading.Thread(target=handle_client_thread, args=())
        client_thread.start()
    # Wait that the threads are ready
    time.sleep(5)
    if notifications_thread_status == "alive" and client_thread_status == "alive":
        status = "ok"
        connect_to_leader()
        return status
    else:
        print("Cannot contact the leader before threads are ok")
        SERVER_PORT = int(input("Try again! Give a port number for receiving messages from clients:"))
        NOTIFICATION_PORT = int(input("Try again! Give a port number for receiving notifications:"))
        tryToConnect()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Server for handling 'like' requests and notifications")
    SERVER_PORT = int(input("Give a port number for receiving messages from clients:"))
    NOTIFICATION_PORT = int(input("Give a port number for receiving notifications:"))
    tryToConnect()
    
