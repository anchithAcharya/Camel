import curses
from .Pad_wsl import Pad
from .Point_wsl import Point
from .colors_wsl import COLOR_DICT
from .keybinds_wsl import KEY_VALUES
from .settings_wsl import MIN_DIMS, KEYBIND_IN_USE as KEYBINDS

# VERSION_NO = "7.3.0"
VERSION_NO = "10.0.0"
linebreaks = (4,9,12,15,17, 22,25,28,31,34,38)

def process_list(lyst, seperator):
	lyst = list(lyst)

	for i in linebreaks:
		lyst.insert(i,seperator)
	
	mid = int(len(lyst)/2)
	lyst = [lyst[:mid],lyst[mid:]]

	max_len = []

	for col in lyst:
		max_len.append(len(max(col, key = len)))
	
	return lyst, max_len

keys = [keybind[0][1] for keybind in KEYBINDS.values()]
actions = KEYBINDS.keys()

keys, max_key_len = process_list(keys, '\n')
actions, max_value_len = process_list(actions, '')

keys = [[(' ' * (max_len - len(item)) + item) for item in x] for x,max_len in zip(keys,max_key_len)]
actions = [[(item + ' ' * (max_len - len(item))) if item else '' for item in x] for x,max_len in zip(actions,max_value_len)]

search_filters = {
	"path" : "Original path of the file",
	"ext" : "Extension of the file",
	"in" : "Parent directory of the file",
	"type" : "Type of the file (folder/song/video/movie/show/etc.)",
	"size" : "Size of the file",

	"year" : "Year of release",
	"genre" : "Genre of the media",
	"language" : "Language of the media",
	"length" : "Length of the media",

	"album" : "Album name of the song",
	"artist" : "Artist who created the song",

	"watched" : "Whether the video has been marked as watched (yes/no)",

	"franchise" : "Franchise name of the movie",
	"installment" : "Installment number of the movie",

	"show" : "Name of the TV Show to which the episode belongs",
	"season" : "Season number",
	"episode" : "Episode number"
}

section_start = [Point(10,3), Point(10, 3 + (max_key_len[0] + 3 + max_value_len[0]) + 5)]
SCROLL_LIMIT = Point(3 + 1 + 2 + 2 + 1 + len(keys[0]) + 5 + len(search_filters) + 1 + 1, 91)

def show_help(pad, screen, dont_touch_cwdbar = False):
	statusbar = screen.statusbar

	og_pad = Pad(Point(MIN_DIMS), screen.frame, noScrollBar = True)
	pad, og_pad = og_pad, pad

	pad.PAD.keypad(1)
	pad.PAD.nodelay(1)
	pad.PAD.timeout(300)

	pad.handle_resize()

	scroll = Point(0)

	sections = []
	for i, start in enumerate(section_start):
		sections.append(pad.subpad(Point(len(keys[i]),(max_key_len[i] + 3 + max_value_len[i])), start))

	screen.refresh_screen = True
	screen.manage_resize = 0

	def print_help():
		pad.erase()
		for section in sections: section.erase()

		pad.safe_print("Console Media Library", COLOR_DICT['LRED_BLACK'])
		pad.safe_print("  v" + VERSION_NO +" - 2020\n" + "Developed by Anchith Acharya U. and Adhish N.\n" + "Github link: ")
		pad.safe_print("https://github.com/anchithAcharya/Camel\n\n", COLOR_DICT['LRED_BLACK'])

		pad.safe_print("Color scheme:")

		color_scheme = {
			"cursor": COLOR_DICT["RED_BLACK"],

			"directory": curses.A_NORMAL,
			"audio file": COLOR_DICT["ORANGE_BLACK"],
			"video file": COLOR_DICT["PURPLE_BLACK"]
		}

		for item, color in color_scheme.items():
			pad.safe_print(f"    {item}", attr = color)

		pad.safe_print('\n"Selected" items have their foreground and background colors ')
		pad.safe_print("inverted", attr = curses.A_REVERSE)
		pad.safe_print(".\n\n\n")

		pad.safe_print("List of actions and their keybinds:\n")

		for i in (0,1):
			for key, action in zip(keys[i], actions[i]):
				sections[i].safe_print(key, COLOR_DICT['LRED_BLACK'])

				if action:
					if action == actions[i][-1]: sections[i].PAD.insstr(' : ' + action)
					else: sections[i].safe_print(' : ' + action)

		pad.safe_print("\n\nSearch syntax: ", COLOR_DICT['LRED_BLACK'], curs_pos = Point(pad.PAD.getyx()[0] + len(keys[0]) + 1, 0))
		pad.safe_print("[${filter1: value1} ${filter2: value2} ...] search_term\n\nFilters:\n")

		for filt, desc in search_filters.items():
			pad.safe_print(f"\t{filt}: ", COLOR_DICT['LRED_BLACK'])
			pad.safe_print(desc + "\n")

		pad.safe_print("\nPress Esc key to close this menu.", COLOR_DICT['LRED_BLACK'])

	
	if not dont_touch_cwdbar: screen.cwdbar.hide(True)
	statusbar.write(('Scroll up','Scroll down','Scroll left', 'Scroll right'), extra = [('Esc',"Close help")])

	print_help()

	def equals(ch, action):
		return any(ch in keybind for keybind in KEYBINDS[action])

	while 1:
		if screen.refresh_screen:
			pad.refresh(scroll)
			screen.refresh_screen = False

		ch = pad.PAD.getch()

		if ch == curses.KEY_RESIZE:
			screen.manage_resize = 1
		
		elif equals(ch, "Scroll up"):
			if scroll.y > 0:
				scroll.y -= 1
			
			screen.refresh_screen = True
		
		elif equals(ch, "Scroll down"):
			if scroll.y < (SCROLL_LIMIT.y - (pad.dim.y - 1)):
				scroll.y += 1
			
			screen.refresh_screen = True

		elif equals(ch, "Scroll left"):
			if scroll.x > 0:
				scroll.x = max(scroll.x -2, 0)
			
			screen.refresh_screen = True
		
		elif equals(ch, "Scroll right"):
			if scroll.x < (SCROLL_LIMIT.x - (pad.dim.x - 1)):
				scroll.x = min(scroll.x + 2, (SCROLL_LIMIT.x - (pad.dim.x - 1)))
			
			screen.refresh_screen = True

		elif equals(ch, "Quit"):
			curses.ungetch(curses.KEY_F10)
			break

		elif ch == KEY_VALUES["Esc"]: break
	
		screen.refresh_status()

	pad, og_pad = og_pad, pad

	statusbar.write(('Help', 'Toggle info panel', 'Search', 'Quit'))

	if screen.searchbar.search_result and screen.searchbar.search_result[0] is True:
		msg = screen.searchbar.search_result[1]
		statusbar.safe_print(msg, attr = statusbar.attr | curses.A_REVERSE, curs_pos_x = statusbar.dim.x - len(msg) - 1)
		statusbar.refresh()

	if not dont_touch_cwdbar: screen.cwdbar.hide(False)