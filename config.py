from utils.singleton import singleton


@singleton
class Config:
    def __init__(self):
        self._data = None

    def parse(self, path_to_config):
        conf = {}
        with open(path_to_config, 'r') as f:
            for line in f.readlines():
                parts = line.split(' ')
                key = parts[0].strip()
                value = parts[1].strip()
                conf[key] = int(value) if value.isdecimal() else value

        assert(conf)
        self._data = {
            'server': {
                'host': '0.0.0.0',
                'port': 8080,
                'log_level': 'info',
                'process_num': conf['cpu_limit']
            },
            'directory': {
                'document_root': conf['document_root']
            }
        }

        print('Parsed config:\n', self._data)

    @property
    def server(self):
        return self._data['server']

    @property
    def directory(self):
        return self._data['directory']
