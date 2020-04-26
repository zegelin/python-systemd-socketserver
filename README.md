# systemd-socketserver

_systemd-socketserver_ is a simple Python 3 package that provides the `SystemdSocketServer` class,
a socket server implementation that works in tandem with systemd's socket activation feature.

Very useful for writing basic socket activated daemons.

### Installation

Install from PyPi:

    pip install systemd-socketserver
    
Or clone from Git and install from source:

    setup.py install

### Basic Usage

For a full example see the `example` directory.

The following Python module, when activated via `.socket` unit, will echo the first sent line to the socket
then disconnect.

    class EchoHandler(socketserver.StreamRequestHandler):
        def handle(self):
            self.data = self.rfile.readline()
            self.wfile.write(self.data.upper())
            
    server = systemd_socketserver.listen_server(EchoHandler)
    
    if server is None:
        print('this example only supports socket activation', file=sys.stderr)
        return
        
    server.listen_forever()


### Features:

* Supports and auto detects both listen and accept sockets (`Accept=true|false` in the `.socket` unit)
* Supports named file descriptors, making it easy to bind different handlers to different sockets.

    This feature relies on functionality currently not present in the most recent package release of
    [python-systemd](https://github.com/systemd/python-systemd), namely the `listen_fds_with_names` function.
    Calling `listen_servers_with_names` will throw a `NotImplementedException` in this case.
    
    Building python-systemd from source will include support for `listen_fds_with_names` and hence this feature
    will work.
    
    For an example of this functionality see the code in the `example` directory.


### Known Limitations

* This module has only been tested with INET sockets.
* Better documentation TODO.
