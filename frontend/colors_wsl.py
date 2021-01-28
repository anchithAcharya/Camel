import curses

COLOR_DICT = {
	# (ID, foreground, <background>)
	"RED_BLACK" : (100, curses.COLOR_RED),		# Red and Black, main color scheme
	"LRED_BLACK" : (101, 9),					# Lighter red and Black, used for ellipses
	"ORANGE_BLACK" : (102, 202),				# Orange and Black, for audio files
	"PURPLE_BLACK" : (103, 90),					# Purple and Black, for video files
	"GRAY_BLACK" : (104, 243),					# Gray and Black, for default prompts
	"GREEN_BLACK" : (105, 76)					# Green and Black, for indicating valid directory in start screen
}

def init_colors():
	global COLOR_DICT

	for color,ID in COLOR_DICT.items():
		if len(ID) == 2:
			ID += (curses.COLOR_BLACK,)

		curses.init_pair(ID[0],ID[1],ID[2])
		COLOR_DICT[color] = curses.color_pair(COLOR_DICT[color][0])
