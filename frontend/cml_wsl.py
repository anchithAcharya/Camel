import os
import curses
import subprocess
from sys import argv

from .misc_wsl import *
from .Pad_wsl import Pad
from .List_wsl import List
from .Point_wsl import Point
from .Window_wsl import Window
from .Statusbar_wsl import Statusbar
from . import settings_wsl as settings
from . import Help_wsl as help_section
from .colors_wsl import COLOR_DICT, init_colors
from .settings_wsl import KEYBIND_IN_USE as KEYBINDS

def main(screen, arg = argv):
	curses.curs_set(0)
	init_colors()

	screen = Window("screen", screen)

	screen.frame = frame = screen.subwin(lambda screen, : (screen.dim - Point(7,2), Point(1)), title = "CML")

	info_panel = InfoPanel(screen, lambda screen : (Point(4,screen.frame.dim.x), screen.frame.start + Point(screen.frame.dim.y, 0)), title = "Details")
	screen.subs.append(info_panel)

	screen.cwdbar = CWDBar(screen)

	statusbar = Statusbar(screen, COLOR_DICT["RED_BLACK"])
	statusbar.write(('Help', 'Reverse sort order', 'Quit'))

	pad = Pad(Point(settings.MIN_DIMS), frame)

	pad.PAD.keypad(1)
	pad.PAD.nodelay(1)
	pad.PAD.timeout(300)

	if len(argv) == 1:
		arg.append(settings.ROOT)
	
	else:
		arg[1] = os.path.abspath(arg[1])
		
		if not os.path.isdir(arg[1]):
			exit(arg[1] + " is not a valid directory.")

	dir_list = List(pad, [arg[1]])
	pad.list = dir_list

	manage_resize = 0		# 0: static screen    1: screen is being resized, wait    2: handle resize
	screen.handle_resize()

	dir_list.cursor = dir_list.list_1d[1]
	curses.ungetch(KEYBINDS["Open file/directory under cursor"][0][0])


	qs = ""
	qs_timeout = -1
	refresh_screen = False
	dirHistory = Stack_pointer()

	def set_scroll():
		nonlocal refresh_screen

		if dir_list.cursor.index.y not in range(pad.scroll_pos, (pad.scroll_pos + pad.dim.y)):
			if dir_list.cursor.index.y < pad.dim.y:
				pad.scroll_pos = 0
		
			elif dir_list.cursor.index.y >= (len(dir_list.LIST) - pad.dim.y):
					pad.scroll_pos = (len(dir_list.LIST) - pad.dim.y)
				
			else: pad.scroll_pos = dir_list.cursor.index.y

		info_panel.show_info(dir_list.cursor)

		refresh_screen = True

	def change_list(path = dir_list.cursor.name, group_open = False, rev = False, add_to_history = True):
		if rev:
			dir_list.reshape_list(rev = rev)

			set_scroll()
			return
		
		if group_open: file_type = "multiple"
		else: file_type = dir_list.cursor.type

		if file_type == "folder":
			this_dir = os.getcwd()

			os.chdir(path)

			if add_to_history:
				dirHistory.append(os.getcwd())

			dir_list.change_list(os.listdir(), (settings.SHOW_HIDDEN_FILES, settings.SHOW_ONLY_MEDIA_FILES))

			if path == '..' and settings.SELECT_PREV_DIR_ON_CD_UP:
				this_dir = os.path.basename(this_dir)
				
				for file in dir_list.list_1d:
					if file.name == this_dir:
						dir_list.cursor = file
			
			screen.cwdbar.print_cwd()
			statusbar.update_count(dir_list.selected_items)
			
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
		
		elif equals(ch, "Back"):
			path = dirHistory.up()

			if path:
				change_list(path, add_to_history = False)
		
		elif equals(ch, "Forward"):
			path = dirHistory.down()

			if path:
				change_list(path, add_to_history = False)

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

			statusbar.update_count(dir_list.selected_items)

			refresh_screen = True

		elif equals(ch, "Group select"):
			if dir_list.selected_items == []: continue

			last_selected = dir_list.selected_items[-1]

			if dir_list.cursor == last_selected or dir_list.cursor == dir_list.list_1d[0]: continue

			select = False

			for file in dir_list.list_1d[1:]:
				if not select and (file == dir_list.cursor or file == last_selected):
					select = True

					if file not in dir_list.selected_items:
						dir_list.selected_items.append(file)
					
					continue
				
				if select:
					if file not in dir_list.selected_items:
						dir_list.selected_items.append(file)
				
					if file == dir_list.cursor or file == last_selected:
						break
			
			statusbar.update_count(dir_list.selected_items)

			refresh_screen = True

		elif equals(ch, "Select all items"):
			if not dir_list.selected_items == dir_list.list_1d[1:]:
				dir_list.selected_items = dir_list.list_1d[1:]
				statusbar.update_count(dir_list.selected_items)

				refresh_screen = True
			
			else: curses.ungetch(KEYBINDS["Deselect all items"][0][0])
		
		elif equals(ch, "Deselect all items"):
			dir_list.selected_items = []

			statusbar.update_count(dir_list.selected_items)
			refresh_screen = True

		elif equals(ch, "Toggle info panel"):
			settings.SHOW_INFO_PANEL = not settings.SHOW_INFO_PANEL
			screen.handle_resize()
			set_scroll()

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