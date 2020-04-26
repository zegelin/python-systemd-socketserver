#!/usr/bin/env sh

systemd-socket-activate -l 11234 -l 11235 python example.py multi-fd
