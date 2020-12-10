import os
from sys import argv
from .frontend import cml_wsl
from .backend import register
from .frontend.settings_wsl import ROOT

os.chdir(argv[1])

if len(argv) == 2:
	argv.append(ROOT)

else:
	argv[2] = os.path.abspath(argv[2])
	
	if not os.path.isdir(argv[2]):
		exit(argv[2] + " is not a valid directory.")

path = argv[2]

new_path = register.reg(path)

os.environ.setdefault('ESCDELAY', '100')
cml_wsl.start(new_path)