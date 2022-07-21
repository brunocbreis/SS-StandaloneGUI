from ss_classes import *

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
    Screen(grid,4,6,1,1),
    Screen(grid,4,6,5,1),
    Screen(grid,4,3,9,1),
    Screen(grid,4,3,9,4)
]



##### RETURN VALUES -------------------------
canvas_values = {
    'Width': canvas.width,
    'Height': canvas.height
}

screen_values = []
for screen in screens:
    screen_value = screen.get_values()
    screen_values.append(screen_value)