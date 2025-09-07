import random

from libs.animation import Animation
from libs.texture import TextureWrapper

class Dancer:

    @staticmethod
    def create(tex: TextureWrapper, index: int, bpm: float):
        map = [DancerGroup0, DancerGroup0, DancerGroup0, DancerGroup1, DancerGroup2, DancerGroup3,
                DancerGroup4, DancerGroup5, DancerGroup6, DancerGroup7, DancerGroup8, DancerGroup9,
                DancerGroup10, DancerGroup11, DancerGroup12, DancerGroup13, DancerGroup14, DancerGroup15,
                DancerGroup16, DancerGroup17, DancerGroup18]
        selected_obj = map[index]
        return selected_obj(tex, index, bpm)

class BaseDancer:
    def __init__(self, name: str, index: int, bpm: float):
        self.name = name
        self.index = index
        self.bpm = bpm
        self.keyframes = []
        self.start_keyframes = []
        self.is_started = False

    def keyframe(self):
        duration = (60000 / self.bpm) / 2
        self.total_duration = duration * len(self.keyframes)
        self.textures = [(duration*i, duration*(i+1), index) for i, index in enumerate(self.keyframes)]
        self.texture_change = Animation.create_texture_change(self.total_duration, textures=self.textures)
        self.texture_change.start()

    def start(self):
        self.is_started = True

        duration = (60000 / self.bpm)
        self.s_bounce_up = Animation.create_move(duration/2, start_position=-200, total_distance=350, ease_out='quadratic', delay=500)
        self.s_bounce_down = Animation.create_move(duration/2, total_distance=140, ease_in='quadratic', delay=self.s_bounce_up.duration + 500)
        self.start_textures = [((duration / len(self.start_keyframes))*i, (duration / len(self.start_keyframes))*(i+1), index) for i, index in enumerate(self.start_keyframes)]
        self.s_texture_change = Animation.create_texture_change(duration, textures=self.start_textures, delay=500)
        self.s_texture_change.start()
        self.s_bounce_up.start()
        self.s_bounce_down.start()

    def update(self, current_time_ms: float, bpm: float):
        self.texture_change.update(current_time_ms)
        if self.is_started:
            self.s_texture_change.update(current_time_ms)
            self.s_bounce_up.update(current_time_ms)
            self.s_bounce_down.update(current_time_ms)
        if bpm != self.bpm:
            self.bpm = bpm
            duration = (60000 / bpm) / 2
            self.total_duration = duration * len(self.keyframes)
            self.textures = [(duration*i, duration*(i+1), index) for i, index in enumerate(self.keyframes)]
            self.texture_change.duration = self.total_duration
            self.texture_change.textures = self.textures
        if self.texture_change.is_finished:
            self.texture_change.restart()

    def draw(self, tex: TextureWrapper, x: int):
        if not self.is_started:
            return
        if not self.s_texture_change.is_finished:
            tex.draw_texture(self.name, str(self.index) + '_start', frame=self.s_texture_change.attribute, x=x, y=-self.s_bounce_up.attribute + self.s_bounce_down.attribute)
        else:
            tex.draw_texture(self.name, str(self.index) + '_loop', frame=self.texture_change.attribute, x=x)

class Dancer0_0(BaseDancer):
    def __init__(self, name: str, index: int, bpm: float):
        super().__init__(name, index, bpm)
        self.start_keyframes = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 3, 4]
        self.keyframes = [0, 1, 2, 1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 7, 6, 7, 8, 5, 9, 4, 10, 4, 9, 4, 10, 4, 9, 11, 12, 13, 12, 11, 12, 13, 12, 11, 9, 4, 10, 4, 9, 4, 10, 4, 9, 11, 12, 13, 12, 11, 12, 13, 12, 11]

class Dancer0_1(BaseDancer):
    def __init__(self, name: str, index: int, bpm: float):
        super().__init__(name, index, bpm)
        self.start_keyframes = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 3, 4]
        self.keyframes = [0, 1, 2, 1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 7, 6, 7, 8, 5, 9, 4, 10, 4, 9, 4, 10, 4, 9, 11, 12, 13, 12, 11, 12, 13, 12, 11, 9, 4, 10, 4, 9, 4, 10, 4, 9, 11, 12, 13, 12, 11, 12, 13, 12, 11]

class Dancer0_2(BaseDancer):
    def __init__(self, name: str, index: int, bpm: float):
        super().__init__(name, index, bpm)
        self.start_keyframes = [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2]
        self.keyframes = [0, 1, 2, 1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 7, 6, 7, 8, 5, 9, 10, 11, 10, 9, 10, 11, 10, 9, 12, 13, 14, 13, 12, 13, 14, 13, 12, 9, 10, 11, 10, 9, 10, 11, 10, 9, 12, 13, 14, 13, 12, 13, 14, 13, 12]

class Dancer0_3(BaseDancer):
    def __init__(self, name: str, index: int, bpm: float):
        super().__init__(name, index, bpm)
        self.start_keyframes = [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2]
        self.keyframes = [0, 1, 2, 1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 7, 6, 7, 8, 5, 9, 10, 11, 10, 9, 10, 11, 10, 9, 12, 13, 14, 13, 12, 13, 14, 13, 12, 9, 10, 11, 10, 9, 10, 11, 10, 9, 12, 13, 14, 13, 12, 13, 14, 13, 12]

class Dancer0_4(BaseDancer):
    def __init__(self, name: str, index: int, bpm: float):
        super().__init__(name, index, bpm)
        self.keyframes = [0, 1, 2, 1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 7, 6, 7, 8, 5, 9, 10, 11, 10, 9, 10, 11, 10, 9, 12, 13, 14, 13, 12, 13, 14, 13, 12, 9, 10, 11, 10, 9, 10, 11, 10, 9, 12, 13, 14, 13, 12, 13, 14, 13, 12]
        self.start_keyframes = [0, 0, 0, 0, 1, 2, 2, 3, 4, 4, 5, 5, 5, 6, 6]
        duration = (60000 / bpm) / 2
        self.bounce_up = Animation.create_move(duration, total_distance=20, ease_out='quadratic', delay=duration*2)
        self.bounce_down = Animation.create_move(duration, total_distance=20, ease_in='quadratic', delay=duration*2+self.bounce_up.duration)
        self.bounce_up.start()
        self.bounce_down.start()

    def update(self, current_time_ms: float, bpm: float):
        super().update(current_time_ms, bpm)
        self.bounce_up.update(current_time_ms)
        self.bounce_down.update(current_time_ms)
        if self.bounce_down.is_finished:
            self.bounce_up.restart()
            self.bounce_down.restart()

    def draw(self, tex: TextureWrapper, x: int):
        if not self.is_started:
            return
        if not self.s_texture_change.is_finished:
            tex.draw_texture(self.name, '4_start', frame=7, x=x, y=-50-self.s_bounce_up.attribute + self.s_bounce_down.attribute)
            tex.draw_texture(self.name, '4_start', frame=self.s_texture_change.attribute, x=x, y=-self.s_bounce_up.attribute + self.s_bounce_down.attribute)
        else:
            if 0 <= self.texture_change.attribute <= 3:
                tex.draw_texture(self.name, '4_loop', frame=15, x=x, y=-self.bounce_up.attribute + self.bounce_down.attribute)
            elif 5 <= self.texture_change.attribute <= 8:
                tex.draw_texture(self.name, '4_loop', frame=17, x=x, y=-self.bounce_up.attribute + self.bounce_down.attribute)
            elif self.texture_change.attribute == 4:
                tex.draw_texture(self.name, '4_loop', frame=16, x=x, y=-self.bounce_up.attribute + self.bounce_down.attribute)
            tex.draw_texture(self.name, '4_loop', frame=self.texture_change.attribute, x=x)

class Dancer1_0(BaseDancer):
    def __init__(self, name: str, index: int, bpm: float):
        super().__init__(name, index, bpm)
        self.start_keyframes = [0, 1, 1, 2, 2, 3, 4, 4, 5, 5, 6, 6, 7, 7, 8, 8, 9, 9, 10, 10, 11, 11]
        self.keyframes = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0]

class Dancer2_0(BaseDancer):
    def __init__(self, name: str, index: int, bpm: float):
        super().__init__(name, index, bpm)
        self.start_keyframes = [0, 1, 1, 2, 2, 3, 4, 4, 5, 5, 6, 6, 7, 7, 8, 8, 9, 9, 10, 10, 11, 11]
        self.keyframes = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

class Dancer3_0(BaseDancer):
    def __init__(self, name: str, index: int, bpm: float):
        super().__init__(name, index, bpm)
        self.start_keyframes = [0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7, 8, 8]
        self.keyframes = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]

class Dancer4_0(BaseDancer):
    def __init__(self, name: str, index: int, bpm: float):
        super().__init__(name, index, bpm)
        self.start_keyframes = [0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7, 8, 8]
        self.keyframes = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]

class Dancer5_0(BaseDancer):
    def __init__(self, name: str, index: int, bpm: float):
        super().__init__(name, index, bpm)
        self.start_keyframes = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 3, 4]
        self.keyframes = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
        duration = (60000 / self.bpm)
        poof_keyframes = [((duration / 7)*i, (duration / 7)*(i+1), i) for i in range(7)]
        self.poof_texture_change = Animation.create_texture_change(duration, textures=poof_keyframes, delay=250)
        self.poof_texture_change.start()

    def update(self, current_time_ms: float, bpm: float):
        super().update(current_time_ms, bpm)
        self.poof_texture_change.update(current_time_ms)

    def draw(self, tex: TextureWrapper, x: int):
        super().draw(tex, x)
        if not self.poof_texture_change.is_finished:
            tex.draw_texture(self.name, 'poof', x=x, frame=self.poof_texture_change.attribute)

class Dancer6_0(BaseDancer):
    def __init__(self, name: str, index: int, bpm: float):
        super().__init__(name, index, bpm)
        self.start_keyframes = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 3, 4]
        self.keyframes = [0, 1, 2, 3, 2, 1, 0, 4, 5, 6, 5, 4, 0, 1, 2, 3, 2, 1, 2, 3, 0, 4, 5, 6, 5, 4, 5, 6, 0]
        duration = (60000 / self.bpm)
        poof_keyframes = [((duration / 7)*i, (duration / 7)*(i+1), i) for i in range(7)]
        self.poof_texture_change = Animation.create_texture_change(duration, textures=poof_keyframes, delay=250)
        self.poof_texture_change.start()

    def update(self, current_time_ms: float, bpm: float):
        super().update(current_time_ms, bpm)
        self.poof_texture_change.update(current_time_ms)

    def draw(self, tex: TextureWrapper, x: int):
        super().draw(tex, x)
        if not self.poof_texture_change.is_finished:
            tex.draw_texture(self.name, 'poof', x=x, frame=self.poof_texture_change.attribute)

class Dancer7_0(BaseDancer):
    def __init__(self, name: str, index: int, bpm: float):
        super().__init__(name, index, bpm)
        self.start_keyframes = [0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6]
        self.keyframes = [0, 1, 0, 1, 0, 2, 3, 4, 0, 1, 0, 1, 0, 5, 6, 7]

class Dancer8_0(BaseDancer):
    def __init__(self, name: str, index: int, bpm: float):
        super().__init__(name, index, bpm)
        self.start_keyframes = [0, 0, 1, 1, 2, 2, 3, 3]
        self.keyframes = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]

class Dancer9_0(BaseDancer):
    def __init__(self, name: str, index: int, bpm: float):
        super().__init__(name, index, bpm)
        self.start_keyframes = [0, 0, 1, 1, 2, 2, 3, 3]
        self.keyframes = [i for i in range(21)]

class Dancer10_0(BaseDancer):
    def __init__(self, name: str, index: int, bpm: float):
        super().__init__(name, index, bpm)
        self.start_keyframes = [0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5]
        self.keyframes = [0, 1, 2, 3, 4, 5, 4, 6, 7, 8]
        duration = (60000 / self.bpm)
        poof_keyframes = [((duration / 7)*i, (duration / 7)*(i+1), i) for i in range(7)]
        self.poof_texture_change = Animation.create_texture_change(duration, textures=poof_keyframes, delay=250)
        self.poof_texture_change.start()

    def update(self, current_time_ms: float, bpm: float):
        super().update(current_time_ms, bpm)
        self.poof_texture_change.update(current_time_ms)

    def draw(self, tex: TextureWrapper, x: int):
        super().draw(tex, x)
        if not self.poof_texture_change.is_finished:
            tex.draw_texture(self.name, str(self.index) + '_poof', x=x, frame=self.poof_texture_change.attribute)

class Dancer11_0(BaseDancer):
    def __init__(self, name: str, index: int, bpm: float):
        super().__init__(name, index, bpm)
        self.start_keyframes = [0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5]
        self.keyframes = [0, 1, 2, 3, 4, 5, 6, 5, 6, 4, 7, 8, 9, 10, 11, 3, 12, 13]
        duration = (60000 / self.bpm)
        poof_keyframes = [((duration / 7)*i, (duration / 7)*(i+1), i) for i in range(7)]
        self.poof_texture_change = Animation.create_texture_change(duration, textures=poof_keyframes, delay=250)
        self.poof_texture_change.start()

    def update(self, current_time_ms: float, bpm: float):
        super().update(current_time_ms, bpm)
        self.poof_texture_change.update(current_time_ms)

    def draw(self, tex: TextureWrapper, x: int):
        super().draw(tex, x)
        if not self.poof_texture_change.is_finished:
            tex.draw_texture(self.name, str(self.index) + '_poof', x=x, frame=self.poof_texture_change.attribute)

class Dancer12_0(BaseDancer):
    def __init__(self, name: str, index: int, bpm: float):
        super().__init__(name, index, bpm)
        self.start_keyframes = [0, 1, 2, 3]
        self.keyframes = [0, 1, 2, 3, 4, 5, 4, 3, 2, 1, 0, 1, 2, 3, 4, 5, 4, 3, 2, 1, 0, 1, 2, 3, 4, 5, 4, 3, 2, 1, 0, 1, 2, 3, 4, 5, 4, 3, 2, 1,
            7, 8, 7, 8, 7, 8, 7, 8, 7, 8, 7, 8, 9, 10, 11, 12, 13, 7,
            14, 15, 16, 17, 18, 19, 20, 19, 18, 17, 16, 15, 14, 15, 16, 17, 18, 19, 20, 19, 18, 17, 16, 15, 14, 15, 16, 17, 18, 19, 20, 19, 18, 17, 16, 15,
            14, 15, 16, 17, 18, 19, 20, 19, 18, 17, 16, 15]

class Dancer13_0(BaseDancer):
    def __init__(self, name: str, index: int, bpm: float):
        super().__init__(name, index, bpm)
        self.start_keyframes = [0, 1, 2, 3, 4, 5]
        self.keyframes = [i for i in range(20)]

class Dancer14_0(BaseDancer):
    def __init__(self, name: str, index: int, bpm: float):
        super().__init__(name, index, bpm)
        self.start_keyframes = [0]
        self.keyframes = [i for i in range(19)]
        duration = (60000 / self.bpm)
        poof_keyframes = [((duration / 7)*i, (duration / 7)*(i+1), i) for i in range(7)]
        self.poof_texture_change = Animation.create_texture_change(duration, textures=poof_keyframes, delay=250)
        self.poof_texture_change.start()

    def update(self, current_time_ms: float, bpm: float):
        super().update(current_time_ms, bpm)
        self.poof_texture_change.update(current_time_ms)

    def draw(self, tex: TextureWrapper, x: int):
        super().draw(tex, x)
        if not self.poof_texture_change.is_finished:
            tex.draw_texture(self.name, str(self.index) + '_poof', x=x, frame=self.poof_texture_change.attribute)

class Dancer15_0(BaseDancer):
    def __init__(self, name: str, index: int, bpm: float):
        super().__init__(name, index, bpm)
        self.start_keyframes = [0, 1, 2, 3, 4, 5]
        self.keyframes = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14,
            1, 2, 3, 4, 5, 6, 7, 16, 17, 18, 9, 10, 11, 12, 13, 14,
            1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14,
            1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14,
            20, 21, 22, 23, 24]

class Dancer16_0(BaseDancer):
    def __init__(self, name: str, index: int, bpm: float):
        super().__init__(name, index, bpm)
        self.start_keyframes = [0, 1, 2, 3]
        self.keyframes = [0, 1, 2, 3, 0, 1, 2, 3,
            4, 5, 6, 7, 8, 6, 7, 8, 9]

class Dancer17_0(BaseDancer):
    def __init__(self, name: str, index: int, bpm: float):
        super().__init__(name, index, bpm)
        self.start_keyframes = [0, 1, 2, 3]
        self.keyframes = [i for i in range(14)]

class Dancer18_0(BaseDancer):
    def __init__(self, name: str, index: int, bpm: float):
        super().__init__(name, index, bpm)
        self.start_keyframes = [0, 1, 2, 3, 4, 5]
        self.keyframes = [i for i in range(44)]

class BaseDancerGroup():
    def __init__(self, tex: TextureWrapper, index: int, bpm: float):
        self.name = 'dancer_' + str(index)
        self.active_count = 0
        tex.load_zip('background', f'dancer/{self.name}')
        self.dancers = []
        # Define spawn positions: center (2), left (1), right (3), far left (0), far right (4)
        self.spawn_positions = [2, 1, 3, 0, 4]
        self.active_dancers = [None] * 5

    def add_dancer(self):
        if self.active_count < len(self.dancers) and self.active_count < len(self.spawn_positions):
            position = self.spawn_positions[self.active_count]
            dancer = self.dancers[self.active_count]
            self.active_dancers[position] = dancer
            dancer.start()
            self.active_count += 1

    def update(self, current_time_ms: float, bpm: float):
        for dancer in self.dancers:
            dancer.update(current_time_ms, bpm)

    def draw(self, tex: TextureWrapper):
        for i, dancer in enumerate(self.active_dancers):
            if dancer is not None:
                dancer.draw(tex, 100 + i * 210)

class DancerGroup0(BaseDancerGroup):
    def __init__(self, tex: TextureWrapper, index: int, bpm: float):
        super().__init__(tex, index, bpm)
        self.dancers = [Dancer0_0(self.name, 0, bpm), Dancer0_1(self.name, 1, bpm),
                       Dancer0_2(self.name, 2, bpm), Dancer0_3(self.name, 3, bpm),
                       Dancer0_4(self.name, 4, bpm)]
        random.shuffle(self.dancers)
        for dancer in self.dancers:
            dancer.keyframe()
        self.add_dancer()

class DancerGroup1(BaseDancerGroup):
    def __init__(self, tex: TextureWrapper, index: int, bpm: float):
        super().__init__(tex, index, bpm)
        dancer_classes = [Dancer1_0]
        self.dancers = []
        for i in range(5):
            DancerClass = random.choice(dancer_classes)
            dancer = DancerClass(self.name, i % 3, bpm)
            self.dancers.append(dancer)

        random.shuffle(self.dancers)

        for dancer in self.dancers:
            dancer.keyframe()
        self.add_dancer()

class DancerGroup2(BaseDancerGroup):
    def __init__(self, tex: TextureWrapper, index: int, bpm: float):
        super().__init__(tex, index, bpm)
        dancer_classes = [Dancer2_0]
        self.dancers = []
        for i in range(5):
            DancerClass = random.choice(dancer_classes)
            dancer = DancerClass(self.name, i % 3, bpm)
            self.dancers.append(dancer)

        random.shuffle(self.dancers)

        for dancer in self.dancers:
            dancer.keyframe()
        self.add_dancer()

class DancerGroup3(BaseDancerGroup):
    def __init__(self, tex: TextureWrapper, index: int, bpm: float):
        super().__init__(tex, index, bpm)
        dancer_classes = [Dancer3_0]
        self.dancers = []
        for i in range(5):
            DancerClass = random.choice(dancer_classes)
            dancer = DancerClass(self.name, i % 4, bpm)
            self.dancers.append(dancer)

        random.shuffle(self.dancers)

        for dancer in self.dancers:
            dancer.keyframe()
        self.add_dancer()

class DancerGroup4(BaseDancerGroup):
    def __init__(self, tex: TextureWrapper, index: int, bpm: float):
        super().__init__(tex, index, bpm)
        dancer_classes = [Dancer4_0]
        self.dancers = []
        for i in range(5):
            DancerClass = random.choice(dancer_classes)
            dancer = DancerClass(self.name, i % 4, bpm)
            self.dancers.append(dancer)

        random.shuffle(self.dancers)

        for dancer in self.dancers:
            dancer.keyframe()
        self.add_dancer()

class DancerGroup5(BaseDancerGroup):
    def __init__(self, tex: TextureWrapper, index: int, bpm: float):
        super().__init__(tex, index, bpm)
        dancer_classes = [Dancer5_0]
        self.dancers = []
        for i in range(5):
            DancerClass = random.choice(dancer_classes)
            dancer = DancerClass(self.name, i % 2, bpm)
            self.dancers.append(dancer)

        random.shuffle(self.dancers)

        for dancer in self.dancers:
            dancer.keyframe()
        self.add_dancer()

class DancerGroup6(BaseDancerGroup):
    def __init__(self, tex: TextureWrapper, index: int, bpm: float):
        super().__init__(tex, index, bpm)
        dancer_classes = [Dancer6_0]
        self.dancers = []
        for i in range(5):
            DancerClass = random.choice(dancer_classes)
            dancer = DancerClass(self.name, i % 2, bpm)
            self.dancers.append(dancer)

        random.shuffle(self.dancers)

        for dancer in self.dancers:
            dancer.keyframe()
        self.add_dancer()

class DancerGroup7(BaseDancerGroup):
    def __init__(self, tex: TextureWrapper, index: int, bpm: float):
        super().__init__(tex, index, bpm)
        dancer_classes = [Dancer7_0]
        self.dancers = []
        for i in range(5):
            DancerClass = random.choice(dancer_classes)
            dancer = DancerClass(self.name, i % 4, bpm)
            self.dancers.append(dancer)

        random.shuffle(self.dancers)

        for dancer in self.dancers:
            dancer.keyframe()
        self.add_dancer()

class DancerGroup8(BaseDancerGroup):
    def __init__(self, tex: TextureWrapper, index: int, bpm: float):
        super().__init__(tex, index, bpm)
        dancer_classes = [Dancer8_0]
        self.dancers = []
        for i in range(5):
            DancerClass = random.choice(dancer_classes)
            dancer = DancerClass(self.name, i % 4, bpm)
            self.dancers.append(dancer)

        random.shuffle(self.dancers)

        for dancer in self.dancers:
            dancer.keyframe()
        self.add_dancer()

class DancerGroup9(BaseDancerGroup):
    def __init__(self, tex: TextureWrapper, index: int, bpm: float):
        super().__init__(tex, index, bpm)
        dancer_classes = [Dancer9_0]
        self.dancers = []
        for i in range(5):
            DancerClass = random.choice(dancer_classes)
            dancer = DancerClass(self.name, i % 3, bpm)
            self.dancers.append(dancer)

        random.shuffle(self.dancers)

        for dancer in self.dancers:
            dancer.keyframe()
        self.add_dancer()

class DancerGroup10(BaseDancerGroup):
    def __init__(self, tex: TextureWrapper, index: int, bpm: float):
        super().__init__(tex, index, bpm)
        dancer_classes = [Dancer10_0]
        self.dancers = []
        for i in range(5):
            DancerClass = random.choice(dancer_classes)
            dancer = DancerClass(self.name, i % 4, bpm)
            self.dancers.append(dancer)

        random.shuffle(self.dancers)

        for dancer in self.dancers:
            dancer.keyframe()
        self.add_dancer()

class DancerGroup11(BaseDancerGroup):
    def __init__(self, tex: TextureWrapper, index: int, bpm: float):
        super().__init__(tex, index, bpm)
        dancer_classes = [Dancer11_0]
        self.dancers = []
        for i in range(5):
            DancerClass = random.choice(dancer_classes)
            dancer = DancerClass(self.name, i % 3, bpm)
            self.dancers.append(dancer)

        random.shuffle(self.dancers)

        for dancer in self.dancers:
            dancer.keyframe()
        self.add_dancer()

class DancerGroup12(BaseDancerGroup):
    def __init__(self, tex: TextureWrapper, index: int, bpm: float):
        super().__init__(tex, index, bpm)
        dancer_classes = [Dancer12_0]
        self.dancers = []
        for i in range(5):
            DancerClass = random.choice(dancer_classes)
            dancer = DancerClass(self.name, i % 3, bpm)
            self.dancers.append(dancer)

        random.shuffle(self.dancers)

        for dancer in self.dancers:
            dancer.keyframe()
        self.add_dancer()

class DancerGroup13(BaseDancerGroup):
    def __init__(self, tex: TextureWrapper, index: int, bpm: float):
        super().__init__(tex, index, bpm)
        dancer_classes = [Dancer13_0]
        self.dancers = []
        for i in range(5):
            DancerClass = random.choice(dancer_classes)
            dancer = DancerClass(self.name, i % 3, bpm)
            self.dancers.append(dancer)

        random.shuffle(self.dancers)

        for dancer in self.dancers:
            dancer.keyframe()
        self.add_dancer()

class DancerGroup14(BaseDancerGroup):
    def __init__(self, tex: TextureWrapper, index: int, bpm: float):
        super().__init__(tex, index, bpm)
        dancer_classes = [Dancer14_0]
        self.dancers = []
        for i in range(5):
            DancerClass = random.choice(dancer_classes)
            dancer = DancerClass(self.name, i % 4, bpm)
            self.dancers.append(dancer)

        random.shuffle(self.dancers)

        for dancer in self.dancers:
            dancer.keyframe()
        self.add_dancer()

class DancerGroup15(BaseDancerGroup):
    def __init__(self, tex: TextureWrapper, index: int, bpm: float):
        super().__init__(tex, index, bpm)
        dancer_classes = [Dancer15_0]
        self.dancers = []
        for i in range(5):
            DancerClass = random.choice(dancer_classes)
            dancer = DancerClass(self.name, i % 3, bpm)
            self.dancers.append(dancer)

        random.shuffle(self.dancers)

        for dancer in self.dancers:
            dancer.keyframe()
        self.add_dancer()

class DancerGroup16(BaseDancerGroup):
    def __init__(self, tex: TextureWrapper, index: int, bpm: float):
        super().__init__(tex, index, bpm)
        dancer_classes = [Dancer16_0]
        self.dancers = []
        for i in range(5):
            DancerClass = random.choice(dancer_classes)
            dancer = DancerClass(self.name, i % 4, bpm)
            self.dancers.append(dancer)

        random.shuffle(self.dancers)

        for dancer in self.dancers:
            dancer.keyframe()
        self.add_dancer()

class DancerGroup17(BaseDancerGroup):
    def __init__(self, tex: TextureWrapper, index: int, bpm: float):
        super().__init__(tex, index, bpm)
        dancer_classes = [Dancer17_0]
        self.dancers = []
        for i in range(5):
            DancerClass = random.choice(dancer_classes)
            dancer = DancerClass(self.name, i % 4, bpm)
            self.dancers.append(dancer)

        random.shuffle(self.dancers)

        for dancer in self.dancers:
            dancer.keyframe()
        self.add_dancer()

class DancerGroup18(BaseDancerGroup):
    def __init__(self, tex: TextureWrapper, index: int, bpm: float):
        super().__init__(tex, index, bpm)
        dancer_classes = [Dancer18_0]
        self.dancers = []
        for i in range(5):
            DancerClass = random.choice(dancer_classes)
            dancer = DancerClass(self.name, i % 2, bpm)
            self.dancers.append(dancer)

        random.shuffle(self.dancers)

        for dancer in self.dancers:
            dancer.keyframe()
        self.add_dancer()
