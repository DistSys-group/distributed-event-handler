import socket

# Define the server address and port of Node 1
NODE1_PORT = 5001  # Port for Node 1

def push_like_button():
    # Connect to Node 1
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('localhost', NODE1_PORT))  # Connect to localhost and Node 1's port
    
    # Send a 'like' request to the server
    client.sendall(b'like')
    print("Like button pushed.")

    client.close()

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
    main()
