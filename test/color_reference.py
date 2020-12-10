import os
import curses
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

	pad = curses.newpad(y_max, x_max)
	pad.refresh(0,0, 2,2, y_max-1,x_max-2)

	for i in range(1,256):
		curses.init_pair(i,i,curses.COLOR_BLACK)

	for i in range(256):
		pad.attron(curses.color_pair(i))
		pad.addstr(str(i) + ' ')
		pad.attroff(curses.color_pair(i))


	pad.refresh(0,0,0,0, y_max,x_max)
	pad.getkey()
if __name__ == "__main__":
	curses.wrapper(main)