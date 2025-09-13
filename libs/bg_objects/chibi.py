import random
from libs.animation import Animation, get_current_ms
from libs.texture import TextureWrapper

import pyray as ray

class Chibi:

    @staticmethod
    def create(index: int, bpm: float, bad: bool, tex: TextureWrapper):
        if bad:
            return ChibiBad(index, bpm, tex)
        map = [Chibi0, BaseChibi, Chibi2, BaseChibi, Chibi4, Chibi5, BaseChibi,
        BaseChibi, Chibi8, BaseChibi, BaseChibi, BaseChibi, BaseChibi, Chibi13]
        selected_obj = map[index]
        return selected_obj(index, bpm, tex)

class BaseChibi:
    def __init__(self, index: int, bpm: float, tex: TextureWrapper):
        self.name = 'chibi_' + str(index)
        self.bpm = bpm
        self.hori_move = Animation.create_move(60000 / self.bpm * 5, total_distance=1280)
        self.hori_move.start()
        self.vert_move = Animation.create_move(60000 / self.bpm / 2, total_distance=50, reverse_delay=0)
        self.vert_move.start()
        self.index = random.randint(0, len([item for item in tex.textures[self.name] if item[0].isdigit()])-1)
        tex_list = tex.textures[self.name][str(self.index)].texture
        keyframe_len = tex_list if isinstance(tex_list, list) else [0]
        self.keyframes = [i for i in range(len(keyframe_len))]
        duration = (60000 / self.bpm) / 2
        textures = [((duration / len(self.keyframes))*i, (duration / len(self.keyframes))*(i+1), index) for i, index in enumerate(self.keyframes)]
        self.texture_change = Animation.create_texture_change(duration, textures=textures)
        self.texture_change.start()

    def update(self, current_time_ms: float):
        self.hori_move.update(current_time_ms)
        self.vert_move.update(current_time_ms)
        if self.vert_move.is_finished:
            self.vert_move.restart()
        self.texture_change.update(current_time_ms)
        if self.texture_change.is_finished:
            self.texture_change.restart()

    def draw(self, tex: TextureWrapper):
        tex.draw_texture(self.name, str(self.index), frame=self.texture_change.attribute, x=self.hori_move.attribute, y=-self.vert_move.attribute)

class ChibiBad(BaseChibi):
    def __init__(self, index: int, bpm: float, tex: TextureWrapper):
        self.bpm = bpm
        self.index = random.randint(0, 2)
        self.keyframes = [3, 4]
        duration = (60000 / self.bpm) / 2
        self.hori_move = Animation.create_move(duration * 10, total_distance=1280)
        self.hori_move.start()
        self.vert_move = Animation.create_move(duration, total_distance=50, reverse_delay=0)
        self.vert_move.start()
        self.fade_in = Animation.create_fade(duration, initial_opacity=0.0, final_opacity=1.0)
        self.fade_in.start()
        s_keyframes = [0, 1, 2]
        textures = [((duration / len(s_keyframes))*i, (duration / len(s_keyframes))*(i+1), index) for i, index in enumerate(s_keyframes)]
        self.s_texture_change = Animation.create_texture_change(duration, textures=textures)
        self.s_texture_change.start()
        duration *= 2
        textures = [((duration / len(self.keyframes))*i, (duration / len(self.keyframes))*(i+1), index) for i, index in enumerate(self.keyframes)]
        self.texture_change = Animation.create_texture_change(duration, textures=textures)
        self.texture_change.start()

    def update(self, current_time_ms: float):
        super().update(current_time_ms)
        self.s_texture_change.update(current_time_ms)
        self.fade_in.update(current_time_ms)

    def draw(self, tex: TextureWrapper):
        if not self.s_texture_change.is_finished:
            tex.draw_texture('chibi_bad', '0', frame=self.s_texture_change.attribute, x=self.hori_move.attribute, y=self.vert_move.attribute, fade=self.fade_in.attribute)
        else:
            tex.draw_texture('chibi_bad', '0', frame=self.texture_change.attribute, x=self.hori_move.attribute, y=self.vert_move.attribute)

class Chibi0(BaseChibi):
    def draw(self, tex: TextureWrapper):
        tex.draw_texture(self.name, str(self.index), frame=self.texture_change.attribute, x=self.hori_move.attribute, y=self.vert_move.attribute)

class Chibi2(BaseChibi):
    def __init__(self, index: int, bpm: float, tex: TextureWrapper):
        super().__init__(index, bpm, tex)
        self.rotate = Animation.create_move(60000 / self.bpm / 2, total_distance=360, reverse_delay=0)
        self.rotate.start()

    def update(self, current_time_ms: float):
        super().update(current_time_ms)
        self.rotate.update(current_time_ms)
        if self.rotate.is_finished:
            self.rotate.restart()

    def draw(self, tex: TextureWrapper):
        origin = ray.Vector2(64, 64)
        tex.draw_texture(self.name, str(self.index), x=self.hori_move.attribute+origin.x, y=origin.y, origin=origin, rotation=self.rotate.attribute)

class Chibi4(BaseChibi):
    def draw(self, tex: TextureWrapper):
        tex.draw_texture(self.name, str(self.index), frame=self.texture_change.attribute, x=self.hori_move.attribute)

class Chibi5(BaseChibi):
    def draw(self, tex: TextureWrapper):
        tex.draw_texture(self.name, str(self.index), frame=self.texture_change.attribute, x=self.hori_move.attribute)

class Chibi8(BaseChibi):
    def draw(self, tex: TextureWrapper):
        tex.draw_texture(self.name, str(self.index), frame=self.texture_change.attribute, x=self.hori_move.attribute)

class Chibi13(BaseChibi):
    def __init__(self, index: int, bpm: float, tex: TextureWrapper):
        super().__init__(index, bpm, tex)
        duration = (60000 / self.bpm)
        self.scale = Animation.create_fade(duration, initial_opacity=1.0, final_opacity=0.75, delay=duration, reverse_delay=duration)
        self.scale.start()
        self.frame = 0

    def update(self, current_time_ms: float):
        super().update(current_time_ms)
        self.scale.update(current_time_ms)
        if self.scale.is_finished:
            self.scale.restart()
        if self.scale.attribute == 0.75:
            self.frame = 1
        else:
            self.frame = 0

    def draw(self, tex: TextureWrapper):
        tex.draw_texture(self.name, 'tail', frame=self.frame, x=self.hori_move.attribute, y=-self.vert_move.attribute)
        if self.scale.attribute == 0.75:
            tex.draw_texture(self.name, str(self.index), frame=self.frame, x=self.hori_move.attribute, y=-self.vert_move.attribute)
        else:
            tex.draw_texture(self.name, str(self.index), scale=self.scale.attribute, center=True, frame=self.frame, x=self.hori_move.attribute, y=-self.vert_move.attribute)


class ChibiController:
    def __init__(self, tex: TextureWrapper, index: int, bpm: float, path: str = 'background'):
        self.chibis = set()
        self.tex = tex
        self.index = index
        print(self.index)
        self.name = 'chibi_' + str(index)
        self.bpm = bpm
        tex.load_zip(path, f'chibi/{self.name}')
        tex.load_zip('background', 'chibi/chibi_bad')

    def add_chibi(self, bad=False):
        self.chibis.add(Chibi.create(self.index, self.bpm, bad, self.tex))

    def update(self, current_time_ms: float, bpm: float):
        self.bpm = bpm
        remove = set()
        for chibi in self.chibis:
            chibi.update(current_time_ms)
            if chibi.hori_move.is_finished:
                remove.add(chibi)

        for chibi in remove:
            self.chibis.remove(chibi)

    def draw(self):
        for chibi in self.chibis:
            chibi.draw(self.tex)
