#!/usr/bin/python
# General - just to a connection then, immediately terminates it. Testing on port 4444


import socket

listr = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# The bellow is to reuse a connection if it doesn't go down with the connection to.
listr.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
listr.bind(("", 4444))
listr.listen(0)
print("\n[+] Waiting for incoming connection.\n")
listr.accept()
print("[+] Got a connection.\n")