import os
from math import ceil
from curses import A_REVERSE
from .Point_wsl import Point
from .colors_wsl import COLOR_DICT
from . import settings_wsl as settings
from ..backend.sql import query_file_type, query_file_details

class Marquee:
	max_strlen = 15
	ellipsis = "..."
	
	def __init__(self, name = "",  file_type = ""):
		self.name = name
		self.type = file_type
		
		self.index = Point()

		if len(self.name) <= Marquee.max_strlen:
			self.disp_str = self.name + ' ' * (Marquee.max_strlen - len(self.name))
			self.show_ellipsis = False

		else:
			self.disp_str = self.name[:Marquee.max_strlen - 3]
			self.show_ellipsis = True

		self.hscroll_index = 0
		self.hscroll_delay = 0

	def __repr__(self) -> str:
		return self.name

	def set_index(self, index):
		self.index = index
	
	def scroll_text(self, cursor, selected_items):
		if self.show_ellipsis and (cursor == self or self in selected_items):
			if self.hscroll_index == 0:
				self.hscroll_delay += 1

				if self.hscroll_delay > 3:
					self.hscroll_delay = 0
					self.hscroll_index += 1

			elif self.hscroll_index > len(self.name) - (Marquee.max_strlen - 1):
				self.hscroll_delay += 1

				if self.hscroll_delay > 3:
					self.hscroll_delay = self.hscroll_index = 0
			
			else: self.hscroll_index += 1

			return ' ' + self.name[self.hscroll_index:][:Marquee.max_strlen-2] + ' ', False
		
		else:
			self.hscroll_index = self.hscroll_delay = 0

		return self.disp_str, self.show_ellipsis

	def display(self, parent_list):
		attr = 0

		if parent_list.cursor == self:
			attr = COLOR_DICT["RED_BLACK"]
		
		elif self.type == "audio":
			attr = COLOR_DICT["ORANGE_BLACK"]
		
		elif self.type in ("movie", "tv_show"):
			attr = COLOR_DICT["PURPLE_BLACK"]
		
		elif self.type == "subs":
			attr = COLOR_DICT["GRAY_BLACK"]
		
		if self in parent_list.selected_items:
			attr |= A_REVERSE
		
		display = []
		string, show_ellipsis = self.scroll_text(parent_list.cursor, parent_list.selected_items)
		
		if self.index.x != 0:
			display.append((parent_list.column_seperator,))

		display.append((string, attr))
		
		if show_ellipsis:
			display.append((Marquee.ellipsis, COLOR_DICT["LRED_BLACK"]))

		return display

class List:
	row_seperator = '\n'
	column_seperator = ' ' * 3
	
	max_strlen = Marquee.max_strlen

	def __init__(self, parent, root_path, dir_list = []):
		self.cursor = None
		self.selected_items = []

		self.dim = Point(0,1)
		self.pad = parent

		self.max_list_width = max(int(self.pad.dim.x / (self.max_strlen + len(self.column_seperator))), 1)
		
		self.list_1d = []
		self.LIST = [[]]
		
		self.root_path = root_path
		self.change_list(dir_list)

	def _enumerate2d(self):
		temp = []
		for x, row in enumerate(self.list_1d):
			for y, element in enumerate(row):
				temp += [[Point(y,x), element]]

		return temp

	def _convert_to_2d(self,list_1d, width = None):
		if not list_1d: return [[]]
		
		width = width or self.max_list_width

		x = width
		y = ceil(len(list_1d)/width)

		temp = [['' for j in range(x)] for i in range(y)]

		count = 0
		for i in range(x):
			for j in range(y):
				temp[j][i] = list_1d[count]
				count += 1

				if count >= len(list_1d):
					ret = [[c for c in row if c != ''] for row in temp]
					return ret

	def _calculate_indices(self):
		length, width = self.dim

		for i in self.LIST:
			for j in i:
				j.set_index(Point(self.LIST.index(i), i.index(j)))

	def _process_list(self, list_1d, show_hidden_files = False,show_only_media_files = True):
		if not show_hidden_files:
			list_1d = [x for x in list_1d if not x.startswith(('.','$'))]
		
		types = []
		to_be_removed = []

		for item in list_1d:
			if item.endswith(settings.EXT['subtitles']):
				to_be_removed.append(item)
			
			else:
				types.append(query_file_type(item))

		for item in to_be_removed:
			list_1d.remove(item)

		if os.getcwd() != self.root_path and os.getcwd() != '/':
			list_1d.insert(0, '..')
			types.insert(0, 'media_dir')

		for item, file_type in zip(list_1d, types):
			self.list_1d.append(Marquee(item, file_type))
		
		for item in self.list_1d:
			file_details = query_file_details(os.path.abspath(item.name), item.type)

			if item.type == "media_dir":
				item.path, item.size, item.children_count = file_details
			
			else:
				item.path, item.size, item.length, item.language, item.genre, item.year = file_details[:6]

				if item.type == "movie":
					item.watched, item.franchise, item.installment = file_details[6:]
			
				elif item.type == "tv_show":
					item.watched, item.show_name, item.season, item.episode = file_details[6:]

				elif item.type == "audio":
					item.artist, item.album = file_details[6:]

		self.LIST = self._convert_to_2d(self.list_1d)

	def reshape_list(self, width = None, rev = False):
		self.max_list_width = max(int(self.pad.dim.x / (self.max_strlen + len(self.column_seperator))),1)
		width =  self.max_list_width
		
		if rev:
			self.list_1d = self.list_1d[:1] + self.list_1d[1:][::-1]

		self.LIST = self._convert_to_2d(self.list_1d, width)
		self.pad.max_used_space = len(self.LIST)

		self._calculate_indices()

	def change_list(self, new_list1d: list, process_settings = (False,True)):
		if not new_list1d: return

		self.list_1d.clear()
		self.selected_items.clear()

		self._process_list(new_list1d, *process_settings)
		
		self.dim = Point(len(self.LIST), len(self.LIST[0]))
		self._calculate_indices()

		self.pad.max_used_space = len(self.LIST)
		self.cursor = self.LIST[0][0]

	def atIndex(self, index: Point):
		for item in self.list_1d:
			if item.index == index:
				return item
		
		return None

	def display(self):
		self.pad.erase()

		for row in self.LIST:
			for item in row:
				display = item.display(self)
				
				for string in display:
					self.pad.safe_print(*string)
				# self.pad.refresh()
		
			self.pad.safe_print(self.row_seperator)

		self.pad.refresh()
