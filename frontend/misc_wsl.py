import os
import curses
from .Pad_wsl import Pad
from .Point_wsl import Point
from .Window_wsl import Subwindow
from .colors_wsl import COLOR_DICT
from . import settings_wsl as settings

def simplify_size(fsize, units = (' bytes',' KB',' MB',' GB')):
	return "{:.2f}{}".format(float(fsize), units[0]) if fsize < 1024 else simplify_size(fsize / 1024, units[1:])

def simplify_length(seconds):
	if not seconds: return None
	
	hours = seconds // (60*60)
	seconds %= (60*60)

	minutes = seconds // 60
	seconds %= 60
	
	return "%02i:%02i:%02i" % (hours, minutes, seconds)

def print_info(pad, info, end_with_newline = True):
	info = list(info.items())
	printed = False

	for key, value in info:
		if value:
			if printed:
				pad.safe_print(" | ", ellipses = True)
			
			if "watched" in str(key):
				pad.safe_print(str(key), attr = COLOR_DICT["RED_BLACK"] | curses.A_REVERSE, ellipses = True)
				printed = True
			
			else:
				pad.safe_print(str(key), attr = COLOR_DICT["RED_BLACK"], ellipses = True)

				if value != " files in folder.":
					pad.safe_print(': ', ellipses = True)
				
				elif key == 1:
					value = " file in folder."

				pad.safe_print(str(value), ellipses = True)
				printed = True
					
	if end_with_newline and printed:
		pad.safe_print("\n")

class Stack:
	def __init__(self, init_list = [], rebase = True, limit = 30) -> None:
		self._stack = []
		self._pointer = -1
		self.rebase = rebase
		self.max_limit = limit

		for item in init_list:
			self.append(item)

	def append(self, item):
		if self._stack:
			if self.rebase and (self._pointer != len(self._stack) - 1):
				self._stack = self._stack[:self._pointer + 1]
			
			if self._stack[-1] == item:
				return

			if len(self._stack) >= self.max_limit:
				self._stack.pop(0)
				self._pointer -= 1
		
		self._stack.append(item)
		self._pointer += 1

	def up(self, func = lambda: None):
		if self._pointer > 0:
			func()

			self._pointer -= 1		
			return self._stack[self._pointer]

	def down(self, func = lambda: None):
		if self._pointer < len(self._stack) - 1:
			func()

			self._pointer += 1
			return self._stack[self._pointer]

	def get_cur(self):
		return self._stack[self._pointer]

	def set_cur(self, value):
		self._stack[self._pointer] = value

class CWDBar:

	def __init__(self, parent, root_path):
		self.CWDBAR = parent.WIN.subwin(1,1, 0,0)
		
		self.dim = Point(1, parent.dim.x)
		self.start = Point()
		
		self.parent = parent
		parent.cwdbar = self

		self.root = root_path
		self.show = True

		self.handle_resize()
	
	def hide(self, hide_CWDbar):
		if hide_CWDbar:
			self.show = False
		
		else:
			self.show = True
		
		self.handle_resize()

	def print_cwd(self, show = True):
		self.CWDBAR.erase()

		if show:
			cwd = os.path.relpath(os.getcwd(), self.root)

			if cwd.startswith('.'):
				cwd = cwd.replace('.', '')

			cwd = " ROOT /" + cwd

			for ch in cwd:
				attr = curses.A_NORMAL
				
				if ch == '/' or ch == '~':
					attr = COLOR_DICT["LRED_BLACK"]

				if ch == '/':
					ch = ' > '
				
				try:
					self.CWDBAR.addstr(ch, attr)
				
				except curses.error:
					break

		self.CWDBAR.refresh()
	
	def handle_resize(self):
		if self.show:
			self.dim = Point(1, self.parent.dim.x)
			self.start = Point(self.parent.dim.y - 2, 0)

			self.CWDBAR.resize(*self.dim)
			self.CWDBAR.mvwin(*self.start)

		self.print_cwd(self.show)

class InfoPanel(Subwindow):
	
	def __init__(self, parent, constraint, title):
		super().__init__(parent, constraint, title)

		self.pad = Pad(self.dim - 2, self, noScrollBar = True)
		self.decorate()
	
	def show_info(self, cursor):
		pad = self.pad
		self.cache = cursor
		
		if not settings.SHOW_INFO_PANEL:
			return

		size = simplify_size(cursor.size)

		pad.erase()

		if cursor.type == "media_dir":
			if "Close search" in cursor.disp_str:
				pad.safe_print("Close the search menu and return to the file tree.", ellipses = True)

			else:
				print_info(pad, {"Size" : size, cursor.children_count : " files in folder."})

		else:
			language = ", ".join(cursor.language[:3])
			genre = ", ".join(cursor.genre[:3])

			print_info(pad, {"Size" : size, "Length" : simplify_length(cursor.length), "Language" : language, "Genre" : genre, "Year" : cursor.year})

			if cursor.type == "movie":
				print_info(pad, {"Franchise" : cursor.franchise, "Installment" : cursor.installment, "Movie watched" : cursor.watched})
			
			elif cursor.type == "tv_show":
				print_info(pad, {"Show name" : cursor.show_name, "Season" : cursor.season, "Episode" : cursor.episode, "Episode watched" : cursor.watched})

			elif cursor.type == "audio":
				artist = ", ".join(cursor.artist)
				print_info(pad, {"Artist" : artist, "Album" : cursor.album})

			print_info(pad, {"Path" : cursor.real_path}, False)

		pad.refresh()

	def handle_resize(self):
		if settings.SHOW_INFO_PANEL:
			super().handle_resize()

			self.show_info(self.cache)
			self.refresh()
		
		else:
			self.dim = Point(1)
			self.start = Point(0)

			self.resize(self.dim)

			self.WIN.mvwin(*self.start)
			self.WIN.mvderwin(*self.start)
