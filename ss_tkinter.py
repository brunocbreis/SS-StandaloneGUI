from turtle import Screen
import ss_classes as ss
from tkinter import *



# GLOBAL VARIABLES AND LISTS ========================
grid_block_widgets = []
screen_widgets = []
list_of_ssscreens = []
coords = [1,1]


# SPLIT SCREENER VARS ========================
ss_canvas = ss.Canvas()
ss_canvas.width = 1920
ss_canvas.height = 1080

ss_margin = ss.Margin(ss_canvas)
ss_grid = ss.Grid(ss_canvas,ss_margin)

ss_margin.top, ss_margin.left, ss_margin.bottom, ss_margin.right, ss_grid.gutter = 40,40,40,40,40
ss_grid.cols = 12
ss_grid.rows = 6

# RENDERING FUNCTIONS ========================
# Computer generates graphics.
def delete_widgets(list_of_widgets: list[Widget]):
    for widget in list_of_widgets:
        widget.place_forget()
    

def widget_from_screen(root: Tk, screen: ss.Screen, color: str) -> Widget:
    """Creates a Label widget from an ss.Screen object and assigns the screen to it as a property."""

    widget = Label(root, bg=color, bd=0, highlightthickness=0, relief='ridge')
    widget.screen = screen
    widget.color = color

    return widget

def place_screen_widget(root: Tk, screen: ss.Screen, color: str, group: list[Widget], append: bool = True) -> Widget:
    """Renders one label widget from a ss.Screen object and appends it to a group."""

    relx = screen.x - screen.width/2
    rely = screen.y - screen.height/2
    relw = screen.width
    relh = screen.height

    widget = Label(root, bg=color, bd=0, highlightthickness=0, relief='ridge')
    widget.place(relwidth=relw,relheight=relh, anchor=NW, relx=relx, rely=rely, bordermode='outside')
    
    if append:
        group.append(widget)
    return widget

def render_all_screens(root: Tk, group: list[ss.Screen]):
    for screen in group:
        place_screen_widget(root, screen, "yellow", screen_widgets)

def create_grid_blocks() -> list[list[ss.Screen]]:
    """
    The preview grid is just a bunch of Screens that are 1x1 in size.
    Every time a change to the grid is made, we have to recreate all of these screens
    to pass to the renderer.
    """
    grid_blocks = []

    for row in range(ss_grid.rows):
        grid_blocks_row = []
        for col in range(ss_grid.cols):
            block = ss.Screen(ss_grid,1,1,col+1,row+1)
            grid_blocks_row.append(block)
        grid_blocks.append(grid_blocks_row)
    
    return grid_blocks

def refresh_grid(root: Tk):
    """
    Every time the user makes any change to the grid settings, 
    it must be re-rendered so that it previews correctly.
    """
    
    if len(grid_block_widgets) > 0: # would mean no grid has ever been rendered
        delete_widgets(grid_block_widgets)
    
    there_are_screens = False # assume the grid is empty
    if len(screen_widgets) > 0: # would mean no screens have been rendered
        there_are_screens = True
        
    
    # Creating actual ss.Screen objects for each grid block
    grid_blocks = create_grid_blocks()

    # Rendering the ss.Screen blocks as Label widgets
    for row_of_blocks_index in range(len(grid_blocks)):
        row = grid_blocks[row_of_blocks_index]

        for block_index in range(len(row)):
            block = row[block_index]
            widget = place_screen_widget(root,block,original_color,grid_block_widgets)
            widget.index = block_index+1 + row_of_blocks_index * len(row)
            grid_state_1(widget)
    
            
    # Re-rendering screens on top of the grid 
    if there_are_screens:
        delete_widgets(screen_widgets)
        render_all_screens(root,list_of_ssscreens)


# USER INTERACTION FUNCTIONS
# User sets parameters that change what is to be rendered.
def add_screen(root: Tk, coords: list[int,int] = coords):
    """Creates a ss.Screen object and appends it to a group. Calls the render_screen function"""
    print("Adding screen...")
    new_screen = ss.Screen.create_from_coords(ss_grid, *coords)  #int(screen_size_entry.get())
    print(new_screen)
    place_screen_widget(root, new_screen, "yellow", screen_widgets)
    list_of_ssscreens.append(new_screen)
    for block in grid_block_widgets:
        grid_state_1(block)

def add_cols(root: Tk, amount: int = 1):
    ss_grid.cols = ss_grid.cols + amount
    delete_widgets(screen_widgets)
    refresh_grid(root)

def register_first_coord(event: Event):
    del coords[0:2]
    coords.append(event.widget.index)
    event.widget.config(bg = click_color)

    for block in grid_block_widgets:
        grid_state_2(block)
    print(coords)

def register_second_coord(event: Event):

    for block in grid_block_widgets:
        pass

    event.widget.config(bg = click_color)
    coords.append(event.widget.index)
    print(coords)


# COLOR PALETTE =====================
hover_color = "#0000cc"
original_color = "#0000ff"
click_color = "#8888ff"

# STATE OF BUTTONS ===========
def grid_state_1(widget: Widget):
    widget.bind("<Enter>", darker_color)
    widget.bind("<Leave>", regular_color)
    widget.bind("<Button-1>", register_first_coord)

def grid_state_2(widget: Widget):
    widget.unbind("<Leave>")
    widget.unbind("<Enter>")
    widget.unbind("<Button-1>")
    widget.bind("<Button-1>", register_second_coord)

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



def main():

    root = Tk()

    # SETTING UP THE MAIN WINDOW ======================
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

    # RENDER GRID FOR THE FIRST TIME ====================
    refresh_grid(canvas)



    # ADDING SOME BUTTONS ======================
    add_col_button = Button(text="Add Column", command=lambda: add_cols(canvas))
    add_col_button.grid(row=2)
    rem_col_button = Button(text="Remove Column", command=lambda: add_cols(canvas, -1))
    rem_col_button.grid(row=3)
    add_screen_button = Button(text="Add Screen", command=lambda: add_screen(canvas, coords))
    add_screen_button.grid(row=4)
    clear_all_button = Button(text="Clear Screens", command=lambda: delete_widgets(screen_widgets))
    clear_all_button.grid(row=6)
    

    screen_size_entry = Entry(root,width=2)
    screen_size_entry.insert(0, "5")
    screen_size_entry.grid(row=5)



    

    
    # STATE1: never clicked
    # STATE2: clicked on first widget

    
    
    
    
    
    
    
    root.mainloop()


if __name__ == '__main__':
    main()
