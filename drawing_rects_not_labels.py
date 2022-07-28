from abc import ABC, abstractmethod
from time import sleep
import tkinter as tk
import ss_classes as ss



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
    # GridBlock.undraw_all()
    canvas.delete('all')
    GridBlock.create_all(canvas,grid)
    GridBlock.draw_all()

class Block (ABC):

    @abstractmethod
    def draw(self) -> None:
        pass

    @abstractmethod
    def undraw(self) -> None:
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

    def __init__(self, canvas: tk.Canvas, screen:ss.Screen, **config):
        self.canvas = canvas
        self.screen = screen
        self.settings = config
        self.compute()
        GridBlock.grid_blocks.append(self)

    def compute(self):
        self.canvas.update()
        canvas_height = self.canvas.winfo_height()
        canvas_width = self.canvas.winfo_width()

        self.x0 = (self.screen.x - self.screen.width/2) * canvas_width 
        self.y0 = (1-self.screen.y - self.screen.height/2) * canvas_height 
        self.x1 = self.x0 + self.screen.width * canvas_width 
        self.y1 = self.y0 + self.screen.height * canvas_height

    def draw(self):
        self.rect = self.canvas.create_rectangle(self.x0,self.y0,self.x1,self.y1,**self.settings)

    def undraw(self,*opt):
        self.canvas.delete(self.rect)
        GridBlock.grid_blocks.remove(self)

    def config(self, **opts):
        self.canvas.itemconfig(self.rect,**opts)
        for key, value in opts.items():
            self.settings[key] = value

    @staticmethod
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

    @staticmethod
    def draw_all():
    
        for block in GridBlock.grid_blocks:
            block.compute()
    
        for block in GridBlock.grid_blocks:
            block.draw()

    @staticmethod
    def undraw_all():
        if len(GridBlock.grid_blocks) > 0:
            for block in GridBlock.grid_blocks:
                block.undraw()
                return
        print("No blocks have been drawn.")

    @staticmethod
    def create_all(canvas: tk.Canvas, grid: ss.Grid, **config):

        GridBlock.grid_blocks.clear()
        
        grid_block_screens = GridBlock.blocks_from_grid(grid)

        for row in grid_block_screens:
            for block in row:
                coords = f'{block.colx},{block.coly}'
                block = GridBlock(canvas,block,fill="#40798C",tag=coords,outline="#1e1e1e")

    @staticmethod
    def config_all(**opts):
        list = GridBlock.grid_blocks
        for block in list:
            block.config(**opts)

    @staticmethod
    def bind_all(event:str, callable):
        for block in GridBlock.grid_blocks:
            block.bind(event, callable)
        ...
    
    def get_property(self, *opts):
        for opt in opts:
            return self.canvas.itemcget(self.rect,opt)
    
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



button = tk.Button(root,text="Make grid wider",command=lambda: global_set(ss_grid, canvas, width=700, cols=4, rows=2))
button.pack(pady=10)

GridBlock.create_all(canvas,ss_grid)
GridBlock.draw_all()

# rect1 = GridBlock(canvas, ss.Screen(ss_grid,6,6,1,1), fill="yellow")
# rect1.draw()




print_coords = tk.StringVar(value="Hello")

def update_coords_first(event):
    print_coords.set(canvas.gettags("current")[0])
    GridBlock.bind_all("<ButtonRelease-1>",update_coords_second)

def update_coords_second(event):
    print_coords.set(canvas.gettags("current")[0])
    GridBlock.bind_all("<Button-1>",update_coords_first)

GridBlock.bind_all("<Button-1>",update_coords_first)


coords_label = tk.Label(root,textvariable=print_coords)
coords_label.pack(ipady=10)

root.mainloop()

