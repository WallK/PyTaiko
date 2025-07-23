import pyray as ray

from libs.utils import OutlinedText, get_current_ms


class DevScreen:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.screen_init = False

        self.time_now = get_current_ms()
        self.test = OutlinedText('Triple Helix', 40, ray.Color(255, 255, 255, 255), ray.Color(101, 0, 82, 255), outline_thickness=4, vertical=True)

    def on_screen_start(self):
        if not self.screen_init:
            self.screen_init = True

    def on_screen_end(self, next_screen: str):
        self.screen_init = False
        return next_screen

    def update(self):
        self.on_screen_start()
        if ray.is_key_pressed(ray.KeyboardKey.KEY_ENTER):
            return self.on_screen_end('TITLE')

    def draw(self):
        ray.draw_rectangle(0, 0, self.width, self.height, ray.WHITE)
        src = ray.Rectangle(0, 0, self.test.texture.width, self.test.texture.height)
        dest = ray.Rectangle(self.width//2 - self.test.texture.width//2, self.height//2 - self.test.texture.height//2, self.test.texture.width, self.test.texture.height)
        self.test.draw(src, dest, ray.Vector2(0, 0), 0, ray.WHITE)
