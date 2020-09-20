import os
import curses
from curses import wrapper

HISTORY_LIMIT = 20
CMD_HISTORY = []

def main(stdscr):
	stdscr.clear()
	stdscr = curses.initscr()
	curses.curs_set()

	while 1:
		cmd = myinput(stdscr, prompt = os.getcwd() + ": ",ac_list = os.listdir())

		if cmd == "ls":
			print(*os.listdir(), sep = '\n',end = "\n\n")
		
		elif cmd.startswith("cd"):
			path = cmd.split()[1]
			os.chdir(path)

		elif cmd == "exit":
			break

		elif cmd == "":
			pass

		else:
			stdscr.addstr("Invalid command: " + cmd + "\n")
			stdscr.refresh()
	

	stdscr.refresh()
	stdscr.getkey()

def myinput(stdscr,y = None,x = None,prompt = "",ac_list = None):
	b,a = curses.getsyx()

	if x is None: x = a
	if y is None: y = b

	stdscr.addstr(y,x,prompt)

	stdscr.keypad(1)

	c = None
	inp = []
	i = h_i = 0
	res = ""
	temp_history = [0] + CMD_HISTORY

	def nav_cmd_stack(upIfTrue):
		nonlocal inp,i,h_i,x,y,temp_history
		temp_history[h_i] = res.join(inp)
				
		stdscr.move(y,x-i)
		stdscr.clrtoeol()
		stdscr.refresh()
		
		if upIfTrue: h_i += 1
		else: h_i -= 1

		inp = list(temp_history[h_i])
		i = len(inp)
		stdscr.addstr(temp_history[h_i])

	while 1:
		c = stdscr.getch()
		y,x = curses.getsyx()

		#Tab key
		if c == 9:
			pass

		elif c == curses.KEY_UP:
			if h_i < len(temp_history)-1:
				nav_cmd_stack(True)

		elif c == curses.KEY_DOWN:
			if h_i > 0:
				nav_cmd_stack(False)
				
		elif c == curses.KEY_LEFT:
			if i > 0:
				i -= 1
				stdscr.move(y,x-1)

		elif c == curses.KEY_RIGHT:
			if i < len(inp):
				i += 1
				stdscr.move(y,x+1)

		# DEL key
		elif c == curses.KEY_DC:
			if i < len(inp):
				inp.pop(i)
				stdscr.delch(y,x)

		elif c == curses.KEY_BACKSPACE:
			if i > 0:
				inp.pop(i-1)
				i -= 1

				stdscr.delch(y,x-1)
				stdscr.move(y,x-1)
		
		elif c == curses.KEY_HOME:
			stdscr.move(y,x-i)
			i = 0
		
		elif c == curses.KEY_END:
			stdscr.move(y,(x + len(inp) - i))
			i = len(inp)
		
		# Enter key
		elif c == 10:
			stdscr.move(y+1,0)
			stdscr.refresh()
			break

		elif chr(c).isprintable():
			if i < len(inp):
				stdscr.insch(c)
				stdscr.move(y,x+1)
			else:
				stdscr.addch(c)
			inp.insert(i,chr(c))

			i += 1
	
	stdscr.keypad(0)

	res = res.join(inp)

	if res != "":
		CMD_HISTORY.insert(0,res)
		if len(CMD_HISTORY) > 30: CMD_HISTORY.pop(0)

	return res

wrapper(main)