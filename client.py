import socket
import argparse

def push_like_button():
    # Connect to Node 1
    available_server = get_available_server()
    if available_server is not None:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((available_server))  # Connect to localhost and Node's port
    
        # Send a 'like' request to the server
        client.sendall(b'like')
        print("Like button pushed.")

        client.close()
    else:
        print("All servers are busy, please wait a moment.")

# Connects to leader node which returns a server for the client to connect to
def get_available_server():
     data = None
     with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect(('localhost', LEADER_PORT))
        client_socket.sendall(str("server_request").encode())
        data = client_socket.recv(1024)

        if not data:
            return None
        else:
            s = data.decode().replace('(', '').replace(')', '').replace("'", '').split(', ') # a bit funky string for now, becomes much more simpler as we start using non local addresses
            ip = str(s[0])
            port = int(s[1])
            return ip, port

def main():
    while True:
        command = input("Enter command ('like' or 'exit'): ")

        if command == 'like':
            push_like_button()
        elif command == 'exit':
            print("Exiting.")
            break
        else:
            print("Invalid command. Please enter 'like' or 'exit'.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Client for sending 'like' requests")
    LEADER_PORT = 5001

    main()
