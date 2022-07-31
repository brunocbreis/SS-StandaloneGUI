from __future__ import annotations
from abc import ABC, abstractmethod
import tkinter as tk
from tkinter import Label, ttk
from tkinter.font import Font
from turtle import width
from typing import Callable
import ss_classes as ss
from fusion_tool_generator import load_defaults, render_fusion_output, save_preset_for_fusion
from PIL import Image, ImageTk
import pyperclip


# FUNCTIONS ======================================================
def is_within(coords: tuple[float, float], area: dict[tuple[float, float]]) -> bool:
    x, y = coords[0], coords[1]
    if x <= area["top_left"][0]:
        return False
    if x >= area["top_right"][0]:
        return False
    if y >= area["top_left"][1]:
        return False
    if y <= area["bottom_left"][1]:
        return False
    return True


def find_grid_block_within(
    coords: tuple[float, float], grid_blocks: list[GridBlock]
) -> GridBlock:
    return next(
        (block for block in grid_blocks if is_within(coords, block.grid_cell.corners)),
        None,
    )


def get_event_coords_normalized(event) -> tuple[float, float]:
    self = event.widget
    coords = (event.x / self.winfo_width(), 1- event.y / self.winfo_height())
    return coords

def clear_status_bar(cls:ScreenSplitter) -> None:
    cls.after(3500, lambda: cls.status_text.set(""))

# CLASSES ======================================================
class Block(ABC):
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
    def bind(self, event: str, callable) -> None:
        pass


class ScreenBlock(Block):
    screen_blocks = None
    settings = None

    def __init__(
        self, tk_canvas: ScreenSplitter, ss_screen: ss.Screen, **config
    ) -> None:
        self.canvas = tk_canvas
        self.screen = ss_screen

        self.compute()
        if ScreenBlock.screen_blocks is None:
            ScreenBlock.grid_blocks = []

        ScreenBlock.grid_blocks.append(self)

        if ScreenBlock.settings is None:
            ScreenBlock.settings = {}
            for key, value in config.items():
                ScreenBlock.settings[key] = value

    def draw(self) -> None:
        self.rect = self.canvas.create_rectangle(
            self.x0, self.y0, self.x1, self.y1, **self.settings
        )

    def compute(self):
        self.canvas.update()
        canvas_height = self.canvas.winfo_height()
        canvas_width = self.canvas.winfo_width()
        screen = self.screen
        y = 1 - screen.y

        self.x0 = (screen.x - screen.width / 2) * canvas_width
        self.y0 = (y - screen.height / 2) * canvas_height
        self.x1 = self.x0 + screen.width * canvas_width
        self.y1 = self.y0 + screen.height * canvas_height


    @classmethod
    def draw_all(cls):
        for block in cls.screen_blocks:
            block.compute()

        for block in cls.screen_blocks:
            block.draw()

    @classmethod
    def redraw_all():
        pass

    def undraw(self) -> None:
        pass

    def config(self, **opts) -> None:
        pass

    def bind(self, event: str, callable) -> None:
        pass


class GridBlock(Block):
    grid_blocks: list[GridBlock] = None
    settings = {}

    def __init__(self, tk_canvas: tk.Canvas, grid_cell: ss.GridCell, **config):
        self.canvas = tk_canvas
        self.grid_cell = grid_cell

        if grid_cell.index == 1:
            for key, value in config.items():
                self.settings[key] = value

        self.compute()
        if GridBlock.grid_blocks is None:
            GridBlock.grid_blocks = []
        GridBlock.grid_blocks.append(self)

    def compute(self):
        self.canvas.update()
        canvas_height = self.canvas.winfo_height()
        canvas_width = self.canvas.winfo_width()
        cell = self.grid_cell
        y = 1 - cell.y

        self.x0 = (cell.x - cell.width / 2) * canvas_width
        self.y0 = (y - cell.height / 2) * canvas_height
        self.x1 = self.x0 + cell.width * canvas_width
        self.y1 = self.y0 + cell.height * canvas_height


    def draw(self):
        self.rect = self.canvas.create_rectangle(
            self.x0, self.y0, self.x1, self.y1, **self.settings
        )

    def undraw(self, *opt):
        self.canvas.delete(self.rect)
        GridBlock.grid_blocks.remove(self)

    def config(self, **opts):
        self.canvas.itemconfig(self.rect, **opts)
        for key, value in opts.items():
            self.settings[key] = value

    @staticmethod
    def blocks_from_grid(grid: ss.Grid) -> list[ss.GridCell]:
        return ss.GridCell.generate_all(grid)

    @classmethod
    def draw_all(cls):
        for block in cls.grid_blocks:
            block.compute()

        for block in cls.grid_blocks:
            block.draw()

    @classmethod
    def undraw_all(cls):
        if len(cls.grid_blocks) > 0:
            for block in cls.grid_blocks:
                block.undraw()
                return
        print("No blocks have been drawn.")

    @classmethod
    def create_all(cls, canvas: tk.Canvas, grid: ss.Grid, **config):
        if cls.grid_blocks is None:
            cls.grid_blocks = []
        cls.grid_blocks.clear()

        # creates grid cells from provided grid
        grid_block_screens = cls.blocks_from_grid(grid)

        # initializes grid block from generated cells
        for cell in grid_block_screens:
            GridBlock(canvas, cell, **config)

    @classmethod
    def config_all(cls, **opts):
        for key, value in opts:
            cls.settings[key] = value
        list = cls.grid_blocks
        for block in list:
            block.config(**opts)

    @classmethod
    def bind_all(cls, event: str, callable: Callable):
        for block in cls.grid_blocks:
            block.bind(event, callable)
        ...

    def get_property(self, *opts):
        for opt in opts:
            return self.canvas.itemcget(self.rect, opt)

    @property
    def tag(self):
        return self.get_property("tag")

    @tag.setter
    def tag(self, tag: str):
        self.config(tag=tag)

    def bind(self, event: str, callable) -> None:
        self.canvas.tag_bind(self.tag, sequence=event, func=callable)


class ScreenSplitter(tk.Canvas):
    new_screen_coords: tuple[tuple[float, float], tuple[float, float]] = (
        (0.0, 0.0),
        (0.0, 0.0),
    )
    new_screen_indexes: tuple[int, int] = (0, 0)
    user_screens: list[ss.Screen] = None
    ss_grid: ss.Grid = None
    grid_blocks: list[GridBlock] = None
    max_width = 750
    max_height = 550
    fusion_export: str = None
    selected_screen = None
    status_text = None

    @classmethod
    def on_click(cls, event: tk.Event) -> None:
        

        self = event.widget
        
        item = self.find_closest(event.x,event.y)
        if self.itemcget(item, "fill") == cls.screen_color:
            print("clicked on screen")
            cls.new_screen_coords = None
            return 

        coords = get_event_coords_normalized(event)
        cls.new_screen_coords = coords
        block = find_grid_block_within(coords, GridBlock.grid_blocks)

        if block is not None:
            index = block.grid_cell.index
            cls.new_screen_indexes = index
            return
        cls.new_screen_indexes = None

    @classmethod
    def on_release(cls, event: tk.Event) -> None:
        # cls.unselect_screen(event.widget)
        if cls.new_screen_coords is None:
            return
        coords = get_event_coords_normalized(event)
        cls.new_screen_coords = (cls.new_screen_coords, coords)
        block = find_grid_block_within(coords, GridBlock.grid_blocks)

        if block is not None:
            index = block.grid_cell.index
            cls.new_screen_indexes = (cls.new_screen_indexes, index)
            event.widget.create_screen()
            return
        cls.new_screen_indexes = None

    def create_screen(self) -> None:
        if ScreenSplitter.ss_grid is None:
            raise Exception("Please attach a grid first.")
        if ScreenSplitter.new_screen_indexes is None:
            return
        new_screen = ss.Screen.create_from_coords(
            ScreenSplitter.ss_grid, *ScreenSplitter.new_screen_indexes
        )

        if ScreenSplitter.user_screens is None:
            ScreenSplitter.user_screens = []
        ScreenSplitter.user_screens.append(new_screen)
        print(ScreenSplitter.user_screens)

        self.draw_screen(new_screen)

    def draw_screen(self, screen: ss.Screen) -> None:
        new_screen_block = ScreenBlock(
            self,
            screen,
            fill=self.screen_color,
            outline=self.screen_color,
            tag="screen",
        )
        new_screen_block.draw()
        self.tag_bind("screen","<ButtonRelease-1>",self.select_screen)



    def deselect_screen(self, event):
        
        item = self.find_closest(event.x,event.y)
        self.itemconfig(item,width=0)
        self.tag_bind("screen","<ButtonRelease-1>",self.select_screen)

        ...

    def select_screen(self, event: tk.Event):
        if self.selected_screen is not None:
            self.selected_screen = None

        item = self.find_closest(event.x,event.y)
        self.selected_screen = item

        print("selected one screen.")
        print(self.selected_screen)

        self.mark_selected()
        ...

    def mark_selected(self):
        self.itemconfig("selected", outline=self.screen_color)
        self.itemconfig(self.selected_screen, width=1, outline="white", tag="selected")
        self.tag_bind("screen","<ButtonRelease-1>",self.select_screen)



    def global_set(self, **kwargs: dict[str, int]) -> None:
        do_width, do_height = False, False
        if "width" in kwargs:
            self.ss_grid.canvas.width = kwargs["width"]
            do_width = True
        if "height" in kwargs:
            self.ss_grid.canvas.height = kwargs["height"]
            do_height = True

        if "top" in kwargs:
            self.ss_grid.margin.top = kwargs["top"]
        if "left" in kwargs:
            self.ss_grid.margin.left = kwargs["left"]
        if "bottom" in kwargs:
            self.ss_grid.margin.bottom = kwargs["bottom"]
        if "right" in kwargs:
            self.ss_grid.margin.right = kwargs["right"]
        if "gutter" in kwargs:
            self.ss_grid.margin.gutter = kwargs["gutter"]

        if "cols" in kwargs:
            self.ss_grid.cols = kwargs["cols"]
        if "rows" in kwargs:
            self.ss_grid.rows = kwargs["rows"]

        self.global_refresh((do_width, do_height))

    # REFRESHING METHODS
    def width_refresh(self, func: Callable):
        self.ss_grid.canvas.width = func()
        self.global_refresh((True, False))

    def height_refresh(self, func: Callable):
        self.ss_grid.canvas.height = func()
        self.global_refresh((False, True))

    def top_refresh(self, func: Callable):
        self.ss_grid.margin.top = func()
        self.global_refresh()

    def left_refresh(self, func: Callable):
        self.ss_grid.margin.left = func()
        self.global_refresh()

    def bottom_refresh(self, func: Callable):
        self.ss_grid.margin.bottom = func()
        self.global_refresh()

    def right_refresh(self, func: Callable):
        self.ss_grid.margin.right = func()
        self.global_refresh()

    def gutter_refresh(self, func: Callable):
        self.ss_grid.margin.gutter = func()
        self.global_refresh()

    def col_refresh(self, func: Callable):
        self.ss_grid.cols = func()
        self.global_refresh()

    def row_refresh(self, func: Callable):
        self.ss_grid.rows = func()
        self.global_refresh()

    def global_refresh(
        self, canvas_changed: tuple[bool, bool] = (False, False)
    ) -> None:
        if canvas_changed[0]:
            self.configure(width=self.ss_grid.canvas.width)
        if canvas_changed[1]:
            self.configure(height=self.ss_grid.canvas.height)

        self.update_dims()

        self.delete("all")
        GridBlock.create_all(self, self.ss_grid)
        GridBlock.draw_all()
        if self.user_screens is None:
            return
        for screen in self.user_screens:
            self.draw_screen(screen)
            # self.tag_all_screens_for_selection()

    def compute_dims(self) -> tuple[int]:
        canvas = self.ss_grid.canvas
        aspect_ratio = canvas.aspect_ratio

        max_width = 750
        max_height = 550

        if aspect_ratio > 1:
            canvas_width = max_width
            canvas_height = canvas_width / aspect_ratio
        else:
            canvas_height = max_height
            canvas_width = canvas_height * aspect_ratio

        return canvas_width, canvas_height

    def update_dims(self) -> None:
        canvas_width, canvas_height = self.compute_dims()
        self.config(width=canvas_width, height=canvas_height)

        self.preview_scale = canvas_width / self.ss_grid.canvas.width

        self.scale_var.set(value=self.preview_scale)
        self.scale_text.set(f"Preview scale: {self.scale_var.get()*100:.1f}%")

    @classmethod
    def export_for_fusion(cls, event: tk.Event) -> None:
        if cls.user_screens is None:
            return
        screen_values = []
        for screen in cls.user_screens:
            screen_values.append(screen.get_values())
        cls.fusion_export = render_fusion_output(screen_values,cls.ss_grid.canvas.resolution,cls.fusion_studio.get())
        pyperclip.copy(cls.fusion_export)
        if cls.status_text is None:
            cls.status_text = tk.StringVar()
        cls.status_text.set("Node tree successfuly copied to clipboard.")


class RectTracker:
    def __init__(self, canvas):
        self.canvas = canvas
        self.item = None

    def draw(self, start, end, **opts):
        """Draw the rectangle"""
        return self.canvas.create_rectangle(*(list(start) + list(end)), **opts)

    def autodraw(self, **opts):
        """Setup automatic drawing; supports command option"""
        self.start = None
        self.canvas.bind("<Button-1>", self.__update, "+")
        self.canvas.bind("<B1-Motion>", self.__update, "+")
        self.canvas.bind("<ButtonRelease-1>", self.__stop, "+")

        self.rectopts = opts

    def __update(self, event):
        if not self.start:
            self.start = [event.x, event.y]
            return

        if self.item is not None:
            self.canvas.delete(self.item)
        self.item = self.draw(self.start, (event.x, event.y), **self.rectopts)
        # self._command(self.start, (event.x, event.y))

    def __stop(self, event):
        self.start = None
        self.canvas.delete(self.item)
        self.item = None




# APP =================================================================================
def main():
    root = tk.Tk()


    # COLOR PALETTE =========================================================
    class ColorPalette:
        root_bg_color = "#282828"
        canvas_bg_color = "#141414"
        canvas_block_color = "#282828"
        canvas_block_hover_color = "#303030"
        canvas_screen_color = "#0070D4"
        text_color = "#D0D0D0"
        entry_bg_color = "#1F1F1F"


    # FONT PALETTE ========================================================
    class FontPalette:
        main = Font(family="Archivo SemiExpanded Light")
        small = Font(family="Archivo SemiExpanded Light", size=12)


    # ROOT CONFIGS =========================================================
    root.configure(bg=ColorPalette.root_bg_color)

    root.option_add("*font",FontPalette.main)
    root.option_add("*foreground", ColorPalette.text_color)
    root.option_add("*Entry.foreground", ColorPalette.text_color)
    root.option_add("*Entry.background", ColorPalette.entry_bg_color)
    root.option_add("*background", ColorPalette.root_bg_color)
    # root.option_add("*Button.background", ColorPalette.root_bg_color)
    # root.option_add("*Label.background", ColorPalette.root_bg_color)
    # root.option_add("*Checkbutton.background", ColorPalette.root_bg_color)
    root.option_add("*Checkbutton.font", FontPalette.small)

    root.title('SplitScreener')
    root.resizable(False,False)


    # TTK STYLE STUFF =========================
    estyle = ttk.Style()
    estyle.element_create("plain.field", "from", "clam")
    estyle.layout("pad.TEntry",
                    [('Entry.plain.field', {'children': [(
                        'Entry.background', {'children': [(
                            'Entry.padding', {'children': [(
                                'Entry.textarea', {'sticky': 'nswe'})],
                        'sticky': 'nswe'})], 'sticky': 'nswe'})],
                        'border':'0', 'sticky': 'nswe'})])
    estyle.configure("pad.TEntry",
                    background=ColorPalette.entry_bg_color, 
                    foreground=ColorPalette.text_color,
                    fieldbackground=ColorPalette.entry_bg_color,
                    padding='20 5 20 5')



    # SETTING UP THE MAIN TK GRID ======================================================
    root.columnconfigure(index=1,   weight=1, minsize=200)  # LEFT SIDEBAR
    root.columnconfigure(index=2,   weight=1, minsize=800)  # MAIN SECTION, THE CREATOR
    root.columnconfigure(index=3,   weight=1, minsize=200)  # RIGHT SIDEBAR (nothing there yet)
    root.rowconfigure(   index=1,   weight=3)               # HEADER
    root.rowconfigure(   index=2,   weight=1)               # MAIN SECTION, THE CREATOR FRAME AND SETTINGS
    root.rowconfigure(   index=3,   weight=1)               # THE RENDER BUTTON FRAME
    root.rowconfigure(   index=4,   weight=3)               # FOOTER


    # CREATING THE FRAMES
    header =                tk.Frame(root)
    button_frame_left =     tk.Frame(root)
    creator_frame =         tk.Frame(root,width=770,height=575)
    button_frame_right =    tk.Frame(root) 
    render_bttn_frame =     tk.Frame(root)
    footer =                tk.Frame(root)

    # adding them to the grid
    header.grid(            column=1,   row=1,  columnspan=3)
    button_frame_left.grid( column=1,   row=2, sticky=tk.E)
    creator_frame.grid(     column=2,   row=2,  padx=10, pady=10)
    button_frame_right.grid(column=3,   row=2, ipadx=20)
    render_bttn_frame.grid( column=2,   row=3)
    footer.grid(            column=1,   row=4,  columnspan=3)


    # APP LOGO
    # if darkdetect.isDark():
    #     logo_img = Image.open('images/SS_logo_white.png').resize((173,62), Image.ANTIALIAS)
    #     logo = ImageTk.PhotoImage(logo_img)

    logo_img = Image.open('images/SS_logo_offwhite.png')#.resize((173,62), Image.Resampling.LANCZOS)
    logo = ImageTk.PhotoImage(logo_img)


    # APP TITLE
    app_title = tk.Label(header, height=100, justify=tk.CENTER, image=logo)
    app_title.pack(anchor=tk.S, pady=40)


    # LOADING SPLITSCREENER DEFAULTS =========================================
    defaults_raw = load_defaults("defaults/defaults.json")
    defaults = {}
    for key in defaults_raw.keys():
        for key, value in defaults_raw[key].items():
            defaults[key] = value

    
    # SPLITSCREENER INITIALIZERS ======================================
    ss_canvas = ss.Canvas((defaults["width"], defaults["height"]))
    ss_margin = ss.Margin(
        ss_canvas,
        tlbr=(defaults["top"], defaults["left"], defaults["bottom"], defaults["right"]),
        gutter=defaults["gutter"],
    )
    ss_grid = ss.Grid(ss_canvas, ss_margin, (defaults["cols"], defaults["rows"]))




    # CREATING WIDGETS =========================================================
    screen_splitter = ScreenSplitter(
        creator_frame, background=ColorPalette.canvas_bg_color, bd=0, highlightthickness=0, relief="ridge"
    )
    ScreenSplitter.ss_grid = ss_grid

    ScreenSplitter.scale_var = tk.DoubleVar()
    ScreenSplitter.scale_text = tk.StringVar()
    ScreenSplitter.screen_color: str = ColorPalette.canvas_screen_color
    ScreenSplitter.fusion_studio: tk.BooleanVar = tk.BooleanVar()

    screen_splitter.update_dims()
    screen_splitter.grid(padx=20, pady=5)




    # RENDERING GRID BLOCKS ======================================================
    GridBlock.create_all(
        screen_splitter,
        ss_grid,
        fill=ColorPalette.canvas_block_color,
        activefill=ColorPalette.canvas_block_hover_color,
        outline=ColorPalette.canvas_block_color,
        activeoutline=ColorPalette.canvas_block_color,
        activewidth=1,
    )
    GridBlock.draw_all()




   # BINDING FOR CLICK AND DRAG SCREEN ADD =======================
    screen_splitter.bind("<Button-1>", screen_splitter.on_click)
    screen_splitter.bind("<ButtonRelease-1>", screen_splitter.on_release)




    # SCALE LABEL ====================================================================
    scale_label = tk.Label(creator_frame, font=FontPalette.small,textvariable=screen_splitter.scale_text, justify=tk.RIGHT, bg=ColorPalette.root_bg_color)
    scale_label.grid(row=2, sticky=tk.NE,  padx=20)

    

    ##################################################################################
    ##################### BUTTON LEFT FRAME ##########################################
    ##################################################################################
    
    # TKINTER VARIABLES FOR USER GRID SETTINGS ========================================
    vars = {}


    # CANVAS =======================
    vars["width"] = tk.IntVar(value=defaults["width"])
    # vars['width'].trace_add('write', lambda a, b, c: screen_splitter.width_refresh(vars['width'].get))

    vars["height"] = tk.IntVar(value=defaults["height"])
    # vars['height'].trace_add('write', lambda a, b, c: screen_splitter.height_refresh(vars['height'].get))



    # MARGIN =======================
    vars["top"] = tk.IntVar(value=defaults["top"])
    # vars["top"].trace_add("write", lambda a, b, c: screen_splitter.top_refresh(vars["top"].get))

    vars["left"] = tk.IntVar(value=defaults["left"])
    # vars["left"].trace_add("write", lambda a, b, c: screen_splitter.left_refresh(vars["left"].get))

    vars["bottom"] = tk.IntVar(value=defaults["bottom"])
    # vars["bottom"].trace_add("write", lambda a, b, c: screen_splitter.bottom_refresh(vars["bottom"].get))

    vars["right"] = tk.IntVar(value=defaults["right"])
    # vars["right"].trace_add("write", lambda a, b, c: screen_splitter.right_refresh(vars["right"].get) )

    vars["gutter"] = tk.IntVar(value=defaults["gutter"])
    # vars["gutter"].trace_add("write", lambda a, b, c: screen_splitter.gutter_refresh(vars["gutter"].get))



    # GRID =======================
    vars["cols"] = tk.IntVar(value=defaults["cols"])
    # vars["cols"].trace_add("write", lambda a, b, c: screen_splitter.col_refresh(vars["cols"].get))

    vars["rows"] = tk.IntVar(value=defaults["rows"])
    # vars["rows"].trace_add( "write", lambda a, b, c: screen_splitter.row_refresh(vars["rows"].get) )



    # NOW THE CORRESPONDING ENTRIES ==============================================
    def mk_entries(root: tk.Frame, vars: dict[str, tk.IntVar]):
        var_entries = {}
        for key, var in vars.items():
            if key == 'cols' or key == 'rows':
                key = f'# {key}'
            label = tk.Label(button_frame_left, text=key.title(), bg=ColorPalette.root_bg_color, justify=tk.LEFT, padx=20)

            entry = tk.Entry(
                button_frame_left,
                width=8,
                justify=tk.CENTER,
                textvariable=var,
                foreground=ColorPalette.text_color,
                bd=0,
                relief="flat",
                bg=ColorPalette.entry_bg_color,
                highlightthickness=1,
                highlightbackground=ColorPalette.canvas_bg_color,
                highlightcolor=ColorPalette.canvas_bg_color
                # style='pad.TEntry'
                # border=ColorPalette.root_bg_color
            )
            var_entries[key] = (label,entry)
        return var_entries

    def grid_entries(entries: dict[str,tuple[tk.Label,tk.Entry]]):
        i = 1
        for key, tuple in entries.items():
            tuple[0].grid(column=1,row=i,padx=10,pady=10,sticky=tk.W)
            tuple[1].grid(column=2,row=i,padx=10,ipady=5)
            if key == 'height' or key == 'gutter':
                i += 1
            i += 1
        tk.Label(button_frame_left,height=1,background=ColorPalette.root_bg_color).grid(row=3, pady=3)
        tk.Label(button_frame_left,height=1,background=ColorPalette.root_bg_color).grid(row=9, pady=3)
        tk.Label(button_frame_left,height=1,background=ColorPalette.root_bg_color).grid(row=12, pady=3)
        ...
    
    
    entries: dict[str,tuple[tk.Label,tk.Entry]] = mk_entries(root, vars)
    grid_entries(entries)




    entries["width"][1].bind("<Return>", lambda a: screen_splitter.width_refresh(vars["width"].get))
    entries["width"][1].bind("<FocusOut>", lambda a: screen_splitter.width_refresh(vars["width"].get))
    entries["width"][1].bind("<KP_Enter>", lambda a: screen_splitter.width_refresh(vars["width"].get))

    entries["height"][1].bind("<Return>", lambda a: screen_splitter.height_refresh(vars["height"].get))
    entries["height"][1].bind("<FocusOut>", lambda a: screen_splitter.height_refresh(vars["height"].get))
    entries["height"][1].bind("<KP_Enter>", lambda a: screen_splitter.height_refresh(vars["height"].get))



    entries["top"][1].bind("<Return>", lambda a: screen_splitter.top_refresh(vars["top"].get))
    entries["top"][1].bind("<FocusOut>", lambda a: screen_splitter.top_refresh(vars["top"].get))
    entries["top"][1].bind("<KP_Enter>", lambda a: screen_splitter.top_refresh(vars["top"].get))

    entries["left"][1].bind("<Return>", lambda a: screen_splitter.left_refresh(vars["left"].get))
    entries["left"][1].bind("<FocusOut>", lambda a: screen_splitter.left_refresh(vars["left"].get))
    entries["left"][1].bind("<KP_Enter>", lambda a: screen_splitter.left_refresh(vars["left"].get))

    entries["bottom"][1].bind("<Return>", lambda a: screen_splitter.bottom_refresh(vars["bottom"].get))
    entries["bottom"][1].bind("<FocusOut>", lambda a: screen_splitter.bottom_refresh(vars["bottom"].get))
    entries["bottom"][1].bind("<KP_Enter>", lambda a: screen_splitter.bottom_refresh(vars["bottom"].get))

    entries["right"][1].bind("<Return>", lambda a: screen_splitter.right_refresh(vars["right"].get))
    entries["right"][1].bind("<FocusOut>", lambda a: screen_splitter.right_refresh(vars["right"].get))
    entries["right"][1].bind("<KP_Enter>", lambda a: screen_splitter.right_refresh(vars["right"].get))

    entries["gutter"][1].bind("<Return>", lambda a: screen_splitter.gutter_refresh(vars["gutter"].get))
    entries["gutter"][1].bind("<FocusOut>", lambda a: screen_splitter.gutter_refresh(vars["gutter"].get))
    entries["gutter"][1].bind("<KP_Enter>", lambda a: screen_splitter.gutter_refresh(vars["gutter"].get))

    entries["# cols"][1].bind("<Return>", lambda a: screen_splitter.col_refresh(vars["cols"].get))
    entries["# cols"][1].bind("<FocusOut>", lambda a: screen_splitter.col_refresh(vars["cols"].get))
    entries["# cols"][1].bind("<KP_Enter>", lambda a: screen_splitter.col_refresh(vars["cols"].get))

    entries["# rows"][1].bind("<Return>", lambda a: screen_splitter.row_refresh(vars["rows"].get))
    entries["# rows"][1].bind("<FocusOut>", lambda a: screen_splitter.row_refresh(vars["rows"].get))
    entries["# rows"][1].bind("<KP_Enter>", lambda a: screen_splitter.row_refresh(vars["rows"].get))


    ##################################################################################
    ##################### BUTTON RIGHT FRAME #########################################
    ##################################################################################

    button_frame_right.columnconfigure(index=1,weight=1)
    button_frame_right.columnconfigure(index=2,weight=1)
    button_frame_right.rowconfigure(index=1,weight=1)
    button_frame_right.rowconfigure(index=2,weight=1)
    button_frame_right.rowconfigure(index=3,weight=1)
    button_frame_right.rowconfigure(index=4,weight=1)
    button_frame_right.rowconfigure(index=5,weight=1)
    button_frame_right.rowconfigure(index=6,weight=1)
    button_frame_right.option_add("*font",FontPalette.small)


    rotate_cw_file = Image.open('images/icn_rotatecw.png')
    rotate_cw_img = ImageTk.PhotoImage(rotate_cw_file)
    rotate_cw_icon = tk.Label(button_frame_right, image=rotate_cw_img)
    rotate_cw_text = tk.Label(button_frame_right, text="Rotate Clockwise", justify=tk.LEFT)
    
    rotate_cw_icon.grid(column=1,row=1,padx=5,pady=20)
    rotate_cw_text.grid(column=2,row=1,padx=10,sticky=tk.W)

    rotate_ccw_file = Image.open('images/icn_rotateccw.png')
    rotate_ccw_img = ImageTk.PhotoImage(rotate_ccw_file)
    rotate_ccw_icon = tk.Label(button_frame_right, image=rotate_ccw_img)
    rotate_ccw_text = tk.Label(button_frame_right, text="Rotate\nCounterclockwise", justify=tk.LEFT)
    
    rotate_ccw_icon.grid(column=1,row=2,padx=5,pady=20)
    rotate_ccw_text.grid(column=2,row=2,padx=10,sticky=tk.W)

    flipv_file = Image.open('images/icn_flipv.png')
    flipv_img = ImageTk.PhotoImage(flipv_file)
    flipv_icon = tk.Label(button_frame_right, image=flipv_img, justify=tk.RIGHT)
    flipv_text = tk.Label(button_frame_right, text="Flip Vertically", justify=tk.LEFT)
    
    flipv_icon.grid(column=1,row=3,padx=5,pady=20)
    flipv_text.grid(column=2,row=3,padx=10,sticky=tk.W)

    fliph_file = Image.open('images/icn_fliph.png')
    fliph_img = ImageTk.PhotoImage(fliph_file)
    fliph_icon = tk.Label(button_frame_right, image=fliph_img)
    fliph_text = tk.Label(button_frame_right, text="Flip Horizontally", justify=tk.LEFT)
    
    fliph_icon.grid(column=1,row=4,padx=5,pady=20)
    fliph_text.grid(column=2,row=4,padx=10,sticky=tk.W)



    delete_file = Image.open('images/icn_delete.png')
    delete_img = ImageTk.PhotoImage(delete_file)

    delete_icon = tk.Label(button_frame_right, image=delete_img)
    delete_text = tk.Label(button_frame_right, text="Delete all Screens", justify=tk.LEFT)
    
    delete_icon.grid(column=1,row=5,padx=10,pady=20)
    delete_text.grid(column=2,row=5,padx=10,sticky=tk.W)


    Label(button_frame_right,height=1).grid(row=6,columnspan=2)


    ##################################################################################
    ##################### RENDER BUTTON AND FOOTER ###################################
    ##################################################################################
    
    # RENDER BUTTON FRAME WIDGETS ================================
    # the render button
    render_bttn_img = Image.open('images/btn_render_flatter.png')
    render_bttn_img = ImageTk.PhotoImage(render_bttn_img)

    render_button = tk.Button(
        render_bttn_frame,
        text="Render Fusion Output",
        cursor="ibeam", 
        borderwidth=0,
        image=render_bttn_img
        )

    render_button = tk.Label(render_bttn_frame,
        image=render_bttn_img,cursor="pointinghand",
    )
    render_button.bind('<Button-1>', screen_splitter.export_for_fusion)


    # fusion studio checkbox
    fu_studio_checkbox = tk.Checkbutton(
        render_bttn_frame,
        text="Fusion Studio (no MediaIns or Outs)", 
        justify=tk.LEFT,
        variable=screen_splitter.fusion_studio, 
        # font="Archivo 10", 
        pady=10
        )

    # gridding...
    render_button.grid(     column=1, row=1, sticky=tk.N, pady=10)
    # fu_studio_checkbox.grid(column=1, row=2, sticky=tk.N)






    # FOOTER FRAME WIDGET ================================================
    ScreenSplitter.status_text = tk.StringVar()
    ScreenSplitter.status_text.trace_add('write',lambda a,b,c: clear_status_bar(screen_splitter))
    status_bar = tk.Label(footer, textvariable=ScreenSplitter.status_text)

    status_bar.pack(pady=25)
    





    # SELECTION RECTANGLE ==============================================
    rect = RectTracker(screen_splitter)
    rect.autodraw(fill="", width=0.5, outline="#D0D0D0", dash=(4, 4))

    
    
    root.mainloop()


if __name__ == "__main__":
    main()
