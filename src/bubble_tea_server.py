import socket
import threading
from bubble_tea_bot import BubbleTeaBot  

host = '0.0.0.0'  # Listen on all available network interfaces
port = 8888  # Same port as in the client code

class BubbleTeaServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server_socket = None
        self.client_socket = None
        self.bot = BubbleTeaBot()  # Initialize the bot

    def start_server(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(1)
        print(f"Server is listening on {self.host}:{self.port}")

        while True:
            self.client_socket, client_address = self.server_socket.accept()
            print(f"Connection established with {client_address}")
            threading.Thread(target=self.handle_client).start()

    def handle_client(self):
        try:
            while True:
                # Receive input from NAO
                data = self.client_socket.recv(1024).decode()
                if not data:
                    break

                print(f"Received from client: {data}")

                # Process input using BubbleTeaBot
                response = self.bot.get_response(data)
                print(f"Bot response: {response}")

                # Send response back to NAO
                self.client_socket.sendall(response.encode())

        except (ConnectionResetError, BrokenPipeError):
            print("Client disconnected.")
        finally:
            self.client_socket.close()

if __name__ == "__main__":
    server = BubbleTeaServer(host, port)
    server.start_server()
