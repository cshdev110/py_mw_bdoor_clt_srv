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
        # keyboard.add_hotkey('enter', lambda: self.app_k__(self.comm))
        # keyboard.add_hotkey('up', lambda: self.rwl_ku__())
        # keyboard.add_hotkey('down', lambda: self.rwl_kd__())
    
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
        wd_ = ''
        col = 1
        row = 1
        buff_ch = ""
        buff_com = ['']
        hist = ''
        (coley, colex) = cole.getmaxyx()
        nm_hist = []
        cli_w = curses.newwin(coley, colex - 3)
        cli_w.scrollok(True)
        cli_w.idlok(True)
        cli_w.keypad(True)
        while True:
            try:
                
                if cole.getmaxyx()[0] != coley or cole.getmaxyx()[1] != colex:
                    (coley, colex) = self.resize_cli_w(cole, cli_w)
                
                #cli_w.clear()
                
                cli_w.addstr(1, 1, hist)
                cli_w.addstr(row, 1, 'lenHist: ' + str(len(nm_hist)) + " :: " + str(self.addrs) + "$ " + buff_ch)

                cli_w.refresh()

                inp_ch = cli_w.getch()
                cli_w.addstr(0,20,"testing... 2: " + str(inp_ch))
                time.sleep(1)

                if inp_ch == curses.KEY_UP or inp_ch == curses.KEY_DOWN:
                    self.app_k__(cli_w, inp_ch, hist)
                elif inp_ch == curses.KEY_ENTER:
                    # Managing the output history
                    hist += str(self.addrs) + "$ " + buff_ch + "\n"
                    buff_com[:0] = [buff_ch] # buff_com is the history commands, which will be scrolled.
                    
                    if cli_w.getyx()[0] + 1 < cli_w.getmaxyx()[0]:
                        row = cli_w.getyx()[0] + 1

                    cli_w.addstr(0,0,"testing...")
                    buff_ch = ''
                    c_, r_ = 0
                    temp_arr = []
                    print("1")
                    # for x in range(len(hist)):
                    #     print("2")
                    #     if x % (colex - 3) == 0:
                    #         print("3")
                    #         nm_hist.append(temp_arr)
                    #         temp_arr = []
                    #     temp_arr.append(hist[x])
                    # cli_w.refresh()
                    # time.sleep(10.1)
                        

                elif inp_ch == curses.KEY_BACKSPACE:
                    buff_ch = buff_ch[:-1]
                elif inp_ch < 127 and inp_ch > 31:
                    buff_ch = buff_ch + chr(inp_ch)
                else:
                    pass

#                self.comm = input(f"({self.addrs}) $ ").split(" ")
#                # Here, the file is appended to the file.
#                if self.comm[0] == "upload":
#                    self.comm.append(self.r_f(self.comm[1]))
#                result = self.exe_rmy(self.comm)
#                # while is to make sure if there is still connection
#                while result == None:
#                    result = self.exe_rmy(self.comm)
#                if self.comm[0] == "download" and "[Bad command]" not in result:
#                    result = self.w_f(self.comm[1], result.encode())
#                print(f"\n{result}\n")
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
                print("Something went wrong. >>> " + str(excep))
    
    def app_k__(self, cli_w, inp_ch, hist):
        sc_ = 0
        while inp_ch == curses.KEY_UP or inp_ch == curses.KEY_DOWN:
            cli_w.clear()
            if inp_ch == curses.KEY_UP:
                if len(hist) + sc_ > cli_w.getmaxyx()[1]*2:
                    sc_ -= cli_w.getmaxyx()[1]
            elif inp_ch == curses.KEY_DOWN:
                if sc_ < -cli_w.getmaxyx()[1]:
                    sc_ += cli_w.getmaxyx()[1]
            cli_w.addstr(0, 1, hist[0:len(hist) + sc_])
            cli_w.refresh()
            inp_ch = cli_w.getch()
    
    def resize_cli_w(self, cole, cli_w):
        (coley, colex) = cole.getmaxyx()
        cli_w.resize(coley, colex - 3)
        cole.clear()
        cole.refresh()
        return (coley, colex)

            

    # def input_(self, inp_ch, buff_word):
    #     ## subprocess
    #     # read_input = "read -sr -n 1 opt && echo -e $opt"
    #     # print(str(read_input))
    #     # read_input[5] = str(self.addrs)
    #     # print(str(read_input))
    #     # output_ = subprocess.run(read_input, capture_output=True, shell=True)
    #     # print(str(output_))
    #     # print(str(output_.stdout))
    #     # print(str(output_.stdout.decode()))
    #     # return output_.stdout.decode().removesuffix('\n')
    #     if inp_ch == curses.KEY_UP:
    #         pass
    #     elif inp_ch == curses.KEY_DOWN:
    #         pass
    #     elif inp_ch == curses.KEY_ENTER:
    #         pass
    #     elif inp_ch == curses.KEY_BACKSPACE:
    #         return buff_word[:-1]
    #     else:
    #         return buff_word + chr(inp_ch)
    #     ##curses

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
    
    def check_ctls(self, word):
        ctls = {
            'up': '\x1b[A', 
            'down': '\x1b[B', 
            'left': '\x1b[D', 
            'right': '\x1b[C',
            'backspace': '\x7f'
            }
        # print("check_ctls")
        print(str(ctls['up']))
        if ctls['up'] in str(word[0]):
            # print('True: UP')
            return True
        elif ctls['down'] in str(word[0]):
            # print('True: DOWN')
            return True
        elif ctls['left'] in str(word[0]):
            # print('True: LEFT')
            return True
        elif ctls['right'] in str(word[0]):
            # print('True: RIGHT')
            return True
        elif ctls['backspace'] in str(word[0]):
            # print('True: BACKSPACE')
            return True
        else:
            return False

    def testing_p(self, cole, row, col, word):
        cole.addstr(row, col, "row: " + str(row+1) + str(self.addrs) + " >> " + chr(word) + \
                            "h&w cole : " + str(cole.getmaxyx()) + \
                            " Begin Coo: " + str(cole.getparyx()) + \
                            " upperLeftCorner: " + str(cole.getbegyx()) + \
                            " CursorPosition: " + str(cole.getyx()) + \
                            " more text: Lorem ipsum dolor sit amet. " + \
                            " Id unde esse in tempore quae ut velit maxime cum voluptates similique" + \
                            " more text: Lorem ipsum dolor sit amet. " + \
                            " Id unde esse in tempore quae ut velit maxime cum voluptates similique" + \
                            " more text: Lorem ipsum dolor sit amet. " + \
                            " Id unde esse in tempore quae ut velit maxime cum voluptates similique")

        
my_listner = Listr('', 4444)
my_listner.main_curses()