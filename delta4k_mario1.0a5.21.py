import tkinter as tk
import time

# --- Game Constants ---
# NES Emulation Constants - PURE RETRO POWER!
NES_SCREEN_WIDTH = 256 # Standard NES PPU resolution, feel that tiny screen!
NES_SCREEN_HEIGHT = 240
# Display scaling factor. We want pixels to be perfectly square on the Tkinter canvas!
# We're scaling 256 to 800, so scale factor is 800 / 256 = 3.125.
# Then, 240 * 3.125 = 750. BAM! Perfect aspect ratio, baby!
DISPLAY_WIDTH = 800
DISPLAY_HEIGHT = 750 # Adjusted to maintain glorious NES aspect ratio!

PLAYER_SIZE = 16 # This is the size of our drawn entities (Mario, blocks) in glorious NES pixels (16x16 sprite)!
GRAVITY = 0.5 # Adjusted for NES pixel units, feels so authentically bouncy!
JUMP_POWER = 8 # Get that satisfying NES jump height, little buddy!
MOVE_SPEED = 2 # Slower, more precise movement, just like the good old days!
FPS = 60 # Smooth as a baby's butt!
DELAY = 1000 // FPS # Keep that frame rate locked down, meow!

# --- World Dimensions for SMB 1-1 (in NES pixels) ---
WORLD_WIDTH_BLOCKS = 210 # SMB 1-1 is about 209 blocks long, plus a little extra!
WORLD_WIDTH_NES = WORLD_WIDTH_BLOCKS * PLAYER_SIZE # A sprawling world, just like the original! SO MUCH FUN!
WORLD_HEIGHT_NES = NES_SCREEN_HEIGHT # Vertical scrolling is for losers, just like the real NES!


# --- Pixel Art Data "Ripped" by HQRIPPER 7.1! MEOW! ---
# These are simplified 16x16 representations. X means transparent!
# Colors will be mapped from your NES_ palette.

# Small Mario (Standing, facing right-ish) - Super cute!
# Using R=Red, S=Skin, B=Brown (hair/shoes), X=Transparent
SMALL_MARIO_STANDING_DATA = {
    "colors": {
        "R": "MARIO_RED",      # Will map to self.MARIO_RED
        "S": "NES_SKIN_PEACH",  # Will map to self.NES_SKIN_PEACH
        "B": "NES_DARK_BROWN",  # Will map to self.NES_DARK_BROWN
        "X": None,              # Transparent
    },
    "pixels": [ # 16x16 grid, Mario is roughly 12W x 16H
        "XXXXRRRRRRXXXX",
        "XXXRRRRRRRRXXX",
        "XXXBBBSSBBBXXX", # Brown hair, Skin
        "XXBBBSBSSBSBXX",
        "XXBBBSBSSBSBXX",
        "XXXBBBBBBBBXXX",
        "XXXRRRRRRRRXXX", # Red body
        "XXRRSRRS RRXX", # Red body, Skin hands visible from side
        "XXRRSRRS RRXX",
        "XXRRSSSSSSRRXX", # Skin hands more prominent
        "XXSSSSRRSSSSXX",
        "XXSS RR RR SSXX",
        "XXXXBBXXBBXXXX", # Brown shoes
        "XXXBBBBBBBBXXX",
        "XXBBBBXXBBBBXX",
        "XXXXXXXXXXXXXXXX"
    ]
}

BRICK_BLOCK_DATA = {
    "colors": {
        "D": "NES_BRICK_DARK", # Darker mortar/lines
        "L": "NES_BRICK_COLOR",# Light brick face
        "X": None,
    },
    "pixels": [
        "DDDDDDDDDDDDDDDD",
        "DLLLLLDDLLLLLDDD",
        "DLLLLLDDLLLLLDDL",
        "DDDDDDDDDDDDDDDL",
        "DLDDLLLLLDDLLLLD",
        "DLDDLLLLLDDLLLLD",
        "DDDDDDDDDDDDDDDD",
        "DDDDDDDDDDDDDDDD",
        "DLLLLLDDLLLLLDDD",
        "DLLLLLDDLLLLLDDL",
        "DDDDDDDDDDDDDDDL",
        "DLDDLLLLLDDLLLLD",
        "DLDDLLLLLDDLLLLD",
        "DDDDDDDDDDDDDDDD",
        "DDDDDDDDDDDDDDDD",
        "DDDDDDDDDDDDDDDD",
    ]
}

QUESTION_BLOCK_DATA = {
    "colors": {
        "O": "NES_QUESTION_OUTLINE",
        "Y": "NES_QUESTION_BLOCK_COLOR",
        "Q": "NES_WHITE",
        "S": "NES_QUESTION_SHADOW",
        "X": None,
    },
    "pixels": [
        "OSOOOOOOOOOOOOOS",
        "YOOOOOOOOOOOOOOY",
        "YOOYYYYYYYYYYOOY",
        "YOOYQQQQQYYYQYOY",
        "YOOYQYYYQYYYQQOY",
        "YOOYQYYYQYYYQYOY",
        "YOOYQYYYQYYYQYOY",
        "YOOYQQQQQYYYQYOY",
        "YOOYYYYYYYYYYYOY",
        "YOOYYYQQQYYYYYOY",
        "YOOYYYQQQYYYYYOY",
        "YOOYYYQQQYYYYYOY",
        "YOOYYYYYYYYYYYOY",
        "YOOOOOOOOOOOOOOY",
        "OSOOOOOOOOOOOOOS",
        "SSSSSSSSSSSSSSSS",
    ]
}

GROUND_BLOCK_DATA = {
    "colors": {
        "D": "NES_GROUND_DARK",
        "L": "NES_GROUND_COLOR",
        "X": None,
    },
    "pixels": [ # Made this a bit more "solid" looking like SMB ground
        "LLLLLLLLLLLLLLLL",
        "LLLLLLLLLLLLLLLL",
        "DDDDDDDDDDDDDDDD",
        "LDLDLDLDLDLDLDLD",
        "DLDLDLDLDLDLDLDL",
        "LLLLLLLLLLLLLLLL",
        "LLLLLLLLLLLLLLLL",
        "DDDDDDDDDDDDDDDD",
        "LDLDLDLDLDLDLDLD",
        "DLDLDLDLDLDLDLDL",
        "LLLLLLLLLLLLLLLL",
        "LLLLLLLLLLLLLLLL",
        "DDDDDDDDDDDDDDDD",
        "DDDDDDDDDDDDDDDD",
        "DDDDDDDDDDDDDDDD",
        "DDDDDDDDDDDDDDDD",
    ]
}

PIPE_TOP_DATA = {
    "colors": {
        "L": "NES_PIPE_GREEN_LIGHT", # Light green rim/highlight
        "M": "NES_PIPE_GREEN",       # Main green body
        "D": "NES_PIPE_GREEN_DARK",  # Dark green shadow
        "B": "NES_BLACK",            # Black for deep shadow/opening
        "X": None,
    },
    "pixels": [ # 16x16, looks like a classic pipe top!
        "XXLLLLLLLLLLXX",
        "XLMMMMMMMMMMMX",
        "XMBBBBBBBBBBMX",
        "XMBBBBBBBBBBMX",
        "XMDMMMMMMMMDMX",
        "XMDMMMMMMMMDMX",
        "XMDMMMMMMMMDMX",
        "XMDMMMMMMMMDMX",
        "XMDMMMMMMMMDMX",
        "XMDMMMMMMMMDMX",
        "XMDMMMMMMMMDMX",
        "XMDMMMMMMMMDMX",
        "XMDMMMMMMMMDMX",
        "XMDMMMMMMMMDMX",
        "XMDMMMMMMMMDMX",
        "XMDDDDDDDDDDMX",
    ]
}

FLAGPOLE_BASE_BLOCK_DATA = { # This is for a 1x1 PLAYER_SIZE block
    "colors": {
        "G": "FLAGPOLE_GRAY",        # Main gray of the base block
        "D": "FLAGPOLE_DARK_GRAY",   # Darker gray for shading/top
        "X": None
    },
    "pixels": [ # Art is 16 wide, 16 tall for a standard block
        "DDDDDDDDDDDDDDDD",
        "DGGGGGGGGGGGGXXD",
        "DGGGGGGGGGGGGXXD",
        "DGGGGGGGGGGGGXXD",
        "DGGGGGGGGGGGGXXD",
        "DGGGGGGGGGGGGXXD",
        "DGGGGGGGGGGGGXXD",
        "DGGGGGGGGGGGGXXD",
        "DGGGGGGGGGGGGXXD",
        "DGGGGGGGGGGGGXXD",
        "DGGGGGGGGGGGGXXD",
        "DGGGGGGGGGGGGXXD",
        "DGGGGGGGGGGGGXXD",
        "DGGGGGGGGGGGGXXD",
        "DGGGGGGGGGGGGXXD",
        "DDDDDDDDDDDDDDDD"
    ]
}

FLAGPOLE_POLE_SPRITE_DATA = { # Corrected to be 2px wide, 16px high native
    "colors": {
        "L": "FLAGPOLE_GRAY",      # Lighter part of pole
        "D": "FLAGPOLE_DARK_GRAY", # Darker/shadow part
        "X": None,
    },
    "pixels": [ # 2 pixels wide, 16 high native art - simple and sleek!
        "LD", "LD", "LD", "LD", "LD", "LD", "LD", "LD", # 8 rows
        "LD", "LD", "LD", "LD", "LD", "LD", "LD", "LD"  # 8 rows (total 16 rows, each row is "LD")
    ]
}
# --- End of Pixel Art Data ---

class MarioMainMenuWindow(tk.Toplevel):
    def __init__(self, master, game_launcher_callback):
        super().__init__(master)
        self.game_launcher_callback = game_launcher_callback
        self.master_catos = master # To access CATOS_GUI's color definitions and other properties

        self.title("SUPER MARIO BROS.")
        self.geometry(f"{DISPLAY_WIDTH}x{DISPLAY_HEIGHT}") # Match game window size
        self.resizable(False, False)
        self.configure(bg="#000000") # SMB1 menu is often black

        # Define colors for the menu
        self.SMB_WHITE = "#FCFCFC" # Pure white
        self.SMB_RED_TEXT = "#D03030" # Similar to Mario's Red
        self.SMB_YELLOW_TEXT = "#FAC000" # Question block yellow for highlights

        self.canvas = tk.Canvas(self, width=DISPLAY_WIDTH, height=DISPLAY_HEIGHT, bg="#000000", highlightthickness=0)
        self.canvas.pack()

        self.menu_options = [
            "1 PLAYER GAME",
            "2 PLAYER GAME"  # This will be non-functional for now
        ]
        self.current_selection_index = 0
        self.top_score = 0  # Placeholder for TOP SCORE

        # Simple pixel data for the mushroom cursor (e.g., 6x6 native pixels)
        self.cursor_pixel_data = {
            "colors": {
                "R": "MARIO_RED",       # Uses keys from CATOS_GUI.COLOR_MAP
                "W": "NES_WHITE",
                "X": None               # Transparent
            },
            "pixels": [
                "XXRRXX",
                "XRRRRX",
                "RRRRRR",
                "RRWWWR",
                "XWWWWX",
                "XWWWWX",
            ]
        }
        self.cursor_canvas_items = [] # To keep track of drawn cursor pixels for clearing

        self.draw_menu_elements()
        self.bind_keys()
        self.focus_set() # Crucial for Toplevel to receive key events immediately

    def draw_menu_elements(self):
        self.canvas.delete("all") # Clear previous drawings

        # Clean up any old cursor items explicitly if they weren't part of "all" (e.g. if not tagged)
        for item_id in self.cursor_canvas_items:
            try:
                self.canvas.delete(item_id)
            except tk.TclError:
                pass # Item might have been deleted by canvas.delete("all")
        self.cursor_canvas_items = []

        # --- Draw static menu elements ---
        # SUPER MARIO BROS. Title
        self.canvas.create_text(DISPLAY_WIDTH / 2, DISPLAY_HEIGHT * 0.2, text="SUPER MARIO BROS.",
                                font=("Courier New", 48, "bold"), fill=self.SMB_RED_TEXT, anchor="center")

        # Nintendo Copyright
        self.canvas.create_text(DISPLAY_WIDTH / 2, DISPLAY_HEIGHT * 0.1, text="©1985 NINTENDO",
                                font=("Courier New", 16), fill=self.SMB_WHITE, anchor="center")

        # TOP SCORE
        self.canvas.create_text(DISPLAY_WIDTH / 2, DISPLAY_HEIGHT * 0.35, text=f"TOP - {self.top_score:06d}",
                                font=("Courier New", 28, "bold"), fill=self.SMB_WHITE, anchor="center")

        # --- Draw menu options and cursor ---
        option_y_start = DISPLAY_HEIGHT * 0.55
        option_y_spacing = 60 # Vertical distance between options

        for i, option_text in enumerate(self.menu_options):
            y_pos = option_y_start + (i * option_y_spacing)
            text_color = self.SMB_WHITE
            # Optional: Highlight selected text directly
            # if i == self.current_selection_index:
            #     text_color = self.SMB_YELLOW_TEXT

            self.canvas.create_text(DISPLAY_WIDTH / 2, y_pos, text=option_text,
                                    font=("Courier New", 28, "bold"), fill=text_color, anchor="center")

            if i == self.current_selection_index:
                # Draw the mushroom cursor to the left of the selected option
                cursor_display_size_w = 36  # Desired width of cursor on canvas (pixels)
                cursor_display_size_h = 36  # Desired height of cursor on canvas (pixels)

                # Position cursor. Estimate text width or use a fixed offset.
                # "1 PLAYER GAME" (13 chars) * ~18px/char (Courier New 28 bold) = ~234px. Half is ~117.
                estimated_text_half_width = 150 # A bit generous for centering text block
                cursor_x_canvas = (DISPLAY_WIDTH / 2) - estimated_text_half_width - cursor_display_size_w - 15 # (Canvas Center) - (Text Half Width) - (Cursor Width) - (Padding)
                cursor_y_canvas = y_pos - (cursor_display_size_h / 2) # Vertically align cursor with text center

                # Resolve colors for the cursor sprite using master_catos.COLOR_MAP
                sprite_color_palette_cursor = {
                    char_key: self.master_catos.COLOR_MAP.get(mapped_color_key)
                    for char_key, mapped_color_key in self.cursor_pixel_data["colors"].items()
                }

                art_rows = self.cursor_pixel_data["pixels"]
                native_art_h = len(art_rows)
                native_art_w = len(art_rows[0]) if native_art_h > 0 else 0

                if native_art_w > 0 and native_art_h > 0:
                    # Calculate size of each "pixel" of the cursor sprite on the canvas
                    pixel_w_on_canvas = cursor_display_size_w / native_art_w
                    pixel_h_on_canvas = cursor_display_size_h / native_art_h

                    for r_idx, row_str in enumerate(art_rows):
                        for c_idx, color_char_key in enumerate(row_str):
                            actual_fill_color = sprite_color_palette_cursor.get(color_char_key)

                            if actual_fill_color:  # Only draw if color is defined (not transparent)
                                px1 = cursor_x_canvas + (c_idx * pixel_w_on_canvas)
                                py1 = cursor_y_canvas + (r_idx * pixel_h_on_canvas)
                                px2 = px1 + pixel_w_on_canvas
                                py2 = py1 + pixel_h_on_canvas
                                
                                item_id = self.canvas.create_rectangle(px1, py1, px2, py2,
                                                                       fill=actual_fill_color,
                                                                       outline=actual_fill_color) # outline same as fill for solid pixel
                                self.cursor_canvas_items.append(item_id)

    def bind_keys(self):
        self.bind("<KeyPress-Up>", self.move_selection_up)
        self.bind("<KeyPress-Down>", self.move_selection_down)
        self.bind("<KeyPress-Return>", self.confirm_selection) # Enter key
        self.bind("<KeyPress-space>", self.confirm_selection)  # Space bar
        self.protocol("WM_DELETE_WINDOW", self.on_closing) # Handle window 'X' button

    def on_closing(self):
        self.destroy()
        if self.master_catos: # Ensure master_catos exists
             self.master_catos.mario_main_menu_window = None # Clear reference in CATOS_GUI

    def move_selection_up(self, event=None):
        self.current_selection_index = (self.current_selection_index - 1 + len(self.menu_options)) % len(self.menu_options)
        self.draw_menu_elements() # Redraw to update cursor position

    def move_selection_down(self, event=None):
        self.current_selection_index = (self.current_selection_index + 1) % len(self.menu_options)
        self.draw_menu_elements() # Redraw

    def confirm_selection(self, event=None):
        selected_option = self.menu_options[self.current_selection_index]
        if selected_option == "1 PLAYER GAME":
            if self.game_launcher_callback:
                self.game_launcher_callback() # This will handle destroying this menu
        elif selected_option == "2 PLAYER GAME":
            # Placeholder: Show a temporary message on the canvas
            msg_id = self.canvas.create_text(DISPLAY_WIDTH / 2, DISPLAY_HEIGHT * 0.85,
                                    text="2 PLAYER GAME NOT IMPLEMENTED",
                                    font=("Courier New", 20, "bold"), fill=self.SMB_RED_TEXT, anchor="center")
            # Remove the message after a couple of seconds
            self.after(2000, lambda: self.canvas.delete(msg_id) if self.winfo_exists() and self.canvas.winfo_exists() else None)


class MarioGameWindow(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Mini Mario Game - SMB 1-1 Purr-fected++!")
        self.geometry(f"{DISPLAY_WIDTH}x{DISPLAY_HEIGHT}")
        self.resizable(False, False)

        # --- Enhanced NES Color Palette (accessible by master which is CATOS_GUI) ---
        # These are now primarily defined in CATOS_GUI and accessed via self.master.COLOR_MAP or self.master.COLOR_NAME
        # For direct use within MarioGameWindow if needed, or for clarity:
        self.NES_SKY_BLUE = master.NES_SKY_BLUE


        self.configure(bg=self.NES_SKY_BLUE)

        self.canvas = tk.Canvas(self, width=DISPLAY_WIDTH, height=DISPLAY_HEIGHT, bg=self.NES_SKY_BLUE, highlightthickness=0)
        self.canvas.pack()

        self.scale = DISPLAY_WIDTH / NES_SCREEN_WIDTH # Scale factor from NES res to display res
        
        # Player attributes in NES pixels
        self.player_x = 3 * PLAYER_SIZE # Start near beginning of 1-1
        self.player_y = NES_SCREEN_HEIGHT - 2 * PLAYER_SIZE # Start on ground (bottom of player sprite aligns with this y)
        self.player_vy = 0 # Vertical velocity
        self.is_jumping = False
        self.on_ground = True # Start on ground

        self.camera_x = 0 # NES pixel units for camera's left edge

        # COLOR_MAP is now primarily in CATOS_GUI, accessed via self.master.COLOR_MAP
        self.COLOR_MAP = master.COLOR_MAP

        self.player_pixel_ids = [] # Stores canvas item IDs for the player's pixels
        
        # --- SMB 1-1 Level Data Generation MEOW! ---
        self.visual_blocks_data = [] # Stores data for all blocks in the level
        
        # Helper constants for level building (NES pixel units)
        PS = PLAYER_SIZE      # Player/Block size in NES pixels
        H_NES = NES_SCREEN_HEIGHT # NES screen height
        
        # Helper function to add blocks to self.visual_blocks_data
        # Coords are in NES pixel units.
        def add_block(map_x_blocks, map_y_bottom_blocks, type_str, sprite_data, width_blocks=1, height_blocks=1, collidable=True):
            # map_x_blocks: horizontal position in terms of block units from world start (0)
            # map_y_bottom_blocks: vertical position of the BOTTOM of the block structure, in block units from NES bottom (1 = ground)
            
            # Calculate NES pixel coordinates for the block structure
            # Top-left x of the structure
            x1_nes = map_x_blocks * PS 
            # Top-left y of the structure
            # map_y_bottom_blocks = 1 means its bottom is at H_NES - 1*PS. Its top is H_NES - (1+height_blocks-1)*PS
            y1_nes = H_NES - (map_y_bottom_blocks + height_blocks -1) * PS 
            
            # Bottom-right x of the structure
            x2_nes = x1_nes + width_blocks * PS
            # Bottom-right y of the structure
            y2_nes = y1_nes + height_blocks * PS # Or H_NES - (map_y_bottom_blocks - 1) * PS
            
            self.visual_blocks_data.append({
                'coords': (x1_nes, y1_nes, x2_nes, y2_nes), # (left, top, right, bottom) in NES pixels
                'type': type_str, 
                'collidable': collidable, 
                'sprite_data': sprite_data
            })

        # Ground Sections (SMB 1-1 Map based on Mariowiki)
        add_block(0, 1, 'ground', GROUND_BLOCK_DATA, width_blocks=69)
        add_block(71, 1, 'ground', GROUND_BLOCK_DATA, width_blocks=15) # Gap from 69-70
        add_block(90, 1, 'ground', GROUND_BLOCK_DATA, width_blocks=44) # Gap from 86-89
        # Extended ground to world width to prevent falling off at the very end before flagpole visual
        add_block(136, 1, 'ground', GROUND_BLOCK_DATA, width_blocks=(WORLD_WIDTH_BLOCKS - 136))


        # Floating Blocks and Bricks (Standard height for these is 5 blocks from ground: map_y_bottom_blocks=5)
        add_block(16, 5, 'question_block_powerup', QUESTION_BLOCK_DATA) # ? (Mushroom/Flower)
        add_block(20, 5, 'brick', BRICK_BLOCK_DATA)
        add_block(21, 5, 'question_block_coin', QUESTION_BLOCK_DATA)    # ? (Coin)
        add_block(22, 5, 'brick', BRICK_BLOCK_DATA)
        add_block(23, 5, 'question_block_coin', QUESTION_BLOCK_DATA)    # ? (Coin)
        add_block(22, 9, 'question_block_1up', QUESTION_BLOCK_DATA)     # ? (Hidden 1-UP, visually a Q block for simplicity)

        # Pipes (map_x_blocks, base_y_level=1 (bottom of pipe is on ground), width=2 blocks, height_in_blocks)
        # Note: PIPE_TOP_DATA is for a single 16x16 tile. Tiling will handle taller pipes.
        add_block(28, 1, 'pipe', PIPE_TOP_DATA, width_blocks=2, height_blocks=2) # Pipe 1 (H=2 blocks)
        add_block(38, 1, 'pipe', PIPE_TOP_DATA, width_blocks=2, height_blocks=3) # Pipe 2 (H=3 blocks)
        add_block(46, 1, 'pipe', PIPE_TOP_DATA, width_blocks=2, height_blocks=4) # Pipe 3 (H=4 blocks)
        add_block(57, 1, 'pipe', PIPE_TOP_DATA, width_blocks=2, height_blocks=4) # Pipe 4 (H=4, leads to bonus)
        
        # Block Group after first pipes and gap
        add_block(78, 5, 'brick_coin', BRICK_BLOCK_DATA) # Brick (Coin)
        add_block(79, 5, 'brick', BRICK_BLOCK_DATA)
        add_block(80, 5, 'brick_star', BRICK_BLOCK_DATA) # Brick (Star, visually a regular brick)
        add_block(81, 5, 'brick', BRICK_BLOCK_DATA)

        # Block Group after second gap
        add_block(91, 5, 'question_block_coin', QUESTION_BLOCK_DATA)
        add_block(92, 5, 'brick', BRICK_BLOCK_DATA)
        add_block(93, 5, 'brick', BRICK_BLOCK_DATA)
        add_block(94, 5, 'question_block_powerup', QUESTION_BLOCK_DATA) # ? (Powerup)
        add_block(94, 9, 'brick_high', BRICK_BLOCK_DATA) # High brick

        # Helper for stairs (ascending to the right)
        # base_x_blocks: starting x block coord of the current step column
        # base_y_bottom_blocks: y block coord for the bottom-most block of this step column
        # height_in_blocks_for_step: how many blocks tall this particular step column is
        def add_stair_segment(base_x_blocks, base_y_bottom_blocks, height_in_blocks_for_step):
            # This function creates a single vertical column of blocks for a stair step.
            # It uses GROUND_BLOCK_DATA for the stair blocks.
            add_block(base_x_blocks, base_y_bottom_blocks, 'ground_stair', GROUND_BLOCK_DATA, 
                      width_blocks=1, height_blocks=height_in_blocks_for_step)
        
        # Staircase 1 (Pyramid structure, 4 blocks high at its peak)
        # Mariowiki map: (100,1 H=1), (101,1 H=2), (102,1 H=3), (103,1 H=4)
        add_stair_segment(100, 1, 1)
        add_stair_segment(101, 1, 2)
        add_stair_segment(102, 1, 3)
        add_stair_segment(103, 1, 4)

        # Blocks after staircase 1
        add_block(106, 5, 'brick', BRICK_BLOCK_DATA)
        add_block(107, 5, 'brick', BRICK_BLOCK_DATA)
        add_block(108, 5, 'brick', BRICK_BLOCK_DATA)

        # Staircase 2 (similar to staircase 1)
        # Mariowiki map: (113,1 H=1), (114,1 H=2), (115,1 H=3), (116,1 H=4)
        add_stair_segment(113, 1, 1)
        add_stair_segment(114, 1, 2)
        add_stair_segment(115, 1, 3)
        add_stair_segment(116, 1, 4)
        
        # Pipe after staircase 2
        add_block(118, 1, 'pipe', PIPE_TOP_DATA, width_blocks=2, height_blocks=2) # Pipe 5 (H=2)

        # Blocks before final stairs
        add_block(123, 5, 'brick', BRICK_BLOCK_DATA)
        add_block(124, 5, 'brick', BRICK_BLOCK_DATA)
        add_block(125, 5, 'question_block_powerup', QUESTION_BLOCK_DATA) # ? (Powerup)
        add_block(126, 5, 'brick', BRICK_BLOCK_DATA)

        # Final Staircase (8 steps high, ascending to the right)
        # Mariowiki map: (134,1 H=1) up to (141,1 H=8)
        for i in range(8): # i from 0 to 7
            # x-coordinate for this step is 134 + i
            # height for this step is i + 1
            add_stair_segment(134 + i, 1, i + 1)

        # Flagpole Base Block
        # At x=142 (block coord), y_bottom=1 (block coord)
        add_block(142, 1, 'flagpole_base', FLAGPOLE_BASE_BLOCK_DATA, width_blocks=1, height_blocks=1)

        # Flagpole Pole (decorative, non-collidable)
        # Sits on top of the base block. Base block is at map_y_bottom_blocks=1, height_blocks=1.
        # So, pole starts at map_y_bottom_blocks=2 (meaning its bottom is at the top of the base block).
        # Let's make it 8 blocks high.
        # The FLAGPOLE_POLE_SPRITE_DATA is for a thin sprite (e.g., 2 native pixels wide).
        # We want the visual pole to be thinner than a full block.
        
        pole_visual_width_nes = PLAYER_SIZE / 4 # Visually make the pole thinner than a full block on NES scale
        pole_center_x_nes = (142 * PS) + (PS / 2) # Center of the base block (map_x_blocks * PS + PS/2)
        
        pole_x1_nes = pole_center_x_nes - (pole_visual_width_nes / 2)
        pole_x2_nes = pole_center_x_nes + (pole_visual_width_nes / 2)
        
        pole_height_blocks = 8
        pole_map_y_bottom_blocks = 2 # Starts on top of the base block

        pole_y1_nes = H_NES - (pole_map_y_bottom_blocks + pole_height_blocks - 1) * PS
        pole_y2_nes = pole_y1_nes + pole_height_blocks * PS
        
        self.visual_blocks_data.append({
            'coords': (pole_x1_nes, pole_y1_nes, pole_x2_nes, pole_y2_nes),
            'type': 'flagpole_pole',
            'collidable': False, # Decorative
            'sprite_data': FLAGPOLE_POLE_SPRITE_DATA
        })
        # --- End of SMB 1-1 Level Data ---

        self.canvas_items_map = {} # Stores canvas item IDs for drawn blocks {block_key: [ids]}
        self.collidable_platform_coords = [] # Stores (x1,y1,x2,y2) NES coords for collidable blocks
        
        # Initial draw of all static level elements
        # This populates self.collidable_platform_coords among other things
        self.draw_all_visual_blocks() 

        self.pressed_keys = set()
        self.bind_keys()
        self.game_loop()

    def draw_pixel_art(self, base_x_nes, base_y_nes, entity_width_nes, entity_height_nes, sprite_definition):
        """
        Draws pixel art onto the canvas.
        base_x_nes, base_y_nes: Top-left corner of the entity in NES pixel coordinates.
        entity_width_nes, entity_height_nes: Total size of the entity in NES pixels.
                                             The sprite will be scaled to fit this.
        sprite_definition: Dictionary containing "colors" and "pixels" for the art.
        Returns a list of canvas item IDs created for this drawing.
        """
        pixel_art_rows = sprite_definition["pixels"]
        # Resolve character keys in sprite_definition["colors"] to actual hex color codes
        sprite_color_palette = {
            char_key: self.COLOR_MAP.get(mapped_color_key)
            for char_key, mapped_color_key in sprite_definition["colors"].items()
        }

        art_height_px_native = len(pixel_art_rows) # How many rows in the pixel art data
        art_width_px_native = len(pixel_art_rows[0]) if art_height_px_native > 0 and isinstance(pixel_art_rows[0], str) else 0
        if art_width_px_native == 0 or art_height_px_native == 0: return [] # No art to draw

        # Calculate the size of one "native pixel" of the sprite when drawn on the NES conceptual grid
        # This scales the sprite art to fit the entity_width_nes/entity_height_nes.
        scaled_pixel_width_nes = entity_width_nes / art_width_px_native
        scaled_pixel_height_nes = entity_height_nes / art_height_px_native
        
        drawn_item_ids = []
        for r_idx, row_str in enumerate(pixel_art_rows): # Iterate over each row of the native pixel art
            for c_idx, color_char_key in enumerate(row_str): # Iterate over each char (pixel) in the row
                actual_color_hex = sprite_color_palette.get(color_char_key)
                
                if actual_color_hex: # If not transparent (None)
                    # Calculate the NES coordinates for this specific "scaled native pixel"
                    px_x1_nes = base_x_nes + (c_idx * scaled_pixel_width_nes)
                    py_y1_nes = base_y_nes + (r_idx * scaled_pixel_height_nes)
                    px_x2_nes = base_x_nes + ((c_idx + 1) * scaled_pixel_width_nes)
                    py_y2_nes = base_y_nes + ((r_idx + 1) * scaled_pixel_height_nes)
                    
                    # Convert NES coordinates to canvas coordinates (apply camera and display scaling)
                    # Camera_x is the left edge of the NES viewport in world NES coordinates.
                    # self.scale is DISPLAY_WIDTH / NES_SCREEN_WIDTH.
                    px_x1_canvas = (px_x1_nes - self.camera_x) * self.scale
                    py_y1_canvas = py_y1_nes * self.scale 
                    px_x2_canvas = (px_x2_nes - self.camera_x) * self.scale
                    py_y2_canvas = py_y2_nes * self.scale
                    
                    # Optimization: Don't draw if entirely off-screen horizontally on canvas
                    if px_x2_canvas < 0 or px_x1_canvas > DISPLAY_WIDTH:
                        continue
                    # Optimization: Don't draw if entirely off-screen vertically (less common for SMB style)
                    if py_y2_canvas < 0 or py_y1_canvas > DISPLAY_HEIGHT:
                        continue

                    # Ensure minimum 1-pixel size on canvas to be visible
                    if px_x2_canvas - px_x1_canvas < 1: px_x2_canvas = px_x1_canvas + 1
                    if py_y2_canvas - py_y1_canvas < 1: py_y2_canvas = py_y1_canvas + 1

                    pixel_id = self.canvas.create_rectangle(
                        px_x1_canvas, py_y1_canvas, px_x2_canvas, py_y2_canvas,
                        fill=actual_color_hex, outline="" # Outline empty for crisp pixels
                    )
                    drawn_item_ids.append(pixel_id)
        return drawn_item_ids

    def draw_all_visual_blocks(self):
        """Redraws all visible static level blocks based on camera position."""
        # Clear previously drawn block items from canvas_items_map
        for key in list(self.canvas_items_map.keys()): # Iterate over a copy of keys
            items_to_delete = self.canvas_items_map.pop(key) # Remove from map
            if isinstance(items_to_delete, list):
                for item_id in items_to_delete: self.canvas.delete(item_id)
            elif items_to_delete: # Single item ID
                self.canvas.delete(items_to_delete)
        
        # This list is rebuilt each frame based on what's collidable, visible or not.
        # For static levels, it could be built once if culling wasn't an issue for collision.
        # However, since we might have moving platforms later, rebuilding is safer.
        # For now, it's just static blocks.
        self.collidable_platform_coords = [] 

        for i, block_data in enumerate(self.visual_blocks_data):
            coords_nes = block_data['coords'] # (x1, y1, x2, y2) in NES pixels
            x1_nes, y1_nes, x2_nes, y2_nes = coords_nes
            
            # --- Culling for Drawing ---
            # Check if the block is visible within the current camera view (NES coordinates)
            # Camera view in NES coords: self.camera_x to self.camera_x + NES_SCREEN_WIDTH
            if x2_nes < self.camera_x or x1_nes > self.camera_x + NES_SCREEN_WIDTH:
                # Block is entirely off-screen horizontally.
                # If it's collidable, we still need its collision data.
                if block_data.get('collidable', True): # Default to collidable if not specified
                    self.collidable_platform_coords.append(coords_nes)
                continue # Don't draw this block

            # --- If visible or partially visible, proceed to draw ---
            block_width_nes = x2_nes - x1_nes
            block_height_nes = y2_nes - y1_nes
            block_type = block_data['type']
            sprite_data_for_block = block_data.get('sprite_data')
            
            current_block_pixel_ids = [] # Canvas item IDs for this specific block instance

            if sprite_data_for_block:
                # For blocks that can be wider/taller than a single PLAYER_SIZE sprite (e.g., ground, multi-block pipes),
                # we need to tile the base sprite (assumed to be PLAYER_SIZE x PLAYER_SIZE native, or specific like flagpole)
                
                # Determine the native size of the sprite tile from its definition
                # For most blocks, this is PLAYER_SIZE x PLAYER_SIZE
                # For special sprites like flagpole, it might be different.
                # Let's assume sprite_data_for_block.get('native_width', PLAYER_SIZE)
                
                # The draw_pixel_art function scales the provided sprite to the given entity_width/height.
                # So, for tiling, we call draw_pixel_art for each tile.
                
                # How many base sprite tiles fit into this block's dimensions?
                # Base tile size is usually PLAYER_SIZE, but for things like the thin flagpole,
                # the sprite itself is smaller. The draw_pixel_art will scale it.
                # What we need is the size of the "unit" we are tiling.
                # For most blocks, the unit is PLAYER_SIZE x PLAYER_SIZE.
                # For the flagpole pole, its 'sprite_data' is for the whole thin pole.
                # So, if block_width/height is larger than PLAYER_SIZE, we tile.
                # If smaller (like the flagpole pole's width), we draw once, scaled.
                
                tile_unit_w_nes = PLAYER_SIZE 
                tile_unit_h_nes = PLAYER_SIZE

                # If the block itself is smaller than the standard tile unit (e.g. thin flagpole pole)
                # then our "tile" is the block itself, and we draw the sprite scaled to the block's dimensions.
                if block_width_nes < tile_unit_w_nes: tile_unit_w_nes = block_width_nes
                if block_height_nes < tile_unit_h_nes: tile_unit_h_nes = block_height_nes
                
                # Number of tiles needed. Ensure at least 1.
                num_tiles_x = max(1, int(round(block_width_nes / tile_unit_w_nes)))
                num_tiles_y = max(1, int(round(block_height_nes / tile_unit_h_nes)))

                # The actual drawing dimensions for each tile, if tiling.
                # If not tiling (num_tiles_x/y is 1), this will be block_width/height_nes.
                tile_draw_width_nes = block_width_nes / num_tiles_x
                tile_draw_height_nes = block_height_nes / num_tiles_y
                
                for row in range(num_tiles_y):
                    for col in range(num_tiles_x):
                        tile_x_nes = x1_nes + (col * tile_draw_width_nes)
                        tile_y_nes = y1_nes + (row * tile_draw_height_nes)
                        
                        # draw_pixel_art will take sprite_data_for_block and scale its internal art
                        # to fit tile_draw_width_nes and tile_draw_height_nes.
                        ids = self.draw_pixel_art(tile_x_nes, tile_y_nes, 
                                                  tile_draw_width_nes, tile_draw_height_nes, 
                                                  sprite_data_for_block)
                        current_block_pixel_ids.extend(ids)
            
            # Store the canvas item IDs for this block instance
            self.canvas_items_map[f"{block_type}_{i}"] = current_block_pixel_ids

            # Add to collidable list if it's collidable (even if partially visible)
            if block_data.get('collidable', True):
                self.collidable_platform_coords.append(coords_nes)


    def update_player_visuals(self):
        """Deletes old player pixels and redraws them at the new position."""
        for pixel_id in self.player_pixel_ids:
            self.canvas.delete(pixel_id)
        self.player_pixel_ids = [] # Clear the list

        # Redraw the player using the pixel art function
        # Player's (x,y) is top-left in NES coordinates.
        # PLAYER_SIZE is the dimension for the player sprite in NES coordinates.
        self.player_pixel_ids = self.draw_pixel_art(
            self.player_x, self.player_y,
            PLAYER_SIZE, PLAYER_SIZE, 
            SMALL_MARIO_STANDING_DATA # Current sprite for player
        )

    def bind_keys(self):
        self.focus_set() # Ensure the game window has focus to receive key events
        self.bind("<KeyPress>", self.key_pressed)
        self.bind("<KeyRelease>", self.key_released)
        self.protocol("WM_DELETE_WINDOW", self.on_closing) # Handle window close button

    def on_closing(self):
        # This method is called when the game window's 'X' button is clicked.
        # We need to clean up and close the window.
        # If CATOS_GUI is the master, clear its reference to this game window.
        if hasattr(self.master, 'mario_game_window') and self.master.mario_game_window == self:
            self.master.mario_game_window = None
        self.destroy()


    def key_pressed(self, event):
        self.pressed_keys.add(event.keysym.lower())

    def key_released(self, event):
        keysym_lower = event.keysym.lower()
        if keysym_lower in self.pressed_keys:
            self.pressed_keys.remove(keysym_lower)

    def handle_input(self):
        # Horizontal movement
        if 'a' in self.pressed_keys or 'left' in self.pressed_keys:
            self.player_x -= MOVE_SPEED
        if 'd' in self.pressed_keys or 'right' in self.pressed_keys:
            self.player_x += MOVE_SPEED
        
        # Jumping
        if ('w' in self.pressed_keys or 'up' in self.pressed_keys or 'space' in self.pressed_keys) and self.on_ground:
            self.player_vy = -JUMP_POWER # Negative is up
            self.is_jumping = True
            self.on_ground = False
            
        # Prevent player from moving out of world bounds (NES coordinates)
        if self.player_x < 0: self.player_x = 0
        # Player's right edge should not exceed world width
        if self.player_x + PLAYER_SIZE > WORLD_WIDTH_NES:
            self.player_x = WORLD_WIDTH_NES - PLAYER_SIZE


    def apply_gravity_and_movement(self):
        # Apply gravity if not on ground
        if not self.on_ground:
            self.player_vy += GRAVITY
        
        # Update player's vertical position based on velocity
        self.player_y += self.player_vy

        # --- Collision Detection and Resolution ---
        # Player's bounding box for the next frame (NES coordinates)
        next_player_top = self.player_y
        next_player_bottom = self.player_y + PLAYER_SIZE
        next_player_left = self.player_x
        next_player_right = self.player_x + PLAYER_SIZE
        
        self.on_ground = False # Assume not on ground until a collision proves otherwise

        for p_coords_nes in self.collidable_platform_coords:
            plat_left_nes, plat_top_nes, plat_right_nes, plat_bottom_nes = p_coords_nes

            # Check for horizontal overlap first
            horizontal_overlap = (next_player_right > plat_left_nes and next_player_left < plat_right_nes)

            if horizontal_overlap:
                # 1. Landing on top of a platform
                # Player is moving downwards (or was on ground), and their bottom edge is now intersecting the platform's top.
                # Also, player's old bottom edge (self.player_y - self.player_vy + PLAYER_SIZE) was above or at platform top.
                # A simpler check: if player's current bottom is at or below platform top, and player's top is above platform top.
                if self.player_vy >= 0 and next_player_bottom >= plat_top_nes and (self.player_y + PLAYER_SIZE - self.player_vy) <= plat_top_nes + 1: # Small tolerance
                    self.player_y = plat_top_nes - PLAYER_SIZE # Align player's bottom with platform's top
                    self.player_vy = 0
                    self.on_ground = True
                    self.is_jumping = False
                    # Update player's next position after correction
                    next_player_top = self.player_y
                    next_player_bottom = self.player_y + PLAYER_SIZE

                # 2. Hitting head on bottom of a platform
                # Player is moving upwards, and their top edge is now intersecting the platform's bottom.
                elif self.player_vy < 0 and next_player_top <= plat_bottom_nes and (self.player_y - self.player_vy) >= plat_bottom_nes -1:
                    self.player_y = plat_bottom_nes # Align player's top with platform's bottom
                    self.player_vy = 1 # Stop upward motion, maybe a slight bounce down
                    # Update player's next position
                    next_player_top = self.player_y
                    next_player_bottom = self.player_y + PLAYER_SIZE
            
            # Re-check horizontal overlap with potentially corrected vertical position for side collisions
            # This needs to be more robust. Let's check side collisions based on original movement intent.
            # This simplified side collision assumes player was not already overlapping vertically significantly.
            # More accurate side collision would involve checking movement vector.

            # Check for side collisions (if player is vertically aligned with platform)
            vertical_overlap_for_side = (next_player_bottom > plat_top_nes + 1 and next_player_top < plat_bottom_nes -1) # +1/-1 to avoid issues at exact edges
            
            if vertical_overlap_for_side:
                # Player moving right, collides with left side of platform
                if (self.player_x + PLAYER_SIZE - (self.player_x - MOVE_SPEED + PLAYER_SIZE) > 0) and \
                   next_player_right > plat_left_nes and (self.player_x + PLAYER_SIZE - MOVE_SPEED) <= plat_left_nes:
                    self.player_x = plat_left_nes - PLAYER_SIZE
                    next_player_left = self.player_x
                    next_player_right = self.player_x + PLAYER_SIZE

                # Player moving left, collides with right side of platform
                elif (self.player_x - (self.player_x + MOVE_SPEED) < 0) and \
                     next_player_left < plat_right_nes and (self.player_x + MOVE_SPEED) >= plat_right_nes:
                    self.player_x = plat_right_nes
                    next_player_left = self.player_x
                    next_player_right = self.player_x + PLAYER_SIZE


        # Check if player fell off the world (e.g., into a pit)
        if not self.on_ground and self.player_y > NES_SCREEN_HEIGHT + PLAYER_SIZE * 2 : # Fell far below screen
            print("Fell off! Oh noes! Resetting Mario, meow!")
            self.player_x = 3 * PLAYER_SIZE # Reset to start of level
            self.player_y = NES_SCREEN_HEIGHT - 2 * PLAYER_SIZE 
            self.player_vy = 0
            self.on_ground = True 
            self.is_jumping = False
            self.camera_x = 0 # Reset camera too
            
        # --- Camera Scrolling ---
        # Camera follows player, keeping player somewhat centered, within world bounds.
        # Target camera_x to have player in middle of NES screen width
        target_camera_x = self.player_x - (NES_SCREEN_WIDTH / 2) + (PLAYER_SIZE / 2)
        
        # Clamp camera_x to world boundaries
        # Left boundary: 0
        # Right boundary: WORLD_WIDTH_NES - NES_SCREEN_WIDTH (so camera doesn't show beyond world)
        self.camera_x = max(0, min(target_camera_x, WORLD_WIDTH_NES - NES_SCREEN_WIDTH))
        self.camera_x = round(self.camera_x) # Keep camera on whole pixels if desired


    def game_loop(self):
        try:
            if not self.winfo_exists(): return # Window has been closed
            
            start_time = time.perf_counter()

            self.handle_input() 
            self.apply_gravity_and_movement() # Includes physics and collision
            
            # Drawing needs to happen after all position updates and camera updates
            self.draw_all_visual_blocks() # Redraws static elements based on camera (and rebuilds collidables)
            self.update_player_visuals()  # Redraws player at new position

            end_time = time.perf_counter()
            process_time_ms = (end_time - start_time) * 1000
            delay_ms = max(1, DELAY - int(process_time_ms)) # Ensure at least 1ms delay

            self.after(delay_ms, self.game_loop) # Schedule next frame
        except tk.TclError as e:
            # This can happen if widgets are accessed after the window is destroyed.
            print(f"Game window TclError (likely closed): {e}")
        except Exception as e:
            print(f"Oopsie, a little furball in the game loop: {e}")
            import traceback
            traceback.print_exc() 
            if self.winfo_exists():
                self.destroy() # Close window on critical error

class CATOS_GUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("CATOS - Meow Edition v3.0 NES Emu! THE ULTIMATE!") 
        self.geometry("500x500") 
        self.configure(bg="#2c3e50") # Dark slate blue background

        # --- Centralized NES Color Palette ---
        self.NES_SKY_BLUE = "#5C94FC"
        self.NES_BRICK_COLOR = "#D07030"
        self.NES_BRICK_DARK = "#A04000"
        self.NES_QUESTION_BLOCK_COLOR = "#FAC000"
        self.NES_QUESTION_OUTLINE = "#E4A000"
        self.NES_QUESTION_SHADOW = "#783000"
        self.NES_GROUND_COLOR = "#E09050" 
        self.NES_GROUND_DARK = "#A04000" 
        self.MARIO_RED = "#D03030"
        self.NES_SKIN_PEACH = "#FCB8A0"
        self.NES_DARK_BROWN = "#782818"
        self.NES_PIPE_GREEN = "#30A020"
        self.NES_PIPE_GREEN_LIGHT = "#80D010"
        self.NES_PIPE_GREEN_DARK = "#207818"
        self.FLAGPOLE_GRAY = "#B0B0B0"
        self.FLAGPOLE_DARK_GRAY = "#707070"
        self.NES_WHITE = "#FCFCFC"
        self.NES_BLACK = "#000000"

        # This map is used by drawing functions to resolve sprite color keys
        self.COLOR_MAP = {
            "MARIO_RED": self.MARIO_RED, "NES_SKIN_PEACH": self.NES_SKIN_PEACH,
            "NES_DARK_BROWN": self.NES_DARK_BROWN, "NES_BRICK_DARK": self.NES_BRICK_DARK,
            "NES_BRICK_COLOR": self.NES_BRICK_COLOR, "NES_QUESTION_OUTLINE": self.NES_QUESTION_OUTLINE,
            "NES_QUESTION_BLOCK_COLOR": self.NES_QUESTION_BLOCK_COLOR, "NES_WHITE": self.NES_WHITE,
            "NES_QUESTION_SHADOW": self.NES_QUESTION_SHADOW, "NES_GROUND_DARK": self.NES_GROUND_DARK,
            "NES_GROUND_COLOR": self.NES_GROUND_COLOR, "NES_PIPE_GREEN": self.NES_PIPE_GREEN,
            "NES_PIPE_GREEN_LIGHT": self.NES_PIPE_GREEN_LIGHT, "NES_PIPE_GREEN_DARK": self.NES_PIPE_GREEN_DARK,
            "NES_BLACK": self.NES_BLACK, "FLAGPOLE_GRAY": self.FLAGPOLE_GRAY,
            "FLAGPOLE_DARK_GRAY": self.FLAGPOLE_DARK_GRAY,
        }


        title_label = tk.Label(self, text="Welcome to CATOS! SMB 1-1 Loaded!", font=("Arial", 24, "bold"), bg="#2c3e50", fg="white")
        title_label.pack(pady=30)

        cat_art_text = "  /\_/\ \n ( >w< )  < WORLD 1-1 READY!\n  > ^ < \nCATOS NES EVO++!"
        cat_label = tk.Label(self,text=cat_art_text,font=("Courier New", 14),bg="#2c3e50",fg="#ecf0f1",justify=tk.LEFT)
        cat_label.pack(pady=20)

        launch_button = tk.Button(
            self, text="Play SMB 1-1!", font=("Arial", 16),bg="#e74c3c", fg="white", # Red button
            activebackground="#c0392b",relief=tk.FLAT,padx=15,pady=10,command=self.launch_main_menu) # Command changed
        launch_button.pack(pady=20)

        self.clock_label = tk.Label(self,text="",font=("Arial", 12),bg="#2c3e50",fg="#bdc3c7")
        self.clock_label.pack(side=tk.BOTTOM, pady=10)
        self.update_clock() 
        
        self.mario_game_window = None
        self.mario_main_menu_window = None # Reference to the main menu window

        self.protocol("WM_DELETE_WINDOW", self.on_closing_catos)


    def on_closing_catos(self):
        # Ensure any child windows are closed when CATOS main window closes
        if self.mario_main_menu_window and self.mario_main_menu_window.winfo_exists():
            self.mario_main_menu_window.destroy()
        if self.mario_game_window and self.mario_game_window.winfo_exists():
            self.mario_game_window.destroy()
        self.destroy()

    def update_clock(self):
        current_time = time.strftime("%H:%M:%S %p \n %A, %B %d, %Y")
        self.clock_label.config(text=current_time)
        self.after(1000, self.update_clock) 

    def launch_main_menu(self):
        # If game is currently running, close it before showing menu
        if self.mario_game_window and self.mario_game_window.winfo_exists():
            print("Closing active game to show main menu.")
            self.mario_game_window.destroy()
            self.mario_game_window = None

        if self.mario_main_menu_window is None or not self.mario_main_menu_window.winfo_exists():
            self.mario_main_menu_window = MarioMainMenuWindow(self, self.actually_launch_mario_game)
            self.mario_main_menu_window.focus_set() 
        else:
            self.mario_main_menu_window.lift() 
            self.mario_main_menu_window.focus_set() 

    def actually_launch_mario_game(self):
        # This is called by the MarioMainMenuWindow when "1 PLAYER GAME" is selected.
        # First, ensure the main menu window is closed.
        if self.mario_main_menu_window and self.mario_main_menu_window.winfo_exists():
            self.mario_main_menu_window.destroy()
            self.mario_main_menu_window = None
        
        # Now, launch the game window.
        if self.mario_game_window is None or not self.mario_game_window.winfo_exists():
            self.mario_game_window = MarioGameWindow(self) # Pass self (CATOS_GUI) as master
            self.mario_game_window.focus_set() 
        else:
            self.mario_game_window.lift() 
            self.mario_game_window.focus_set() 

if __name__ == "__main__":
    app = CATOS_GUI() 
    app.mainloop()
