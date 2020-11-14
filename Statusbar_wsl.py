import curses
from Point_wsl import Point
from Window_wsl import Window
from settings_wsl import KEYBIND_IN_USE as KEYBINDS

class Statusbar:

	def __init__(self, parent: Window, attr):
		self.STATUSBAR = parent.WIN.subwin(1,1, 0,0)
		
		self.parent = parent
		parent.statusbar = self

		self.attr = attr
		self.content = []

		self.handle_resize()
	
	def erase(self):
		self.STATUSBAR.erase()

	def draw(self):
		self.erase()

		self.STATUSBAR.attron(self.attr | curses.A_REVERSE)

		for i in range(self.dim.x):
			self.STATUSBAR.insch(' ')

		self.STATUSBAR.attron(self.attr | curses.A_REVERSE)

	def safe_print(self, string, attr = None, curs_pos_x = None):
		attr = attr or self.attr
		curs_pos_x = curs_pos_x or self.STATUSBAR.getyx()[1]

		if attr: self.STATUSBAR.attron(attr)

		while 1:
			try:
				self.STATUSBAR.addstr(0,curs_pos_x, string, attr)
				break

			except curses.error:
				return
		
		if attr: self.STATUSBAR.attroff(attr)

	def write(self, actions, extra = []):
		messages = []
		
		for action in actions:
			messages.append((KEYBINDS[action][0][1], action))

		messages += extra

		self.content = messages

		self.draw()
		self.safe_print('  ', self.attr | curses.A_REVERSE)

		for key, action in messages:
			self.safe_print(key)
			self.safe_print(' ' + action + '  ', self.attr | curses.A_REVERSE)
		
		self.refresh()
	
	def refresh(self):
		self.STATUSBAR.refresh()
	
	def handle_resize(self):
		self.dim = Point(1, self.parent.dim.x)
		self.start = Point(self.parent.dim.y - 1, 0)

		self.STATUSBAR.resize(*self.dim)
		self.STATUSBAR.mvwin(*self.start)

		self.write([],extra = self.content)
		self.refresh()