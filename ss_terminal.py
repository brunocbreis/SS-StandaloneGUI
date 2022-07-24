from operator import indexOf
from ss_classes import Canvas, Margin, Grid, Screen
import ss_user_input_functions as user
from ss_generator import render_fusion_output, save_preset
from pickle import load
from os import listdir
from os.path import join
from time import sleep


# Load defaults.
input('\nWelcome to SplitScreener. Press [ENTER] start.')

def load_defaults(defaults_directory: str) -> tuple[str]:
    defaults_files = listdir(defaults_directory)
    defaults_files.sort()

    defaults = []
    for file in defaults_files:
        with open(join('defaults',file),'rb') as file:
            dict = load(file)
            defaults.append(dict)

    canvas_defaults, grid_defaults, margin_defaults = [default for default in defaults]
    return (canvas_defaults, grid_defaults, margin_defaults)

canvas_defaults, grid_defaults, margin_defaults = load_defaults('defaults')


# Setting up the Canvas and the Grid.
canvas = Canvas()
canvas.width, canvas.height = [canvas_defaults[key] for key in [*canvas_defaults]]

margin = Margin(canvas)
margin.top, margin.left, margin.bottom, margin.right = [margin_defaults[key] for key in [*margin_defaults]]

grid = Grid(canvas, margin)
grid.cols, grid.rows, grid.gutter = [grid_defaults[key] for key in [*grid_defaults]]

print("\n\nDEFAULT SETTINGS\n")
print(canvas,margin,grid, sep='\n')


# User customizes setup.
wants_to_customize = user.ask_if_custom_setup() 
using_defaults = not wants_to_customize

while wants_to_customize:
    user_choice = user.choose_custom_setup()
    print(f'Enter your custom {user_choice.title()} settings below.')
    if user_choice == 'canvas':
        custom_values = user.customize_canvas()
        canvas.width, canvas.height = [value for value in custom_values]

    if user_choice == 'margin':
        custom_values = user.customize_margin()
        margin.top, margin.left, margin.bottom, margin.right = [value for value in custom_values]
    
    if user_choice == 'grid':
        custom_values = user.customize_grid()
        grid.cols, grid.rows, grid.gutter = [value for value in custom_values]
    
    wants_to_customize = user.ask_if_custom_setup(False)

if not using_defaults:
    print(canvas,margin,grid, sep='\n')

input("Press [ENTER] to continue.")


# User creates screens.
screens = []

input("\nTime to set up your SplitScreener Screens! [ENTER]")

input("\nFor each new Screen, you'll be asked to provide 4 values. [ENTER]")

print("\nWIDTH (measured in columns), HEIGHT (measured in rows),")
print(f"X POSITION (1 is the leftmost column, {grid.cols} is the rightmost column),")
input(f"and Y POSITION (1 being the top row, {grid.rows} being the bottom row.\t[ENTER]")

input("\nWhen you're ready to start, press [ENTER].")

wants_more_screens = True
while wants_more_screens:
    print(f"\nSCREEN {len(screens) + 1}")
    cv = user.screen_config()
    screen = Screen(
        grid = grid,
        colspan=cv[0],
        rowspan=cv[1],
        colx=cv[2],
        coly=cv[3]
        )
    screens.append(screen)
    wants_more_screens = user.ask_if_more_screens()

input(f"You have created {len(screens)} Screen{'s' if len(screens) > 1 else ''}. [ENTER]")
print("\nComputing SplitScreener values...")

screen_values = []
for screen in screens:
    screen_value = screen.get_values()
    screen_values.append(screen_value)

sleep(1)

# SplitScreener renders Fusion output
input("Done! Press [ENTER] to render Fusion output.")

fusion_output = render_fusion_output(screen_values, canvas.resolution)


# Users save presets
want_to_save = input("Choose a name for your new preset. Or press [ENTER] to leave without saving.\n> ")

if want_to_save:
    save_preset('presets',fusion_output,want_to_save)
    print(f"\nPreset {want_to_save} saved in the Presets folder.\n\n")
else:
    print("\n\nAll right. Paste your result in DaVinci Resolve Fusion and you're good to go.\n")

print("Have fun SplitScreening!\n")