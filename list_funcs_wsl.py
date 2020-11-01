import os
import math
import curses
import pad_funcs_wsl as pf
import settings_wsl as settings
from colors_wsl import COLOR_DICT

MAX = 15
CURSOR_POS = [0,0]
SELECTED_ITEMS = []
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

def convert_to_2d(mylist,width=None):
	if not width: width = LIST_WIDTH

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

def process_list(mylist, show_hidden_files = False, show_only_media_files = True):
	if not show_hidden_files:
		mylist = [x for x in mylist if not x.startswith(('.','$'))]
	
	types = []
	to_be_removed = []

	for item in mylist:
		if os.path.isdir(item):
			types.append('folder')

		elif item.endswith(tuple(settings.EXT.audio)):
			types.append('audio')
		
		elif item.endswith(tuple(settings.EXT.video)):
			types.append('video')
		
		elif item.endswith(tuple(settings.EXT.subs)):
			types.append('subs')
		
		else:
			if show_only_media_files:
				to_be_removed.append(item)
			
			else:
				types.append(None)
	
	for value in to_be_removed:
		mylist.remove(value)

	if (os.getcwd() != settings.ROOT) or settings.GO_ABOVE_ROOT:
		mylist.insert(0, '..')
		types.insert(0, 'folder')

	mylist = convert_to_2d(mylist)
	types = convert_to_2d(types)

	return mylist, types

def print_list(win,scrollwin, max_YX, prnt_list, item_types):
	global HSCROLL_INDEX,_HSCROLL_DELAY,LIST_WIDTH
	
	print_ellipsis = False
	win.erase()
	pf.MAX_USED_SPACE = len(prnt_list)

	for x,y,line in enumerate2d(prnt_list):
		if len(line) > MAX:
			if [x,y] == CURSOR_POS or (x,y) in SELECTED_ITEMS:
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


		if item_types[x][y] == "audio":
			attr = COLOR_DICT["ORANGE_BLACK"]
		
		elif item_types[x][y] == "video":
			attr = COLOR_DICT["PURPLE_BLACK"]
		
		elif item_types[x][y] == "subs":
			attr = COLOR_DICT["GRAY_BLACK"]

		else: attr = 0

		if [x,y] == CURSOR_POS:
			attr = COLOR_DICT["RED_BLACK"]

		if (x,y) in SELECTED_ITEMS:
			attr = attr | curses.A_REVERSE
		
		win.attron(attr)

		pf.safe_print(win,line)
		win.attroff(attr)

		if print_ellipsis:
			pf.safe_print(win, '...', attr = COLOR_DICT["LRED_BLACK"])
			print_ellipsis = False

		if y == len(prnt_list[x]) - 1:
			pf.safe_print(win,'\n')
		
		else:
			pf.safe_print(win, SEP)

	pf.safe_print(win, '\n')
	pf.pad_refresh(win,scrollwin, max_YX)