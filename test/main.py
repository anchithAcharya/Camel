import os
import curses
import fnmatch

HISTORY_LIMIT = 20
CMD_HISTORY = []
scroll_pos = 0

def safe_print(win,y=None,x=None,str=str):
	b,a = win.getyx()
	if x is None: x = a
	if y is None: y = b

	q,p = win.getmaxyx()
	if b >= q - 5:
		win.resize(q+20,p)

	win.addstr(y,x,str)

def pad_refresh(win,scrollwin,max_YX,auto_scroll = False):
	global scroll_pos

	p = round((scroll_pos/(win.getmaxyx()[0] - (max_YX[0] - 2))) * scrollwin.getmaxyx()[0])
	while p > scrollwin.getmaxyx()[0]-1: p -= 1

	scrollwin.clear()
	scrollwin.insstr(p,0,'█')
	scrollwin.refresh()

	win.refresh(scroll_pos,0, 2,2, *max_YX)

	while auto_scroll and (curses.getsyx()[0] >= max_YX[0]-1):
		scroll_pos += 1
		win.refresh(scroll_pos,0, 2,2, *max_YX)

def main(stdscr):
	stdscr.clear()
	curses.echo()
	
	y_max,x_max = stdscr.getmaxyx()
	border = (y_max-3,x_max-2, 1,1)

	screen = curses.newwin(*border)
	y_max,x_max = screen.getmaxyx()
	screen.box()
	screen.refresh()

	scrollwin = curses.newwin(y_max-2,1,2,x_max-1)
	scrollwin.leaveok(1)

	pad = curses.newpad(y_max*3, x_max+10)
	pad.refresh(0,0, 2,2, y_max-1,x_max-2)

	def eval_fn(str):
		for it in ('cd','ls'):
			if str.startswith(it + ' '):
				arg = str.replace(it + ' ','')

				ac_list = os.listdir()
				ac_list = fnmatch.filter(ac_list,arg + '*')
				return ac_list or []
		
		return []

	while 1:
		cmd = myinput(pad, max_YX = (y_max-1,x_max-2), scrollwin = scrollwin, prompt = os.getcwd() + ": ")

		if cmd.startswith('ls'):
			if cmd == 'ls':
				path = '.'
			else:
				path = cmd.replace('ls ','')
	
			ls_result = ['.', '..'] + os.listdir(path)

			for item in ls_result:
				safe_print(pad,str = item + '\n')
			
			safe_print(pad, str = '\n')
		
		elif cmd.startswith("cd"):
			path = cmd.split()[1]
			os.chdir(path)

		elif cmd == "exit":
			break

		elif cmd == "":
			pass

		else:
			safe_print(pad, str = "Invalid command: " + cmd + "\n\n")
			screen.refresh()

	pad.refresh(0,0, 2,2, y_max-1,x_max-2)
	pad.getkey()

def myinput(win, y = None,x = None, max_YX = None, scrollwin = None, prompt = "", eval_fn = None):
	global scroll_pos
	win.keypad(1)

	safe_print(win, y,x,prompt)

	inp = []
	i = h_i = 0
	res = ""
	temp_history = [0] + CMD_HISTORY
	flag = False
	ac_list = []

	def nav_cmd_stack(upIfTrue):
		nonlocal inp,i,h_i,temp_history
		temp_history[h_i] = "".join(inp)
				
		win.move(y,x-i)
		win.clrtoeol()
		pad_refresh(win,scrollwin,max_YX)
		
		if upIfTrue: h_i += 1
		else: h_i -= 1

		inp = list(temp_history[h_i])
		i = len(inp)
		safe_print(win, str=temp_history[h_i])

	def handle_tab():
		nonlocal flag,i,inp

		cmd = "".join(inp)
		arg = ""
		for it in ('cd','ls'):
			if cmd.startswith(it + ' '):
				arg = cmd.replace(it + ' ','')

		starts_with_res = []

		if ac_list == []:
			curses.beep()
			return

		for line in ac_list:
			if line.startswith(arg):
				starts_with_res.append(line)
		
		if len(starts_with_res) == 0:
			curses.beep()
			return

		# direct match
		if len(starts_with_res) == 1:
			temp = starts_with_res[0].replace(arg,'',1)

			safe_print(win, str = temp)
			pad_refresh(win,scrollwin,max_YX)

			inp += list(temp)
			i = len(inp)
			
			return

		else:
			temp_list = []
			idx = len(arg)

			while True:
				ch = starts_with_res[0][idx]

				for line in starts_with_res:
					if line[idx] == ch:
						temp_list.append(line)
					
					# match for multiple values
					else:
						if flag:
							if len(starts_with_res) > 5:
								safe_print(win, y+2,0,"Show all  " + str(len(starts_with_res)) + " possibilities?  [y/n]: ")
								pad_refresh(win,scrollwin,max_YX, auto_scroll=True)
							while True:
								if len(starts_with_res) > 5:
									key = chr(win.getch())
								else: key = 'y'
									
								win.addch('\n')

								if key == 'y':
									for p in starts_with_res:
										safe_print(win, str = p + "\n")
										pad_refresh(win,scrollwin,max_YX, auto_scroll=True)
									
									safe_print(win, str="\n" + prompt + "".join(inp))
									pad_refresh(win,scrollwin,max_YX)
									break

								elif key == 'n':
									win.move(y+2,0)
									win.clrtoeol()

									win.move(y,x)
									pad_refresh(win,scrollwin,max_YX)
									break
						
						flag = not flag
						return

				idx += 1

				# partial match
				if starts_with_res != temp_list:
					temp = starts_with_res[0][:idx+1].replace(arg,'',1)

					safe_print(win, str = temp)
					pad_refresh(win,scrollwin,max_YX)

					inp += list(temp)
					i = len(inp)
					
					return

	while 1:
		pad_refresh(win,scrollwin,max_YX)
		c = win.getch()
		y,x = win.getyx()

		#Tab key
		if c == 9:
			handle_tab()

		elif c == curses.KEY_UP:
			if h_i < len(temp_history)-1:
				nav_cmd_stack(True)

		elif c == curses.KEY_DOWN:
			if h_i > 0:
				nav_cmd_stack(False)
				
		elif c == curses.KEY_LEFT:
			if i > 0:
				i -= 1
				win.move(y,x-1)

		elif c == curses.KEY_RIGHT:
			if i < len(inp):
				i += 1
				win.move(y,x+1)

		# DEL key
		elif c == curses.KEY_DC:
			if i < len(inp):
				inp.pop(i)
				win.delch(y,x)

		elif c == curses.KEY_BACKSPACE:
			if i > 0:
				inp.pop(i-1)
				i -= 1

				win.delch(y,x-1)
				win.move(y,x-1)
		
		elif c == curses.KEY_HOME:
			win.move(y,x-i)
			i = 0
		
		elif c == curses.KEY_END:
			win.move(y,(x + len(inp) - i))
			i = len(inp)
		
		elif c == curses.KEY_NPAGE:
			if scroll_pos < (win.getmaxyx()[0] - (max_YX[0] - 2)):
				scroll_pos += 1

		elif c == curses.KEY_PPAGE:
			if scroll_pos > 0:
				scroll_pos -= 1

		# Enter key
		elif c == 10:
			win.move(y+1,0)	
			pad_refresh(win,scrollwin,max_YX, auto_scroll=True)
			break

		elif chr(c).isprintable():
			if i < len(inp):
				win.insch(c)
				win.move(y,x+1)
			else:
				win.addch(c)
			inp.insert(i,chr(c))

			i += 1

		res = "".join(inp)
		if eval_fn != None:
			ac_list = eval_fn(res)

	win.keypad(0)

	if res != "":
		CMD_HISTORY.insert(0,res)
		if len(CMD_HISTORY) > 30: CMD_HISTORY.pop(0)

	return res

if __name__ == "__main__":
	curses.wrapper(main)
	curses.endwin()
