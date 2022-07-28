import pyperclip
from ss_classes import Canvas, Margin, Grid, Screen
import fusion_tool_generator as fu

def main():

    ##### CREATE CANVAS -------------------------------
    canvas = Canvas()
    canvas.width = 500
    canvas.height = 500

    ##### CREATE MARGINS -----------------------------
    mg_size = 15
    margin = Margin(canvas)
    margin.top = margin.bottom = margin.left = margin.right = mg_size

    ##### CREATE GRID   -----------------------------
    grid = Grid(
        canvas = canvas,
        margin = margin
    )
    grid.gutter = 5

    ##### CREATE SCREENS  ---------------------------
    screens = [
        Screen.create_from_coords(grid,1,64),
        Screen.create_from_coords(grid,5,68),
        Screen(grid,4,3,9,1),
        Screen(grid,4,3,9,4)
    ]

    print(screens[0].x,1-screens[0].y,screens[0].width, screens[0].height)
    print(screens[0])

    ##### RETURN VALUES -------------------------
    screen_values = []
    for screen in screens:
        screen_value = screen.compute()
        screen_values.append(screen_value)

    return screen_values
    # ##### RENDER OUTPUT -----------------------
    # fusion_output = fu.render_fusion_output(screen_values, canvas.resolution, True)
    # pyperclip.copy(fusion_output)

    # ##### SAVE PRESET ---------------------------
    # want_to_save = input("Choose a name for your new preset. Or press ENTER to leave without saving.\n")

    # if want_to_save:
    #     fu.save_preset_for_fusion('presets',fusion_output,want_to_save)
        
        
screen_values = main()