import tkinter as tk
import time
import threading # For sound playback
import math # For rounding in physics
import collections # For deque to track keys

# Attempt to import sound libraries
SOUND_ENABLED = False
try:
    import numpy as np
    import simpleaudio as sa
    SOUND_ENABLED = True
    print("Sound libraries (numpy, simpleaudio) loaded successfully. Sound ENABLED. Meow-some!")
except ImportError:
    print("WARNING: numpy or simpleaudio library not found. Sound will be DISABLED. No purrs for you!")
    print("Please install them by running: pip install numpy simpleaudio. It's super easy, peasy, lemon squeezy!")

# --- Game Constants ---
NES_SCREEN_WIDTH = 256
NES_SCREEN_HEIGHT = 240
DISPLAY_WIDTH = 800
DISPLAY_HEIGHT = 750 # Adjusted to maintain NES aspect ratio (800 / 256 * 240 = 750)

PLAYER_SIZE = 16 # NES pixels (16x16 sprite)
GRAVITY = 0.5
JUMP_POWER = 8
MOVE_SPEED = 2
FPS = 60
DELAY_MS = 1000 // FPS # Milliseconds per frame

# --- World Dimensions for SMB 1-1 (in NES pixels) ---
WORLD_WIDTH_BLOCKS = 210
WORLD_WIDTH_NES = WORLD_WIDTH_BLOCKS * PLAYER_SIZE
WORLD_HEIGHT_NES = NES_SCREEN_HEIGHT


# --- Pixel Art Data ---
# Mario Sprites (Simplified for this example)
SMALL_MARIO_STANDING_DATA = {
    "colors": { "R": "MARIO_RED", "S": "NES_SKIN_PEACH", "B": "NES_DARK_BROWN", "X": None, },
    "pixels": [
        "XXXXRRRRRRXXXX", "XXXRRRRRRRRXXX", "XXXBBBSSBBBXXX", "XXBBBSBSSBSBXX",
        "XXBBBSBSSBSBXX", "XXXBBBBBBBBXXX", "XXXRRRRRRRRXXX", "XXRRSRRS RRXX",
        "XXRRSRRS RRXX", "XXRRSSSSSSRRXX", "XXSSSSRRSSSSXX", "XXSS RR RR SSXX",
        "XXXXBBXXBBXXXX", "XXXBBBBBBBBXXX", "XXBBBBXXBBBBXX", "XXXXXXXXXXXXXXXX"
    ]
}
# Bug 11 fix: Added walking and jumping sprites, Mario's gonna move!
SMALL_MARIO_WALKING_1_DATA = { # Right-facing, one frame of walk
    "colors": { "R": "MARIO_RED", "S": "NES_SKIN_PEACH", "B": "NES_DARK_BROWN", "X": None, },
    "pixels": [
        "XXXXRRRRRRXXXX", "XXXRRRRRRRRXXX", "XXXBBBSSBBBXXX", "XXBBBSBSSBSBXX",
        "XXBBBSBSSBSBXX", "XXXBBBBBBBBXXX", "XXXRRRRRRRRXXX", "XXRRSRRS RRXX",
        "XXRRSRRS RRXX", "XXRRSSSSSSRRXX", "XXSSSSRRSSSSXX", "XXSS RR RR SSXX",
        "XXXXBBBBBBXXXX", "XXXBBXXBBBBXXX", "XXBBXX XXBBBBXX", "XXXXXXXXXXXXXXXX"
    ]
}
SMALL_MARIO_JUMPING_DATA = {
    "colors": { "R": "MARIO_RED", "S": "NES_SKIN_PEACH", "B": "NES_DARK_BROWN", "X": None, },
    "pixels": [
        "XXXXRRRRRRXXXX", "XXXRRRRRRRRXXX", "XXXBBBSSBBBXXX", "XXBBBSBSSBSBXX",
        "XXBBBSBSSBSBXX", "XXXBBBBBBBBXXX", "XXXRRRRRRRRXXX", "XXRRSRRS RRXX",
        "XXRRSRRS RRXX", "XXRRSSSSSSRRXX", "XXSSSSRRSSSSXX", "XXSS RR RR SSXX",
        "XXXBBBBBBBBXXX", "XXBBBBXXBBBBXX", "XBBXXXXXXBBX", "XXXXXXXXXXXXXXXX"
    ]
}

BRICK_BLOCK_DATA = {
    "colors": { "D": "NES_BRICK_DARK", "L": "NES_BRICK_COLOR", "X": None, },
    "pixels": [
        "DDDDDDDDDDDDDDDD", "DLLLLLDDLLLLLDDD", "DLLLLLDDLLLLLDDL", "DDDDDDDDDDDDDDDL",
        "DLDDLLLLLDDLLLLD", "DLDDLLLLLDDLLLLD", "DDDDDDDDDDDDDDDD", "DDDDDDDDDDDDDDDD",
        "DLLLLLDDLLLLLDDD", "DLLLLLDDLLLLLDDL", "DDDDDDDDDDDDDDDL", "DLDDLLLLLDDLLLLD",
        "DLDDLLLLLDDLLLLD", "DDDDDDDDDDDDDDDD", "DDDDDDDDDDDDDDDD", "DDDDDDDDDDDDDDDD",
    ]
}
QUESTION_BLOCK_DATA = {
    "colors": { "O": "NES_QUESTION_OUTLINE", "Y": "NES_QUESTION_BLOCK_COLOR", "Q": "NES_WHITE", "S": "NES_QUESTION_SHADOW", "X": None, },
    "pixels": [
        "OSOOOOOOOOOOOOOS", "YOOOOOOOOOOOOOOY", "YOOYYYYYYYYYYOOY", "YOOYQQQQQYYYQYOY",
        "YOOYQYYYQYYYQQOY", "YOOYQYYYQYYYQYOY", "YOOYQYYYQYYYQYOY", "YOOYQQQQQYYYQYOY",
        "YOOYYYYYYYYYYYOY", "YOOYYYQQQYYYYYOY", "YOOYYYQQQYYYYYOY", "YOOYYYQQQYYYYYOY",
        "YOOYYYYYYYYYYYOY", "YOOOOOOOOOOOOOOY", "OSOOOOOOOOOOOOOS", "SSSSSSSSSSSSSSSS",
    ]
}
GROUND_BLOCK_DATA = {
    "colors": { "D": "NES_GROUND_DARK", "L": "NES_GROUND_COLOR", "X": None, },
    "pixels": [
        "LLLLLLLLLLLLLLLL", "LLLLLLLLLLLLLLLL", "DDDDDDDDDDDDDDDD", "LDLDLDLDLDLDLDLD",
        "DLDLDLDLDLDLDLDL", "LLLLLLLLLLLLLLLL", "LLLLLLLLLLLLLLLL", "DDDDDDDDDDDDDDDD",
        "LDLDLDLDLDLDLDLD", "DLDLDLDLDLDLDLDL", "LLLLLLLLLLLLLLLL", "LLLLLLLLLLLLLLLL",
        "DDDDDDDDDDDDDDDD", "DDDDDDDDDDDDDDDD", "DDDDDDDDDDDDDDDD", "DDDDDDDDDDDDDDDD",
    ]
}
PIPE_TOP_DATA = {
    "colors": { "L": "NES_PIPE_GREEN_LIGHT", "M": "NES_PIPE_GREEN", "D": "NES_PIPE_GREEN_DARK", "B": "NES_BLACK", "X": None, },
    "pixels": [
        "XXLLLLLLLLLLXX", "XLMMMMMMMMMMMX", "XMBBBBBBBBBBMX", "XMBBBBBBBBBBMX",
        "XMDMMMMMMMMDMX", "XMDMMMMMMMMDMX", "XMDMMMMMMMMDMX", "XMDMMMMMMMMDMX",
        "XMDMMMMMMMMDMX", "XMDMMMMMMMMDMX", "XMDMMMMMMMMDMX", "XMDMMMMMMMMDMX",
        "XMDMMMMMMMMDMX", "XMDMMMMMMMMDMX", "XMDMMMMMMMMDMX", "XMDDDDDDDDDDMX",
    ]
}
# Bug 13 fix: Added PIPE_MIDDLE_DATA for proper pipe drawing, so seamless!
PIPE_MIDDLE_DATA = {
    "colors": { "L": "NES_PIPE_GREEN_LIGHT", "M": "NES_PIPE_GREEN", "D": "NES_PIPE_GREEN_DARK", "B": "NES_BLACK", "X": None, },
    "pixels": [
        "BLLLLLLLLLLLLLLB", "BLLLLLLLLLLLLLLB", "BMMMMMMMMMMMMMMB", "BMMMMMMMMMMMMMMB",
        "BMMMMMMMMMMMMMMB", "BMMMMMMMMMMMMMMB", "BMMMMMMMMMMMMMMB", "BMMMMMMMMMMMMMMB",
        "BMMMMMMMMMMMMMMB", "BMMMMMMMMMMMMMMB", "BMMMMMMMMMMMMMMB", "BMMMMMMMMMMMMMMB",
        "BMMMMMMMMMMMMMMB", "BMMMMMMMMMMMMMMB", "BMMMMMMMMMMMMMMB", "BDDDDDDDDDDDDDDB",
    ]
}
FLAGPOLE_BASE_BLOCK_DATA = {
    "colors": { "G": "FLAGPOLE_GRAY", "D": "FLAGPOLE_DARK_GRAY", "X": None },
    "pixels": [
        "DDDDDDDDDDDDDDDD", "DGGGGGGGGGGGGXXD", "DGGGGGGGGGGGGXXD", "DGGGGGGGGGGGGXXD",
        "DGGGGGGGGGGGGXXD", "DGGGGGGGGGGGGXXD", "DGGGGGGGGGGGGXXD", "DGGGGGGGGGGGGXXD",
        "DGGGGGGGGGGGGXXD", "DGGGGGGGGGGGGXXD", "DGGGGGGGGGGGGXXD", "DGGGGGGGGGGGGXXD",
        "DGGGGGGGGGGGGXXD", "DGGGGGGGGGGGGXXD", "DGGGGGGGGGGGGXXD", "DDDDDDDDDDDDDDDD"
    ]
}
FLAGPOLE_POLE_SPRITE_DATA = { # Native is 2x16 pixels
    "colors": { "L": "FLAGPOLE_GRAY", "D": "FLAGPOLE_DARK_GRAY", "X": None, },
    "pixels": [ "LD", "LD", "LD", "LD", "LD", "LD", "LD", "LD", "LD", "LD", "LD", "LD", "LD", "LD", "LD", "LD" ]
}
# --- End of Pixel Art Data ---

# --- Sound Engine Constants and Data ---
SAMPLE_RATE = 44100
NOTE_FREQUENCIES = {
    'REST': 0, 'C3': 130.81, 'CS3': 138.59, 'D3': 146.83, 'DS3': 155.56, 'E3': 164.81, 'F3': 174.61, 'FS3': 185.00, 'G3': 196.00, 'GS3': 207.65, 'A3': 220.00, 'AS3': 233.08, 'B3': 246.94,
    'C4': 261.63, 'CS4': 277.18, 'D4': 293.66, 'DS4': 311.13, 'E4': 329.63, 'F4': 349.23, 'FS4': 369.99, 'G4': 392.00, 'GS4': 415.30, 'A4': 440.00, 'AS4': 466.16, 'B4': 493.88,
    'C5': 523.25, 'CS5': 554.37, 'D5': 587.33, 'DS5': 622.25, 'E5': 659.25, 'F5': 698.46, 'FS5': 739.99, 'G5': 783.99, 'GS5': 830.61, 'A5': 880.00, 'AS5': 932.33, 'B5': 987.77,
    'C6': 1046.50, 'CS6': 1108.73, 'D6': 1174.66, 'DS6': 1244.51, 'E6': 1318.51, 'F6': 1396.91, 'FS6': 1479.98, 'G6': 1567.98, 'GS6': 1661.22, 'A6': 1760.00, 'AS6': 1864.66, 'B6': 1975.53,
    'JUMP_SFX': 600, 'LAND_SFX': 400 # Bug 12 fix: Added specific SFX frequencies, boing!
}
SMB_1_1_LOOP_THEME = [
    ('E5', 1), ('E5', 1), ('REST', 1), ('E5', 1), ('REST', 1), ('C5', 1), ('E5', 1), ('REST', 1),
    ('G5', 2), ('REST', 2), ('G4', 2), ('REST', 2), ('C5', 2), ('REST', 2), ('G4', 2), ('REST', 2),
    ('E4', 2), ('REST', 2), ('A4', 1), ('B4', 1), ('AS4', 1), ('A4', 1), ('G4', 3), ('E5', 3),
    ('G5', 2), ('A5', 2), ('F5', 2), ('G5', 2), ('REST', 1), ('E5', 1), ('C5', 1), ('D5', 1), ('B4', 2), ('REST', 4)
]

if SOUND_ENABLED:
    def generate_square_wave(frequency, duration_seconds, amplitude=0.25):
        if frequency <= 0:
            return np.zeros(int(duration_seconds * SAMPLE_RATE)).astype(np.int16)
        num_samples = int(duration_seconds * SAMPLE_RATE)
        t = np.linspace(0, duration_seconds, num_samples, False)
        wave = amplitude * np.sign(np.sin(2 * np.pi * frequency * t))
        audio_data = (wave * 32767).astype(np.int16)
        return audio_data

class SoundEngine:
    def __init__(self, tempo_bpm=100):
        if not SOUND_ENABLED: return
        self.tempo = tempo_bpm
        self.quarter_note_duration_sec = 60.0 / self.tempo
        self.base_unit_duration_sec = self.quarter_note_duration_sec / 4.0
        self.song_data = []
        self.is_playing = False
        self.loop_playback = False
        self.playback_thread = None
        self.current_play_obj = None

        # Bug 12 fix: SFX management, multiple sound channels for pure chaos!
        self.sfx_volume = 0.15 # Slightly lower volume for SFX, so you don't go deaf!
        self.sfx_channels = [] # To manage multiple concurrent SFX, multi-tasking like a boss!
        self.max_sfx_channels = 8 # Limit concurrent SFX, more channels means more fun, purr nyah!

    def load_song(self, song_tuples):
        if not SOUND_ENABLED: return
        self.song_data = song_tuples

    def _playback_task(self):
        if not SOUND_ENABLED: return
        while self.is_playing:
            for note_name, duration_units in self.song_data:
                if not self.is_playing: break
                frequency = NOTE_FREQUENCIES.get(note_name, 0)
                actual_duration_sec = self.base_unit_duration_sec * duration_units
                if frequency > 0:
                    audio_segment = generate_square_wave(frequency, actual_duration_sec, amplitude=0.25)
                    if audio_segment.size > 0:
                        self.current_play_obj = sa.play_buffer(audio_segment, 1, 2, SAMPLE_RATE)
                        self.current_play_obj.wait_done()
                else: time.sleep(actual_duration_sec)
            if not self.loop_playback: self.is_playing = False
        if self.current_play_obj and self.current_play_obj.is_playing():
            self.current_play_obj.stop()
        self.current_play_obj = None

    def play(self, loop=False):
        if not SOUND_ENABLED or self.is_playing or not self.song_data:
            if not self.song_data and SOUND_ENABLED: print("SoundEngine: No song loaded. Boo hiss!")
            return
        self.is_playing = True
        self.loop_playback = loop
        self.playback_thread = threading.Thread(target=self._playback_task, daemon=True)
        self.playback_thread.start()
        print("SoundEngine: Music started! Time to groove, baby!")

    # Bug 12 fix: New method for playing sound effects, blast off!
    def play_sfx(self, note_name, duration_seconds=0.1, amplitude=None):
        if not SOUND_ENABLED: return
        frequency = NOTE_FREQUENCIES.get(note_name, 0)
        if frequency <= 0: return

        amp = amplitude if amplitude is not None else self.sfx_volume
        audio_segment = generate_square_wave(frequency, duration_seconds, amp)
        
        # Clean up finished SFX channels
        self.sfx_channels = [p for p in self.sfx_channels if p.is_playing()]

        # Play if there's an available channel
        if len(self.sfx_channels) < self.max_sfx_channels:
            try:
                play_obj = sa.play_buffer(audio_segment, 1, 2, SAMPLE_RATE)
                self.sfx_channels.append(play_obj)
            except Exception as e:
                print(f"SoundEngine: Failed to play SFX: {e}. Oopsie!")
        # else: print("SoundEngine: SFX channels full. Dropping SFX. No room for more noise!")

    def stop(self):
        if not SOUND_ENABLED and not self.is_playing: return
        self.is_playing = False
        if self.current_play_obj and self.current_play_obj.is_playing():
            self.current_play_obj.stop()
        # Stop all SFX channels too! So much stopping!
        for sfx_obj in self.sfx_channels:
            if sfx_obj.is_playing(): sfx_obj.stop()
        self.sfx_channels.clear()

        if self.playback_thread and self.playback_thread.is_alive():
            self.playback_thread.join(timeout=0.5)
        self.playback_thread = None
        self.current_play_obj = None
        print("SoundEngine: Playback stopped. Silence is golden... sometimes!")
# --- End of Sound Engine ---


class MarioMainMenuWindow(tk.Toplevel):
    def __init__(self, master, game_launcher_callback):
        super().__init__(master)
        self.game_launcher_callback = game_launcher_callback
        self.master_catos = master

        self.title("SUPER MARIO BROS. - Purr-fect Start!")
        self.geometry(f"{DISPLAY_WIDTH}x{DISPLAY_HEIGHT}")
        self.resizable(False, False)
        # Bug 9 fix: Use NES sky blue for menu background for consistency, it's so pretty!
        self.configure(bg=self.master_catos.NES_SKY_BLUE) 

        self.SMB_WHITE = "#FCFCFC"
        self.SMB_RED_TEXT = "#D03030"
        self.SMB_YELLOW_TEXT = "#FAC000"

        self.canvas = tk.Canvas(self, width=DISPLAY_WIDTH, height=DISPLAY_HEIGHT, bg=self.master_catos.NES_SKY_BLUE, highlightthickness=0)
        self.canvas.pack()

        self.menu_options = ["1 PLAYER GAME", "2 PLAYER GAME"]
        self.current_selection_index = 0
        self.top_score = 0 # This would typically be loaded from a save file, but hey, it's a demo!

        self.cursor_pixel_data = {
            "colors": { "R": "MARIO_RED", "W": "NES_WHITE", "X": None },
            "pixels": [ "XXRRXX", "XRRRRX", "RRRRRR", "RRWWWR", "XWWWWX", "XWWWWX", ]
        }
        self.cursor_image_id = None # Will store the canvas ID for the cursor image
        self.cursor_photo_image = None # To store the PhotoImage for the cursor

        self._create_cursor_photo_image() # Create the cursor image, yay!
        self.draw_menu_elements()
        self.bind_keys()
        self.focus_set()

    def _create_cursor_photo_image(self):
        """Creates the PhotoImage for the menu cursor. It's a tiny, powerful pixel-pusher!"""
        cursor_display_size_w = 36
        cursor_display_size_h = 36

        art_rows = self.cursor_pixel_data["pixels"]
        native_art_h = len(art_rows)
        native_art_w = len(art_rows[0]) if native_art_h > 0 else 0

        if not (native_art_w > 0 and native_art_h > 0): return

        self.cursor_photo_image = tk.PhotoImage(width=cursor_display_size_w, height=cursor_display_size_h)
        
        pixel_w_on_image = cursor_display_size_w / native_art_w
        pixel_h_on_image = cursor_display_size_h / native_art_h

        resolved_colors = {
            char_key: self.master_catos.COLOR_MAP.get(mapped_color_key)
            for char_key, mapped_color_key in self.cursor_pixel_data["colors"].items()
            if mapped_color_key is not None
        }

        for r_idx, row_str in enumerate(art_rows):
            for c_idx, color_char_key in enumerate(row_str):
                actual_fill_color = resolved_colors.get(color_char_key)
                if actual_fill_color:
                    x1 = round(c_idx * pixel_w_on_image)
                    y1 = round(r_idx * pixel_h_on_image)
                    x2 = round((c_idx + 1) * pixel_w_on_image)
                    y2 = round((r_idx + 1) * pixel_h_on_image)
                    
                    for y_px in range(y1, y2):
                        for x_px in range(x1, x2):
                            if 0 <= x_px < cursor_display_size_w and 0 <= y_px < cursor_display_size_h:
                                try:
                                    self.cursor_photo_image.put(actual_fill_color, (x_px, y_px))
                                except tk.TclError:
                                    pass # Silently fail if color or coords are invalid, better than crashing, meow!


    def draw_menu_elements(self):
        self.canvas.delete("all") # Clear previous drawings, poof!

        # SUPER MARIO BROS. Title, so epic!
        self.canvas.create_text(DISPLAY_WIDTH / 2, DISPLAY_HEIGHT * 0.2, text="SUPER MARIO BROS.",
                                font=("Press Start 2P", 48, "bold"), fill=self.SMB_RED_TEXT, anchor="center") # Custom font is so cool!
        # Nintendo Copyright, gotta respect the classics!
        self.canvas.create_text(DISPLAY_WIDTH / 2, DISPLAY_HEIGHT * 0.1, text="©1985 NINTENDO",
                                font=("Press Start 2P", 16), fill=self.SMB_WHITE, anchor="center") # Also custom font!
        # TOP SCORE, let's aim for that high score, purr nyah!
        self.canvas.create_text(DISPLAY_WIDTH / 2, DISPLAY_HEIGHT * 0.35, text=f"TOP - {self.top_score:06d}",
                                font=("Press Start 2P", 28, "bold"), fill=self.SMB_WHITE, anchor="center") # Custom font!

        option_y_start = DISPLAY_HEIGHT * 0.55
        option_y_spacing = 60

        for i, option_text in enumerate(self.menu_options):
            y_pos = option_y_start + (i * option_y_spacing)
            self.canvas.create_text(DISPLAY_WIDTH / 2, y_pos, text=option_text,
                                    font=("Press Start 2P", 28, "bold"), fill=self.SMB_WHITE, anchor="center") # Custom font, yay!

            if i == self.current_selection_index and self.cursor_photo_image:
                cursor_display_size_w = self.cursor_photo_image.width()
                
                estimated_text_half_width = 250 # Approximate adjusted for new font size, gotta make it look sleek!
                cursor_x_canvas = (DISPLAY_WIDTH / 2) - estimated_text_half_width - cursor_display_size_w - 15
                cursor_y_canvas = y_pos # Vertically align with text center (anchor for image will be 'c')
                
                if self.cursor_image_id:
                    self.canvas.coords(self.cursor_image_id, cursor_x_canvas, cursor_y_canvas)
                else:
                    self.cursor_image_id = self.canvas.create_image(cursor_x_canvas, cursor_y_canvas,
                                                                 image=self.cursor_photo_image, anchor="c")

    def bind_keys(self):
        self.bind("<KeyPress-Up>", self.move_selection_up)
        self.bind("<KeyPress-Down>", self.move_selection_down)
        self.bind("<KeyPress-Return>", self.confirm_selection)
        self.bind("<KeyPress-space>", self.confirm_selection)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        self.destroy()
        if self.master_catos: self.master_catos.mario_main_menu_window = None

    def move_selection_up(self, event=None):
        self.current_selection_index = (self.current_selection_index - 1 + len(self.menu_options)) % len(self.menu_options)
        self.draw_menu_elements()
        if self.master_catos.sound_engine: self.master_catos.sound_engine.play_sfx('C5', duration_seconds=0.05) # Play a little boop!

    def move_selection_down(self, event=None):
        self.current_selection_index = (self.current_selection_index + 1) % len(self.menu_options)
        self.draw_menu_elements()
        if self.master_catos.sound_engine: self.master_catos.sound_engine.play_sfx('C5', duration_seconds=0.05) # Another boop!

    def confirm_selection(self, event=None):
        if self.master_catos.sound_engine: self.master_catos.sound_engine.play_sfx('E5', duration_seconds=0.08) # Confirm sound!
        selected_option = self.menu_options[self.current_selection_index]
        if selected_option == "1 PLAYER GAME":
            print("Attempting to launch 1 PLAYER GAME... Get ready for some fun!") # Debug print
            if self.game_launcher_callback: self.game_launcher_callback()
        elif selected_option == "2 PLAYER GAME":
            # Bug 8 fix: Make the message more noticeable and stay a bit longer. Also, a cute sad face!
            msg_id = self.canvas.create_text(DISPLAY_WIDTH / 2, DISPLAY_HEIGHT * 0.85,
                                             text="2 PLAYER GAME NOT IMPLEMENTED :(\n(Yet! Meow!)",
                                             font=("Press Start 2P", 24, "bold"), fill=self.SMB_YELLOW_TEXT, anchor="center") # Changed color and font!
            self.after(3000, lambda: self.canvas.delete(msg_id) if self.winfo_exists() and self.canvas.winfo_exists() else None)


class MarioGameWindow(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.master_catos = master
        self.title("Mini Mario Game - SMB 1-1 Purr-fected++ Optimized!")
        self.geometry(f"{DISPLAY_WIDTH}x{DISPLAY_HEIGHT}")
        self.resizable(False, False)

        self.NES_SKY_BLUE = master.NES_SKY_BLUE
        self.configure(bg=self.NES_SKY_BLUE)

        self.canvas = tk.Canvas(self, width=DISPLAY_WIDTH, height=DISPLAY_HEIGHT, bg=self.NES_SKY_BLUE, highlightthickness=0)
        self.canvas.pack()

        self.scale = DISPLAY_WIDTH / NES_SCREEN_WIDTH # Canvas pixels per NES pixel

        self.player_x = 3 * PLAYER_SIZE
        self.player_y = NES_SCREEN_HEIGHT - 2 * PLAYER_SIZE
        self.player_vy = 0
        self.is_jumping = False
        self.on_ground = True # Bug 16 fix: Mario starts on the ground, ready to rumble!

        self.camera_x = 0
        self.COLOR_MAP = master.COLOR_MAP
        
        self.player_image_id = None # Stores canvas ID for the player's image
        self.sprite_images = {} # Cache for PhotoImage objects: {sprite_key: PhotoImage}, so speedy!

        # Bug 1 fix: Initialize pressed_keys, a secret weapon!
        self.pressed_keys = set() # To keep track of what keys are being held down, it's like a secret diary!
        
        # Bug 11 fix: Mario sprite state, he's a chameleon!
        self.player_state = 'standing' # 'standing', 'walking', 'jumping'
        self.player_facing_right = True # For future mirroring, if we get fancy!

        # Bug 10 fix: Score system, gotta keep track of those points!
        self.score = 0
        self.score_text_id = None

        # Bug 18 fix: Win condition flag, aim for glory!
        self.game_won = False
        self.win_text_id = None

        # Bug 3 fix: Refactored level data to individual tiles, so clean, so powerful!
        self.level_tiles = [] # List of individual tile definitions, much cleaner!
        self.collidable_platform_coords = [] # Still need this for collision detection

        self._build_level() # Populate self.level_tiles and pre-cache block sprites, building dreams!
        
        self.bind_keys()
        self.focus_set() # Crucial for Toplevel to receive key events, gotta listen up!
        self.game_loop_active = True
        self.last_frame_time = time.perf_counter() # For FPS calculation, keeping it smooth!
        
        self._draw_all_level_elements() # Initial draw before loop starts
        self.update_score_display() # Show the score right away!
        self.game_loop_step() # Bug 6 fix: Start the game loop from here directly, less confusing!

    def _get_or_create_sprite_image(self, sprite_type_key, sprite_definition, entity_display_width, entity_display_height):
        """
        Creates (or retrieves from cache) a PhotoImage for a given sprite type and display size.
        It's like a magic factory for pixel art!
        """
        entity_display_width = int(round(entity_display_width))
        entity_display_height = int(round(entity_display_height))

        if entity_display_width <= 0 or entity_display_height <= 0:
            return None # Cannot create a zero or negative size image, that's just silly!

        cache_key = f"{sprite_type_key}_{entity_display_width}x{entity_display_height}"

        if cache_key in self.sprite_images:
            return self.sprite_images[cache_key]

        art_rows = sprite_definition["pixels"]
        native_art_h = len(art_rows)
        native_art_w = len(art_rows[0]) if native_art_h > 0 else 0

        if not (native_art_w > 0 and native_art_h > 0): return None

        img = tk.PhotoImage(width=entity_display_width, height=entity_display_height)

        pixel_w_on_image = entity_display_width / native_art_w
        pixel_h_on_image = entity_display_height / native_art_h
        
        resolved_sprite_colors = {
            char_key: self.COLOR_MAP.get(mapped_color_key)
            for char_key, mapped_color_key in sprite_definition["colors"].items()
            if mapped_color_key is not None
        }

        for r_idx, row_str in enumerate(art_rows):
            for c_idx, color_char_key in enumerate(row_str):
                actual_fill_color = resolved_sprite_colors.get(color_char_key)
                if actual_fill_color:
                    x1 = round(c_idx * pixel_w_on_image)
                    y1 = round(r_idx * pixel_h_on_image)
                    x2 = round((c_idx + 1) * pixel_w_on_image)
                    y2 = round((r_idx + 1) * pixel_h_on_image)
                    
                    for y_px in range(y1, y2):
                        for x_px in range(x1, x2):
                            if 0 <= x_px < entity_display_width and 0 <= y_px < entity_display_height:
                                try:
                                    img.put(actual_fill_color, (x_px, y_px))
                                except tk.TclError:
                                    pass # Just keep going, no biggie!
        
        self.sprite_images[cache_key] = img
        return img

    def _add_level_block_to_tiles(self, map_x_blocks, map_y_bottom_blocks, type_str, sprite_data, width_blocks=1, height_blocks=1, collidable=True):
        """
        Helper to add blocks to the level, breaking them into individual PLAYER_SIZE tiles.
        Bug 3 fix: This function now adds individual tiles to self.level_tiles.
        Bug 13 fix: Handles pipes and flagpole tiling logic. So much precision, it's criminal!
        """
        PS = PLAYER_SIZE
        H_NES = NES_SCREEN_HEIGHT

        # Define sprite data based on type
        actual_sprite_data = sprite_data
        
        if type_str == 'flagpole_pole':
            # Bug 4 fix: Proper flagpole dimensions and tiling, it's a pole party!
            pole_native_width_nes = len(FLAGPOLE_POLE_SPRITE_DATA["pixels"][0]) # 2
            pole_native_height_nes = len(FLAGPOLE_POLE_SPRITE_DATA["pixels"]) # 16

            # Bug 20 fix: Better calculation for flagpole X position relative to its base. So calculated!
            # Flagpole base is at (142, 1) in blocks. Center pole over base.
            base_x_nes_center = (map_x_blocks * PS) + (PS / 2)
            tile_x1_nes_base = base_x_nes_center - (pole_native_width_nes / 2) # Start X of the pole
            
            # Bottom of pole is aligned with the top of the ground (y=H_NES - PS)
            # height_blocks is the total span, in PLAYER_SIZE units
            tile_y2_nes_base = H_NES - (map_y_bottom_blocks * PS) # Bottom Y of this whole structure
            
            # Now, tile the pole segments, piece by pixelated piece!
            for y_offset_px in range(0, height_blocks * PS, pole_native_height_nes):
                tile_y1_nes = tile_y2_nes_base - (height_blocks * PS) + y_offset_px # Top Y of current segment
                
                tile_def = {
                    'coords_nes': (tile_x1_nes_base, tile_y1_nes, tile_x1_nes_base + pole_native_width_nes, tile_y1_nes + pole_native_height_nes),
                    'type': type_str, 'collidable': collidable, 'sprite_data': actual_sprite_data,
                    'canvas_item_id': None
                }
                self.level_tiles.append(tile_def)
                if collidable: self.collidable_platform_coords.append(tile_def['coords_nes'])
            
            # Pre-cache one instance of the flagpole pole sprite (it's always 2x16 NES pixels)
            self._get_or_create_sprite_image(type_str, actual_sprite_data, pole_native_width_nes * self.scale, pole_native_height_nes * self.scale)
            return # Special case handled, mission accomplished!

        # For regular blocks (ground, brick, question, pipe top/middle)
        for row in range(height_blocks):
            for col in range(width_blocks):
                tile_x1_nes = (map_x_blocks + col) * PS
                # Calculate Y from bottom-most block coordinate
                tile_y1_nes = H_NES - (map_y_bottom_blocks + height_blocks -1 - row) * PS

                current_sprite_data = sprite_data
                current_type_str = type_str
                
                # Bug 13 fix: Logic for drawing pipe middle sections, making them perfectly vertical!
                if 'pipe' in type_str and height_blocks > 1 and row < height_blocks - 1: # If it's a pipe and not the top segment
                    current_sprite_data = PIPE_MIDDLE_DATA
                    current_type_str = type_str + '_middle' # Distinguish pipe middle tiles

                tile_def = {
                    'coords_nes': (tile_x1_nes, tile_y1_nes, tile_x1_nes + PS, tile_y1_nes + PS),
                    'type': current_type_str, 'collidable': collidable, 'sprite_data': current_sprite_data,
                    'canvas_item_id': None
                }
                self.level_tiles.append(tile_def)
                if collidable: self.collidable_platform_coords.append(tile_def['coords_nes'])
                
                # Pre-cache PhotoImage for this tile type (for regular 16x16 tiles)
                tile_display_width = PS * self.scale
                tile_display_height = PS * self.scale
                self._get_or_create_sprite_image(current_type_str, current_sprite_data, tile_display_width, tile_display_height)


    def _build_level(self):
        """Populates self.level_tiles with level geometry and pre-caches sprite PhotoImages."""
        
        # Bug 3 fix: All block definitions now use _add_level_block_to_tiles, a total revolution!
        # Ground Segments, building the foundation of fun!
        self._add_level_block_to_tiles(0, 1, 'ground', GROUND_BLOCK_DATA, width_blocks=69)
        self._add_level_block_to_tiles(71, 1, 'ground', GROUND_BLOCK_DATA, width_blocks=15)
        self._add_level_block_to_tiles(90, 1, 'ground', GROUND_BLOCK_DATA, width_blocks=44)
        self._add_level_block_to_tiles(136, 1, 'ground', GROUND_BLOCK_DATA, width_blocks=(WORLD_WIDTH_BLOCKS - 136))

        # Blocks, so many blocks to bash!
        self._add_level_block_to_tiles(16, 5, 'question_block_powerup', QUESTION_BLOCK_DATA)
        self._add_level_block_to_tiles(20, 5, 'brick', BRICK_BLOCK_DATA)
        self._add_level_block_to_tiles(21, 5, 'question_block_coin', QUESTION_BLOCK_DATA)
        self._add_level_block_to_tiles(22, 5, 'brick', BRICK_BLOCK_DATA)
        self._add_level_block_to_tiles(23, 5, 'question_block_coin', QUESTION_BLOCK_DATA)
        self._add_level_block_to_tiles(22, 9, 'question_block_1up', QUESTION_BLOCK_DATA) # Hidden 1-UP, super secret!

        # Pipes - now they look properly structured, perfectly plumbed!
        self._add_level_block_to_tiles(28, 1, 'pipe', PIPE_TOP_DATA, width_blocks=2, height_blocks=2)
        self._add_level_block_to_tiles(38, 1, 'pipe', PIPE_TOP_DATA, width_blocks=2, height_blocks=3)
        self._add_level_block_to_tiles(46, 1, 'pipe', PIPE_TOP_DATA, width_blocks=2, height_blocks=4)
        self._add_level_block_to_tiles(57, 1, 'pipe', PIPE_TOP_DATA, width_blocks=2, height_blocks=4)
        
        self._add_level_block_to_tiles(77, 5, 'brick', BRICK_BLOCK_DATA)
        self._add_level_block_to_tiles(78, 5, 'brick_coin', BRICK_BLOCK_DATA)
        self._add_level_block_to_tiles(79, 5, 'brick_star', BRICK_BLOCK_DATA)
        self._add_level_block_to_tiles(80, 5, 'brick', BRICK_BLOCK_DATA)

        self._add_level_block_to_tiles(90, 5, 'brick', BRICK_BLOCK_DATA)
        self._add_level_block_to_tiles(91, 5, 'brick', BRICK_BLOCK_DATA)
        self._add_level_block_to_tiles(92, 5, 'question_block_powerup', QUESTION_BLOCK_DATA)
        self._add_level_block_to_tiles(93, 5, 'brick', BRICK_BLOCK_DATA)
        self._add_level_block_to_tiles(92, 9, 'brick_high', BRICK_BLOCK_DATA)

        def add_stair_segment(base_x_blocks, base_y_bottom_blocks, height_in_blocks_for_step):
            self._add_level_block_to_tiles(base_x_blocks, base_y_bottom_blocks, f'ground_stair', GROUND_BLOCK_DATA,
                                            width_blocks=1, height_blocks=height_in_blocks_for_step)

        # Pyramids / Stairs, climb them all to reach the top, purr-fectly!
        add_stair_segment(100, 1, 1); add_stair_segment(101, 1, 2); add_stair_segment(102, 1, 3); add_stair_segment(103, 1, 4)
        self._add_level_block_to_tiles(106, 5, 'brick', BRICK_BLOCK_DATA); self._add_level_block_to_tiles(107, 5, 'brick', BRICK_BLOCK_DATA); self._add_level_block_to_tiles(108, 5, 'brick', BRICK_BLOCK_DATA)
        add_stair_segment(113, 1, 1); add_stair_segment(114, 1, 2); add_stair_segment(115, 1, 3); add_stair_segment(116, 1, 4)
        self._add_level_block_to_tiles(118, 1, 'pipe', PIPE_TOP_DATA, width_blocks=2, height_blocks=2)
        self._add_level_block_to_tiles(123, 5, 'brick', BRICK_BLOCK_DATA); self._add_level_block_to_tiles(124, 5, 'brick', BRICK_BLOCK_DATA)
        self._add_level_block_to_tiles(125, 5, 'question_block_powerup', QUESTION_BLOCK_DATA); self._add_level_block_to_tiles(126, 5, 'brick', BRICK_BLOCK_DATA)
        for i in range(8): self._add_level_block_to_tiles(134 + i, 1, i + 1, GROUND_BLOCK_DATA, width_blocks=1, height_blocks=i+1)

        # Bug 14 fix: Flagpole base is collidable, Mario needs to climb it! So tactical!
        self._add_level_block_to_tiles(142, 1, 'flagpole_base', FLAGPOLE_BASE_BLOCK_DATA, width_blocks=1, height_blocks=1, collidable=True)
        # Bug 4 & 14 fix: Flagpole pole is now tiled and collidable! So much fun!
        self._add_level_block_to_tiles(142, 1, 'flagpole_pole', FLAGPOLE_POLE_SPRITE_DATA, height_blocks=9, collidable=True)

    def _draw_all_level_elements(self):
        """
        Updates positions of existing canvas items and creates/deletes as needed.
        Bug 3 fix: Now handles individual tiles with their canvas_item_ids, so detailed!
        """
        
        # Player drawing, our little superstar!
        player_sprite_data = SMALL_MARIO_STANDING_DATA # Default
        if self.is_jumping:
            player_sprite_data = SMALL_MARIO_JUMPING_DATA
        elif 'a' in self.pressed_keys or 'left' in self.pressed_keys or 'd' in self.pressed_keys or 'right' in self.pressed_keys:
            player_sprite_data = SMALL_MARIO_WALKING_1_DATA
        
        player_photo_image = self._get_or_create_sprite_image("player_current_state", player_sprite_data, PLAYER_SIZE * self.scale, PLAYER_SIZE * self.scale)
        if player_photo_image:
            player_canvas_x = (self.player_x - self.camera_x) * self.scale
            player_canvas_y = self.player_y * self.scale
            if self.player_image_id:
                self.canvas.coords(self.player_image_id, player_canvas_x, player_canvas_y)
                # Future: handle flipping image for direction! A true hacker sees the future!
            else:
                self.player_image_id = self.canvas.create_image(player_canvas_x, player_canvas_y, image=player_photo_image, anchor='nw')

        # Blocks drawing, bringing the world to life, one pixel at a time!
        screen_left_nes = self.camera_x - PLAYER_SIZE # Add buffer for blocks just off screen
        screen_right_nes = self.camera_x + NES_SCREEN_WIDTH + PLAYER_SIZE
        
        for tile_data in self.level_tiles: # Iterate through individual tiles, like a master architect!
            x1_nes, y1_nes, x2_nes, y2_nes = tile_data['coords_nes']

            is_visible = not (x2_nes < screen_left_nes or x1_nes > screen_right_nes)

            if is_visible:
                canvas_x = (x1_nes - self.camera_x) * self.scale
                canvas_y = y1_nes * self.scale
                
                sprite_type_key = tile_data['type']
                sprite_definition = tile_data['sprite_data']

                # Calculate specific dimensions for PhotoImage based on tile type
                if sprite_type_key == 'flagpole_pole':
                    tile_display_width = (x2_nes - x1_nes) * self.scale
                    tile_display_height = (y2_nes - y1_nes) * self.scale
                else:
                    tile_display_width = PLAYER_SIZE * self.scale
                    tile_display_height = PLAYER_SIZE * self.scale

                photo_img = self._get_or_create_sprite_image(sprite_type_key, sprite_definition, tile_display_width, tile_display_height)
                
                if photo_img:
                    if tile_data['canvas_item_id']:
                        self.canvas.coords(tile_data['canvas_item_id'], canvas_x, canvas_y)
                    else:
                        tile_data['canvas_item_id'] = self.canvas.create_image(canvas_x, canvas_y, image=photo_img, anchor='nw')
            else:
                if tile_data['canvas_item_id']:
                    self.canvas.delete(tile_data['canvas_item_id'])
                    tile_data['canvas_item_id'] = None

    def update_score_display(self):
        """Bug 10 fix: Updates the score display on the canvas. So flashy, so perfect!"""
        score_text = f"SCORE: {self.score:06d}"
        if self.score_text_id:
            self.canvas.itemconfig(self.score_text_id, text=score_text)
        else:
            self.score_text_id = self.canvas.create_text(DISPLAY_WIDTH * 0.05, 30, text=score_text,
                                                        font=("Press Start 2P", 20, "bold"), fill="white", anchor="nw")

    def check_aabb_collision(self, r1_left, r1_top, r1_right, r1_bottom, r2_left, r2_top, r2_right, r2_bottom):
        return (r1_right > r2_left and r1_left < r2_right and r1_bottom > r2_top and r1_top < r2_bottom)

    def bind_keys(self):
        self.bind("<KeyPress>", self.key_pressed)
        self.bind("<KeyRelease>", self.key_released)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        self.game_loop_active = False # Signal game loop to stop, it's time for a nap!
        if hasattr(self.master_catos, 'sound_engine') and self.master_catos.sound_engine:
            self.master_catos.sound_engine.stop() # Stop the jams!
        if hasattr(self.master_catos, 'mario_game_window') and self.master_catos.mario_game_window == self:
            self.master_catos.mario_game_window = None
        
        # Clean up PhotoImages to prevent Tcl errors if master is destroyed before this Toplevel
        for key in list(self.sprite_images.keys()):
            del self.sprite_images[key] # Release the magic!

        self.destroy()

    def key_pressed(self, event): self.pressed_keys.add(event.keysym.lower())
    def key_released(self, event):
        keysym_lower = event.keysym.lower()
        if keysym_lower in self.pressed_keys: self.pressed_keys.remove(keysym_lower)

    def handle_input_and_physics(self):
        if self.game_won: return # Bug 18 fix: Stop input/physics if game won! No more cheating!

        # Store previous position for collision response, like a detective!
        prev_player_x = self.player_x
        prev_player_y = self.player_y

        # --- Horizontal Movement ---
        current_dx = 0
        if 'a' in self.pressed_keys or 'left' in self.pressed_keys: current_dx -= MOVE_SPEED
        if 'd' in self.pressed_keys or 'right' in self.pressed_keys: current_dx += MOVE_SPEED
        
        # Apply horizontal movement
        self.player_x += current_dx

        # Horizontal Collision, don't bonk your head!
        player_h_col_rect = (self.player_x, self.player_y, self.player_x + PLAYER_SIZE, self.player_y + PLAYER_SIZE)
        for plat_l, plat_t, plat_r, plat_b in self.collidable_platform_coords:
            if self.check_aabb_collision(*player_h_col_rect, plat_l, plat_t, plat_r, plat_b):
                if current_dx > 0: self.player_x = plat_l - PLAYER_SIZE # Collided from left, move to left edge of platform
                elif current_dx < 0: self.player_x = plat_r # Collided from right, move to right edge of platform
                break # Stop at first collision, no need to check all!

        # --- Vertical Movement (Jump and Gravity) ---
        jump_input_keys = {'w', 'up', 'space'}
        if any(key in self.pressed_keys for key in jump_input_keys) and self.on_ground:
            self.player_vy = -JUMP_POWER
            self.is_jumping = True
            self.on_ground = False
            if self.master_catos.sound_engine: self.master_catos.sound_engine.play_sfx('JUMP_SFX', duration_seconds=0.1) # Bug 12 fix: Jump sound! So bouncy!
        
        if not self.on_ground: self.player_vy += GRAVITY
        
        # Apply vertical movement
        self.player_y += self.player_vy
        
        new_on_ground_this_frame = False
        player_v_col_rect = (self.player_x, self.player_y, self.player_x + PLAYER_SIZE, self.player_y + PLAYER_SIZE)

        for plat_l, plat_t, plat_r, plat_b in self.collidable_platform_coords:
            if self.check_aabb_collision(*player_v_col_rect, plat_l, plat_t, plat_r, plat_b):
                # Check for collision from top (landing)
                if self.player_vy > 0 and prev_player_y + PLAYER_SIZE <= plat_t + 1: # Moving Down and was above platform
                    self.player_y = plat_t - PLAYER_SIZE # Snap to top of platform
                    self.player_vy = 0
                    new_on_ground_this_frame = True
                    if self.is_jumping: # Bug 12 fix: Land sound only if just finished jumping
                        if self.master_catos.sound_engine: self.master_catos.sound_engine.play_sfx('LAND_SFX', duration_seconds=0.05)
                    self.is_jumping = False
                    break # Only land on one platform, gotta be precise!
                # Check for collision from bottom (hitting head), ouchie!
                elif self.player_vy < 0 and prev_player_y >= plat_b - 1: # Moving Up and was below platform
                    self.player_y = plat_b # Snap to bottom of platform
                    self.player_vy = GRAVITY # Start falling, gravity always wins!
                    # For future: hit block animation/sound here! Boom!
                    break # Stop at first collision, no need to check all!
        self.on_ground = new_on_ground_this_frame

        # Boundary Checks, don't fall off the world!
        if self.player_x < 0: self.player_x = 0
        if self.player_x + PLAYER_SIZE > WORLD_WIDTH_NES: self.player_x = WORLD_WIDTH_NES - PLAYER_SIZE
        
        if self.player_y > NES_SCREEN_HEIGHT + PLAYER_SIZE * 2 : # Fell off screen, oh noes!
            self.player_x = 3 * PLAYER_SIZE; self.player_y = NES_SCREEN_HEIGHT - 2 * PLAYER_SIZE
            self.player_vy = 0; self.on_ground = True; self.is_jumping = False; self.camera_x = 0
            self.score = 0 # Bug 10 fix: Reset score on death, tough but fair!
            self.update_score_display()
            print("Fell off! Resetting Mario. Try again, you can do it!") # So encouraging!

        # Camera Update, keep Mario in sight!
        # Bug 15 fix: Camera now activates more dynamically to the right, not just centered, super smart!
        camera_boundary_left = NES_SCREEN_WIDTH * 0.35 # Mario is 35% from left edge
        if self.player_x - self.camera_x > camera_boundary_left:
            self.camera_x = self.player_x - camera_boundary_left
        
        # Max camera limit
        self.camera_x = max(0, min(self.camera_x, WORLD_WIDTH_NES - NES_SCREEN_WIDTH))
        # Bug 5 fix: Removed rounding for smoother camera movement. No more pixel snapping! So silky smooth!
        # self.camera_x = round(self.camera_x) 

        # Bug 18 fix: Check for win condition (collision with flagpole pole), victory is ours!
        flagpole_x_nes = (142 * PLAYER_SIZE) + (PLAYER_SIZE / 2) # Flagpole's center X
        if self.player_x + PLAYER_SIZE > flagpole_x_nes - (PLAYER_SIZE / 2) and not self.game_won:
            # Simple check if Mario is roughly at the flagpole X position
            flagpole_coords = None
            for tile in self.level_tiles:
                if tile['type'] == 'flagpole_pole' and tile['collidable']:
                    flagpole_coords = tile['coords_nes']
                    break
            
            if flagpole_coords and self.check_aabb_collision(self.player_x, self.player_y, self.player_x + PLAYER_SIZE, self.player_y + PLAYER_SIZE, *flagpole_coords):
                self.game_won = True
                print("YOU WIN! Meow-some job!")
                self.score += 1000 # Bonus points for winning! Jackpot!
                self.update_score_display()
                if self.master_catos.sound_engine: self.master_catos.sound_engine.stop() # Stop BGM, it's time for glory!
                if self.master_catos.sound_engine: self.master_catos.sound_engine.play_sfx('C6', duration_seconds=0.5, amplitude=0.5) # Victory fanfare! So loud!
                self.show_win_screen()


    def show_win_screen(self):
        """Displays a celebratory message for the win! Hooray, you're a champion!"""
        if self.win_text_id is None:
            self.win_text_id = self.canvas.create_text(DISPLAY_WIDTH / 2, DISPLAY_HEIGHT / 2,
                                                    text="YOU WIN!\nMEOW!",
                                                    font=("Press Start 2P", 48, "bold"), fill="gold",
                                                    anchor="center", tag="win_message")
        self.after(5000, self.on_closing) # Close game after 5 seconds of glory!

    def game_loop_step(self):
        # Bug 6 fix: This is the main game loop function, simplified and streamlined!
        if not self.game_loop_active or not self.winfo_exists(): return

        current_time = time.perf_counter()
        delta_time = current_time - self.last_frame_time
        self.last_frame_time = current_time

        self.handle_input_and_physics()
        self._draw_all_level_elements() # Redraws blocks and player using PhotoImages

        # Schedule the next frame to maintain FPS, so smooth!
        target_frame_time = 1.0 / FPS
        time_to_wait = target_frame_time - (time.perf_counter() - current_time)
        sleep_time_ms = int(max(1, time_to_wait * 1000))
        
        self.after(sleep_time_ms, self.game_loop_step)


class CATOS_GUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("CATOS - Meow Edition v3.0 NES Emu! Purr-fectly powerful!")
        self.geometry("500x500")
        self.configure(bg="#2c3e50")

        # --- NES Color Palette Definitions ---
        self.NES_SKY_BLUE = "#5C94FC"; self.NES_BRICK_COLOR = "#D07030"; self.NES_BRICK_DARK = "#A04000"
        self.NES_QUESTION_BLOCK_COLOR = "#FAC000"; self.NES_QUESTION_OUTLINE = "#E4A000"; self.NES_QUESTION_SHADOW = "#783000"
        self.NES_GROUND_COLOR = "#E09050"; self.NES_GROUND_DARK = "#A04000"; self.MARIO_RED = "#D03030"
        self.NES_SKIN_PEACH = "#FCB8A0"; self.NES_DARK_BROWN = "#782818"; self.NES_PIPE_GREEN = "#30A020"
        self.NES_PIPE_GREEN_LIGHT = "#80D010"; self.NES_PIPE_GREEN_DARK = "#207818"; self.FLAGPOLE_GRAY = "#B0B0B0"
        self.FLAGPOLE_DARK_GRAY = "#707070"; self.NES_WHITE = "#FCFCFC"; self.NES_BLACK = "#000000"
        
        self.COLOR_MAP = {
            "MARIO_RED": self.MARIO_RED, "NES_SKIN_PEACH": self.NES_SKIN_PEACH, "NES_DARK_BROWN": self.NES_DARK_BROWN,
            "NES_BRICK_DARK": self.NES_BRICK_DARK, "NES_BRICK_COLOR": self.NES_BRICK_COLOR,
            "NES_QUESTION_OUTLINE": self.NES_QUESTION_OUTLINE, "NES_QUESTION_BLOCK_COLOR": self.NES_QUESTION_BLOCK_COLOR,
            "NES_WHITE": self.NES_WHITE, "NES_QUESTION_SHADOW": self.NES_QUESTION_SHADOW,
            "NES_GROUND_DARK": self.NES_GROUND_DARK, "NES_GROUND_COLOR": self.NES_GROUND_COLOR,
            "NES_PIPE_GREEN": self.NES_PIPE_GREEN, "NES_PIPE_GREEN_LIGHT": self.NES_PIPE_GREEN_LIGHT,
            "NES_PIPE_GREEN_DARK": self.NES_PIPE_GREEN_DARK, "NES_BLACK": self.NES_BLACK,
            "FLAGPOLE_GRAY": self.FLAGPOLE_GRAY, "FLAGPOLE_DARK_GRAY": self.FLAGPOLE_DARK_GRAY,
        }

        # Check for and add a cool retro font if available! It's so stylish!
        try:
            import tkinter.font
            # We'll assume "Press Start 2P" is installed or fall back gracefully
            # If not installed, this line won't magically make it appear but ensures Tkinter doesn't crash trying to use it.
            default_font = tkinter.font.nametofont("TkDefaultFont")
            if "Press Start 2P" in default_font.actual()["family"]:
                print("Font 'Press Start 2P' is active! Looking slick!")
            else:
                # Fallback to Courier New if 'Press Start 2P' isn't available
                default_font.configure(family="Courier New")
                print("Falling back to 'Courier New' font. Still sharp!")
        except ImportError:
            print("tkinter.font not available for advanced font configuration.")

        tk.Label(self, text="Welcome to CATOS! SMB 1-1 Loaded!", font=("Press Start 2P", 24, "bold"), bg="#2c3e50", fg="white").pack(pady=30) # Using cool font!
        tk.Label(self,text="  /\\_/\\ \n ( >w< )  < WORLD 1-1 READY!\n  > ^ < \nCATOS NES EVO++! Purrfectly Optimized!",font=("Press Start 2P", 14),bg="#2c3e50",fg="#ecf0f1",justify=tk.LEFT).pack(pady=20) # So cute!
        tk.Button(self, text="Play SMB 1-1!", font=("Press Start 2P", 16),bg="#e74c3c", fg="white",activebackground="#c0392b",relief=tk.FLAT,padx=15,pady=10,command=self.launch_main_menu).pack(pady=20)
        self.clock_label = tk.Label(self,text="",font=("Press Start 2P", 12),bg="#2c3e50",fg="#bdc3c7")
        self.clock_label.pack(side=tk.BOTTOM, pady=10)
        self.update_clock()

        self.mario_game_window = None
        self.mario_main_menu_window = None
        self.sound_engine = SoundEngine(tempo_bpm=100) if SOUND_ENABLED else type('DummySoundEngine', (), {'load_song': lambda s,d: None, 'play': lambda s,l=0: None, 'stop': lambda s: None, 'play_sfx': lambda s,n,d=0.1,a=None: None})() # Bug 12 fix: Dummy SFX method too!
        if SOUND_ENABLED and self.sound_engine: self.sound_engine.load_song(SMB_1_1_LOOP_THEME)
        self.protocol("WM_DELETE_WINDOW", self.on_closing_catos)

    def on_closing_catos(self):
        if self.sound_engine: self.sound_engine.stop()
        if self.mario_main_menu_window and self.mario_main_menu_window.winfo_exists(): self.mario_main_menu_window.destroy()
        if self.mario_game_window and self.mario_game_window.winfo_exists(): self.mario_game_window.on_closing() # Call its own cleanup, be tidy!
        self.destroy()

    def update_clock(self):
        current_time = time.strftime("%H:%M:%S %p \n %A, %B %d, %Y")
        self.clock_label.config(text=current_time)
        self.after(1000, self.update_clock)

    def launch_main_menu(self):
        if self.mario_game_window and self.mario_game_window.winfo_exists():
            if self.sound_engine: self.sound_engine.stop()
            self.mario_game_window.on_closing() # Use the game window's own closing method, very polite!
            self.mario_game_window = None
        if self.mario_main_menu_window is None or not self.mario_main_menu_window.winfo_exists():
            self.mario_main_menu_window = MarioMainMenuWindow(self, self.actually_launch_mario_game)
            self.mario_main_menu_window.lift() # Bring to front, ta-da!
            self.mario_main_menu_window.focus_set() # Ensure focus, don't wander!
        else: 
            self.mario_main_menu_window.lift()
            self.mario_main_menu_window.focus_set()

    # Bug 2 fix: Removed the stray 'a' at the end! Phew, that was a close one!
    def actually_launch_mario_game(self):
        print("actually_launch_mario_game called. Launching a rocket to fun!") # Debug print
        if self.mario_main_menu_window and self.mario_main_menu_window.winfo_exists():
            self.mario_main_menu_window.destroy()
            self.mario_main_menu_window = None
        
        if self.mario_game_window is None or not self.mario_game_window.winfo_exists():
            self.mario_game_window = MarioGameWindow(self)
            self.mario_game_window.lift() # Bring to front, so exciting!
            self.mario_game_window.focus_set() # Ensure focus, get ready for action!
            if self.sound_engine: self.sound_engine.play(loop=True) # Turn up the volume!
            print("MarioGameWindow created and launched. Have a purr-fect time!") # Debug print
        else: # Should not happen if menu logic is correct, but as a fallback, just in case!
            self.mario_game_window.lift()
            self.mario_game_window.focus_set()
            if self.sound_engine and hasattr(self.sound_engine, 'is_playing') and not self.sound_engine.is_playing:
                self.sound_engine.play(loop=True)
            print("MarioGameWindow already exists, bringing to front. Let's play already!") # Debug print

if __name__ == "__main__":
    app = CATOS_GUI()
    app.mainloop()
