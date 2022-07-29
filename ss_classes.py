from __future__ import annotations
from typing import Callable


# helper function for Screen and Grid classes
def get_coords(item, matrix: list[list]) -> tuple[int, int]:
    for i, v in enumerate(matrix):
        if item in v:
            y = i
            x = v.index(item)
    return x + 1, y + 1


class Canvas:
    """Canvas object. Sizes defined and returned in pixels."""

    _children: list[Callable] = []

    def __init__(self, resolution: tuple[int, int] = (1920, 1080)):
        self._width_px, self._height_px = resolution

    def __str__(self) -> str:
        title = "CANVAS\n"
        message = f"Width: {self.width}px\tHeight: {self.height}px\n"
        return title + message

    def give_birth(self, function: Callable) -> None:
        self._children.append(function)

    @property
    def width(self) -> int:
        return self._width_px

    @width.setter  # will call children
    def width(self, width: int):
        self.resolution = (width, self.height)

    @property
    def height(self) -> int:
        return self._height_px

    @height.setter  # will call children
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
        self,
        canvas: Canvas,
        all: int = None,
        tlbr: tuple[int, int, int, int] = None,
        gutter: int = None,
    ) -> None:

        self.canvas = canvas

        if all:
            tlbr = (all, all, all, all)
        elif not tlbr:
            tlbr = (0, 0, 0, 0)
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
        title = "MARGIN\n"
        message = f"Top: {self._top_px}px\tBottom: {self._right_px}px\tGutter: {self._gutter_px}px\nLeft: {self._left_px}px\tRight: {self._right_px}px\n"
        return title + message

    def give_birth(self, function: Callable) -> None:
        self._children.append(function)

    @property
    def top(self) -> float:
        """Returns a normalized value. For pixel value, use _px"""
        return self._top

    @top.setter
    def top(self, value: int) -> None:
        self._top_px = value
        self.compute()

    @property
    def left(self) -> float:
        """Returns a normalized value. For pixel value, use _px"""
        return self._left

    @left.setter
    def left(self, value: int) -> None:
        self._left_px = value
        self.compute()

    @property
    def bottom(self) -> float:
        """Returns a normalized value. For pixel value, use _px"""
        return self._bottom

    @bottom.setter
    def bottom(self, value: int) -> None:
        self._bottom_px = value
        self.compute()

    @property
    def right(self) -> float:
        """Returns a normalized value. For pixel value, use _px"""
        return self._right

    @right.setter
    def right(self, value: int) -> None:
        self._right_px = value
        self.compute()

    @property
    def all(self) -> dict[str, float]:
        margins = {
            "top": self.top,
            "left": self.left,
            "bottom": self.bottom,
            "right": self.right,
        }
        return margins

    @all.setter
    def all(self, value: int) -> None:
        """Sets all margins to the same pixel value"""
        self._top_px = self._left_px = self._bottom_px = self._right_px = value
        self.compute()

    @property
    def tlbr(self) -> dict[str, float]:
        return self.all

    @tlbr.setter
    def tlbr(self, values: tuple[int, int, int, int]) -> None:
        """Set all margins at the same time, with different values (top, left, bottom, right)"""
        self._top_px, self._left_px, self._bottom_px, self._right_px = values
        self.compute()

    @property
    def gutter(self) -> tuple[float, float]:
        """Returns Gutter values (w,h), normalized."""
        return self._gutter_w, self._gutter_h

    @gutter.setter
    def gutter(self, value: int):
        self._gutter_px = value
        self.compute()

    def compute(self) -> None:
        """Computes normalized values and calls children."""

        cwidth, cheight = self.canvas.width, self.canvas.height

        self._top = self._top_px / cheight
        self._left = self._left_px / cwidth
        self._bottom = self._bottom_px / cheight
        self._right = self._right_px / cwidth

        gutter = self._gutter_px

        self._gutter_w = gutter / cwidth
        self._gutter_h = gutter / cheight

        for child in self._children:
            child()


class Grid:
    """Grid object. Creates a layout of columns and rows and returns their dimensions in normalized values."""

    _children: list[Callable] = []
    _matrix: list[list[int]] = []

    def __init__(
        self, canvas: Canvas, margin: Margin, layout: tuple[int, int] = (12, 6)
    ) -> None:
        self.canvas = canvas
        self.margin = margin
        self._cols, self._rows = layout

        self.compute()
        self.margin.give_birth(self.compute)

    def __str__(self) -> str:
        title = "GRID\n"
        message = f"Cols: {self.cols}\tRows: {self.rows}\n"
        return title + message

    def give_birth(self, function: Callable) -> None:
        self._children.append(function)

    def rotate_clockwise(self) -> None:  # something's still not working
        self.canvas.resolution = self.canvas.height, self.canvas.width
        self.margin.tlbr = (
            self.margin.right,
            self.margin.top,
            self.margin.left,
            self.margin.bottom,
        )
        self.composition = self.rows, self.cols
        ...

    def rotate_counterclockwise(self) -> None:
        ...

    @property
    def cols(self) -> int:
        """Number of grid columns."""
        return self._cols

    @cols.setter
    def cols(self, value: int):
        self._cols = value
        self.compute()

    @property
    def rows(self) -> int:
        """Number of grid rows."""
        return self._rows

    @rows.setter
    def rows(self, value: int):
        self._rows = value
        self.compute()

    @property
    def gutter(self) -> tuple[float, float]:
        """Returns Margin Gutter values (w,h), normalized."""
        return self.margin.gutter

    @gutter.setter
    def gutter(self, value: int):
        """Sets Margin Gutter in pixels"""
        self.margin.gutter = value

    @property
    def composition(self) -> tuple[int, int]:
        return (self.cols, self.rows)

    @composition.setter
    def composition(self, value: tuple[int, int]) -> None:
        self._cols, self._rows = value
        self.compute()

    def compute(self) -> None:
        """Computes normalized values and calls children."""

        mg = self.margin
        self.col_width = (
            1 - mg.left - mg.right - (self.cols - 1) * self.gutter[0]
        ) / self.cols
        self.row_height = (
            1 - mg.top - mg.bottom - (self.rows - 1) * self.gutter[1]
        ) / self.rows

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
    """Screen object class. Its dimensions and position are defined in columns and rows and returned in normalized values."""

    list_of_screens: list[Screen] = None
    count = 0

    def __init__(
        self, grid: Grid, colspan: int, rowspan: int, col: int, row: int
    ) -> Screen:
        self.grid = grid

        self._colspan = colspan
        self._rowspan = rowspan

        self._col = col
        self._row = row

        Screen.count += 1

        self._name: str = f"SSScreen{Screen.count}"

        self.compute()
        self.grid.give_birth(self.compute)

        if Screen.list_of_screens is None:
            Screen.list_of_screens = []

        self.list_of_screens.append(self)

    def __str__(self) -> str:
        message = f"Colw: {self.colspan}\tRoww: {self.rowspan}\nColx: {self.col}\tColy: {self.row}\n"
        return message

    def delete(self) -> None:
        Screen.list_of_screens.remove(self)

    @classmethod
    def create_from_coords(cls: Screen, grid: Grid, point1: int, point2: int) -> Screen:
        matrix = grid.matrix

        p1 = get_coords(point1, matrix)
        p2 = get_coords(point2, matrix)

        colspan = abs(p1[0] - p2[0]) + 1
        rowspan = abs(p1[1] - p2[1]) + 1
        col = min(p1[0], p2[0])
        row = min(p1[1], p2[1])

        return Screen(grid, colspan, rowspan, col, row)

    # Screen transformations ==========================
    @classmethod
    def flip_horizontally(cls) -> None:
        """Flips current screen layout horizontally"""
        for screen in cls.list_of_screens:
            col = screen.col - 1
            newcol = screen.grid.cols - col - screen.colspan
            screen.col = newcol + 1

    @classmethod
    def flip_vertically(cls) -> None:
        """Flips current screen layout vertically"""
        for screen in cls.list_of_screens:
            row = screen.row - 1
            newrow = screen.grid.rows - row - screen.rowspan
            screen.row = newrow + 1

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

        width = grid.col_width * self._colspan + (self._colspan - 1) * grid.gutter[0]
        height = grid.row_height * self._rowspan + (self._rowspan - 1) * grid.gutter[1]

        size = max(width, height)

        x = (
            width / 2
            + margin.left
            + (self._col - 1) * (grid.col_width + grid.gutter[0])
        )
        y = (
            height / 2
            + margin.bottom
            + (self._row - 1) * (grid.row_height + grid.gutter[1])
        )

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
            "Size": size,
        }

    def get_values(self) -> dict[str, int]:
        return self.values

# not working at all
class GridCell(Screen):
    """Grid Cells are Screens of 1 col width x 1 row height that compose a grid."""

    grid: Grid = None
    all_blocks = None

    def __init__(self, grid: Grid, index: int = None):

        if GridCell.grid is None:
            GridCell.grid = grid

        self._colspan = self._rowspan = 1

        if index is None:
            self._col = self._row = 1
        else:
            self._col, self._row = get_coords(index, GridCell.grid.matrix)
        
        self.compute()
        self.grid.give_birth(self.compute)

    @classmethod
    def generate_all(cls, grid: Grid) -> list[GridCell]:
        if cls.all_blocks is None:
            cls.all_blocks = []
        else:
            cls.all_blocks.clear()
        
        for row in grid.matrix:
            for index in row:
                cls.all_blocks.append(GridCell(grid, index))
        return cls.all_blocks

    def compute(self):
        grid = GridCell.grid
        margin = grid.margin

        x = (
            grid.col_width / 2
            + margin.left
            + (self._col - 1) * (grid.col_width + grid.gutter[0])
        )
        y = (
            grid.row_height / 2
            + margin.bottom
            + (self._row - 1) * (grid.row_height + grid.gutter[1])
        )
        # y = 1 - y

        self.width = grid.col_width
        self.height = grid.row_height
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

    margin = Margin(canvas, 20, gutter=20)

    print(margin)

    grid = Grid(canvas, margin)

    print(grid)

    canvas.width = 500
    canvas.height = 500

    margin.all = 15

    margin.gutter = 35

    print(canvas, margin, grid, sep="\n")

    cells = GridCell.generate_all(grid)
    print(cells)
    w1 = GridCell.all_blocks[0].width

    grid.cols = 6
    w2 = GridCell.all_blocks[0].width

    print(w2/w1)

if __name__ == "__main__":
    test()
