from math import ceil
import socket
import threading
import struct
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
    def threadproc():
        nonlocal shutdown
        host = '127.0.0.1'
        port = 12345
        exit_message = ':exit'

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            def shutdown_func():
                logging.info('Shutting down TCP server')
                send(exit_message)

            shutdown = shutdown_func
            event.set()
            s.bind((host, port))
            s.listen()
            message = None

            while message != exit_message:
                connection, address = s.accept()
                try:
                    message = _receive_data(connection)

                    if message == exit_message:
                        _send_data(connection, 'ok')
                        continue
                    else:
                        response = channel.send_to_client(message)
                        _send_data(connection, response)
                finally:
                    connection.close()


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


def _send_data(socket, message):
    assert isinstance(message, str)
    raw_bytes = message.encode('utf-8')
    length = struct.pack('I', len(raw_bytes))
    buffer = length + raw_bytes
    socket.sendall(buffer)


def _receive_data(socket):
    block_size = 4096
    buffer = socket.recv(4)
    byte_count = struct.unpack('I', buffer)[0]
    nblocks = ceil(byte_count / block_size)
    buffer = b''
    for _ in range(nblocks):
        buffer += socket.recv(block_size)
    return buffer.decode('utf-8')


def send(message):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        host = '127.0.0.1'
        port = 12345

        logging.debug(f'Connecting to {host}:{port}')
        s.connect((host, port))

        logging.debug(f'Sending message {message}')
        _send_data(s, message)

        logging.debug(f'Waiting for response')
        response = _receive_data(s)
        return response
