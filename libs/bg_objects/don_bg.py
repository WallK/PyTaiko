from libs.texture import TextureWrapper


class DonBG:

    @staticmethod
    def create(tex: TextureWrapper, index: int, player_num: int, path: str = 'background'):
        map = [DonBG1, DonBG2, DonBG3, DonBG4, DonBG5, DonBG6]
        selected_obj = map[index]
        return selected_obj(tex, index, player_num, path)

class DonBGBase:
    def __init__(self, tex: TextureWrapper, index: int, player_num: int, path: str):
        self.name = f'{index}_{player_num}'
        tex.load_zip(path, f'donbg/{self.name}')
        self.move = tex.get_animation(0)
        self.is_clear = False
        self.clear_fade = tex.get_animation(1)

    def update(self, current_time_ms: float, is_clear: bool):
        if not self.is_clear and is_clear:
            self.clear_fade.start()
        self.is_clear = is_clear
        self.move.update(current_time_ms)
        self.clear_fade.update(current_time_ms)

class DonBG1(DonBGBase):
    def __init__(self, tex: TextureWrapper, index: int, player_num: int, path: str):
        super().__init__(tex, index, player_num, path)
        self.overlay_move = tex.get_animation(2)
    def update(self, current_time_ms: float, is_clear: bool):
        super().update(current_time_ms, is_clear)
        self.overlay_move.update(current_time_ms)
    def draw(self, tex: TextureWrapper, y: float=0):
        self._draw_textures(tex, 1.0, y)
        if self.is_clear:
            self._draw_textures(tex, self.clear_fade.attribute, y)
    def _draw_textures(self, tex: TextureWrapper, fade: float, y: float):
        for i in range(5):
            tex.draw_texture(self.name, 'background', frame=self.is_clear, fade=fade, x=(i*328)+self.move.attribute, y=y)
        for i in range(6):
            tex.draw_texture(self.name, 'overlay', frame=self.is_clear, fade=fade, x=(i*347)+self.move.attribute*(347/328), y=self.overlay_move.attribute+y)
        for i in range(30):
            tex.draw_texture(self.name, 'footer', frame=self.is_clear, fade=fade, x=(i*56)+self.move.attribute*((56/328)*3), y=self.overlay_move.attribute+y)

class DonBG2(DonBGBase):
    def __init__(self, tex: TextureWrapper, index: int, player_num: int, path: str):
        super().__init__(tex, index, player_num, path)
        self.overlay_move = tex.get_animation(3)
    def update(self, current_time_ms: float, is_clear: bool):
        super().update(current_time_ms, is_clear)
        self.overlay_move.update(current_time_ms)
    def draw(self, tex: TextureWrapper, y: float = 0):
        self._draw_textures(tex, 1.0, y)
        if self.is_clear:
            self._draw_textures(tex, self.clear_fade.attribute, y)
    def _draw_textures(self, tex: TextureWrapper, fade: float, y: float):
        for i in range(5):
            tex.draw_texture(self.name, 'background', frame=self.is_clear, fade=fade, x=(i*328)+self.move.attribute, y=y)
            tex.draw_texture(self.name, 'overlay', frame=self.is_clear, fade=fade, x=(i*328)+self.move.attribute, y=self.overlay_move.attribute+y)

class DonBG3(DonBGBase):
    def __init__(self, tex: TextureWrapper, index: int, player_num: int, path: str):
        super().__init__(tex, index, player_num, path)
        self.bounce_up = tex.get_animation(4)
        self.bounce_down = tex.get_animation(5)
        self.bounce_up.start()
        self.bounce_down.start()
        self.overlay_move = tex.get_animation(6)
        self.overlay_move_2 = tex.get_animation(7)

    def update(self, current_time_ms: float, is_clear: bool):
        super().update(current_time_ms, is_clear)
        self.bounce_up.update(current_time_ms)
        self.bounce_down.update(current_time_ms)
        if self.bounce_down.is_finished:
            self.bounce_up.restart()
            self.bounce_down.restart()
        self.overlay_move.update(current_time_ms)
        self.overlay_move_2.update(current_time_ms)

    def draw(self, tex: TextureWrapper, y: float = 0):
        self._draw_textures(tex, 1.0, y)
        if self.is_clear:
            self._draw_textures(tex, self.clear_fade.attribute, y)

    def _draw_textures(self, tex: TextureWrapper, fade: float, y: float):
        for i in range(10):
            tex.draw_texture(self.name, 'background', frame=self.is_clear, fade=fade, x=(i*164)+self.move.attribute, y=y)
        y_pos = self.bounce_up.attribute - self.bounce_down.attribute + self.overlay_move.attribute + self.overlay_move_2.attribute
        for i in range(6):
            tex.draw_texture(self.name, 'overlay', frame=self.is_clear, fade=fade, x=(i*328)+(self.move.attribute*2), y=y_pos+y)

class DonBG4(DonBGBase):
    def __init__(self, tex: TextureWrapper, index: int, player_num: int, path: str):
        super().__init__(tex, index, player_num, path)
        self.overlay_move = tex.get_animation(2)
    def update(self, current_time_ms: float, is_clear: bool):
        super().update(current_time_ms, is_clear)
        self.overlay_move.update(current_time_ms)
    def draw(self, tex: TextureWrapper, y: float = 0):
        self._draw_textures(tex, 1.0, y)
        if self.is_clear:
            self._draw_textures(tex, self.clear_fade.attribute, y)

    def _draw_textures(self, tex: TextureWrapper, fade: float, y: float):
        for i in range(5):
            tex.draw_texture(self.name, 'background', frame=self.is_clear, fade=fade, x=(i*328)+self.move.attribute, y=y)
            tex.draw_texture(self.name, 'overlay', frame=self.is_clear, fade=fade, x=(i*328)+self.move.attribute, y=self.overlay_move.attribute+y)

class DonBG5(DonBGBase):
    def __init__(self, tex: TextureWrapper, index: int, player_num: int, path: str):
        super().__init__(tex, index, player_num, path)
        self.bounce_up = tex.get_animation(4)
        self.bounce_down = tex.get_animation(5)
        self.bounce_up.start()
        self.bounce_down.start()
        self.adjust = tex.get_animation(8)

    def update(self, current_time_ms: float, is_clear: bool):
        super().update(current_time_ms, is_clear)
        self.bounce_up.update(current_time_ms)
        self.bounce_down.update(current_time_ms)
        if self.bounce_down.is_finished:
            self.bounce_up.restart()
            self.bounce_down.restart()
        self.adjust.update(current_time_ms)

    def draw(self, tex: TextureWrapper, y: float = 0):
        self._draw_textures(tex, 1.0, y)
        if self.is_clear:
            self._draw_textures(tex, self.clear_fade.attribute, y)

    def _draw_textures(self, tex: TextureWrapper, fade: float, y: float):
        for i in range(5):
            tex.draw_texture(self.name, 'background', frame=self.is_clear, fade=fade, x=(i*328)+self.move.attribute, y=y)
        for i in range(6):
            tex.draw_texture(self.name, 'overlay', frame=self.is_clear, fade=fade, x=(i*368)+(self.move.attribute * ((184/328)*2)), y=self.bounce_up.attribute - self.bounce_down.attribute - self.adjust.attribute + y)

class DonBG6(DonBGBase):
    def __init__(self, tex: TextureWrapper, index: int, player_num: int, path: str):
        super().__init__(tex, index, player_num, path)
        self.overlay_move = tex.get_animation(2)
    def update(self, current_time_ms: float, is_clear: bool):
        super().update(current_time_ms, is_clear)
        self.overlay_move.update(current_time_ms)
    def draw(self, tex: TextureWrapper, y: float = 0):
        self._draw_textures(tex, 1.0, y)
        if self.is_clear:
            self._draw_textures(tex, self.clear_fade.attribute, y)

    def _draw_textures(self, tex: TextureWrapper, fade: float, y: float):
        for i in range(5):
            tex.draw_texture(self.name, 'background', frame=self.is_clear, fade=fade, x=(i*328)+self.move.attribute, y=y)
        for i in range(0, 6, 2):
            tex.draw_texture(self.name, 'overlay_1', frame=self.is_clear, fade=fade, x=(i*264) + self.move.attribute*3, y=-self.move.attribute*0.85+y)
        for i in range(5):
            tex.draw_texture(self.name, 'overlay_2', frame=self.is_clear, fade=fade, x=(i*328)+self.move.attribute, y=self.overlay_move.attribute+y)
