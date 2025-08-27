import pyray as ray

from libs.texture import tex
from libs.utils import get_current_ms
from scenes.song_select import ScoreHistory


class DevScreen:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.screen_init = False

    def on_screen_start(self):
        if not self.screen_init:
            self.screen_init = True


    def on_screen_end(self, next_screen: str):
        self.screen_init = False
        return next_screen

    def update(self):
        self.on_screen_start()
        if ray.is_key_pressed(ray.KeyboardKey.KEY_ENTER):
            return self.on_screen_end('GAME')

    def draw(self):
        pass

    def draw_3d(self):
        pass
