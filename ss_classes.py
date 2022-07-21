from dataclasses import dataclass

@dataclass
class Canvas:
    """Defines the canvas size in pixels"""
    width: int = 1920
    height: int = 1080

    def set_resolution(self, width: int = None, height: int = None):
        if width is int:
            self.width = width
        if height is int:
            self.height = height

@dataclass(slots=True)
class Margin:
    """Margin object. Values defined in pixels"""
    top: int = 0
    left: int = 0
    bottom: int = 0
    right: int = 0

    def set_margins(self, top: int, left: int, bottom: int, right: int):
        if top is not int or left is not int or bottom is not int or right is not int:
            raise "Please only use integer values"
            return
        self.top = top
        self.left = left
        self.bottom = bottom
        self.right = right
          
@dataclass
class Grid:
    canvas: Canvas
    cols: int = 12
    rows: int = 6
    margin: Margin = Margin(0,0,0,0)
    gutter: int = 0

    def __post_init__(self):
        self._has_been_computed = False

    def compute_values(self):
        canvas = self.canvas
        margin = self.margin
        self.col_width = (canvas.width - 
                             margin.left - 
                             margin.right -
                             (self.cols-1) * self.gutter) / self.cols
        self.row_height = (canvas.height - 
                             margin.top - 
                             margin.bottom -
                             (self.rows-1) * self.gutter) / self.rows
        self._has_been_computed = True

@dataclass
class Screen:
    grid: Grid
    colspan: int
    rowspan: int
    colx: int
    coly: int

    def __post_init__(self):
        self._has_been_computed = False

    def compute_values(self, update_grid = True):
        
        if update_grid: 
            self.grid.compute_values()

        if (not self.grid._has_been_computed):
            print("Grid values have to be computed first.")
            return False

        grid = self.grid
        margin = grid.margin
        
        width = grid.col_width * self.colspan + (self.colspan-1) * grid.gutter
        height = grid.row_height * self.rowspan + (self.rowspan-1) * grid.gutter
        x = width/2 + margin.left + (self.colx - 1) * (grid.col_width + grid.gutter)
        y = height/2 + margin.bottom + (self.coly - 1) * (grid.row_height + grid.gutter)
        
        self.width = width / grid.canvas.width
        self.height = height / grid.canvas.height
        self.x = x / grid.canvas.width
        self.y = y / grid.canvas.height
        
        self.size = max(self.width,self.height)

        self._has_been_computed = True

    def get_values(self) -> list:
        if not self._has_been_computed:
            print("Values have not yet been computed.")
            return
        values = {
            "Width": self.width,
            "Height": self.height,
            "Center.X": self.x,
            "Center.Y": self.y,
            "Size": self.size
        }
        # print(values)
        # return [*values.values()]
        return values