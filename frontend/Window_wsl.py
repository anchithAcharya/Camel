import curses
from .Point_wsl import Point
from .colors_wsl import COLOR_DICT
from . import settings_wsl as settings

class Window:

	def __init__(self, title, window):
		self.WIN = window
		self.dim = Point(self.WIN.getmaxyx())
		self.title = title
		
		self.subs = []
		self.frame = None
		self.cwdbar = None
		self.searchbar = None
		self.statusbar = None

		self.refresh_screen = False
		self.manage_resize = 0		# 0: static screen    1: screen is being resized; wait    2: handle resize
		
		self.WIN.clear()
		self.refresh()
	
	def safe_print(self, str, method = "addstr", curs_pos = Point(), attr = None):
		curs_pos = curs_pos.assign_if_none(Point(self.WIN.getyx()))

		if attr: self.WIN.attron(attr)

		while 1:
			try:
				if method == "border":
					getattr(self.WIN, method)()

				else: getattr(self.WIN, method)(*curs_pos, str)
				break

			except curses.error:
				self.resize(self.max_y + 20, self.max_x)

		if attr: self.WIN.attroff(attr)

	def subwin(self, constraint, title = ""):
		return Subwindow(self, constraint, title)

	def refresh(self):
		self.WIN.refresh()
		
	def resize(self, new_dim: Point):
		try:
			self.WIN.resize(*new_dim)
			self.dim = new_dim
		
		except curses.error:
			exit("Could not resize window " + self.title)

	def refresh_status(self):
		if self.manage_resize == 2:
			self.handle_resize()

			curses.curs_set(1)
			curses.curs_set(0)

			self.manage_resize = 0
			self.refresh_screen = True
		
		if self.manage_resize != 0: self.manage_resize = 2

	def handle_resize(self):
		self.dim = Point(self.WIN.getmaxyx())

		# top_padding + (cml top border + (cml content) + cml bottom border) + (details top border + (details content) + details bottom border) + cwdbar + statusbar
		if self.dim < (1 + (1 + (1) + 1) + (1 + (3) + 1) + 1 + 1):
			exit("window size too small")

		self.WIN.clear()
		self.refresh()
		
		self.frame.handle_resize()
		self.cwdbar.handle_resize()
		self.statusbar.handle_resize()
		self.searchbar.handle_resize()

		for sub in self.subs:
			sub.handle_resize()

		self.refresh_screen = True


class Subwindow(Window):
	
	def __init__(self, parent, constraint, title):
		dim, start = constraint(parent)
		
		try:
			sub = parent.WIN.subwin(1,1)
		
		except curses.error:
			exit("could not create subwindow " + title)
		
		self.WIN = sub
		self.subwin = None
		
		self.parent = parent
		self.constraint = constraint
		
		self.dim = dim
		self.start = start

		self.pad = None
		self.title = title

	def decorate(self):
		self.safe_print(None, "border", attr = COLOR_DICT["RED_BLACK"])
	
		if self.title:
			self.safe_print(" " + self.title + " ", curs_pos = Point(0,5))

	def refresh(self):
		super().refresh()
		
		if self.pad: self.pad.refresh()

	def handle_resize(self):
		if self.title == "CML":
			if settings.SHOW_INFO_PANEL:
				self.constraint = lambda screen, : (screen.dim - Point(8,2), Point(1))
		
			else:
				self.constraint = lambda screen, : (screen.dim - Point(3,2), Point(1))

		dim, self.start = self.constraint(self.parent)
		
		self.WIN.mvwin(*self.start)
		self.WIN.mvderwin(*self.start)
		
		self.resize(dim)

		self.WIN.erase()
		self.decorate()

		if self.pad:
			self.pad.handle_resize()

		self.refresh()