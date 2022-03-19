import argparse

from config import Config
from server.server import Server
from utils.logger import Logger


def argsparser():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, default="httpd.conf")
    return parser.parse_args()


def main():
    args = argsparser()

    conf = Config()
    conf.parse(args.config)

    server = Server(conf.server)
    server.start()


if __name__ == "__main__":
    main()
