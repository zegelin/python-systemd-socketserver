#!/usr/bin/env sh

systemd-socket-activate -l 11234 -l 11235 --fdname=echo:reversed python example.py named-fd
