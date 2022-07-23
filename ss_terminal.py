from ss_classes import Canvas, Margin, Grid, Screen
from pickle import load
from os import listdir
from os.path import join

print('Welcome to SplitScreener. Loading defaults...\n')

# Load defaults.
defaults_files = listdir('defaults')
defaults_files.sort()

defaults = []
for file in defaults_files:
    with open(join('defaults',file),'rb') as file:
        dict = load(file)
        defaults.append(dict)

canvas_defaults, grid_defaults, margin_defaults = [default for default in defaults]


# Setting up the Canvas and the Grid.
canvas = Canvas()
canvas.width = canvas_defaults['width']
canvas.height = canvas_defaults['height']

margin = Margin(canvas)
margin.top, margin.left, margin.bottom, margin.right = [margin_defaults[key] for key in [*margin_defaults]]

grid = Grid(canvas, margin)
grid.cols, grid.rows, grid.gutter = [grid_defaults[key] for key in [*grid_defaults]]

print(canvas,margin,grid, sep='\n')

input('Do you want to customize anything? ')
