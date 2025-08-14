import pyray as ray

from libs.texture import tex
from libs.utils import (
    get_current_ms,
    is_l_don_pressed,
    is_l_kat_pressed,
    is_r_don_pressed,
    is_r_kat_pressed,
)
from scenes.game import KusudamaAnimation


class DevScreen:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.screen_init = False

    def on_screen_start(self):
        if not self.screen_init:
            self.screen_init = True
            tex.load_screen_textures('game')
            self.kusudama = None
            self.count = 0

    def on_screen_end(self, next_screen: str):
        self.screen_init = False
        return next_screen

    def update(self):
        self.on_screen_start()
        if self.kusudama is not None:
            self.kusudama.update(get_current_ms(), self.count == 100)
            if self.kusudama.is_finished:
                self.kusudama = None
        if is_l_kat_pressed() or is_r_kat_pressed():
            self.kusudama = KusudamaAnimation(100)
            self.count = 0

        if is_l_don_pressed() or is_r_don_pressed():
            if self.kusudama is not None:
                self.count += 1
                self.kusudama.update_count(self.count)

        if ray.is_key_pressed(ray.KeyboardKey.KEY_ENTER):
            return self.on_screen_end('RESULT')

    def draw(self):
        if self.kusudama is not None:
            self.kusudama.draw()

    def draw_3d(self):
        pass
