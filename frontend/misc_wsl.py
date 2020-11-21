import os
import curses
from .Point_wsl import Point
from .Window_wsl import Subwindow
from .colors_wsl import COLOR_DICT
from . import settings_wsl as settings

class Stack_pointer:
	max_limit = 30

	def __init__(self) -> None:
		self._stack = []
		self._pointer = -1

	def append(self, item):
		if self._stack:
			if self._pointer != len(self._stack) - 1:
				self._stack = self._stack[:self._pointer + 1]
			
			if self._stack[-1] == item:
				return

			if len(self._stack) >= Stack_pointer.max_limit:
				self._stack.pop(0)
				self._pointer -= 1
		
		self._stack.append(item)
		self._pointer += 1
	
	def up(self):
		if self._pointer > 0:
			self._pointer -= 1
		
			return self._stack[self._pointer]

	def down(self):
		if self._pointer < len(self._stack) - 1:
			self._pointer += 1

			return self._stack[self._pointer]
	
	def get_cur(self):
		return self._stack[self._pointer]

class CWDBar:

	def __init__(self, parent):
		self.CWDBAR = parent.WIN.subwin(1,1, 0,0)
		self.dim = Point(1, parent.dim.x)
		self.start = Point()
		
		self.parent = parent
		parent.cwdbar = self

		self.handle_resize()
	
	def print_cwd(self):
		cwd = os.path.relpath(os.getcwd(), settings.ROOT)

		if cwd.startswith('.'):
			cwd = cwd.replace('.', '')

		cwd = "~/" + cwd

		self.CWDBAR.erase()

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
		self.dim = Point(1, self.parent.dim.x)
		self.start = Point(self.parent.dim.y - 2, 0)

		self.CWDBAR.resize(*self.dim)
		self.CWDBAR.mvwin(*self.start)

		self.print_cwd()

class InfoPanel(Subwindow):
	
	def show_info(self, cursor):
		self.cache = cursor
		
		if not settings.SHOW_INFO_PANEL:
			return
		
		self.WIN.erase()
		self.decorate()
		
		def human_size(bytes, units = [' bytes','KB','MB','GB']):
			return str(bytes) + units[0] if bytes < 1024 else human_size(bytes>>10, units[1:])
		
		name = os.path.split(os.path.abspath(cursor.name))[-1]
		size = human_size(os.path.getsize(cursor.name))
		self.safe_print(name, curs_pos = Point(1))
		self.safe_print(size, curs_pos = Point(2,1))

		self.refresh()

	def handle_resize(self):
		if settings.SHOW_INFO_PANEL:
			super().handle_resize()
			self.refresh()
		
		else:
			self.dim = Point(1)
			self.start = Point(0)

			self.resize(self.dim)

			self.WIN.mvwin(*self.start)
			self.WIN.mvderwin(*self.start)
