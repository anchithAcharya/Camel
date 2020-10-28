import os
import curses
import pad_funcs_wsl as pf
import print_list_wsl as pl
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

	def handle_resize():
		nonlocal y_max,x_max, max_YX

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
			pad.resize(y, pf.PAD_XMAX+10)

		max_YX = (y_max-1,x_max-2)
		pl.LIST_WIDTH = max(int(pf.PAD_XMAX / (pl.MAX + len(pl.SEP))),1)

		if pf.PAD_YMAX < 5 or pf.PAD_XMAX < 5:
			exit("window size too small")
	
	handle_resize()
	pad.refresh(0,0, 2,2, y_max-1,x_max-2)

	pad.keypad(1)
	pad.nodelay(1)
	pad.timeout(300)

	my_list = [[settings.ROOT]]
	curses.ungetch(10)

	def set_scroll():
		if pl.SELECTED_ITEM[0] not in range(pf.SCROLL_POS,pf.SCROLL_POS + pf.PAD_YMAX):
			if pl.SELECTED_ITEM[0] < pf.PAD_YMAX:
				pf.SCROLL_POS = 0
			
			elif pl.SELECTED_ITEM[0] >= (len(my_list) - pf.PAD_YMAX):
				pf.SCROLL_POS = (len(my_list) - pf.PAD_YMAX)
			
			else: pf.SCROLL_POS = pl.SELECTED_ITEM[0]

	def show_help():
		nonlocal my_list
		
		SCROLL_LIMIT = 15
		scroll = 0
		keys = list(settings.KEYBINDS.keys())
		values = list(settings.KEYBINDS.values())

		keys = [keys[:8],keys[8:]]
		values = [values[:8],values[8:]]

		keys = [[(' ' * (len(max(x,key=len)) - len(key)) + key) for key in x] for x in keys]
		values = [[value + (' ' * (len(max(x,key=len)) - len(value))) for value in x] for x in values]

		for i in (4,7):
			keys[0].insert(i,'\n')
			values[0].insert(i,'')

		for i in (1,3,6):
			keys[1].insert(i,'\n')
			values[1].insert(i,'')


		scrollwin.erase()
		scrollwin.refresh()

		def print_help():
			pf.safe_print(pad, "Console Media Library", attr = COLOR_DICT['LRED_BLACK'])
			pf.safe_print(pad, "  v2.1.2 - 2020\n" + "Developed by Anchith Acharya U. and Adhish N.\n" + "Github link: ")
			pf.safe_print(pad, "https://github.com/anchithAcharya/Camel\n\n", attr = COLOR_DICT['LRED_BLACK'])

			start_x_pos = 3
			start_y_pos = pad.getyx()[0]

			for row_k,row_v in zip(keys,values):
				pad.move(start_y_pos,start_x_pos)
				for key,value in zip(row_k,row_v):
					pf.safe_print(pad, key, attr = COLOR_DICT['LRED_BLACK'], x = start_x_pos)
					if value: pf.safe_print(pad, ' : ' + value + '\n')
					
				start_x_pos += len(max(row_k,key=len)+max(row_v,key=len)) + 3 + 8

			pf.safe_print(pad, "\nPress Esc key to close this menu.\n\n", attr = COLOR_DICT['LRED_BLACK'])
			try: pad.refresh(scroll,0, 2,2, *max_YX)
			except curses.error: pass

		print_statusbar(('^PgUp','^PgDn','F10'), extra={'Esc':"Close help"})

		pad.nodelay(0)

		while 1:
			pad.erase()
			print_help()
			ch = pad.getch()

			if ch == curses.KEY_RESIZE:
				y,x = stdscr.getmaxyx()
				screen.resize(y-3, x-2)
				scrollwin.resize(y-5, 1)

				handle_resize()
				print_statusbar(('^PgUp','^PgDn','F10'), extra={'Esc':"Close help"})

				curses.curs_set(1)
				curses.curs_set(0)
			
			elif ch == curses.KEY_UP:
				if scroll > 0:
					scroll -= 1
					pad.refresh(scroll,0, 2,2, *max_YX)
			
			elif ch == curses.KEY_DOWN:
				if scroll < (SCROLL_LIMIT - (pf.PAD_YMAX - 1)):
					scroll += 1
					pad.refresh(scroll,0, 2,2, *max_YX)

			elif ch == curses.KEY_F10:
				curses.ungetch(curses.KEY_F10)
				break

			elif ch == 27:
				break
		
		print_statusbar(('F1','F4','F10'))
		change_list()
		
		pad.nodelay(1)
		pad.timeout(300)

	def change_list(path = '.', rev = False):
		nonlocal my_list

		if os.path.isdir(path):
			this_dir = None

			if path == '.':
				this_dir = my_list[pl.SELECTED_ITEM[0]][pl.SELECTED_ITEM[1]]
				
			elif path == '..':
				this_dir = os.path.basename(os.getcwd())
			
			os.chdir(path)

			my_list = os.listdir()
			if rev: my_list.reverse()
			my_list = pl.process_list(my_list)

			if path == '.' or (path == '..' and settings.SELECT_PREV_DIR_ON_CD_UP):
				try:
					for x in my_list:
						if this_dir in x:
							pl.SELECTED_ITEM = [my_list.index(x), x.index(this_dir)]
							break

				except ValueError: pl.SELECTED_ITEM = [0,0]
			
			else: pl.SELECTED_ITEM = [0,0]

			set_scroll()

	rev = False

	while(1):
		pad.erase()
		pl.print_list(pad,scrollwin, max_YX, my_list)

		ch = pad.getch()

		if ch == curses.KEY_RESIZE:
			y,x = stdscr.getmaxyx()
			screen.resize(y-3, x-2)
			scrollwin.resize(y-5, 1)

			handle_resize()
			change_list()

			curses.curs_set(1)
			curses.curs_set(0)

		elif ch == curses.KEY_UP:
			if pl.SELECTED_ITEM[0] > 0:
				pl.SELECTED_ITEM[0] -= 1

			if pl.SELECTED_ITEM[0] < pf.SCROLL_POS and pf.SCROLL_POS > 0:
					pf.SCROLL_POS -= 1

			set_scroll()
			pl.HSCROLL_DELAY = pl.HSCROLL_INDEX = 0

		elif ch == curses.KEY_DOWN:
			if pl.SELECTED_ITEM[0] < len(my_list) - 1:
				try:
					my_list[pl.SELECTED_ITEM[0]+1][pl.SELECTED_ITEM[1]]
					pl.SELECTED_ITEM[0] += 1
				except IndexError: pass
			
				if pl.SELECTED_ITEM[0] > (pf.SCROLL_POS + pf.PAD_YMAX) - 1:
					pf.SCROLL_POS += 1

			set_scroll()
			pl.HSCROLL_DELAY = pl.HSCROLL_INDEX = 0
		
		elif ch == curses.KEY_LEFT:
			if pl.SELECTED_ITEM[1] > 0:
				pl.SELECTED_ITEM[1] -= 1

				set_scroll()

		elif ch == curses.KEY_RIGHT:
			if pl.SELECTED_ITEM[1] < len(my_list[pl.SELECTED_ITEM[0]]) - 1:
				pl.SELECTED_ITEM[1] += 1

				set_scroll()

		elif ch == curses.KEY_HOME:
			pl.SELECTED_ITEM = [0,0]
			pf.SCROLL_POS = 0

			pl.HSCROLL_DELAY = pl.HSCROLL_INDEX = 0

		elif ch == curses.KEY_END:
			pl.SELECTED_ITEM = [len(my_list)-1,len(my_list[-1])-1]
			pf.SCROLL_POS = pf.MAX_USED_SPACE - pf.PAD_YMAX

			if pf.SCROLL_POS < 0:
				pf.SCROLL_POS = 0

			pl.HSCROLL_DELAY = pl.HSCROLL_INDEX = 0

		#detect ALT + KEY_UP
		elif ch == 564:
			if my_list[0][0] == '..':
				pl.SELECTED_ITEM = [0,0]
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

		elif ch == 10:
			path = my_list[pl.SELECTED_ITEM[0]][pl.SELECTED_ITEM[1]]
			change_list(path)

		elif ch == curses.KEY_BACKSPACE: show_help()

		elif ch == curses.KEY_F4:
			rev = not rev
			change_list(rev = rev)

		elif ch == curses.KEY_F10: break

os.environ.setdefault('ESCDELAY', '100')
curses.wrapper(main)
