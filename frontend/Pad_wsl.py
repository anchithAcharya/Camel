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
		self.scroll_len = 1
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

	def update_scroll(self):
		List = self.parent.list

		try:
			self.scroll_pos = round(((List.cursor.index.y + 1) / List.dim.y) * (self.dim.y - 1))

			if self.scroll_pos > self.dim.y:
				self.scroll_pos = self.dim.y

			self.scroll_len = round(self.dim.y / List.dim.y)

			self.scroll_len = max(self.scroll_len, 1)
			self.scroll_len = min(self.scroll_len, self.dim.y)

		except (ZeroDivisionError, AttributeError):
			self.scroll_pos = 0
			self.scroll_len = 1

	def scroll(self):
		self.WIN.erase()

		scroll_pos_y = self.scroll_pos

		for _ in range(self.scroll_len):
			self.WIN.insstr(scroll_pos_y,0, self.SCROLL_CHAR)
			scroll_pos_y -= 1

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

	def safe_print(self, string, attr = curses.A_NORMAL, curs_pos = Point(None), ellipses = False):
		curs_pos = curs_pos.assign_if_none(Point(self.PAD.getyx()))

		while 1:
			try:
				limit = len(string) - (self.dim.x - curs_pos.x)

				if ellipses and limit > 0 and string != "\n":
					self.PAD.addstr(*curs_pos, string[:-(limit+3)], attr)
					self.PAD.addstr("...", COLOR_DICT["RED_BLACK"])

				else:
					self.PAD.addstr(*curs_pos, string, attr)

				break

			except curses.error:
				if ellipses:
					self.resize(Point(self.max.y + 5, self.max.x))

				else:
					exit("Error: Window size too small")

	def refresh(self, scroll = Point(), offset = None, refresh_scrollbar = True):
		scroll = scroll.assign_if_none(Point(self.scroll_pos, 0))
		offset = offset or self.start
		
		self.PAD.refresh(*scroll, *offset, *(self.dim + (offset - 1)))
		
		if self.SCROLLBAR and refresh_scrollbar:
			self.SCROLLBAR.update_scroll()
			self.SCROLLBAR.scroll()
			self.SCROLLBAR.refresh()

	def subpad(self, dim: Point, start: Point):
		return Subpad(self, dim,start)

	def resize(self, new_dim: Point):
		try:
			self.PAD.resize(*new_dim)
			self.max = new_dim
			self.dim = self.parent.dim - 2
		
		except curses.error:
			exit("could not resize pad")

	def handle_resize(self):
		new_dim = self.parent.dim - 2

		if new_dim > self.dim:
			self.resize(new_dim)

		else: self.dim = new_dim

		if self.SCROLLBAR:
			self.dim -= Point(0,1)

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