import socket
import argparse
import time

def push_like_button(SERVER_PORT):
    # Connect to Node 1
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('localhost', SERVER_PORT))  # Connect to localhost and Node's port
    
    # Send a 'like' request to the server
    client.sendall(b'like')
    print("Like button pushed.")

    client.close()

def main(SERVER_PORT):
    while True:
        command = input("Enter command ('like' or 'like many' or 'exit'): ")

        if command == 'like':
            push_like_button(SERVER_PORT)
        elif command == 'exit':
            print("Exiting.")
            break
        elif command == 'like many':
            sleep = input("Enter sleep:")
            amount_of_like_events = input("Enter amount of like events:")
            time.sleep(int(sleep))
            for x in range(int(amount_of_like_events)):
                push_like_button(SERVER_PORT)
                time.sleep(0.01)
            print(f'Liked {amount_of_like_events} times')
        else:
            print("Invalid command. Please enter 'like' or 'like many' or 'exit'.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Client for sending 'like' requests")
    parser.add_argument('port', type=int, help="Port number for the server")
    args = parser.parse_args()

    SERVER_PORT = args.port
    main(SERVER_PORT)
