import curses
from re import findall, sub
from .Point_wsl import Point
from .Help_wsl import show_help
from .colors_wsl import COLOR_DICT
from .misc_wsl import Stack
from .settings_wsl import KEYBIND_IN_USE as keybind

class SearchBar:

	def __init__(self, parent, query_obj):
		self.SEARCHBAR = parent.WIN.subwin(1,1, 0,0)
		self.SEARCHBAR.keypad(1)

		self.dim = Point(1, parent.dim.x)
		self.start = Point()
		
		self.parent = parent
		parent.searchbar = self

		self.query = query_obj
		self.history = Stack(rebase = False)

		self.cache = ""
		self.search_result = None
		self.in_search_results = False
		
		self.handle_resize()
	
	def print(self, string, attr = curses.A_NORMAL, alt_attr = None):
		text = []
		alt_attr = alt_attr or COLOR_DICT["LRED_BLACK"]

		alt_texts = findall(r"(?<!\\){(.*?)(?!\\)}", string)
		string = sub(r"\\(.)", '\\1', string)

		if not alt_texts:
			text.append("n: " + string)

		for alt_text in alt_texts:
			split = string.split('{' + alt_text + '}', 1)

			text.append("n: " + split[0])
			text.append("a: " + alt_text)
		
			if alt_text == alt_texts[-1]:
				text.append("n: " + split[1])

			string = split[1]

		try:
			for part in text:
				if part.startswith("n: "):
					self.SEARCHBAR.addstr(part[3:], attr)

				elif part.startswith("a: "):
					self.SEARCHBAR.addstr(part[3:], alt_attr)

		except curses.error:
			return

	def _prompt(self):
		self.print("{ Search:} ", alt_attr = COLOR_DICT["RED_BLACK"] | curses.A_REVERSE)

	def search(self, dir_list):
		statusbar = self.parent.statusbar

		def print_success(msg):
			statusbar.safe_print(msg, attr = statusbar.attr | curses.A_REVERSE, curs_pos_x = statusbar.dim.x - len(msg) - 1)
			statusbar.refresh()

			statusbar.alt_cache = msg

		def print_error(msg):
			close()

			self.SEARCHBAR.erase()
			self.print(f"{{Error:}} {msg}", alt_attr = COLOR_DICT["RED_BLACK"] | curses.A_REVERSE)
			self.print(" Press {Esc} to return to the file navigator, or try again by pressing any other key.")
			self.SEARCHBAR.refresh()

		def close(clear_cwdbar = True, clear_statusbar = True):
			if clear_cwdbar:
				self.SEARCHBAR.erase()
				self.SEARCHBAR.refresh()

			if clear_statusbar:
				statusbar.write(('Help', 'Reverse sort order', 'Quit'))

		while 1:
			self.SEARCHBAR.erase()
			self._prompt()

			self.print(f"Press any key to start searching.", attr = COLOR_DICT["GRAY_BLACK"])
			self.SEARCHBAR.refresh()

			statusbar.write(extra = [("Esc", "Cancel"), (keybind["Help"][0][1], "See how to use search")])

			if self.search_result:
				if self.search_result[0] is True:
					print_success(self.search_result[1])

				elif self.search_result[0] is False:
					print_error(self.search_result[1])
					self.search_result = None

			if (query := self._get_input(dir_list)) is False:
				if self.in_search_results:
					close(clear_statusbar = False)
					return True
				
				else:
					close()
					return False

			parsed = self._parse_query(query)

			try:
				fileList = self.query.search(parsed)
				dir_list.change_list(fileList, search = True)
				dir_list.display()

				msg = f" | {len(fileList)} file{'s' if len(fileList) > 1 else ''} found"
				self.search_result = (True, msg)
				self.in_search_results = True

				close()
				print_success(msg)
				return msg
			
			except (ValueError, SyntaxError, AttributeError, TypeError, FileNotFoundError) as e:
				self.search_result = (False, e.args[0])
				statusbar.alt_cache = ""

	def _parse_query(self, query):
		# keywords = ["in", "type", "path", "ext", "size", "year", "genre", "length", "language", "album", "artist", "watched", "franchise", "installment", "show", "season", "episode"]
		parsed = query
		results = findall("\${(.*?: .*?)}", query)

		for result in results:
			parsed = parsed.replace("${" + result + "}", '')
		
		results.append("name: " + parsed.strip())

		matches = {}
		for result in results:
			i = result.split(': ', maxsplit = 1)
			matches[i[0]] = i[1]

		return matches

	def _get_input(self, dir_list):
		localHistory = Stack(self.history._stack + [None], rebase = False)
		win = self.SEARCHBAR
		inp_list = []
		string = ""
		index = 0
		first = True

		curses.noecho()
		win.keypad(1)
		win.nodelay(1)
		self.parent.manage_resize = 0

		def handle_history(func):
			nonlocal index, inp_list, string

			ret = func(lambda: localHistory.set_cur(string))

			if ret is not None:
				inp_list = list(ret)
				index = len(inp_list)
				string = ''.join(inp_list)

				win.move(0,0)
				win.clrtoeol()

				self._prompt()
				win.addstr(string)

		while 1:
			c = win.getch()
			
			if c == curses.KEY_RESIZE:
				self.parent.manage_resize = 1
				self.cache = string

			elif c != -1:
				y,x = win.getyx()

				if first:
					first = False

					win.erase()
					self._prompt()
					curses.curs_set(1)

				if c == curses.KEY_UP:
					handle_history(localHistory.up)

				elif c == curses.KEY_DOWN:
					handle_history(localHistory.down)

				elif c == curses.KEY_LEFT:
					if index > 0:
						index -= 1
						win.move(y,x-1)

				elif c == curses.KEY_RIGHT:
					if index < len(inp_list):
						index += 1
						win.move(y,x+1)

				elif c == curses.KEY_DC:
					if index < len(inp_list):
						inp_list.pop(index)
						win.delch(y,x)

				elif c == curses.KEY_BACKSPACE:
					if index > 0:
						inp_list.pop(index-1)
						index -= 1

						win.delch(y,x-1)
						win.move(y,x-1)
				
				elif c == curses.KEY_HOME:
					win.move(y,x-index)
					index = 0
				
				elif c == curses.KEY_END:
					win.move(y,(x + len(inp_list) - index))
					index = len(inp_list)

				elif c == 10:
					break

				elif c == 27:
					string = False
					break

				elif c == keybind["Help"][0][0]:
					curses.curs_set(0)

					win.erase()
					win.refresh()

					show_help(dir_list.pad, self.parent)
					dir_list.display()

					win.erase()
					self._prompt()
					win.addstr(string)

					curses.curs_set(1)

				elif chr(c).isprintable():
					if len(inp_list) < (self.dim.x - 10):				
						if index < len(inp_list):
							win.insch(c)
							win.move(y, x + 1)

						else:
							win.addch(c)

						inp_list.insert(index, chr(c))
						index += 1

						string = ''.join(inp_list)

			if self.parent.manage_resize == 2:
				self.parent.refresh_status()

				win.erase()
				self._prompt()
				win.addstr(self.cache)

				curses.curs_set(1)
			
			else: self.parent.refresh_status()

			win.refresh()

		if string: self.history.append(string)
		curses.curs_set(0)

		return string

	def handle_resize(self):
		self.dim = Point(1, self.parent.dim.x)
		self.start = Point(self.parent.dim.y - 2, 0)

		self.SEARCHBAR.resize(*self.dim)
		self.SEARCHBAR.mvwin(*self.start)