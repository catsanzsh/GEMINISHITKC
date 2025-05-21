import tkinter as tk
import time

# --- Game Constants ---
# NES Emulation Constants - PURE RETRO POWER!
NES_SCREEN_WIDTH = 256 # Standard NES PPU resolution, feel that tiny screen!
NES_SCREEN_HEIGHT = 240 # make 1-1 (User comment, seems like a note to self)
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
# Mariowiki map data for 1-1 often goes up to around 220-224 blocks.
# We'll set it a bit generously to accommodate everything.
WORLD_WIDTH_BLOCKS = 224 # SMB 1-1 is about 209 blocks long to the castle area. Let's give some buffer.
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

# MEOW-TASTIC NEW SPRITES!
PIPE_TOP_DATA = { # This sprite will be tiled for taller pipes.
    "colors": {
        "L": "NES_PIPE_GREEN_LIGHT", # Light green rim/highlight
        "M": "NES_PIPE_GREEN",       # Main green body
        "D": "NES_PIPE_GREEN_DARK",  # Dark green shadow
        "B": "NES_BLACK",            # Black for deep shadow/opening
        "X": None,
    },
    "pixels": [ # 16x16, looks like a classic pipe top!
        "XXLLLLLLLLLLXX", # Rim
        "XLMMMMMMMMMMMX", # Top body
        "XMBBBBBBBBBBMX", # Opening
        "XMBBBBBBBBBBMX", # Opening
        "XMDMMMMMMMMDMX", # Body shading starts
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
        "XMDDDDDDDDDDMX", # Base shadow of this segment
    ]
}

FLAGPOLE_BASE_BLOCK_DATA = { # This is for a 1x1 PLAYER_SIZE block
    "colors": {
        "G": "FLAGPOLE_GRAY",       # Main gray of the base block
        "D": "FLAGPOLE_DARK_GRAY",  # Darker gray for shading/top
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
        self.title("Mini Mario Game - SMB 1-1 Purr-fected++ MEGA DELUXE!")
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
            # top Y of the entire block structure in NES pixel coordinates (0 is top of screen)
            y1_nes = H - (map_y_bottom + height_blocks -1) * PS 
            # bottom Y of the entire block structure in NES pixel coordinates
            y2_nes = H - (map_y_bottom -1) * PS 
            # left X of the block structure in NES pixel coordinates
            x1_nes = map_x * PS
            # right X of the block structure in NES pixel coordinates
            x2_nes = x1_nes + width_blocks * PS
            
            self.visual_blocks_data.append({
                'coords': (x1_nes, y1_nes, x2_nes, y2_nes), 
                'type': type_str, 
                'collidable': collidable, 
                'sprite_data': sprite
            })

        # Ground Sections (SMB 1-1 Map based on Mariowiki)
        # Screen 0-3 (0-63)
        add_block(0, 1, 'ground', GROUND_BLOCK_DATA, width_blocks=69)  # Ground 0-68
        # Gap at 69-70
        # Screen 4-5 (64-95)
        add_block(71, 1, 'ground', GROUND_BLOCK_DATA, width_blocks=16) # Ground 71-86
        # Gap at 87-89
        # Screen 6-8 (96-143)
        add_block(90, 1, 'ground', GROUND_BLOCK_DATA, width_blocks=44) # Ground 90-133
        # Gap at 134-135 (under final stairs start)
        # Ground continues under final stairs and to end of defined world
        add_block(136, 1, 'ground', GROUND_BLOCK_DATA, width_blocks=(WORLD_WIDTH_BLOCKS - 136))


        # --- Floating Blocks, Bricks, Pipes, Stairs ---
        # Heights are map_y_bottom (1 = ground level)
        # Standard floating block height is 5 (4 blocks of air below)

        # Initial set of blocks
        add_block(16, 5, 'question_block_powerup', QUESTION_BLOCK_DATA) # ? (Mushroom/Flower)
        add_block(20, 5, 'brick', BRICK_BLOCK_DATA)
        add_block(21, 5, 'question_block_coin', QUESTION_BLOCK_DATA)    # ? (Coin)
        add_block(22, 5, 'brick', BRICK_BLOCK_DATA)
        add_block(23, 5, 'question_block_coin', QUESTION_BLOCK_DATA)    # ? (Coin)
        add_block(22, 9, 'question_block_1up', QUESTION_BLOCK_DATA)     # ? (Hidden 1-UP)

        # Pipes
        add_block(28, 1, 'pipe', PIPE_TOP_DATA, width_blocks=2, height_blocks=2) # Pipe 1 (H=2)
        add_block(38, 1, 'pipe', PIPE_TOP_DATA, width_blocks=2, height_blocks=3) # Pipe 2 (H=3)
        add_block(46, 1, 'pipe', PIPE_TOP_DATA, width_blocks=2, height_blocks=4) # Pipe 3 (H=4)
        add_block(57, 1, 'pipe', PIPE_TOP_DATA, width_blocks=2, height_blocks=4) # Pipe 4 (H=4, leads to bonus area!) MEOW!

        # Block Group after first pipes and first major gap (after x=70)
        add_block(78, 5, 'brick_coin', BRICK_BLOCK_DATA) # Brick (Coin)
        add_block(79, 5, 'question_block_powerup', QUESTION_BLOCK_DATA) # ? (Powerup) - was brick
        add_block(80, 5, 'brick_star', BRICK_BLOCK_DATA) # Brick (Star, visually a brick)
        add_block(81, 5, 'brick', BRICK_BLOCK_DATA)

        # Block Group after second major gap (after x=89)
        add_block(91, 5, 'question_block_coin', QUESTION_BLOCK_DATA)
        add_block(92, 5, 'brick', BRICK_BLOCK_DATA)
        add_block(93, 5, 'brick', BRICK_BLOCK_DATA)
        add_block(94, 5, 'question_block_powerup', QUESTION_BLOCK_DATA) # ? (Powerup)
        add_block(94, 9, 'brick_high', BRICK_BLOCK_DATA) # High brick

        # Helper for stairs (ascending to the right or single columns)
        def add_stair_segment(base_x, base_y_bottom, height_in_blocks):
            for i in range(height_in_blocks): # For each vertical layer of the current step
                add_block(base_x, base_y_bottom + i, 'ground_stair', GROUND_BLOCK_DATA, width_blocks=1, height_blocks=1)
        
        # Staircase 1 (Pyramid up, 4 steps high)
        add_stair_segment(100, 1, 1)
        add_stair_segment(101, 1, 2)
        add_stair_segment(102, 1, 3)
        add_stair_segment(103, 1, 4)

        # Blocks after staircase 1 pyramid
        add_block(106, 5, 'brick', BRICK_BLOCK_DATA)
        add_block(107, 5, 'brick', BRICK_BLOCK_DATA)
        add_block(108, 5, 'brick', BRICK_BLOCK_DATA)

        # Staircase 2 (Pyramid down, 4 steps high)
        add_stair_segment(109, 1, 4) # Tallest part of descending stairs
        add_stair_segment(110, 1, 3)
        add_stair_segment(111, 1, 2)
        add_stair_segment(112, 1, 1) # Shortest part of descending stairs

        # Staircase 3 (Pyramid up, 4 steps high, similar to Staircase 1)
        add_stair_segment(113, 1, 1)
        add_stair_segment(114, 1, 2)
        add_stair_segment(115, 1, 3)
        add_stair_segment(116, 1, 4)
        
        # Pipe after staircase 3
        add_block(118, 1, 'pipe', PIPE_TOP_DATA, width_blocks=2, height_blocks=2) # Pipe 5 (H=2, bonus exit often here)

        # Blocks before final stairs / next pipe
        add_block(123, 5, 'brick', BRICK_BLOCK_DATA)
        add_block(124, 5, 'brick_multicoin', BRICK_BLOCK_DATA) # Visually brick, special property (10 coins)
        add_block(125, 5, 'question_block_powerup', QUESTION_BLOCK_DATA) # ? (Powerup)
        add_block(126, 5, 'brick', BRICK_BLOCK_DATA)
        
        # Pipe
        add_block(129, 1, 'pipe', PIPE_TOP_DATA, width_blocks=2, height_blocks=2) # Pipe 6 (H=2)

        # Final Staircase (8 steps high, ascending to the right)
        for i in range(8): # i from 0 to 7
            add_stair_segment(134 + i, 1, i + 1) # Step height increases from 1 to 8

        # Flagpole Base and Pole
        add_block(142, 1, 'flagpole_base', FLAGPOLE_BASE_BLOCK_DATA)
        # Block at top of flagpole structure for pole to "rest" on
        add_block(142, 9, 'ground_stair', GROUND_BLOCK_DATA) # map_y_bottom = 9 for 1 block high

        pole_width_nes = PS / 4 # Visually make the pole thinner (4 NES pixels)
        pole_x_start_nes = (142 * PS) + (PS / 2) - (pole_width_nes / 2) # Centered on map_x=142
        # Pole sits effectively from map_y_bottom=2 (on top of base block) and is 8 blocks tall
        pole_y1_nes = H - (2 + 8 - 1) * PS # Top of pole (map_y_bottom_pole=2, height_blocks_pole=8)
        pole_y2_nes = H - (2 - 1) * PS     # Bottom of pole (where it meets base/top block)
        
        self.visual_blocks_data.append({
            'coords': (pole_x_start_nes, pole_y1_nes, pole_x_start_nes + pole_width_nes, pole_y2_nes),
            'type': 'flagpole_pole',
            'collidable': False,
            'sprite_data': FLAGPOLE_POLE_SPRITE_DATA
        })

        # Blocks after flagpole (approaching "castle" area)
        add_block(149, 5, 'brick', BRICK_BLOCK_DATA)
        add_block(150, 5, 'brick', BRICK_BLOCK_DATA)
        add_block(151, 5, 'brick', BRICK_BLOCK_DATA)

        add_block(157, 5, 'brick', BRICK_BLOCK_DATA)
        add_block(158, 5, 'brick', BRICK_BLOCK_DATA)
        add_block(159, 5, 'brick', BRICK_BLOCK_DATA)

        # Pipe near end of level area
        add_block(163, 1, 'pipe', PIPE_TOP_DATA, width_blocks=2, height_blocks=2) # Pipe 7 (H=2)

        # Small hills/platforms
        add_stair_segment(169, 1, 2) # 2 blocks high
        add_stair_segment(172, 1, 3) # 3 blocks high

        # Last pipe before typical end-of-level graphic (not implemented)
        add_block(179, 1, 'pipe', PIPE_TOP_DATA, width_blocks=2, height_blocks=2) # Pipe 8 (H=2)

        # --- SECRET BONUS AREA (COIN HEAVEN!) ---
        # Accessed via pipe at map_x=57. Placed far away in world coords.
        # Actual transition logic not implemented, just the blocks for the room.
        # This room is roughly one screen wide (16 blocks).
        bonus_room_map_x_start = 300 # Arbitrary far-off X coordinate
        
        # Floor of bonus room
        add_block(bonus_room_map_x_start, 1, 'brick', BRICK_BLOCK_DATA, width_blocks=16)
        # Ceiling of bonus room (map_y_bottom=13 means 12 blocks air, then ceiling, total room height about 13 player_size)
        # NES Screen height is 240px = 15 blocks (PLAYER_SIZE=16). map_y_bottom=13 means block is at y levels 13 and 14 from bottom.
        add_block(bonus_room_map_x_start, 14, 'brick', BRICK_BLOCK_DATA, width_blocks=16) # Top row (map_y_bottom 14, height 1)

        # Rows of Coin blocks
        # Row 1 (lower) - map_y_bottom = 4
        for i in range(10): # 10 ? blocks in a row
            add_block(bonus_room_map_x_start + 3 + i, 4, 'question_block_coin', QUESTION_BLOCK_DATA)
        # Row 2 (middle) - map_y_bottom = 7
        for i in range(10):
            add_block(bonus_room_map_x_start + 3 + i, 7, 'question_block_coin', QUESTION_BLOCK_DATA)
        # Row 3 (upper) - map_y_bottom = 10
        for i in range(10):
            add_block(bonus_room_map_x_start + 3 + i, 10, 'question_block_coin', QUESTION_BLOCK_DATA)

        # Exit pipe for bonus room (on the right side, on the floor)
        add_block(bonus_room_map_x_start + 14, 1, 'pipe', PIPE_TOP_DATA, width_blocks=2, height_blocks=2)
        # --- End of SMB 1-1 Level Data ---

        self.canvas_items_map = {} # Stores canvas item IDs for drawn blocks
        self.collidable_platform_coords = [] # Stores NES coordinates of collidable platforms
        self.draw_all_visual_blocks() # Initial draw of all blocks

        self.pressed_keys = set()
        self.bind_keys()
        self.game_loop()

    def draw_pixel_art(self, base_x_nes, base_y_nes, entity_width_nes, entity_height_nes, sprite_definition):
        """
        Draws a given sprite definition onto the canvas.
        base_x_nes, base_y_nes: Top-left corner of the entity in NES pixel coordinates.
        entity_width_nes, entity_height_nes: Total dimensions of the entity in NES pixels.
                                            The sprite art will be scaled to fit these dimensions.
        sprite_definition: A dictionary containing "colors" and "pixels" for the sprite.
        Returns a list of canvas item IDs created for this sprite.
        """
        pixel_art_rows = sprite_definition["pixels"]
        sprite_color_palette = {
            char_key: self.COLOR_MAP.get(mapped_color_key)
            for char_key, mapped_color_key in sprite_definition["colors"].items()
        }

        art_height_px_native = len(pixel_art_rows) # How many rows in the pixel art definition
        art_width_px_native = len(pixel_art_rows[0]) if art_height_px_native > 0 and isinstance(pixel_art_rows[0], str) else 0
        if art_width_px_native == 0 or art_height_px_native == 0: return [] # No pixels to draw

        scaled_pixel_width_nes = entity_width_nes / art_width_px_native
        scaled_pixel_height_nes = entity_height_nes / art_height_px_native
        
        drawn_item_ids = []
        for r_idx, row_str in enumerate(pixel_art_rows):
            for c_idx, color_char_key in enumerate(row_str):
                actual_color_hex = sprite_color_palette.get(color_char_key)
                if actual_color_hex: 
                    px_x1_nes = base_x_nes + (c_idx * scaled_pixel_width_nes)
                    py_y1_nes = base_y_nes + (r_idx * scaled_pixel_height_nes)
                    px_x2_nes = base_x_nes + ((c_idx + 1) * scaled_pixel_width_nes)
                    py_y2_nes = base_y_nes + ((r_idx + 1) * scaled_pixel_height_nes)
                    
                    px_x1_canvas = (px_x1_nes - self.camera_x) * self.scale
                    py_y1_canvas = py_y1_nes * self.scale 
                    px_x2_canvas = (px_x2_nes - self.camera_x) * self.scale
                    py_y2_canvas = py_y2_nes * self.scale
                    
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
        """
        Clears and redraws all visual blocks based on the current camera position.
        Also populates self.collidable_platform_coords with all collidable blocks.
        """
        for key in list(self.canvas_items_map.keys()):
            items_to_delete = self.canvas_items_map.pop(key)
            if isinstance(items_to_delete, list):
                for item_id in items_to_delete: self.canvas.delete(item_id)
            elif items_to_delete:
                self.canvas.delete(items_to_delete)
        
        self.collidable_platform_coords = [] 

        for i, block_data in enumerate(self.visual_blocks_data):
            coords_nes = block_data['coords'] 
            x1_nes, y1_nes, x2_nes, y2_nes = coords_nes
            
            if block_data.get('collidable', False):
                self.collidable_platform_coords.append(coords_nes)

            block_right_on_canvas = (x2_nes - self.camera_x) * self.scale
            block_left_on_canvas = (x1_nes - self.camera_x) * self.scale
            
            if block_right_on_canvas < 0 or block_left_on_canvas > DISPLAY_WIDTH:
                continue 

            block_width_nes = x2_nes - x1_nes
            block_height_nes = y2_nes - y1_nes
            block_type = block_data['type']
            sprite_data_for_block = block_data.get('sprite_data')
            
            current_block_pixel_ids = []

            if sprite_data_for_block:
                if block_type == 'flagpole_pole':
                    ids = self.draw_pixel_art(x1_nes, y1_nes, block_width_nes, block_height_nes, sprite_data_for_block)
                    current_block_pixel_ids.extend(ids)
                else:
                    tile_unit_w_nes = PLAYER_SIZE 
                    tile_unit_h_nes = PLAYER_SIZE
                    
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
            
            self.canvas_items_map[f"{block_type}_{i}"] = current_block_pixel_ids


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
        print("Closing Mario Game Window... Purrrr :3")
        self.destroy()

    def key_pressed(self, event):
        self.pressed_keys.add(event.keysym.lower())

    def key_released(self, event):
        try:
            self.pressed_keys.remove(event.keysym.lower())
        except KeyError:
            pass 

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
        # Allow player to go into bonus room area if it exists
        # WORLD_WIDTH_NES is for main level, bonus room is beyond
        max_player_x = WORLD_WIDTH_NES 
        # A simple check if bonus room exists (based on its starting X)
        # This logic would need to be more robust for actual transitions
        if any(block['coords'][0] >= 300 * PLAYER_SIZE for block in self.visual_blocks_data): # bonus_room_map_x_start = 300
             max_player_x = (300 + 20) * PLAYER_SIZE # Allow travel into a wider world if bonus room is present

        if self.player_x + PLAYER_SIZE > max_player_x: # Check against potentially larger world
            self.player_x = max_player_x - PLAYER_SIZE


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
                # Landing
                if self.player_vy >= 0 and next_player_bottom >= plat_top_nes and (self.player_y + PLAYER_SIZE) <= plat_top_nes + GRAVITY +1 : 
                    self.player_y = plat_top_nes - PLAYER_SIZE 
                    self.player_vy = 0
                    self.on_ground = True
                    self.is_jumping = False 
                    next_player_top = self.player_y 
                    next_player_bottom = self.player_y + PLAYER_SIZE

                # Hitting head
                elif self.player_vy < 0 and next_player_top <= plat_bottom_nes and self.player_y >= plat_bottom_nes - GRAVITY -1:
                    self.player_y = plat_bottom_nes 
                    self.player_vy = 1 
                    next_player_top = self.player_y
                    next_player_bottom = self.player_y + PLAYER_SIZE
            
            vertical_overlap_for_side = (next_player_bottom > plat_top_nes and next_player_top < plat_bottom_nes)

            if vertical_overlap_for_side:
                # Side collision (hitting left side of platform)
                if (self.player_x + PLAYER_SIZE) > plat_left_nes and self.player_x < plat_left_nes and (self.player_x + PLAYER_SIZE - MOVE_SPEED) <= plat_left_nes :
                    self.player_x = plat_left_nes - PLAYER_SIZE 
                    next_player_left = self.player_x
                    next_player_right = self.player_x + PLAYER_SIZE

                # Side collision (hitting right side of platform)
                elif self.player_x < plat_right_nes and (self.player_x + PLAYER_SIZE) > plat_right_nes and (self.player_x + MOVE_SPEED) >= plat_right_nes:
                    self.player_x = plat_right_nes 
                    next_player_left = self.player_x
                    next_player_right = self.player_x + PLAYER_SIZE

        if not self.on_ground and self.player_y > NES_SCREEN_HEIGHT + PLAYER_SIZE * 5 : # Fell way below screen
            print("Fell off! Oh noes! Resetting Mario, meow! So sad, like a kitten in the rain!")
            self.player_x = 3 * PLAYER_SIZE 
            self.player_y = NES_SCREEN_HEIGHT - 2 * PLAYER_SIZE 
            self.player_vy = 0
            self.on_ground = True 
            self.is_jumping = False
            self.camera_x = 0 
            
        target_camera_x = self.player_x - (NES_SCREEN_WIDTH / 2) + (PLAYER_SIZE / 2)
        # Max camera should consider the main world width, not bonus room unless player is there.
        # For now, simple clamp to main world width. True bonus room transition would handle camera differently.
        max_cam_x = WORLD_WIDTH_NES - NES_SCREEN_WIDTH
        # If player is in bonus room area, allow camera to go further
        if self.player_x > WORLD_WIDTH_NES:
             max_cam_x = (300 + 20) * PLAYER_SIZE - NES_SCREEN_WIDTH # Allow camera to see bonus room

        self.camera_x = max(0, min(target_camera_x, max_cam_x))
        self.camera_x = round(self.camera_x) 


    def game_loop(self):
        try:
            if not self.winfo_exists(): 
                print("Game window no longer exists. Stopping game loop. Bye bye, little butterfly!")
                return 
            
            start_time = time.perf_counter()

            self.handle_input() 
            self.apply_gravity_and_movement() 
            
            self.draw_all_visual_blocks() 
            self.update_player_visuals()  

            end_time = time.perf_counter()
            process_time_ms = (end_time - start_time) * 1000
            delay_ms = max(1, DELAY - int(process_time_ms)) 

            self.after(delay_ms, self.game_loop) 
        
        except tk.TclError as e:
            print(f"Game window closed or TclError: {e}. Gracefully exiting game loop. It's like a gentle purr ending...")
        except Exception as e:
            print(f"Oopsie, a little furball in the game loop: {e}. This is more tangled than a ball of yarn!")
            import traceback
            traceback.print_exc() 
            if self.winfo_exists(): 
                self.destroy()

class CATOS_GUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("CATOS - Meow Edition v3.1 FULL 1-1! THE MOST FUN EVER!") 
        self.geometry("600x550") # Slightly bigger for more awesome!
        self.configure(bg="#2c3e50") 

        title_label = tk.Label(self, text="CATOS Presents: SMB 1-1 COMPLETE!", font=("Arial Black", 26, "bold"), bg="#2c3e50", fg="#1abc9c") # Teal title
        title_label.pack(pady=30)

        cat_art_text = (
            "  /\\_/\\    -- MEOW! --\n"
            " ( o.o )  World 1-1 Fully Loaded!\n"
            "  > ^ <   Pipes, secrets, all here!\n"
            " CATOS NES EVO++ HYPER EDITION!"
        )
        cat_label = tk.Label(self,text=cat_art_text,font=("Courier New", 16, "bold"),bg="#2c3e50",fg="#f1c40f",justify=tk.LEFT) # Golden text
        cat_label.pack(pady=25)

        launch_button = tk.Button(
            self, text="LET'S-A GO! Play SMB 1-1!", font=("Impact", 20),bg="#e67e22", fg="white", # Carrot orange button
            activebackground="#d35400",relief=tk.RAISED, borderwidth=3, padx=20,pady=15,command=self.launch_mario_game)
        launch_button.pack(pady=25)

        self.clock_label = tk.Label(self,text="",font=("Consolas", 14),bg="#2c3e50",fg="#95a5a6") # Silver clock text
        self.clock_label.pack(side=tk.BOTTOM, pady=15)
        self.update_clock() 
        self.mario_game_window = None 

    def update_clock(self):
        current_time = time.strftime("%I:%M:%S %p \n %A, %B %d, %Y \n Tick-tock, it's game o'clock, meow!")
        self.clock_label.config(text=current_time)
        self.after(1000, self.update_clock) 

    def launch_mario_game(self):
        if self.mario_game_window is None or not self.mario_game_window.winfo_exists():
            self.mario_game_window = MarioGameWindow(self) 
            self.mario_game_window.focus_set() 
            print("Launching SMB 1-1! Get ready for an adventure, purrrr!")
        else:
            self.mario_game_window.lift() 
            self.mario_game_window.focus_set()
            print("Game window already open, bringing it to the front! More fun times ahead, meow!")

if __name__ == "__main__":
    app = CATOS_GUI()
    app.mainloop()
