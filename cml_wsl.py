import os
import curses
import print_list_wsl as pl
import pad_funcs_wsl as pf

def main(stdscr):
	curses.start_color()

	stdscr.clear()
	curses.echo()
	curses.curs_set(0)
	
	y_max,x_max = stdscr.getmaxyx()
	border = (y_max-3,x_max-2, 1,1)

	screen = curses.newwin(*border)
	y_max,x_max = screen.getmaxyx()

	curses.init_pair(1,curses.COLOR_RED,curses.COLOR_BLACK)
	
	screen.attron(curses.color_pair(1))
	screen.box()
	screen.attroff(curses.color_pair(1))

	screen.addstr(0,5," CML ")
	screen.refresh()

	scrollwin = curses.newwin(y_max-2,1,2,x_max-1)
	scrollwin.leaveok(1)

	pad = curses.newpad(y_max*10, x_max+10)
	pad.refresh(0,0, 2,2, y_max-1,x_max-2)

	pad.keypad(1)
	pad.nodelay(1)
	pad.timeout(300)

	max_YX = (y_max-1,x_max-2)
	my_list = ['..'] + os.listdir()

	while(1):
		pad.erase()
		pl.print_list(pad,scrollwin, max_YX, my_list)

		ch = pad.getch()
		y,x = pad.getyx()

		if ch == curses.KEY_UP:
			if pl.SELECTED_ITEM > 0: pl.SELECTED_ITEM -= 1
			pl.HSCROLL_DELAY = pl.HSCROLL_INDEX = 0

			if y >= 0:
				if pf.SCROLL_POS > 0:
					pf.SCROLL_POS -= 1

		elif ch == curses.KEY_DOWN:
			if pl.SELECTED_ITEM < len(my_list) - 1:
				if pl.SELECTED_ITEM > max_YX[0] - 3:
					pf.SCROLL_POS += 1

				pl.SELECTED_ITEM += 1

			pl.HSCROLL_DELAY = pl.HSCROLL_INDEX = 0
		
		elif ch == 10:
			path = os.getcwd() + '/' + my_list[pl.SELECTED_ITEM]
			if os.path.isdir(path):
				os.chdir(path)
				my_list = ['..'] + os.listdir()
				pl.SELECTED_ITEM = 0
				pf.SCROLL_POS = 0

curses.wrapper(main)
