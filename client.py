import sys
import socket
import argparse
import time

LEADER_ADDRESS = ('svm-11.cs.helsinki.fi', 5001)
SERVER_ADDRESS = None

def push_like_button():
    global SERVER_ADDRESS
    if SERVER_ADDRESS is None:
        SERVER_ADDRESS = get_available_server()
    if SERVER_ADDRESS is not None:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            client.connect((SERVER_ADDRESS))
            # Send a 'like' request to the server
            client.sendall(b'like')
            print("Like button pushed.")
            client.close()            
        except:
            SERVER_ADDRESS = None    
            print("Connection to server lost. Please try again.")
    else:
        print("All servers are busy, please wait a moment.")

# Connects to leader node which returns a server for the client to connect to
def get_available_server():
     data = None
     with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect(LEADER_ADDRESS)
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
        command = input("Enter command ('like' or 'like many' or 'exit'): ")

        if command == 'like':
            push_like_button()
        elif command == 'exit':
            print("Exiting.")
            break
        elif command == 'like many':
            sleep = input("Enter sleep:")
            amount_of_like_events = input("Enter amount of like events:")
            time.sleep(int(sleep))
            for x in range(int(amount_of_like_events)):
                push_like_button()
                time.sleep(0.01)
            print(f'Liked {amount_of_like_events} times')
        else:
            print("Invalid command. Please enter 'like' or 'like many' or 'exit'.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Client for sending 'like' requests")
    parser.add_argument("-d", "--debug", action="store_true")
    args = parser.parse_args()
    if args.debug:
        LEADER_ADDRESS = ('localhost', 5001)        
    print(LEADER_ADDRESS);
    SERVER_ADDRESS = get_available_server()
    print(f'Server address: {SERVER_ADDRESS}')

    main()
