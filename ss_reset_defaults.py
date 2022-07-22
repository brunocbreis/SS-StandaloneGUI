from pickle import dump
from os.path import join

def reset_defaults():

    defaults_dir = 'defaults'


    canvas_defaults = {
        'Width': 1920,
        'Height': 1080
    }
    canvas_defaults_file = 'canvas_defaults.pkl'
    with open(join(defaults_dir,canvas_defaults_file), 'wb') as file:
        dump(canvas_defaults, file)


    margin_defaults = {
        'top': 0,
        'left': 0,
        'bottom': 0,
        'right': 0
    }
    margin_defaults_file = 'margin_defaults.pkl'
    with open(join(defaults_dir, margin_defaults_file), 'wb') as file:
        dump(margin_defaults, file)


    grid_defaults = {
        'cols': 12,
        'rows': 6,
        'gutter': 0
    }
    grid_defaults_file = 'grid_defaults.pkl'
    with open(join(defaults_dir, grid_defaults_file), 'wb') as file:
        dump(grid_defaults, file)

if __name__ == '__main__':
    reset_defaults()