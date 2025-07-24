import threading

import pyray as ray

from libs.song_hash import build_song_hashes
from libs.utils import global_data
from scenes.song_select import SongSelectScreen


class LoadScreen:
    def __init__(self, width: int, height: int, song_select_screen: SongSelectScreen):
        self.width = width
        self.height = height
        self.screen_init = False
        self.songs_loaded = False
        self.navigator_started = False
        self.loading_complete = False
        self.song_select_screen = song_select_screen

        # Progress bar settings
        self.progress_bar_width = width * 0.6
        self.progress_bar_height = 20
        self.progress_bar_x = (width - self.progress_bar_width) // 2
        self.progress_bar_y = height * 0.7

        # Thread references
        self.loading_thread = None
        self.navigator_thread = None

    def _load_song_hashes(self):
        """Background thread function to load song hashes"""
        try:
            global_data.song_hashes = build_song_hashes()
            self.songs_loaded = True
        except Exception as e:
            print(f"Error loading song hashes: {e}")
            self.songs_loaded = True

    def _load_navigator(self):
        """Background thread function to load navigator"""
        try:
            self.song_select_screen.load_navigator()
            self.loading_complete = True
        except Exception as e:
            print(f"Error loading navigator: {e}")
            self.loading_complete = True

    def on_screen_start(self):
        if not self.screen_init:
            self.loading_thread = threading.Thread(target=self._load_song_hashes)
            self.loading_thread.daemon = True
            self.loading_thread.start()
            self.screen_init = True

    def on_screen_end(self, next_screen: str):
        self.screen_init = False

        if self.loading_thread and self.loading_thread.is_alive():
            self.loading_thread.join(timeout=1.0)
        if self.navigator_thread and self.navigator_thread.is_alive():
            self.navigator_thread.join(timeout=1.0)

        return next_screen

    def update(self):
        self.on_screen_start()

        if self.songs_loaded and not self.navigator_started:
            self.navigator_thread = threading.Thread(target=self._load_navigator)
            self.navigator_thread.daemon = True
            self.navigator_thread.start()
            self.navigator_started = True

        if self.loading_complete:
            return self.on_screen_end('TITLE')

    def draw(self):
        ray.draw_rectangle(0, 0, self.width, self.height, ray.BLACK)

        # Draw progress bar background
        ray.draw_rectangle(
            int(self.progress_bar_x),
            int(self.progress_bar_y),
            int(self.progress_bar_width),
            int(self.progress_bar_height),
            ray.DARKGRAY
        )

        # Draw progress bar fill
        progress = max(0.0, min(1.0, global_data.song_progress))
        fill_width = self.progress_bar_width * progress
        if fill_width > 0:
            ray.draw_rectangle(
                int(self.progress_bar_x),
                int(self.progress_bar_y),
                int(fill_width),
                int(self.progress_bar_height),
                ray.RED
            )

        # Draw border
        ray.draw_rectangle_lines(
            int(self.progress_bar_x),
            int(self.progress_bar_y),
            int(self.progress_bar_width),
            int(self.progress_bar_height),
            ray.WHITE
        )
