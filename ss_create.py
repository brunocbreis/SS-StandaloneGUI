from ss_classes import Canvas, Margin, Grid, Screen
from ss_generator import render_fusion_output, save_preset

def main():

    ##### CREATE CANVAS -------------------------------
    canvas = Canvas()
    canvas.width = 1920
    canvas.height = 1080

    ##### CREATE MARGINS -----------------------------
    mg_size = 60
    margin = Margin(canvas)
    margin.top = margin.bottom = margin.left = margin.right = mg_size

    ##### CREATE GRID   -----------------------------
    grid = Grid(
        canvas = canvas,
        margin = margin
    )
    grid.gutter = 30

    ##### CREATE SCREENS  ---------------------------
    screens = [
        Screen.create_from_coords(grid,1,64),
        Screen.create_from_coords(grid,5,68),
        Screen(grid,4,3,9,1),
        Screen(grid,4,3,9,4)
    ]

    ##### RETURN VALUES -------------------------
    screen_values = []
    for screen in screens:
        screen_value = screen.get_values()
        screen_values.append(screen_value)


    ##### RENDER OUTPUT -----------------------
    fusion_output = render_fusion_output(screen_values, canvas.resolution)


    ##### SAVE PRESET ---------------------------
    want_to_save = input("Choose a name for your new preset. Or press ENTER to leave without saving.\n")

    if want_to_save:
        save_preset('presets',fusion_output,want_to_save)
        
if __name__ == "__main__":
    main()