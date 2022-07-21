from ss_classes import *

##### CREATE CANVAS -------------------------------
canvas = Canvas()


##### CREATE MARGINS -----------------------------
mg_size = 200
margin = Margin(mg_size,mg_size,mg_size,mg_size)



##### CREATE GRID   -----------------------------
grid = Grid(
    canvas = canvas,
    margin = margin,
    gutter = 25
)

##### CREATE SCREENS  ---------------------------
screens = [
    Screen(grid,4,6,1,1),
    Screen(grid,4,6,5,1),
    Screen(grid,4,6,9,1)
]


##### COMPUTE VALUES --------------------------
grid.compute_values()
for screen in screens:
    screen.compute_values(update_grid=False)

screen_values = []
for screen in screens:
    screen_value = screen.get_values()
    screen_values.append(screen_value)