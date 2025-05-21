import tkinter as tk
import time
import threading # For sound playback

# Attempt to import sound libraries
SOUND_ENABLED = False
try:
    import numpy as np
    import simpleaudio as sa
    SOUND_ENABLED = True
    print("Sound libraries (numpy, simpleaudio) loaded successfully. Sound ENABLED.")
except ImportError:
    print("WARNING: numpy or simpleaudio library not found. Sound will be DISABLED.")
    print("Please install them by running: pip install numpy simpleaudio")

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

# --- Sound Engine Constants and Data ---
SAMPLE_RATE = 44100  # Samples per second (Hz)

NOTE_FREQUENCIES = {
    'REST': 0,
    'C3': 130.81, 'CS3': 138.59, 'D3': 146.83, 'DS3': 155.56, 'E3': 164.81, 'F3': 174.61, 'FS3': 185.00, 'G3': 196.00, 'GS3': 207.65, 'A3': 220.00, 'AS3': 233.08, 'B3': 246.94,
    'C4': 261.63, 'CS4': 277.18, 'D4': 293.66, 'DS4': 311.13, 'E4': 329.63, 'F4': 349.23, 'FS4': 369.99, 'G4': 392.00, 'GS4': 415.30, 'A4': 440.00, 'AS4': 466.16, 'B4': 493.88,
    'C5': 523.25, 'CS5': 554.37, 'D5': 587.33, 'DS5': 622.25, 'E5': 659.25, 'F5': 698.46, 'FS5': 739.99, 'G5': 783.99, 'GS5': 830.61, 'A5': 880.00, 'AS5': 932.33, 'B5': 987.77,
    'C6': 1046.50, 'CS6': 1108.73, 'D6': 1174.66, 'DS6': 1244.51, 'E6': 1318.51, 'F6': 1396.91, 'FS6': 1479.98, 'G6': 1567.98, 'GS6': 1661.22, 'A6': 1760.00, 'AS6': 1864.66, 'B6': 1975.53,
}

# Duration units: 1 = sixteenth note, 2 = eighth, 3 = dotted eighth, 4 = quarter
# This is a recognizable looping segment of the SMB 1-1 Overworld theme.
SMB_1_1_LOOP_THEME = [
    # Measure 1
    ('E5', 1), ('E5', 1), ('REST', 1), ('E5', 1), ('REST', 1), ('C5', 1), ('E5', 1), ('REST', 1),
    # Measure 2
    ('G5', 2), ('REST', 2), ('G4', 2), ('REST', 2),
    # Measure 3
    ('C5', 2), ('REST', 2), ('G4', 2), ('REST', 2), # Simplified from C . . G . . E
    # Measure 4
    ('E4', 2), ('REST', 2), ('A4', 1), ('B4', 1), ('AS4', 1), ('A4', 1),
    # Measure 5 (Start of repeating phrase)
    ('G4', 3), ('E5', 3), 
    ('G5', 2), ('A5', 2),
    # Measure 6
    ('F5', 2), ('G5', 2), ('REST', 1), ('E5', 1),
    # Measure 7
    ('C5', 1), ('D5', 1), ('B4', 2), ('REST', 4) 
    # This is roughly 7 measures, makes a decent loop.
]

if SOUND_ENABLED:
    def generate_square_wave(frequency, duration_seconds, amplitude=0.25):
        """Generates a square wave as a NumPy array for simpleaudio."""
        if frequency <= 0:  # Rest or invalid frequency
            return np.zeros(int(duration_seconds * SAMPLE_RATE)).astype(np.int16)
        
        num_samples = int(duration_seconds * SAMPLE_RATE)
        t = np.linspace(0, duration_seconds, num_samples, False)
        wave = amplitude * np.sign(np.sin(2 * np.pi * frequency * t))
        
        # Ensure it's 16-bit PCM format
        audio_data = (wave * 32767).astype(np.int16)
        return audio_data

class SoundEngine:
    def __init__(self, tempo_bpm=100):
        if not SOUND_ENABLED:
            return

        self.tempo = tempo_bpm
        # Duration of a quarter note in seconds
        self.quarter_note_duration_sec = 60.0 / self.tempo
        # Base duration for our song data (1 = sixteenth note)
        self.base_unit_duration_sec = self.quarter_note_duration_sec / 4.0
        
        self.song_data = []
        self.is_playing = False
        self.loop_playback = False
        self.playback_thread = None
        self.current_play_obj = None

    def load_song(self, song_tuples): # list of (note_name_str, duration_units)
        if not SOUND_ENABLED:
            return
        self.song_data = song_tuples

    def _playback_task(self):
        if not SOUND_ENABLED:
            return

        while self.is_playing:
            for note_name, duration_units in self.song_data:
                if not self.is_playing:  # Check before processing each note
                    break 
                
                frequency = NOTE_FREQUENCIES.get(note_name, 0)
                actual_duration_sec = self.base_unit_duration_sec * duration_units

                if frequency > 0:
                    audio_segment = generate_square_wave(frequency, actual_duration_sec)
                    if audio_segment.size > 0:
                        self.current_play_obj = sa.play_buffer(audio_segment, 1, 2, SAMPLE_RATE) # num_channels=1, bytes_per_sample=2
                        self.current_play_obj.wait_done() 
                else: # REST
                    time.sleep(actual_duration_sec)
            
            if not self.loop_playback: # If not looping, stop after one full playthrough
                self.is_playing = False
        
        # Ensure any lingering play object is stopped if loop ends or is_playing becomes false
        if self.current_play_obj and self.current_play_obj.is_playing():
            self.current_play_obj.stop()
        self.current_play_obj = None


    def play(self, loop=False):
        if not SOUND_ENABLED or self.is_playing:
            return
        
        if not self.song_data:
            print("SoundEngine: No song loaded.")
            return

        self.is_playing = True
        self.loop_playback = loop
        
        # Create and start a new thread for playback
        self.playback_thread = threading.Thread(target=self._playback_task, daemon=True)
        self.playback_thread.start()

    def stop(self):
        if not SOUND_ENABLED or not self.is_playing:
            return

        self.is_playing = False # Signal the thread to stop
        if self.current_play_obj and self.current_play_obj.is_playing():
            self.current_play_obj.stop() # Stop current note playback immediately

        if self.playback_thread and self.playback_thread.is_alive():
            self.playback_thread.join(timeout=0.5) # Wait briefly for thread to clean up
        
        self.playback_thread = None
        self.current_play_obj = None
        print("SoundEngine: Playback stopped.")

# --- End of Sound Engine ---


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
                "R": "MARIO_RED",      # Uses keys from CATOS_GUI.COLOR_MAP
                "W": "NES_WHITE",
                "X": None              # Transparent
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
        self.master_catos = master # Store reference to CATOS_GUI
        self.title("Mini Mario Game - SMB 1-1 Purr-fected++!")
        self.geometry(f"{DISPLAY_WIDTH}x{DISPLAY_HEIGHT}")
        self.resizable(False, False)

        self.NES_SKY_BLUE = master.NES_SKY_BLUE
        self.configure(bg=self.NES_SKY_BLUE)

        self.canvas = tk.Canvas(self, width=DISPLAY_WIDTH, height=DISPLAY_HEIGHT, bg=self.NES_SKY_BLUE, highlightthickness=0)
        self.canvas.pack()

        self.scale = DISPLAY_WIDTH / NES_SCREEN_WIDTH
        
        self.player_x = 3 * PLAYER_SIZE
        self.player_y = NES_SCREEN_HEIGHT - 2 * PLAYER_SIZE 
        self.player_vy = 0
        self.is_jumping = False
        self.on_ground = True 

        self.camera_x = 0
        self.COLOR_MAP = master.COLOR_MAP
        self.player_pixel_ids = []
        
        self.visual_blocks_data = []
        PS = PLAYER_SIZE
        H_NES = NES_SCREEN_HEIGHT
        
        def add_block(map_x_blocks, map_y_bottom_blocks, type_str, sprite_data, width_blocks=1, height_blocks=1, collidable=True):
            x1_nes = map_x_blocks * PS 
            y1_nes = H_NES - (map_y_bottom_blocks + height_blocks -1) * PS 
            
            x2_nes = x1_nes + width_blocks * PS
            y2_nes = y1_nes + height_blocks * PS 
            
            self.visual_blocks_data.append({
                'coords': (x1_nes, y1_nes, x2_nes, y2_nes),
                'type': type_str, 
                'collidable': collidable, 
                'sprite_data': sprite_data
            })

        # --- Build Level ---
        add_block(0, 1, 'ground', GROUND_BLOCK_DATA, width_blocks=69)
        add_block(71, 1, 'ground', GROUND_BLOCK_DATA, width_blocks=15)
        add_block(90, 1, 'ground', GROUND_BLOCK_DATA, width_blocks=44) 
        add_block(136, 1, 'ground', GROUND_BLOCK_DATA, width_blocks=(WORLD_WIDTH_BLOCKS - 136)) 

        add_block(16, 5, 'question_block_powerup', QUESTION_BLOCK_DATA)
        add_block(20, 5, 'brick', BRICK_BLOCK_DATA)
        add_block(21, 5, 'question_block_coin', QUESTION_BLOCK_DATA)
        add_block(22, 5, 'brick', BRICK_BLOCK_DATA)
        add_block(23, 5, 'question_block_coin', QUESTION_BLOCK_DATA)
        add_block(22, 9, 'question_block_1up', QUESTION_BLOCK_DATA) 

        # Pipes 
        add_block(28, 1, 'pipe', PIPE_TOP_DATA, width_blocks=2, height_blocks=2) 
        add_block(38, 1, 'pipe', PIPE_TOP_DATA, width_blocks=2, height_blocks=3) 
        add_block(46, 1, 'pipe', PIPE_TOP_DATA, width_blocks=2, height_blocks=4) 
        add_block(57, 1, 'pipe', PIPE_TOP_DATA, width_blocks=2, height_blocks=4) 
        
        add_block(78, 5, 'brick_coin', BRICK_BLOCK_DATA)
        add_block(79, 5, 'brick', BRICK_BLOCK_DATA)
        add_block(80, 5, 'brick_star', BRICK_BLOCK_DATA) 
        add_block(81, 5, 'brick', BRICK_BLOCK_DATA)

        add_block(91, 5, 'question_block_coin', QUESTION_BLOCK_DATA)
        add_block(92, 5, 'brick', BRICK_BLOCK_DATA) 
        add_block(93, 5, 'brick', BRICK_BLOCK_DATA)
        add_block(94, 5, 'question_block_powerup', QUESTION_BLOCK_DATA)
        add_block(94, 9, 'brick_high', BRICK_BLOCK_DATA) 

        # Pyramid / Stairs
        def add_stair_segment(base_x_blocks, base_y_bottom_blocks, height_in_blocks_for_step):
            add_block(base_x_blocks, base_y_bottom_blocks, 'ground_stair', GROUND_BLOCK_DATA, 
                      width_blocks=1, height_blocks=height_in_blocks_for_step)
        
        add_stair_segment(100, 1, 1)
        add_stair_segment(101, 1, 2)
        add_stair_segment(102, 1, 3)
        add_stair_segment(103, 1, 4)

        add_block(106, 5, 'brick', BRICK_BLOCK_DATA)
        add_block(107, 5, 'brick', BRICK_BLOCK_DATA)
        add_block(108, 5, 'brick', BRICK_BLOCK_DATA)

        add_stair_segment(113, 1, 1) 
        add_stair_segment(114, 1, 2)
        add_stair_segment(115, 1, 3)
        add_stair_segment(116, 1, 4)
        
        add_block(118, 1, 'pipe', PIPE_TOP_DATA, width_blocks=2, height_blocks=2) 

        add_block(123, 5, 'brick', BRICK_BLOCK_DATA) 
        add_block(124, 5, 'brick', BRICK_BLOCK_DATA)
        add_block(125, 5, 'question_block_powerup', QUESTION_BLOCK_DATA)
        add_block(126, 5, 'brick', BRICK_BLOCK_DATA)

        for i in range(8): 
            add_stair_segment(134 + i, 1, i + 1) 

        add_block(142, 1, 'flagpole_base', FLAGPOLE_BASE_BLOCK_DATA, width_blocks=1, height_blocks=1) 

        pole_visual_width_nes = PLAYER_SIZE / 4 
        pole_center_x_nes = (142 * PS) + (PS / 2) 
        pole_x1_nes = pole_center_x_nes - (pole_visual_width_nes / 2)
        pole_x2_nes = pole_center_x_nes + (pole_visual_width_nes / 2)
        
        pole_height_blocks_visual = 8 
        pole_bottom_y_on_base = H_NES - (1 * PS) 
        pole_y1_nes = pole_bottom_y_on_base - (pole_height_blocks_visual * PS) 
        pole_y2_nes = pole_bottom_y_on_base 
        
        self.visual_blocks_data.append({
            'coords': (pole_x1_nes, pole_y1_nes, pole_x2_nes, pole_y2_nes),
            'type': 'flagpole_pole', 'collidable': False, 
            'sprite_data': FLAGPOLE_POLE_SPRITE_DATA 
        })
        # --- End of Level Build ---

        self.canvas_items_map = {}
        
        self.collidable_platform_coords = []
        
        self.draw_all_visual_blocks() 

        self.pressed_keys = set()
        self.bind_keys()
        self.game_loop()

    def check_aabb_collision(self, r1_left, r1_top, r1_right, r1_bottom, r2_left, r2_top, r2_right, r2_bottom):
        """Helper function for Axis-Aligned Bounding Box collision detection."""
        return (r1_right > r2_left and
                r1_left < r2_right and
                r1_bottom > r2_top and
                r1_top < r2_bottom)

    def draw_pixel_art(self, base_x_nes, base_y_nes, entity_width_nes, entity_height_nes, sprite_definition):
        """
        Draws pixel art onto the canvas, scaled and positioned.
        base_x_nes, base_y_nes: Top-left corner of the entity in NES coordinates.
        entity_width_nes, entity_height_nes: Total dimensions of the entity in NES units.
        sprite_definition: Dictionary containing "pixels" (list of strings) and "colors" (char to hex map).
        Returns a list of canvas item IDs created.
        """
        pixel_art_rows = sprite_definition["pixels"]
        
        # Resolve color character keys to actual hex color strings using the main COLOR_MAP
        sprite_color_palette = {
            char_key: self.COLOR_MAP.get(mapped_color_key) 
            for char_key, mapped_color_key in sprite_definition["colors"].items()
            if mapped_color_key is not None 
        }

        art_height_px_native = len(pixel_art_rows)
        art_width_px_native = len(pixel_art_rows[0]) if art_height_px_native > 0 else 0
        
        if art_width_px_native == 0 or art_height_px_native == 0:
            return []


        # How large each "native pixel" of the art should be when drawn for this entity
        scaled_pixel_width_on_entity_nes = entity_width_nes / art_width_px_native
        scaled_pixel_height_on_entity_nes = entity_height_nes / art_height_px_native
        
        drawn_item_ids = []
        for r_idx, row_str in enumerate(pixel_art_rows):
            for c_idx, color_char_key in enumerate(row_str):
                actual_color_hex = sprite_color_palette.get(color_char_key)
                
                if actual_color_hex: 
                    px_x1_nes = base_x_nes + (c_idx * scaled_pixel_width_on_entity_nes)
                    py_y1_nes = base_y_nes + (r_idx * scaled_pixel_height_on_entity_nes)
                    px_x2_nes = base_x_nes + ((c_idx + 1) * scaled_pixel_width_on_entity_nes)
                    py_y2_nes = base_y_nes + ((r_idx + 1) * scaled_pixel_height_on_entity_nes)
                    
                    # Convert to canvas coordinates (apply camera and scaling)
                    px_x1_canvas = (px_x1_nes - self.camera_x) * self.scale
                    py_y1_canvas = py_y1_nes * self.scale 
                    px_x2_canvas = (px_x2_nes - self.camera_x) * self.scale
                    py_y2_canvas = py_y2_nes * self.scale
                    
                    if px_x2_canvas < 0 or px_x1_canvas > DISPLAY_WIDTH or \
                       py_y2_canvas < 0 or py_y1_canvas > DISPLAY_HEIGHT:
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
        """Redraws all visible static level blocks based on camera position."""
        for key in list(self.canvas_items_map.keys()): 
            items_to_delete = self.canvas_items_map.pop(key) 
            if isinstance(items_to_delete, list):
                for item_id in items_to_delete:
                    self.canvas.delete(item_id)
            elif items_to_delete: 
                 self.canvas.delete(items_to_delete)
        
        self.collidable_platform_coords = []

        for i, block_data in enumerate(self.visual_blocks_data):
            coords_nes = block_data['coords']
            x1_nes, y1_nes, x2_nes, y2_nes = coords_nes
            
            if x2_nes < self.camera_x or x1_nes > self.camera_x + NES_SCREEN_WIDTH:
                if block_data.get('collidable', True):
                    self.collidable_platform_coords.append(coords_nes)
                continue

            block_width_nes = x2_nes - x1_nes
            block_height_nes = y2_nes - y1_nes
            block_type = block_data['type']
            sprite_data_for_block = block_data.get('sprite_data')
            
            current_block_pixel_ids = []

            if sprite_data_for_block:
                tile_unit_w_nes = PLAYER_SIZE 
                tile_unit_h_nes = PLAYER_SIZE

                if block_width_nes < tile_unit_w_nes: tile_unit_w_nes = block_width_nes
                if block_height_nes < tile_unit_h_nes: tile_unit_h_nes = block_height_nes
                
                num_tiles_x = max(1, int(round(block_width_nes / tile_unit_w_nes)))
                num_tiles_y = max(1, int(round(block_height_nes / tile_unit_h_nes)))

                tile_draw_width_nes = block_width_nes / num_tiles_x
                tile_draw_height_nes = block_height_nes / num_tiles_y
                
                for row in range(num_tiles_y):
                    for col in range(num_tiles_x):
                        tile_x_nes = x1_nes + (col * tile_draw_width_nes)
                        tile_y_nes = y1_nes + (row * tile_draw_height_nes)
                        
                        ids = self.draw_pixel_art(tile_x_nes, tile_y_nes, 
                                                  tile_draw_width_nes, tile_draw_height_nes, 
                                                  sprite_data_for_block)
                        current_block_pixel_ids.extend(ids)
            
            self.canvas_items_map[f"{block_type}_{i}"] = current_block_pixel_ids

            if block_data.get('collidable', True):
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
        if hasattr(self.master_catos, 'sound_engine') and self.master_catos.sound_engine:
            self.master_catos.sound_engine.stop()

        if hasattr(self.master_catos, 'mario_game_window') and self.master_catos.mario_game_window == self:
            self.master_catos.mario_game_window = None
        self.destroy()


    def key_pressed(self, event):
        self.pressed_keys.add(event.keysym.lower())

    def key_released(self, event):
        keysym_lower = event.keysym.lower()
        if keysym_lower in self.pressed_keys:
            self.pressed_keys.remove(keysym_lower)

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
        prev_player_x = self.player_x
        prev_player_y = self.player_y

        current_dx = 0
        if 'a' in self.pressed_keys or 'left' in self.pressed_keys:
            current_dx -= MOVE_SPEED
        if 'd' in self.pressed_keys or 'right' in self.pressed_keys:
            current_dx += MOVE_SPEED
        
        self.player_x += current_dx

        player_h_col_rect_left = self.player_x
        player_h_col_rect_top = prev_player_y 
        player_h_col_rect_right = self.player_x + PLAYER_SIZE
        player_h_col_rect_bottom = prev_player_y + PLAYER_SIZE

        for plat_l, plat_t, plat_r, plat_b in self.collidable_platform_coords:
            if self.check_aabb_collision(player_h_col_rect_left, player_h_col_rect_top, player_h_col_rect_right, player_h_col_rect_bottom,
                                         plat_l, plat_t, plat_r, plat_b):
                if current_dx > 0: 
                    self.player_x = plat_l - PLAYER_SIZE
                elif current_dx < 0: 
                    self.player_x = plat_r
                
                player_h_col_rect_left = self.player_x 
                player_h_col_rect_right = self.player_x + PLAYER_SIZE
                break 

        if not self.on_ground or self.is_jumping: 
            self.player_vy += GRAVITY
        
        self.player_y += self.player_vy
        
        new_on_ground_status_this_frame = False

        player_v_col_rect_left = self.player_x 
        player_v_col_rect_top = self.player_y
        player_v_col_rect_right = self.player_x + PLAYER_SIZE
        player_v_col_rect_bottom = self.player_y + PLAYER_SIZE
        
        for plat_l, plat_t, plat_r, plat_b in self.collidable_platform_coords:
            if self.check_aabb_collision(player_v_col_rect_left, player_v_col_rect_top, player_v_col_rect_right, player_v_col_rect_bottom,
                                         plat_l, plat_t, plat_r, plat_b):
                
                if self.player_vy > 0: 
                    if prev_player_y + PLAYER_SIZE <= plat_t + 0.1: 
                        self.player_y = plat_t - PLAYER_SIZE 
                        self.player_vy = 0
                        new_on_ground_status_this_frame = True 
                        self.is_jumping = False 
                elif self.player_vy < 0: 
                    if prev_player_y >= plat_b - 0.1: 
                        self.player_y = plat_b 
                        self.player_vy = GRAVITY 
                
                player_v_col_rect_top = self.player_y
                player_v_col_rect_bottom = self.player_y + PLAYER_SIZE
                if new_on_ground_status_this_frame: break 

        self.on_ground = new_on_ground_status_this_frame

        if self.player_x < 0: self.player_x = 0
        if self.player_x + PLAYER_SIZE > WORLD_WIDTH_NES:
            self.player_x = WORLD_WIDTH_NES - PLAYER_SIZE
        
        if self.player_y > NES_SCREEN_HEIGHT + PLAYER_SIZE * 2 : 
            print("Fell off! Oh noes! Resetting Mario, meow!")
            self.player_x = 3 * PLAYER_SIZE 
            self.player_y = NES_SCREEN_HEIGHT - 2 * PLAYER_SIZE 
            self.player_vy = 0
            self.on_ground = True 
            self.is_jumping = False
            self.camera_x = 0 
            
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
        except tk.TclError as e:
            print(f"Game window TclError (likely closed or during shutdown): {e}")
        except Exception as e:
            print(f"Oopsie, a little furball in the game loop: {e}")
            import traceback
            traceback.print_exc() 
            if self.winfo_exists():
                self.on_closing() 

class CATOS_GUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("CATOS - Meow Edition v3.0 NES Emu! THE ULTIMATE!") 
        self.geometry("500x500") 
        self.configure(bg="#2c3e50")

        # --- NES Color Palette Definitions ---
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
        # --- End of NES Color Palette ---

        # Master Color Map for resolving sprite color keys to hex values
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

        cat_art_text = "  /\\_/\\ \n ( >w< )  < WORLD 1-1 READY!\n  > ^ < \nCATOS NES EVO++!" 
        cat_label = tk.Label(self,text=cat_art_text,font=("Courier New", 14),bg="#2c3e50",fg="#ecf0f1",justify=tk.LEFT)
        cat_label.pack(pady=20)

        launch_button = tk.Button(
            self, text="Play SMB 1-1!", font=("Arial", 16),bg="#e74c3c", fg="white",
            activebackground="#c0392b",relief=tk.FLAT,padx=15,pady=10,command=self.launch_main_menu)
        launch_button.pack(pady=20)

        self.clock_label = tk.Label(self,text="",font=("Arial", 12),bg="#2c3e50",fg="#bdc3c7")
        self.clock_label.pack(side=tk.BOTTOM, pady=10)
        self.update_clock() 
        
        self.mario_game_window = None
        self.mario_main_menu_window = None

        # Initialize Sound Engine
        self.sound_engine = None
        if SOUND_ENABLED:
            self.sound_engine = SoundEngine(tempo_bpm=100) 
            self.sound_engine.load_song(SMB_1_1_LOOP_THEME)
        else: 
            class DummySoundEngine:
                def load_song(self, song): pass
                def play(self, loop=False): pass
                def stop(self): pass
            self.sound_engine = DummySoundEngine()


        self.protocol("WM_DELETE_WINDOW", self.on_closing_catos)

    def on_closing_catos(self):
        if self.sound_engine:
            self.sound_engine.stop()
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
        if self.mario_game_window and self.mario_game_window.winfo_exists():
            print("Closing active game to show main menu.")
            if self.sound_engine: self.sound_engine.stop() 
            self.mario_game_window.destroy()
            self.mario_game_window = None

        if self.mario_main_menu_window is None or not self.mario_main_menu_window.winfo_exists():
            self.mario_main_menu_window = MarioMainMenuWindow(self, self.actually_launch_mario_game)
            self.mario_main_menu_window.focus_set() 
        else:
            self.mario_main_menu_window.lift() 
            self.mario_main_menu_window.focus_set() 

    def actually_launch_mario_game(self):
        if self.mario_main_menu_window and self.mario_main_menu_window.winfo_exists():
            self.mario_main_menu_window.destroy()
            self.mario_main_menu_window = None
        
        if self.mario_game_window is None or not self.mario_game_window.winfo_exists():
            self.mario_game_window = MarioGameWindow(self) 
            self.mario_game_window.focus_set() 
            if self.sound_engine: 
                self.sound_engine.play(loop=True)
        else:
            self.mario_game_window.lift() 
            self.mario_game_window.focus_set() 
            if self.sound_engine and not self.sound_engine.is_playing: 
                 self.sound_engine.play(loop=True)


if __name__ == "__main__":
    app = CATOS_GUI() 
    app.mainloop() 
