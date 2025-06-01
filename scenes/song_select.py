import sqlite3
from pathlib import Path
from typing import Optional

import pyray as ray

from libs import song_hash
from libs.animation import Animation
from libs.audio import audio
from libs.tja import TJAParser
from libs.utils import (
    OutlinedText,
    get_config,
    get_current_ms,
    global_data,
    load_all_textures_from_zip,
    session_data,
)


class SongSelectScreen:
    BOX_CENTER = 444
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_init = False
        self.root_dir = get_config()["paths"]["tja_path"]
        self.screen_width = screen_width
        self.screen_height = screen_height

        self.navigator = FileNavigator(self.root_dir)

    def load_textures(self):
        self.textures = load_all_textures_from_zip(Path('Graphics/lumendata/song_select.zip'))
        self.textures['custom'] = [ray.load_texture('1.png'), ray.load_texture('2.png')]

    def load_sounds(self):
        sounds_dir = Path("Sounds")
        self.sound_don = audio.load_sound(sounds_dir / "inst_00_don.wav")
        self.sound_kat = audio.load_sound(sounds_dir / "inst_00_katsu.wav")
        self.sound_skip = audio.load_sound(sounds_dir / 'song_select' / 'Skip.ogg')
        #self.sound_select = audio.load_sound(sounds_dir / "song_select.wav")
        #self.sound_cancel = audio.load_sound(sounds_dir / "cancel.wav")

    def on_screen_start(self):
        if not self.screen_init:
            self.load_textures()
            self.load_sounds()
            self.selected_song = None
            self.selected_difficulty = 0
            self.game_transition = None
            self.move_away = Animation.create_move(float('inf'))
            self.diff_fade_out = Animation.create_fade(0, final_opacity=1.0)
            self.background_move = Animation.create_move(15000, start_position=0, total_distance=1280)
            self.state = "BROWSING"
            self.text_fade_out = None
            self.text_fade_in = None
            self.texture_index = 784
            self.last_texture_index = 784
            self.background_fade_change = None
            self.demo_song = None
            for item in self.navigator.items:
                item.box.reset()
            self.navigator.get_current_item().box.get_scores()
            self.screen_init = True

    def on_screen_end(self):
        self.screen_init = False
        global_data.selected_song = self.navigator.get_current_item().path
        session_data.selected_difficulty = self.selected_difficulty
        self.reset_demo_music()
        for zip in self.textures:
            for texture in self.textures[zip]:
                ray.unload_texture(texture)
        return "GAME"

    def reset_demo_music(self):
        if self.demo_song is not None:
            audio.stop_music_stream(self.demo_song)
            audio.unload_music_stream(self.demo_song)
        self.demo_song = None
        self.navigator.get_current_item().box.wait = get_current_ms()
    def handle_input(self):
        if self.state == "BROWSING":
            # Up/Down navigation
            keys = get_config()["keybinds"]["left_kat"]
            for key in keys:
                if ray.is_key_pressed(ord(key)):
                    self.reset_demo_music()
                    self.navigator.navigate_left()
                    audio.play_sound(self.sound_kat)

            keys = get_config()["keybinds"]["right_kat"]
            for key in keys:
                if ray.is_key_pressed(ord(key)):
                    self.reset_demo_music()
                    self.navigator.navigate_right()
                    audio.play_sound(self.sound_kat)
            if ray.is_key_pressed(ray.KeyboardKey.KEY_LEFT_CONTROL):
                self.reset_demo_music()
                self.wait = get_current_ms()
                for i in range(10):
                    self.navigator.navigate_left()
                audio.play_sound(self.sound_skip)

            if ray.is_key_pressed(ray.KeyboardKey.KEY_RIGHT_CONTROL):
                self.reset_demo_music()
                for i in range(10):
                    self.navigator.navigate_right()
                audio.play_sound(self.sound_skip)

            # Select/Enter
            keys = get_config()["keybinds"]["left_don"] + get_config()["keybinds"]["right_don"]
            for key in keys:
                if ray.is_key_pressed(ord(key)):
                    selected_item = self.navigator.items[self.navigator.selected_index]
                    if selected_item is not None and selected_item.box.name == "Back":
                        self.navigator.go_back()
                        #audio.play_sound(self.sound_cancel)
                    else:
                        selected_song = self.navigator.select_current_item()
                        if selected_song:
                            self.state = "SONG_SELECTED"
                            audio.play_sound(self.sound_don)
                            self.move_away = Animation.create_move(233, total_distance=500)
                            self.diff_fade_out = Animation.create_fade(83)

        elif self.state == "SONG_SELECTED":
            # Handle song selection confirmation or cancel
            keys = get_config()["keybinds"]["left_don"] + get_config()["keybinds"]["right_don"]
            for key in keys:
                if ray.is_key_pressed(ord(key)):
                    if self.selected_difficulty == -1:
                        self.selected_song = None
                        self.move_away = Animation.create_move(float('inf'))
                        self.diff_fade_out = Animation.create_fade(0, final_opacity=1.0)
                        self.text_fade_out = None
                        self.text_fade_in = None
                        self.state = "BROWSING"
                        for item in self.navigator.items:
                            item.box.reset()
                    else:
                        audio.play_sound(self.sound_don)
                        self.game_transition = Transition(self.screen_height)
            keys = get_config()["keybinds"]["left_kat"]
            for key in keys:
                if ray.is_key_pressed(ord(key)):
                    audio.play_sound(self.sound_kat)
                    if self.selected_difficulty >= 0:
                        self.selected_difficulty = (self.selected_difficulty - 1)
            keys = get_config()["keybinds"]["right_kat"]
            for key in keys:
                if ray.is_key_pressed(ord(key)):
                    audio.play_sound(self.sound_kat)
                    if self.selected_difficulty < 4:
                        self.selected_difficulty = (self.selected_difficulty + 1)

    def update(self):
        self.on_screen_start()
        if self.background_move.is_finished:
            self.background_move = Animation.create_move(15000, start_position=0, total_distance=1280)
        self.background_move.update(get_current_ms())

        if self.game_transition is not None:
            self.game_transition.update(get_current_ms())
            if self.game_transition.is_finished:
                return self.on_screen_end()

        self.handle_input()

        if self.demo_song is not None:
            audio.update_music_stream(self.demo_song)

        if self.background_fade_change is None:
            self.last_texture_index = self.texture_index
        for song in self.navigator.items:
            song.box.update(self.state == "SONG_SELECTED")
            song.box.is_open = song.box.position == SongSelectScreen.BOX_CENTER + 150
            if not isinstance(song, Directory) and song.box.is_open:
                if self.demo_song is None and get_current_ms() >= song.box.wait + (83.33*3):
                    song.box.get_scores()
                    self.demo_song = audio.load_music_stream(song.tja.metadata.wave)
                    audio.normalize_music_stream(self.demo_song, 0.1935)
                    audio.seek_music_stream(self.demo_song, song.tja.metadata.demostart)
                    audio.play_music_stream(self.demo_song)
            if song.box.is_open:
                current_box = song.box
                if current_box.texture_index != 552 and get_current_ms() >= song.box.wait + (83.33*3):
                    self.texture_index = SongBox.BACKGROUND_MAP[current_box.texture_index]

        if self.last_texture_index != self.texture_index and self.background_fade_change is None:
            self.background_fade_change = Animation.create_fade(200)

        self.move_away.update(get_current_ms())
        self.diff_fade_out.update(get_current_ms())

        if self.background_fade_change is not None:
            self.background_fade_change.update(get_current_ms())
            if self.background_fade_change.is_finished:
                self.background_fade_change = None

        if self.move_away.is_finished and self.text_fade_out is None:
            self.text_fade_out = Animation.create_fade(33)
            self.text_fade_in = Animation.create_fade(33, initial_opacity=0.0, final_opacity=1.0, delay=self.text_fade_out.duration)

        if self.text_fade_out is not None:
            self.text_fade_out.update(get_current_ms())
            if self.text_fade_out.is_finished:
                self.selected_song = True

        if self.text_fade_in is not None:
            self.text_fade_in.update(get_current_ms())

    def draw_selector(self):
        if self.selected_difficulty == -1:
            ray.draw_texture(self.textures['song_select'][133], 314, 110, ray.WHITE)
        else:
            ray.draw_texture(self.textures['song_select'][140], 450 + (self.selected_difficulty * 115), 7, ray.WHITE)
            ray.draw_texture(self.textures['song_select'][131], 461 + (self.selected_difficulty * 115), 132, ray.WHITE)

    def draw(self):
        # Draw file/directory list
        texture_back = self.textures['song_select'][self.last_texture_index]
        texture = self.textures['song_select'][self.texture_index]
        for i in range(0, texture.width * 4, texture.width):
            if self.background_fade_change is not None:
                color = ray.fade(ray.WHITE, self.background_fade_change.attribute)
                ray.draw_texture(texture_back, i - int(self.background_move.attribute), 0, color)
                reverse_color = ray.fade(ray.WHITE, 1 - self.background_fade_change.attribute)
                ray.draw_texture(texture, i - int(self.background_move.attribute), 0, reverse_color)
            else:
                ray.draw_texture(texture, i - int(self.background_move.attribute), 0, ray.WHITE)

        for item in self.navigator.get_items():
            box = item.box
            if -156 <= box.position <= self.screen_width + 144:
                if box.position <= 500:
                    box.draw(box.position - int(self.move_away.attribute), 95, self.textures, self.diff_fade_out.attribute)
                else:
                    box.draw(box.position + int(self.move_away.attribute), 95, self.textures, self.diff_fade_out.attribute)

        if self.selected_song and self.state == "SONG_SELECTED":
            self.draw_selector()
            fade = ray.WHITE
            if self.text_fade_in is not None:
                fade = ray.fade(ray.WHITE, self.text_fade_in.attribute)
            ray.draw_texture(self.textures['song_select'][192], 5, 5, fade)
        else:
            fade = ray.WHITE
            if self.text_fade_out is not None:
                fade = ray.fade(ray.WHITE, self.text_fade_out.attribute)
            ray.draw_texture(self.textures['song_select'][244], 5, 5, fade)

        ray.draw_texture(self.textures['song_select'][394], 0, self.screen_height - self.textures['song_select'][394].height, ray.WHITE)

        if self.game_transition is not None:
            self.game_transition.draw(self.screen_height)


class SongBox:
    OUTLINE_MAP = {
        555: ray.Color(0, 77, 104, 255),
        560: ray.Color(156, 64, 2, 255),
        565: ray.Color(153, 4, 46, 255),
        570: ray.Color(60, 104, 0, 255),
        575: ray.Color(134, 88, 0, 255),
        580: ray.Color(79, 40, 134, 255),
        585: ray.Color(148, 24, 0, 255),
        615: ray.Color(84, 101, 126, 255)
    }
    FOLDER_HEADER_MAP = {
        555: 643,
        560: 645,
        565: 647,
        570: 649,
        575: 651,
        580: 653,
        585: 655,
        615: 667,
        620: 670
    }
    FULL_FOLDER_HEADER_MAP = {
        555: 736,
        560: 738,
        565: 740,
        570: 742,
        575: 744,
        580: 746,
        585: 748,
        615: 760,
        620: 762,
    }
    BACKGROUND_MAP = {
        555: 772,
        560: 773,
        565: 774,
        570: 775,
        575: 776,
        580: 777,
        585: 778,
        615: 783,
        620: 784
    }
    GENRE_CHAR_MAP = {
        555: 507,
        560: 509,
        565: 511,
        570: 513,
        575: 515,
        580: 517,
        585: 519,
        615: 532,
    }
    def __init__(self, name: str, texture_index: int, is_dir: bool, tja: Optional[TJAParser] = None, tja_count: Optional[int] = None):
        self.text_name = name
        self.texture_index = texture_index
        self.scores = dict()
        self.position = -11111
        self.start_position = -1
        self.target_position = -1
        self.is_open = False
        self.name = None
        self.black_name = None
        self.hori_name = None
        self.yellow_box = None
        self.open_anim = None
        self.open_fade = None
        self.move = None
        self.wait = 0
        self.is_dir = is_dir
        self.tja_count = tja_count
        self.tja_count_text = None
        if self.tja_count is not None and self.tja_count != 0:
            self.tja_count_text = OutlinedText(str(self.tja_count), 35, ray.Color(255, 255, 255, 255), ray.Color(0, 0, 0, 255), outline_thickness=5, horizontal_spacing=1.2)
        self.tja = tja
        self.hash = dict()
        self.update(False)

    def reset(self):
        if self.black_name is not None:
            self.yellow_box = YellowBox(self.black_name, self.texture_index == 552, tja=self.tja)
        self.open_anim = None
        self.open_fade = None

    def get_scores(self):
        if self.tja is None:
            return

        with sqlite3.connect('scores.db') as con:
            cursor = con.cursor()

            diffs_to_compute = []
            for diff in self.tja.metadata.course_data:
                if diff not in self.hash:
                    diffs_to_compute.append(diff)

            if diffs_to_compute:
                for diff in diffs_to_compute:
                    notes, _, bars = self.tja.notes_to_position(diff)
                    self.hash[diff] = self.tja.hash_note_data(notes, bars)

            # Batch database query for all diffs at once
            if self.tja.metadata.course_data:
                hash_values = [self.hash[diff] for diff in self.tja.metadata.course_data]
                placeholders = ','.join('?' * len(hash_values))

                batch_query = f"""
                    SELECT hash, score, good, ok, bad
                    FROM Scores
                    WHERE hash IN ({placeholders})
                """
                cursor.execute(batch_query, hash_values)

                hash_to_score = {row[0]: row[1:] for row in cursor.fetchall()}

                for diff in self.tja.metadata.course_data:
                    diff_hash = self.hash[diff]
                    self.scores[diff] = hash_to_score.get(diff_hash)

    def update(self, is_diff_select):
        self.is_diff_select = is_diff_select
        if self.yellow_box is not None:
            self.yellow_box.update(is_diff_select)
        is_open_prev = self.is_open
        if self.position != self.target_position and self.move is None:
            if self.position < self.target_position:
                direction = 1
            else:
                direction = -1
            if abs(self.target_position - self.position) > 250:
                direction *= -1
            self.move = Animation.create_move(66.67, start_position=0, total_distance=100 * direction)
            if self.is_open or self.target_position == SongSelectScreen.BOX_CENTER + 150:
                self.move.total_distance = 250 * direction
            self.start_position = self.position
        if self.move is not None:
            self.move.update(get_current_ms())
            self.position = self.start_position + int(self.move.attribute)
            if self.move.is_finished:
                self.position = self.target_position
                self.move = None
        self.is_open = self.position == SongSelectScreen.BOX_CENTER + 150
        if not is_open_prev and self.is_open:
            if self.black_name is None:
                self.black_name = OutlinedText(self.text_name, 40, ray.Color(255, 255, 255, 255), ray.Color(0, 0, 0, 255), outline_thickness=5, vertical=True)
                #print(f"loaded black name {self.text_name}")
            if self.tja is not None or self.texture_index == 552:
                self.yellow_box = YellowBox(self.black_name, self.texture_index == 552, tja=self.tja)
                self.yellow_box.create_anim()
            else:
                self.hori_name = OutlinedText(self.text_name, 40, ray.Color(255, 255, 255, 255), ray.Color(0, 0, 0, 255), outline_thickness=5)
                #print(f"loaded hori name {self.text_name}")
                self.open_anim = Animation.create_move(133, start_position=0, total_distance=150, delay=83.33)
                self.open_fade = Animation.create_fade(200, initial_opacity=0, final_opacity=1.0)
            self.wait = get_current_ms()


        elif not self.is_open:
            if self.black_name is not None:
                self.black_name.unload()
                self.black_name = None
            if self.yellow_box is not None:
                self.yellow_box = None
            if self.hori_name is not None:
                self.hori_name.unload()
                self.hori_name = None

        if self.open_anim is not None:
            self.open_anim.update(get_current_ms())
        if self.open_fade is not None:
            self.open_fade.update(get_current_ms())

        '''
        if self.black_name is None:
            self.black_name = OutlinedText(self.text_name, 40, ray.Color(255, 255, 255, 255), ray.Color(0, 0, 0, 255), outline_thickness=5, vertical=True)
        if self.name is None:
            self.name = OutlinedText(self.text_name, 40, ray.Color(255, 255, 255, 255), SongBox.OUTLINE_MAP.get(self.texture_index, ray.Color(101, 0, 82, 255)), outline_thickness=5, vertical=True)
        '''

        if self.name is None and -56 <= self.position <= 1280:
            self.name = OutlinedText(self.text_name, 40, ray.Color(255, 255, 255, 255), SongBox.OUTLINE_MAP.get(self.texture_index, ray.Color(101, 0, 82, 255)), outline_thickness=5, vertical=True)
            #print(f"loaded {self.text_name}")
        elif self.name is not None and (self.position < -56 or self.position > 1280):
            self.name.unload()
            self.name = None


    def _draw_closed(self, x: int, y: int, textures):
        ray.draw_texture(textures['song_select'][self.texture_index+1], x, y, ray.WHITE)
        offset = 0
        if 555 <= self.texture_index <= 600:
            offset = 1
        for i in range(0, textures['song_select'][self.texture_index].width * 4, textures['song_select'][self.texture_index].width):
            ray.draw_texture(textures['song_select'][self.texture_index], (x+32)+i, y - offset, ray.WHITE)
        ray.draw_texture(textures['song_select'][self.texture_index+2], x+64, y, ray.WHITE)
        if self.texture_index == 620:
            ray.draw_texture(textures['song_select'][self.texture_index+3], x+12, y+16, ray.WHITE)
        if self.texture_index != 552 and self.is_dir:
            ray.draw_texture(textures['song_select'][SongBox.FOLDER_HEADER_MAP[self.texture_index]], x+4 - offset, y-6, ray.WHITE)


        if self.texture_index == 552:
            ray.draw_texture(textures['song_select'][422], x + 47 - int(textures['song_select'][422].width / 2), y+35, ray.WHITE)
        elif self.name is not None:
            src = ray.Rectangle(0, 0, self.name.texture.width, self.name.texture.height)
            dest = ray.Rectangle(x + 47 - int(self.name.texture.width / 2), y+35, self.name.texture.width, min(self.name.texture.height, 417))
            self.name.draw(src, dest, ray.Vector2(0, 0), 0, ray.WHITE)
        #ray.draw_text(str(self.position), x, y-25, 25, ray.GREEN)

    def _draw_open(self, x: int, y: int, textures, fade_override):
        if self.open_anim is not None:
            color = ray.WHITE
            if fade_override is not None:
                color = ray.fade(ray.WHITE, fade_override)
            if self.hori_name is not None and self.open_anim.attribute >= 100:
                texture = textures['song_select'][SongBox.FULL_FOLDER_HEADER_MAP[self.texture_index]]
                src = ray.Rectangle(0, 0, texture.width, texture.height)
                dest = ray.Rectangle(x-115+48, (y-56) + 150 - int(self.open_anim.attribute), texture.width+220, texture.height)
                ray.draw_texture_pro(texture, src, dest, ray.Vector2(0,0), 0, color)

                texture = textures['song_select'][SongBox.FULL_FOLDER_HEADER_MAP[self.texture_index]+1]
                src = ray.Rectangle(0, 0, -texture.width, texture.height)
                dest = ray.Rectangle(x-115, y-56 + 150 - int(self.open_anim.attribute), texture.width, texture.height)
                ray.draw_texture(texture, x+160, y-56 + 150 - int(self.open_anim.attribute), color)
                ray.draw_texture_pro(texture, src, dest, ray.Vector2(0,0), 0, color)

                src = ray.Rectangle(0, 0, self.hori_name.texture.width, self.hori_name.texture.height)
                dest_width = min(300, self.hori_name.texture.width)
                dest = ray.Rectangle((x + 48) - (dest_width//2), y-50 + 150 - int(self.open_anim.attribute), dest_width, self.hori_name.texture.height)
                self.hori_name.draw(src, dest, ray.Vector2(0, 0), 0, color)


            ray.draw_texture(textures['song_select'][self.texture_index+1], x - int(self.open_anim.attribute), y, ray.WHITE)

            offset = 0
            if 555 <= self.texture_index <= 600:
                offset = 1
            for i in range(0, textures['song_select'][self.texture_index].width * (5+int(self.open_anim.attribute / 4)), textures['song_select'][self.texture_index].width):
                ray.draw_texture(textures['song_select'][self.texture_index], ((x- int(self.open_anim.attribute))+32)+i, y - offset, ray.WHITE)

            ray.draw_texture(textures['song_select'][self.texture_index+2], x+64 + int(self.open_anim.attribute), y, ray.WHITE)

            color = ray.WHITE
            if self.texture_index == 620:
                ray.draw_texture(textures['song_select'][self.texture_index+4], x+12 - 150, y+16, color)
            if fade_override is not None:
                color = ray.fade(ray.WHITE, min(0.5, fade_override))
            ray.draw_texture(textures['song_select'][492], 470, 125, color)

            color = ray.WHITE
            if fade_override is not None:
                color = ray.fade(ray.WHITE, fade_override)
            if self.tja_count_text is not None:
                ray.draw_texture(textures['song_select'][493], 475, 125, color)
                ray.draw_texture(textures['song_select'][494], 600, 125, color)
                src = ray.Rectangle(0, 0, self.tja_count_text.texture.width, self.tja_count_text.texture.height)
                dest_width = min(124, self.tja_count_text.texture.width)
                dest = ray.Rectangle(560 - (dest_width//2), 118, dest_width, self.tja_count_text.texture.height)
                self.tja_count_text.draw(src, dest, ray.Vector2(0, 0), 0, color)
            if self.texture_index in SongBox.GENRE_CHAR_MAP:
                ray.draw_texture(textures['song_select'][SongBox.GENRE_CHAR_MAP[self.texture_index]+1], 650, 125, color)
                ray.draw_texture(textures['song_select'][SongBox.GENRE_CHAR_MAP[self.texture_index]], 470, 180, color)

    def draw(self, x: int, y: int, textures, fade_override=None):
        if self.is_open and get_current_ms() >= self.wait + 83.33:
            if self.yellow_box is not None:
                self.yellow_box.draw(textures, self, fade_override)
            else:
                if self.open_fade is not None:
                    self._draw_open(x, y, textures, self.open_fade.attribute)
        else:
            self._draw_closed(x, y, textures)

class YellowBox:
    def __init__(self, name: OutlinedText, is_back: bool, tja: Optional[TJAParser] = None):
        self.is_diff_select = False
        self.right_x = 803
        self.left_x = 443
        self.top_y = 96
        self.bottom_y = 543
        self.center_width = 332
        self.center_height = 422
        self.edge_height = 32
        self.name = name
        self.is_back = is_back
        self.tja = tja
        self.anim_created = False
        self.left_out = Animation.create_move(83.33, total_distance=-152, delay=83.33)
        self.right_out = Animation.create_move(83.33, total_distance=145, delay=83.33)
        self.center_out = Animation.create_move(83.33, total_distance=300, delay=83.33)
        self.fade = Animation.create_fade(83.33, initial_opacity=1.0, final_opacity=1.0, delay=83.33)
        self.reset_animations()

    def reset_animations(self):
        self.fade_in = Animation.create_fade(float('inf'), initial_opacity=0.0, final_opacity=1.0, delay=83.33)
        self.left_out_2 = Animation.create_move(float('inf'), total_distance=-213)
        self.right_out_2 = Animation.create_move(float('inf'), total_distance=0)
        self.center_out_2 = Animation.create_move(float('inf'), total_distance=423)
        self.top_y_out = Animation.create_move(float('inf'), total_distance=-62)
        self.center_h_out = Animation.create_move(float('inf'), total_distance=60)

    def create_anim(self):
        self.left_out = Animation.create_move(83.33, total_distance=-152, delay=83.33)
        self.right_out = Animation.create_move(83.33, total_distance=145, delay=83.33)
        self.center_out = Animation.create_move(83.33, total_distance=300, delay=83.33)
        self.fade = Animation.create_fade(83.33, initial_opacity=0.0, final_opacity=1.0, delay=83.33)

    def create_anim_2(self):
        self.left_out_2 = Animation.create_move(116.67, total_distance=-213)
        self.right_out_2 = Animation.create_move(116.67, total_distance=211)
        self.center_out_2 = Animation.create_move(116.67, total_distance=423)

        self.top_y_out = Animation.create_move(133.33, total_distance=-62, delay=self.left_out_2.duration)
        self.center_h_out = Animation.create_move(133.33, total_distance=60, delay=self.left_out_2.duration)

        self.fade_in = Animation.create_fade(116.67, initial_opacity=0.0, final_opacity=1.0, delay=self.left_out_2.duration + self.top_y_out.duration + 16.67)


    def update(self, is_diff_select: bool):
        self.left_out.update(get_current_ms())
        self.right_out.update(get_current_ms())
        self.center_out.update(get_current_ms())
        self.fade.update(get_current_ms())
        self.fade_in.update(get_current_ms())
        self.left_out_2.update(get_current_ms())
        self.right_out_2.update(get_current_ms())
        self.center_out_2.update(get_current_ms())
        self.top_y_out.update(get_current_ms())
        self.center_h_out.update(get_current_ms())
        self.is_diff_select = is_diff_select
        if self.is_diff_select:
            if not self.anim_created:
                self.anim_created = True
                self.create_anim_2()
            self.right_x = 803 + int(self.right_out_2.attribute)
            self.left_x = 443 + int(self.left_out_2.attribute)
            self.top_y = 96 + int(self.top_y_out.attribute)
            self.center_width = 332 + int(self.center_out_2.attribute)
            self.center_height = 422 + int(self.center_h_out.attribute)
        else:
            self.anim_created = False
            self.right_x = 658 + int(self.right_out.attribute)
            self.left_x = 595  + int(self.left_out.attribute)
            self.top_y = 96
            self.center_width = 32 + int(self.center_out.attribute)
            self.center_height = 422

    def draw(self, textures: dict[str, list[ray.Texture]], song_box: SongBox, fade_override: Optional[float]):
        # Draw corners
        ray.draw_texture(textures['song_select'][235], self.right_x, self.bottom_y, ray.WHITE)  # Bottom right
        ray.draw_texture(textures['song_select'][236], self.left_x, self.bottom_y, ray.WHITE)   # Bottom left
        ray.draw_texture(textures['song_select'][237], self.right_x, self.top_y, ray.WHITE)     # Top right
        ray.draw_texture(textures['song_select'][238], self.left_x, self.top_y, ray.WHITE)      # Top left

        # Edges
        # Bottom edge
        texture = textures['song_select'][231]
        src = ray.Rectangle(0, 0, texture.width, texture.height)
        dest = ray.Rectangle(self.left_x + self.edge_height, self.bottom_y, self.center_width, texture.height)
        ray.draw_texture_pro(texture, src, dest, ray.Vector2(0, 0), 0, ray.WHITE)

        # Right edge
        texture = textures['song_select'][232]
        src = ray.Rectangle(0, 0, texture.width, texture.height)
        dest = ray.Rectangle(self.right_x, self.top_y + self.edge_height, texture.width, self.center_height)
        ray.draw_texture_pro(texture, src, dest, ray.Vector2(0, 0), 0, ray.WHITE)

        # Left edge
        texture = textures['song_select'][233]
        src = ray.Rectangle(0, 0, texture.width, texture.height)
        dest = ray.Rectangle(self.left_x, self.top_y + self.edge_height, texture.width, self.center_height)
        ray.draw_texture_pro(texture, src, dest, ray.Vector2(0, 0), 0, ray.WHITE)

        # Top edge
        texture = textures['song_select'][234]
        src = ray.Rectangle(0, 0, texture.width, texture.height)
        dest = ray.Rectangle(self.left_x + self.edge_height, self.top_y, self.center_width, texture.height)
        ray.draw_texture_pro(texture, src, dest, ray.Vector2(0, 0), 0, ray.WHITE)

        # Center
        texture = textures['song_select'][230]
        src = ray.Rectangle(0, 0, texture.width, texture.height)
        dest = ray.Rectangle(self.left_x + self.edge_height, self.top_y + self.edge_height, self.center_width, self.center_height)
        ray.draw_texture_pro(texture, src, dest, ray.Vector2(0, 0), 0, ray.WHITE)


        if self.is_diff_select:
            #Back Button
            color = ray.fade(ray.WHITE, self.fade_in.attribute)
            ray.draw_texture(textures['song_select'][153], 314, 110, color)

            #Difficulties
            ray.draw_texture(textures['song_select'][154], 450, 90, color)
            ray.draw_texture(textures['song_select'][182], 565, 90, color)
            ray.draw_texture(textures['song_select'][185], 680, 90, color)
            ray.draw_texture(textures['song_select'][188], 795, 90, color)

            if self.tja is not None:
                for course in self.tja.metadata.course_data:
                    for j in range(self.tja.metadata.course_data[course].level):
                        ray.draw_texture(textures['song_select'][155], 482+(course*115), 471+(j*-20), color)

        else:
            #Crowns
            fade = self.fade.attribute
            if fade_override is not None:
                fade = min(self.fade.attribute, fade_override)
            color = ray.fade(ray.WHITE, fade)
            if self.is_back:
                ray.draw_texture(textures['song_select'][421], 498, 250, color)
            elif self.tja is not None:
                for diff in self.tja.metadata.course_data:
                    if diff in song_box.scores and song_box.scores[diff] is not None and song_box.scores[diff][3] == 0:
                        ray.draw_texture(textures['song_select'][160], 473 + (diff*60), 175, color)
                    ray.draw_texture(textures['song_select'][158], 473 + (diff*60), 175, ray.fade(color, min(fade, 0.25)))

                #EX Data
                if self.tja.ex_data.new_audio:
                    ray.draw_texture(textures['custom'][0], 458, 120, color)
                elif self.tja.ex_data.old_audio:
                    ray.draw_texture(textures['custom'][1], 458, 120, color)
                elif self.tja.ex_data.limited_time:
                    ray.draw_texture(textures['song_select'][418], 458, 120, color)

                #Difficulties
                ray.draw_texture(textures['song_select'][395], 458, 210, color)
                ray.draw_texture(textures['song_select'][401], 518, 210, color)
                ray.draw_texture(textures['song_select'][403], 578, 210, color)
                ray.draw_texture(textures['song_select'][406], 638, 210, color)

                #Stars
                for course in self.tja.metadata.course_data:
                    for j in range(self.tja.metadata.course_data[course].level):
                        ray.draw_texture(textures['song_select'][396], 474+(course*60), 490+(j*-17), color)
            else:
                pass
        if self.is_back:
            texture = textures['song_select'][422]
            x = int(((song_box.position + 47) - texture.width / 2) + (int(self.right_out.attribute)*0.85) + (int(self.right_out_2.attribute)))
            y = self.top_y+35
            ray.draw_texture(texture, x, y, ray.WHITE)
        elif self.name is not None:
            texture = self.name.texture
            x = int(((song_box.position + 47) - texture.width / 2) + (int(self.right_out.attribute)*0.85) + (int(self.right_out_2.attribute)))
            y = self.top_y+35
            src = ray.Rectangle(0, 0, texture.width, texture.height)
            dest = ray.Rectangle(x, y, texture.width, min(texture.height, 417))
            self.name.draw(src, dest, ray.Vector2(0, 0), 0, ray.WHITE)

class Transition:
    def __init__(self, screen_height: int) -> None:
        self.is_finished = False
        self.rainbow_up = Animation.create_move(266, start_position=0, total_distance=screen_height + global_data.textures['scene_change_rainbow'][2].height, ease_in='cubic')
        self.chara_down = None
    def update(self, current_time_ms: float):
        self.rainbow_up.update(current_time_ms)
        if self.rainbow_up.is_finished and self.chara_down is None:
            self.chara_down = Animation.create_move(33, start_position=0, total_distance=30)

        if self.chara_down is not None:
            self.chara_down.update(current_time_ms)
            self.is_finished = self.chara_down.is_finished

    def draw(self, screen_height: int):
        ray.draw_texture(global_data.textures['scene_change_rainbow'][2], 0, screen_height - int(self.rainbow_up.attribute), ray.WHITE)
        texture = global_data.textures['scene_change_rainbow'][0]
        src = ray.Rectangle(0, 0, texture.width, texture.height)
        dest = ray.Rectangle(0, screen_height - int(self.rainbow_up.attribute) + global_data.textures['scene_change_rainbow'][2].height, texture.width, screen_height)
        ray.draw_texture_pro(texture, src, dest, ray.Vector2(0, 0), 0, ray.WHITE)
        texture = global_data.textures['scene_change_rainbow'][3]
        offset = 0
        if self.chara_down is not None:
            offset = int(self.chara_down.attribute)
        ray.draw_texture(texture, 76, 816 - int(self.rainbow_up.attribute) + offset, ray.WHITE)

class FileSystemItem:
    GENRE_MAP = {
        'J-POP': 555,
        'アニメ': 560,
        'どうよう': 565,
        'バラエティー': 570,
        'クラシック': 575,
        'ゲームミュージック': 580,
        'ナムコオリジナル': 585,
        'VOCALOID': 615,
    }
    """Base class for files and directories in the navigation system"""
    def __init__(self, path: Path, name: str):
        self.path = path
        self.selected = False

    def is_selectable(self):
        return True


class Directory(FileSystemItem):
    """Represents a directory in the navigation system"""
    def __init__(self, path: Path, name: str, texture_index: int, has_box_def=False, to_root=False, back=False):
        super().__init__(path, name)
        self.has_box_def = has_box_def
        self.to_root = to_root
        self.back = back
        if self.to_root or self.back:
            texture_index = 552
        tja_count = 0
        if self.has_box_def:
            tja_count = self.count_tja_files(path)
        if (path / "song_list.txt").exists():
            with open(path / "song_list.txt", 'r', encoding='utf-8-sig') as song_list_file:
                tja_count += len(song_list_file.readlines())
        self.box = SongBox(name, texture_index, True, tja_count=tja_count)

    def count_tja_files(self, folder_path: Path):
        tja_count = 0

        #print(f"Scanning {folder_path}")
        try:
            items = folder_path.iterdir()

            for item in items:
                item_path = folder_path / item

                if item_path.is_file():
                    if item.suffix == '.tja':
                        tja_count += 1
                        #print(f"Found: {item_path}")

                elif item_path.is_dir():
                    tja_count += self.count_tja_files(item_path)

        except PermissionError:
            print(f"Permission denied accessing '{folder_path}'")
        except Exception as e:
            print(f"Error accessing '{folder_path}': {e}")

        return tja_count

    def get_display_name(self):
        return self.box


class SongFile(FileSystemItem):
    """Represents a song file (TJA) in the navigation system"""
    def __init__(self, path: Path, name: str, texture_index: int):
        super().__init__(path, name)
        self.tja = TJAParser(path)
        title = self.tja.metadata.title.get(get_config()['general']['language'].lower(), self.tja.metadata.title['en'])
        self.box = SongBox(title, texture_index, False, tja=self.tja)


    def get_display_name(self):
        return self.box


class FileNavigator:
    """Manages navigation through the file system"""
    def __init__(self, root_dirs: list[str]):
        # Handle both single path and list of paths
        if isinstance(root_dirs, (list, tuple)):
            self.root_dirs = [Path(p) if not isinstance(p, Path) else p for p in root_dirs]
        else:
            self.root_dirs = [Path(root_dirs) if not isinstance(root_dirs, Path) else root_dirs]

        self.in_root_selection = True  # Whether we're showing the root directory selection screen
        self.current_dir = Path()
        self.current_root_dir = Path()
        self.items: list[Directory | SongFile] = []
        self.selected_index = 0
        self.history = []  # For tracking directory navigation history
        self.load_root_directories()

    def check_for_box_def(self, dir_path: Path):
        """Check if the directory contains a box.def file"""
        box_def_path = dir_path / "box.def"
        return box_def_path.exists()

    def get_tja_folder_count(self, directory: Path):
        return len(self.find_tja_files_recursive(directory))

    def find_tja_files_recursive(self, directory: Path, box_def_dirs_only=True):
        tja_files = []

        try:
            has_box_def = self.check_for_box_def(directory)
            if box_def_dirs_only and has_box_def and directory != self.current_dir:
                return []
            for path in directory.iterdir():
                if path.is_file() and path.suffix.lower() == ".tja":
                    tja_files.append(path)
                elif path.is_dir():
                    sub_dir_has_box_def = self.check_for_box_def(path)
                    if not sub_dir_has_box_def:
                        tja_files.extend(self.find_tja_files_recursive(path, box_def_dirs_only))
        except (PermissionError, OSError):
            pass

        return tja_files

    def parse_box_def(self, path):
        texture_index = 620
        name = path.name
        with open(path / "box.def", 'r', encoding='utf-8') as box_def:
            for line in box_def:
                if line.strip().startswith("#GENRE:"):
                    texture_index = FileSystemItem.GENRE_MAP[line.split(":")[1].strip()]
                if line.strip().startswith("#TITLE:"):
                    name = line.split(":")[1].strip()
                if line.strip().startswith("#TITLEJA:"):
                    if get_config()['general']['language'] == 'ja':
                        name = line.split(":")[1].strip()
        return name, texture_index

    def calculate_box_positions(self):
        """Dynamically calculate box positions based on current selection with wrap-around support"""
        if not self.items:
            return

        num_items = len(self.items)

        # Calculate positions for each item relative to the selected item
        for i, item in enumerate(self.items):
            # Calculate the circular distance from selected index
            offset = i - self.selected_index

            # Handle wrap-around by choosing the shortest circular distance
            if offset > num_items // 2:
                offset -= num_items
            elif offset < -num_items // 2:
                offset += num_items

            # Calculate position based on offset
            position = SongSelectScreen.BOX_CENTER + (100 * offset)

            # Apply the same position adjustments as before
            if position == SongSelectScreen.BOX_CENTER:
                position += 150
            elif position > SongSelectScreen.BOX_CENTER:
                position += 300
            else:
                position -= 0

            if item.box.position == -11111:
                item.box.position = position
                item.box.target_position = position
            else:
                item.box.target_position = position

    def set_base_positions(self):
        """Set initial positions for all items"""
        self.calculate_box_positions()

    def load_root_directories(self):
        """Load the list of root directories as selectable items"""
        self.items = []
        self.in_root_selection = True
        self.current_dir = Path()
        self.current_root_dir = Path()

        # Create directory items for each root
        for root_path in self.root_dirs:
            name = root_path.name if root_path.name else str(root_path)
            has_box_def = self.check_for_box_def(root_path)
            # Only add roots with box.def as directories
            if has_box_def:
                name, texture_index = self.parse_box_def(root_path)
                self.items.append(Directory(root_path, name, texture_index, has_box_def=True))
            else:
                # For roots without box.def, add their TJA files directly to the root selection
                tja_files = self.find_tja_files_recursive(root_path)
                for tja_path in sorted(tja_files):
                    self.items.append(SongFile(tja_path, tja_path.name, 620))

        # Reset selection
        self.selected_index = 0 if self.items else -1

        self.calculate_box_positions()

    def load_current_directory(self):
        """Load all directories and TJA files in the current directory"""
        self.items = []
        self.selected_index = 0

        if self.current_dir != self.current_root_dir:
            self.items.append(Directory(self.current_dir.parent, "", 552, back=True))
        elif not self.in_root_selection:
            self.items.append(Directory(Path(), "", 552, to_root=True))
        # Add only directories that contain box.def files
        for path in sorted(self.current_dir.iterdir()):
            if path.is_dir():
                has_box_def = self.check_for_box_def(path)
                if has_box_def:
                    name, texture_index = self.parse_box_def(path)
                    self.items.append(Directory(path, name, texture_index, has_box_def=True))

        tja_files = []
        if (self.current_dir / 'song_list.txt').exists():
            updated_lines = []
            file_updated = False

            with open(self.current_dir / 'song_list.txt', 'r', encoding='utf-8-sig') as song_list:
                for line in song_list:
                    hash, title, subtitle = line.strip().split('|')
                    original_hash = hash

                    if song_hash.song_hashes is not None:
                        if hash in song_hash.song_hashes:
                            tja_files.append(Path(song_hash.song_hashes[hash]["file_path"]))
                        else:
                            for key, value in song_hash.song_hashes.items():
                                if value["title"]["en"] == title and value["subtitle"]["en"][2:] == subtitle and Path(value["file_path"]).exists():
                                    hash = key
                                    tja_files.append(Path(song_hash.song_hashes[hash]["file_path"]))
                                    break
                    if hash != original_hash:
                        file_updated = True
                    updated_lines.append(f"{hash}|{title}|{subtitle}")

            if file_updated:
                with open(self.current_dir / 'song_list.txt', 'w', encoding='utf-8-sig') as song_list:
                    for line in updated_lines:
                        song_list.write(line + '\n')

        else:
            tja_files = self.find_tja_files_recursive(self.current_dir)

        # Then add TJA files found
        for i, tja_path in enumerate(sorted(tja_files)):
            if i % 10 == 0 and i != 0:
                if self.current_dir != self.current_root_dir:
                    self.items.append(Directory(self.current_dir.parent, "", 552, back=True))
                elif not self.in_root_selection:
                    self.items.append(Directory(Path(), "", 552, to_root=True))
            texture_index = 620
            _, texture_index = self.parse_box_def(self.current_dir)
            self.items.append(SongFile(tja_path, tja_path.name, texture_index))

        self.calculate_box_positions()

    def navigate_left(self):
        """Move selection left with wrap-around"""
        if self.items:
            self.selected_index = (self.selected_index - 1) % len(self.items)
            self.calculate_box_positions()

    def navigate_right(self):
        """Move selection right with wrap-around"""
        if self.items:
            self.selected_index = (self.selected_index + 1) % len(self.items)
            self.calculate_box_positions()

    def get_items(self):
        """Get visible items on screen - now returns all items since positions are dynamic"""
        # With wrap-around, we might want to show all items or filter based on visibility
        # For now, return all items since their positions are dynamically calculated
        return self.items

    def get_visible_items(self, screen_width=1280):
        """Get only the items that would be visible on screen"""
        if not self.items:
            return []

        visible_items = []
        center = SongSelectScreen.BOX_CENTER
        half_screen = screen_width // 2

        for item in self.items:
            # Check if item's position is within the visible screen area
            if abs(item.box.position - center) <= half_screen:
                visible_items.append(item)

        return visible_items

    def select_current_item(self):
        """Select the currently highlighted item"""
        if not self.items or self.selected_index >= len(self.items):
            return

        selected_item = self.items[self.selected_index]

        if isinstance(selected_item, Directory):
            if selected_item.to_root:
                self.load_root_directories()
            else:
                if self.current_dir is not None:
                    self.history.append((self.current_dir, self.selected_index, self.in_root_selection, self.current_root_dir))
                self.current_dir = selected_item.path
                if self.in_root_selection:
                    self.current_root_dir = selected_item.path
                    self.in_root_selection = False
                self.selected_index = 0
                self.load_current_directory()
        elif isinstance(selected_item, SongFile):
            return selected_item

    def go_back(self):
        """Navigate back to the previous directory"""
        if self.history:
            previous_dir, previous_index, previous_in_root, previous_root_dir = self.history.pop()
            self.current_dir = previous_dir
            self.selected_index = previous_index
            self.in_root_selection = previous_in_root
            self.current_root_dir = previous_root_dir
            self.load_current_directory()
        elif not self.in_root_selection:
            # If we're not in history but also not in root selection, go back to root selection
            self.load_root_directories()

    def get_current_item(self):
        """Get the currently selected item"""
        if self.items and 0 <= self.selected_index < len(self.items):
            return self.items[self.selected_index]
        raise Exception()
