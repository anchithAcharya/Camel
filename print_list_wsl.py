import curses
from pad_funcs_wsl import pad_refresh

MAX = 10
SELECTED_ITEM = 0
HSCROLL_INDEX = 0
HSCROLL_DELAY = 0
BLINK_DELAY = 0

def print_list(win,scrollwin, max_YX, prnt_list):
	global HSCROLL_INDEX,HSCROLL_DELAY,BLINK_DELAY

	flag = False
	win.erase()

	for i,line in enumerate(prnt_list):
		if len(line) > MAX:
			if i == SELECTED_ITEM:
				if HSCROLL_INDEX == 0:
					HSCROLL_DELAY += 1

					if HSCROLL_DELAY > 3:
						HSCROLL_DELAY = 0
						HSCROLL_INDEX += 1

				elif HSCROLL_INDEX > len(line) - MAX + 1:
					HSCROLL_DELAY += 1

					if HSCROLL_DELAY > 3:
						HSCROLL_DELAY = HSCROLL_INDEX = 0
				
				else: HSCROLL_INDEX += 1

				line = ' ' + line[HSCROLL_INDEX:][:MAX-2] + ' '
			
			else:
				line = line[:MAX-3]
				flag = True

		if i == SELECTED_ITEM:
			win.attron(curses.A_REVERSE)
			
		win.addstr(line)
		win.attroff(curses.A_REVERSE)

		if flag and BLINK_DELAY == 0:
			win.addstr('...')

			flag = False

		win.addch('\n')
		
	BLINK_DELAY += 1
	BLINK_DELAY %= 3

	win.addch('\n')
	pad_refresh(win,scrollwin, max_YX)
