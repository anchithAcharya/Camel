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

	def __init__(self, parent, root_path):
		self.CWDBAR = parent.WIN.subwin(1,1, 0,0)
		
		self.dim = Point(1, parent.dim.x)
		self.start = Point()
		
		self.parent = parent
		parent.cwdbar = self

		self.root = root_path

		self.handle_resize()
	
	def print_cwd(self):
		cwd = os.path.relpath(os.getcwd(), self.root)

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
			pad.safe_print(f"Size: {size} | {cursor.children_count} files in folder.\n")

		else:
			pad.safe_print(f"Size: {size} | Length: {simplify_length(cursor.length)} | Language: {cursor.language} | Genre: {cursor.genre} | Year: {cursor.year}\n")
			
			if cursor.type == "movie":
				if cursor.franchise and cursor.installment:
					pad.safe_print(f"Franchise: {cursor.franchise} | Installment: {cursor.installment}")
					
				if cursor.watched:
					pad.safe_print(" | ")
					pad.safe_print("Movie watched", attr = COLOR_DICT["RED_BLACK"] | curses.A_REVERSE)
					pad.safe_print("\n")
			
			elif cursor.type == "tv_show":
				pad.safe_print(f"Show name: {cursor.show_name} | Season: {cursor.season} | Episode: {cursor.episode}")
				
				if cursor.watched:
					pad.safe_print(" | ")
					pad.safe_print("Episode watched", attr = COLOR_DICT["RED_BLACK"] | curses.A_REVERSE)
					pad.safe_print("\n")

			elif cursor.type == "audio":
				pad.safe_print(f"Artist: {cursor.artist} | Album: {cursor.album}\n")

		pad.safe_print(f"Path: {cursor.path}")

		pad.refresh()

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
