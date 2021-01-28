from .keybinds_wsl import KEYBINDS

MIN_DIMS = (55, 110)
# ROOT = "/home/anchith/media"
DATABASE_DIR = "/home/anchith/cml/backend/test/databases/"
ORGANISED_DIR = "/home/anchith/cml/backend/test/organised/"
STRICT_TYPE_CHECK_SEARCH = True
KEYBIND_IN_USE = KEYBINDS[1]
DEFAULT_MARQUEE_LEN = 20
UNIX_STYLE_LIST_ORDER = False
END_SELECTS_LAST_ITEM = False
SELECT_PREV_DIR_ON_CD_UP = True
MEDIA_PLAYER_PATH = "/mnt/p/VLC/vlc.exe"
SHOW_INFO_PANEL = False		# info panel hidden in the beginning

EXT = {
	"audio" : ('.3ga','.aac','.cda','.flac','.m4a','.mp3','.ogg','.opus','.pls','.snd','.wma','.zab'),
	"video" : ('.264','.3gp','.avi','.dash','.dvr','.m2t','.m2ts','.m4v','.mkv','.mov','.mp4','.mpg','.mts','.ogv','.rec','.rmvb','.ts','.vob','.webm','.wmv'),
	"subtitles" : ('.lrc','.srt','.sub')
}
