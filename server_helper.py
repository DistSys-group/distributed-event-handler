import socket
from server_class import Server


def handle_accept_confirmation(data):
    print(f"I am accepted! {data}")
    parts = data.split("\n")
    my_node = parts[2]
    my_id = my_node.split(":")[0]
    prev_consensus = my_node.split(":")[4]
    return my_id, prev_consensus


def send_message_to_all_nodes(message, list_of_servers: [Server]):
    responses = []
    for node_id, server in list_of_servers.items():
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            print(f"Connecting to {server.address}:{server.notification_port}")
            client_socket.connect((server.address, int(server.notification_port)))
            client_socket.sendall(message.encode())
            client_socket.close()
            responses.append(node_id)
        except Exception as err:
            print(f"Error connection to node {node_id}")
    return responses


def send_message_to_one_node(message, address):
    try:
        node_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        node_socket.connect(address)
        node_socket.sendall(message.encode())
        node_socket.close()
    except Exception as err:
        print(f"Unexpected {err=}, {type(err)=}")


def update_server_list(data, my_notification_port):
    server_list = {}
    title, nodes_string = data.split('\n', 1)

    nodes = nodes_string.split('\n')
    for node in nodes:
        node_id, ip, port = node.split(':')
        if int(port) != my_notification_port:
            server_list[node_id] = Server(node_id, ip, port, None, "alive")
    return server_list


def ports_are_valid(leader_port, client_port, notifications_port):
    print(f"leader: {leader_port}, client: {client_port}, notification: {notifications_port}")
    if client_port == leader_port or notifications_port == leader_port:
        print(f"Leader in port {leader_port}. Pick another port")
        return False
    elif client_port == notifications_port:
        print(f"Client and notification ports have to be unique. Client: {client_port} Notifications: {notifications_port} ")
        return False
    else:
        print(f"Ports {client_port} and {notifications_port} are valid")
        return True
   

def handle_alive_message(list_of_servers, data):
    parts = data.split(':')
    server_id = int(parts[1])
    client_count = int(parts[3])
    list_of_servers[server_id].clients = client_count
    print(f"Server {server_id} is alive ")
    list_of_servers[server_id].status = "alive"
    return list_of_servers

def handle_consensus_vote(list_of_servers, data):
    parts = data.split(':')
    server_id = int(parts[1])
    like_count = int(parts[3])
    list_of_servers[server_id].likes = like_count
    print(f"Server {server_id} like count: {like_count} ")
    return list_of_servers
