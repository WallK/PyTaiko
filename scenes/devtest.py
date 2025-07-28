import pyray as ray

from libs.utils import get_current_ms, is_l_don_pressed, is_r_don_pressed
from scenes.song_select import Transition


class DevScreen:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.screen_init = False
        self.transition = Transition(self.height, 'TRIPLE HELIX', 'Yonokid')

    def on_screen_start(self):
        if not self.screen_init:
            self.screen_init = True

    def on_screen_end(self, next_screen: str):
        self.screen_init = False
        return next_screen

    def update(self):
        self.on_screen_start()
        self.transition.update(get_current_ms())

        if is_l_don_pressed() or is_r_don_pressed():
            self.transition = Transition(self.height, 'TRIPLE HELIX', 'Yonokid')

        if ray.is_key_pressed(ray.KeyboardKey.KEY_ENTER):
            return self.on_screen_end('GAME')

    def draw(self):
        self.transition.draw(self.height)

    def draw_3d(self):
       pass
