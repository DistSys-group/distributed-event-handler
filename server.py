import sys
import socket
import threading
import argparse
from server_helper import handle_accept_confirmation, send_message_to_all_nodes, send_message_to_one_node, update_server_list, ports_are_valid
from server_class import Server
import time

LEADER_ADDRESS = ('svm-11.cs.helsinki.fi', 5001)
SERVER_PORT = 0
NOTIFICATION_PORT = 0
lock = threading.Lock()
like_count = 0
consensus_client_buffer = 0
consensus_peer_buffer = 0
isBuffering = False
other_nodes = {}
active_clients = []
my_id = 0

notifications_thread_status = "Not connected"
client_thread_status = "Not connected"

def handle_client(client_socket):
    global like_count, isBuffering
    
    while True:
        data = client_socket.recv(1024)
        if not data:
            break
        
        # Process like request
        if isBuffering:
            _increment_buffered_likes('client')
        else:    
            _increment_likes()
            send_notifications(other_nodes)

    client_socket.close()


# Todo: Modify the message to contain more info (timestamp, node_id)
def send_notifications(other_nodes):
    message = "Like event"
    send_message_to_all_nodes(message, other_nodes)


def _increment_likes():
    global like_count
    with lock:
        like_count += 1
        print(f"Received like. Liked count: {like_count}")


def _increment_buffered_likes(buffer):
    global consensus_client_buffer, consensus_peer_buffer
    if buffer == 'client':
        with lock:
            consensus_client_buffer += 1
            print(f"Buffered client like. Buffer count: {consensus_client_buffer}")
    if buffer == 'peer':
        with lock:
            consensus_peer_buffer += 1
            print(f"Buffered peer like. Buffer count: {consensus_peer_buffer}")
        

# Inform the leader that this is a new server node
def connect_to_leader():
    new_node_info = f'join_request\nnew_node:{NOTIFICATION_PORT}:{SERVER_PORT}'  # Replace with appropriate node info
    try:
        send_message_to_one_node(new_node_info, LEADER_ADDRESS)
        print(f"Connected to leader node at {LEADER_ADDRESS}")
    except Exception as err:
        print(f"Could not find or connect to leader node: {err=}, {type(err)=}")
    
    
def handle_notifications(other_node_socket):
    global isBuffering
    data = other_node_socket.recv(1024)
    if data:
        decodedData = data.decode()
        if decodedData.startswith("server_info"): # Means that a notification is coming from the leader
            handle_leader_notification(decodedData)
        elif decodedData.startswith("health_check"): # Health check message
            respond_to_healthcheck()
        elif decodedData.startswith("consensus_request"):
            respond_to_consensus_request()
        elif decodedData.startswith("consensus_declaration"):
            handle_consensus_declaration(decodedData)
        else: # Like event
            if isBuffering:
                _increment_buffered_likes('peer')
            else:
                _increment_likes()


def respond_to_healthcheck():
    print("Received health check from leader")
    global active_clients
    alive_message = f'alive\nmy_node_id:{my_id}:client_count:{len(active_clients)}'
    print(f"Sending health status to leader node at {LEADER_ADDRESS}")
    send_message_to_one_node(alive_message, LEADER_ADDRESS)


def respond_to_consensus_request():
    print("Leader requested like amount")
    global like_count, isBuffering

    # Trigger buffering for new likes while consensus lasts
    isBuffering = True
    print(f"Consensus buffering started")

    like_message = f'consensus_request_response\nmy_node_id:{my_id}:amount_of_likes:{like_count}'
    print(f"Sending current value of likes to leader node at {LEADER_ADDRESS}")
    send_message_to_one_node(like_message, LEADER_ADDRESS)


def handle_buffered_likes():
    global like_count, consensus_client_buffer, consensus_peer_buffer
    buffered_likes_total = consensus_client_buffer + consensus_peer_buffer

    if buffered_likes_total > 0:
        with lock:
            like_count += buffered_likes_total

        print(f"Applied buffered likes: {buffered_likes_total}")
    
        for i in range(consensus_client_buffer):
            send_notifications(other_nodes)

        with lock:
            consensus_client_buffer = 0
            consensus_peer_buffer = 0


def handle_consensus_declaration(data):
    global like_count, my_id, isBuffering
    parts = data.split(":")
    like_value = int(parts[1])
    if like_value:
        with lock:
            like_count = like_value
        print(f"Like value updated at {my_id} to {like_value}")
    
    # Apply likes from consensus buffer
    isBuffering = False
    print(f"Consensus buffering stopped")
    handle_buffered_likes()


def handle_leader_notification(data):
    global my_id, other_nodes, like_count
    print(f'Received notification from the leader')
    if "server accepted" in data:
        my_id, prev_consensus = handle_accept_confirmation(data)
        with lock:
            like_count = int(prev_consensus)
        print(f"My id is {my_id}, likes set to {prev_consensus}")
    else: 
        # Parse the node information from the message
        other_nodes = update_server_list(data, NOTIFICATION_PORT)
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
            if not client_address[0] in active_clients:
                active_clients.append(client_address[0])
            print(f"Connection from {client_address}")
            handle_client(client_socket)
    except Exception as err:
        print(f"Error in the client thread: {err}")


def handle_notifications_thread():
    global notifications_thread_status
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.bind(('', NOTIFICATION_PORT))
            server_socket.listen(5)
            print(f"Notification server listening on port {NOTIFICATION_PORT}")
            notifications_thread_status = "alive"
            while True:
                notification_socket, other_node_address = server_socket.accept()
                print(f"Notification connection from {other_node_address}")
                handle_notifications(notification_socket)
                notification_socket.close() # Not sure if this has to be here...
    except Exception as err:
        print(f"Error in the notifications thread: {err}")


def user_interface():
    global SERVER_PORT, NOTIFICATION_PORT
    SERVER_PORT = int(input("Give a port number for receiving messages from clients:"))
    NOTIFICATION_PORT = int(input("Give a port number for receiving notifications:"))
    try_to_connect()


def try_to_connect():
    if ports_are_valid(LEADER_ADDRESS[1], SERVER_PORT, NOTIFICATION_PORT):
        notification_thread = threading.Thread(target=handle_notifications_thread, args=())
        notification_thread.start()
    
        client_thread = threading.Thread(target=handle_client_thread, args=())
        client_thread.start()
        # Wait that the threads are ready
        print("Waiting for 5 seconds to start the threads")
        time.sleep(5)
        if notifications_thread_status == "alive" and client_thread_status == "alive":
            connect_to_leader()
        else:
            print("Threads did not start. Try giving another ports.")
            user_interface()
    else:
        user_interface()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Server for handling 'like' requests and notifications")
    parser.add_argument("-d", "--debug", action="store_true")
    args = parser.parse_args()
    if args.debug:
        LEADER_ADDRESS = ('localhost', 5001)        
    user_interface()
    
