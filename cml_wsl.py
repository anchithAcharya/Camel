import os
import curses
import pad_funcs_wsl as pf
import print_list_wsl as pl
import settings_wsl as settings
from colors_wsl import COLOR_DICT, init_colors

def main(stdscr):		# TODO: Handle terminal resize events
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

		stdscr.attron(COLOR_DICT['RED_BLACK'])
	
		stdscr.addstr(last_line-1,0, '█' * (x_max-1))
		stdscr.insstr('█')

		stdscr.move(last_line-1,2)

		for key in elements:
			stdscr.addstr(key)

			stdscr.attron(curses.A_REVERSE)
			stdscr.addstr(' ' + elements[key] + '  ')
			stdscr.attroff(curses.A_REVERSE)

		stdscr.attroff(COLOR_DICT['RED_BLACK'])

		stdscr.refresh()

	print_statusbar(('F1','F10'))
	screen = curses.newwin(y_max-3,x_max-2, 1,1)
	y_max,x_max = screen.getmaxyx()

	
	screen.attron(COLOR_DICT["RED_BLACK"])
	screen.box()
	screen.attroff(COLOR_DICT["RED_BLACK"])

	screen.addstr(0,5," CML ")
	screen.refresh()


	scrollwin = curses.newwin(y_max-2,1,2,x_max-1)
	scrollwin.leaveok(1)

	pad = curses.newpad(y_max, x_max)
	pad.refresh(0,0, 2,2, y_max-1,x_max-2)

	pf.PAD_YMAX = y_max - 2
	pf.PAD_XMAX = x_max - 5
	pl.LIST_WIDTH = int(pf.PAD_XMAX / (pl.MAX + len(pl.SEP)))

	pad.keypad(1)
	pad.nodelay(1)
	pad.timeout(300)

	max_YX = (y_max-1,x_max-2)
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
		
		scroll = 0
		keys = pl.convert_to_2d(list(settings.KEYBINDS.keys()),2)
		values = pl.convert_to_2d(list(settings.KEYBINDS.values()),2)

		for x in (4,6):
			keys.insert(x,[''])
			values.insert(x,[''])

		pad.erase()
		scrollwin.erase()

		pad.attron(COLOR_DICT['LRED_BLACK'])
		pad.addstr("Console Media Library")
		pad.attroff(COLOR_DICT['LRED_BLACK'])
		pad.addstr("  v2.1.2 - 2020\n")
		pad.addstr("Developed by Anchith Acharya U. and Adhish N.\n")
		pad.addstr("Github link: ")
		pad.attron(COLOR_DICT['LRED_BLACK'])
		pad.addstr("https://github.com/anchithAcharya/Camel\n\n")
		pad.attroff(COLOR_DICT['LRED_BLACK'])

		pl.print_list(pad,scrollwin, max_YX, keys,values, concat=False)		# TODO: just make this a usual for loop and remove unnecessary modifications to pl.print_list()
		print_statusbar(('^PgUp','^PgDn','F10'), extra={'Esc':"Close help"})

		pad.attron(COLOR_DICT['LRED_BLACK'])		# TODO: integrate this into pf.safe_print()
		pad.addstr("Press Esc key to close this menu.\n\n")
		pad.attroff(COLOR_DICT['LRED_BLACK'])
		pad.refresh(scroll,0, 2,2, *max_YX)


		while 1:
			ch = pad.getch()

			if ch == curses.KEY_UP:
				if scroll > 0:
					scroll -= 1
					pad.refresh(scroll,0, 2,2, *max_YX)
			
			elif ch == curses.KEY_DOWN:
				if scroll < (14 - pf.PAD_YMAX):
					scroll += 1
					pad.refresh(scroll,0, 2,2, *max_YX)

			elif ch == curses.KEY_F10:
				curses.ungetch(curses.KEY_F10)
				break

			elif ch == 27:
				break
		
		print_statusbar(('F1','F10'))

	while(1):
		pad.erase()
		pl.print_list(pad,scrollwin, max_YX, my_list)

		ch = pad.getch()

		if ch == curses.KEY_UP:
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

		elif ch == curses.KEY_RIGHT:
			if pl.SELECTED_ITEM[1] < len(my_list[pl.SELECTED_ITEM[0]]) - 1:
				pl.SELECTED_ITEM[1] += 1

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
			if os.path.isdir(path):
				this_dir = None

				if path == '..':
					this_dir = os.path.basename(os.getcwd())

				os.chdir(path)

				my_list = os.listdir()
				if os.getcwd() != '/':
					my_list.insert(0, '..')
					
				my_list = pl.convert_to_2d(my_list)

				if path == '..' and settings.SELECT_PREV_DIR_ON_CD_UP:
					try:
						for x in my_list:
							if this_dir in x:
								pl.SELECTED_ITEM = [my_list.index(x), x.index(this_dir)]
								break

					except ValueError: pl.SELECTED_ITEM = [0,0]
				
				else: pl.SELECTED_ITEM = [0,0]

				set_scroll()

		elif ch == curses.KEY_BACKSPACE: show_help()

		elif ch == curses.KEY_F10: break

os.environ.setdefault('ESCDELAY', '100')
curses.wrapper(main)
