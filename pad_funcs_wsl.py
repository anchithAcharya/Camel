import curses

SCROLL_POS = 0
MAX_USED_SPACE = -1
PAD_XMAX = -1
PAD_YMAX = -1

def pad_refresh(pad,scrollwin,max_YX,auto_scroll = False):
	global SCROLL_POS

	try:
		p = round((SCROLL_POS/(MAX_USED_SPACE - PAD_YMAX)) * PAD_YMAX)
	except ZeroDivisionError:
		p = 0
		
	if p > scrollwin.getmaxyx()[0] - 1: p = scrollwin.getmaxyx()[0] - 1

	scrollwin.erase()
	scrollwin.insstr(p,0,'█')
	scrollwin.refresh()

	try:
		pad.refresh(SCROLL_POS,0, 2,2, *max_YX)
	
	except curses.error:
		pass

	while auto_scroll and (pad.getyx()[0] >= max_YX[0]-1):
		SCROLL_POS += 1
		pad.refresh(SCROLL_POS,0, 2,2, *max_YX)

def safe_print(pad,str, x = None, y = None, attr = None):
	if y == None: y = pad.getyx()[0]
	if x == None: x = pad.getyx()[1]

	if attr: pad.attron(attr)
	while 1:
		try:
			pad.addstr(y,x, str)
			break
		except curses.error:
			y_max,x_max = pad.getmaxyx()
			pad.resize(y_max*2,x_max)
	if attr: pad.attroff(attr)