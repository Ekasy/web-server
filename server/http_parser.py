class Parser:
    def __init__(self):
        self._method = ''
        self._path = ''

    def parse(self, request):
        head = request.decode().splitlines()[0]

        try:
            self._method, self._path, _ = head.split(' ')
        except Exception:
            return
        cgi_params_index = self._path.find('?')
        if cgi_params_index > 0:
            self._path = self._path[:cgi_params_index]

    @property
    def method(self):
        return self._method

    @property
    def path(self):
        return self._path
