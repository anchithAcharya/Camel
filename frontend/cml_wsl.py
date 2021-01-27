import os
import curses
import subprocess

from .misc_wsl import *
from .Pad_wsl import Pad
from .List_wsl import List
from .Point_wsl import Point
from .Window_wsl import Window
from ..backend.sql import query
from .Search_wsl import SearchBar
from .colors_wsl import COLOR_DICT
from .Statusbar_wsl import Statusbar
from . import settings_wsl as settings
from . import Help_wsl as help_section
from .settings_wsl import KEYBIND_IN_USE as KEYBINDS

def main(screen, root_path, db_path):
	curses.curs_set(0)

	sql = query(db_path)

	screen = Window("screen", screen)

	screen.frame = screen.subwin(lambda screen, : (screen.dim - Point(8,2), Point(1)), title = "File Navigator", main_window = True)

	info_panel = InfoPanel(screen, lambda screen : (Point(5,screen.frame.dim.x), screen.frame.start + Point(screen.frame.dim.y, 0)), title = "Details")
	screen.subs.append(info_panel)

	screen.cwdbar = CWDBar(screen, root_path)
	screen.searchbar = SearchBar(screen, sql)

	statusbar = Statusbar(screen, COLOR_DICT["RED_BLACK"], bg_attr = COLOR_DICT["RED_BLACK"] | curses.A_REVERSE)
	statusbar.write(('Help', 'Toggle info panel', 'Search', 'Quit'))

	pad = Pad(Point(settings.MIN_DIMS), screen.frame)

	pad.PAD.keypad(1)
	pad.PAD.nodelay(1)
	pad.PAD.timeout(300)

	dir_list = List(pad, root_path, sql, [])
	pad.list = dir_list

	screen.handle_resize()

	qs = ""
	qs_timeout = -1
	dirHistory = Stack()

	def set_scroll():
		nonlocal screen

		if dir_list.cursor.index.y not in range(pad.scroll_pos, (pad.scroll_pos + pad.dim.y)):
			if dir_list.cursor.index.y < pad.dim.y:
				pad.scroll_pos = 0
		
			elif dir_list.cursor.index.y >= (len(dir_list.LIST) - pad.dim.y):
					pad.scroll_pos = (len(dir_list.LIST) - pad.dim.y)
				
			else: pad.scroll_pos = dir_list.cursor.index.y

		info_panel.show_info(dir_list.cursor)

		screen.refresh_screen = True

	def change_list(path = None, group_open = False, rev = False, add_to_history = True):
		if rev:
			dir_list.reshape_list(rev = rev)

			set_scroll()
			return
		
		if not path:
			path = dir_list.cursor.path

		if dir_list.cursor:
			file_type = dir_list.cursor.type

		else:
			file_type = "media_dir"

		if file_type in ("audio", "movie", "tv_show") or group_open:
			if group_open:
				to_open = dir_list.selected_items or [dir_list.cursor]
				to_open = [x.path for x in to_open]
			
			else:
				to_open = [path]
			
			paths = sql.generate_paths(to_open)

			if len(to_open) == 1 and not os.path.isdir(str(to_open[0])):
				cmd = f"(cd {paths[0]} && {settings.MEDIA_PLAYER_PATH} {paths[1]}  vlc://quit &)"

			else:
				cmd = settings.MEDIA_PLAYER_PATH + ' ' + paths + '  vlc://quit &'

			subprocess.call(cmd, shell = True,
							stdout = subprocess.DEVNULL, stderr = subprocess.DEVNULL)

		elif file_type == "media_dir":
			if screen.searchbar.search_result:
				screen.searchbar.in_search_results = False
				screen.searchbar.search_result = None
				screen.frame.title = "File Navigator"
				screen.cwdbar.hide(False)
				statusbar.alt_cache = ""

				screen.handle_resize()

			this_dir = os.getcwd()

			os.chdir(path)

			if add_to_history:
				dirHistory.append(os.getcwd())

			dir_list.change_list([os.path.abspath(x) for x in os.listdir()])

			if path == '..' and settings.SELECT_PREV_DIR_ON_CD_UP:
				this_dir = os.path.basename(this_dir)
				
				for file in dir_list.list_1d:
					if file.name == this_dir:
						dir_list.cursor = file
			
			screen.cwdbar.print_cwd()
			statusbar.update_count(len(dir_list.selected_items))
			
			set_scroll()

	def equals(ch, action):
		return any(ch in keybind for keybind in KEYBINDS[action])

	change_list(root_path, add_to_history = False)

	while 1:

		if screen.refresh_screen or (screen.manage_resize == 0 and dir_list.cursor.show_ellipsis):
			dir_list.display()
			screen.refresh_screen = False
		
		ch = pad.PAD.getch()

		if ch == curses.KEY_RESIZE:
			screen.manage_resize = 1

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

			screen.refresh_screen = True

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
			
			screen.refresh_screen = True
		
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
		
			screen.refresh_screen = True
		
		elif equals(ch, "Scroll down"):
			if pad.scroll_pos < (pad.max_used_space - pad.dim.y):
				pad.scroll_pos += 1
			
			screen.refresh_screen = True

		elif equals(ch, "Page up"):
			pad.scroll_pos = max(pad.scroll_pos - (pad.dim.y - 1), 0)
			screen.refresh_screen = True
		
		elif equals(ch, "Page down"):
			pad.scroll_pos = min(pad.scroll_pos + (pad.dim.y - 1), max(pad.max_used_space - pad.dim.y, 0))
			screen.refresh_screen = True

		elif equals(ch, "Increase marquee length"):
			dir_list.cursor.change_strlen(increase = True)
			dir_list.reshape_list()

			for file in dir_list.list_1d:
				file.set_disp_str(file.name)

			screen.refresh_screen = True

		elif equals(ch, "Decrease marquee length"):
			dir_list.cursor.change_strlen(increase = False)
			dir_list.reshape_list()

			for file in dir_list.list_1d:
				file.set_disp_str(file.name)

			screen.refresh_screen = True

		elif equals(ch, "Toggle watched state"):
			to_toggle = dir_list.selected_items or [dir_list.cursor]

			for item in to_toggle:
				item.toggle_watched()
			
			info_panel.show_info(dir_list.cursor)

		elif equals(ch, "Select/deselect item under cursor"):
			if dir_list.cursor not in dir_list.selected_items:
				if dir_list.cursor.name != "..":
					dir_list.selected_items.append(dir_list.cursor)
			
			else:
				dir_list.selected_items.remove(dir_list.cursor)

			statusbar.update_count(len(dir_list.selected_items))

			screen.refresh_screen = True

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
			
			statusbar.update_count(len(dir_list.selected_items))

			screen.refresh_screen = True

		elif equals(ch, "Select all items"):
			all_items = dir_list.list_1d
			
			if all_items[0].name == "..":
				all_items = all_items[1:]

			if not dir_list.selected_items == all_items:
				dir_list.selected_items = all_items
				statusbar.update_count(len(dir_list.selected_items))

				screen.refresh_screen = True
			
			else: curses.ungetch(KEYBINDS["Deselect all items"][0][0])
		
		elif equals(ch, "Deselect all items"):
			dir_list.selected_items = []

			statusbar.update_count(len(dir_list.selected_items))
			screen.refresh_screen = True

		elif equals(ch, "Toggle info panel"):
			settings.SHOW_INFO_PANEL = not settings.SHOW_INFO_PANEL
			screen.handle_resize()
			set_scroll()

			screen.refresh_screen = True

		elif equals(ch, "Group open all selected items directly"):
			if not (dir_list.selected_items == [] and dir_list.cursor.name == ".."):
				change_list(group_open = True)
		
		elif equals(ch, "Open file/directory under cursor"):
			change_list(dir_list.cursor.path)

		elif equals(ch, "Help"):
			settings.SHOW_INFO_PANEL = False
			screen.frame.title = "Help section"
			screen.handle_resize()
			set_scroll()

			help_section.show_help(pad, screen, screen.searchbar.in_search_results)

			screen.frame.title = "File Navigator"
			screen.handle_resize()

		elif equals(ch, "Search"):
			screen.cwdbar.hide(True)

			if not screen.searchbar.search(dir_list):
				screen.cwdbar.hide(False)

			else:
				screen.frame.title = "Search Results"

			screen.handle_resize()

		elif equals(ch, "Reverse sort order"):
			change_list(rev = True)

		elif equals(ch, "Quit"):
			sql.close()
			break

		elif ch > 0 and chr(ch).isalnum():
			qs += chr(ch)

			for file in dir_list.list_1d:
				if file.name.lower().replace(' ', '').startswith(qs):
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

		screen.refresh_status()

def start(org_path, db_path):
	curses.wrapper(main, org_path, db_path)