import threading
import socket
import argparse
import os

class Server(threading.Thread):
    def __init__(self, host, port):
        super().__init__()
        self.connections = []
        self.host = host
        self.port = port

    def run(self):
        print('Server started')
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((self.host, self.port))

        sock.listen(1)
        print("Listening at", sock.getsockname())

        while True:
            # Accepting new connections
            sc, sockname = sock.accept()
            print('Accepted a new connection from {} to {}'.format(sc.getpeername(), sc.getsockname()))

            # Creating a new thread
            server_socket = ServerSocket(sc, sockname, self)
            server_socket.start()

            # Adding thread to active connections
            self.connections.append(server_socket)
            print('Ready to receive messages from', sc.getpeername())
    
    def broadcast(self, message, source):
        for connection in self.connections:
            if connection.sockname != source:
                connection.send(message)
    
    def remove_connection(self, connection):
        self.connections.remove(connection)

class ServerSocket(threading.Thread):
    def __init__(self, sc, sockname, server):
        super().__init__()
        self.sc = sc
        self.sockname = sockname
        self.server = server
    
    def run(self):
        while True:
            message = self.sc.recv(1024).decode('ascii')
            if message:
                print('{} says {!r}'.format(self.sockname, message))
                self.server.broadcast(message, self.sockname)
            else:
                print('{} has closed the connection'.format(self.sockname))
                self.sc.close()
                self.server.remove_connection(self)
                return
    
    def send(self, message):
        self.sc.sendall(message.encode('ascii'))

def exit(server):
    while True:
        ipt = input('')
        if ipt == 'exit':
            print('Closing all connections...')
            for connection in server.connections:
                connection.sc.close()
            print('Shutting down the server...')
            os._exit(0)

if __name__== '__main__':
    parser = argparse.ArgumentParser(description='Chat Server')
    parser.add_argument('--host', default='127.0.0.1', help='Interface the server listens on (default: 127.0.0.1)')
    parser.add_argument('-p', '--port', metavar='PORT', type=int, default=1060, help='TCP port (default: 1060)')
    args = parser.parse_args()

    server = Server(args.host, args.port)
    server.start()

    exit_thread = threading.Thread(target=exit, args=(server,))
    exit_thread.start()

# Video for refrence 
# https://www.youtube.com/watch?v=MLvBToAhiI4&list=PLWnON6N0wn-FXZ0ECb9iSAZwWoeGr1rUp&index=5
