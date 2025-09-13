import random
from libs.bg_objects.bg_fever import BGFeverBase
from libs.bg_objects.bg_normal import BGNormalBase
from libs.bg_objects.chibi import ChibiController
from libs.bg_objects.dancer import BaseDancer, BaseDancerGroup
from libs.bg_objects.fever import Fever3
from libs.bg_objects.footer import Footer
from libs.bg_objects.renda import RendaController
from libs.texture import TextureWrapper
from libs.bg_objects.don_bg import DonBG4


class Background:
    def __init__(self, tex: TextureWrapper, player_num: int, bpm: float):
        self.tex_wrapper = tex
        path = 'background/collab/animal'
        self.max_dancers = 5
        self.don_bg = DonBG4(self.tex_wrapper, 4, player_num, 'background')
        self.bg_normal = BGNormal(self.tex_wrapper, 0, path)
        self.bg_fever = BGFever(self.tex_wrapper, 0, path)
        self.footer = Footer(self.tex_wrapper, 0, path)
        self.fever = Fever3(self.tex_wrapper, 0, bpm, path)
        self.dancer = DancerGroup(self.tex_wrapper, 0, bpm, self.max_dancers, path)
        self.renda = RendaController(self.tex_wrapper, 0, path)
        self.chibi = ChibiController(self.tex_wrapper, 0, bpm, path)

class DancerGroup(BaseDancerGroup):
    def __init__(self, tex: TextureWrapper, index: int, bpm: float, max_dancers: int, path: str):
        self.name = 'dancer_' + str(index)
        self.active_count = 0
        tex.load_zip(path, f'dancer/{self.name}')
        self.spawn_positions = [2, 1, 3, 0, 4]
        self.active_dancers = [None] * max_dancers
        self.dancers = [BaseDancer(self.name, i, bpm, tex) for i in range(max_dancers)]
        random.shuffle(self.dancers)
        self.add_dancer()

class BGNormal(BGNormalBase):
    def update(self, current_time_ms: float):
        pass

    def draw(self, tex: TextureWrapper):
        tex.draw_texture(self.name, 'background')

class BGFever(BGFeverBase):
    def start(self):
        self.transitioned = True
    def update(self, current_time_ms: float):
        pass
    def draw(self, tex: TextureWrapper):
        tex.draw_texture(self.name, 'background')
