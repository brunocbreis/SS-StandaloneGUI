from dataclasses import dataclass, field

@dataclass
class Canvas:
    """Defines the canvas size in pixels"""
    width: int = 1920
    height: int = 1080
    _children: list = field(default_factory=list, repr=False)

    @width.setter
    def width(self, width: int):
        self.width = width

    @height.setter
    def height(self, height: int):
        self.height = height

    @property
    def width(self):
        return self.width

    @property
    def height(self):
        return self.height

    def give_birth(self, child):
        self._children.append(child)

class MarginsExceedCanvas(Exception):
    pass

@dataclass(slots=True)
class Margin:
    """Margin object. Values defined in pixels"""
    canvas: Canvas
    top: int = 0
    left: int = 0
    bottom: int = 0
    right: int = 0

    def __post_init__(self):
        self.canvas.give_birth(self)

    def set_margins(self, top: int, left: int, bottom: int, right: int):
        try:
            if top + bottom > self.canvas.height | left + right > self.canvas.width:
                print("Margin values exceed canvas dimensions.")
                raise MarginsExceedCanvas
        except:
            self.top = top
            self.left = left
            self.bottom = bottom
            self.right = right

    def needs_update(self):
        self.is_up_to_date = False   
          
@dataclass
class Grid:
    canvas: Canvas
    margin: Margin
    cols: int = 12
    rows: int = 6
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

    def get_values(self) -> dict:
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
        return values

def main():
    canvas = Canvas(500,500)
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

    for screen in screens:
        screen.compute_values()

    for screen in screens:
        values = screen.get_values()
        print(values)

    margin.set_margins(300,300,300,300)
    # grid.compute_values()

    for screen in screens:
        screen.compute_values()

    for screen in screens:
        values = screen.get_values()
        print(values)

    print(canvas._children)

if __name__ == "__main__":
    main()