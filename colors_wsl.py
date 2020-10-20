import curses

COLORPAIR_RED_BLACK = 100	# Red and Black, main color scheme
COLORPAIR_LRED_BLACK = 101	# Lighter red and Black, used for ellipses

def initialize_colors():
	curses.init_pair(COLORPAIR_RED_BLACK,curses.COLOR_RED,curses.COLOR_BLACK)
	curses.init_pair(COLORPAIR_LRED_BLACK,9,curses.COLOR_BLACK)
