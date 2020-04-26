import argparse
import sys
import threading
from socketserver import StreamRequestHandler
from systemd_socketserver import listen_server, listen_servers, listen_servers_with_names


class EchoHandler(StreamRequestHandler):
    def handle(self):
        self.data = self.rfile.readline()
        self.wfile.write(self.data.upper())


class ReversingEchoHandler(StreamRequestHandler):
    def handle(self):
        self.data = self.rfile.readline()[::-1]
        self.wfile.write(self.data.upper())


def basic(args):
    server = listen_server(EchoHandler)

    if server is None:
        print('this example only supports socket activation', file=sys.stderr)
        return

    server.serve_forever()


def multi_fd(args):
    servers = listen_servers(EchoHandler)

    if len(servers) == 0:
        print('this example only supports socket activation', file=sys.stderr)
        return

    for server in servers:
        threading.Thread(name=f'server for fd {server.fileno()}', target=server.serve_forever).start()


def named_fd(args):
    servers = listen_servers_with_names({
        'echo': EchoHandler,
        'reversed': ReversingEchoHandler
    })

    if len(servers) == 0:
        print('this example only supports socket activation', file=sys.stderr)
        return

    for (name, server) in servers:
        threading.Thread(name=f'server for fd {server.fileno()}', target=server.serve_forever).start()


parser = argparse.ArgumentParser('systemd socket activation example')
subparsers = parser.add_subparsers(title='subcommands')

basic_parser = subparsers.add_parser('basic')
basic_parser.set_defaults(func=basic)

multi_fd_parser = subparsers.add_parser('multi-fd')
multi_fd_parser.set_defaults(func=multi_fd)

named_fd_parser = subparsers.add_parser('named-fd')
named_fd_parser.set_defaults(func=named_fd)

args = parser.parse_args()

args.func(args)
