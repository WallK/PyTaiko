import pyray as ray

from libs.global_objects import Indicator
from libs.utils import get_current_ms
from libs.texture import tex


class DevScreen:
    def __init__(self):
        self.width = 1280
        self.height = 720
        self.screen_init = False
        self.length = 100

    def on_screen_start(self):
        if not self.screen_init:
            self.screen_init = True
            tex.load_screen_textures('game')
            self.indicator = Indicator(Indicator.State.SELECT)

    def on_screen_end(self, next_screen: str):
        self.screen_init = False
        return next_screen

    def update(self):
        self.on_screen_start()
        self.indicator.update(get_current_ms())
        if ray.is_key_pressed(ray.KeyboardKey.KEY_ENTER):
            return self.on_screen_end('GAME')
        elif ray.is_key_pressed(ray.KeyboardKey.KEY_RIGHT):
            self.length += 1
            print(self.length)
        elif ray.is_key_pressed(ray.KeyboardKey.KEY_LEFT):
            self.length -= 1
            print(self.length)
        elif ray.is_key_pressed(ray.KeyboardKey.KEY_UP):
            self.length += 10
            print(self.length)
        elif ray.is_key_pressed(ray.KeyboardKey.KEY_DOWN):
            self.length -= 10
            print(self.length)

    def draw(self):
        ray.draw_rectangle(0, 0, 1280, 720, ray.GREEN)
        start_position = 100
        end_position = start_position + self.length
        color = ray.WHITE
        tex.draw_texture('notes', "8", frame=0, x=start_position+64, y=192, x2=self.length-47, color=color)
        tex.draw_texture('notes', "drumroll_tail", x=end_position+64, y=192, color=color)
        tex.draw_texture('notes', str(5), frame=0, x=start_position, y=192, color=color)

    def draw_3d(self):
        pass
