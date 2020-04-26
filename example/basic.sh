#!/usr/bin/env sh

systemd-socket-activate -l 11234 -l 3456 python example.py basic
