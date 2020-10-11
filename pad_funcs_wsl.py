import curses

SCROLL_POS = 0

def pad_refresh(pad,scrollwin,max_YX,auto_scroll = False):
	global SCROLL_POS

	p = round((SCROLL_POS/(pad.getmaxyx()[0] - (max_YX[0] - 2))) * scrollwin.getmaxyx()[0])
	while p > scrollwin.getmaxyx()[0]-1: p -= 1

	scrollwin.clear()
	scrollwin.insstr(p,0,'█')
	scrollwin.refresh()

	pad.refresh(SCROLL_POS,0, 2,2, *max_YX)

	while auto_scroll and (pad.getyx()[0] >= max_YX[0]-1):
		SCROLL_POS += 1
		pad.refresh(SCROLL_POS,0, 2,2, *max_YX)

