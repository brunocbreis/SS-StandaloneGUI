from typing import Callable

# helper function for Screen classes
def get_coords(item, matrix: list[list]) -> tuple[int,int]:
  for i in range(len(matrix)):
    if item in matrix[i]:
      y = i
      x = matrix[i].index(item)
  return x+1, y+1


class Canvas:
    """Canvas object. Sizes defined and returned in pixels."""
    _children: list[Callable] = []

    def __init__(self, resolution: tuple[int,int] = (1920,1080)):
        self._width_px, self._height_px = resolution

    def __str__(self) -> str:
        title = 'CANVAS\n'
        message = f"Width: {self.width}px\tHeight: {self.height}px\n"
        return title + message

    def give_birth(self, function: Callable) -> None:
        self._children.append(function)

    @property
    def width(self) -> int:
        return self._width_px

    @width.setter # will call children
    def width(self, width: int):
        self.resolution = (width, self.height)

    @property
    def height(self) -> int:
        return self._height_px

    @height.setter # will call children
    def height(self, height: int):
        self.resolution = (self.width, height)

    @property
    def resolution(self) -> tuple[int]:
        return (self.width, self.height)

    @resolution.setter
    def resolution(self, values: tuple[int, int]):
        self._width_px, self._height_px = values
        for child in self._children:
            child()


class Margin: 
    """Margin object. Values defined in pixels but returned normalized."""
    _children: list[Callable] = []

    def __init__(
            self, canvas: Canvas, 
            all: int = None,
            tlbr: tuple[int,int,int,int] = None, 
            gutter: int = None 
            ) -> None: 

        self.canvas = canvas  

        if all:
            tlbr = (all,all,all,all)
        elif not tlbr:
            tlbr = (0,0,0,0)
        else:
            pass
        
        self._top_px, self._left_px, self._bottom_px, self._right_px = tlbr
        self._top = self._left = self._bottom = self._right = 0.0

        if not gutter:
            gutter = 0

        self._gutter_px = gutter
        self._gutter_h = self._gutter_w = 0.0

        self.compute()
        self.canvas.give_birth(self.compute)

    def __str__(self) -> str:
        title = 'MARGIN\n'
        message = f'Top: {self._top_px}px\tBottom: {self._right_px}px\tGutter: {self._gutter_px}px\nLeft: {self._left_px}px\tRight: {self._right_px}px\n'
        return title + message

    def give_birth(self, function: Callable) -> None:
        self._children.append(function)

    @property
    def top(self) -> float:
        '''Returns a normalized value. For pixel value, use _px'''
        return self._top

    @top.setter
    def top(self, value: int) -> None:
        self._top_px = value
        self.compute()
 
    @property
    def left(self) -> float:
        '''Returns a normalized value. For pixel value, use _px'''
        return self._left

    @left.setter
    def left(self, value: int) -> None:
        self._left_px = value
        self.compute()

    @property
    def bottom(self) -> float:
        '''Returns a normalized value. For pixel value, use _px'''
        return self._bottom

    @bottom.setter
    def bottom(self, value: int) -> None:
        self._bottom_px = value
        self.compute()

    @property
    def right(self) -> float:
        '''Returns a normalized value. For pixel value, use _px'''
        return self._right

    @right.setter
    def right(self, value: int) -> None:
        self._right_px = value
        self.compute()

    @property
    def all(self) -> dict[str,float]:
        margins = {
            'top': self.top,
            'left': self.left,
            'bottom': self.bottom,
            'right': self.right
        }
        return margins

    @all.setter
    def all(self, value:int) -> None:
        '''Sets all margins to the same pixel value'''
        self._top_px = self._left_px = self._bottom_px = self._right_px = value
        self.compute()

    @property
    def gutter(self) -> tuple[float,float]:
        '''Returns Gutter values (w,h), normalized.'''
        return self._gutter_w, self._gutter_h

    @gutter.setter
    def gutter(self, value: int):
        self._gutter_px = value
        self.compute()

    def compute(self) -> None:
        '''Computes normalized values and calls children.'''

        cwidth, cheight = self.canvas.width, self.canvas.height
        
        self._top = self._top_px / cheight
        self._left = self._left_px / cwidth
        self._bottom = self._bottom_px / cheight
        self._right = self._right_px  / cwidth

        gutter = self._gutter_px

        self._gutter_w = gutter / cwidth
        self._gutter_h = gutter / cheight

        for child in self._children:
            child()


class Grid:
    """Grid object. Creates a layout of columns and rows and returns their dimensions in normalized values."""
    _children: list[Callable] = []
    _matrix: list[list[int]] = []

    def __init__(self, canvas: Canvas, margin: Margin, layout: tuple[int,int] = (12,6)) -> None:
        self.canvas = canvas
        self.margin = margin
        self._cols, self._rows = layout

        self.compute()
        self.margin.give_birth(self.compute)

    def __str__(self) -> str:
        title = 'GRID\n'
        message = f'Cols: {self.cols}\tRows: {self.rows}\n'
        return title + message

    def give_birth(self, function: Callable) -> None:
        self._children.append(function)


    @property
    def cols(self) -> int:
        '''Number of grid columns.'''
        return self._cols

    @cols.setter
    def cols(self, value: int):
        self._cols = value
        self.compute()

    @property
    def rows(self) -> int:
        '''Number of grid rows.'''
        return self._rows

    @rows.setter
    def rows(self, value: int):
        self._rows = value
        self.compute()

    @property
    def gutter(self) -> tuple[float,float]:
        '''Returns Margin Gutter values (w,h), normalized.'''
        return self.margin.gutter

    @gutter.setter
    def gutter(self, value: int):
        '''Sets Margin Gutter in pixels'''
        self.margin.gutter = value

    @property
    def composition(self) -> tuple[int,int]:
        return (self.cols, self.rows)

    @composition.setter
    def composition(self, value: tuple[int,int]) -> None:
        self._cols, self._rows = value
        self.compute()

    def compute(self) -> None: 
        '''Computes normalized values and calls children.'''

        mg = self.margin
        self.col_width = (1 - mg.left - mg.right -
                (self.cols-1) * self.gutter[0]) / self.cols
        self.row_height = (1 - mg.top - mg.bottom -
                (self.rows-1) * self.gutter[1]) / self.rows

        self._matrix.clear()
        for row in range(self.rows):
            x = row * self.cols + 1
            matrix_row = [col + x for col in range(self.cols)]
            self._matrix.append(matrix_row)

        for child in self._children:
            child()

    @property
    def matrix(self) -> list:
        return self._matrix


class Screen:  
    """Screen object. Its dimensions and position are defined in columns and rows and returned in normalized values."""
    list_of_screens = []
    count = 0

    def __init__(self, grid: Grid, colspan: int, rowspan: int, col: int, row: int) -> None:
        self.grid = grid
        
        self._colspan = colspan
        self._rowspan = rowspan

        self._col = col
        self._row = row

        Screen.count += 1

        self._name: str = f"SSScreen{Screen.count}"

        self.compute()
        self.grid.give_birth(self.compute)

        self.list_of_screens.append(self)

    def __str__(self) -> str:
        message = f'Colw: {self.colspan}\tRoww: {self.rowspan}\nColx: {self.col}\tColy: {self.row}\n'
        return message

    def delete(self) -> None:
        Screen.list_of_screens.remove(self)

    @staticmethod
    def create_from_coords(grid: Grid, point1: int, point2: int):
        matrix = grid.matrix
        p1 = get_coords(point1,matrix)

        p2 = get_coords(point2,matrix)

        colspan = abs(p1[0] - p2[0]) + 1
        rowspan = abs(p1[1] - p2[1]) + 1
        col = min(p1[0], p2[0])
        row = min(p1[1], p2[1])

        return Screen(grid,colspan,rowspan,col,row)
   
   
    # Screen transformations ==========================
    @staticmethod
    def flip_horizontally():
        """Flips current screen layout horizontally"""
        for screen in Screen.list_of_screens:
            screen.col = screen.grid.cols - screen.col

    @staticmethod
    def flip_vertically():
        """Flips current screen layout vertically"""
        for screen in Screen.list_of_screens:
            screen.row = screen.grid.rows - screen.row
    # =================================================


    # Properties and setters ==========================
    @property
    def colspan(self) -> int:
        return self._colspan

    @colspan.setter
    def colspan(self, value: int) -> None:
        self._colspan = value
        self.compute()

    @property
    def rowspan(self) -> int:
        return self._rowspan

    @rowspan.setter
    def rowspan(self, value: int) -> None:
        self._rowspan = value
        self.compute()

    @property
    def col(self) -> int:
        return self._col

    @col.setter
    def col(self, value: int) -> None:
        self._col = value
        self.compute()

    @property
    def row(self) -> int:
        return self._row

    @row.setter
    def row(self, value: int) -> None:
        self._row = value
        self.compute()

    @property
    def name(self) -> str:
        return self._name
    
    @name.setter
    def name(self, value: str) -> None:
        if value in self.list_of_screens:
            print("Please choose another name.")
            return
        self._name = value
    # ================================================


    def edit(self, colspan: int, rowspan: int, col: int, row: int) -> None:
        """For editing multiple attributes at the same time. Computes only once."""

        self._colspan = colspan
        self._rowspan = rowspan
        self._col = col
        self._row = row
        self.compute()
    
    def compute(self) -> None:
        """Normalizes pixel values."""

        grid = self.grid
        margin = grid.margin

        width = grid.col_width * self._colspan + (self._colspan-1) * grid.gutter[0]
        height = grid.row_height * self._rowspan + (self._rowspan-1) * grid.gutter[1]

        size = max(width,height)

        x = width/2 + margin.left + (self._col - 1) * (grid.col_width + grid.gutter[0])
        y = height/2 + margin.bottom + (self._row - 1) * (grid.row_height + grid.gutter[1])

        # the "setters"
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        self.size = size

        self.values = {
            "Width": width,
            "Height": height,
            "Center.X": x,
            "Center.Y": y,
            "Size": size
        }

    def get_values(self) -> dict[str,int]:
        return self.values

    

class GridCell(Screen):
    """Grid Cells are Screens of 1 col width x 1 row height that compose a grid."""

    def __init__(self, grid: Grid, index: int):
        self.grid = grid
        self.index = index
        self.col, self.row = get_coords(index, grid.matrix)
        self.width = grid.col_width
        self.height = grid.row_height
        self.compute()
        self.grid.give_birth(self.compute)
    
    @staticmethod
    def generate_all(grid:Grid) -> list:
        all_blocks = []
        for row in grid.matrix:
            for index in row:
                all_blocks.append(GridCell(grid,index))
        return all_blocks

    def compute(self):
        grid = self.grid
        margin = grid.margin

        x = self.width/2 + margin.left + (self.col - 1) * (grid.col_width + grid.gutter[0])
        y = self.height/2 + margin.bottom + (self.row - 1) * (grid.row_height + grid.gutter[1])
        y = 1 - y

        self.x = x
        self.y = y


# Exceptions (not yet implemented)
class MarginsExceedCanvas(Exception):
    """Error for when margins are too big. Should be called when changin resolution or margins"""
    ...

class GutterExceedsCanvas(Exception):
    ...



def test():
    canvas = Canvas()
    print(canvas)

    margin = Margin(canvas,20, gutter=20)

    print(margin)

    grid = Grid(canvas,margin)

    print(grid)

    canvas.width = 500
    canvas.height = 500

    margin.all = 15

    margin.gutter = 35

    print(canvas, margin, grid, sep = '\n')

    screen = Screen(grid,6,6,1,1)
    screen2 = Screen.create_from_coords(grid,8,36)




    # margin = Margin(canvas)
    # grid = Grid(canvas=canvas,margin=margin)
    # screens = [
    #     Screen(
    #         grid = grid,
    #         colspan= 6,
    #         rowspan= 6,
    #         row = 1,
    #         col = 1
    #     ),
    #     Screen(
    #         grid = grid,
    #         colspan= 6,
    #         rowspan= 6,
    #         colx = 7,
    #         coly = 1
    #     )
    # ]

    # # grid.cols = 5
    # # grid.rows = 3
    # print(grid.matrix)

    # coords = (1,34)

    # screens.append(Screen.create_from_coords(grid,*coords))

    # print(screens)


if __name__ == "__main__":
    test()