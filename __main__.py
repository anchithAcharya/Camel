import os
from sys import argv
from .frontend import cml_wsl
from .backend.__main__ import main
from .frontend.settings_wsl import ROOT

if "-r" in argv:
	recalculate = True
	argv.remove("-r")

else:
	recalculate = False

if len(argv) == 1:
	argv.append(ROOT)

path = argv[1]

if not os.path.isdir(path):
	exit(path + " is not a valid directory.")

new_path, db_path = main(path, recalculate)

os.environ.setdefault('ESCDELAY', '100')
cml_wsl.start(new_path, db_path)