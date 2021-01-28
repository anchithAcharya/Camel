import os
import curses
from .frontend.Pad_wsl import Pad
from .frontend.cml_wsl import start
from .frontend.Point_wsl import Point
from .frontend.Window_wsl import Window
from .frontend.Statusbar_wsl import Statusbar
from .backend.__main__ import main as register_dir
from .frontend.colors_wsl import COLOR_DICT, init_colors
from .frontend.settings_wsl import DATABASE_DIR, KEYBIND_IN_USE

def print_welcome(pad):
	welcome_msg = "Welcome to Console Media Library (CML)!"
	center = int((pad.dim.x / 2) - (len(welcome_msg) / 2))

	pad.safe_print(welcome_msg + "\n\n", curs_pos = Point(1, center))

def prompt(pad):
	pad.safe_print("Enter the path:", attr = COLOR_DICT["RED_BLACK"] | curses.A_REVERSE, curs_pos = Point(pad.dim.y - 1, 0))
	pad.safe_print(" ")

def str_eval(string, screen):
	screen.cwdbar.erase()
	screen.cwdbar.safe_print("   ")

	if not string:
		screen.cwdbar.safe_print("Please enter the path of the directory to be organised.", attr = COLOR_DICT["LRED_BLACK"])
		return False
	
	elif string == '/':
		screen.cwdbar.safe_print("It is not advisable to enter the root directory.", attr = COLOR_DICT["ORANGE_BLACK"])
		return True
	
	else:
		string = os.path.expanduser(string)

	if os.path.exists(string):
		if os.path.isdir(string):
			screen.cwdbar.safe_print("Valid directory. Press Enter to continue.", attr = COLOR_DICT["GREEN_BLACK"])
			return True
		
		else:
			screen.cwdbar.safe_print("File exists, but it is not a directory.", attr = COLOR_DICT["ORANGE_BLACK"])
			return False
	
	else:
		screen.cwdbar.safe_print("The file does not exist. Please enter a valid path.", attr = COLOR_DICT["LRED_BLACK"])
		return False

def get_input(pad, screen):
	valid_dir = False
	inp_list = []
	string = ""
	cache = ""
	index = 0

	curses.noecho()
	pad.PAD.keypad(1)
	pad.PAD.nodelay(1)
	screen.manage_resize = 0

	while 1:
		c = pad.PAD.getch()
		
		if c == curses.KEY_RESIZE:
			screen.manage_resize = 1
			cache = string

		elif c != -1:
			y,x = pad.PAD.getyx()

			if c == curses.KEY_LEFT:
				if index > 0:
					index -= 1
					pad.PAD.move(y,x-1)

			elif c == curses.KEY_RIGHT:
				if index < len(inp_list):
					index += 1
					pad.PAD.move(y,x+1)

			elif c == curses.KEY_UP or c == curses.KEY_DOWN:
				pass

			elif c == curses.KEY_DC:
				if index < len(inp_list):
					inp_list.pop(index)
					pad.PAD.delch(y,x)

			elif c == curses.KEY_BACKSPACE:
				if index > 0:
					inp_list.pop(index-1)
					index -= 1

					pad.PAD.delch(y,x-1)
					pad.PAD.move(y,x-1)
			
			elif c == curses.KEY_HOME:
				pad.PAD.move(y,x-index)
				index = 0
			
			elif c == curses.KEY_END:
				pad.PAD.move(y,(x + len(inp_list) - index))
				index = len(inp_list)

			elif c == 10 and valid_dir:
				break

			elif chr(c).isprintable():
				if len(inp_list) < (pad.dim.x - 20):
					if index < len(inp_list):
						pad.PAD.insch(c)
						pad.PAD.move(y, x + 1)

					else:
						pad.PAD.addch(c)

					inp_list.insert(index, chr(c))
					index += 1

			string = ''.join(inp_list)
			valid_dir = str_eval(string, screen)
			screen.cwdbar.refresh()
			pad.refresh()

		if screen.manage_resize == 2:
			screen.refresh_status()

			pad.erase()
			print_welcome(pad)
			prompt(pad)
			pad.PAD.addstr(cache)
			pad.refresh()

			valid_dir = str_eval(string, screen)

			curses.curs_set(1)
		
		else:
			screen.refresh_status()

	curses.curs_set(0)
	pad.PAD.nodelay(0)

	return os.path.abspath(os.path.expanduser(string))

def main(screen):
	init_colors()

	screen = Window("screen", screen)
	screen.frame = screen.subwin(lambda screen, : (screen.dim - 1, Point(1)), title = "CML", main_window = True)

	screen.cwdbar = Statusbar(screen, y_pos = -2)
	screen.statusbar = Statusbar(screen, COLOR_DICT["RED_BLACK"], bg_attr = COLOR_DICT["RED_BLACK"] | curses.A_REVERSE)

	screen.statusbar.write(extra = [("", "Enter the path of the directory to be organised, and press"), ("Enter", "")])

	pad = Pad(screen.frame.dim - 1, screen.frame, noScrollBar = True)
	screen.handle_resize()

	print_welcome(pad)
	prompt(pad)
	pad.refresh()
	
	path = get_input(pad, screen)

	db_name = "db_" + str(os.stat(path).st_ino) + ".db"
	choice = True

	if os.path.exists(DATABASE_DIR + db_name):
		pad.PAD.move(4,0)
		pad.PAD.clrtobot()

		msg = "This directory has already been organised previously. Do you want to load the same?"
		center = int((pad.dim.x / 2) - (len(msg) / 2))

		pad.safe_print(msg + "\n\n", curs_pos = Point(4, center))

		yes = "  Yes  "
		no = "  No  "
		center = int((pad.dim.x / 2) - (len(yes + "  " + no) / 2))

		attr = COLOR_DICT["LRED_BLACK"]

		screen.statusbar.erase()
		screen.statusbar.write(extra = [('←', "Select left"), ('→', "Select right"), ("Enter", "Confirm selection")])

		while 1:
			pad.PAD.move(6,0)
			pad.PAD.clrtoeol()

			pad.safe_print(yes, attr = (attr | curses.A_REVERSE if choice else attr), curs_pos = Point(6, center))
			pad.safe_print(no, attr = (attr | curses.A_REVERSE if not choice else attr), curs_pos = Point(6, center + len(yes) + 2))

			pad.refresh()

			screen.cwdbar.erase()

			if choice:
				screen.cwdbar.safe_print("This will load the existing file hierarchy that had been organised before.", attr = COLOR_DICT["GREEN_BLACK"])
			
			else:
				screen.cwdbar.safe_print("This will delete the collected data, and the directory will be organised again. This may take some time.", attr = COLOR_DICT["RED_BLACK"])
			
			screen.cwdbar.refresh()

			ch = pad.PAD.getch()

			if ch == curses.KEY_LEFT:
				choice = True

			elif ch == curses.KEY_RIGHT:
				choice = False
			
			elif ch == 10:
				break

	pad.PAD.move(4,0)
	pad.PAD.clrtobot()
	pad.refresh()
	screen.statusbar.draw()
	screen.statusbar.refresh()

	new_path, db_path = register_dir(screen, path, not choice)

	pad.erase()
	msg = "Ready! Press any key to continue to the file navigator."
	x_center = int((pad.dim.x / 2) - (len(msg) / 2))
	y_center = int(pad.dim.y/2)
	pad.safe_print(msg, curs_pos = Point(y_center, x_center))

	help_key = KEYBIND_IN_USE["Help"][0][1]
	msg = "Quick tip: Press '" + help_key + "' to see the various shortcuts and other handy info!"
	x_center = int((pad.dim.x / 2) - (len(msg) / 2))
	pad.safe_print(msg, curs_pos = Point(y_center + 1, x_center))

	pad.refresh()
	pad.PAD.getch()

	start(new_path, db_path)

os.environ.setdefault('ESCDELAY', '100')
curses.wrapper(main)