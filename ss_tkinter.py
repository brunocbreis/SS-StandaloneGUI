from turtle import Screen
import ss_classes as ss
from tkinter import *


# STATE OF BUTTONS ===========
def grid_state_1(widget: Widget):
    widget.bind("<Enter>", darker_color)
    widget.bind("<Leave>", regular_color)
    widget.bind("<Button-1>", selected_color)

def grid_state_2(widget: Widget):
    widget.unbind("<Leave>")
    widget.unbind("<Enter>")

def darker_color(event: Event):
    widget = event.widget
    widget.configure(bg = hover_color)

def regular_color(event: Event):
    widget = event.widget
    widget.configure(bg = original_color)

def selected_color(event: Event):
    widget = event.widget
    widget.configure(bg = click_color)
    grid_state_2(widget)

# RENDERING FUNCTIONS
# Computer generates graphics.
def remove_screens(group: list[Widget]):
    for widget in group:
        widget.place_forget()

def render_screen(root: Tk, screen: ss.Screen, color: str, group: list[Widget], append: bool = True) -> Widget:
    """Renders one label widget from a ss.Screen object and appends it to a group."""

    relx = screen.x - screen.width/2
    rely = screen.y + screen.height/2
    relw = screen.width
    relh = screen.height

    widget = Label(root, bg=color, bd=0, highlightthickness=0, relief='ridge')
    widget.place(relwidth=relw,relheight=relh, anchor=NW, relx=relx, rely=1-rely, bordermode='outside')
    
    if append:
        group.append(widget)
    return widget

def render_all_screens(root: Tk, group: list[ss.Screen]):
    for screen in group:
        render_screen(root, screen, "yellow", group, append=False)

def compute_preview_grid(grid: ss.Grid) -> list[ss.Screen]:
    grid_blocks = []

    for row in range(grid.rows):
        grid_blocks_row = []
        for col in range(grid.cols):
            block = ss.Screen(grid,1,1,col+1,row+1)
            grid_blocks_row.append(block)
        grid_blocks.append(grid_blocks_row)
    
    return grid_blocks

def render_preview_grid(root: Tk, group_of_widgets: list[Widget], group_of_screen_widgets: list[Widget], list_of_screens: list[ss.Screen], grid: ss.Grid):
    there_are_screens = False
    if len(group_of_widgets) > 0: #would mean no grid has been rendered
        remove_screens(group_of_widgets)
    if len(group_of_screen_widgets) > 0: #would mean no screens have been rendered
        there_are_screens = True
        remove_screens(group_of_screen_widgets)
    
    # Creating actual ss.Screen objects for each grid block
    grid_blocks = compute_preview_grid(grid)

    # Rendering the ss.Screens as Label widgets
    for screen_row in grid_blocks:
        for screen in screen_row:
            render_screen(root,screen,original_color,group_of_widgets)
            grid_state_1(group_of_widgets[-1])
            
    # Re-rendering screens on top of the grid 
    if there_are_screens:
        render_all_screens(root,list_of_screens)


# ADDING FUNCTIONS
# User sets parameters that change what is to be rendered.
def add_screen(root: Tk, group_of_screen_objects: list[ss.Screen], group_of_widgets: list[Widget]):
    """Creates a ss.Screen object and appends it to a group. Calls the render_screen function"""

    new_screen = ss.Screen(ss_grid, 6, 6, 1, 1)  #int(screen_size_entry.get())
    render_screen(root, new_screen, "yellow", group_of_widgets)
    group_of_screen_objects.append(new_screen)

def add_col(root: Tk, grid: ss.Grid, group_of_grid_widgets: list[Widget], group_of_screen_widgets: list[Widget], list_of_screens: list[ss.Screen]):
    grid.cols = grid.cols + 1
    remove_screens(group_of_screen_widgets)
    render_preview_grid(root, group_of_grid_widgets,group_of_screen_widgets,list_of_screens, grid)

def rem_col(root: Tk, grid: ss.Grid, group_of_grid_widgets: list[Widget], group_of_screen_widgets: list[Widget], list_of_screens: list[ss.Screen]):
    grid.cols = grid.cols - 1
    remove_screens(group_of_screen_widgets)
    render_preview_grid(root, group_of_grid_widgets,group_of_screen_widgets,list_of_screens, grid)




# =====================
grid_block_widgets = []
screen_widgets = []
list_of_ssscreens = []

# SPLIT SCREENER VARS ========
ss_canvas = ss.Canvas()
ss_canvas.width = 1920
ss_canvas.height = 1080
ss_margin = ss.Margin(ss_canvas)
ss_grid = ss.Grid(ss_canvas,ss_margin)

ss_margin.top, ss_margin.left, ss_margin.bottom, ss_margin.right, ss_grid.gutter = 40,40,40,40,40
ss_grid.cols = 12
ss_grid.rows = 6



# COLOR PALETTE =====================

hover_color = "#0000cc"
original_color = "#0000ff"
click_color = "#8888ff"


def main():

    root = Tk()

    #Dimensions
    x = 1440
    y = 900
    dim = {
        "x": x,
        "y": y,
        "screenx": root.winfo_screenwidth(),
        "screeny": root.winfo_screenheight(),
        "screenx_center": int(root.winfo_screenwidth()/2),
        "screeny_center": int(root.winfo_screenheight()/2),
    }

    #Root Window
    root.title('SplitScreener')
    root.geometry(f"{dim['x']}x{dim['y']}+{dim['screenx_center'] - int(dim['x']/2)}+{dim['screeny_center'] - int(dim['y']/2)}")
    root.resizable(False,False)
    root.configure(background = "#FFFFFF")


    canvas = Canvas(root, width = ss_canvas.width/2, height = ss_canvas.height/2, bg="#1e1e1e", bd=0, highlightthickness=0, relief='ridge')
    canvas.grid(padx=100, pady=80)

    # CREATES THE FICTIONAL GRID
    
        

    

    

        

    render_preview_grid(canvas, grid_block_widgets,screen_widgets,list_of_ssscreens, ss_grid)



    add_col_button = Button(text="Add Column", command=lambda: add_col(canvas, ss_grid,grid_block_widgets,screen_widgets,list_of_ssscreens))
    add_col_button.grid(row=2)
    rem_col_button = Button(text="Remove Column", command=lambda: rem_col(canvas, ss_grid,grid_block_widgets,screen_widgets,list_of_ssscreens))
    rem_col_button.grid(row=3)
    add_screen_button = Button(text="Add Screen", command=lambda: add_screen(canvas,list_of_ssscreens, screen_widgets))
    add_screen_button.grid(row=4)
    

    screen_size_entry = Entry(root,width=2)
    screen_size_entry.insert(0, "5")
    screen_size_entry.grid(row=5)



    

    
    # STATE1: never clicked.
    # STATE2: clicked on first widget

    
    
    
    
    
    
    
    root.mainloop()


if __name__ == '__main__':
    main()
