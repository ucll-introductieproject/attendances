import socketserver
import threading
import logging
from contextlib import contextmanager


class UnidirectionalChannel:
    def __init__(self):
        self.__message = None
        self.__message_event = threading.Event()

    def send(self, message):
        self.__message = message
        self.__message_event.set()

    def receive(self):
        self.__message_event.wait()
        self.__message_event.clear()
        return self.__message

    @property
    def message_waiting(self):
        return self.__message_event.is_set()


class Channel:
    def __init__(self):
        self.__client_to_server = UnidirectionalChannel()
        self.__server_to_client = UnidirectionalChannel()

    def send_to_client(self, message):
        self.__server_to_client.send(message)
        return self.__client_to_server.receive()

    @property
    def message_from_server_waiting(self):
        return self.__server_to_client.message_waiting

    def receive_from_server(self):
        return self.__server_to_client.receive()

    def respond_to_server(self, message):
        self.__client_to_server.send(message)


@contextmanager
def server(channel):
    class Handler(socketserver.StreamRequestHandler):
        def handle(self):
            logging.debug('Server has received external message')
            line = self.rfile.readline()
            logging.debug("Server sends message to client and waits for response")
            response = channel.send_to_client(line)
            logging.debug('Server received answer from client')
            print(response)

    def threadproc():
        nonlocal shutdown
        host = '127.0.0.1'
        port = 12345

        with socketserver.TCPServer((host, port), Handler) as server:
            def shutdown_func():
                logging.info('Shutting down TCP server')
                server.shutdown()
            shutdown = shutdown_func
            event.set()
            logging.info(f'Started TCP server on {host}:{port}')
            server.serve_forever()

    event = threading.Event()
    shutdown = None
    thread = threading.Thread(target=threadproc)
    thread.daemon = True
    thread.start()
    event.wait()
    try:
        yield
    finally:
        shutdown()

