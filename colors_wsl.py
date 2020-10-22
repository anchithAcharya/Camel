import curses

COLOR_DICT = {
	"RED_BLACK" : 100,		# Red and Black, main color scheme
	"LRED_BLACK" : 101,		# Lighter red and Black, used for ellipses
}

def init_colors():
	global COLOR_DICT
	
	curses.init_pair(COLOR_DICT["RED_BLACK"],curses.COLOR_RED,curses.COLOR_BLACK)
	curses.init_pair(COLOR_DICT["LRED_BLACK"],9,curses.COLOR_BLACK)

	COLOR_DICT["RED_BLACK"] = curses.color_pair(COLOR_DICT["RED_BLACK"])
	COLOR_DICT["LRED_BLACK"] = curses.color_pair(COLOR_DICT["LRED_BLACK"])
