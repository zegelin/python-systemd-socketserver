import socket
import socketserver
from typing import Dict, List, NamedTuple, Type

import systemd.daemon

import logging

_logger = logging.getLogger(__name__)


class SystemdSocketServer(socketserver.BaseServer):
    def __init__(self, fd, RequestHandlerClass: Type[socketserver.BaseRequestHandler]):
        self.socket = socket.socket(fileno=fd)

        if not systemd.daemon.is_socket(self.socket):
            raise ConnectionError(f'file descriptor {fd} is not a socket.')

        self.listening = systemd.daemon.is_socket(self.socket, listening=1)

        super().__init__(self.socket.getsockname(), RequestHandlerClass)

    def fileno(self):
        return self.socket.fileno()

    def get_request(self):
        if self.listening:
            return self.socket.accept()
        else:
            # socket has already been accepted by systemd
            return self.socket, self.socket.getpeername()

    def shutdown_request(self, request):
        try:
            request.shutdown(socket.SHUT_WR)
        except OSError:
            pass #some platforms may raise ENOTCONN here

        self.close_request(request)


class TooManyFdsError(Exception):
    def __init__(self, *args):
        super().__init__(*args)


def listen_servers(RequestHandlerClass: Type[socketserver.BaseRequestHandler], limit=-1, unset_environment=True,
                   ServerClass=SystemdSocketServer) -> List[SystemdSocketServer]:
    fds = systemd.daemon.listen_fds(unset_environment)
    if limit > 0:
        if len(fds) > limit:
            raise TooManyFdsError(f'more listen_fds ({len(fds)}) provided than expected ({limit}).')

        fds = fds[:limit]

    return [ServerClass(fd, RequestHandlerClass) for fd in fds]


def listen_server(RequestHandlerClass: Type[socketserver.BaseRequestHandler], **kwargs) -> SystemdSocketServer:
    return next(iter(listen_servers(RequestHandlerClass, limit=1, **kwargs)), None)


class NamedSocketServer(NamedTuple):
    name: str
    server: socketserver.BaseServer


def listen_servers_with_names(named_request_handlers: Dict[str, Type[socketserver.BaseRequestHandler]],
                              unset_environment=True, ServerClass=SystemdSocketServer) -> List[NamedSocketServer]:

    if not "listen_fds_with_names" in dir(systemd.daemon):
        try:
            import pkg_resources
            python_systemd_package_version = pkg_resources.get_distribution("systemd-python").version
        except:
            python_systemd_package_version = "'unknown'"

        raise NotImplementedError(f'listen_fds_with_names is not available in python-systemd version {python_systemd_package_version}.')

    named_fds = systemd.daemon.listen_fds_with_names(unset_environment)

    try:
        return [NamedSocketServer(name, ServerClass(fd, named_request_handlers[name])) for (fd, name) in
                named_fds.items()]

    except KeyError as e:
        raise LookupError(f'no handler found for file descriptor named "{e.args[0]}"')
