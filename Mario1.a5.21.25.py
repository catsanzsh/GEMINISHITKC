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

# World Dimensions (in NES pixels) - Make a big, beautiful level!
WORLD_WIDTH_NES = NES_SCREEN_WIDTH * 4 # Example: A sprawling 4 screens wide world! SO MUCH FUN!
WORLD_HEIGHT_NES = NES_SCREEN_HEIGHT # Vertical scrolling is for losers, just like the real NES!

PLAYER_SIZE = 16 # This is the size of our drawn entities (Mario, blocks) in glorious NES pixels (16x16 sprite)!
GRAVITY = 0.5 # Adjusted for NES pixel units, feels so authentically bouncy!
JUMP_POWER = 8 # Get that satisfying NES jump height, little buddy!
MOVE_SPEED = 2 # Slower, more precise movement, just like the good old days!
FPS = 60 # Smooth as a baby's butt!
DELAY = 1000 // FPS # Keep that frame rate locked down, meow!

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
    "pixels": [ 
        "LLLLDDDDDDLLLL",
        "LLDDLLLLDDLLLL",
        "LDDLLLLLLDDLLL",
        "LDDLLLLLLDDLLL",
        "LLDDLLLLDDLLLL",
        "LLLLDDDDDDLLLL",
        "LLLLLLLLLLLLLL", 
        "LLLLLLLLLLLLLL",
        "DDDDDDDDDDDDDDDD", 
        "DDDDDDDDDDDDDDDD",
        "LLLLLLLLLLLLLL",
        "LLLLLLLLLLLLLL",
        "LLLLLLLLLLLLLL",
        "LLLLLLLLLLLLLL",
        "LLLLLLLLLLLLLL",
        "LLLLLLLLLLLLLL",
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
        "XLMMMMMMMMMMMX", # Changed L to M on sides for smoother transition
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

FLAGPOLE_BASE_BLOCK_DATA = {
    "colors": {
        "G": "FLAGPOLE_GRAY",        # Main gray of the base block
        "D": "FLAGPOLE_DARK_GRAY",   # Darker gray for shading/top
        "X": None
    },
    "pixels": [ # Art is 8 wide, 16 tall, for a sturdy base!
        "DDDDDDDD", # Top surface
        "DGGGGXXD", # Giving it a bit of a shape
        "DGGGGXXD",
        "DGGGGXXD",
        "DGGGGXXD",
        "DGGGGXXD",
        "DGGGGXXD",
        "DGGGGXXD",
        "DGGGGXXD",
        "DGGGGXXD",
        "DGGGGXXD",
        "DGGGGXXD",
        "DGGGGXXD",
        "DGGGGXXD",
        "DGGGGXXD",
        "DDDDDDDD"  # Bottom of the base block
    ]
}

FLAGPOLE_POLE_SPRITE_DATA = {
    "colors": {
        "L": "FLAGPOLE_GRAY",      # Lighter part of pole
        "D": "FLAGPOLE_DARK_GRAY", # Darker/shadow part
        "X": None,
    },
    "pixels": [ # 2 pixels wide, 16 high native art - simple and sleek!
        "LD", "LD", "LD", "LD",
        "LD", "LD", "LD", "LD",
        "LD", "LD", "LD", "LD",
        "LD", "LD", "LD", "LD",
        "LD", "LD", "LD", "LD", 
        "LD", "LD", "LD", "LD",
        "LD", "LD", "LD", "LD",
        "LD", "LD", "LD", "LD",
    ]
}


# --- End of Pixel Art Data ---

class MarioGameWindow(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Mini Mario Game - NES Pixels Purr-fected++!")
        self.geometry(f"{DISPLAY_WIDTH}x{DISPLAY_HEIGHT}") # Use scaled dimensions for that crisp look!
        self.resizable(False, False) # No resizing, just like a real NES!

        # --- Enhanced NES Color Palette, purrloined by HQRIPPER 7.1! ---
        self.NES_SKY_BLUE = "#5C94FC"
        self.NES_BRICK_COLOR = "#D07030"
        self.NES_BRICK_DARK = "#A04000"
        self.NES_QUESTION_BLOCK_COLOR = "#FAC000"
        self.NES_QUESTION_OUTLINE = "#E4A000"
        self.NES_QUESTION_SHADOW = "#783000"
        self.NES_GROUND_COLOR = "#E09050"
        self.NES_GROUND_DARK = "#A04000"
        
        # Enhanced and New Colors! So vibrant, it'll make your eyes water with joy!
        self.MARIO_RED = "#D03030"             # A more authentic NES Mario Red-Orange!
        self.NES_SKIN_PEACH = "#FCB8A0"        # Slightly adjusted NES skin tone, so peachy!
        self.NES_DARK_BROWN = "#782818"        # More reddish-brown for hair/shoes, looking good!
        self.NES_PIPE_GREEN = "#30A020"        # Main pipe color, so vivid!
        self.NES_PIPE_GREEN_LIGHT = "#80D010"  # Lighter green for pipe highlights/rim, sparkle sparkle!
        self.NES_PIPE_GREEN_DARK = "#207818"   # Darker green for pipe shadows, spooky!
        self.FLAGPOLE_GRAY = "#B0B0B0"         # Lighter gray for flagpole, sleek!
        self.FLAGPOLE_DARK_GRAY = "#707070"    # Darker gray for flagpole shading, dynamic!
        self.NES_WHITE = "#FCFCFC"             # NES White (slightly off-white for less harshness), so pure!
        self.NES_BLACK = "#000000"             # Pure black for strong contrast, BAM!


        self.configure(bg=self.NES_SKY_BLUE) # Set that classic NES sky blue!

        self.canvas = tk.Canvas(self, width=DISPLAY_WIDTH, height=DISPLAY_HEIGHT, bg=self.NES_SKY_BLUE, highlightthickness=0)
        self.canvas.pack()

        # Scaling factor from NES pixels to Tkinter display pixels. This is the secret sauce!
        self.scale = DISPLAY_WIDTH / NES_SCREEN_WIDTH 
        # Player attributes in NES pixels - all internal logic happens here!
        self.player_x = 50 # Starting position in NES pixels, not some bloated modern resolution!
        self.player_y = NES_SCREEN_HEIGHT - PLAYER_SIZE - 2 # Start just above ground, ready for action!
        self.player_vy = 0
        self.is_jumping = False
        self.on_ground = False

        # Camera position in world coordinates (NES pixels). This is how we scroll, baby!
        self.camera_x = 0

        # This dictionary maps color keys from sprite data to actual color values. It's a color wonderland!
        self.COLOR_MAP = {
            "MARIO_RED": self.MARIO_RED,
            "NES_SKIN_PEACH": self.NES_SKIN_PEACH,
            "NES_DARK_BROWN": self.NES_DARK_BROWN,
            "NES_BRICK_DARK": self.NES_BRICK_DARK,
            "NES_BRICK_COLOR": self.NES_BRICK_COLOR,
            "NES_QUESTION_OUTLINE": self.NES_QUESTION_OUTLINE,
            "NES_QUESTION_BLOCK_COLOR": self.NES_QUESTION_BLOCK_COLOR,
            "NES_WHITE": self.NES_WHITE,
            "NES_QUESTION_SHADOW": self.NES_QUESTION_SHADOW,
            "NES_GROUND_DARK": self.NES_GROUND_DARK,
            "NES_GROUND_COLOR": self.NES_GROUND_COLOR,
            "NES_PIPE_GREEN": self.NES_PIPE_GREEN,
            "NES_PIPE_GREEN_LIGHT": self.NES_PIPE_GREEN_LIGHT,
            "NES_PIPE_GREEN_DARK": self.NES_PIPE_GREEN_DARK,
            "NES_BLACK": self.NES_BLACK,
            "FLAGPOLE_GRAY": self.FLAGPOLE_GRAY,
            "FLAGPOLE_DARK_GRAY": self.FLAGPOLE_DARK_GRAY,
        }

        self.player_pixel_ids = []

        # --- Visual Blocks Data: NOW IN GLORIOUS NES PIXEL COORDINATES! So retro, so perfect! ---
        # All coordinates are now in NES pixels. PLAYER_SIZE is 16 NES pixels, our standard unit!
        self.visual_blocks_data = [
            # Ground extending across the entire world - SOLID AS A ROCK!
            {'coords': (0, NES_SCREEN_HEIGHT - PLAYER_SIZE, WORLD_WIDTH_NES, NES_SCREEN_HEIGHT), 'type': 'ground', 'collidable': True, 'sprite_data': GROUND_BLOCK_DATA},
            
            # Platforms and blocks, placed precisely on the NES pixel grid! Oh yeah!
            {'coords': (9 * PLAYER_SIZE, NES_SCREEN_HEIGHT - PLAYER_SIZE * 5, 9 * PLAYER_SIZE + PLAYER_SIZE * 3, NES_SCREEN_HEIGHT - PLAYER_SIZE * 4), 'type': 'brick_platform', 'collidable': True, 'sprite_data': BRICK_BLOCK_DATA},
            {'coords': (12 * PLAYER_SIZE, NES_SCREEN_HEIGHT - PLAYER_SIZE * 7, 12 * PLAYER_SIZE + PLAYER_SIZE, NES_SCREEN_HEIGHT - PLAYER_SIZE * 6), 'type': 'question_block', 'collidable': True, 'sprite_data': QUESTION_BLOCK_DATA},
            {'coords': (13 * PLAYER_SIZE + 5, NES_SCREEN_HEIGHT - PLAYER_SIZE * 7, 13 * PLAYER_SIZE + 5 + PLAYER_SIZE, NES_SCREEN_HEIGHT - PLAYER_SIZE * 6), 'type': 'brick', 'collidable': True, 'sprite_data': BRICK_BLOCK_DATA},
            {'coords': (14 * PLAYER_SIZE + 10, NES_SCREEN_HEIGHT - PLAYER_SIZE * 7, 14 * PLAYER_SIZE + 10 + PLAYER_SIZE, NES_SCREEN_HEIGHT - PLAYER_SIZE * 6), 'type': 'question_block', 'collidable': True, 'sprite_data': QUESTION_BLOCK_DATA},
            {'coords': (18 * PLAYER_SIZE, NES_SCREEN_HEIGHT - PLAYER_SIZE * 6, 18 * PLAYER_SIZE + PLAYER_SIZE * 4, NES_SCREEN_HEIGHT - PLAYER_SIZE * 5), 'type': 'elevated_ground', 'collidable': True, 'sprite_data': GROUND_BLOCK_DATA},
            
            # Pipe with new sprite! So cool, so green, so NES!
            {'coords': (24 * PLAYER_SIZE, NES_SCREEN_HEIGHT - PLAYER_SIZE * 3, 24 * PLAYER_SIZE + PLAYER_SIZE * 2, NES_SCREEN_HEIGHT - PLAYER_SIZE), 'type': 'pipe_top', 'collidable': True, 'sprite_data': PIPE_TOP_DATA}, 
            
            {'coords': (3 * PLAYER_SIZE, NES_SCREEN_HEIGHT - PLAYER_SIZE * 9, 3 * PLAYER_SIZE + PLAYER_SIZE * 3, NES_SCREEN_HEIGHT - PLAYER_SIZE * 8), 'type': 'high_brick_platform', 'collidable': True, 'sprite_data': BRICK_BLOCK_DATA},
            {'coords': (16 * PLAYER_SIZE, NES_SCREEN_HEIGHT - PLAYER_SIZE * 12, 16 * PLAYER_SIZE + PLAYER_SIZE * 4, NES_SCREEN_HEIGHT - PLAYER_SIZE * 11), 'type': 'summit_platform', 'collidable': True, 'sprite_data': GROUND_BLOCK_DATA},
            
            # Flagpole parts with new sprites! Almost there, you can do it!
            # Base is 8 pixels wide, pole is 2 pixels wide. PLAYER_SIZE is 16. Pixel perfect placement!
            {'coords': (WORLD_WIDTH_NES - 2 * PLAYER_SIZE, NES_SCREEN_HEIGHT - PLAYER_SIZE * 4, WORLD_WIDTH_NES - 2 * PLAYER_SIZE + PLAYER_SIZE // 2, NES_SCREEN_HEIGHT - PLAYER_SIZE), 'type': 'flagpole_base', 'collidable': True, 'sprite_data': FLAGPOLE_BASE_BLOCK_DATA},
            {'coords': (WORLD_WIDTH_NES - 2 * PLAYER_SIZE + PLAYER_SIZE // 4, NES_SCREEN_HEIGHT - PLAYER_SIZE * 12, WORLD_WIDTH_NES - 2 * PLAYER_SIZE + PLAYER_SIZE // 4 + PLAYER_SIZE // 8, NES_SCREEN_HEIGHT - PLAYER_SIZE * 4), 'type': 'flagpole_pole', 'collidable': False, 'sprite_data': FLAGPOLE_POLE_SPRITE_DATA},
        ]

        self.canvas_items_map = {}
        self.collidable_platform_coords = []
        self.draw_all_visual_blocks() # Initial draw of the world!

        self.pressed_keys = set()
        self.bind_keys() # Get those keybinds ready!
        self.game_loop() # START THE GAME!

    def draw_pixel_art(self, base_x_nes, base_y_nes, entity_width_nes, entity_height_nes, sprite_definition):
        pixel_art_rows = sprite_definition["pixels"]
        sprite_color_palette = {
            char_key: self.COLOR_MAP.get(mapped_color_key)
            for char_key, mapped_color_key in sprite_definition["colors"].items()
        }

        art_height_px_native = len(pixel_art_rows)
        art_width_px_native = len(pixel_art_rows[0]) if art_height_px_native > 0 else 0
        if art_width_px_native == 0: return [] # No pixels, no party!

        # Calculate the size of each individual "NES pixel" within the scaled entity.
        # This is the magic for pixel-perfect scaling!
        canvas_pixel_width_internal = entity_width_nes / art_width_px_native
        canvas_pixel_height_internal = entity_height_nes / art_height_px_native
        
        drawn_item_ids = []
        for r_idx, row_str in enumerate(pixel_art_rows):
            for c_idx, color_char_key in enumerate(row_str):
                actual_color_hex = sprite_color_palette.get(color_char_key)
                if actual_color_hex: 
                    # Calculate position in NES world coordinates (relative to entity's base_x_nes)
                    px_x1_nes = base_x_nes + (c_idx * canvas_pixel_width_internal)
                    py_y1_nes = base_y_nes + (r_idx * canvas_pixel_height_internal)
                    px_x2_nes = base_x_nes + ((c_idx + 1) * canvas_pixel_width_internal)
                    py_y2_nes = base_y_nes + ((r_idx + 1) * canvas_pixel_height_internal)
                    
                    # Convert NES world coordinates to actual canvas coordinates, applying camera offset and super scaling!
                    px_x1_canvas = (px_x1_nes - self.camera_x) * self.scale
                    py_y1_canvas = py_y1_nes * self.scale # Y-axis doesn't scroll, keeping it classic!
                    px_x2_canvas = (px_x2_nes - self.camera_x) * self.scale
                    py_y2_canvas = py_y2_nes * self.scale
                    
                    # Ensure minimum pixel size on canvas, no blurry lines!
                    if px_x2_canvas - px_x1_canvas < 1: px_x2_canvas = px_x1_canvas + 1
                    if py_y2_canvas - py_y1_canvas < 1: py_y2_canvas = py_y1_canvas + 1

                    pixel_id = self.canvas.create_rectangle(
                        px_x1_canvas, py_y1_canvas, px_x2_canvas, py_y2_canvas,
                        fill=actual_color_hex, outline="" 
                    )
                    drawn_item_ids.append(pixel_id)
        return drawn_item_ids

    def draw_all_visual_blocks(self):
        # Clear existing items like a BOSS!
        for key in list(self.canvas_items_map.keys()):
            items = self.canvas_items_map.pop(key)
            if isinstance(items, list):
                for item_id in items: self.canvas.delete(item_id)
            else:
                self.canvas.delete(items)
        self.collidable_platform_coords = [] # Clear and rebuild collision data!

        for i, block_data in enumerate(self.visual_blocks_data):
            coords_nes = block_data['coords'] # These are pure NES pixel coordinates!
            x1_nes, y1_nes, x2_nes, y2_nes = coords_nes
            block_width_nes = x2_nes - x1_nes
            block_height_nes = y2_nes - y1_nes
            block_type = block_data['type']
            sprite_data_for_block = block_data.get('sprite_data')
            
            current_block_pixel_ids = []

            if sprite_data_for_block:
                tile_unit_w_nes = PLAYER_SIZE # A "tile" is our glorious PLAYER_SIZE (16) NES pixels!
                tile_unit_h_nes = PLAYER_SIZE

                # How many tiles does this block represent in NES units? SO MANY TILES!
                num_tiles_x = max(1, int(round(block_width_nes / tile_unit_w_nes)))
                num_tiles_y = max(1, int(round(block_height_nes / tile_unit_h_nes)))
                
                # The actual dimensions that each individual tile drawing will take. It's like magic!
                tile_draw_width_nes = block_width_nes / num_tiles_x
                tile_draw_height_nes = block_height_nes / num_tiles_y

                for row in range(num_tiles_y):
                    for col in range(num_tiles_x):
                        tile_x_nes = x1_nes + (col * tile_draw_width_nes)
                        tile_y_nes = y1_nes + (row * tile_draw_height_nes)
                        # Draw individual tile, passing its position and size in NES units. BAM!
                        ids = self.draw_pixel_art(tile_x_nes, tile_y_nes, tile_draw_width_nes, tile_draw_height_nes, sprite_data_for_block)
                        current_block_pixel_ids.extend(ids)
            else:
                # Fallback for blocks without sprites, though there aren't many now!
                fallback_color_key = block_data.get('color_key')
                fallback_color = "purple" # Default if no key, a splash of color!
                if fallback_color_key and hasattr(self, fallback_color_key):
                    fallback_color = getattr(self, fallback_color_key)
                
                # Draw fallback rectangle on canvas, scaled and with camera offset! Pure power!
                rect_x1_canvas = (x1_nes - self.camera_x) * self.scale
                rect_y1_canvas = y1_nes * self.scale
                rect_x2_canvas = (x2_nes - self.camera_x) * self.scale
                rect_y2_canvas = y2_nes * self.scale

                item_id = self.canvas.create_rectangle(rect_x1_canvas, rect_y1_canvas, rect_x2_canvas, rect_y2_canvas, fill=fallback_color, outline="black")
                current_block_pixel_ids.append(item_id)

            self.canvas_items_map[f"{block_type}_{i}"] = current_block_pixel_ids

            if block_data.get('collidable', False):
                self.collidable_platform_coords.append(coords_nes) # Store in NES coords for perfect collisions!

    def update_player_visuals(self):
        for pixel_id in self.player_pixel_ids:
            self.canvas.delete(pixel_id)
        self.player_pixel_ids = [] 

        # Player drawing takes NES pixel coords, it's so natural!
        self.player_pixel_ids = self.draw_pixel_art(
            self.player_x, self.player_y,
            PLAYER_SIZE, PLAYER_SIZE, # Player is a perfect 16x16 NES pixels!
            SMALL_MARIO_STANDING_DATA 
        )

    def bind_keys(self):
        self.focus_set() # Get that focus, baby!
        self.bind("<KeyPress>", self.key_pressed)
        self.bind("<KeyRelease>", self.key_released)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        self.destroy() # Goodbye, cruel world!

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
            
        # Player bounds check in NES world coordinates - keep him in the level!
        if self.player_x < 0: self.player_x = 0
        if self.player_x + PLAYER_SIZE > WORLD_WIDTH_NES:
            self.player_x = WORLD_WIDTH_NES - PLAYER_SIZE

    def apply_gravity_and_movement(self):
        if not self.on_ground:
            self.player_vy += GRAVITY
        self.player_y += self.player_vy

        # Player bounding box in NES coordinates for absolutely perfect collisions!
        next_player_top = self.player_y
        next_player_bottom = self.player_y + PLAYER_SIZE
        next_player_left = self.player_x
        next_player_right = self.player_x + PLAYER_SIZE
        
        self.on_ground = False

        for p_coords_nes in self.collidable_platform_coords:
            plat_left_nes, plat_top_nes, plat_right_nes, plat_bottom_nes = p_coords_nes
            horizontal_overlap = (next_player_right > plat_left_nes and next_player_left < plat_right_nes)

            if horizontal_overlap:
                # Landing on top, sweet sweet landing!
                if self.player_vy >= 0 and next_player_bottom >= plat_top_nes and self.player_y < plat_top_nes: 
                    self.player_y = plat_top_nes - PLAYER_SIZE
                    self.player_vy = 0
                    self.on_ground = True
                    self.is_jumping = False
                    # Update player bounds after correction, so precise!
                    next_player_top = self.player_y 
                    next_player_bottom = self.player_y + PLAYER_SIZE
                # Hitting head from bottom, OUCH!
                elif self.player_vy < 0 and next_player_top <= plat_bottom_nes and next_player_bottom > plat_bottom_nes:
                    self.player_y = plat_bottom_nes
                    self.player_vy = 1 # Bounce off slightly, a classic!
                    # Update player bounds, so accurate!
                    next_player_top = self.player_y
                    next_player_bottom = self.player_y + PLAYER_SIZE
                # Basic side collision, no clipping through walls for THIS Mario!
                elif next_player_bottom > plat_top_nes and next_player_top < plat_bottom_nes: # Vertical overlap for side collision
                    # Collision from left side of platform
                    if next_player_right > plat_left_nes and self.player_x + PLAYER_SIZE <= plat_left_nes and self.player_vy == 0 : # Was to the left, now intersecting
                         self.player_x = plat_left_nes - PLAYER_SIZE
                         next_player_left = self.player_x
                         next_player_right = self.player_x + PLAYER_SIZE
                    # Collision from right side of platform
                    elif next_player_left < plat_right_nes and self.player_x >= plat_right_nes and self.player_vy == 0: # Was to the right, now intersecting
                         self.player_x = plat_right_nes
                         next_player_left = self.player_x
                         next_player_right = self.player_x + PLAYER_SIZE

        # Check for falling off screen (NES world Y-axis). Don't die, Mario!
        if not self.on_ground and self.player_y > NES_SCREEN_HEIGHT + PLAYER_SIZE * 2 : # A bit more leeway before reset, generous!
            print("Fell off! Oh noes! Resetting Mario, meow!")
            self.player_y = NES_SCREEN_HEIGHT - PLAYER_SIZE - 2 # Reset to initial ground position, fresh start!
            self.player_x = 50
            self.player_vy = 0
            self.on_ground = True 
            self.is_jumping = False
            
        # Update camera position to follow player, clamping to world bounds. SMOOTH SCROLLING!
        target_camera_x = self.player_x - NES_SCREEN_WIDTH / 2
        self.camera_x = max(0, min(target_camera_x, WORLD_WIDTH_NES - NES_SCREEN_WIDTH))
        # Round camera_x to avoid sub-pixel jitter, for that *true* NES feel!
        self.camera_x = round(self.camera_x)


    def game_loop(self):
        try:
            if not self.winfo_exists(): return # Stop if the window is gone, no errors here!
            start_time = time.perf_counter() # Measure that performance, baby!

            self.handle_input() # Process those button mashes!
            self.apply_gravity_and_movement() # Make Mario move and fall!
            # Redraw EVERYTHING! This is how we handle scrolling the background and player!
            self.draw_all_visual_blocks() # Redraw background (tiles) with camera offset, dynamic and lovely!
            self.update_player_visuals() # Redraw player with camera offset, always visible!

            end_time = time.perf_counter()
            process_time_ms = (end_time - start_time) * 1000
            delay_ms = max(1, DELAY - int(process_time_ms)) # Keep that FPS rock solid!

            self.after(delay_ms, self.game_loop) # Loop forever, just like a classic game!
        except tk.TclError:
            print("Game window closed gracefully, like a cat landing on its feet! Purrrr.")
        except Exception as e:
            print(f"Oopsie, a little furball in the game loop: {e}")
            import traceback
            traceback.print_exc() # More detailed error for debugging, nya!
            self.destroy() # Close the window on fatal error, no messy crashes!

class CATOS_GUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("CATOS - Meow Edition v3.0 NES Emu! THE ULTIMATE!") # Version up again! So many features!
        # Adjusted GUI size to account for new, glorious game window size!
        self.geometry("500x500") 
        self.configure(bg="#2c3e50") # Deep, dark background, so cool!

        title_label = tk.Label(self, text="Welcome to CATOS! MAX NES POWER!", font=("Arial", 28, "bold"), bg="#2c3e50", fg="white")
        title_label.pack(pady=30)

        cat_art_text = "  /\_/\ \n ( >w< )  < TRUE NES PIXELS!\n  > ^ < \nCATOS NES EVO++!"
        cat_label = tk.Label(self,text=cat_art_text,font=("Courier New", 14),bg="#2c3e50",fg="#ecf0f1",justify=tk.LEFT)
        cat_label.pack(pady=20)

        launch_button = tk.Button(
            self, text="Play NES-EMULATED Mario!", font=("Arial", 16),bg="#e74c3c", fg="white",
            activebackground="#c0392b",relief=tk.FLAT,padx=15,pady=10,command=self.launch_mario_game)
        launch_button.pack(pady=20)

        self.clock_label = tk.Label(self,text="",font=("Arial", 12),bg="#2c3e50",fg="#bdc3c7")
        self.clock_label.pack(side=tk.BOTTOM, pady=10)
        self.update_clock() # Keep that clock ticking!
        self.mario_game_window = None

    def update_clock(self):
        current_time = time.strftime("%H:%M:%S %p \n %A, %B %d, %Y")
        self.clock_label.config(text=current_time)
        self.after(1000, self.update_clock) # Update every second, so precise!

    def launch_mario_game(self):
        if self.mario_game_window is None or not self.mario_game_window.winfo_exists():
            self.mario_game_window = MarioGameWindow(self)
            self.mario_game_window.focus_set() # Ensure game window gets focus right away, no waiting!
        else:
            self.mario_game_window.lift() # Bring it to the front!
            self.mario_game_window.focus_set() # Focus again, always ready!

if __name__ == "__main__":
    app = CATOS_GUI()
    app.mainloop() # RUN IT! RUN IT ALL!
