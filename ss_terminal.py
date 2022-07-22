from ss_classes import *
from pickle import load
from os import listdir
from os.path import join
from pprint import pprint

print('Welcome to SplitScreener. Loading defaults...')

# Load defaults.
defaults_files = listdir('defaults')
defaults_files.sort()

defaults = []
for file in defaults_files:
    with open(join('defaults',file),'rb') as file:
        dict = load(file)
        defaults.append(dict)

canvas_defaults, grid_defaults, margin_defaults = [default for default in defaults]