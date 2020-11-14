import curses
from Point_wsl import Point
from Colors_wsl import COLOR_DICT

class Window: # TODO: add statusbar, include it in resize()

	def __init__(self, window):
		self.WIN = window
		self.dim = Point(self.WIN.getmaxyx())
		
		self.sub = None
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

	def subwin(self, dim: Point, start = Point(0,0)):
		self.sub = Subwindow(self, dim, start)

		return self.sub
		
	def refresh(self):
		self.WIN.refresh()
		
	def resize(self, new_dim: Point):
		try:
			self.WIN.resize(*new_dim)
			self.dim = new_dim
		
		except curses.error:
			exit("Could not resize window.")

	def handle_resize(self):
		self.dim = Point(self.WIN.getmaxyx())

		if self.dim < 8:
			exit("window size too small")

		self.WIN.clear()
		self.refresh()
		
		self.sub.handle_resize()
		self.statusbar.handle_resize()

class Subwindow(Window):
	def __init__(self, parent, dim: Point, start = Point(0,0)):
		try:
			sub = parent.WIN.subwin(*dim, *start)
		
		except curses.error:
			exit("could not create subwindow.")
		
		super().__init__(sub)
		del self.sub, self.statusbar
		self.subwin = None

		self.parent = parent
		
		self.start = start
		self.pad = None

		self.refresh()
	
	def decorate(self):
		self.safe_print(None, "border", attr = COLOR_DICT["RED_BLACK"])
		self.safe_print(" CML ", curs_pos = Point(0,5))

	def handle_resize(self):
		self.resize(self.parent.dim - Point(3,2))
		self.decorate()

		self.pad.handle_resize()
		self.refresh()