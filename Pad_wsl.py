import curses
from Point_wsl import Point

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

	def __init__(self, size: Point, parent):
		self.PAD = curses.newpad(1,1)
		self.parent = parent
		parent.pad = self
		
		self.SCROLLBAR = Scrollwin(self)

		self.scroll_pos = 0
		self.max_used_space = None

		self.max = Point()
		self.dim = self.parent.dim - Point(2,3)

		self.start = Point(parent.WIN.getparyx()) + 1

		self.list = None

		self.resize(size)

	def erase(self):
		self.PAD.erase()

	def safe_print(self, string, attr = curses.A_NORMAL, curs_pos = Point(None)):
		curs_pos = curs_pos.assign_if_none(Point(self.PAD.getyx()))

		while 1:
			try:
				self.PAD.addstr(*curs_pos, string, attr)
				break

			except curses.error:
				self.resize(Point(self.max.y + 20, self.max.x))

	def refresh(self, scroll = Point(), offset = None, refresh_scrollbar = True):
		scroll = scroll.assign_if_none(Point(self.scroll_pos, 0))
		offset = offset or self.start
		
		self.PAD.refresh(*scroll, *offset, *(self.dim + (offset - 1)))
		
		if refresh_scrollbar:
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

		if self.max.x < self.dim.x:
			self.resize(Point(self.max.y, self.dim.x))

		self.SCROLLBAR.resize(self.dim.y)
		if self.list: self.list.reshape_list()

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