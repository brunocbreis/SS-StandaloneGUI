from dataclasses import dataclass, field
import numpy as np

@dataclass
class Canvas:
    """Canvas object. Sizes defined and returned in pixels."""
    _children: list = field(default_factory=list, repr=False, init=False)

    def __post_init__(self):
        self._width_px = 1920
        self._height_px = 1080

    def __str__(self) -> str:
        title = 'CANVAS\n'
        message = f"Width: {self.width}px\tHeight: {self.height}px\n"
        return title + message

    @property
    def width(self) -> int:
        return self._width_px

    @width.setter # will call children
    def width(self, width: int):
        self._width_px = width
        for child in self._children:
            child()

    @property
    def height(self) -> int:
        return self._height_px

    @height.setter # will call children
    def height(self, height: int):
        self._height_px = height
        for child in self._children:
            child()

    def give_birth(self, child):
        self._children.append(child)

class MarginsExceedCanvas(Exception):
    """Error for when margins are too big. Should be called when changin resolution or margins"""
    pass

class Margin:
    """Margin object. Values defined in pixels but returned normalized."""

    def __init__(self, canvas: Canvas) -> None:     
        self.canvas = canvas  
        self.canvas.give_birth(self.compute)
        self._top_px = 0
        self._left_px = 0
        self._bottom_px = 0
        self._right_px = 0
        self._top = 0.0
        self._left = 0.0
        self._bottom = 0.0
        self._right = 0.0

    def __str__(self) -> str:
        title = 'MARGIN\n'
        message = f'Top: {self._top_px}px\tBottom: {self._right_px}px\nLeft: {self._left_px}px\tRight: {self._right_px}px\n'
        return title + message

    @property
    def top(self) -> int:
        '''Returns a normalized value. For pixel value, use _px'''
        return self._top

    @top.setter
    def top(self, value: int):
        if self._bottom_px + value > self.canvas.height:
            print("Margin values exceed canvas dimensions.")
            raise MarginsExceedCanvas
        self._top_px = value
        self._top = value / self.canvas.height

    @property
    def bottom(self) -> int:
        '''Returns a normalized value. For pixel value, use _px'''
        return self._bottom

    @bottom.setter
    def bottom(self, value: int):
        if self._top_px + value > self.canvas.height:
            print("Margin values exceed canvas dimensions.")
            raise MarginsExceedCanvas
        self._bottom_px = value
        self._bottom = value / self.canvas.height

    @property
    def left(self) -> int:
        '''Returns a normalized value. For pixel value, use _px'''
        return self._left

    @left.setter
    def left(self, value: int):
        if self._right_px + value > self.canvas.width:
            print("Margin values exceed canvas dimensions.")
            raise MarginsExceedCanvas
        self._left_px = value
        self._left = value / self.canvas.width

    @property
    def right(self) -> int:
        '''Returns a normalized value. For pixel value, use _px'''
        return self._right

    @right.setter
    def right(self, value: int):
        if self._left_px + value > self.canvas.width:
            print("Margin values exceed canvas dimensions.")
            raise MarginsExceedCanvas
        self._right_px = value
        self._right = value / self.canvas.width

    def compute(self):
        '''Recomputes normalized values for when something has changed in a parent class.'''
        self.top = self._top_px
        self.left = self._left_px
        self.bottom = self._bottom_px
        self.right = self._right_px
          
class Grid:
    def __init__(self, canvas: Canvas, margin: Margin) -> None:
        self.canvas = canvas
        self.margin = margin
        self._cols = 12
        self._rows = 6
        self._gutter_px = 0
        self._gutter_w = 0.0
        self._gutter_h = 0.0
        self.canvas.give_birth(self.compute)

    def __str__(self) -> str:
        title = 'GRID\n'
        message = f'Cols: {self.cols}\tRows: {self.rows}\nGutter: {self._gutter_px}px\n'
        return title + message

    @property
    def cols(self) -> int:
        '''Number of grid columns.'''
        return self._cols

    @cols.setter
    def cols(self, value: int):
        self._cols = value

    @property
    def rows(self) -> int:
        '''Number of grid rows.'''
        return self._rows

    @rows.setter
    def rows(self, value: int):
        self._rows = value

    @property
    def gutter(self) -> float:
        '''Returns Gutter values (w,h), normalized.'''
        return (self._gutter_w, self._gutter_h)

    @gutter.setter
    def gutter(self, value: int):
        self._gutter_px = value
        self._gutter_w = value / self.canvas.width
        self._gutter_h = value / self.canvas.height

    @property
    def col_width(self) -> float:
        '''Returns Column width, normalized.'''
        mg = self.margin
        width = (1 - mg.left - mg.right -
                (self.cols-1) * self.gutter[0]) / self.cols
        return width

    @property
    def row_height(self) -> float:
        '''Returns Row height, normalized.'''
        mg = self.margin
        height = (1 - mg.top - mg.bottom -
                (self.rows-1) * self.gutter[1]) / self.rows
        return height 

    @property
    def matrix(self) -> list:
        matrix = []
        for row in range(self.rows):
            x = row * self.cols + 1
            matrix_row = [col + x for col in range(self.cols)]
            matrix.append(matrix_row)
        return np.array(matrix)

    def compute(self) -> None: 
        '''Recomputes normalized values for when something has changed in parent classes.'''
        self.gutter = self._gutter_px

@dataclass
class Screen:
    grid: Grid
    colspan: int
    rowspan: int
    colx: int
    coly: int

    def __post_init__(self):
        self._has_been_computed = False

    @property
    def width(self) -> float:
        '''Returns screen width, normalized.'''
        grid = self.grid
        width = grid.col_width * self.colspan + (self.colspan-1) * grid.gutter[0]
        return width

    @property
    def height(self) -> float:
        '''Returns screen height, normalized.'''
        grid = self.grid
        height = grid.row_height * self.rowspan + (self.rowspan-1) * grid.gutter[1]
        return height

    @property
    def x(self):
        '''Returns screen X position, normalized.'''
        grid = self.grid
        margin = grid.margin
        x = self.width/2 + margin.left + (self.colx - 1) * (grid.col_width + grid.gutter[0])
        return x

    @property
    def y(self):
        '''Returns screen Y position, normalized.'''
        grid = self.grid
        margin = grid.margin
        y = self.height/2 + margin.bottom + (self.coly - 1) * (grid.row_height + grid.gutter[1])
        return y

    @property
    def size(self):
        '''Returns screen size, normalized.'''
        return max(self.width, self.height)

    @staticmethod
    def create_from_coords(grid: Grid, point1: int, point2: int):
        matrix = grid.matrix
        p1 = min(point1,point2)
        p2 = max(point1, point2)
        n = 1
        for list in matrix:
            if p2 in list:
                colspan = list.index(p2) + 2 - p1
                rowspan = n
            n +=1
        colx = p1
        i = 1
        for list in matrix:
            if p1 in list:
                coly = i
            i += 1
        return Screen(grid,colspan,rowspan,colx,coly)

    # SIMPLIFIES THE CALLING, COMPUTES ON THE GO    
    def get_values(self) -> dict:
        values = {
            "Width": self.width,
            "Height": self.height,
            "Center.X": self.x,
            "Center.Y": self.y,
            "Size": self.size
        }
        return values


def test():
    canvas = Canvas()
    canvas.width = 500
    canvas.height = 500
    margin = Margin(canvas)
    grid = Grid(canvas=canvas,margin=margin)
    screens = [
        Screen(
            grid = grid,
            colspan= 6,
            rowspan= 6,
            colx = 1,
            coly = 1
        ),
        Screen(
            grid = grid,
            colspan= 6,
            rowspan= 6,
            colx = 7,
            coly = 1
        )
    ]

    grid.cols = 5
    grid.rows = 3
    print(grid.matrix)

if __name__ == "__main__":
    test()