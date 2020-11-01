import os
import curses
import subprocess
import pad_funcs_wsl as pf
import list_funcs_wsl as lf
import settings_wsl as settings
from colors_wsl import COLOR_DICT, init_colors

def main(stdscr):
	curses.start_color()
	init_colors()

	curses.echo()
	curses.curs_set(0)
	
	y_max,x_max = stdscr.getmaxyx()
	stdscr.clear()

	def print_statusbar(keys, extra=None):
		last_line = stdscr.getmaxyx()[0]
		elements = {key: settings.KEYBINDS[key] for key in keys}
		elements.update((extra or {}))

		try:
			stdscr.attron(COLOR_DICT['RED_BLACK'] | curses.A_REVERSE)
	
			stdscr.addstr(last_line-1,0, ' ' * (x_max+1))
			stdscr.insstr(' ')

			stdscr.attroff(curses.A_REVERSE)

			stdscr.move(last_line-1,2)

			for key in elements:
				stdscr.addstr(key)
				pf.safe_print(stdscr, ' ' + elements[key] + '  ', attr = curses.A_REVERSE)

			stdscr.attroff(COLOR_DICT['RED_BLACK'])

			stdscr.refresh()
		except curses.error: pass

	screen = curses.newwin(y_max-3,x_max-2, 1,1)

	scrollwin = curses.newwin(0,0)
	scrollwin.leaveok(1)

	pad = curses.newpad(*settings.MIN_DIMS)
	max_YX = -1

	manage_resize = 0		# 0: static screen    1: screen is being resized, wait    2: handle resize

	def handle_resize():		# BUG: making window height 0 while resizing will disble screen border for some reason
		nonlocal y_max,x_max, max_YX

		y,x = stdscr.getmaxyx()

		if y < 5 or x < 5:
			exit("window size too small")

		screen.resize(y-3, x-2)
		scrollwin.resize(y-5, 1)

		y_max,x_max = screen.getmaxyx()

		screen.erase()
		stdscr.erase()

		print_statusbar(('F1','F4','F10'))

		screen.attron(COLOR_DICT["RED_BLACK"])
		screen.box()
		screen.attroff(COLOR_DICT["RED_BLACK"])

		screen.addstr(0,5," CML ")
		screen.refresh()

		pf.PAD_YMAX = y_max - 2
		pf.PAD_XMAX = x_max - 5

		scrollwin.resize(pf.PAD_YMAX, 1)
		try: scrollwin.mvwin(2, x_max-1)
		except curses.error: pass
		scrollwin.refresh()

		if pad.getmaxyx()[1] <= pf.PAD_XMAX:
			y,x = pad.getmaxyx()
			pad.resize(y, pf.PAD_XMAX + 10)

		max_YX = (y_max-1,x_max-2)
		lf.LIST_WIDTH = max(int(pf.PAD_XMAX / (lf.MAX + len(lf.SEP))),1)
	
	handle_resize()
	pad.refresh(0,0, 2,2, y_max-1,x_max-2)

	pad.keypad(1)
	pad.nodelay(1)
	pad.timeout(300)

	my_list = [[settings.ROOT]]
	item_types = [["folder"]]
	curses.ungetch(10)

	def set_scroll():
		if lf.CURSOR_POS[0] not in range(pf.SCROLL_POS, pf.SCROLL_POS + pf.PAD_YMAX):
			if lf.CURSOR_POS[0] < pf.PAD_YMAX:
				pf.SCROLL_POS = 0
			
			elif lf.CURSOR_POS[0] >= (len(my_list) - pf.PAD_YMAX):
				pf.SCROLL_POS = (len(my_list) - pf.PAD_YMAX)
			
			else: pf.SCROLL_POS = lf.CURSOR_POS[0]

	def show_help():
		nonlocal my_list, manage_resize
		
		VERSION_NO = "4.1.2"
		scroll = 0
		keys = list(settings.KEYBINDS.keys())
		values = list(settings.KEYBINDS.values())

		keys = [keys[:10],keys[10:]]
		values = [values[:10],values[10:]]

		keys = [[(' ' * (len(max(x,key=len)) - len(key)) + key) for key in x] for x in keys]
		values = [[value + (' ' * (len(max(x,key=len)) - len(value))) for value in x] for x in values]

		for i in (4,7,10):
			keys[0].insert(i,'\n')
			values[0].insert(i,'')

		for i in (1,4,7,9):
			keys[1].insert(i,'\n')
			values[1].insert(i,'')

		SCROLL_LIMIT = len(keys[0]) + 5

		scrollwin.erase()
		scrollwin.refresh()

		def print_help():
			pf.safe_print(pad, "Console Media Library", attr = COLOR_DICT['LRED_BLACK'])
			pf.safe_print(pad, "  v" + VERSION_NO +" - 2020\n" + "Developed by Anchith Acharya U. and Adhish N.\n" + "Github link: ")
			pf.safe_print(pad, "https://github.com/anchithAcharya/Camel\n\n", attr = COLOR_DICT['LRED_BLACK'])

			start_x_pos = 3
			start_y_pos = pad.getyx()[0]

			for row_k,row_v in zip(keys,values):
				pad.move(start_y_pos,start_x_pos)
				for key,value in zip(row_k,row_v):
					pf.safe_print(pad, key, attr = COLOR_DICT['LRED_BLACK'], x = start_x_pos)
					if value: pf.safe_print(pad, ' : ' + value + '\n')
					
				start_x_pos += len(max(row_k,key=len)+max(row_v,key=len)) + 3 + 5

			pf.safe_print(pad, "\nPress Esc key to close this menu.\n\n", attr = COLOR_DICT['LRED_BLACK'])
			try: pad.refresh(scroll,0, 2,2, *max_YX)
			except curses.error: pass

		print_statusbar(('^PgUp','^PgDn','F10'), extra={'Esc':"Close help"})

		while 1:
			pad.erase()
			print_help()
			ch = pad.getch()

			if ch == curses.KEY_RESIZE:
				manage_resize = 1
			
			# detect CTRL + PAGE UP
			elif ch == 555:
				if scroll > 0:
					scroll -= 1
					pad.refresh(scroll,0, 2,2, *max_YX)
			
			# detect CTRL + PAGE DOWN
			elif ch == 550:
				if scroll < (SCROLL_LIMIT - (pf.PAD_YMAX - 1)):
					scroll += 1
					pad.refresh(scroll,0, 2,2, *max_YX)

			elif ch == curses.KEY_F10:
				curses.ungetch(curses.KEY_F10)
				break

			elif ch == 27:
				break
		
			if manage_resize == 2:
				handle_resize()
				print_statusbar(('^PgUp','^PgDn','F10'), extra={'Esc':"Close help"})

				curses.curs_set(1)
				curses.curs_set(0)

				manage_resize = 0
			
			if manage_resize != 0: manage_resize = 2

		print_statusbar(('F1','F4','F10'))
		manage_resize = 0
		change_list()

	def change_list(path = '.', rev = False):
		nonlocal my_list, item_types

		if path == '.':
			file_type = "folder"
		
		elif path == "/group$open":
			file_type = "multiple"

		else:
			file_type = item_types[lf.CURSOR_POS[0]][lf.CURSOR_POS[1]]

		if file_type == "folder":
			this_dir = None
			selected_dirs = []

			if path == '.':
				this_dir = my_list[lf.CURSOR_POS[0]][lf.CURSOR_POS[1]]

				for item in lf.SELECTED_ITEMS:
					selected_dirs.append(my_list[item[0]][item[1]])
				
			elif path == '..':
				this_dir = os.path.basename(os.getcwd())
			
			os.chdir(path)
			lf.SELECTED_ITEMS.clear()

			my_list = os.listdir()
			if rev: my_list.reverse()
			my_list, item_types = lf.process_list(my_list, show_hidden_files = settings.SHOW_HIDDEN_FILES, show_only_media_files = settings.SHOW_ONLY_MEDIA_FILES)

			if path == '.' or (path == '..' and settings.SELECT_PREV_DIR_ON_CD_UP):
				try:
					for x in my_list:
						if this_dir in x:
							lf.CURSOR_POS = [my_list.index(x), x.index(this_dir)]
						
					for x in selected_dirs:
						for y in my_list:
							if x in y:
								lf.SELECTED_ITEMS.append((my_list.index(y), y.index(x)))
								break

				except ValueError: lf.CURSOR_POS = [0, 0]
			
			else: lf.CURSOR_POS = [0, 0]

			set_scroll()

		elif file_type == "audio" or file_type == "video" or file_type == "multiple":
			if file_type == "multiple":
				path = ""

				for item in (lf.SELECTED_ITEMS or [tuple(lf.CURSOR_POS)]):
					path += '"{}" '.format(my_list[item[0]][item[1]])
			
			else:
				path = '"{}"'.format(path)

			subprocess.call(settings.MEDIA_PLAYER_PATH + ' ' + path + '  vlc://quit &', shell = True,
							stdout = subprocess.DEVNULL, stderr = subprocess.DEVNULL)

	reverse_list = False

	while 1:
		pad.erase()
		lf.print_list(pad,scrollwin, max_YX, my_list, item_types)

		ch = pad.getch()

		if ch == curses.KEY_RESIZE:
			manage_resize = 1

		elif ch == curses.KEY_UP:
			if lf.CURSOR_POS[0] > 0:
				lf.CURSOR_POS[0] -= 1

				if lf.CURSOR_POS[0] < pf.SCROLL_POS and pf.SCROLL_POS > 0:
					pf.SCROLL_POS -= 1

				lf.HSCROLL_DELAY = lf.HSCROLL_INDEX = 0
			
			set_scroll()

		elif ch == curses.KEY_DOWN:
			if lf.CURSOR_POS[0] < len(my_list) - 1:
				try:
					my_list[lf.CURSOR_POS[0] + 1][lf.CURSOR_POS[1]]
					lf.CURSOR_POS[0] += 1
				except IndexError: pass
			
				if lf.CURSOR_POS[0] > (pf.SCROLL_POS + pf.PAD_YMAX) - 1:
					pf.SCROLL_POS += 1

				lf.HSCROLL_DELAY = lf.HSCROLL_INDEX = 0

			set_scroll()
		
		elif ch == curses.KEY_LEFT:
			if lf.CURSOR_POS[1] > 0:
				lf.CURSOR_POS[1] -= 1

				set_scroll()
				lf.HSCROLL_DELAY = lf.HSCROLL_INDEX = 0

		elif ch == curses.KEY_RIGHT:
			if lf.CURSOR_POS[1] < len(my_list[lf.CURSOR_POS[0]]) - 1:
				lf.CURSOR_POS[1] += 1

				set_scroll()
				lf.HSCROLL_DELAY = lf.HSCROLL_INDEX = 0

		elif ch == curses.KEY_HOME:
			lf.CURSOR_POS = [0, 0]
			pf.SCROLL_POS = 0

			lf.HSCROLL_DELAY = lf.HSCROLL_INDEX = 0

		elif ch == curses.KEY_END:
			lf.CURSOR_POS = [len(my_list) - 1, len(my_list[-1]) - 1]
			pf.SCROLL_POS = pf.MAX_USED_SPACE - pf.PAD_YMAX

			if pf.SCROLL_POS < 0:
				pf.SCROLL_POS = 0

			lf.HSCROLL_DELAY = lf.HSCROLL_INDEX = 0

		# detect ALT + KEY_UP
		elif ch == 564:
			if my_list[0][0] == '..':
				lf.CURSOR_POS = [0, 0]
				curses.ungetch(10)
		
		# detect CTRL + PAGE UP
		elif ch == 555:
			if pf.SCROLL_POS > 0:
				pf.SCROLL_POS -= 1
		
		# detect CTRL + PAGE DOWN
		elif ch == 550:
			if pf.SCROLL_POS < (pf.MAX_USED_SPACE - pf.PAD_YMAX):
				pf.SCROLL_POS += 1

		elif ch == curses.KEY_PPAGE:
			temp = pf.SCROLL_POS - (pf.PAD_YMAX - 1)

			if temp < 0:
				temp = 0
			
			pf.SCROLL_POS = temp
		
		elif ch == curses.KEY_NPAGE:
			temp = pf.SCROLL_POS + (pf.PAD_YMAX - 1)

			if temp > pf.MAX_USED_SPACE - pf.PAD_YMAX:
				temp = pf.MAX_USED_SPACE - pf.PAD_YMAX
				if temp < 0: temp = 0
			
			pf.SCROLL_POS = temp

		elif ch == ord('.'):
			curs_pos = tuple(lf.CURSOR_POS)

			if not curs_pos in lf.SELECTED_ITEMS:
				if my_list[lf.CURSOR_POS[0]][lf.CURSOR_POS[1]] != "..":
					lf.SELECTED_ITEMS.append(curs_pos)
			
			else:
				lf.SELECTED_ITEMS.remove(curs_pos)

		# detect CTRL + A
		elif ch == 1:
			lf.SELECTED_ITEMS.clear()
			
			for row in my_list:
				for item in row:
					lf.SELECTED_ITEMS.append((my_list.index(row),row.index(item)))
			
			del lf.SELECTED_ITEMS[0]
		
		# detect CTRL + D
		elif ch == 4:
			lf.SELECTED_ITEMS.clear()

		# detect CTRL + O
		elif ch == 15:
			if not (lf.SELECTED_ITEMS == [] and lf.CURSOR_POS == [0,0]):
				change_list(path = "/group$open")
		
		elif ch == 10 or ch == ord('o'):
			path = my_list[lf.CURSOR_POS[0]][lf.CURSOR_POS[1]]
			change_list(path)

		elif ch == curses.KEY_BACKSPACE: show_help()	# make it F1 in release version

		elif ch == curses.KEY_F4:
			reverse_list = not reverse_list
			change_list(rev = reverse_list)

		elif ch == curses.KEY_F10: break

		if manage_resize == 2:
			handle_resize()
			change_list()

			curses.curs_set(1)
			curses.curs_set(0)

			manage_resize = 0
		
		if manage_resize != 0: manage_resize = 2


os.environ.setdefault('ESCDELAY', '100')
curses.wrapper(main)
