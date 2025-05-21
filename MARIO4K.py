import tkinter as tk
import time

# --- Game Constants ---
PLAYER_SIZE = 30 # This will be the size of our drawn entities (Mario, blocks)
# PLAYER_COLOR is now handled by pixel art! So fancy!
# PLATFORM_COLOR is now block-specific pixel art! Wow!
# BACKGROUND_COLOR is set in class, NES sky blue! Whee!
GRAVITY = 1.5
JUMP_POWER = 20
MOVE_SPEED = 7
FPS = 60
DELAY = 1000 // FPS

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
    ]
}


# --- End of Pixel Art Data ---

class MarioGameWindow(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Mini Mario Game - NES Pixels Purr-fected++!")
        self.geometry("800x600")
        self.resizable(False, False)

        # --- Enhanced NES Color Palette, purrloined by HQRIPPER 7.1! ---
        self.NES_SKY_BLUE = "#5C94FC"
        self.NES_BRICK_COLOR = "#D07030"
        self.NES_BRICK_DARK = "#A04000"
        self.NES_QUESTION_BLOCK_COLOR = "#FAC000"
        self.NES_QUESTION_OUTLINE = "#E4A000"
        self.NES_QUESTION_SHADOW = "#783000"
        self.NES_GROUND_COLOR = "#E09050"
        self.NES_GROUND_DARK = "#A04000"
        
        # Enhanced and New Colors! So vibrant!
        self.MARIO_RED = "#D03030"             # A more authentic NES Mario Red-Orange
        self.NES_SKIN_PEACH = "#FCB8A0"        # Slightly adjusted NES skin tone
        self.NES_DARK_BROWN = "#782818"        # More reddish-brown for hair/shoes
        self.NES_PIPE_GREEN = "#30A020"        # Main pipe color
        self.NES_PIPE_GREEN_LIGHT = "#80D010"  # Lighter green for pipe highlights/rim
        self.NES_PIPE_GREEN_DARK = "#207818"   # Darker green for pipe shadows
        self.FLAGPOLE_GRAY = "#B0B0B0"         # Lighter gray for flagpole
        self.FLAGPOLE_DARK_GRAY = "#707070"    # Darker gray for flagpole shading
        self.NES_WHITE = "#FCFCFC"             # NES White (slightly off-white for less harshness)
        self.NES_BLACK = "#000000"             # Pure black for strong contrast


        self.configure(bg=self.NES_SKY_BLUE)

        self.canvas = tk.Canvas(self, width=800, height=600, bg=self.NES_SKY_BLUE, highlightthickness=0)
        self.canvas.pack()

        # Player attributes
        self.player_x = 50
        self.player_y = 500 - PLAYER_SIZE
        self.player_vy = 0
        self.is_jumping = False
        self.on_ground = False

        # This dictionary maps color keys from sprite data to actual color values
        # It's super useful for our draw_pixel_art function!
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
            # NEW MAPPINGS FOR ENHANCED SPRITES! YAY!
            "NES_PIPE_GREEN": self.NES_PIPE_GREEN,
            "NES_PIPE_GREEN_LIGHT": self.NES_PIPE_GREEN_LIGHT,
            "NES_PIPE_GREEN_DARK": self.NES_PIPE_GREEN_DARK,
            "NES_BLACK": self.NES_BLACK,
            "FLAGPOLE_GRAY": self.FLAGPOLE_GRAY,
            "FLAGPOLE_DARK_GRAY": self.FLAGPOLE_DARK_GRAY,
        }

        self.player_pixel_ids = []

        # --- Visual Blocks Data: Now with more pixel purr-fection! ---
        self.visual_blocks_data = [
            {'coords': (0, 550, 800, 600), 'type': 'ground', 'collidable': True, 'sprite_data': GROUND_BLOCK_DATA},
            {'coords': (150, 450, 150 + PLAYER_SIZE * 3, 450 + PLAYER_SIZE), 'type': 'brick_platform', 'collidable': True, 'sprite_data': BRICK_BLOCK_DATA},
            {'coords': (200, 350, 200 + PLAYER_SIZE, 350 + PLAYER_SIZE), 'type': 'question_block', 'collidable': True, 'sprite_data': QUESTION_BLOCK_DATA},
            {'coords': (200 + PLAYER_SIZE + 5, 350, 200 + PLAYER_SIZE * 2 + 5, 350 + PLAYER_SIZE), 'type': 'brick', 'collidable': True, 'sprite_data': BRICK_BLOCK_DATA},
            {'coords': (200 + PLAYER_SIZE*2 + 10, 350, 200 + PLAYER_SIZE*3 + 10, 350 + PLAYER_SIZE), 'type': 'question_block', 'collidable': True, 'sprite_data': QUESTION_BLOCK_DATA},
            {'coords': (350, 400, 350 + PLAYER_SIZE * 4, 400 + PLAYER_SIZE), 'type': 'elevated_ground', 'collidable': True, 'sprite_data': GROUND_BLOCK_DATA},
            
            # Pipe with new sprite! So cool!
            {'coords': (550, 550 - PLAYER_SIZE * 2, 550 + PLAYER_SIZE * 1.5, 550), 'type': 'pipe_top', 'collidable': True, 'sprite_data': PIPE_TOP_DATA}, 
            
            {'coords': (50, 250, 200, 270), 'type': 'high_brick_platform', 'collidable': True, 'sprite_data': BRICK_BLOCK_DATA},
            {'coords': (300, 100, 450, 120), 'type': 'summit_platform', 'collidable': True, 'sprite_data': GROUND_BLOCK_DATA},
            
            # Flagpole parts with new sprites! Almost there!
            {'coords': (700, 550 - PLAYER_SIZE*3, 700 + PLAYER_SIZE*0.5, 550), 'type': 'flagpole_base', 'collidable': True, 'sprite_data': FLAGPOLE_BASE_BLOCK_DATA},
            {'coords': (700 + (PLAYER_SIZE*0.5/2) - (PLAYER_SIZE*0.1/2), 200, 700 + (PLAYER_SIZE*0.5/2) + (PLAYER_SIZE*0.1/2), 550 - PLAYER_SIZE*3), 'type': 'flagpole_pole', 'collidable': False, 'sprite_data': FLAGPOLE_POLE_SPRITE_DATA},
            # You could add a flagpole ball on top here too! Just a thought, teehee!
        ]

        self.canvas_items_map = {}
        self.collidable_platform_coords = []
        self.draw_all_visual_blocks() 

        self.pressed_keys = set()
        self.bind_keys()
        self.game_loop()

    def draw_pixel_art(self, base_x, base_y, entity_width, entity_height, sprite_definition):
        pixel_art_rows = sprite_definition["pixels"]
        sprite_color_palette = {
            char_key: self.COLOR_MAP.get(mapped_color_key)
            for char_key, mapped_color_key in sprite_definition["colors"].items()
        }

        art_height_px_native = len(pixel_art_rows)
        art_width_px_native = len(pixel_art_rows[0]) if art_height_px_native > 0 else 0
        if art_width_px_native == 0: return [] 

        canvas_pixel_width = entity_width / art_width_px_native
        canvas_pixel_height = entity_height / art_height_px_native
        
        drawn_item_ids = []
        for r_idx, row_str in enumerate(pixel_art_rows):
            for c_idx, color_char_key in enumerate(row_str):
                actual_color_hex = sprite_color_palette.get(color_char_key)
                if actual_color_hex: 
                    px_x1 = base_x + (c_idx * canvas_pixel_width)
                    py_y1 = base_y + (r_idx * canvas_pixel_height)
                    px_x2 = base_x + ((c_idx + 1) * canvas_pixel_width)
                    py_y2 = base_y + ((r_idx + 1) * canvas_pixel_height)
                    
                    if px_x2 - px_x1 < 0.5: px_x2 = px_x1 + 0.5
                    if py_y2 - py_y1 < 0.5: py_y2 = py_y1 + 0.5

                    pixel_id = self.canvas.create_rectangle(
                        px_x1, py_y1, px_x2, py_y2,
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
            coords = block_data['coords']
            x1, y1, x2, y2 = coords
            block_width = x2 - x1
            block_height = y2 - y1
            block_type = block_data['type']
            sprite_data_for_block = block_data.get('sprite_data')
            
            current_block_pixel_ids = []

            if sprite_data_for_block:
                # Tiling logic refined for non-square sprites too, purrfect!
                # Native dimensions of the sprite art itself
                native_art_height = len(sprite_data_for_block["pixels"])
                native_art_width = len(sprite_data_for_block["pixels"][0]) if native_art_height > 0 else 1

                # How many times would the NATIVE sprite art fit into the block?
                # For tiling, we'd usually tile based on PLAYER_SIZE or a fixed tile dimension.
                # Here, we scale the sprite to fit the block if it's not meant to be tiled,
                # or tile it if the block is much larger than a typical tile (PLAYER_SIZE).
                
                # Simplified: if block is much larger than player_size, tile. Otherwise, scale sprite to block.
                # This is a bit of a heuristic. A more robust system might specify tile size per sprite.
                tile_unit_w = PLAYER_SIZE 
                tile_unit_h = PLAYER_SIZE

                if block_width > tile_unit_w * 1.1 or block_height > tile_unit_h * 1.1: # Heuristic for tiling
                    num_tiles_x = max(1, int(round(block_width / tile_unit_w)))
                    num_tiles_y = max(1, int(round(block_height / tile_unit_h)))
                else: # Scale single sprite to fit
                    num_tiles_x = 1
                    num_tiles_y = 1
                
                tile_draw_width = block_width / num_tiles_x
                tile_draw_height = block_height / num_tiles_y

                for row in range(num_tiles_y):
                    for col in range(num_tiles_x):
                        tile_x = x1 + (col * tile_draw_width)
                        tile_y = y1 + (row * tile_draw_height)
                        ids = self.draw_pixel_art(tile_x, tile_y, tile_draw_width, tile_draw_height, sprite_data_for_block)
                        current_block_pixel_ids.extend(ids)
            else:
                # Fallback for blocks without sprites (should be fewer now!)
                fallback_color_key = block_data.get('color_key')
                fallback_color = "purple" # Default if no key
                if fallback_color_key and hasattr(self, fallback_color_key):
                    fallback_color = getattr(self, fallback_color_key)
                item_id = self.canvas.create_rectangle(coords, fill=fallback_color, outline="black")
                current_block_pixel_ids.append(item_id)

            self.canvas_items_map[f"{block_type}_{i}"] = current_block_pixel_ids

            if block_data.get('collidable', False):
                self.collidable_platform_coords.append(coords)

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
        if self.player_x + PLAYER_SIZE > self.canvas.winfo_width():
            self.player_x = self.canvas.winfo_width() - PLAYER_SIZE

    def apply_gravity_and_movement(self):
        if not self.on_ground:
            self.player_vy += GRAVITY
        self.player_y += self.player_vy

        next_player_top = self.player_y
        next_player_bottom = self.player_y + PLAYER_SIZE
        next_player_left = self.player_x
        next_player_right = self.player_x + PLAYER_SIZE
        
        self.on_ground = False

        for p_coords in self.collidable_platform_coords:
            plat_left, plat_top, plat_right, plat_bottom = p_coords
            horizontal_overlap = (next_player_right > plat_left and next_player_left < plat_right)

            if horizontal_overlap:
                # Landing on top
                if self.player_vy >= 0 and next_player_bottom >= plat_top and self.player_y < plat_top: # check self.player_y was above plat_top before movement
                    self.player_y = plat_top - PLAYER_SIZE
                    self.player_vy = 0
                    self.on_ground = True
                    self.is_jumping = False
                    # Update next positions after correction
                    next_player_top = self.player_y 
                    next_player_bottom = self.player_y + PLAYER_SIZE
                    # No break here, check other collisions like side/head too if needed in complex scenarios
                # Hitting head from bottom
                elif self.player_vy < 0 and next_player_top <= plat_bottom and next_player_bottom > plat_bottom:
                    self.player_y = plat_bottom
                    self.player_vy = 1 
                    # Update next positions
                    next_player_top = self.player_y
                    next_player_bottom = self.player_y + PLAYER_SIZE
                # Basic side collision (can be improved)
                # Check if player was previously outside horizontally but now inside
                # And is vertically overlapping
                elif next_player_bottom > plat_top and next_player_top < plat_bottom: # Vertical overlap for side collision
                    # Collision from left side of platform
                    if next_player_right > plat_left and self.player_x + PLAYER_SIZE <= plat_left and self.player_vy == 0 : # Was to the left, now intersecting
                         self.player_x = plat_left - PLAYER_SIZE
                         next_player_left = self.player_x
                         next_player_right = self.player_x + PLAYER_SIZE
                    # Collision from right side of platform
                    elif next_player_left < plat_right and self.player_x >= plat_right and self.player_vy == 0: # Was to the right, now intersecting
                         self.player_x = plat_right
                         next_player_left = self.player_x
                         next_player_right = self.player_x + PLAYER_SIZE


        # Check for falling off screen after all platform checks
        if not self.on_ground and self.player_y + PLAYER_SIZE > self.canvas.winfo_height() + PLAYER_SIZE*2 : # A bit more leeway before reset
            print("Fell off! Oh noes! Resetting Mario, meow!")
            self.player_y = 500 - PLAYER_SIZE 
            self.player_x = 50
            self.player_vy = 0
            self.on_ground = True 
            self.is_jumping = False


    def game_loop(self):
        try:
            if not self.winfo_exists(): return
            start_time = time.perf_counter() 

            self.handle_input()
            self.apply_gravity_and_movement()
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
            traceback.print_exc() # More detailed error for debugging, nya!
            self.destroy() 

class CATOS_GUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("CATOS - Meow Edition v2.2 Pixel Purr-fection Enhanced!") # Version up!
        self.geometry("500x400")
        self.configure(bg="#2c3e50")

        title_label = tk.Label(self, text="Welcome to CATOS! MAX NES POWER!", font=("Arial", 28, "bold"), bg="#2c3e50", fg="white")
        title_label.pack(pady=30)

        cat_art_text = "  /\_/\ \n ( >w< )  < MORE PIXELS!\n  > ^ < \nCATOS NES EVO++!"
        cat_label = tk.Label(self,text=cat_art_text,font=("Courier New", 14),bg="#2c3e50",fg="#ecf0f1",justify=tk.LEFT)
        cat_label.pack(pady=20)

        launch_button = tk.Button(
            self, text="Play ENHANCED Pixel Mario!", font=("Arial", 16),bg="#e74c3c", fg="white",
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
            self.mario_game_window.focus_set() # Ensure game window gets focus right away!
        else:
            self.mario_game_window.lift()
            self.mario_game_window.focus_set()

if __name__ == "__main__":
    app = CATOS_GUI()
    app.mainloop()
