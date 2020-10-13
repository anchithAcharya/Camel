import os
import curses
import pad_funcs_wsl as pf
import print_list_wsl as pl
import settings_wsl as settings

def main(stdscr):
	curses.start_color()
	stdscr.clear()

	curses.echo()
	curses.curs_set(0)
	
	y_max,x_max = stdscr.getmaxyx()
	border = (y_max-3,x_max-2, 1,1)

	screen = curses.newwin(*border)
	y_max,x_max = screen.getmaxyx()

	curses.init_pair(100,curses.COLOR_RED,curses.COLOR_BLACK)
	curses.init_pair(101,9,curses.COLOR_BLACK) #TODO: add color pairs to colors_wsl.py
	
	screen.attron(curses.color_pair(100))
	screen.box()
	screen.attroff(curses.color_pair(100))

	screen.addstr(0,5," CML ")
	screen.refresh()

	scrollwin = curses.newwin(y_max-2,1,2,x_max-1)
	scrollwin.leaveok(1)

	pad = curses.newpad(y_max, x_max)
	pad.refresh(0,0, 2,2, y_max-1,x_max-2)

	pf.PAD_YMAX = y_max - 2
	pf.PAD_XMAX = x_max - 5

	pad.keypad(1)
	pad.nodelay(1)
	pad.timeout(300)

	max_YX = (y_max-1,x_max-2)
	my_list = ['..'] + os.listdir()

	def set_scroll():
		if pl.SELECTED_ITEM not in range(pf.SCROLL_POS,pf.SCROLL_POS + pf.PAD_YMAX):
			if pl.SELECTED_ITEM < pf.PAD_YMAX:
				pf.SCROLL_POS = 0
			
			elif pl.SELECTED_ITEM >= (len(my_list) - pf.PAD_YMAX):
				pf.SCROLL_POS = (len(my_list) - pf.PAD_YMAX)
			
			else: pf.SCROLL_POS = pl.SELECTED_ITEM

	while(1):
		pad.erase()
		pl.print_list(pad,scrollwin, max_YX, my_list)

		ch = pad.getch()

		if ch == curses.KEY_UP:
			if pl.SELECTED_ITEM > 0:
				pl.SELECTED_ITEM -= 1

			if pl.SELECTED_ITEM < pf.SCROLL_POS and pf.SCROLL_POS > 0:
					pf.SCROLL_POS -= 1

			set_scroll()
			pl.HSCROLL_DELAY = pl.HSCROLL_INDEX = 0

		elif ch == curses.KEY_DOWN:
			if pl.SELECTED_ITEM < len(my_list) - 1:
				pl.SELECTED_ITEM += 1

				if pl.SELECTED_ITEM > (pf.SCROLL_POS + pf.PAD_YMAX) - 1:
					pf.SCROLL_POS += 1

			set_scroll()
			pl.HSCROLL_DELAY = pl.HSCROLL_INDEX = 0
		
		elif ch == curses.KEY_HOME:
			pl.SELECTED_ITEM = 0
			pf.SCROLL_POS = 0

			pl.HSCROLL_DELAY = pl.HSCROLL_INDEX = 0

		elif ch == curses.KEY_END:
			pl.SELECTED_ITEM = len(my_list) - 1
			pf.SCROLL_POS = pf.MAX_USED_SPACE - pf.PAD_YMAX

			if pf.SCROLL_POS < 0:
				pf.SCROLL_POS = 0

			pl.HSCROLL_DELAY = pl.HSCROLL_INDEX = 0

		#detect ALT + KEY_UP
		elif ch == 564:
			if my_list[0] == '..':
				pl.SELECTED_ITEM = 0
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
			path = my_list[pl.SELECTED_ITEM]
			if os.path.isdir(path):
				this_dir = None

				if path == '..':
					this_dir = os.path.basename(os.getcwd())

				os.chdir(path)

				my_list = os.listdir()
				if os.getcwd() != '/':
					my_list.insert(0, '..')

				if settings.SELECT_PREV_DIR_ON_CD_UP:
					try: pl.SELECTED_ITEM = my_list.index(this_dir)
					except ValueError: pl.SELECTED_ITEM = 0
				
				else: pl.SELECTED_ITEM = 0

				set_scroll()

curses.wrapper(main)
