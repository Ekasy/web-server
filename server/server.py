import asyncio
from multiprocessing import Process, cpu_count
import socket

from server.http import Request
from utils.logger import Logger


class Server:
    def __init__(self, config):
        self.host = config['host']
        self.port = config['port']
        self.process_num = Server.__get_process_num(config['process_num'])
        self.logger = Logger(config['log_level']).logger
        self.process_pull = []
        self.server_socket = None

    @staticmethod
    def __get_process_num(process_num):
        return process_num if process_num > 0 else cpu_count()

    def initialize_socket(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        try:
            self.server_socket.bind((self.host, self.port))
        except socket.error as e:
            self.server_socket.close()
            self.logger.info('[Server:initialize_socket] socket not binded')
            raise socket.error(e)

        self.server_socket.listen()
        self.server_socket.setblocking(False)

    def prefork(self):
        for _ in range(self.process_num):
            prc = Process(target=self._start)
            self.process_pull.append(prc)
            prc.start()

    def start(self):
        if not self.server_socket:
            self.initialize_socket()

        if not self.process_pull:
            self.prefork()

        try:
            self.logger.info(f'start server at {self.host}:{self.port}\n\tprocess_num: {self.process_num}')
            for prc in self.process_pull:
                prc.join()
        except KeyboardInterrupt:
            self.logger.info(f'stop server')
            for prc in self.process_pull:
                prc.terminate()
            self.server_socket.close()

    def _start(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._handle_socket())

    async def _handle_socket(self):
        loop = asyncio.get_event_loop()
        while True:
            client_socket, _ = await loop.sock_accept(self.server_socket)
            request = Request(loop, client_socket)
            loop.create_task(request.handle())
