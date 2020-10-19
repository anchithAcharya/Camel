import math
import curses
import pad_funcs_wsl as pf

MAX = 15
SELECTED_ITEM = [0,0]
HSCROLL_INDEX = 0
_HSCROLL_DELAY = 0
LIST_WIDTH = 1
SEP = '   '

def enumerate2d(mylist):
	temp = []
	for x, row in enumerate(mylist):
		for y, element in enumerate(row):
			temp += [[x, y, element]]

	return temp

def convert_to_2d(mylist,width):
	x = width
	y = math.ceil(len(mylist)/width)
	ret = [['' for j in range(x)] for i in range(y)]

	count = 0
	for i in range(x):
		for j in range(y):
			ret[j][i] = mylist[count]
			count += 1

			if count >= len(mylist):
				temp = [[c for c in row if c != ''] for row in ret]
				return temp

def print_list(win,scrollwin, max_YX, prnt_list):
	global HSCROLL_INDEX,_HSCROLL_DELAY,LIST_WIDTH
	
	print_ellipsis = False
	win.erase()
	pf.MAX_USED_SPACE = len(prnt_list)

	for x,y,line in enumerate2d(prnt_list):
		if len(line) > MAX:
			if [x,y] == SELECTED_ITEM:
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
				print_ellipsis = True

		else:
			line += ' ' * (MAX - len(line))
			
		if [x,y] == SELECTED_ITEM:
			win.attron(curses.A_REVERSE)

		pf.safe_print(win,line)
		win.attroff(curses.A_REVERSE)

		if print_ellipsis:
			win.attron(curses.color_pair(101))
			pf.safe_print(win,'...')
			win.attroff(curses.color_pair(101))

			print_ellipsis = False

		if y == len(prnt_list[x]) - 1:
			pf.safe_print(win,'\n')
		
		else:
			pf.safe_print(win, SEP)

	pf.safe_print(win, '\n')
	pf.pad_refresh(win,scrollwin, max_YX)
