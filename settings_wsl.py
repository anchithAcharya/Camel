MIN_DIMS = (24, 97)
GO_ABOVE_ROOT = True
ROOT = '/mnt/d/Media'
SHOW_HIDDEN_FILES = False
SHOW_ONLY_MEDIA_FILES = True
END_SELECTS_LAST_ITEM = False
SELECT_PREV_DIR_ON_CD_UP = True
MEDIA_PLAYER_PATH = "/mnt/p/VLC/vlc.exe"

class EXT:
	audio = ['.3ga','.aac','.cda','.flac','.m4a','.mp3','.ogg','.opus','.pls','.snd','.wma','.zab']
	video = ['.264','.3gp','.avi','.dash','.dvr','.m2t','.m2ts','.m4v','.mkv','.mov','.mp4','.mpg','.mts','.ogv','.rec','.rmvb','.ts','.vob','.webm','.wmv']
	subs = ['.lrc','.srt','.sub']

KEYBINDS = {
	'↑': "Navigate up",
	'↓': "Navigate down",
	'←': "Navigate left",
	'→': "Navigate right",

	'^PgUp': "Scroll up",
	'^PgDn': "Scroll down",

	'PgUp': "Page up",
	'PgDn': "Page down",

	'Home': "Navigate to first item",
	'End': "Navigate to bottom-most item",


	'.': "Select item under cursor",

	'^A': "Select all items",
	'^D': "Deselect all items",

	'Enter/O': "Open file/directory under cursor",
	'^O': "Group open all selected items directly",
	
	'Alt+↑': "Move up by one directory",

	'F1': "Help",
	'F4': "Reverse sort order",
	'F10': "Quit"
}