from __future__ import annotations
import tkinter as tk
import ss_classes as ss
from ss_export import load_defaults, render_fusion_output
from PIL import ImageTk
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
    coords = (event.x / self.winfo_width(), 1 - event.y / self.winfo_height())
    return coords


def clear_status_bar(cls: ScreenSplitter) -> None:
    cls.after(3500, lambda: cls.status_text.set(""))


def btn_on_hover(event: tk.Event, image: ImageTk.PhotoImage = None):
    event.widget.configure(image=image)


def set_hover_style(button: tk.Label, img_list: list[ImageTk.PhotoImage]):
    button.bind("<Enter>", lambda e: btn_on_hover(event=e, image=img_list[1]))
    button.bind("<Leave>", lambda e: btn_on_hover(event=e, image=img_list[0]))
    button.bind("<Button-1>", lambda e: btn_on_hover(event=e, image=img_list[2]))
    button.bind("<ButtonRelease-1>", lambda e: btn_on_hover(event=e, image=img_list[1]))


##################################################################################
#####################           CLASSES       ####################################
##################################################################################

###################         BLOCKS            ##########################
class ScreenBlock:
    screen_blocks: list[ScreenBlock] = None
    settings: dict[str, int | str] = None

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


class GridBlock:
    grid_blocks: list[GridBlock] = None
    settings = {}

    def __init__(self, tk_canvas: tk.Canvas, grid_cell: ss.GridCell, **config):
        self.canvas = tk_canvas
        self.grid_cell = grid_cell

        if grid_cell.index == 1:
            # GridBlock.settings = {}
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
    def create_all(cls, canvas: tk.Canvas, grid: ss.Grid, **config):
        if cls.grid_blocks is None:
            cls.grid_blocks = []
        cls.grid_blocks.clear()

        # creates grid cells from provided grid
        grid_block_screens = cls.blocks_from_grid(grid)

        # initializes grid block from generated cells
        for cell in grid_block_screens:
            GridBlock(canvas, cell, **config)

    def bind(self, event: str, function) -> None:
        self.canvas.tag_bind(self.tag, sequence=event, func=function)


###################         SCREEN SPLITTER         ####################
class ScreenSplitter(tk.Canvas):
    # Grid and Grid display
    ss_grid: ss.Grid = None
    grid_blocks: list[GridBlock] = None

    # Color Palette
    screen_color: str = None
    screen_color_pre_delete: str = None
    screen_color_hover: str = None

    # User Inputs
    vars: dict[str, tk.IntVar] = None
    entries: dict[str, tk.Entry] = None

    # CLICKING AND DRAGGING MECHANISM      ======================
    new_screen_coords: tuple[tuple[float, float], tuple[float, float]] = (
        (0.0, 0.0),
        (0.0, 0.0),
    )
    new_screen_indexes: tuple[int, int] = (0, 0)

    @classmethod
    def on_click(cls, event: tk.Event) -> None:
        self = event.widget

        item = self.find_closest(event.x, event.y)
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

    # SCREEN CREATION       =================================
    def create_screen(self) -> None:
        if ScreenSplitter.ss_grid is None:
            raise Exception("Please attach a grid first.")
        if ScreenSplitter.new_screen_indexes is None:
            return
        new_screen = ss.Screen.create_from_coords(
            ScreenSplitter.ss_grid, *ScreenSplitter.new_screen_indexes
        )
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

        id = new_screen_block.rect
        screen.id = id

        self.tag_bind(id, "<Button-2>", self.pre_delete_screen)
        self.tag_bind(id, "<Button-2> <Leave>", lambda e: self.cancel_deletion(id=id))
        self.tag_bind(id, "<Button-2> <ButtonRelease-2>", self.delete_screen)

    # SCREEN DELETION       =================================
    user_wants_to_delete = True

    def pre_delete_screen(self, event: tk.Event) -> None:
        id = self.find_closest(event.x, event.y)[0]
        self.itemconfig(
            id, fill=self.screen_color_pre_delete, outline=self.screen_color_pre_delete
        )

    def cancel_deletion(self=None, event: tk.Event = None, id=None) -> None:
        self.user_wants_to_delete = False
        self.itemconfig(id, fill=self.screen_color, outline=self.screen_color)

    def delete_screen(self, event: tk.Event):
        if not self.user_wants_to_delete:
            self.user_wants_to_delete = True
            return "break"

        canvas: tk.Canvas = event.widget
        screen_rect_id = canvas.find_closest(event.x, event.y)[0]
        self.delete(screen_rect_id)

        to_delete = [
            screen for screen in self.ss_grid.screens if screen.id == screen_rect_id
        ]
        self.ss_grid.screens.remove(*to_delete)
        self.user_wants_to_delete = True

    # SCREEN BATCH DELETION =================================
    def delete_all_screens(self, event):
        if not self.delete_screen_rectangles():
            return
        self.ss_grid.screens.clear()

    def pre_delete_all_screens(self, event):
        if self.ss_grid.screens is None:
            return
        ids_to_delete = [screen.id for screen in self.ss_grid.screens]
        for id in ids_to_delete:
            self.itemconfig(
                id,
                fill=self.screen_color_pre_delete,
                outline=self.screen_color_pre_delete,
            )

    # SCREEN SELECTION (not implemented)
    selected_screen = None

    def select_screen(self, event: tk.Event):
        ...

    def mark_selected(self):
        ...

    def deselect_screen(self, event):
        ...

    # LINK OR UNLINK MARGIN CONTROL     ======================
    def link_margins(self, event: tk.Event):
        lbr = {k: self.entries[k][1] for k in ("left", "bottom", "right")}
        for mg in lbr.values():
            mg.configure(state="disabled")

        # rebind
        event.widget.unbind("<Button-1>")
        event.widget.bind("<Button-1>", self.unlink_margins)

        self.all_mg_refresh(self.vars["top"].get)

        # change labels
        self.entries["top"][0].configure(text="Margin")
        self.entries["left"][0].configure(foreground=ColorPalette.TEXT_DARKER)
        self.entries["bottom"][0].configure(foreground=ColorPalette.TEXT_DARKER)
        self.entries["right"][0].configure(foreground=ColorPalette.TEXT_DARKER)

        self.entries["top"][1].unbind("<Return>")
        self.entries["top"][1].unbind("<FocusOut>")
        self.entries["top"][1].unbind("<KP_Enter>")
        self.entries["top"][1].bind(
            "<Return>", lambda a: self.all_mg_refresh(self.vars["top"].get)
        )
        self.entries["top"][1].bind(
            "<FocusOut>", lambda a: self.all_mg_refresh(self.vars["top"].get)
        )
        self.entries["top"][1].bind(
            "<KP_Enter>", lambda a: self.all_mg_refresh(self.vars["top"].get)
        )
        # self.global_refresh()
        self.update_all_vars()

    def unlink_margins(self, event):
        lbr = {k: self.entries[k][1] for k in ("left", "bottom", "right")}
        for mg in lbr.values():
            mg.configure(state=tk.NORMAL)

        # rebind
        event.widget.unbind("<Button-1>")
        event.widget.bind("<Button-1>", self.link_margins)

        # change labels
        self.entries["top"][0].configure(text="Top")
        self.entries["left"][0].configure(foreground=ColorPalette.TEXT)
        self.entries["bottom"][0].configure(foreground=ColorPalette.TEXT)
        self.entries["right"][0].configure(foreground=ColorPalette.TEXT)

        self.entries["top"][1].unbind("<Return>")
        self.entries["top"][1].unbind("<FocusOut>")
        self.entries["top"][1].unbind("<KP_Enter>")

        self.entries["top"][1].bind(
            "<Return>", lambda a: self.top_refresh(self.vars["top"].get)
        )
        self.entries["top"][1].bind(
            "<FocusOut>", lambda a: self.top_refresh(self.vars["top"].get)
        )
        self.entries["top"][1].bind(
            "<KP_Enter>", lambda a: self.top_refresh(self.vars["top"].get)
        )

    @classmethod
    def update_all_vars(cls):
        cls.vars["width"].set(cls.ss_grid.canvas.width)
        cls.vars["height"].set(cls.ss_grid.canvas.height)

        cls.vars["top"].set(cls.ss_grid.margin._top_px)
        cls.vars["left"].set(cls.ss_grid.margin._left_px)
        cls.vars["bottom"].set(cls.ss_grid.margin._bottom_px)
        cls.vars["right"].set(cls.ss_grid.margin._right_px)
        cls.vars["gutter"].set(cls.ss_grid.margin._gutter_px)

        cls.vars["cols"].set(cls.ss_grid.cols)
        cls.vars["rows"].set(cls.ss_grid.rows)

    # TRANSFORMATION METHODS
    def flip_h(self, event):
        if not self.ss_grid.flip_horizontally():
            return
        self.screens_only_refresh()

    def flip_v(self, event):
        if not self.ss_grid.flip_vertically():
            return
        self.screens_only_refresh()

    def rotate_cw(self, event):
        self.ss_grid.rotate_clockwise()
        if self.ss_grid.screens is not None:
            for screen in self.ss_grid.screens:
                screen.rotate_clockwise()

        self.global_refresh()
        self.update_all_vars()
        ...

    def rotate_ccw(self, event):
        self.ss_grid.rotate_counterclockwise()
        self.global_refresh()
        self.update_all_vars()
        ...

    # REFRESHING METHODS        =================================
    # GLOBAL
    def global_refresh(
        self, canvas_changed: tuple[bool, bool] = (False, False)
    ) -> None:
        if canvas_changed[0]:
            self.configure(width=self.ss_grid.canvas.width)
        if canvas_changed[1]:
            self.configure(height=self.ss_grid.canvas.height)

        self.update_dims()

        GridBlock.create_all(self, self.ss_grid)

        self.delete("all")
        GridBlock.draw_all()
        if self.ss_grid.screens is None:
            return
        for screen in self.ss_grid.screens:
            self.draw_screen(screen)

    # canvas
    def width_refresh(self, func: function):
        newset = func()
        oldset = self.ss_grid.canvas.width
        if oldset == newset:
            return

        self.ss_grid.canvas.width = newset
        self.global_refresh((True, False))

    def height_refresh(self, func: function):
        newset = func()
        oldset = self.ss_grid.canvas.height
        if oldset == newset:
            return

        self.ss_grid.canvas.height = newset
        self.global_refresh((False, True))

    # margin
    def all_mg_refresh(self, func: function):
        newset = func()

        top = self.ss_grid.margin._top_px
        left = self.ss_grid.margin._left_px
        bottom = self.ss_grid.margin._bottom_px
        right = self.ss_grid.margin._right_px

        if top == left == bottom == right == newset:
            return

        self.ss_grid.margin.all = newset
        self.global_refresh()
        self.update_all_vars()

    def top_refresh(self, func: function):
        newset = func()
        oldset = self.ss_grid.margin._top_px
        if oldset == newset:
            return

        self.ss_grid.margin.top = newset
        self.global_refresh()

    def left_refresh(self, func: function):
        newset = func()
        oldset = self.ss_grid.margin._left_px
        if oldset == newset:
            return

        self.ss_grid.margin.left = newset
        self.global_refresh()

    def bottom_refresh(self, func: function):
        newset = func()
        oldset = self.ss_grid.margin._bottom_px
        if oldset == newset:
            return

        self.ss_grid.margin.bottom = newset
        self.global_refresh()

    def right_refresh(self, func: function):
        newset = func()
        oldset = self.ss_grid.margin._right_px
        if oldset == newset:
            return

        self.ss_grid.margin.right = newset
        self.global_refresh()

    def gutter_refresh(self, func: function):
        newset = func()
        oldset = self.ss_grid.margin._gutter_px
        if oldset == newset:
            return

        self.ss_grid.margin.gutter = newset
        self.global_refresh()

    # grid
    def col_refresh(self, func: function):
        newset = func()
        oldset = self.ss_grid.cols
        if oldset == newset:
            return

        self.ss_grid.cols = newset
        self.global_refresh()

    def row_refresh(self, func: function):
        newset = func()
        oldset = self.ss_grid.rows
        if oldset == newset:
            return

        self.ss_grid.rows = newset
        self.global_refresh()

    # screens
    def screens_only_refresh(self):
        if not self.delete_screen_rectangles():
            return

        # redraw everything
        for screen in self.ss_grid.screens:
            self.draw_screen(screen)

    def delete_screen_rectangles(self) -> bool:
        if self.ss_grid.screens is None:
            return False

        # delete actual rectangles
        ids_to_delete = [screen.id for screen in self.ss_grid.screens]
        for id in ids_to_delete:
            self.delete(id)

        return True

    # CANVAS DISPLAY METHODS ==========================================
    max_width = 750
    max_height = 550

    scale_var: tk.DoubleVar() = None
    scale_text: tk.StringVar() = None

    def compute_dims(self) -> tuple[int]:
        canvas = self.ss_grid.canvas
        aspect_ratio = canvas.aspect_ratio

        max_width = self.max_width
        max_height = self.max_height

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

    # IO METHODS            ==========================================
    fusion_export: str = None  # for saving
    status_text = None  # for announcing
    fusion_studio: tk.BooleanVar = None

    @classmethod
    def export_for_fusion(cls, event: tk.Event) -> None:
        if cls.ss_grid.screens is None:
            return
        screen_values = []
        for screen in cls.ss_grid.screens:
            screen_values.append(screen.get_values())
        cls.fusion_export = render_fusion_output(
            screen_values, cls.ss_grid.canvas.resolution, cls.fusion_studio.get()
        )
        pyperclip.copy(cls.fusion_export)
        if cls.status_text is None:
            cls.status_text = tk.StringVar()
        cls.status_text.set("Node tree successfuly copied to clipboard.")

    def save_splitscreener_preset():
        ...

    def save_fusion_preset():
        ...

    def reset_defaults():
        ...

    def save_new_defaults():
        ...


###################         RECT TRACKER            ####################
class RectTracker:
    def __init__(self, canvas: tk.Canvas):
        self.canvas = canvas
        self.item = None

    def draw(self, start: list[int, int], end: list[int, int], **opts):
        """Draw the rectangle"""
        return self.canvas.create_rectangle(*(list(start) + list(end)), **opts)

    def autodraw(self, **opts):
        """Setup automatic drawing; supports command option"""
        self.start = None
        self.canvas.bind("<Button-1>", self.__update, "+")
        self.canvas.bind("<B1-Motion>", self.__update, "+")
        self.canvas.bind("<ButtonRelease-1>", self.__stop, "+")

        self.rectopts = opts

    def __update(self, event: tk.Event):
        if not self.start:
            self.start = [event.x, event.y]
            return

        if self.item is not None:
            self.canvas.delete(self.item)
        self.item = self.draw(self.start, (event.x, event.y), **self.rectopts)
        # self._command(self.start, (event.x, event.y))

    def __stop(self, event: tk.Event):
        self.start = None
        self.canvas.delete(self.item)
        self.item = None


###################         STYLE PALETTES          ####################
class ColorPalette:
    # root
    ROOT_BG = "#282828"
    TEXT = "#D0D0D0"
    TEXT_DARKER = "#A3A3A3"

    # canvas
    CANVAS_BG = "#141414"
    CANVAS_BLOCK = "#282828"
    CANVAS_BLOCK_HOVER = "#303030"
    CANVAS_SCREEN = "#0070D4"
    CANVAS_SCREEN_PRE_DELETE = "#193470"
    CANVAS_SCREEN_HOVER = "#258BE6"

    # entries
    ENTRY_BG = "#1F1F1F"


class ImgPalette:
    # app icon
    app_icon = "app_icon.icns"

    # right column icons
    icn_rotate_cw = [
        "icn_rotatecw_state1.png",
        "icn_rotatecw_state2.png",
        "icn_rotatecw_state3.png",
    ]
    icn_rotate_ccw = [
        "icn_rotateccw_state1.png",
        "icn_rotateccw_state2.png",
        "icn_rotateccw_state3.png",
    ]
    icn_flip_v = [
        "icn_flipv_state1.png",
        "icn_flipv_state2.png",
        "icn_flipv_state3.png",
    ]
    icn_flip_h = [
        "icn_fliph_state1.png",
        "icn_fliph_state2.png",
        "icn_fliph_state3.png",
    ]
    icn_delete_all = [
        "icn_trash_state1.png",
        "icn_trash_state2.png",
        "icn_trash_state3.png",
    ]

    # app logo
    app_logo = "ss_logo_spaced.png"

    # render button
    btn_render = "btn_render_flatter.png"

    # link bracket
    icn_lbracket_top = "lbracket1.png"
    icn_lbracket_bottom = "lbracket2.png"

    icn_link = ["icn_link_state1.png", "icn_link_state2.png", "icn_link_state3.png"]


class Defaults:
    def __init__(self):
        defaults_raw = load_defaults("defaults.json")
        defaults = {}
        for key in defaults_raw.keys():
            for key, value in defaults_raw[key].items():
                defaults[key] = value
        self.grid = defaults


##################################################################################
#####################       SPLITSCREENER APP       ##############################
##################################################################################
def main():

    root = tk.Tk()

    # FONT PALETTE ========================================================
    class FontPalette:
        # main = Font(family="Archivo SemiExpanded Light")
        # small = Font(family="Archivo SemiExpanded Light", size=12)
        main = "TkDefaultFont"
        small = "TkSmallCaptionFont 12"

    # LOADING SPLITSCREENER DEFAULTS =========================================
    df = Defaults()
    defaults = df.grid

    # SPLITSCREENER INITIALIZERS ======================================
    ss_canvas = ss.Canvas((defaults["width"], defaults["height"]))
    ss_margin = ss.Margin(
        ss_canvas,
        tlbr=(defaults["top"], defaults["left"], defaults["bottom"], defaults["right"]),
        gutter=defaults["gutter"],
    )
    ss_grid = ss.Grid(ss_canvas, ss_margin, (defaults["cols"], defaults["rows"]))

    ##################################################################################
    #####################       ROOT & SETUP      ####################################
    ##################################################################################

    cp = ColorPalette()
    fp = FontPalette()
    ip = ImgPalette()

    # root.iconbitmap(ip.app_icon)

    # ROOT CONFIGS =========================================================
    root.configure(bg=cp.ROOT_BG)
    root.option_add("*font", fp.main)
    root.option_add("*foreground", cp.TEXT)
    root.option_add("*Entry.foreground", cp.TEXT)
    root.option_add("*Entry.background", cp.ENTRY_BG)
    root.option_add("*Entry.disabledbackground", cp.TEXT_DARKER)
    root.option_add("*background", cp.ROOT_BG)
    root.option_add("*Checkbutton.font", fp.small)
    root.minsize(1260, 740)
    root.title("SplitScreener 1.0")
    # root.resizable(False,False)

    # SETTING UP THE MAIN TK GRID ======================================================
    root.columnconfigure(index=1, weight=1, minsize=220)  # LEFT SIDEBAR
    root.columnconfigure(index=2, weight=1, minsize=820)  # MAIN SECTION, THE CREATOR
    root.columnconfigure(
        index=3, weight=1, minsize=220
    )  # RIGHT SIDEBAR (nothing there yet)
    root.rowconfigure(index=1, weight=3)  # HEADER
    root.rowconfigure(index=2, weight=1)  # MAIN SECTION, THE CREATOR FRAME AND SETTINGS
    root.rowconfigure(index=3, weight=1)  # THE RENDER BUTTON FRAME
    root.rowconfigure(index=4, weight=3)  # FOOTER

    # CREATING THE FRAMES
    header = tk.Frame(root)
    button_frame_left = tk.Frame(root)
    creator_frame = tk.Frame(root)
    button_frame_right = tk.Frame(root)
    render_bttn_frame = tk.Frame(root)
    footer = tk.Frame(root)

    # adding them to the grid
    header.grid(column=1, row=1, columnspan=3)
    button_frame_left.grid(column=1, row=2)
    creator_frame.grid(column=2, row=2, padx=10, pady=10)
    button_frame_right.grid(column=3, row=2, ipadx=20)
    render_bttn_frame.grid(column=2, row=3)
    footer.grid(column=1, row=4, columnspan=3)

    ##################################################################################
    #####################       HEADER      ##########################################
    ##################################################################################

    # APP LOGO
    logo = ImageTk.PhotoImage(file=ip.app_logo)

    # APP TITLE
    app_title = tk.Label(header, height=100, justify=tk.CENTER, image=logo)
    app_title.pack(anchor=tk.S, pady=20)

    ##################################################################################
    #####################       SCREEN SPLITTER  #####################################
    ##################################################################################
    screen_splitter = ScreenSplitter(
        creator_frame,
        background=cp.CANVAS_BG,
        bd=0,
        highlightthickness=0,
        relief="ridge",
    )
    ScreenSplitter.ss_grid = ss_grid
    ScreenSplitter.scale_var = tk.DoubleVar()
    ScreenSplitter.scale_text = tk.StringVar()
    ScreenSplitter.screen_color: str = cp.CANVAS_SCREEN
    ScreenSplitter.screen_color_pre_delete = cp.CANVAS_SCREEN_PRE_DELETE
    ScreenSplitter.screen_color_hover = cp.CANVAS_SCREEN_HOVER
    ScreenSplitter.fusion_studio: tk.BooleanVar = tk.BooleanVar()

    screen_splitter.update_dims()

    # instruction_label = tk.Label(creator_frame, text="Click and drag below to draw your first Screen.", font=fp.small)

    # BINDING FOR CLICK AND DRAG SCREEN ADD =======================
    screen_splitter.bind("<Button-1>", screen_splitter.on_click)
    screen_splitter.bind("<ButtonRelease-1>", screen_splitter.on_release)

    # SCALE LABEL ====================================================================
    scale_label = tk.Label(
        creator_frame,
        font=fp.small,
        textvariable=screen_splitter.scale_text,
        justify=tk.RIGHT,
        bg=cp.ROOT_BG,
        foreground=cp.TEXT_DARKER,
    )

    # instruction_label.grid( row=1,  sticky=tk.W)
    screen_splitter.grid(row=2, ipadx=20, pady=5)
    scale_label.grid(row=3, sticky=tk.NE)

    # RENDERING GRID BLOCKS ======================================================
    GridBlock.create_all(
        screen_splitter,
        ss_grid,
        fill=cp.CANVAS_BLOCK,
        activefill=cp.CANVAS_BLOCK_HOVER,
        outline=cp.CANVAS_BLOCK,
        activeoutline=cp.CANVAS_BLOCK,
        activewidth=1,
    )
    GridBlock.draw_all()

    # SELECTION RECTANGLE ==============================================
    rect = RectTracker(screen_splitter)
    rect.autodraw(fill="", width=0.5, outline=cp.TEXT_DARKER, dash=(4, 4))

    ##################################################################################
    ##################### BUTTON LEFT FRAME ##########################################
    ##################################################################################

    # TKINTER VARIABLES FOR USER GRID SETTINGS ========================================
    vars: dict[str, tk.IntVar] = {}

    # CANVAS =======================
    vars["width"] = tk.IntVar(value=defaults["width"])

    vars["height"] = tk.IntVar(value=defaults["height"])

    # MARGIN =======================
    vars["top"] = tk.IntVar(value=defaults["top"])

    vars["left"] = tk.IntVar(value=defaults["left"])

    vars["bottom"] = tk.IntVar(value=defaults["bottom"])

    vars["right"] = tk.IntVar(value=defaults["right"])

    vars["gutter"] = tk.IntVar(value=defaults["gutter"])

    # GRID =======================
    vars["cols"] = tk.IntVar(value=defaults["cols"])

    vars["rows"] = tk.IntVar(value=defaults["rows"])

    ScreenSplitter.vars = vars

    # LINK MARGINS ======================================================================
    # top bracket
    lbracket_top_image = ImageTk.PhotoImage(file=ip.icn_lbracket_top)
    lbracket_top = tk.Label(button_frame_left, image=lbracket_top_image)
    lbracket_top.grid(column=2, row=4, rowspan=2, sticky=tk.E, padx=11)

    # link button
    link_margins_image = [ImageTk.PhotoImage(file=ip.icn_link[x]) for x in range(3)]
    link_margins = tk.Label(button_frame_left, image=link_margins_image[0])
    link_margins.grid(column=2, row=5, rowspan=2, sticky=tk.W, padx=9)
    set_hover_style(link_margins, link_margins_image)
    link_margins.bind("<Button-1>", screen_splitter.link_margins, add="+")

    # bottom bracket
    lbracket_btm_image = ImageTk.PhotoImage(file=ip.icn_lbracket_bottom)
    lbracket_btm = tk.Label(button_frame_left, image=lbracket_btm_image)
    lbracket_btm.grid(column=2, row=6, rowspan=2, sticky=tk.E, padx=11)

    tk.Frame(button_frame_left, width=10).grid(column=1)

    # ENTRIES FOR USER INPUT ==============================================
    def mk_entries(parent: tk.Frame, vars: dict[str, tk.IntVar]):
        var_entries = {}
        for key, var in vars.items():
            new_key = key
            if key == "cols" or key == "rows":
                new_key = f"# {key}"
            label = tk.Label(
                parent, text=new_key.title(), bg=cp.ROOT_BG, justify=tk.LEFT, padx=20
            )

            entry = tk.Entry(
                parent,
                width=8,
                justify=tk.CENTER,
                textvariable=var,
                foreground=cp.TEXT,
                bd=0,
                relief="flat",
                bg=cp.ENTRY_BG,
                highlightthickness=1,
                highlightbackground=cp.CANVAS_BG,
                highlightcolor=cp.CANVAS_BG,
                disabledbackground=cp.CANVAS_BLOCK,
            )
            var_entries[key] = (label, entry)
        return var_entries

    def grid_entries(entries: dict[str, tuple[tk.Label, tk.Entry]]):
        i = 1
        for key, tuple in entries.items():
            tuple[0].grid(column=3, row=i, padx=0, pady=10, sticky=tk.W)
            tuple[1].grid(column=4, row=i, padx=10, ipady=5)
            if key == "height" or key == "gutter":
                i += 1
            i += 1

        # adds spacers
        tk.Label(button_frame_left, height=1, background=cp.ROOT_BG).grid(
            column=2, row=3, pady=3
        )
        tk.Label(button_frame_left, height=1, background=cp.ROOT_BG).grid(
            column=2, row=9, pady=3
        )
        tk.Label(button_frame_left, height=1, background=cp.ROOT_BG).grid(
            column=2, row=12, pady=3
        )

    entries: dict[str, tuple[tk.Label, tk.Entry]] = mk_entries(button_frame_left, vars)
    grid_entries(entries)

    ScreenSplitter.entries = entries

    # BINDING ENTRIES TO REFRESH FUNCS ======================================================================
    entries["width"][1].bind(
        "<Return>", lambda a: screen_splitter.width_refresh(vars["width"].get)
    )
    entries["width"][1].bind(
        "<FocusOut>", lambda a: screen_splitter.width_refresh(vars["width"].get)
    )
    entries["width"][1].bind(
        "<KP_Enter>", lambda a: screen_splitter.width_refresh(vars["width"].get)
    )

    entries["height"][1].bind(
        "<Return>", lambda a: screen_splitter.height_refresh(vars["height"].get)
    )
    entries["height"][1].bind(
        "<FocusOut>", lambda a: screen_splitter.height_refresh(vars["height"].get)
    )
    entries["height"][1].bind(
        "<KP_Enter>", lambda a: screen_splitter.height_refresh(vars["height"].get)
    )

    entries["top"][1].bind(
        "<Return>", lambda a: screen_splitter.top_refresh(vars["top"].get)
    )
    entries["top"][1].bind(
        "<FocusOut>", lambda a: screen_splitter.top_refresh(vars["top"].get)
    )
    entries["top"][1].bind(
        "<KP_Enter>", lambda a: screen_splitter.top_refresh(vars["top"].get)
    )

    entries["left"][1].bind(
        "<Return>", lambda a: screen_splitter.left_refresh(vars["left"].get)
    )
    entries["left"][1].bind(
        "<FocusOut>", lambda a: screen_splitter.left_refresh(vars["left"].get)
    )
    entries["left"][1].bind(
        "<KP_Enter>", lambda a: screen_splitter.left_refresh(vars["left"].get)
    )

    entries["bottom"][1].bind(
        "<Return>", lambda a: screen_splitter.bottom_refresh(vars["bottom"].get)
    )
    entries["bottom"][1].bind(
        "<FocusOut>", lambda a: screen_splitter.bottom_refresh(vars["bottom"].get)
    )
    entries["bottom"][1].bind(
        "<KP_Enter>", lambda a: screen_splitter.bottom_refresh(vars["bottom"].get)
    )

    entries["right"][1].bind(
        "<Return>", lambda a: screen_splitter.right_refresh(vars["right"].get)
    )
    entries["right"][1].bind(
        "<FocusOut>", lambda a: screen_splitter.right_refresh(vars["right"].get)
    )
    entries["right"][1].bind(
        "<KP_Enter>", lambda a: screen_splitter.right_refresh(vars["right"].get)
    )

    entries["gutter"][1].bind(
        "<Return>", lambda a: screen_splitter.gutter_refresh(vars["gutter"].get)
    )
    entries["gutter"][1].bind(
        "<FocusOut>", lambda a: screen_splitter.gutter_refresh(vars["gutter"].get)
    )
    entries["gutter"][1].bind(
        "<KP_Enter>", lambda a: screen_splitter.gutter_refresh(vars["gutter"].get)
    )

    entries["cols"][1].bind(
        "<Return>", lambda a: screen_splitter.col_refresh(vars["cols"].get)
    )
    entries["cols"][1].bind(
        "<FocusOut>", lambda a: screen_splitter.col_refresh(vars["cols"].get)
    )
    entries["cols"][1].bind(
        "<KP_Enter>", lambda a: screen_splitter.col_refresh(vars["cols"].get)
    )

    entries["rows"][1].bind(
        "<Return>", lambda a: screen_splitter.row_refresh(vars["rows"].get)
    )
    entries["rows"][1].bind(
        "<FocusOut>", lambda a: screen_splitter.row_refresh(vars["rows"].get)
    )
    entries["rows"][1].bind(
        "<KP_Enter>", lambda a: screen_splitter.row_refresh(vars["rows"].get)
    )

    ##################################################################################
    ##################### BUTTON RIGHT FRAME #########################################
    ##################################################################################

    button_frame_right.columnconfigure(index=1, weight=1)
    button_frame_right.columnconfigure(index=2, weight=1)
    button_frame_right.rowconfigure(index=1, weight=1)
    button_frame_right.rowconfigure(index=2, weight=1)
    button_frame_right.rowconfigure(index=3, weight=1)
    button_frame_right.rowconfigure(index=4, weight=1)
    button_frame_right.rowconfigure(index=5, weight=1)
    button_frame_right.rowconfigure(index=6, weight=1)
    button_frame_right.option_add("*font", fp.small)

    # Rotate Clockwise
    rotate_cw_img = [ImageTk.PhotoImage(file=ip.icn_rotate_cw[x]) for x in range(3)]
    rotate_cw_icon = tk.Label(button_frame_right, image=rotate_cw_img[0])
    rotate_cw_text = tk.Label(
        button_frame_right, text="Rotate Clockwise", justify=tk.LEFT
    )
    set_hover_style(rotate_cw_icon, rotate_cw_img)

    # rotate_cw_icon.bind("<Button-1>", screen_splitter.rotate_cw_img, add='+')
    rotate_cw_icon.grid(column=1, row=1, padx=5, pady=20)
    rotate_cw_text.grid(column=2, row=1, padx=10, sticky=tk.W)

    # Rotate Counterclockwise
    rotate_ccw_img = [ImageTk.PhotoImage(file=ip.icn_rotate_ccw[x]) for x in range(3)]
    rotate_ccw_icon = tk.Label(button_frame_right, image=rotate_ccw_img[0])
    rotate_ccw_text = tk.Label(
        button_frame_right, text="Rotate\nCounterclockwise", justify=tk.LEFT
    )
    set_hover_style(rotate_ccw_icon, rotate_ccw_img)

    # rotate_ccw_icon.bind("<Button-1>", screen_splitter.rotate_ccw, add='+')
    rotate_ccw_icon.grid(column=1, row=2, padx=5, pady=20)
    rotate_ccw_text.grid(column=2, row=2, padx=10, sticky=tk.W)

    # Flip Vertically
    flipv_img = [ImageTk.PhotoImage(file=ip.icn_flip_v[x]) for x in range(3)]
    flipv_icon = tk.Label(button_frame_right, image=flipv_img[0])
    flipv_text = tk.Label(button_frame_right, text="Flip Vertically", justify=tk.LEFT)

    set_hover_style(flipv_icon, flipv_img)

    flipv_icon.bind("<Button-1>", screen_splitter.flip_v, add="+")

    flipv_icon.grid(column=1, row=3, padx=5, pady=20)
    flipv_text.grid(column=2, row=3, padx=10, sticky=tk.W)

    # Flip Horizontally
    fliph_img = [ImageTk.PhotoImage(file=ip.icn_flip_h[x]) for x in range(3)]
    fliph_icon = tk.Label(button_frame_right, image=fliph_img[0])
    fliph_text = tk.Label(button_frame_right, text="Flip Horizontally", justify=tk.LEFT)

    set_hover_style(fliph_icon, fliph_img)

    fliph_icon.bind("<Button-1>", screen_splitter.flip_h, add="+")

    fliph_icon.grid(column=1, row=4, padx=5, pady=20)
    fliph_text.grid(column=2, row=4, padx=10, sticky=tk.W)

    # Delete all screens
    delete_img = [ImageTk.PhotoImage(file=ip.icn_delete_all[x]) for x in range(3)]

    delete_icon = tk.Label(button_frame_right, image=delete_img[0])
    delete_text = tk.Label(
        button_frame_right, text="Delete all Screens", justify=tk.LEFT
    )
    set_hover_style(delete_icon, delete_img)

    delete_icon.bind("<Button-1>", screen_splitter.pre_delete_all_screens, add="+")
    delete_icon.bind("<ButtonRelease-1>", screen_splitter.delete_all_screens, add="+")

    delete_icon.grid(column=1, row=5, padx=5, pady=20)
    delete_text.grid(column=2, row=5, padx=10, sticky=tk.W)

    # spacer
    tk.Label(button_frame_right, height=1).grid(row=6, columnspan=2)

    ##################################################################################
    ##################### RENDER BUTTON AND FOOTER ###################################
    ##################################################################################

    render_bttn_img = ImageTk.PhotoImage(file=ip.btn_render)

    render_button = tk.Button(
        render_bttn_frame,
        text="Render Fusion Output",
        cursor="ibeam",
        borderwidth=0,
        image=render_bttn_img,
    )

    render_button = tk.Label(
        render_bttn_frame,
        image=render_bttn_img,
        cursor="pointinghand",
    )
    render_button.bind("<Button-1>", screen_splitter.export_for_fusion)
    render_button.grid(column=1, row=1, sticky=tk.N, pady=20)

    # FOOTER FRAME ================================================
    ScreenSplitter.status_text = tk.StringVar()
    ScreenSplitter.status_text.trace_add(
        "write", lambda a, b, c: clear_status_bar(screen_splitter)
    )
    status_bar = tk.Label(
        footer,
        textvariable=ScreenSplitter.status_text,
        justify=tk.CENTER,
        foreground=cp.TEXT_DARKER,
    )

    status_bar.pack(pady=15)
    tk.Frame(footer, height=15).pack()

    root.mainloop()


if __name__ == "__main__":
    main()
