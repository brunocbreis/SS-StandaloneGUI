from abc import ABC, abstractmethod
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
    settings = {}

    def __init__(self, canvas: tk.Canvas, grid_cell:ss.GridCell, **config):
        self.canvas = canvas
        self.grid_cell = grid_cell

        if grid_cell.index == 1:
            for key, value in config.items():
                self.settings[key] = value

        self.compute()
        GridBlock.grid_blocks.append(self)

    def compute(self):
        self.canvas.update()
        canvas_height = self.canvas.winfo_height()
        canvas_width = self.canvas.winfo_width()
        cell = self.grid_cell

        self.x0 = (cell.x - cell.width/2) * canvas_width 
        self.y0 = (1-cell.y - cell.height/2) * canvas_height 
        self.x1 = self.x0 + cell.width * canvas_width 
        self.y1 = self.y0 + cell.height * canvas_height

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
    def blocks_from_grid(grid: ss.Grid) -> list[ss.GridCell]:
        return ss.GridCell.generate_all(grid)

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
        # removes all created grid blocks from class list
        GridBlock.grid_blocks.clear()

        # creates grid cells from provided grid
        grid_block_screens = GridBlock.blocks_from_grid(grid)

        # initializes grid block from generated cells
        for cell in grid_block_screens:
            # coords = f'{block.colx},{block.coly}'
            grid_block = GridBlock(canvas,cell,**config)
            grid_block.cell = cell

    @staticmethod
    def config_all(**opts):
        for key, value in opts:
            GridBlock.settings[key] = value
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




def main():
    root = tk.Tk()

    ss_canvas = ss.Canvas((500,500))
    ss_margin = ss.Margin(ss_canvas,15,gutter=15)
    ss_grid = ss.Grid(ss_canvas,ss_margin,(12,6))



    canvas = tk.Canvas(root, width=500,height=500,background="#1e1e1e")
    canvas.pack(padx=20,pady=20)



    button = tk.Button(root,text="Make grid wider",command=lambda: global_set(ss_grid, canvas, width=700, cols=4, rows=2))
    button.pack(pady=10)

    GridBlock.create_all(canvas,ss_grid,fill="#40798C",activefill="#2C5360", outline="#1e1e1e")
    GridBlock.draw_all()






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


    x, y = None, None
    def cool_design(event):
        global x, y
        kill_xy()
        
        dashes = [3, 2]
        x = canvas.create_line(event.x, 0, event.x, 1000, dash=dashes, tags='no')
        y = canvas.create_line(0, event.y, 1000, event.y, dash=dashes, tags='no')
        canvas.tag_raise(x, y)
        
    def kill_xy(event=None):
        canvas.delete('no')

    canvas.bind('<Motion>', cool_design, '+')

    root.mainloop()

if __name__ == "__main__":
    main()