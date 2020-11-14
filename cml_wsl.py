import os
import curses
import subprocess
from Pad_wsl import Pad
from List_wsl import List
from Point_wsl import Point
from Window_wsl import Window
import Help_wsl as help_section
import settings_wsl as settings
from Statusbar_wsl import Statusbar
from colors_wsl import COLOR_DICT, init_colors
from settings_wsl import KEYBIND_IN_USE as KEYBINDS

def main(screen):
	# screen = curses.initscr()
	curses.curs_set(0)
	init_colors()

	screen = Window(screen)
	frame = screen.subwin(screen.dim - Point(3,2), Point(1))
	frame.decorate()
	frame.refresh()

	statusbar = Statusbar(screen, COLOR_DICT["RED_BLACK"])
	statusbar.write(('Help', 'Reverse sort order', 'Quit'))

	pad = Pad(Point(settings.MIN_DIMS), frame)

	pad.PAD.keypad(1)
	pad.PAD.nodelay(1)
	pad.PAD.timeout(300)

	dir_list = List(pad, [settings.ROOT])
	pad.list = dir_list

	manage_resize = 0		# 0: static screen    1: screen is being resized, wait    2: handle resize
	screen.handle_resize()

	dir_list.cursor = dir_list.list_1d[1]
	curses.ungetch(KEYBINDS["Open file/directory under cursor"][0][0])


	qs = ""
	qs_timeout = -1
	refresh_screen = False

	def set_scroll():
		nonlocal refresh_screen

		if dir_list.cursor.index.y not in range(pad.scroll_pos, (pad.scroll_pos + pad.dim.y)):
			if dir_list.cursor.index.y < pad.dim.y:
				pad.scroll_pos = 0
		
			elif dir_list.cursor.index.y >= (len(dir_list.LIST) - pad.dim.y):
					pad.scroll_pos = (len(dir_list.LIST) - pad.dim.y)
				
			else: pad.scroll_pos = dir_list.cursor.index.y

		refresh_screen = True

	def change_list(path = dir_list.cursor.name, group_open = False, rev = False):
		if rev:
			dir_list.reshape_list(rev = rev)

			set_scroll()
			return
		
		if group_open: file_type = "multiple"
		else: file_type = dir_list.cursor.type

		if file_type == "folder":
			if path == "..":
				prev_wd = os.path.basename(os.getcwd())

			os.chdir(path)

			dir_list.change_list(os.listdir(), (settings.SHOW_HIDDEN_FILES, settings.SHOW_ONLY_MEDIA_FILES))

			if path == '..' and settings.SELECT_PREV_DIR_ON_CD_UP:
				for file in dir_list.list_1d:
					if file.name == prev_wd:
						dir_list.cursor = file
			
			set_scroll()

		elif file_type == "audio" or file_type == "video" or group_open:
			if group_open:
				path = ""

				for item in (dir_list.selected_items or [dir_list.cursor]):
					path += '"{}" '.format(item.name)
			
			else:
				path = '"{}"'.format(path)

			subprocess.call(settings.MEDIA_PLAYER_PATH + ' ' + path + '  vlc://quit &', shell = True,
							stdout = subprocess.DEVNULL, stderr = subprocess.DEVNULL)

	def equals(ch, action):
		return any(ch in keybind for keybind in KEYBINDS[action])

	while 1:

		if refresh_screen or (manage_resize == 0 and dir_list.cursor.show_ellipsis):
			dir_list.display()
			refresh_screen = False
		
		ch = pad.PAD.getch()

		if ch == curses.KEY_RESIZE:
			manage_resize = 1

		elif equals(ch, "Navigate up"):
			index = dir_list.cursor.index
			up = dir_list.atIndex(index - Point(1,0))

			if up:
				dir_list.cursor = up

				if up.index.y < pad.scroll_pos and pad.scroll_pos > 0:
					pad.scroll_pos -= 1

				set_scroll()

		elif equals(ch, "Navigate down"):
			index = dir_list.cursor.index
			down = dir_list.atIndex(index + Point(1,0))

			if down:
				dir_list.cursor = down

				if down.index.y > (pad.scroll_pos + pad.dim.y) - 1:
					pad.scroll_pos += 1

				set_scroll()
		
		elif equals(ch, "Navigate left"):
			index = dir_list.cursor.index
			left = dir_list.atIndex(index - Point(0,1))

			if left:
				dir_list.cursor = left
				set_scroll()

		elif equals(ch, "Navigate right"):
			index = dir_list.cursor.index
			right = dir_list.atIndex(index + Point(0,1))

			if right:
				dir_list.cursor = right
				set_scroll()

		elif equals(ch, "Navigate to first item"):
			dir_list.cursor = dir_list.list_1d[0]
			pad.scroll_pos = 0

			refresh_screen = True

		elif equals(ch, "Navigate to bottom-most item"):
			if settings.END_SELECTS_LAST_ITEM:
				dir_list.cursor = dir_list.list_1d[-1]
			
			else:
				dir_list.cursor = dir_list.LIST[-1][-1]
			
			set_scroll()

		elif equals(ch, "Move up by one directory"):
			if dir_list.list_1d[0].name == "..":
				dir_list.cursor = dir_list.list_1d[0]
				curses.ungetch(KEYBINDS["Open file/directory under cursor"][0][0])
			
			refresh_screen = True
		
		elif equals(ch, "Scroll up"):
			if pad.scroll_pos > 0:
				pad.scroll_pos -= 1
		
			refresh_screen = True
		
		elif equals(ch, "Scroll down"):
			if pad.scroll_pos < (pad.max_used_space - pad.dim.y):
				pad.scroll_pos += 1
			
			refresh_screen = True

		elif equals(ch, "Page up"):
			pad.scroll_pos = max(pad.scroll_pos - (pad.dim.y - 1), 0)
			refresh_screen = True
		
		elif equals(ch, "Page down"):
			pad.scroll_pos = min(pad.scroll_pos + (pad.dim.y - 1), max(pad.max_used_space - pad.dim.y, 0))
			refresh_screen = True

		elif equals(ch, "Select/deselect item under cursor"):
			if dir_list.cursor not in dir_list.selected_items:
				if dir_list.cursor.name != "..":
					dir_list.selected_items.append(dir_list.cursor)
			
			else:
				dir_list.selected_items.remove(dir_list.cursor)

			refresh_screen = True

		elif equals(ch, "Select all items"):
			if not dir_list.selected_items == dir_list.list_1d[1:]:
				dir_list.selected_items = dir_list.list_1d[1:]
				refresh_screen = True
			
			else: curses.ungetch(KEYBINDS["Deselect all items"][0][0])
		
		elif equals(ch, "Deselect all items"):
			dir_list.selected_items = []
			refresh_screen = True

		elif equals(ch, "Group open all selected items directly"):
			if not (dir_list.selected_items == [] and dir_list.cursor.name == ".."):
				change_list(group_open = True)
		
		elif equals(ch, "Open file/directory under cursor"):
			change_list(dir_list.cursor.name)

		elif equals(ch, "Help"):
			help_section.show_help(pad, screen.statusbar, screen.handle_resize)
			refresh_screen = True

		elif equals(ch, "Reverse sort order"):
			change_list(rev = True)

		elif equals(ch, "Quit"): break

		elif ch > 0 and chr(ch).isalnum():
			qs += chr(ch)

			for file in dir_list.list_1d:
				if file.name.lower().startswith(qs):
					dir_list.cursor = file

					set_scroll()
					break

			qs_timeout = 3

		elif ch == -1:
			if qs_timeout >= 0:
				qs_timeout -= 1

				if qs_timeout == 0:
					qs_timeout = -1
					qs = ""

		if manage_resize == 2:
			screen.handle_resize()

			curses.curs_set(1)
			curses.curs_set(0)

			manage_resize = 0
			refresh_screen = True
		
		if manage_resize != 0: manage_resize = 2

os.environ.setdefault('ESCDELAY', '100')
curses.wrapper(main)