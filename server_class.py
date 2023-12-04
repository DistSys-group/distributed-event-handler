class Server:
    def __init__(self, server_id, address, notification_port, client_port, status):
        self.node_id = server_id
        self.address = address
        self.notification_port = notification_port
        self.client_port = client_port        
        self.clients = 0
        self.status = status
        
    def __str__(self):
        return f"{self.node_id} {self.address} {self.client_port} {self.notification_port} {self.status}"
