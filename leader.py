import socket
import threading

LEADER_ADDRESS = ('localhost', 5001)

# Dictionary to store information about other server nodes: {node_id: (ip_address, port)}
list_of_servers = {}
id_count = 0

def handle_new_server(node_socket, notifications_port):
    add_new_node_to_list(notifications_port)
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
      received_data = node_socket.recv(1024).decode()
      if received_data.startswith("join_request"):
          message, ip, receive_port = received_data.split(':')
          threading.Thread(target=handle_new_server, args=(node_socket, receive_port)).start()
      else:
          threading.Thread(target=handle_node, args=(node_socket, receive_port)).start()


def add_new_node_to_list(notifications_port):
    global id_count
    print(f'Adding a new node')
    
    # Should the node id come from the node itself or does the leader decide it?
    id_count += 1
    node_id = id_count

    ip = 'localhost' # Todo: add possibility to configure other addresses
    list_of_servers[node_id] = (ip, int(notifications_port))
    print(f"Added new server: {node_id} - {ip}:{notifications_port}")


if __name__ == "__main__":
    leader_server()
