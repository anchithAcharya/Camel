import curses

KEY_VALUES = {
	'↑': curses.KEY_UP,
	'↓': curses.KEY_DOWN,
	'←': curses.KEY_LEFT,
	'→': curses.KEY_RIGHT,

	'^↑': 566,
	'^↓': 525,
	'^←': 545,
	'^→': 560,

	'PgUp': curses.KEY_PPAGE,
	'PgDn': curses.KEY_NPAGE,

	'Home': curses.KEY_HOME,
	'End': curses.KEY_END,

	'^PgUp' : 555,
	'^PgDn' : 550,

	'^Home' : 535,
	'^End' : 530,

	'Enter' : 10,
	'Esc' : 27,

	'Insert' : curses.KEY_IC,
	'Del' : curses.KEY_DC,
	'Backspace' : curses.KEY_BACKSPACE,

	'^a' : 1,
	'^d' : 4,
	'^i' : 9,
	'^o' : 15,
	'^w' : 23,
	'Shift+.' : ord('>'),

	'Alt+↑' : 564,
	'Alt+←' : 543,
	'Alt+→' : 558,

	'.' : ord('.'),
	'*' : ord('*'),
	'+' : ord('+'),
	'-' : ord('-'),
	'/' : ord('/'),
	'Space' : ord(' '),

	'F1' : curses.KEY_F1,
	'F4' : curses.KEY_F4,
	'F10' : curses.KEY_F10,
}

def create_keybind(*args):
	temp = []
	for key_repr in args:
		if key_repr in KEY_VALUES:
			temp.append((KEY_VALUES[key_repr], key_repr))

		else:
			temp.append((key_repr, chr(key_repr)))
			
	return tuple(temp)

KEYBINDS = []

KEYBINDS.append({
	"Navigate up" : create_keybind("↑"),
	"Navigate down" : create_keybind("↓"),
	"Navigate left" : create_keybind("←"),
	"Navigate right" : create_keybind("→"),

	"Scroll up" : create_keybind("^PgUp"),
	"Scroll down" : create_keybind("^PgDn"),
	"Scroll left" : create_keybind("^Home"),
	"Scroll right" : create_keybind("^End"),

	"Page up" : create_keybind("PgUp"),
	"Page down" : create_keybind("PgDn"),

	"Navigate to first item" : create_keybind("Home"),
	"Navigate to bottom-most item" : create_keybind("End"),

	"Toggle watched state" : create_keybind("^w"),
	"Toggle info panel" : create_keybind("^i"),


	"Move up by one directory" : create_keybind("Alt+↑"),
	
	"Back" : create_keybind("Alt+←"),
	"Forward" : create_keybind("Alt+→"),

	"Select/deselect item under cursor" : create_keybind(".", "Space"),
	"Group select" : create_keybind("Shift+."),

	"Select all items" : create_keybind("^a"),
	"Deselect all items" : create_keybind("^d"),

	"Open file/directory under cursor" : create_keybind("Enter"),
	"Group open all selected items directly" : create_keybind("^o"),
	
	"Help" : create_keybind("F1"),
	"Reverse sort order" : create_keybind("F4"),
	
	"Quit" : create_keybind("F10")
})

KEYBINDS.append({
	"Navigate up" : create_keybind(ord('8')),
	"Navigate down" : create_keybind(ord('5')),
	"Navigate left" : create_keybind(ord('4')),
	"Navigate right" : create_keybind(ord('6')),

	"Scroll up" : create_keybind("↑"),
	"Scroll down" : create_keybind("↓"),
	"Scroll left" : create_keybind("←"),
	"Scroll right" : create_keybind("→"),

	"Page up" : create_keybind(ord('9'), "PgUp"),
	"Page down" : create_keybind(ord('3'), "PgDn"),
	
	"Navigate to first item" : create_keybind("Home", ord('7')),
	"Navigate to bottom-most item" : create_keybind("End", ord('1')),

	"Toggle watched state" : create_keybind("^w"),
	"Toggle info panel" : create_keybind("^i"),


	"Move up by one directory" : create_keybind("Alt+↑", "/"),
	
	"Back" : create_keybind("-", "Alt+←"),
	"Forward" : create_keybind("+", "Alt+→"),

	"Select/deselect item under cursor" : create_keybind(".", "Space"),
	"Group select" : create_keybind("Shift+.", "Del"),
	
	"Select all items" : create_keybind("*", "^a"),
	"Deselect all items" : create_keybind("^d"),

	"Open file/directory under cursor" : create_keybind(ord('0')),
	"Group open all selected items directly" : create_keybind("Enter"),

	
	"Help" : create_keybind("F1", "Backspace"),
	"Reverse sort order" : create_keybind("F4"),
	
	"Quit" : create_keybind("F10")
})

KEYBINDS.append({
	"Navigate up" : create_keybind("↑"),
	"Navigate down" : create_keybind("↓"),
	"Navigate left" : create_keybind("←"),
	"Navigate right" : create_keybind("→"),

	"Scroll up" : create_keybind("^↑"),
	"Scroll down" : create_keybind("^↓"),
	"Scroll left" : create_keybind("^←"),
	"Scroll right" : create_keybind("^→"),

	"Page up" : create_keybind("PgUp"),
	"Page down" : create_keybind("PgDn"),
	
	"Navigate to first item" : create_keybind("Home"),
	"Navigate to bottom-most item" : create_keybind("End"),

	"Toggle watched state" : create_keybind("^w"),
	"Toggle info panel" : create_keybind("^i"),


	"Move up by one directory" : create_keybind("Alt+↑", "/"),
	
	"Back" : create_keybind("-", "Alt+←"),
	"Forward" : create_keybind("+", "Alt+→"),

	"Select/deselect item under cursor" : create_keybind("Del"),
	"Group select" : create_keybind("Shift+.", "Del"),

	"Select all items" : create_keybind("*", "^a"),
	"Deselect all items" : create_keybind("^d"),

	"Open file/directory under cursor" : create_keybind("Enter"),
	"Group open all selected items directly" : create_keybind("Insert"),
	
	"Help" : create_keybind("F1"),
	"Reverse sort order" : create_keybind("F4"),
	
	"Quit" : create_keybind("F10")
})

