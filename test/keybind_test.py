import os
import curses

#git push remote HEAD:master

def main(stdscr):
	curses.start_color()

	stdscr.clear()
	curses.noecho()
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

	while(1):
		ch = pad.getch()
		pad.clear()
		pad.addstr(str(ch) + "\t" + chr(ch))
		pad.refresh(0,0,1,1, y_max-1,x_max-2)

if __name__ == "__main__":
	curses.wrapper(main)