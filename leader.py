import socket
import threading
import random
import sys

LEADER_ADDRESS = ('localhost', 5001)

# Dictionary to store information about other server nodes: {node_id: (ip_address, port)}
list_of_servers = {}
id_count = 0
available_servers = {}
number_of_clients = {}

def handle_new_server(node_socket, notifications_port, own_port):
    add_new_node_to_list(notifications_port, own_port)
    inform_other_nodes()
    node_socket.close()


def send_node_information(node_socket):
    node_info = "server_info\n" + '\n'.join([f"{node_id}:{address[0]}:{address[1]}" for node_id, address in list_of_servers.items()])
    node_socket.sendall(node_info.encode())


def handle_node(node_socket):
    send_node_information(node_socket)
    node_socket.close()


def inform_other_nodes():
    # Inform all existing servers about the updated node information
    updated_node_info = "server_info\n" + '\n'.join([f"{node_id}:{address[0]}:{address[1]}" for node_id, address in list_of_servers.items()])
    
    for node_id, address in list_of_servers.items():
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ADDRESS = ('localhost', address[1])
        client_socket.connect(ADDRESS)
        client_socket.sendall(updated_node_info.encode())
        client_socket.close()


def leader_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(LEADER_ADDRESS)
    server.listen(5)
    print(f"Leader server listening on {LEADER_ADDRESS}")

    while True:
        node_socket, node_address = server.accept()
        print(f"Connection from {node_address}")
        # Check if it's a new server joining or an existing server communicating
        received_data = str(node_socket.recv(1024).decode())
        if received_data.startswith("join_request"):
            message, ip, receive_port, own_port = received_data.split(':')
            threading.Thread(target=handle_new_server, args=(node_socket, receive_port, own_port)).start()

        elif received_data.startswith("server_request"):
            threading.Thread(target=send_available_server, args=(node_socket,)).start()
    
        else:
            threading.Thread(target=handle_node, args=(node_socket, receive_port)).start()


def add_new_node_to_list(notifications_port, own_port):
    global id_count
    print(f'Adding a new node')
    
    # Should the node id come from the node itself or does the leader decide it?
    id_count += 1
    node_id = id_count

    ip = 'localhost' # Todo: add possibility to configure other addresses
    list_of_servers[node_id] = (ip, int(notifications_port))
    available_servers[node_id] = (ip, int(own_port))
    number_of_clients[node_id] = 0;
    print(f"Added new server: {node_id} - {ip}:{notifications_port}")
    
def get_available_server():
    min_clients = sys.maxsize
    selected = None
    for node in number_of_clients:
        if number_of_clients[node] < min_clients:
            min_clients = number_of_clients[node]       
            selected = node
    return selected    

def send_available_server(client_socket):
    i = get_available_server()

    if i is not None:
        number_of_clients[i] += 1
        node_info = str(available_servers[i])
        client_socket.sendall(node_info.encode())
        print("Sent available server to client")
    else:
        client_socket.close()
        print("No servers available")

# todo, a method that determines which servers are available for client

if __name__ == "__main__":
    leader_server()
