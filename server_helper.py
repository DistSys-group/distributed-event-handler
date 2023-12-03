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
