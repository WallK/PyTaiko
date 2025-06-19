import random
from pathlib import Path

import pyray as ray

from libs.animation import Animation
from libs.audio import audio
from libs.utils import (
    get_current_ms,
    global_data,
    is_l_don_pressed,
    is_r_don_pressed,
    load_all_textures_from_zip,
    load_texture_from_zip,
)
from libs.video import VideoPlayer


class State:
    OP_VIDEO = 0
    WARNING = 1
    ATTRACT_VIDEO = 2

class TitleScreen:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        video_dir = Path(global_data.config["paths"]["video_path"]) / "op_videos"
        self.op_video_list = [file for file in video_dir.glob("**/*.mp4")]
        video_dir = Path(global_data.config["paths"]["video_path"]) / "attract_videos"
        self.attract_video_list = [file for file in video_dir.glob("**/*.mp4")]
        self.load_sounds()
        self.screen_init = False
        self.fade_out = None

    def get_videos(self):
        return self.op_video, self.attract_video

    def load_sounds(self):
        sounds_dir = Path("Sounds")
        title_dir = sounds_dir / "title"
        self.sound_don = audio.load_sound(sounds_dir / "inst_00_don.wav")
        self.sound_bachi_swipe = audio.load_sound(title_dir / "SE_ATTRACT_2.ogg")
        self.sound_bachi_hit = audio.load_sound(title_dir / "SE_ATTRACT_3.ogg")
        self.sound_warning_message = audio.load_sound(title_dir / "VO_ATTRACT_3.ogg")
        self.sound_warning_error = audio.load_sound(title_dir / "SE_ATTRACT_1.ogg")
        self.sounds = [self.sound_bachi_swipe, self.sound_bachi_hit, self.sound_warning_message, self.sound_warning_error]

    def load_textures(self):
        self.textures = load_all_textures_from_zip(Path('Graphics/lumendata/attract/keikoku.zip'))
        self.texture_black = load_texture_from_zip(Path('Graphics/lumendata/attract/movie.zip'), 'movie_img00000.png')

    def on_screen_start(self):
        if not self.screen_init:
            self.screen_init = True
            self.load_textures()
            self.state = State.OP_VIDEO
            self.op_video = VideoPlayer(random.choice(self.op_video_list))
            self.attract_video = VideoPlayer(random.choice(self.attract_video_list))
            self.warning_board = None

    def on_screen_end(self) -> str:
        self.op_video.stop()
        self.attract_video.stop()
        for sound in self.sounds:
            if audio.is_sound_playing(sound):
                audio.stop_sound(sound)
        for zip in self.textures:
            for texture in self.textures[zip]:
                ray.unload_texture(texture)
        self.screen_init = False
        return "ENTRY"

    def scene_manager(self):
        if self.state == State.OP_VIDEO:
            if not self.op_video.is_started():
                self.op_video.start(get_current_ms())
            self.op_video.update()
            if self.op_video.is_finished():
                self.op_video.stop()
                self.op_video = VideoPlayer(random.choice(self.op_video_list))

                self.state = State.WARNING
                self.warning_board = WarningScreen(get_current_ms(), self)
        elif self.state == State.WARNING and self.warning_board is not None:
            self.warning_board.update(get_current_ms(), self)
            if self.warning_board.is_finished:
                self.state = State.ATTRACT_VIDEO
                self.attract_video.start(get_current_ms())
        elif self.state == State.ATTRACT_VIDEO:
            self.attract_video.update()
            if self.attract_video.is_finished():
                self.attract_video.stop()
                self.attract_video = VideoPlayer(random.choice(self.attract_video_list))

                self.state = State.OP_VIDEO
                self.op_video.start(get_current_ms())


    def update(self):
        self.on_screen_start()

        if self.fade_out is not None:
            self.fade_out.update(get_current_ms())
            if self.fade_out.is_finished:
                return self.on_screen_end()

        self.scene_manager()
        if is_l_don_pressed() or is_r_don_pressed():
            self.fade_out = Animation.create_fade(1000, initial_opacity=0.0, final_opacity=1.0)
            audio.play_sound(self.sound_don)

    def draw(self):
        if self.state == State.OP_VIDEO:
            self.op_video.draw()
        elif self.state == State.WARNING and self.warning_board is not None:
            bg_source = ray.Rectangle(0, 0, self.textures['keikoku'][0].width, self.textures['keikoku'][0].height)
            bg_dest = ray.Rectangle(0, 0, self.width, self.height)
            ray.draw_texture_pro(self.textures['keikoku'][0], bg_source, bg_dest, ray.Vector2(0,0), 0, ray.WHITE)
            self.warning_board.draw(self)
        elif self.state == State.ATTRACT_VIDEO:
            self.attract_video.draw()

        if self.fade_out is not None:
            src = ray.Rectangle(0, 0, self.texture_black.width, self.texture_black.height)
            dest = ray.Rectangle(0, 0, self.width, self.height)
            ray.draw_texture_pro(self.texture_black, src, dest, ray.Vector2(0, 0), 0, ray.fade(ray.WHITE, self.fade_out.attribute))

class WarningScreen:
    class X:
        DELAY = 4250
        def __init__(self):
            self.resize = Animation.create_texture_resize(166.67, initial_size=1.0, final_size=1.5, delay=self.DELAY, reverse_delay=0)
            self.fadein = Animation.create_fade(166.67, delay=self.DELAY, initial_opacity=0.0, final_opacity=1.0, reverse_delay=166.67)
            self.fadein_2 = Animation.create_fade(166.67, delay=self.DELAY + self.fadein.duration, initial_opacity=0.0, final_opacity=1.0)

            self.sound_played = False

        def update(self, current_ms: float, sound, elapsed_time):
            self.fadein.update(current_ms)
            self.fadein_2.update(current_ms)
            self.resize.update(current_ms)

            if self.DELAY + self.fadein.duration <= elapsed_time and not self.sound_played:
                audio.play_sound(sound)
                self.sound_played = True

        def draw(self, texture):
            scale = self.resize.attribute
            x_x = 150 + (texture.width//2) - ((texture.width * scale)//2)
            x_y = 200 + (texture.height//2) - ((texture.height * scale)//2)
            x_source = ray.Rectangle(0, 0, texture.width, texture.height)
            x_dest = ray.Rectangle(x_x, x_y, texture.width*scale, texture.height*scale)
            ray.draw_texture_pro(texture, x_source, x_dest, ray.Vector2(0,0), 0, ray.fade(ray.WHITE, self.fadein.attribute))

    class BachiHit:
        def __init__(self):
            self.resize = Animation.create_texture_resize(233.34, initial_size=0.5, final_size=1.5)
            self.fadein = Animation.create_fade(116.67, initial_opacity=0.0, final_opacity=1.0, reverse_delay=0)

            self.sound_played = False

        def update(self, current_ms: float, sound):
            if not self.sound_played:
                audio.play_sound(sound)
                self.sound_played = True
                self.resize.start_ms = current_ms
                self.fadein.start_ms = current_ms
            self.resize.update(current_ms)
            self.fadein.update(current_ms)

        def draw(self, texture):
            scale = self.resize.attribute
            hit_x = 350 + (texture.width//2) - ((texture.width * scale)//2)
            hit_y = 225 + (texture.height//2) - ((texture.height * scale)//2)
            hit_source = ray.Rectangle(0, 0, texture.width, texture.height)
            hit_dest = ray.Rectangle(hit_x, hit_y, texture.width*scale, texture.height*scale)
            ray.draw_texture_pro(texture, hit_source, hit_dest, ray.Vector2(0,0), 0, ray.fade(ray.WHITE, self.fadein.attribute))

    class Characters:
        def __init__(self, current_ms: float, start_ms: float):
            self.start_ms = start_ms
            self.current_ms = current_ms
            self.shadow_fade = Animation.create_fade(50, delay=16.67, initial_opacity=0.75)

            self.animation_sequence = [(300.00, 5, 4), (183.33, 6, 4), (166.67, 7, 4), (166.67, 8, 9), (166.67, 11, 9), (166.67, 12, 9), (166.67, 13, 9),
                     (166.67, 5, 4), (150.00, 5, 4), (133.34, 6, 4), (133.34, 7, 4), (133.34, 8, 9), (133.34, 11, 9), (133.34, 12, 9), (133.34, 13, 9),
                     (133.34, 5, 4), (116.67, 5, 4), (100.00, 6, 4), (100.00, 7, 4), (100.00, 8, 9), (100.00, 11, 9), (100.00, 12, 9), (100.00, 13, 9),
                     (100.00, 5, 4), (100.00, 5, 4), (83.330, 6, 4), (83.330, 7, 4), (83.330, 8, 9), (83.330, 11, 9), (83.330, 12, 9), (83.330, 13, 9),
                     (83.330, 5, 4), (83.330, 5, 4), (66.670, 6, 4), (66.670, 7, 4), (66.670, 8, 9), (66.670, 11, 9), (66.670, 12, 9), (66.670, 13, 9),
                     (66.670, 5, 4), (66.670, 5, 4), (66.670, 6, 4), (66.670, 7, 4), (66.670, 8, 9), (66.670, 11, 9), (66.670, 12, 9), (66.670, 13, 9),
                     (66.670, 5, 4), (66.670, 5, 4), (66.670, 6, 4), (66.670, 7, 4), (66.670, 8, 9), (66.670, 11, 9), (66.670, 12, 9), (66.670, 13, 9),
                     (66.670, 17, 16)]


            self.time = 0
            self.index_val = 0
            self.is_finished = False

        def character_index(self, index: int) -> int:
            elapsed_time = self.current_ms - self.start_ms
            delay = 566.67
            if self.index_val == len(self.animation_sequence)-1:
                return int(self.animation_sequence[len(self.animation_sequence)-1][index])
            elif elapsed_time <= delay:
                return int(self.animation_sequence[0][index])
            elif elapsed_time >= delay + self.time:
                new_index = self.animation_sequence[self.index_val][index]
                self.index_val += 1
                self.shadow_fade.start_ms = self.current_ms
                self.shadow_fade.duration = int(self.animation_sequence[self.index_val][0])
                self.time += self.animation_sequence[self.index_val][0]
                return int(new_index)
            else:
                return int(self.animation_sequence[self.index_val][index])

        def update(self, current_ms: float):
            self.shadow_fade.update(current_ms)
            self.current_ms = current_ms
            self.is_finished = True if self.character_index(1) == self.animation_sequence[-1][1] else False

        def draw(self, textures, fade: ray.Color, fade_2: ray.Color, y: int):
            ray.draw_texture(textures['keikoku'][2], 135, y+textures['keikoku'][4].height+110, fade_2)
            ray.draw_texture(textures['keikoku'][self.character_index(2)], 115, y+150, fade)

            ray.draw_texture(textures['keikoku'][3], 360, y+textures['keikoku'][5].height+60, fade_2)

            if 6 < self.character_index(1) < 17:
                ray.draw_texture(textures['keikoku'][self.character_index(1) - 1], 315, y+100, ray.fade(ray.WHITE, self.shadow_fade.attribute))
            ray.draw_texture(textures['keikoku'][self.character_index(1)], 315, y+100, fade)
            if self.character_index(1) == 17:
                ray.draw_texture(textures['keikoku'][19], 350, y+135, ray.WHITE)

    class Board:
        def __init__(self, screen_width, screen_height, texture):
            #Move warning board down from top of screen
            self.move_down = Animation.create_move(266.67, total_distance=screen_height + ((screen_height - texture.height)//2) + 20, start_position=-720)

            #Move warning board up a little bit
            self.move_up = Animation.create_move(116.67, start_position=92 + 20, delay=self.move_down.duration, total_distance =-30)

            #And finally into its correct position
            self.move_center = Animation.create_move(116.67, start_position=82, delay=self.move_down.duration + self.move_up.duration, total_distance=10)
            self.y_pos = 0

        def update(self, current_ms):
            self.move_down.update(current_ms)
            self.move_up.update(current_ms)
            self.move_center.update(current_ms)
            if self.move_up.is_finished:
                self.y_pos = int(self.move_center.attribute)
            elif self.move_down.is_finished:
                self.y_pos = int(self.move_up.attribute)
            else:
                self.y_pos = int(self.move_down.attribute)

        def draw(self, texture):
            ray.draw_texture(texture, 0, self.y_pos, ray.WHITE)


    def __init__(self, current_ms: float, title_screen: TitleScreen):
        self.start_ms = current_ms

        self.fade_in = Animation.create_fade(300, delay=266.67, initial_opacity=0.0, final_opacity=1.0)
        self.fade_out = Animation.create_fade(500, delay=1000, initial_opacity=0.0, final_opacity=1.0)

        self.board = self.Board(title_screen.width, title_screen.height, title_screen.textures['keikoku'][1])
        self.warning_x = self.X()
        self.warning_bachi_hit = self.BachiHit()
        self.characters = self.Characters(current_ms, self.start_ms)

        self.source_rect = ray.Rectangle(0, 0, title_screen.texture_black.width, title_screen.texture_black.height)
        self.dest_rect = ray.Rectangle(0, 0, title_screen.width, title_screen.height)

        self.is_finished = False

    def update(self, current_ms: float, title_screen: TitleScreen):
        self.board.update(current_ms)
        self.fade_in.update(current_ms)
        self.fade_out.update(current_ms)
        delay = 566.67
        elapsed_time = current_ms - self.start_ms
        self.warning_x.update(current_ms, title_screen.sound_warning_error, elapsed_time)
        self.characters.update(current_ms)

        if self.characters.is_finished:
            self.warning_bachi_hit.update(current_ms, title_screen.sound_bachi_hit)
        else:
            self.fade_out.delay = elapsed_time + 500
            if delay <= elapsed_time and not audio.is_sound_playing(title_screen.sound_bachi_swipe):
                audio.play_sound(title_screen.sound_warning_message)
                audio.play_sound(title_screen.sound_bachi_swipe)

        self.is_finished = self.fade_out.is_finished

    def draw(self, title_screen: TitleScreen):
        fade = ray.fade(ray.WHITE, self.fade_in.attribute)
        fade_2 = ray.fade(ray.WHITE, self.fade_in.attribute if self.fade_in.attribute < 0.75 else 0.75)
        self.board.draw(title_screen.textures['keikoku'][1])
        ray.draw_texture(title_screen.textures['keikoku'][15], 150, 200, ray.fade(ray.WHITE, self.warning_x.fadein_2.attribute))

        self.characters.draw(title_screen.textures, fade, fade_2, self.board.y_pos)

        self.warning_x.draw(title_screen.textures['keikoku'][14])

        self.warning_bachi_hit.draw(title_screen.textures['keikoku'][18])

        ray.draw_texture_pro(title_screen.texture_black, self.source_rect, self.dest_rect, ray.Vector2(0,0), 0, ray.fade(ray.WHITE, self.fade_out.attribute))
