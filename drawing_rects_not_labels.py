from abc import ABC, abstractmethod
import tkinter as tk
import ss_classes as ss

def blocks_from_grid(grid: ss.Grid) -> list[list[ss.Screen]]:
    """
    The preview grid is just a bunch of Screens that are 1x1 in size.
    Every time a change to the grid is made, we have to recreate all of these screens
    to pass to the renderer.
    """
    grid_blocks = []

    for row in range(grid.rows):
        grid_blocks_row = []
        for col in range(grid.cols):
            block = ss.Screen(grid,1,1,col+1,row+1)
            grid_blocks_row.append(block)
        grid_blocks.append(grid_blocks_row)
    
    return grid_blocks

def global_set(grid: ss.Grid, canvas: tk.Canvas, **kwargs: dict[str,int]) -> None:
    if 'width' in kwargs:
        grid.canvas.width = kwargs['width']
        canvas.configure(width=kwargs['width'])
    if 'height' in kwargs:
        grid.canvas.height = kwargs['height']
        canvas.configure(height=kwargs['height'])

    

    if 'top' in kwargs:
        grid.margin.top = kwargs['top']
    if 'left' in kwargs:
        grid.margin.left = kwargs['left']
    if 'bottom' in kwargs:
        grid.margin.bottom = kwargs['bottom']
    if 'right' in kwargs:
        grid.margin.right = kwargs['right']

    if 'cols' in kwargs:
        grid.cols = kwargs['cols']
    if 'rows' in kwargs:
        grid.rows = kwargs['rows']
    if 'gutter' in kwargs:
        grid.gutter = kwargs['gutter']

    # redraw the rectangles
    GridBlock.redraw_all()

class Block (ABC):
    @abstractmethod
    def delete(self) -> None:
        pass

    @abstractmethod
    def config(self, **opts) -> None:
        pass

    @abstractmethod
    def bind(self, event:str, callable) -> None:
        pass

class ScreenBlock(Block):
    screen_blocks = []

    @staticmethod
    def redraw_all():
        pass

class GridBlock(Block):
    grid_blocks = []

    @staticmethod
    def redraw_all():
        for grid in GridBlock.grid_blocks:
            grid.delete()

            grid.canvas.update()
            canvas_height = canvas.winfo_height()
            canvas_width = canvas.winfo_width()

            x0 = (grid.screen.x - grid.screen.width/2) * canvas_width 
            y0 = (1-grid.screen.y - grid.screen.height/2) * canvas_height 
            x1 = x0 + grid.screen.width * canvas_width 
            y1 = y0 + grid.screen.height * canvas_height 

            grid.rect = canvas.create_rectangle(x0,y0,x1,y1,**grid.settings)
            # grid.config(**grid.settings)

    @staticmethod
    def config_all(**opts):
        list = GridBlock.grid_blocks
        for block in list:
            block.config(**opts)

    def __init__(self, canvas: tk.Canvas, screen:ss.Screen, **config):
        
        canvas.update()
        canvas_height = canvas.winfo_height()
        canvas_width = canvas.winfo_width()

        x0 = (screen.x - screen.width/2) * canvas_width 
        y0 = (1-screen.y - screen.height/2) * canvas_height 
        x1 = x0 + screen.width * canvas_width 
        y1 = y0 + screen.height * canvas_height 

        self.rect = canvas.create_rectangle(x0,y0,x1,y1)
        self.canvas = canvas

        self.screen = screen

        self.settings: dict = {}
        self.config(**config)

        GridBlock.grid_blocks.append(self)

    def get_property(self, *opts):
        for opt in opts:
            return self.canvas.itemcget(self.rect,opt)
    
    def config(self, **opts):
        self.canvas.itemconfig(self.rect,**opts)
        for key, value in opts.items():
            self.settings[key] = value

    def delete(self,*opt):
        self.canvas.delete(self.rect)

    @property  
    def tag(self):
        return self.get_property("tag")

    @tag.setter
    def tag(self, tag: str):
        self.config(tag=tag)

    def bind(self, event:str, callable) -> None:          
        self.canvas.tag_bind(self.tag,sequence=event,func=callable)
        


root = tk.Tk()

ss_canvas = ss.Canvas()
ss_canvas.width, ss_canvas.height = 500,500

ss_margin = ss.Margin(ss_canvas)
ss_margin.top, ss_margin.left, ss_margin.bottom, ss_margin.right = 15,15,15,15
ss_grid = ss.Grid(ss_canvas,ss_margin)
ss_grid.cols, ss_grid.rows = 12,6
ss_grid.gutter = 15


canvas = tk.Canvas(root, width=500,height=500,background="#1e1e1e")
canvas.pack(padx=20,pady=20)

# rect1 = GridBlock(canvas, ss.Screen(ss_grid,6,6,1,1), fill = "white", activefill='red')
# rect2 = GridBlock(canvas, ss.Screen(ss_grid,6,6,7,1), fill = "white", activefill='red')

# rect2.config(fill="blue")

# button = tk.Button(root,text="Make grid wider",command=lambda: global_set(ss_grid, canvas, width=700, cols=14))
# button.pack(pady=20)

# button2 = tk.Button(root,text="Make grid even wider",command=lambda: global_set(ss_grid, canvas, width=900, cols=12))
# button2.pack(pady=20)

# rect1.bind("<Button-2>",rect1.delete)

grid_block_screens = blocks_from_grid(ss_grid)
grid_blocks = []

for row in grid_block_screens:
    row_of_blocks = []
    for block in row:
        grid_block = GridBlock(canvas,block,fill="#40798C")
        row_of_blocks.append(grid_block)
    grid_blocks.append(row_of_blocks)





# global_set(ss_grid, canvas, width=700)






root.mainloop()

