import socket
from server_class import Server


def parse_my_id_from_message(data):
  print(f"I am accepted! {data}")
  parts = data.split("\n")
  my_node = parts[2]
  my_id = my_node.split(":")[0]
  return my_id


def send_message_to_all_nodes(message, list_of_servers: [Server]):
  for server_id, server in list_of_servers.items():
        print(f'Notification to address {server.address}')
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print(f"Connecting to {server.address}:{server.notification_port}")
        client_socket.connect((server.address, int(server.notification_port)))
        client_socket.sendall(message.encode())
        client_socket.close()


def send_message_to_leader_node(message, leader_address):
  leader_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  leader_socket.connect(leader_address)
  leader_socket.sendall(message.encode())
  leader_socket.close()


def update_server_list(other_nodes, data, my_notification_port):
  title, nodes_string = data.split('\n', 1)

  nodes = nodes_string.split('\n')
  for node in nodes:
    node_id, ip, port = node.split(':')
    if int(port) != my_notification_port:
        other_nodes[node_id] = Server(node_id, ip, port, None, "alive")
  return other_nodes


def portsAreValid(leader_port, client_port, notifications_port):
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