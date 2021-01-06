import curses
from .Point_wsl import Point
from .colors_wsl import COLOR_DICT

class Scrollwin:
		SCROLL_CHAR = '█'

		def __init__(self, parent):
			self.WIN = curses.newwin(1,1)
			self.parent = parent

			self.WIN.leaveok(1)

			self.scroll_pos = 0
			self.dim = Point(0,1)

		def resize(self, new_ylen = None):
			new_ylen = new_ylen or self.parent.dim.y

			try:
				self.WIN.resize(new_ylen, self.dim.x)

				pos = Point(self.parent.start) + Point(0,self.parent.dim.x)
				self.WIN.mvwin(*pos)
			
			except curses.error:
				exit("could not resize scrollwin")
	
			self.dim.y = new_ylen
	
		def update_scroll_pos(self):
			pad = self.parent

			try:
				self.scroll_pos = round((pad.scroll_pos/(pad.max_used_space - pad.dim.y)) * (self.dim.y - 1))
			
				if self.scroll_pos > self.dim.y:
					self.scroll_pos = self.dim.y

			except ZeroDivisionError:
				self.scroll_pos = 0

		def scroll(self):
			self.WIN.erase()
			self.WIN.insstr(self.scroll_pos,0, self.SCROLL_CHAR)
			self.refresh()
		
		def refresh(self):
			self.WIN.refresh()

class Pad:

	def __init__(self, size: Point, parent, noScrollBar = False):
		self.PAD = curses.newpad(1,1)
		self.parent = parent
		parent.pad = self
		
		self.scroll_pos = 0
		self.max_used_space = None

		self.max = Point()
		self.dim = self.parent.dim - 2

		if noScrollBar:
			self.SCROLLBAR = None
		
		else:
			self.SCROLLBAR = Scrollwin(self)
			self.dim.x -= 1

		self.start = parent.start + 1

		self.list = None

		self.resize(size)

	def erase(self):
		self.PAD.erase()

	def safe_print(self, string, attr = curses.A_NORMAL, curs_pos = Point(None)):
		curs_pos = curs_pos.assign_if_none(Point(self.PAD.getyx()))

		while 1:
			try:
				limit = len(string) - (self.dim.x - curs_pos.x)

				if limit > 0 and string != "\n":
					self.PAD.addstr(*curs_pos, string[:-(limit+3)], attr)
					self.PAD.addstr("...", COLOR_DICT["RED_BLACK"])

				else:
					self.PAD.addstr(*curs_pos, string, attr)

				break

			except curses.error:
				self.resize(Point(self.max.y + 5, self.max.x))

	def refresh(self, scroll = Point(), offset = None, refresh_scrollbar = True):
		scroll = scroll.assign_if_none(Point(self.scroll_pos, 0))
		offset = offset or self.start
		
		self.PAD.refresh(*scroll, *offset, *(self.dim + (offset - 1)))
		
		if self.SCROLLBAR and refresh_scrollbar:
			self.SCROLLBAR.update_scroll_pos()
			self.SCROLLBAR.scroll()
			self.SCROLLBAR.refresh()

	def subpad(self, dim: Point, start: Point):
		return Subpad(self, dim,start)

	def resize(self, new_dim: Point):
		try:
			self.PAD.resize(*new_dim)
			self.max = new_dim
		
		except curses.error:
			exit("could not resize pad")

	def handle_resize(self):
		self.dim = self.parent.dim - Point(2,3)
		self.start = self.parent.start + 1

		if self.max.x < self.dim.x:
			self.resize(Point(self.max.y, self.dim.x))

		if self.list: self.list.reshape_list()
		if self.SCROLLBAR: self.SCROLLBAR.resize(self.dim.y)

		self.refresh()

class Subpad(Pad):
	def __init__(self, parent, dim: Point, start = Point(0,0)):
		try:
			self.PAD = parent.PAD.subpad(*dim, *start)
		
		except curses.error:
			exit("could not create subwindow.")
		
		self.parent = parent
		
		self.dim = dim
		self.start = start

		self.subpad = self.resize = self.handle_resize = None

	def refresh(self):
		self.parent.refresh()