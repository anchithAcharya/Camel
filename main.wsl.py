import os
import curses
from curses import wrapper

HISTORY_LIMIT = 20
CMD_HISTORY = []

def main(stdscr):
	stdscr.clear()
	stdscr = curses.initscr()
	stdscr.scrollok(True)

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

def myinput(stdscr,y = None,x = None,prompt = "",ac_list = []):
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
	flag = False

	def nav_cmd_stack(upIfTrue):
		nonlocal inp,i,h_i,temp_history
		temp_history[h_i] = "".join(inp)
				
		stdscr.move(y,x-i)
		stdscr.clrtoeol()
		stdscr.refresh()
		
		if upIfTrue: h_i += 1
		else: h_i -= 1

		inp = list(temp_history[h_i])
		i = len(inp)
		stdscr.addstr(temp_history[h_i])

	def handle_tab():
		nonlocal flag,i,inp

		res = "".join(inp)
		starts_with_res = []

		for line in ac_list:
			if line.startswith(res):
				starts_with_res.append(line)
		
		if len(starts_with_res) == 0:
			return

		#direct match
		if len(starts_with_res) == 1:
			stdscr.move(y,x-i)
			stdscr.clrtoeol()

			stdscr.addstr(starts_with_res[0])
			stdscr.refresh()

			inp.clear()
			inp = list(starts_with_res[0])
			i = len(inp)
			
			return

		else:
			temp_list = []
			idx = len(res)

			while True:
				ch = starts_with_res[0][idx]

				for line in starts_with_res:
					if line[idx] == ch:
						temp_list.append(line)
					
					#match for multiple values
					else:
						if flag:
							if len(starts_with_res) > 5:
								stdscr.addstr(y+2,0,"Show all  "+ str(len(starts_with_res)) + " possibilities?  [y/n]: ")
							while True:
								if len(starts_with_res) > 5:
									key = chr(stdscr.getch())
								else: key = 'y'
									
								stdscr.addch('\n')

								if key == 'y':
									for p in starts_with_res:
										stdscr.addstr(p + "\n")
									
									stdscr.addstr("\n" + prompt + res)
									stdscr.refresh()
									break

								elif key == 'n':
									stdscr.move(y+2,0)
									stdscr.clrtoeol()

									stdscr.move(y,x)
									stdscr.refresh()
									break
						
						flag = not flag
						return

				idx += 1

				#partial match
				if starts_with_res != temp_list:
					stdscr.move(y,x-i)
					stdscr.clrtoeol()

					stdscr.addstr(starts_with_res[0][:idx+1])
					stdscr.refresh()

					inp.clear()
					inp = list(starts_with_res[0][:idx+1])
					i = len(inp)
					
					return

	while 1:
		c = stdscr.getch()
		y,x = curses.getsyx()

		#Tab key
		if c == 9:
			handle_tab()
			continue

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
