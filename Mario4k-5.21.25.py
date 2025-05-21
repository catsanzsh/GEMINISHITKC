import tkinter as tk
import time

# --- Game Constants ---
PLAYER_SIZE = 30
# PLAYER_COLOR is set in class, Mario's classic red!
# PLATFORM_COLOR is now block-specific! So exciting!
# BACKGROUND_COLOR is set in class, NES sky blue! Whee!
GRAVITY = 1.5  # Increased gravity for more noticeable effect
JUMP_POWER = 20 # Increased jump power
MOVE_SPEED = 7
FPS = 60 # Target frames per second
DELAY = 1000 // FPS # Delay in milliseconds

class MarioGameWindow(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Mini Mario Game - NES Evolution Stage 1!")
        self.geometry("800x600")
        self.resizable(False, False)

        # --- NES-ish Colors, purrloined by HQRIPPER 7.1! ---
        self.NES_SKY_BLUE = "#5C94FC" # A common SMB sky blue, so pretty!
        self.NES_BRICK_COLOR = "#D07030" # Orangey-brown for bricks, yummy!
        self.NES_QUESTION_BLOCK_COLOR = "#FAC000" # Golden yellow for ? blocks, shiny!
        self.NES_GROUND_COLOR = "#E09050" # A lighter brown/tan for ground, so earthy!
        self.NES_PIPE_GREEN = "#30A020" # Green for pipes, let's-a-go!
        self.MARIO_RED = "#FF0000" # Classic Mario red, meow!
        self.FLAGPOLE_GRAY = "#808080" # Gray for the flagpole, almost there!
        self.FLAGPOLE_DARK_GRAY = "#A9A9A9" # Darker gray for accents, so stylish!


        self.configure(bg=self.NES_SKY_BLUE) # Set the background color here, meow!

        self.canvas = tk.Canvas(self, width=800, height=600, bg=self.NES_SKY_BLUE, highlightthickness=0)
        self.canvas.pack()

        # Player attributes
        self.player_x = 50
        self.player_y = 500 - PLAYER_SIZE
        self.player_vy = 0  # Vertical velocity
        self.is_jumping = False
        self.on_ground = False

        self.player_rect = self.canvas.create_rectangle(
            self.player_x, self.player_y,
            self.player_x + PLAYER_SIZE, self.player_y + PLAYER_SIZE,
            fill=self.MARIO_RED, outline="black" # Using Mario's iconic red!
        )

        # --- Visual Blocks Data: AlphaEvolve's first masterpiece! ---
        # Defines all visual elements and their properties. So organized, wow!
        self.visual_blocks_data = [
            # Ground layer, super solid!
            {'coords': (0, 550, 800, 600), 'color': self.NES_GROUND_COLOR, 'type': 'ground', 'collidable': True},
            # Some brick platforms, so classic!
            {'coords': (150, 450, 150 + PLAYER_SIZE * 3, 450 + PLAYER_SIZE), 'color': self.NES_BRICK_COLOR, 'type': 'brick_platform', 'collidable': True},
            # A question block! What could be inside? Magic!
            {'coords': (200, 350, 200 + PLAYER_SIZE, 350 + PLAYER_SIZE), 'color': self.NES_QUESTION_BLOCK_COLOR, 'type': 'question_block', 'collidable': True},
            # Another brick, just because bricks are cool!
            {'coords': (200 + PLAYER_SIZE + 5, 350, 200 + PLAYER_SIZE * 2 + 5, 350 + PLAYER_SIZE), 'color': self.NES_BRICK_COLOR, 'type': 'brick', 'collidable': True},
            # Another Question Block, double the fun!
            {'coords': (200 + PLAYER_SIZE*2 + 10, 350, 200 + PLAYER_SIZE*3 + 10, 350 + PLAYER_SIZE), 'color': self.NES_QUESTION_BLOCK_COLOR, 'type': 'question_block', 'collidable': True},
            # Elevated ground section, for daring jumps!
            {'coords': (350, 400, 350 + PLAYER_SIZE * 4, 400 + PLAYER_SIZE), 'color': self.NES_GROUND_COLOR, 'type': 'elevated_ground', 'collidable': True},
            # A cute little pipe! Maybe a Piranha Plant will live here later, teehee!
            {'coords': (550, 550 - PLAYER_SIZE * 2, 550 + PLAYER_SIZE * 1.5, 550), 'color': self.NES_PIPE_GREEN, 'type': 'pipe_top', 'collidable': True}, # Top part of pipe (collidable)
            # Higher platform for tricky jumps!
            {'coords': (50, 250, 200, 270), 'color': self.NES_BRICK_COLOR, 'type': 'high_brick_platform', 'collidable': True},
             # Highest platform to test those super jumps! Reach for the stars!
            {'coords': (300, 100, 450, 120), 'color': self.NES_GROUND_COLOR, 'type': 'summit_platform', 'collidable': True},
            # Flagpole base - YOU'RE A WINNER! (soon!)
            {'coords': (700, 550 - PLAYER_SIZE*3, 700 + PLAYER_SIZE*0.5, 550), 'color': self.FLAGPOLE_GRAY, 'type': 'flagpole_base', 'collidable': True},
            # The flagpole itself! (Visual only for now, teehee!)
            {'coords': (700 + (PLAYER_SIZE*0.5/2) - (PLAYER_SIZE*0.1/2), 200, 700 + (PLAYER_SIZE*0.5/2) + (PLAYER_SIZE*0.1/2), 550 - PLAYER_SIZE*3), 'color': self.FLAGPOLE_DARK_GRAY, 'type': 'flagpole_pole', 'collidable': False},
        ]

        self.canvas_items_map = {} # Stores canvas item IDs if we need to change them later! So clever!
        self.collidable_platform_coords = [] # For the physics engine, only the solid stuff!

        for i, block_data in enumerate(self.visual_blocks_data):
            coords = block_data['coords']
            color = block_data['color']
            block_type = block_data['type']
            item_id = self.canvas.create_rectangle(coords, fill=color, outline="black")
            self.canvas_items_map[f"{block_type}_{i}"] = item_id # Store it with a unique key!

            if block_data.get('collidable', False): # Only add if collidable is true! Safety first, meow!
                self.collidable_platform_coords.append(coords)

        # Controls, gotta go fast!
        self.pressed_keys = set()
        self.bind_keys()

        # Game loop, the heart of the fun!
        self.game_loop()

    def bind_keys(self):
        self.focus_set() # Crucial for Toplevel to receive key events, don't forget this little kitty!
        self.bind("<KeyPress>", self.key_pressed)
        self.bind("<KeyRelease>", self.key_released)
        self.protocol("WM_DELETE_WINDOW", self.on_closing) # Bye-bye window!

    def on_closing(self):
        # If you need to stop the game loop or do cleanup, like giving the cat a treat!
        self.destroy()


    def key_pressed(self, event):
        self.pressed_keys.add(event.keysym.lower()) # Add ALL THE KEYS!

    def key_released(self, event):
        if event.keysym.lower() in self.pressed_keys:
            self.pressed_keys.remove(event.keysym.lower()) # Okay, maybe not ALL the keys forever.

    def handle_input(self):
        if 'a' in self.pressed_keys or 'left' in self.pressed_keys:
            self.player_x -= MOVE_SPEED # Zoom left!
        if 'd' in self.pressed_keys or 'right' in self.pressed_keys:
            self.player_x += MOVE_SPEED # Zoom right!
        if ('w' in self.pressed_keys or 'up' in self.pressed_keys or 'space' in self.pressed_keys) and self.on_ground:
            self.player_vy = -JUMP_POWER # JUMP FOR JOY! BOING!
            self.is_jumping = True
            self.on_ground = False # We have lift off, Houston!
            
        # Keep player within canvas bounds (horizontally), no escaping this fun dimension!
        if self.player_x < 0:
            self.player_x = 0
        if self.player_x + PLAYER_SIZE > self.canvas.winfo_width():
            self.player_x = self.canvas.winfo_width() - PLAYER_SIZE


    def apply_gravity_and_movement(self):
        # Apply gravity, what goes up must come down, meow!
        if not self.on_ground:
            self.player_vy += GRAVITY
        
        # Update player's vertical position
        self.player_y += self.player_vy

        # Tentative new position, let's see where we're going!
        next_player_top = self.player_y
        next_player_bottom = self.player_y + PLAYER_SIZE
        next_player_left = self.player_x
        next_player_right = self.player_x + PLAYER_SIZE
        
        self.on_ground = False # Assume not on ground until collision check proves otherwise, innocent until proven guilty!

        for p_coords in self.collidable_platform_coords: # Use the collidable coords list now, smart kitty!
            plat_left, plat_top, plat_right, plat_bottom = p_coords

            # Check horizontal overlap for potential vertical collision, very technical!
            horizontal_overlap = (next_player_right > plat_left and next_player_left < plat_right)

            if horizontal_overlap:
                # Collision from top (landing), thud!
                # Player is moving down (or was above) and next bottom edge is inside or at platform top
                # is_above_platform = (self.player_y + PLAYER_SIZE - self.player_vy <= plat_top) # Check previous position

                if self.player_vy >= 0 and next_player_bottom >= plat_top and next_player_top < plat_top:
                    self.player_y = plat_top - PLAYER_SIZE
                    self.player_vy = 0
                    self.on_ground = True # Safe landing! Pat pat!
                    self.is_jumping = False
                    break # Landed on one platform, no need to check others! Efficiency!

                # Collision from bottom (hitting head), ouchie! Bonk!
                # Player is moving up and next top edge is inside or at platform bottom
                if self.player_vy < 0 and next_player_top <= plat_bottom and next_player_bottom > plat_bottom:
                    self.player_y = plat_bottom
                    self.player_vy = 1 # Bounce off slightly or just stop, like a confused kitten.
                    break # Bonked your head, silly!
        
        # If player falls off screen bottom, reset (or game over), whoopsie!
        if self.player_y + PLAYER_SIZE > self.canvas.winfo_height() + PLAYER_SIZE*2: # Give a little leeway
            # For now, just put player back on a default ground, try again!
            self.player_y = 500 - PLAYER_SIZE 
            self.player_x = 50 # Back to the start, little one!
            self.player_vy = 0
            self.on_ground = True # Assume it landed on some invisible fluffy cloud!
            self.is_jumping = False

    def update_player_position(self):
        self.canvas.coords(self.player_rect, 
                           self.player_x, self.player_y, 
                           self.player_x + PLAYER_SIZE, self.player_y + PLAYER_SIZE) # Lookin' good, Mario!

    def game_loop(self):
        try:
            if not self.winfo_exists(): # If window is gone, stop the loop, good kitty.
                return
            self.handle_input()
            self.apply_gravity_and_movement()
            self.update_player_position()
            self.after(DELAY, self.game_loop) # Again! Again! This is so much fun!
        except tk.TclError:
            # This can happen if the window is destroyed while an 'after' call is pending
            print("Game window closed gracefully, like a cat landing on its feet! Purrrr.")

class CATOS_GUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("CATOS - Meow Edition v2.0!") # Upgraded!
        self.geometry("500x400")
        self.configure(bg="#2c3e50") # A nice dark blue, so mysterious!

        # OS Title Label
        title_label = tk.Label(
            self, 
            text="Welcome to CATOS! NES POWER!", 
            font=("Arial", 28, "bold"), 
            bg="#2c3e50", 
            fg="white"
        )
        title_label.pack(pady=30)

        # Cat ASCII Art (or a simple message)
        cat_art_text = "  /\_/\ \n ( o.o )  < MEOW!\n  > ^ < \nCATOS NES EV0!" # EVOLUTION!
        cat_label = tk.Label(
            self,
            text=cat_art_text,
            font=("Courier New", 14),
            bg="#2c3e50",
            fg="#ecf0f1", # Light gray
            justify=tk.LEFT
        )
        cat_label.pack(pady=20)

        # Button to launch Mario Game
        launch_button = tk.Button(
            self, 
            text="Play Evolved Mini Mario!", 
            font=("Arial", 16),
            bg="#e74c3c", # Reddish button, so inviting!
            fg="white",
            activebackground="#c0392b",
            relief=tk.FLAT,
            padx=15,
            pady=10,
            command=self.launch_mario_game
        )
        launch_button.pack(pady=20)

        # Simple Clock
        self.clock_label = tk.Label(
            self,
            text="",
            font=("Arial", 12),
            bg="#2c3e50",
            fg="#bdc3c7" # Lighter gray for clock
        )
        self.clock_label.pack(side=tk.BOTTOM, pady=10)
        self.update_clock()

        self.mario_game_window = None

    def update_clock(self):
        current_time = time.strftime("%H:%M:%S %p \n %A, %B %d, %Y") # Time flies when you're having fun!
        self.clock_label.config(text=current_time)
        self.after(1000, self.update_clock) # Update every second, tick tock!

    def launch_mario_game(self):
        if self.mario_game_window is None or not self.mario_game_window.winfo_exists():
            self.mario_game_window = MarioGameWindow(self) # Let the games begin!
            # self.mario_game_window.grab_set() # Make the game window modal (optional, but focuses attention!)
        else:
            self.mario_game_window.lift() # Bring to front if already open, peek-a-boo!
            self.mario_game_window.focus_set() # Focus!

if __name__ == "__main__":
    app = CATOS_GUI()
    app.mainloop()
