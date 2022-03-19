import logging


class Logger:
    def __init__(self, level):
        self._logger = logging.getLogger('logger')
        self._logger.setLevel(level.upper())
        logging.basicConfig(format='[%(asctime)s] %(message)s')

    @property
    def logger(self):
        return self._logger
