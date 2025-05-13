import os
from pathlib import Path
import sqlite3

import pyray as ray

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
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.song_list: dict[str, list] = dict()
        self.song_name_textures: list[OutlinedText] = []
        self.selected_song = 0
        self.selected_difficulty = 0

        self.song_boxes: list[SongBox] = []
        self.yellow_box = YellowBox()

        self.screen_init = False

        self.box_wait = 0
        self.move = Animation.create_move(0)

        self.game_transition = None

    def _load_font_for_text(self, text: str) -> ray.Font:
        codepoint_count = ray.ffi.new('int *', 0)
        unique_codepoints = set(text)
        codepoints = ray.load_codepoints(''.join(unique_codepoints), codepoint_count)
        return ray.load_font_ex(str(Path('Graphics/Modified-DFPKanteiryu-XB.ttf')), 40, codepoints, 0)

    def load_textures(self):
        self.textures = load_all_textures_from_zip(Path('Graphics/lumendata/song_select.zip'))

    def load_sounds(self):
        sounds_dir = Path("Sounds")
        self.sound_don = audio.load_sound(str(sounds_dir / "inst_00_don.wav"))
        self.sound_kat = audio.load_sound(str(sounds_dir / "inst_00_katsu.wav"))

    def get_scores(self, tja: TJAParser, difficulty: int):
        with sqlite3.connect('scores.db') as con:
            cursor = con.cursor()
            hash = tja.hash_note_data(tja.data_to_notes(difficulty)[0])
            check_query = "SELECT score, good, ok, bad FROM Scores WHERE hash = ? LIMIT 1"
            cursor.execute(check_query, (hash,))
            result = cursor.fetchone()
        return result

    def on_screen_start(self):
        if not self.screen_init:
            self.load_textures()
            self.load_sounds()
            self.game_transition = None
            for dirpath, dirnames, filenames in os.walk(f'{get_config()["paths"]["tja_path"]}'):
                for filename in filenames:
                    if filename.endswith(".tja"):
                        tja = TJAParser(dirpath)
                        scores = dict()
                        self.song_list[dirpath] = tja.get_metadata()
                        for diff in self.song_list[dirpath][8].keys():
                            scores[diff] = self.get_scores(tja, diff)
                        name = self.song_list[dirpath][0]
                        font = self._load_font_for_text(name)
                        text = OutlinedText(font, name, 40, ray.WHITE, ray.BLACK, outline_thickness=4, vertical=True)
                        self.song_boxes.append(SongBox(text, dirpath, scores))
            self.screen_init = True
            self.is_song_select = True
            self.is_difficulty_select = False
            self.background_move = Animation.create_move(15000, start_position=0, total_distance=1280)

    def on_screen_end(self):
        self.screen_init = False
        session_data.selected_song = self.song_boxes[5].dirpath
        session_data.selected_difficulty = self.selected_difficulty
        for zip in self.textures:
            for texture in self.textures[zip]:
                ray.unload_texture(texture)
        return "GAME"

    def update_song_select(self):
        if ray.is_key_pressed(ray.KeyboardKey.KEY_ENTER):
            audio.play_sound(self.sound_don)
            self.is_song_select = False
            self.is_difficulty_select = True
        elif ray.is_key_pressed(ray.KeyboardKey.KEY_LEFT):
            audio.play_sound(self.sound_kat)
            self.song_boxes.insert(0, self.song_boxes.pop())
            self.move = Animation.create_move(66.68, start_position=0, total_distance=100)
            self.box_wait = get_current_ms()
        elif ray.is_key_pressed(ray.KeyboardKey.KEY_RIGHT):
            audio.play_sound(self.sound_kat)
            self.song_boxes.append(self.song_boxes.pop(0))
            self.move = Animation.create_move(66.68, start_position=0, total_distance=-100)
            self.box_wait = get_current_ms()

    def update_difficulty_select(self):
        if ray.is_key_pressed(ray.KeyboardKey.KEY_ENTER):
            if self.selected_difficulty == -1:
                self.is_song_select = True
                self.is_difficulty_select = False
            else:
                audio.play_sound(self.sound_don)
                self.game_transition = Transition(self.height)
        elif ray.is_key_pressed(ray.KeyboardKey.KEY_LEFT):
            audio.play_sound(self.sound_kat)
            if self.selected_difficulty >= 0:
                self.selected_difficulty = (self.selected_difficulty - 1)
        elif ray.is_key_pressed(ray.KeyboardKey.KEY_RIGHT):
            audio.play_sound(self.sound_kat)
            if self.selected_difficulty < 4:
                self.selected_difficulty = (self.selected_difficulty + 1)

    def update(self):
        self.on_screen_start()
        self.background_move.update(get_current_ms())
        if self.game_transition is not None:
            self.game_transition.update(get_current_ms())
            if self.game_transition.is_finished:
                return self.on_screen_end()
        if self.background_move.is_finished:
            self.background_move = Animation.create_move(15000, start_position=0, total_distance=1280)
        if self.is_song_select:
            self.update_song_select()
            self.yellow_box.update(self.song_boxes[5].name, False)
        elif self.is_difficulty_select:
            self.yellow_box.update(self.song_boxes[5].name, True)
            self.update_difficulty_select()
        if self.move is not None:
            self.move.update(get_current_ms())

    def draw_song_select(self):
        offset = 0
        for i in range(-1, 17):
            box = self.song_boxes[i+1]
            if i == 4 and self.move.is_finished and get_current_ms() >= self.box_wait + 133.36:
                self.yellow_box.draw(self.textures, self.song_list, self.song_boxes)
                offset = 300
            else:
                move = 0
                if self.move is not None:
                    move = int(self.move.attribute) - self.move.total_distance
                box.draw(44 + (i*100) + offset + move, 95, 620, self.textures)

    def draw_selector(self):
        if self.selected_difficulty == -1:
            ray.draw_texture(self.textures['song_select'][133], 314, 110, ray.WHITE)
        else:
            ray.draw_texture(self.textures['song_select'][140], 450 + (self.selected_difficulty * 115), 7, ray.WHITE)
            ray.draw_texture(self.textures['song_select'][131], 461 + (self.selected_difficulty * 115), 132, ray.WHITE)

    def draw_difficulty_select(self):
        self.yellow_box.draw(self.textures, self.song_list, self.song_boxes)
        self.draw_selector()

    def draw(self):
        texture = self.textures['song_select'][784]
        for i in range(0, texture.width * 4, texture.width):
            ray.draw_texture(self.textures['song_select'][784], i - int(self.background_move.attribute), 0, ray.WHITE)
        if self.is_song_select:
            self.draw_song_select()
            ray.draw_texture(self.textures['song_select'][244], 5, 5, ray.WHITE)
        elif self.is_difficulty_select:
            self.draw_difficulty_select()
            ray.draw_texture(self.textures['song_select'][192], 5, 5, ray.WHITE)
        ray.draw_texture(self.textures['song_select'][394], 0, self.height - self.textures['song_select'][394].height, ray.WHITE)

        if self.game_transition is not None:
            self.game_transition.draw(self.height)

class SongBox:
    def __init__(self, song_name_texture: OutlinedText, dirpath, scores):
        self.name = song_name_texture
        self.dirpath = dirpath
        self.scores = scores
    def update(self):
        pass
    def draw(self, x: int, y: int, texture_index: int, textures):
        ray.draw_texture(textures['song_select'][texture_index+1], x, y, ray.WHITE)
        for i in range(0, textures['song_select'][texture_index].width * 4, textures['song_select'][texture_index].width):
            ray.draw_texture(textures['song_select'][texture_index], (x+32)+i, y, ray.WHITE)
        ray.draw_texture(textures['song_select'][texture_index+2], x+64, y, ray.WHITE)
        ray.draw_texture(textures['song_select'][texture_index+3], x+12, y+16, ray.WHITE)

        src = ray.Rectangle(0, 0, self.name.texture.width, self.name.texture.height)
        dest = ray.Rectangle(x + 47 - int(self.name.texture.width / 2), y+35, self.name.texture.width, min(self.name.texture.height, 417))
        self.name.draw(src, dest, ray.Vector2(0, 0), 0, ray.WHITE)

class YellowBox:
    def __init__(self):
        self.is_diff_select = False
        self.right_x = 803
        self.left_x = 443
        self.top_y = 94
        self.bottom_y = 542
        self.center_width = 331
        self.center_height = 422
        self.edge_height = 32
        self.name = None
    def update(self, name, is_diff_select):
        self.is_diff_select = is_diff_select
        self.name = name
        if self.is_diff_select:
            self.right_x = 1014
            self.left_x = 230
            self.top_y = 34
            self.center_width = 755
            self.center_height = 482
        else:
            self.right_x = 803
            self.left_x = 443
            self.top_y = 94
            self.center_width = 331
            self.center_height = 422
    def draw(self, textures, song_list, song_boxes):

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
            ray.draw_texture(textures['song_select'][153], 314, 110, ray.WHITE)

            #Difficulties
            ray.draw_texture(textures['song_select'][154], 450, 90, ray.WHITE)
            ray.draw_texture(textures['song_select'][182], 565, 90, ray.WHITE)
            ray.draw_texture(textures['song_select'][185], 680, 90, ray.WHITE)
            ray.draw_texture(textures['song_select'][188], 795, 90, ray.WHITE)

            for i in range(4):
                try:
                    for j in range(song_list[song_boxes[5].dirpath][8][i][0]):
                        ray.draw_texture(textures['song_select'][155], 482+(i*115), 471+(j*-20), ray.WHITE)
                except:
                    pass

        else:
            #Crowns
            for i in range(4):
                if i in song_boxes[5].scores and song_boxes[5].scores[i] is not None and song_boxes[5].scores[i][3] == 0:
                    ray.draw_texture(textures['song_select'][160], 473 + (i*60), 175, ray.WHITE)
                ray.draw_texture(textures['song_select'][158], 473 + (i*60), 175, ray.fade(ray.WHITE, 0.25))

            #Difficulties
            ray.draw_texture(textures['song_select'][395], 458, 210, ray.WHITE)
            ray.draw_texture(textures['song_select'][401], 518, 210, ray.WHITE)
            ray.draw_texture(textures['song_select'][403], 578, 210, ray.WHITE)
            ray.draw_texture(textures['song_select'][406], 638, 210, ray.WHITE)

            #Stars
            for i in range(4):
                try:
                    for j in range(song_list[song_boxes[5].dirpath][8][i][0]):
                        ray.draw_texture(textures['song_select'][396], 474+(i*60), 490+(j*-17), ray.WHITE)
                except:
                    pass

        if self.name is not None:
            texture = self.name.texture
            src = ray.Rectangle(0, 0, texture.width, texture.height)
            dest = ray.Rectangle((self.right_x - 32) - texture.width / 2, self.top_y + 32, texture.width, min(texture.height, 417))
            self.name.draw(src, dest, ray.Vector2(0, 0), 0, ray.WHITE)

class Transition:
    def __init__(self, screen_height) -> None:
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

    def draw(self, screen_height):
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
