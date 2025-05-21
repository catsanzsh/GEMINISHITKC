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
        "R": "MARIO_RED",       # Will map to self.MARIO_RED
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

# MEOW-TASTIC NEW SPRITES!
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

class MarioGameWindow(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Mini Mario Game - SMB 1-1 Purr-fected++!")
        self.geometry(f"{DISPLAY_WIDTH}x{DISPLAY_HEIGHT}")
        self.resizable(False, False)

        # --- Enhanced NES Color Palette ---
        self.NES_SKY_BLUE = "#5C94FC"
        self.NES_BRICK_COLOR = "#D07030"
        self.NES_BRICK_DARK = "#A04000"
        self.NES_QUESTION_BLOCK_COLOR = "#FAC000"
        self.NES_QUESTION_OUTLINE = "#E4A000"
        self.NES_QUESTION_SHADOW = "#783000"
        self.NES_GROUND_COLOR = "#E09050" # A bit more saturated for SMB feel
        self.NES_GROUND_DARK = "#A04000" # Darker lines/texture for ground
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

        self.configure(bg=self.NES_SKY_BLUE)

        self.canvas = tk.Canvas(self, width=DISPLAY_WIDTH, height=DISPLAY_HEIGHT, bg=self.NES_SKY_BLUE, highlightthickness=0)
        self.canvas.pack()

        self.scale = DISPLAY_WIDTH / NES_SCREEN_WIDTH
        
        # Player attributes in NES pixels
        self.player_x = 3 * PLAYER_SIZE # Start near beginning of 1-1
        self.player_y = NES_SCREEN_HEIGHT - 2 * PLAYER_SIZE # Start on ground
        self.player_vy = 0
        self.is_jumping = False
        self.on_ground = True # Start on ground

        self.camera_x = 0

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

        self.player_pixel_ids = []
        
        # --- SMB 1-1 Level Data Generation MEOW! ---
        self.visual_blocks_data = []
        
        # Helper constants for level building
        PS = PLAYER_SIZE
        H = NES_SCREEN_HEIGHT
        
        # Helper function to add blocks to self.visual_blocks_data
        def add_block(map_x, map_y_bottom, type_str, sprite, width_blocks=1, height_blocks=1, collidable=True):
            # map_y_bottom: 1 means ground level, 2 means one block layer above ground, etc.
            # top Y of the entire block structure
            y1_nes = H - (map_y_bottom + height_blocks - 1) * PS 
            # bottom Y of the entire block structure
            y2_nes = H - (map_y_bottom - 1) * PS 
            x1_nes = map_x * PS
            x2_nes = x1_nes + width_blocks * PS
            
            self.visual_blocks_data.append({
                'coords': (x1_nes, y1_nes, x2_nes, y2_nes), 
                'type': type_str, 
                'collidable': collidable, 
                'sprite_data': sprite
            })

        # Ground Sections (SMB 1-1 Map based on Mariowiki)
        add_block(0, 1, 'ground', GROUND_BLOCK_DATA, width_blocks=69)
        add_block(71, 1, 'ground', GROUND_BLOCK_DATA, width_blocks=15) # Gap from 69-70
        add_block(90, 1, 'ground', GROUND_BLOCK_DATA, width_blocks=44) # Gap from 86-89
        add_block(136, 1, 'ground', GROUND_BLOCK_DATA, width_blocks=(WORLD_WIDTH_BLOCKS - 136)) # Gap from 134-135 (under final stairs)

        # Floating Blocks and Bricks (Standard height map_y_bottom=5)
        add_block(16, 5, 'question_block_powerup', QUESTION_BLOCK_DATA) # ? (Mushroom/Flower)
        add_block(20, 5, 'brick', BRICK_BLOCK_DATA)
        add_block(21, 5, 'question_block_coin', QUESTION_BLOCK_DATA)    # ? (Coin)
        add_block(22, 5, 'brick', BRICK_BLOCK_DATA)
        add_block(23, 5, 'question_block_coin', QUESTION_BLOCK_DATA)    # ? (Coin)
        add_block(22, 9, 'question_block_1up', QUESTION_BLOCK_DATA)     # ? (Hidden 1-UP, visually a Q block)

        # Pipes (map_x, base_y_level=1, width=2, height_in_blocks)
        add_block(28, 1, 'pipe', PIPE_TOP_DATA, width_blocks=2, height_blocks=2) # Pipe 1 (H=2)
        add_block(38, 1, 'pipe', PIPE_TOP_DATA, width_blocks=2, height_blocks=3) # Pipe 2 (H=3)
        add_block(46, 1, 'pipe', PIPE_TOP_DATA, width_blocks=2, height_blocks=4) # Pipe 3 (H=4)
        add_block(57, 1, 'pipe', PIPE_TOP_DATA, width_blocks=2, height_blocks=4) # Pipe 4 (H=4, leads to bonus)
        
        # Block Group after first pipes and gap
        add_block(78, 5, 'brick_coin', BRICK_BLOCK_DATA) # Brick (Coin)
        add_block(79, 5, 'brick', BRICK_BLOCK_DATA)
        add_block(80, 5, 'brick_star', BRICK_BLOCK_DATA) # Brick (Star, make it a regular brick visually)
        add_block(81, 5, 'brick', BRICK_BLOCK_DATA)

        # Block Group after second gap
        add_block(91, 5, 'question_block_coin', QUESTION_BLOCK_DATA)
        add_block(92, 5, 'brick', BRICK_BLOCK_DATA)
        add_block(93, 5, 'brick', BRICK_BLOCK_DATA)
        add_block(94, 5, 'question_block_powerup', QUESTION_BLOCK_DATA) # ? (Powerup)
        add_block(94, 9, 'brick_high', BRICK_BLOCK_DATA) # High brick

        # Helper for stairs (ascending to the right)
        def add_stair_segment(base_x, base_y_bottom, height_in_blocks):
            for i in range(height_in_blocks): # For each vertical layer of the current step
                add_block(base_x, base_y_bottom + i, 'ground_stair', GROUND_BLOCK_DATA, width_blocks=1, height_blocks=1)
        
        # Staircase 1 (4 steps high, decreasing height to the right, effectively ascending left if approaching from right)
        # This is actually a pyramid structure.
        # Mariowiki map: blocks at (100,1), (101,1-2), (102,1-3), (103,1-4)
        add_stair_segment(100, 1, 1)
        add_stair_segment(101, 1, 2)
        add_stair_segment(102, 1, 3)
        add_stair_segment(103, 1, 4)

        # Blocks after staircase 1
        add_block(106, 5, 'brick', BRICK_BLOCK_DATA)
        add_block(107, 5, 'brick', BRICK_BLOCK_DATA)
        add_block(108, 5, 'brick', BRICK_BLOCK_DATA)

        # Staircase 2 (similar to staircase 1)
        # Mariowiki map: blocks at (113,1), (114,1-2), (115,1-3), (116,1-4)
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

        # Final Staircase (8 steps high)
        # Mariowiki map: blocks from (134,1) to (141,1-8)
        for i in range(8): # i from 0 to 7
            add_stair_segment(134 + i, 1, i + 1) # Step height increases from 1 to 8

        # Flagpole Base
        # Flagpole base block at x=142, y=1 (map coordinates)
        add_block(142, 1, 'flagpole_base', FLAGPOLE_BASE_BLOCK_DATA, width_blocks=1, height_blocks=1)

        # Flagpole Pole (decorative, non-collidable)
        # Pole sits on top of the base block. Base block top is at H - 1*PS.
        # Pole starts at map_y_bottom = 2, extends 8 blocks high.
        # Pole x centered on base block (142). Sprite is thin.
        pole_width_nes = PS / 4 # Visually make the pole thinner than a full block
        pole_x_start_nes = (142 * PS) + (PS / 2) - (pole_width_nes / 2) # Centered
        pole_y1_nes = H - (2 + 8 - 1) * PS # Top of an 8-block high pole starting at level 2
        pole_y2_nes = H - (2 - 1) * PS     # Bottom of that pole (top of base block)
        
        self.visual_blocks_data.append({
            'coords': (pole_x_start_nes, pole_y1_nes, pole_x_start_nes + pole_width_nes, pole_y2_nes),
            'type': 'flagpole_pole',
            'collidable': False,
            'sprite_data': FLAGPOLE_POLE_SPRITE_DATA
        })
        # --- End of SMB 1-1 Level Data ---

        self.canvas_items_map = {}
        self.collidable_platform_coords = []
        self.draw_all_visual_blocks()

        self.pressed_keys = set()
        self.bind_keys()
        self.game_loop()

    def draw_pixel_art(self, base_x_nes, base_y_nes, entity_width_nes, entity_height_nes, sprite_definition):
        pixel_art_rows = sprite_definition["pixels"]
        sprite_color_palette = {
            char_key: self.COLOR_MAP.get(mapped_color_key)
            for char_key, mapped_color_key in sprite_definition["colors"].items()
        }

        art_height_px_native = len(pixel_art_rows)
        art_width_px_native = len(pixel_art_rows[0]) if art_height_px_native > 0 and isinstance(pixel_art_rows[0], str) else 0
        if art_width_px_native == 0: return [] 

        canvas_pixel_width_internal = entity_width_nes / art_width_px_native
        canvas_pixel_height_internal = entity_height_nes / art_height_px_native
        
        drawn_item_ids = []
        for r_idx, row_str in enumerate(pixel_art_rows):
            for c_idx, color_char_key in enumerate(row_str):
                actual_color_hex = sprite_color_palette.get(color_char_key)
                if actual_color_hex: 
                    px_x1_nes = base_x_nes + (c_idx * canvas_pixel_width_internal)
                    py_y1_nes = base_y_nes + (r_idx * canvas_pixel_height_internal)
                    px_x2_nes = base_x_nes + ((c_idx + 1) * canvas_pixel_width_internal)
                    py_y2_nes = base_y_nes + ((r_idx + 1) * canvas_pixel_height_internal)
                    
                    # Convert to canvas coordinates, apply camera and scaling
                    px_x1_canvas = (px_x1_nes - self.camera_x) * self.scale
                    py_y1_canvas = py_y1_nes * self.scale 
                    px_x2_canvas = (px_x2_nes - self.camera_x) * self.scale
                    py_y2_canvas = py_y2_nes * self.scale
                    
                    # Optimization: Don't draw if entirely off-screen horizontally
                    if px_x2_canvas < 0 or px_x1_canvas > DISPLAY_WIDTH:
                        continue

                    if px_x2_canvas - px_x1_canvas < 1: px_x2_canvas = px_x1_canvas + 1
                    if py_y2_canvas - py_y1_canvas < 1: py_y2_canvas = py_y1_canvas + 1

                    pixel_id = self.canvas.create_rectangle(
                        px_x1_canvas, py_y1_canvas, px_x2_canvas, py_y2_canvas,
                        fill=actual_color_hex, outline="" 
                    )
                    drawn_item_ids.append(pixel_id)
        return drawn_item_ids

    def draw_all_visual_blocks(self):
        for key in list(self.canvas_items_map.keys()):
            items = self.canvas_items_map.pop(key)
            if isinstance(items, list):
                for item_id in items: self.canvas.delete(item_id)
            else:
                self.canvas.delete(items)
        self.collidable_platform_coords = [] 

        for i, block_data in enumerate(self.visual_blocks_data):
            coords_nes = block_data['coords'] 
            x1_nes, y1_nes, x2_nes, y2_nes = coords_nes
            
            # Optimization: Basic culling if block is entirely off-screen (camera view)
            block_right_on_canvas = (x2_nes - self.camera_x) * self.scale
            block_left_on_canvas = (x1_nes - self.camera_x) * self.scale
            if block_right_on_canvas < 0 or block_left_on_canvas > DISPLAY_WIDTH:
                if block_data.get('collidable', False): # Still need its collision data
                     self.collidable_platform_coords.append(coords_nes)
                continue # Don't draw if not visible

            block_width_nes = x2_nes - x1_nes
            block_height_nes = y2_nes - y1_nes
            block_type = block_data['type']
            sprite_data_for_block = block_data.get('sprite_data')
            
            current_block_pixel_ids = []

            if sprite_data_for_block:
                # For blocks like ground, pipes, they can be wider/taller than 1 PLAYER_SIZE unit.
                # We tile the 16x16 (PLAYER_SIZE) sprite across them.
                tile_unit_w_nes = PLAYER_SIZE 
                tile_unit_h_nes = PLAYER_SIZE

                # Special handling for thin items like flagpole pole where block_width might be < PLAYER_SIZE
                if block_width_nes < tile_unit_w_nes : tile_unit_w_nes = block_width_nes
                if block_height_nes < tile_unit_h_nes : tile_unit_h_nes = block_height_nes


                num_tiles_x = max(1, int(round(block_width_nes / tile_unit_w_nes)))
                num_tiles_y = max(1, int(round(block_height_nes / tile_unit_h_nes)))
                
                tile_draw_width_nes = block_width_nes / num_tiles_x
                tile_draw_height_nes = block_height_nes / num_tiles_y

                for row in range(num_tiles_y):
                    for col in range(num_tiles_x):
                        tile_x_nes = x1_nes + (col * tile_draw_width_nes)
                        tile_y_nes = y1_nes + (row * tile_draw_height_nes)
                        ids = self.draw_pixel_art(tile_x_nes, tile_y_nes, tile_draw_width_nes, tile_draw_height_nes, sprite_data_for_block)
                        current_block_pixel_ids.extend(ids)
            # Fallback removed as all items should have sprites now

            self.canvas_items_map[f"{block_type}_{i}"] = current_block_pixel_ids

            if block_data.get('collidable', False):
                self.collidable_platform_coords.append(coords_nes)

    def update_player_visuals(self):
        for pixel_id in self.player_pixel_ids:
            self.canvas.delete(pixel_id)
        self.player_pixel_ids = [] 

        self.player_pixel_ids = self.draw_pixel_art(
            self.player_x, self.player_y,
            PLAYER_SIZE, PLAYER_SIZE, 
            SMALL_MARIO_STANDING_DATA 
        )

    def bind_keys(self):
        self.focus_set() 
        self.bind("<KeyPress>", self.key_pressed)
        self.bind("<KeyRelease>", self.key_released)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        self.destroy()

    def key_pressed(self, event):
        self.pressed_keys.add(event.keysym.lower())

    def key_released(self, event):
        if event.keysym.lower() in self.pressed_keys:
            self.pressed_keys.remove(event.keysym.lower())

    def handle_input(self):
        if 'a' in self.pressed_keys or 'left' in self.pressed_keys:
            self.player_x -= MOVE_SPEED
        if 'd' in self.pressed_keys or 'right' in self.pressed_keys:
            self.player_x += MOVE_SPEED
        if ('w' in self.pressed_keys or 'up' in self.pressed_keys or 'space' in self.pressed_keys) and self.on_ground:
            self.player_vy = -JUMP_POWER
            self.is_jumping = True
            self.on_ground = False
            
        if self.player_x < 0: self.player_x = 0
        if self.player_x + PLAYER_SIZE > WORLD_WIDTH_NES:
            self.player_x = WORLD_WIDTH_NES - PLAYER_SIZE

    def apply_gravity_and_movement(self):
        if not self.on_ground:
            self.player_vy += GRAVITY
        self.player_y += self.player_vy

        next_player_top = self.player_y
        next_player_bottom = self.player_y + PLAYER_SIZE
        next_player_left = self.player_x
        next_player_right = self.player_x + PLAYER_SIZE
        
        self.on_ground = False

        for p_coords_nes in self.collidable_platform_coords:
            plat_left_nes, plat_top_nes, plat_right_nes, plat_bottom_nes = p_coords_nes
            horizontal_overlap = (next_player_right > plat_left_nes and next_player_left < plat_right_nes)

            if horizontal_overlap:
                # Landing on top
                if self.player_vy >= 0 and next_player_bottom >= plat_top_nes and self.player_y < plat_top_nes: 
                    self.player_y = plat_top_nes - PLAYER_SIZE
                    self.player_vy = 0
                    self.on_ground = True
                    self.is_jumping = False
                    next_player_top = self.player_y 
                    next_player_bottom = self.player_y + PLAYER_SIZE
                # Hitting head from bottom
                elif self.player_vy < 0 and next_player_top <= plat_bottom_nes and next_player_bottom > plat_bottom_nes:
                    self.player_y = plat_bottom_nes
                    self.player_vy = 1 
                    next_player_top = self.player_y
                    next_player_bottom = self.player_y + PLAYER_SIZE
                # Side collision
                elif next_player_bottom > plat_top_nes and next_player_top < plat_bottom_nes: 
                    # Collision from left side of platform
                    if next_player_right > plat_left_nes and self.player_x + PLAYER_SIZE <= plat_left_nes + MOVE_SPEED : # Was to the left, now intersecting
                         self.player_x = plat_left_nes - PLAYER_SIZE
                         next_player_left = self.player_x
                         next_player_right = self.player_x + PLAYER_SIZE
                    # Collision from right side of platform
                    elif next_player_left < plat_right_nes and self.player_x >= plat_right_nes - MOVE_SPEED: # Was to the right, now intersecting
                         self.player_x = plat_right_nes
                         next_player_left = self.player_x
                         next_player_right = self.player_x + PLAYER_SIZE

        if not self.on_ground and self.player_y > NES_SCREEN_HEIGHT + PLAYER_SIZE * 2 : 
            print("Fell off! Oh noes! Resetting Mario, meow!")
            self.player_x = 3 * PLAYER_SIZE # Reset to start of level
            self.player_y = NES_SCREEN_HEIGHT - 2 * PLAYER_SIZE 
            self.player_vy = 0
            self.on_ground = True 
            self.is_jumping = False
            self.camera_x = 0 # Reset camera too
            
        target_camera_x = self.player_x - (NES_SCREEN_WIDTH / 2) + (PLAYER_SIZE / 2)
        self.camera_x = max(0, min(target_camera_x, WORLD_WIDTH_NES - NES_SCREEN_WIDTH))
        self.camera_x = round(self.camera_x)


    def game_loop(self):
        try:
            if not self.winfo_exists(): return 
            start_time = time.perf_counter()

            self.handle_input() 
            self.apply_gravity_and_movement() 
            self.draw_all_visual_blocks() 
            self.update_player_visuals() 

            end_time = time.perf_counter()
            process_time_ms = (end_time - start_time) * 1000
            delay_ms = max(1, DELAY - int(process_time_ms)) 

            self.after(delay_ms, self.game_loop) 
        except tk.TclError:
            print("Game window closed gracefully, like a cat landing on its feet! Purrrr.")
        except Exception as e:
            print(f"Oopsie, a little furball in the game loop: {e}")
            import traceback
            traceback.print_exc() 
            self.destroy()

class CATOS_GUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("CATOS - Meow Edition v3.0 NES Emu! THE ULTIMATE!") 
        self.geometry("500x500") 
        self.configure(bg="#2c3e50") 

        title_label = tk.Label(self, text="Welcome to CATOS! SMB 1-1 Loaded!", font=("Arial", 24, "bold"), bg="#2c3e50", fg="white")
        title_label.pack(pady=30)

        cat_art_text = "  /\_/\ \n ( >w< )  < WORLD 1-1 READY!\n  > ^ < \nCATOS NES EVO++!"
        cat_label = tk.Label(self,text=cat_art_text,font=("Courier New", 14),bg="#2c3e50",fg="#ecf0f1",justify=tk.LEFT)
        cat_label.pack(pady=20)

        launch_button = tk.Button(
            self, text="Play SMB 1-1!", font=("Arial", 16),bg="#e74c3c", fg="white",
            activebackground="#c0392b",relief=tk.FLAT,padx=15,pady=10,command=self.launch_mario_game)
        launch_button.pack(pady=20)

        self.clock_label = tk.Label(self,text="",font=("Arial", 12),bg="#2c3e50",fg="#bdc3c7")
        self.clock_label.pack(side=tk.BOTTOM, pady=10)
        self.update_clock() 
        self.mario_game_window = None

    def update_clock(self):
        current_time = time.strftime("%H:%M:%S %p \n %A, %B %d, %Y")
        self.clock_label.config(text=current_time)
        self.after(1000, self.update_clock) 

    def launch_mario_game(self):
        if self.mario_game_window is None or not self.mario_game_window.winfo_exists():
            self.mario_game_window = MarioGameWindow(self)
            self.mario_game_window.focus_set() 
        else:
            self.mario_game_window.lift() 
            self.mario_game_window.focus_set() 

if __name__ == "__main__":
    app = CATOS_GUI()
    app.mainloop()
