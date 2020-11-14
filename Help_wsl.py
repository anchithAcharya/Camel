import curses
from Point_wsl import Point
from colors_wsl import COLOR_DICT
from keybinds_wsl import KEY_VALUES
from settings_wsl import KEYBIND_IN_USE as KEYBINDS

VERSION_NO = "5.1.0"

def process_list(lyst, seperator):
	lyst = list(lyst)

	for i in (4,9,12,16,18,21,24):
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

section_start = [Point(4,3), Point(4, 3 + (max_key_len[0] + 3 + max_value_len[0]) + 5)]
SCROLL_LIMIT = Point(len(keys[0]) + 5, 91)


def show_help(pad, statusbar, handle_resize):
	scroll = Point(0)

	sections = []
	for i, start in enumerate(section_start):
		sections.append(pad.subpad(Point(len(keys[i]),(max_key_len[i] + 3 + max_value_len[i])), start))

	refresh_screen = True
	manage_resize = 0

	pad.SCROLLBAR.WIN.erase()
	pad.SCROLLBAR.refresh()

	def print_help():
		pad.erase()
		for section in sections: section.erase()

		pad.safe_print("Console Media Library", COLOR_DICT['LRED_BLACK'])
		pad.safe_print("  v" + VERSION_NO +" - 2020\n" + "Developed by Anchith Acharya U. and Adhish N.\n" + "Github link: ")
		pad.safe_print("https://github.com/anchithAcharya/Camel\n\n", COLOR_DICT['LRED_BLACK'])
		
		for i in (0,1):
			for key, action in zip(keys[i], actions[i]):
				sections[i].safe_print(key, COLOR_DICT['LRED_BLACK'])

				if action:
					if action == actions[i][-1]: sections[i].PAD.insstr(' : ' + action)
					else: sections[i].safe_print(' : ' + action)
		
		pad.safe_print("\nPress Esc key to close this menu.\n\n", COLOR_DICT['LRED_BLACK'], curs_pos = Point(sections[0].start.y + sections[0].dim.y,0))

	
	statusbar.write(('Scroll up','Scroll down','Scroll left', 'Scroll right'), extra = [('Esc',"Close help")])

	print_help()

	def equals(ch, action):
		return any(ch in keybind for keybind in KEYBINDS[action])

	while 1:
		if refresh_screen:
			pad.refresh(scroll, refresh_scrollbar = False)
			refresh_screen = False

		ch = pad.PAD.getch()

		if ch == curses.KEY_RESIZE:
			manage_resize = 1
		
		elif equals(ch, "Scroll up"):
			if scroll.y > 0:
				scroll.y -= 1
			
			refresh_screen = True
		
		elif equals(ch, "Scroll down"):
			if scroll.y < (SCROLL_LIMIT.y - (pad.dim.y - 1)):
				scroll.y += 1
			
			refresh_screen = True

		elif equals(ch, "Scroll left"):
			if scroll.x > 0:
				scroll.x = max(scroll.x -2, 0)
			
			refresh_screen = True
		
		elif equals(ch, "Scroll right"):
			if scroll.x < (SCROLL_LIMIT.x - (pad.dim.x - 1)):
				scroll.x = min(scroll.x + 2, (SCROLL_LIMIT.x - (pad.dim.x - 1)))
			
			refresh_screen = True

		elif equals(ch, "Quit"):
			curses.ungetch(curses.KEY_F10)
			break

		elif ch == KEY_VALUES["Esc"]: break
	
		if manage_resize == 2:
			handle_resize()
			# print_statusbar(('^PgUp','^PgDn','F10'), extra={'Esc':"Close help"})

			curses.curs_set(1)
			curses.curs_set(0)

			manage_resize = 0
			refresh_screen = True
		
		if manage_resize != 0: manage_resize = 2

	statusbar.write(('Help', 'Reverse sort order', 'Quit'))