import json

def reset_defaults():
    """Creates default.json file with default values"""

    canvas_defaults = {
        'width': 1920,
        'height': 1080
    }

    margin_defaults = {
        'top': 15,
        'left': 15,
        'bottom': 15,
        'right': 15
    }

    grid_defaults = {
        'cols': 12,
        'rows': 6,
        'gutter': 15
    }

    defaults = {
        'canvas': canvas_defaults,
        'margin': margin_defaults,
        'grid': grid_defaults
    }

    # write file
    with open('defaults/defaults.json', 'w') as defaults_file:
        json.dump(defaults, defaults_file)

if __name__ == '__main__':
    reset_defaults()