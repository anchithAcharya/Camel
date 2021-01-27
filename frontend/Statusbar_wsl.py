import curses
from .Point_wsl import Point
from .Window_wsl import Window
from .settings_wsl import KEYBIND_IN_USE as KEYBINDS

class Statusbar:

	def __init__(self, parent: Window, attr = curses.A_NORMAL, bg_attr = curses.A_NORMAL, y_pos = -1):
		self.STATUSBAR = parent.WIN.subwin(1,1, 0,0)

		self.y_pos = y_pos
		self.dim = Point(1, parent.dim.x)
		self.start = Point()

		self.parent = parent
		parent.statusbar = self

		self.attr = attr
		self.bg_attr = bg_attr

		self.content = []
		self.alt_cache = ""

		self.handle_resize()
	
	def erase(self):
		self.STATUSBAR.erase()

	def draw(self, till = None):
		self.erase()
		till = till or self.dim.x

		for i in range(till):
			self.STATUSBAR.insch(' ', self.bg_attr)

	def safe_print(self, string, attr = None, curs_pos_x = None):
		attr = attr or self.attr
		curs_pos_x = curs_pos_x or self.STATUSBAR.getyx()[1]

		try:
			self.STATUSBAR.addstr(0,curs_pos_x, string, attr)

		except curses.error:
			return
		
	def write(self, actions = [], extra = []):
		messages = []
		
		for action in actions:
			messages.append((KEYBINDS[action][0][1], action))

		messages += extra

		self.content = messages

		self.draw()
		self.safe_print('  ', self.bg_attr)

		for key, action in messages:
			self.safe_print(key)
			self.safe_print(' ' + action + '  ', self.bg_attr)
		
		self.refresh()
	
	def refresh(self):
		self.STATUSBAR.refresh()
	
	def update_count(self, count):
		string = f" | {count} item{'s' if count > 1 else ''} selected."
		start = self.dim.x - len(string)

		self.write([], extra = self.content)

		if count > 0:
			self.alt_cache = count
			self.safe_print(string, self.bg_attr, start)
			self.refresh()
		
	def handle_resize(self):
		self.dim = Point(1, self.parent.dim.x)
		self.start = Point(self.parent.dim.y + self.y_pos, 0)

		self.STATUSBAR.resize(*self.dim)
		self.STATUSBAR.mvwin(*self.start)

		self.write(actions = [], extra = self.content)
		
		if type(self.alt_cache) is int:
			self.update_count(self.alt_cache)
		
		else:
			self.safe_print(self.alt_cache, self.bg_attr, (self.dim.x - len(self.alt_cache)))

		self.refresh()