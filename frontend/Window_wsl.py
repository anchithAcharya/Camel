import curses
from .Point_wsl import Point
from .colors_wsl import COLOR_DICT
from . import settings_wsl as settings

class Window: # TODO: add statusbar, include it in resize()

	def __init__(self, title, window):
		self.WIN = window
		self.dim = Point(self.WIN.getmaxyx())
		self.title = title
		
		self.subs = []
		self.frame = None
		self.cwdbar = None
		self.statusbar = None
		
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

	def handle_resize(self):
		self.dim = Point(self.WIN.getmaxyx())

		if self.dim < 10:
			exit("window size too small")

		self.WIN.clear()
		self.refresh()
		
		self.frame.handle_resize()
		self.cwdbar.handle_resize()
		self.statusbar.handle_resize()

		for sub in self.subs:
			sub.handle_resize()


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

	def handle_resize(self):
		if self.title == "CML":
			if settings.SHOW_INFO_PANEL:
				self.constraint = lambda screen, : (screen.dim - Point(7,2), Point(1))
		
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