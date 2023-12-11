import socket
import threading
import sys
import time
from server_class import Server
from server_helper import send_message_to_all_nodes, send_message_to_one_node, handle_alive_message, handle_consensus_vote

LEADER_ADDRESS = ('', 5001)

# Dictionary to store information about other server nodes: 
# {node_id: Server}
# Server: { server_id: int, address: Any, notification_port: int, client_port: int, status: str }
list_of_servers = {}
id_count = 0
prev_consensus = 0

def handle_new_server(node_socket, server_addr, notification_port, server_port):
    add_new_node_to_list(server_addr, notification_port, server_port)
    inform_other_nodes_about_node_updates()
    node_socket.close()


def send_accept_message(server: Server):
    global prev_consensus
    message = "server_info\n" + "server accepted\n"+'\n'.join([f"{server.node_id}:{server.address}:{server.client_port}:{server.notification_port}:{prev_consensus}"])
    address = (server.address, server.notification_port)
    send_message_to_one_node(message, (address))


def health_check():
    print("Health check")
    global list_of_servers
    
    # Put first all servers to dead status
    for node in list_of_servers:
        list_of_servers[node].status = "dead"
    
    message = "health_check\n"    
    responseIds = send_message_to_all_nodes(message, list_of_servers)

    # Remove failed connections immediately.
    for node_id in list_of_servers:
        if node_id not in responseIds:
            remove_dead_node(node_id)

    # Alive-messages are sent with separate connections.
    # Wait 5 seconds and then check the health status.
    time.sleep(5)
    for node in list_of_servers.copy():
        if list_of_servers[node].status == "dead":
          remove_dead_node(node)


def establish_like_consensus():
    print("Creating consensus of like amounts")
    global list_of_servers, prev_consensus

    message = "consensus_request\n"
    send_message_to_all_nodes(message, list_of_servers)

    # Consensus votes are sent with separate connections.
    # Wait 5 seconds and calculate results.
    time.sleep(5)
    max_likes = 0  #Max value of likes is the best estimate we can have of the like value
    for node_id in list_of_servers:
        if max_likes < list_of_servers[node_id].likes:
            max_likes = list_of_servers[node_id].likes

    print("Like amount according to leader: {}".format(max_likes))
    prev_consensus = max_likes
    for node_id in list_of_servers:
        list_of_servers[node_id].likes = max_likes

    # Then we inform nodes about the correct like value
    inform_nodes_about_consensus(max_likes)


def inform_nodes_about_consensus(like_value):
    message = "consensus_declaration\namount_of_likes:{}".format(like_value)
    send_message_to_all_nodes(message, list_of_servers)
    

def consensus_check_timer():
    while True:
        time.sleep(20)  #low value for demonstration purposes
        establish_like_consensus()
        

def remove_dead_node(node_id):
    del list_of_servers[node_id]
    print(f"Node {node_id} is dead. Removed it from the list.")
    inform_other_nodes_about_node_updates()


def health_check_timer():
  while True:  
    time.sleep(20)
    health_check()


def inform_other_nodes_about_node_updates():
    # Inform all existing servers about the updated node information
    updated_node_info = "server_info\n" + '\n'.join([f"{server_id}:{server.address}:{server.notification_port}" for server_id, server in list_of_servers.items()])
    try:
      send_message_to_all_nodes(updated_node_info, list_of_servers)
    except Exception as err:
      print(f"Error occured while sending node info: {err}")


def handle_message(node_socket, node_address):
    global list_of_servers
    received_data = str(node_socket.recv(1024).decode())
    if received_data.startswith("join_request"):
        message, receive_port, server_port = received_data.split(':')
        print(f"Join request {node_address[0]} {receive_port} {server_port}")
        handle_new_server(node_socket, node_address[0], receive_port, server_port)
    elif received_data.startswith("server_request"):
        send_available_server(node_socket)
    elif received_data.startswith("alive"):
        list_of_servers = handle_alive_message(list_of_servers, received_data)
    elif received_data.startswith("consensus_request_response"):
        list_of_servers = handle_consensus_vote(list_of_servers, received_data)

def start_leader_server_thread():
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(LEADER_ADDRESS)
        server.listen(5)
        print(f"Leader server listening on {LEADER_ADDRESS}")
        while True:
            node_socket, node_address = server.accept()
            handle_message(node_socket, node_address)
    except Exception as err:
        print(f"Error in leader thread: {err}")
 
    
def add_new_node_to_list(server_addr, notification_port, server_port):
    global id_count
    global list_of_servers
    print(f'Adding a new node')
    id_count += 1
    node_id = id_count

    new_server = Server(node_id, server_addr, int(notification_port), int(server_port), "alive")
    list_of_servers[node_id] = new_server
    print(f"Added new server: {node_id} - {server_addr}:{notification_port}")
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
    server_id = get_available_server()

    if server_id is not None:
        list_of_servers[server_id].clients = list_of_servers[server_id].clients + 1
        node_info = f"({list_of_servers[server_id].address}, {list_of_servers[server_id].client_port})"
        client_socket.sendall(node_info.encode())
        print("Sent available server to client")
    else:
        client_socket.close()
        print("No servers available")

# todo, a method that determines which servers are available for client

if __name__ == "__main__":
    threading.Thread(target=start_leader_server_thread).start()
    threading.Thread(target=health_check_timer).start()
    threading.Thread(target=consensus_check_timer).start()
