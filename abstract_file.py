import ss_classes as ss

# THIS IS A BLUEPRINT FOR FUTURE IMPLEMENTATIONS AND STRUCTURE OF THE GUI APP

# What the User will be able to do


#  with the Grid...
def edit_grid():
    ...

def reset_grid_to_default():
    ...


# with Screens...
def create_screen():
    ...

def edit_screen():
    ...

def rename_screen():
    ...

def delete_screen():
    ...


# Transformations
def flip_horizontal(screens: list[ss.Screen]) -> None: # GRID (to children) || depends on screen setter methods
    '''flips screen layout horizontally'''
    for screen in screens:
        screen.row = screen.grid.cols - screen.row
        screen.compute() # or implement setters so that it computes automatically
        ...
    ...

def flip_vertical(screens: list[ss.Screen]) -> None: # GRID (to children)
    '''flips screen layout vertically'''
    for screen in screens:
        screen.col = screen.grid.rows - screen.col
        screen.compute()
    ...

def rotate_grid(): # clockwise, clounterclockwise
    '''affects grid and screen layout'''
    ...

# Exporting
def export_to_fusion(): # to clipboard
    ...

def save_preset(): # saves both a splitscreener .json file and a .setting file
    ...

# Importing
def load_presets(): # loads grid and/or screen presets
    ...


# Config
def save_defaults(): # creates a new default
    ...

def reset_defaults(): # resets to factory defaults
    ...







#################

# root.update()
# winfo_rootx() and winfo_rooty() return the coordinates relative to the screen's upper left corner. --> for the canvas position
# winfo_x and winfo_y return the coordinates of a window relative to its parent. --> for the widgets relative to the canvas