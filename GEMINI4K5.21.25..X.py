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
# Based on common SMB1 small Mario palette.
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
        "DLLLLLDDLLLLLDDD", # Adding some edge definition
        "DLLLLLDDLLLLLDDL",
        "DDDDDDDDDDDDDDDL",
        "DLDDLLLLLDDLLLLD", # Swapped order for variety
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
        "O": "NES_QUESTION_OUTLINE", # Outline/Darker Yellow
        "Y": "NES_QUESTION_BLOCK_COLOR", # Yellow main
        "Q": "NES_WHITE",             # Question mark itself (white or very light)
        "S": "NES_QUESTION_SHADOW",   # Shadow for rivet/detail
        "X": None,
    },
    "pixels": [ # A common style of SMB1 ? block
        "OSOOOOOOOOOOOOOS", # Rivet S
        "YOOOOOOOOOOOOOOY",
        "YOOYYYYYYYYYYOOY",
        "YOOYQQQQQYYYQYOY", # Q for Question Mark
        "YOOYQYYYQYYYQQOY",
        "YOOYQYYYQYYYQYOY",
        "YOOYQYYYQYYYQYOY",
        "YOOYQQQQQYYYQYOY",
        "YOOYYYYYYYYYYYOY",
        "YOOYYYQQQYYYYYOY", # Dot of ?
        "YOOYYYQQQYYYYYOY",
        "YOOYYYQQQYYYYYOY",
        "YOOYYYYYYYYYYYOY",
        "YOOOOOOOOOOOOOOY",
        "OSOOOOOOOOOOOOOS", # Rivet S
        "SSSSSSSSSSSSSSSS", # Bottom shadow/line
    ]
}

GROUND_BLOCK_DATA = {
    "colors": {
        "D": "NES_GROUND_DARK", # Darker Brown
        "L": "NES_GROUND_COLOR",# Lighter Brown
        "X": None,
    },
    "pixels": [ # Making it look a bit like SMB1 ground blocks (rounded tops)
        "LLLLDDDDDDLLLL",
        "LLDDLLLLDDLLLL",
        "LDDLLLLLLDDLLL",
        "LDDLLLLLLDDLLL",
        "LLDDLLLLDDLLLL",
        "LLLLDDDDDDLLLL",
        "LLLLLLLLLLLLLL", # Solid lines
        "LLLLLLLLLLLLLL",
        "DDDDDDDDDDDDDDDD", # Contrast for below
        "DDDDDDDDDDDDDDDD",
        "LLLLLLLLLLLLLL",
        "LLLLLLLLLLLLLL",
        "LLLLLLLLLLLLLL",
        "LLLLLLLLLLLLLL",
        "LLLLLLLLLLLLLL",
        "LLLLLLLLLLLLLL",
    ]
}

# --- End of Pixel Art Data ---

class MarioGameWindow(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Mini Mario Game - NES Pixels Purr-fected!")
        self.geometry("800x600")
        self.resizable(False, False)

        # --- Enhanced NES Color Palette, purrloined by HQRIPPER 7.1! ---
        self.NES_SKY_BLUE = "#5C94FC"
        self.NES_BRICK_COLOR = "#D07030"       # SMB1 Brick Orange
        self.NES_BRICK_DARK = "#A04000"        # Mortar for bricks
        self.NES_QUESTION_BLOCK_COLOR = "#FAC000" # SMB1 Question Block Yellow
        self.NES_QUESTION_OUTLINE = "#E4A000"  # Darker yellow/brown for ? outline
        self.NES_QUESTION_SHADOW = "#783000"   # Dark brown for ? block rivet/shadow
        self.NES_GROUND_COLOR = "#E09050"      # SMB1 Ground Tan
        self.NES_GROUND_DARK = "#A04000"       # Darker ground for contrast
        self.NES_PIPE_GREEN = "#30A020"
        self.MARIO_RED = "#FF0000"             # Classic Mario red (can be #B80000 for more NES feel)
        self.NES_SKIN_PEACH = "#FFB890"        # Mario's skin
        self.NES_DARK_BROWN = "#702800"        # Mario's hair/shoes
        self.FLAGPOLE_GRAY = "#808080"
        self.FLAGPOLE_DARK_GRAY = "#A9A9A9"
        self.NES_WHITE = "#FFFFFF"             # For ? mark details


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
            # Add any other mappings you need here!
        }

        # Player pixel art canvas items, meow!
        self.player_pixel_ids = []
        # Initial draw of player, so exciting!
        # self.update_player_visuals() # We'll call this in the game loop for the first time

        # --- Visual Blocks Data: AlphaEvolve's first masterpiece! ---
        self.visual_blocks_data = [
            {'coords': (0, 550, 800, 600), 'color_key': 'NES_GROUND_COLOR', 'type': 'ground', 'collidable': True, 'sprite_data': GROUND_BLOCK_DATA},
            {'coords': (150, 450, 150 + PLAYER_SIZE * 3, 450 + PLAYER_SIZE), 'color_key': 'NES_BRICK_COLOR', 'type': 'brick_platform', 'collidable': True, 'sprite_data': BRICK_BLOCK_DATA},
            {'coords': (200, 350, 200 + PLAYER_SIZE, 350 + PLAYER_SIZE), 'color_key': 'NES_QUESTION_BLOCK_COLOR', 'type': 'question_block', 'collidable': True, 'sprite_data': QUESTION_BLOCK_DATA},
            {'coords': (200 + PLAYER_SIZE + 5, 350, 200 + PLAYER_SIZE * 2 + 5, 350 + PLAYER_SIZE), 'color_key': 'NES_BRICK_COLOR', 'type': 'brick', 'collidable': True, 'sprite_data': BRICK_BLOCK_DATA},
            {'coords': (200 + PLAYER_SIZE*2 + 10, 350, 200 + PLAYER_SIZE*3 + 10, 350 + PLAYER_SIZE), 'color_key': 'NES_QUESTION_BLOCK_COLOR', 'type': 'question_block', 'collidable': True, 'sprite_data': QUESTION_BLOCK_DATA},
            {'coords': (350, 400, 350 + PLAYER_SIZE * 4, 400 + PLAYER_SIZE), 'color_key': 'NES_GROUND_COLOR', 'type': 'elevated_ground', 'collidable': True, 'sprite_data': GROUND_BLOCK_DATA},
            {'coords': (550, 550 - PLAYER_SIZE * 2, 550 + PLAYER_SIZE * 1.5, 550), 'color_key': 'NES_PIPE_GREEN', 'type': 'pipe_top', 'collidable': True}, # No sprite yet
            {'coords': (50, 250, 200, 270), 'color_key': 'NES_BRICK_COLOR', 'type': 'high_brick_platform', 'collidable': True, 'sprite_data': BRICK_BLOCK_DATA},
            {'coords': (300, 100, 450, 120), 'color_key': 'NES_GROUND_COLOR', 'type': 'summit_platform', 'collidable': True, 'sprite_data': GROUND_BLOCK_DATA},
            {'coords': (700, 550 - PLAYER_SIZE*3, 700 + PLAYER_SIZE*0.5, 550), 'color_key': 'FLAGPOLE_GRAY', 'type': 'flagpole_base', 'collidable': True}, # No sprite yet
            {'coords': (700 + (PLAYER_SIZE*0.5/2) - (PLAYER_SIZE*0.1/2), 200, 700 + (PLAYER_SIZE*0.5/2) + (PLAYER_SIZE*0.1/2), 550 - PLAYER_SIZE*3), 'color_key': 'FLAGPOLE_DARK_GRAY', 'type': 'flagpole_pole', 'collidable': False}, # No sprite yet
        ]

        self.canvas_items_map = {}
        self.collidable_platform_coords = []
        self.draw_all_visual_blocks() # New function to handle drawing, so tidy!

        self.pressed_keys = set()
        self.bind_keys()
        self.game_loop()

    def draw_pixel_art(self, base_x, base_y, entity_width, entity_height, sprite_definition):
        # sprite_definition = {"colors": {"KEY": "COLOR_MAP_KEY"}, "pixels": ["R...", "B..."]}
        pixel_art_rows = sprite_definition["pixels"]
        # Map conceptual colors (like 'R' for Mario's red) to actual hex colors via self.COLOR_MAP
        sprite_color_palette = {
            char_key: self.COLOR_MAP.get(mapped_color_key)
            for char_key, mapped_color_key in sprite_definition["colors"].items()
        }

        art_height_px_native = len(pixel_art_rows)
        art_width_px_native = len(pixel_art_rows[0]) if art_height_px_native > 0 else 0
        if art_width_px_native == 0: return [] # No pixels to draw, silly kitty!

        canvas_pixel_width = entity_width / art_width_px_native
        canvas_pixel_height = entity_height / art_height_px_native
        
        drawn_item_ids = []
        for r_idx, row_str in enumerate(pixel_art_rows):
            for c_idx, color_char_key in enumerate(row_str):
                actual_color_hex = sprite_color_palette.get(color_char_key)
                if actual_color_hex: # If not transparent (None) or key not found
                    px_x1 = base_x + (c_idx * canvas_pixel_width)
                    py_y1 = base_y + (r_idx * canvas_pixel_height)
                    px_x2 = base_x + ((c_idx + 1) * canvas_pixel_width)
                    py_y2 = base_y + ((r_idx + 1) * canvas_pixel_height)
                    
                    # Tiny adjustment for super small pixels to ensure they draw!
                    if px_x2 - px_x1 < 0.5: px_x2 = px_x1 + 0.5
                    if py_y2 - py_y1 < 0.5: py_y2 = py_y1 + 0.5

                    pixel_id = self.canvas.create_rectangle(
                        px_x1, py_y1, px_x2, py_y2,
                        fill=actual_color_hex, outline="" # No outlines for pixels for that smooth retro look!
                    )
                    drawn_item_ids.append(pixel_id)
        return drawn_item_ids

    def draw_all_visual_blocks(self):
        # Clear previous items if any (useful for dynamic levels later, maybe!)
        for key in list(self.canvas_items_map.keys()):
            items = self.canvas_items_map.pop(key)
            if isinstance(items, list):
                for item_id in items: self.canvas.delete(item_id)
            else:
                self.canvas.delete(items)
        self.collidable_platform_coords = [] # Reset collidable coords

        for i, block_data in enumerate(self.visual_blocks_data):
            coords = block_data['coords']
            x1, y1, x2, y2 = coords
            block_width = x2 - x1
            block_height = y2 - y1
            block_type = block_data['type']
            sprite_data_for_block = block_data.get('sprite_data')
            
            current_block_pixel_ids = []

            if sprite_data_for_block:
                # Tile the sprite if the block area is larger than PLAYER_SIZE (our assumed tile size)
                num_tiles_x = max(1, int(round(block_width / PLAYER_SIZE)))
                num_tiles_y = max(1, int(round(block_height / PLAYER_SIZE)))
                
                tile_draw_width = block_width / num_tiles_x
                tile_draw_height = block_height / num_tiles_y

                for row in range(num_tiles_y):
                    for col in range(num_tiles_x):
                        tile_x = x1 + (col * tile_draw_width)
                        tile_y = y1 + (row * tile_draw_height)
                        ids = self.draw_pixel_art(tile_x, tile_y, tile_draw_width, tile_draw_height, sprite_data_for_block)
                        current_block_pixel_ids.extend(ids)
            else:
                # Fallback for blocks without sprites (like pipes, flagpole for now)
                fallback_color = getattr(self, block_data['color_key'], "purple") # Default to purple if key fails
                item_id = self.canvas.create_rectangle(coords, fill=fallback_color, outline="black")
                current_block_pixel_ids.append(item_id)

            self.canvas_items_map[f"{block_type}_{i}"] = current_block_pixel_ids

            if block_data.get('collidable', False):
                self.collidable_platform_coords.append(coords)

    def update_player_visuals(self):
        # Delete old player pixels, like a cat shedding fur!
        for pixel_id in self.player_pixel_ids:
            self.canvas.delete(pixel_id)
        self.player_pixel_ids = [] # Empty the list, all fresh!

        # Draw new player pixels, purrfect!
        self.player_pixel_ids = self.draw_pixel_art(
            self.player_x, self.player_y,
            PLAYER_SIZE, PLAYER_SIZE,
            SMALL_MARIO_STANDING_DATA # Our cute Mario sprite!
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
                if self.player_vy >= 0 and next_player_bottom >= plat_top and next_player_top < plat_top:
                    self.player_y = plat_top - PLAYER_SIZE
                    self.player_vy = 0
                    self.on_ground = True
                    self.is_jumping = False
                    break 
                # Hitting head from bottom
                if self.player_vy < 0 and next_player_top <= plat_bottom and next_player_bottom > plat_bottom:
                    self.player_y = plat_bottom
                    self.player_vy = 1 
                    break 
        
        if self.player_y + PLAYER_SIZE > self.canvas.winfo_height() + PLAYER_SIZE*2:
            self.player_y = 500 - PLAYER_SIZE 
            self.player_x = 50
            self.player_vy = 0
            self.on_ground = True
            self.is_jumping = False

    # Removed update_player_position, visuals are now handled by update_player_visuals

    def game_loop(self):
        try:
            if not self.winfo_exists(): return
            start_time = time.perf_counter() # Meow, for smooth FPS!

            self.handle_input()
            self.apply_gravity_and_movement()
            self.update_player_visuals() # This now handles drawing Mario! So neat!

            end_time = time.perf_counter()
            process_time_ms = (end_time - start_time) * 1000
            delay_ms = max(1, DELAY - int(process_time_ms)) # Ensure positive delay

            self.after(delay_ms, self.game_loop)
        except tk.TclError:
            print("Game window closed gracefully, like a cat landing on its feet! Purrrr.")
        except Exception as e:
            print(f"Oopsie, a little furball in the game loop: {e}")
            self.destroy() # Close on error to prevent badness

class CATOS_GUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("CATOS - Meow Edition v2.1 Pixel Purrfect!") # Version up!
        self.geometry("500x400")
        self.configure(bg="#2c3e50")

        title_label = tk.Label(self, text="Welcome to CATOS! NES POWER!", font=("Arial", 28, "bold"), bg="#2c3e50", fg="white")
        title_label.pack(pady=30)

        cat_art_text = "  /\_/\ \n ( o.o )  < PIXELS!\n  > ^ < \nCATOS NES EVO!"
        cat_label = tk.Label(self,text=cat_art_text,font=("Courier New", 14),bg="#2c3e50",fg="#ecf0f1",justify=tk.LEFT)
        cat_label.pack(pady=20)

        launch_button = tk.Button(
            self, text="Play Pixel-Perfect Mario!", font=("Arial", 16),bg="#e74c3c", fg="white",
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
        else:
            self.mario_game_window.lift()
            self.mario_game_window.focus_set()

if __name__ == "__main__":
    app = CATOS_GUI()
    app.mainloop()
