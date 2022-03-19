from datetime import datetime
from mimetypes import types_map
import os
from urllib.parse import unquote

from config import Config
from server.http_parser import Parser


REQUEST_BUF_SIZE = 4096
CHUNK_SIZE = 16384

METHOD_GET = 'GET'
METHOD_HEAD = 'HEAD'

STATUS_OK = 200
FORBIDDEN = 403
NOT_FOUND = 404
METHOD_NOT_ALLOWED = 405

INDEX_HTML = 'index.html'


class Request:
    ALLOWED_METHODS = [METHOD_GET, METHOD_HEAD]

    def __init__(self, loop, client_socket):
        self.loop = loop
        self.client_socket = client_socket

    async def handle(self):
        request = b''
        while True:
            buf = (await self.loop.sock_recv(self.client_socket, REQUEST_BUF_SIZE))
            request += buf
            if buf:
                break

        await self._handle(request)
        self.client_socket.close()

    @staticmethod
    def parse(request):
        parser = Parser()
        parser.parse(request)
        return parser.method, parser.path

    @staticmethod
    def parse_path(path):
        """ return path to file and file extension
        """
        path = unquote(path)
        request_to_dir = False
        if path.endswith('/'):  # handle way when path like /<directory>/
            if path.find('.') < 0:
                request_to_dir = True
            path += INDEX_HTML

        path = Config().directory['document_root'] + path

        if path.find('/..') > 0 or path.find('/.') > 0:
            return None, FORBIDDEN

        if request_to_dir and not os.path.exists(path):
            return None, FORBIDDEN
        elif not os.path.exists(path):
            return None, NOT_FOUND

        return {
            'path_to_file': path, 
            'extension': '.{}'.format(path.split(".")[-1]).lower()
        }, STATUS_OK

    async def send_body(self, path_to_file):
        with open(path_to_file, 'rb') as file:
            while True:
                chunk = file.read(CHUNK_SIZE)
                if chunk:
                    await self.loop.sock_sendall(self.client_socket, chunk)
                else:
                    break

    async def _handle(self, request):
        method, path = Request.parse(request)
        if method not in Request.ALLOWED_METHODS:
            resp = Response.make_response(METHOD_NOT_ALLOWED)
            await self.loop.sock_sendall(self.client_socket, resp)
            return

        file, code = Request.parse_path(path)
        if not file:
            resp = Response.make_response(code)
            await self.loop.sock_sendall(self.client_socket, resp)
            return

        resp = Response.make_response(code, content_length=os.path.getsize(file['path_to_file']), content_type=types_map[file['extension']])
        await self.loop.sock_sendall(self.client_socket, resp)
        if method == METHOD_GET:
            try:
                await self.send_body(file['path_to_file'])
            except Exception as e:
                print('[EXCEPTION]', e)


DELIM = '\r\n'


class Response:
    MESSAGE_BY_CODE = {
        STATUS_OK: 'OK',
        FORBIDDEN: 'Forbidden',
        NOT_FOUND: 'Not Found',
        METHOD_NOT_ALLOWED: 'Method Not Allowed',
    }

    def __init__(self):
        pass

    @staticmethod
    def make_response(code, content_length=None, content_type=None):
        head = f'HTTP/1.1 {code} {Response.MESSAGE_BY_CODE[code]}{DELIM}'
        headers = {
            'Server': '[python]:prefork&coroutines',
            'Date': datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
            'Connection': 'close'
        }

        if code == STATUS_OK:
            if content_type:
                headers['Content-Type'] = content_type
            if content_length:
                headers['Content-Length'] = content_length

        raw_headers = ''.join([f'{k}: {v}{DELIM}' for k, v in headers.items()])
        return f'{head}{raw_headers}{DELIM}'.encode()
