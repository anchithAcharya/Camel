import curses

SCROLL_POS = 0
MAX_USED_SPACE = -1
PAD_XMAX = -1
PAD_YMAX = -1

def pad_refresh(pad,scrollwin,max_YX,auto_scroll = False):
	global SCROLL_POS

	p = round((SCROLL_POS/(MAX_USED_SPACE - PAD_YMAX)) * PAD_YMAX)
	while p > scrollwin.getmaxyx()[0]-1: p -= 1

	scrollwin.clear()
	scrollwin.insstr(p,0,'█')
	scrollwin.refresh()

	pad.refresh(SCROLL_POS,0, 2,2, *max_YX)

	while auto_scroll and (pad.getyx()[0] >= max_YX[0]-1):
		SCROLL_POS += 1
		pad.refresh(SCROLL_POS,0, 2,2, *max_YX)

def safe_print(pad,str):
	try:
		pad.addstr(str)
	except curses.error:
		y,x = pad.getmaxyx()
		pad.resize(y *2,x)