import tkinter as tk
import ss_classes as ss


def delete_widgets(list_of_widgets: list[tk.Widget]):
    for widget in list_of_widgets:
        widget.place_forget()
        widget.destroy()
    list_of_widgets.clear()

def grid_state_1():
    pass



class SplitScreenCreator(tk.Canvas):
    """Class for the area where the user draws screens over a grid."""

    original_color = "#0000ff"
    screen_color = "yellow"
    new_screen_coords: tuple = (1,1)

    def __init__(self, master: tk.Tk, ss_grid: ss.Grid):
        self.master = master
        self.ss_grid = ss_grid
        self.grid_block_widgets: list[RenderedScreen] = []
        self.screen_widgets: list[RenderedScreen] = []
        self.list_of_ssscreens: list[ss.Screen] = []


    def append_grid_block(self, block: tk.Label) -> None:
        self.grid_block_widgets.append(block)

    def append_screen_widget(self, screen_widget: tk.Label) -> None:
        self.screen_widgets.append(screen_widget)

    def append_ssscreen(self, screen: ss.Screen) -> None:
        self.list_of_ssscreens.append(screen)

    def save_first_coord(self, coord: int) -> None:
        """Overwrites screen coordinates. Means user will add new Screen"""
        self.new_screen_coords = coord
        pass

    def save_second_coord(self, coord: int) -> None:
        """Adds the second value to the tuple. Means user released the mouse"""
        self.new_screen_coords = (self.new_screen_coords, coord)
        pass
        
    def add_screen(self):
        print("Adding screen...")
        try:
            new_screen = ss.Screen.create_from_coords(self.ss_grid, *self.new_screen_coords)
        except:
            print("Can't create screen. Have you tried resetting the coordinates?")
            return
        print(new_screen)

        self.append_ssscreen(new_screen)
        print(self.list_of_ssscreens)

        self.refresh(screens_only=True)

        for block in self.grid_block_widgets:
            grid_state_1(block)
            block.config(bg = self.original_color)


    def create_grid_blocks(self) -> list[list[ss.Screen]]:
        grid_blocks = []

        for row in range(self.ss_grid.rows):
            grid_blocks_row = []
            for col in range(self.ss_grid.cols):
                block = ss.Screen(self.ss_grid,1,1,col+1,row+1)
                grid_blocks_row.append(block)
            grid_blocks.append(grid_blocks_row)
        
        return grid_blocks

    def refresh(self, screens_only: bool = False):

        if not screens_only:
            if len(self.grid_block_widgets) > 0:
                delete_widgets(self.grid_block_widgets)
            
            grid_blocks = self.create_grid_blocks()

            # CREATING widgets and indexing them
            for block_y in range(len(grid_blocks)):
                row = grid_blocks[block_y]
                ncols = len(row)

                for block_x in range(len(row)):
                    block = row[block_x]
                    widget = RenderedScreen(self,block, self.original_color, self.grid_block_widgets)
                    
                    widget.index = block_x + 1 + block_y * ncols
                    
                    widget.config(text = widget.index)
                    grid_state_1(widget)

            for widget in self.grid_block_widgets:
                widget.place_screen()
        
        there_are_screens = False
        if len(self.list_of_ssscreens) > 0:
            there_are_screens = True

        if there_are_screens:
            delete_widgets(self.screen_widgets)
            for screen in self.list_of_ssscreens:
                 RenderedScreen(self, screen, self.screen_color, self.screen_widgets)
            for screen_widget in self.screen_widgets:
                screen_widget.place_screen()
    

class RenderedScreen(tk.Label):
    """Class for Label objects that have been generated from ss.Screen objects"""

    def __init__(self, master: SplitScreenCreator, ss_screen: ss.Screen, color: str, category: str):
        self.master = master
        self.bg = color
        self.bd = 0,
        self.highlightthickness=0
        self.relief = 'ridge'

        self.ss_screen = ss_screen

        if category == "screen":
            self.master.append_screen_widget(self)
        if category == "block":
            self.master.append_grid_block(self)

    def place_screen(self):
        screen = self.ss_screen

        relx = screen.x - screen.width/2
        rely = 1 - (screen.y + screen.height/2)
        relwidth = screen.width
        relheight = screen.height

        self.place(relwidth=relwidth,relheight=relheight, anchor=tk.NW, relx=relx, rely=rely, bordermode='outside')

    def should_be_painted(self) -> bool:
        """Determines whether a grid block should change color,
            meaning it's part of the new screen being created.
        """

        coords = self.master.new_screen_coords
        grid = self.master.ss_grid

        block_x, block_y = ss.get_coords(self.index,grid.matrix)
        coords_1, coords_2 = ss.get_coords(coords[0],grid.matrix), ss.get_coords(coords[1],grid.matrix)
        coords_x, coords_y = (coords_1[0], coords_2[0]+1), (coords_1[1], coords_2[1]+1)

        if block_x in range(*coords_x):
            if block_y in range(*coords_y):
                return True
        return False


class SplitScreenerSettings(tk.Frame):
    """Class for the area where user sets values"""

    def __init__(self, master: tk.Tk, creator: SplitScreenCreator):
        pass


color_palette = {

}



def main():
    root = tk.Tk()

    creator = tk.Canvas()
    creator.master = root

    print(creator.master)

    root.mainloop()
    pass

if __name__ == "__main__":
    main()