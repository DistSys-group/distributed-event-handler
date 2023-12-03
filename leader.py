import socket
import threading
import sys
import time
from server_class import Server
from server_helper import send_message_to_all_nodes

LEADER_ADDRESS = ('localhost', 5001)
LEADER_PORT = 5001

# Dictionary to store information about other server nodes: {node_id: (ip_address, port)}
list_of_servers = {}
id_count = 0

def handle_new_server(node_socket, server_addr, notification_port, server_port):
    add_new_node_to_list(server_addr, notification_port, server_port)
    inform_other_nodes_about_new_node()
    node_socket.close()


def send_accept_message(server: Server):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #print(f"Connecting to {server.address}:{server.notification_port}")
    message = "server_info\n" + "server accepted\n"+'\n'.join([f"{server.node_id}:{server.address}:{server.client_port}:{server.notification_port}"])
    client_socket.connect((server.address, server.notification_port))
    client_socket.sendall(message.encode())
    client_socket.close()


def send_node_information(node_socket):
    message = "server_info\n" + '\n'.join([f"{node_id}:{address[0]}:{address[1]}"])
    for server in list_of_servers.items():
        node_socket.sendall(message.encode())


def handle_node(node_socket):
    send_node_information(node_socket)   
    node_socket.close()


def health_check():            
    print("Health check");
    global list_of_servers
    message = "health_check\n"    
    # TODO : put "dead" to all nodes and after alive messages make them alive again"
    # Then check periodically the status of the servers, maybe before starting the health check
    send_message_to_all_nodes(message, list_of_servers)


def health_check_timer():
    count = 0
    while True:
        if count > 2:
            health_check()
            count = 0
        count += 1
        time.sleep(5)


def inform_other_nodes_about_new_node():
    # Inform all existing servers about the updated node information
    updated_node_info = "server_info\n" + '\n'.join([f"{server_id}:{server.address}:{server.notification_port}" for server_id, server in list_of_servers.items()])
    send_message_to_all_nodes(updated_node_info, list_of_servers)


def leader_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('', LEADER_PORT))
    server.listen(5)
    print(f"Leader server listening on {LEADER_ADDRESS}")
    
    threading.Thread(target=health_check_timer).start()

    while True:
        node_socket, node_address = server.accept()
        print(f"Connection from {node_address}")
        # Check if it's a new server joining or an existing server communicating
        received_data = str(node_socket.recv(1024).decode())
        if received_data.startswith("join_request"):
            message, ip, receive_port, server_port = received_data.split(':')
            print(f"Join request {ip} {receive_port} {server_port}")
            threading.Thread(target=handle_new_server, args=(node_socket, ip, receive_port, server_port)).start()

        elif received_data.startswith("server_request"):
            threading.Thread(target=send_available_server, args=(node_socket,)).start()
        elif received_data.startswith("alive"):
                parts = received_data.split(':')
                server_id = int(parts[1])
                client_count = int(parts[3])
                list_of_servers[server_id].clients = client_count
                print(f"Server {server_id} is alive ")
                # TODO: Add status to Server object. Check periodically the status of the nodes, if 
                # TODO: aquire lock before 
                list_of_servers[server_id].status = "alive"
        else:
            threading.Thread(target=handle_node, args=(node_socket, receive_port)).start()


def add_new_node_to_list(server_addr, notification_port, server_port):
    global id_count
    print(f'Adding a new node')
    
    # Should the node id come from the node itself or does the leader decide it?
    id_count += 1
    node_id = id_count

    new_server = Server(node_id, server_addr, int(notification_port), int(server_port), "alive")

    global list_of_servers
    list_of_servers[node_id] = new_server
    print(f"Added new server: {node_id} - {server_addr}:{notification_port}")
    #print(list_of_servers[node_id])
    send_accept_message(new_server)

    
def get_available_server():
    min_clients = sys.maxsize
    print(f"min_clients {min_clients}")
    selected = None
    for server_id in list_of_servers:
        if list_of_servers[server_id].clients < min_clients:
            print(f"server {server_id} has {list_of_servers[server_id].clients} clients")
            min_clients = list_of_servers[server_id].clients
            selected = server_id
        else: 
            print(f"Else: server {server_id} has {list_of_servers[server_id].clients} clients")
    return selected    

def send_available_server(client_socket):
    i = get_available_server()

    if i is not None:
        list_of_servers[i].clients = list_of_servers[i].clients + 1
        node_info = f"({list_of_servers[i].address}, {list_of_servers[i].client_port})"
        client_socket.sendall(node_info.encode())
        print("Sent available server to client")
    else:
        client_socket.close()
        print("No servers available")

# todo, a method that determines which servers are available for client

if __name__ == "__main__":
    leader_server()
