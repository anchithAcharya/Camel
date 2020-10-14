import curses
import pad_funcs_wsl as pf

MAX = 15
SELECTED_ITEM = 0
HSCROLL_INDEX = 0
_HSCROLL_DELAY = 0

def print_list(win,scrollwin, max_YX, prnt_list):
	global HSCROLL_INDEX,_HSCROLL_DELAY
	
	flag = False
	win.erase()
	pf.MAX_USED_SPACE = len(prnt_list)

	for i,line in enumerate(prnt_list):
		if len(line) > MAX:
			if i == SELECTED_ITEM:
				if HSCROLL_INDEX == 0:
					_HSCROLL_DELAY += 1

					if _HSCROLL_DELAY > 3:
						_HSCROLL_DELAY = 0
						HSCROLL_INDEX += 1

				elif HSCROLL_INDEX > len(line) - (MAX - 1):
					_HSCROLL_DELAY += 1

					if _HSCROLL_DELAY > 3:
						_HSCROLL_DELAY = HSCROLL_INDEX = 0
				
				else: HSCROLL_INDEX += 1

				line = ' ' + line[HSCROLL_INDEX:][:MAX-2] + ' '
			
			else:
				line = line[:MAX-3]
				flag = True

		if i == SELECTED_ITEM:
			win.attron(curses.A_REVERSE)
			
		pf.safe_print(win,line)
		win.attroff(curses.A_REVERSE)

		if flag:
			win.attron(curses.color_pair(101))
			pf.safe_print(win,'...')
			win.attroff(curses.color_pair(101))

			flag = False

		pf.safe_print(win,'\n')

	pf.safe_print(win,'\n')
	pf.pad_refresh(win,scrollwin, max_YX)
