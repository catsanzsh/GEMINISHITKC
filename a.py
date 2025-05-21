import tkinter as tk
import time

# --- Game Constants ---
PLAYER_SIZE = 30
PLAYER_COLOR = "red"
PLATFORM_COLOR = "green"
BACKGROUND_COLOR = "light blue"
GRAVITY = 1.5  # Increased gravity for more noticeable effect
JUMP_POWER = 20 # Increased jump power
MOVE_SPEED = 7
FPS = 60 # Target frames per second
DELAY = 1000 // FPS # Delay in milliseconds

class MarioGameWindow(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Mini Mario Game")
        self.geometry("800x600")
        self.resizable(False, False)
        self.configure(bg=BACKGROUND_COLOR)

        self.canvas = tk.Canvas(self, width=800, height=600, bg=BACKGROUND_COLOR, highlightthickness=0)
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
            fill=PLAYER_COLOR, outline="black"
        )

        # Platforms (x1, y1, x2, y2)
        self.platforms_coords = [
            (0, 550, 800, 600),    # Ground
            (150, 450, 300, 470),
            (350, 350, 500, 370),
            (50, 250, 200, 270),
            (550, 200, 700, 220), # Higher platform
            (300, 100, 450, 120)  # Highest platform for testing jumps
        ]
        self.platforms = []
        for p_coords in self.platforms_coords:
            platform = self.canvas.create_rectangle(p_coords, fill=PLATFORM_COLOR, outline="black")
            self.platforms.append(platform)

        # Controls
        self.pressed_keys = set()
        self.bind_keys()

        # Game loop
        self.game_loop()

    def bind_keys(self):
        self.focus_set() # Crucial for Toplevel to receive key events
        self.bind("<KeyPress>", self.key_pressed)
        self.bind("<KeyRelease>", self.key_released)
        # Special handling for closing the window
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        # If you need to stop the game loop or do cleanup
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
            
        # Keep player within canvas bounds (horizontally)
        if self.player_x < 0:
            self.player_x = 0
        if self.player_x + PLAYER_SIZE > self.canvas.winfo_width():
            self.player_x = self.canvas.winfo_width() - PLAYER_SIZE


    def apply_gravity_and_movement(self):
        # Apply gravity
        if not self.on_ground:
            self.player_vy += GRAVITY
        
        # Update player's vertical position
        self.player_y += self.player_vy

        # Tentative new position
        next_player_top = self.player_y
        next_player_bottom = self.player_y + PLAYER_SIZE
        next_player_left = self.player_x
        next_player_right = self.player_x + PLAYER_SIZE
        
        self.on_ground = False # Assume not on ground until collision check proves otherwise

        for p_coords in self.platforms_coords:
            plat_left, plat_top, plat_right, plat_bottom = p_coords

            # Check horizontal overlap for potential vertical collision
            horizontal_overlap = (next_player_right > plat_left and next_player_left < plat_right)

            if horizontal_overlap:
                # Collision from top (landing)
                # Player is moving down (or was above) and next bottom edge is inside or at platform top
                is_above_platform = (self.player_y + PLAYER_SIZE - self.player_vy <= plat_top) # Check previous position

                if self.player_vy >= 0 and next_player_bottom >= plat_top and next_player_top < plat_top:
                    self.player_y = plat_top - PLAYER_SIZE
                    self.player_vy = 0
                    self.on_ground = True
                    self.is_jumping = False
                    break # Landed on one platform

                # Collision from bottom (hitting head)
                # Player is moving up and next top edge is inside or at platform bottom
                if self.player_vy < 0 and next_player_top <= plat_bottom and next_player_bottom > plat_bottom:
                    self.player_y = plat_bottom
                    self.player_vy = 1 # Bounce off slightly or just stop
                    break
        
        # Horizontal collision (simplified: just stop)
        # This needs to be integrated carefully with vertical collision to avoid sticking
        # For simplicity, this part is often more complex and involves checking sides
        # For now, we'll let the boundary check in handle_input manage side limits mostly

        # If player falls off screen bottom, reset (or game over)
        if self.player_y + PLAYER_SIZE > self.canvas.winfo_height():
            # For now, just put player back on a default ground
            self.player_y = 500 - PLAYER_SIZE 
            self.player_x = 50
            self.player_vy = 0
            self.on_ground = True # Assume it landed on some invisible floor
            self.is_jumping = False

    def update_player_position(self):
        self.canvas.coords(self.player_rect, 
                           self.player_x, self.player_y, 
                           self.player_x + PLAYER_SIZE, self.player_y + PLAYER_SIZE)

    def game_loop(self):
        try:
            self.handle_input()
            self.apply_gravity_and_movement()
            self.update_player_position()
            self.after(DELAY, self.game_loop)
        except tk.TclError:
            # This can happen if the window is destroyed while an 'after' call is pending
            print("Game window closed.")

class CATOS_GUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("CATOS - Meow Edition")
        self.geometry("500x400")
        self.configure(bg="#2c3e50") # A nice dark blue

        # OS Title Label
        title_label = tk.Label(
            self, 
            text="Welcome to CATOS!", 
            font=("Arial", 28, "bold"), 
            bg="#2c3e50", 
            fg="white"
        )
        title_label.pack(pady=30)

        # Cat ASCII Art (or a simple message)
        cat_art_text = "  /\_/\ \n ( o.o )\n  > ^ < \nCATOS v0.1"
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
            text="Play Mini Mario Game", 
            font=("Arial", 16),
            bg="#e74c3c", # Reddish button
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
        current_time = time.strftime("%H:%M:%S %p \n %A, %B %d, %Y")
        self.clock_label.config(text=current_time)
        self.after(1000, self.update_clock) # Update every second

    def launch_mario_game(self):
        if self.mario_game_window is None or not self.mario_game_window.winfo_exists():
            self.mario_game_window = MarioGameWindow(self)
            self.mario_game_window.grab_set() # Make the game window modal (optional)
        else:
            self.mario_game_window.lift() # Bring to front if already open
            self.mario_game_window.focus_set()

if __name__ == "__main__":
    app = CATOS_GUI()
    app.mainloop()
