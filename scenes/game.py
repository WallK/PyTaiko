import bisect
import math
from collections import deque

import pyray as ray

from libs.animation import Animation
from libs.audio import audio
from libs.tja import TJAParser, calculate_base_score
from libs.utils import (
    GlobalData,
    get_config,
    get_current_ms,
    load_image_from_zip,
    load_texture_from_zip,
)


class GameScreen:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.judge_x = 414
        self.current_ms = 0
        self.song_is_started = False

    def load_textures(self):
        zip_file = 'Graphics\\lumendata\\enso_system\\common.zip'
        self.texture_judge_circle = load_texture_from_zip(zip_file, 'lane_hit_img00017.png')

        self.image_lane = load_image_from_zip(zip_file, 'lane_img00000.png')
        ray.image_resize(self.image_lane, 948, 176)
        self.texture_lane = ray.load_texture_from_image(self.image_lane)

        self.texture_lane_cover = load_texture_from_zip(zip_file, 'lane_obi_img00000.png')
        self.texture_score_cover = load_texture_from_zip(zip_file, 'lane_obi_img00003.png')

        self.texture_don = [load_texture_from_zip(zip_file, 'onp_don_img00000.png'),
        load_texture_from_zip(zip_file, 'onp_don_img00001.png')]
        self.texture_kat = [load_texture_from_zip(zip_file, 'onp_katsu_img00000.png'),
        load_texture_from_zip(zip_file, 'onp_katsu_img00001.png')]

        self.texture_dai_don = [load_texture_from_zip(zip_file, 'onp_don_dai_img00000.png'),
        load_texture_from_zip(zip_file, 'onp_don_dai_img00001.png')]
        self.texture_dai_kat = [load_texture_from_zip(zip_file, 'onp_katsu_dai_img00000.png'),
        load_texture_from_zip(zip_file, 'onp_katsu_dai_img00001.png')]

        self.texture_balloon_head = [load_texture_from_zip(zip_file, 'onp_fusen_img00001.png'),
        load_texture_from_zip(zip_file, 'onp_fusen_img00002.png')]
        self.texture_balloon_tail = [load_texture_from_zip(zip_file, 'onp_fusen_img00000.png'),
        load_texture_from_zip(zip_file, 'onp_fusen_img00000.png')]

        self.texture_drumroll_head = [load_texture_from_zip(zip_file, 'onp_renda_img00002.png'),
        load_texture_from_zip(zip_file, 'onp_renda_img00003.png')]
        self.texture_drumroll_body = [load_texture_from_zip(zip_file, 'onp_renda_img00000.png'),
        load_texture_from_zip(zip_file, 'onp_renda_img00000.png')]
        self.texture_drumroll_tail = [load_texture_from_zip(zip_file, 'onp_renda_img00001.png'),
        load_texture_from_zip(zip_file, 'onp_renda_img00001.png')]
        self.texture_dai_drumroll_head = [load_texture_from_zip(zip_file, 'onp_renda_dai_img00002.png'),
        load_texture_from_zip(zip_file, 'onp_renda_dai_img00003.png')]
        self.texture_dai_drumroll_body = [load_texture_from_zip(zip_file, 'onp_renda_dai_img00000.png'),
        load_texture_from_zip(zip_file, 'onp_renda_dai_img00000.png')]
        self.texture_dai_drumroll_tail = [load_texture_from_zip(zip_file, 'onp_renda_dai_img00001.png'),
        load_texture_from_zip(zip_file, 'onp_renda_dai_img00001.png')]
        self.texture_drumroll_count = load_texture_from_zip(zip_file, 'renda_num_img00000.png')
        self.texture_drumroll_number = []
        for i in range(1, 11):
            filename = f'renda_num_img{str(i).zfill(5)}.png'
            self.texture_drumroll_number.append(load_texture_from_zip(zip_file, filename))


        self.texture_barline = load_texture_from_zip(zip_file, 'lane_syousetsu_img00000.png')

        self.texture_good = load_texture_from_zip(zip_file, 'lane_hit_effect_img00009.png')
        self.texture_good_hit_center = load_texture_from_zip(zip_file, 'lane_hit_img00019.png')
        self.texture_good_hit_center_big = load_texture_from_zip(zip_file, 'lane_hit_img00021.png')
        self.texture_good_hit_effect = [load_texture_from_zip(zip_file, 'lane_hit_effect_img00005.png'),
        load_texture_from_zip(zip_file, 'lane_hit_effect_img00006.png'),
        load_texture_from_zip(zip_file, 'lane_hit_effect_img00007.png'),
        load_texture_from_zip(zip_file, 'lane_hit_effect_img00008.png'),
        load_texture_from_zip(zip_file, 'lane_hit_effect_img00008.png')]
        self.texture_good_hit_effect_big = [load_texture_from_zip(zip_file, 'lane_hit_effect_img00011.png'),
        load_texture_from_zip(zip_file, 'lane_hit_effect_img00012.png'),
        load_texture_from_zip(zip_file, 'lane_hit_effect_img00013.png'),
        load_texture_from_zip(zip_file, 'lane_hit_effect_img00014.png'),
        load_texture_from_zip(zip_file, 'lane_hit_effect_img00015.png')]

        self.texture_ok = load_texture_from_zip(zip_file, 'lane_hit_effect_img00004.png')
        self.texture_ok_hit_center = load_texture_from_zip(zip_file, 'lane_hit_img00018.png')
        self.texture_ok_hit_center_big = load_texture_from_zip(zip_file, 'lane_hit_img00020.png')
        self.texture_ok_hit_effect = [load_texture_from_zip(zip_file, 'lane_hit_effect_img00000.png'),
        load_texture_from_zip(zip_file, 'lane_hit_effect_img00001.png'),
        load_texture_from_zip(zip_file, 'lane_hit_effect_img00002.png'),
        load_texture_from_zip(zip_file, 'lane_hit_effect_img00003.png'),
        load_texture_from_zip(zip_file, 'lane_hit_effect_img00003.png')]
        self.texture_ok_hit_effect_big = [load_texture_from_zip(zip_file, 'lane_hit_effect_img00016.png'),
        load_texture_from_zip(zip_file, 'lane_hit_effect_img00017.png'),
        load_texture_from_zip(zip_file, 'lane_hit_effect_img00018.png'),
        load_texture_from_zip(zip_file, 'lane_hit_effect_img00019.png'),
        load_texture_from_zip(zip_file, 'lane_hit_effect_img00020.png')]

        self.texture_bad = load_texture_from_zip(zip_file, 'lane_hit_effect_img00010.png')

        self.image_lane_effect_good = load_image_from_zip(zip_file, 'lane_hit_img00007.png')
        ray.image_resize(self.image_lane_effect_good, 951, 130)
        self.image_lane_effect_don = load_image_from_zip(zip_file, 'lane_hit_img00005.png')
        ray.image_resize(self.image_lane_effect_don, 951, 130)
        self.image_lane_effect_kat = load_image_from_zip(zip_file, 'lane_hit_img00006.png')
        ray.image_resize(self.image_lane_effect_kat, 951, 130)
        self.texture_lane_effect_good = ray.load_texture_from_image(self.image_lane_effect_good)
        self.texture_lane_effect_don = ray.load_texture_from_image(self.image_lane_effect_don)
        self.texture_lane_effect_kat = ray.load_texture_from_image(self.image_lane_effect_kat)

        self.texture_drum = load_texture_from_zip(zip_file, 'lane_obi_img00014.png')
        self.texture_don_R = load_texture_from_zip(zip_file, 'lane_obi_img00015.png')
        self.texture_don_L = load_texture_from_zip(zip_file, 'lane_obi_img00016.png')
        self.texture_kat_R = load_texture_from_zip(zip_file, 'lane_obi_img00017.png')
        self.texture_kat_L = load_texture_from_zip(zip_file, 'lane_obi_img00018.png')

        self.texture_1p_emblem = load_texture_from_zip(zip_file, 'lane_obi_img00019.png')
        self.texture_difficulty = [load_texture_from_zip(zip_file, 'lane_obi_img00021.png'),
        load_texture_from_zip(zip_file, 'lane_obi_img00022.png'),
        load_texture_from_zip(zip_file, 'lane_obi_img00023.png'),
        load_texture_from_zip(zip_file, 'lane_obi_img00024.png'),
        load_texture_from_zip(zip_file, 'lane_obi_img00025.png'),
        load_texture_from_zip(zip_file, 'lane_obi_img00025.png'),
        load_texture_from_zip(zip_file, 'lane_obi_img00025.png')]

        self.texture_combo_text = [load_texture_from_zip(zip_file, 'lane_obi_img00035.png'),
        load_texture_from_zip(zip_file, 'lane_obi_img00046.png')]
        self.texture_combo_numbers = []
        for i in range(36, 58):
            if i not in [46, 48]:
                filename = f'lane_obi_img{str(i).zfill(5)}.png'
                self.texture_combo_numbers.append(load_texture_from_zip(zip_file, filename))
        self.texture_combo_glimmer = load_texture_from_zip(zip_file, 'lane_obi_img00048.png')

        self.texture_score_numbers = []
        for i in range(4, 14):
            filename = f'lane_obi_img{str(i).zfill(5)}.png'
            self.texture_score_numbers.append(load_texture_from_zip(zip_file, filename))

        self.texture_se_moji = []
        for i in range(0, 17):
            filename = f'onp_moji_img{str(i).zfill(5)}.png'
            if i == 8:
                filename = 'onp_renda_moji_img00001.png'
            self.texture_se_moji.append(load_texture_from_zip(zip_file, filename))

        zip_file = 'Graphics\\lumendata\\enso_system\\base1p.zip'
        self.texture_balloon_speech_bubble_p1 = load_texture_from_zip(zip_file, 'action_fusen_1p_img00000.png')
        self.texture_balloon = [load_texture_from_zip(zip_file, 'action_fusen_1p_img00011.png'),
        load_texture_from_zip(zip_file, 'action_fusen_1p_img00012.png'),
        load_texture_from_zip(zip_file, 'action_fusen_1p_img00013.png'),
        load_texture_from_zip(zip_file, 'action_fusen_1p_img00014.png'),
        load_texture_from_zip(zip_file, 'action_fusen_1p_img00015.png'),
        load_texture_from_zip(zip_file, 'action_fusen_1p_img00016.png'),
        load_texture_from_zip(zip_file, 'action_fusen_1p_img00017.png'),
        load_texture_from_zip(zip_file, 'action_fusen_1p_img00018.png')]
        self.texture_balloon_number = [load_texture_from_zip(zip_file, 'action_fusen_1p_img00001.png'),
        load_texture_from_zip(zip_file, 'action_fusen_1p_img00002.png'),
        load_texture_from_zip(zip_file, 'action_fusen_1p_img00003.png'),
        load_texture_from_zip(zip_file, 'action_fusen_1p_img00004.png'),
        load_texture_from_zip(zip_file, 'action_fusen_1p_img00005.png'),
        load_texture_from_zip(zip_file, 'action_fusen_1p_img00006.png'),
        load_texture_from_zip(zip_file, 'action_fusen_1p_img00007.png'),
        load_texture_from_zip(zip_file, 'action_fusen_1p_img00008.png'),
        load_texture_from_zip(zip_file, 'action_fusen_1p_img00009.png'),
        load_texture_from_zip(zip_file, 'action_fusen_1p_img00010.png')]
        self.texture_base_score_numbers = []
        for i in range(0, 10):
            filename = f'score_add_1p_img{str(i).zfill(5)}.png'
            self.texture_base_score_numbers.append(load_texture_from_zip(zip_file, filename))

    def load_sounds(self):
        self.sound_don = audio.load_sound('Sounds\\inst_00_don.wav')
        self.sound_kat = audio.load_sound('Sounds\\inst_00_katsu.wav')
        self.sound_balloon_pop = audio.load_sound('Sounds\\balloon_pop.wav')

    def init_tja(self, song: str, difficulty: int):
        self.load_textures()
        self.load_sounds()

        #Map notes to textures
        self.note_type_dict = {'1': self.texture_don,
        '2': self.texture_kat,
        '3': self.texture_dai_don,
        '4': self.texture_dai_kat,
        '5': self.texture_drumroll_head,
        '6': self.texture_dai_drumroll_head,
        '7': self.texture_balloon_head,
        'drumroll_body': self.texture_drumroll_body,
        'drumroll_tail': self.texture_drumroll_tail,
        'dai_drumroll_body': self.texture_dai_drumroll_body,
        'dai_drumroll_tail': self.texture_dai_drumroll_tail,
        'balloon_tail': self.texture_balloon_tail}

        self.tja = TJAParser(song)
        self.tja.get_metadata()
        self.tja.distance = self.width - self.judge_x

        self.player_1 = Player(self, 1, difficulty, get_config()["general"]["judge_offset"])
        self.song_music = audio.load_sound(self.tja.wave)
        self.start_ms = get_current_ms() - self.tja.offset*1000

        audio.play_sound(self.song_music)


    def update(self):
        if GlobalData.start_song and not self.song_is_started:
            self.init_tja(GlobalData.selected_song, GlobalData.selected_difficulty)
            self.song_is_started = True
        self.current_ms = get_current_ms() - self.start_ms
        self.player_1.update(self)
        if len(self.player_1.play_note_list) == 0 and not audio.is_sound_playing(self.song_music):
            GlobalData.result_good, GlobalData.result_ok, GlobalData.result_bad, GlobalData.result_score = self.player_1.get_result_score()
            GlobalData.start_song = False
            self.song_is_started = False
            return 'RESULT'

    def draw(self):
        self.player_1.draw(self)

class Player:
    def __init__(self, game_screen, player_number: int, difficulty: int, judge_offset: int):
        self.timing_good = 25.0250015258789
        self.timing_ok = 75.0750045776367
        self.timing_bad = 108.441665649414

        self.player_number = player_number
        self.difficulty = difficulty

        self.play_note_list, self.draw_note_list, self.draw_bar_list = game_screen.tja.notes_to_position(self.difficulty)
        self.base_score = calculate_base_score(self.play_note_list)

        self.judge_offset = judge_offset

        #Note management
        self.current_notes = deque()
        self.current_bars = []
        self.current_notes_draw = []
        self.play_note_index = 0
        self.draw_note_index = 0
        self.bar_index = 0
        self.is_drumroll = False
        self.drumroll_big = 0
        self.curr_drumroll_count = 0
        self.is_balloon = False
        self.curr_balloon_count = 0

        #Score management
        self.good_count = 0
        self.ok_count = 0
        self.bad_count = 0
        self.combo = 0
        self.score = 0
        self.max_combo = 0

        self.arc_points = 25

        self.draw_judge_list = []
        self.draw_effect_list = []
        self.draw_arc_list = []
        self.draw_drum_hit_list = []
        self.drumroll_counter = []
        self.balloon_list = []
        self.combo_list = []
        self.score_list = []
        self.base_score_list = []

    def get_result_score(self):
        return self.good_count, self.ok_count, self.bad_count, self.score

    def get_position(self, game_screen, ms, pixels_per_frame):
        return int(game_screen.width + pixels_per_frame * 60 / 1000 * (ms - game_screen.current_ms + self.judge_offset) - 64)

    def animation_manager(self, game_screen, animation_list):
        if len(animation_list) <= 0:
            return
        for i in range(len(animation_list)-1, -1, -1):
            animation = animation_list[i]
            animation.update(game_screen.current_ms)
            if animation.is_finished:
                animation_list.pop(i)

    def bar_manager(self, game_screen):
        #Add bar to current_bars list if it is ready to be shown on screen
        if len(self.draw_bar_list) > 0 and game_screen.current_ms > self.draw_bar_list[0]['load_ms']:
            self.current_bars.append(self.draw_bar_list.popleft())

        #If a bar is off screen, remove it
        if len(self.current_bars) <= 0:
            return

        for i in range(len(self.current_bars)-1, -1, -1):
            bar_ms, pixels_per_frame = self.current_bars[i]['ms'], self.current_bars[i]['ppf']
            position = self.get_position(game_screen, bar_ms, pixels_per_frame)
            if position < game_screen.judge_x + 650:
                self.current_bars.pop(i)

    def play_note_manager(self, game_screen):
        #Add note to current_notes list if it is ready to be shown on screen
        if len(self.play_note_list) > 0 and game_screen.current_ms + 1000 >= self.play_note_list[0]['load_ms']:
            if self.play_note_list[0]['note'] == '8':
                self.current_notes.append(self.play_note_list.popleft())
            self.current_notes.append(self.play_note_list.popleft())

        #if a note was not hit within the window, remove it
        if len(self.current_notes) == 0:
            return

        note = self.current_notes[0]
        if note['ms'] + self.timing_bad < game_screen.current_ms:
            if note['note'] in {'1', '2', '3', '4'}:
                self.combo = 0
                self.bad_count += 1
            self.current_notes.popleft()
        elif (note['ms'] <= game_screen.current_ms):
            if note['note'] == '5':
                self.is_drumroll = True
                self.drumroll_big = 0
            elif note['note'] == '6':
                self.is_drumroll = True
                self.drumroll_big = 2
            elif note['note'] == '7':
                self.is_balloon = True
            elif note['note'] == '8' and (self.is_drumroll or self.is_balloon):
                self.is_drumroll = False
                self.is_balloon = False

    def draw_note_manager(self, game_screen):
        if len(self.draw_note_list) > 0 and game_screen.current_ms + 1000 >= self.draw_note_list[0]['load_ms']:
            if self.draw_note_list[0]['note'] in {'5', '6', '7'}:
                while self.draw_note_list[0]['note'] != '8':
                    bisect.insort_left(self.current_notes_draw, self.draw_note_list.popleft(), key=lambda x: x['index'])
                bisect.insort_left(self.current_notes_draw, self.draw_note_list.popleft(), key=lambda x: x['index'])
            else:
                bisect.insort_left(self.current_notes_draw, self.draw_note_list.popleft(), key=lambda x: x['index'])

        #If a note is off screen, remove it
        if len(self.current_notes_draw) == 0:
            return

        if self.current_notes_draw[0]['note'] in {'5', '6', '8'} and 255 > self.current_notes_draw[0]['color'] > 0:
            self.current_notes_draw[0]['color'] += 1

        note = self.current_notes_draw[0]
        if note['note'] in {'5', '6', '7'}:
            note = self.current_notes_draw[1]
        position = self.get_position(game_screen, note['ms'], note['ppf'])
        if position < game_screen.judge_x + 650:
            if note['note'] == '8':
                self.current_notes_draw.pop(0)
            self.current_notes_draw.pop(0)

    def note_manager(self, game_screen):
        self.bar_manager(game_screen)
        self.play_note_manager(game_screen)
        self.draw_note_manager(game_screen)

    def note_correct(self, game_screen, note):
        index = note['index']
        if note['note'] == '8':
            note_type = game_screen.note_type_dict['3']
        else:
            note_type = game_screen.note_type_dict[note['note']]

        self.combo += 1
        if self.combo > self.max_combo:
            self.max_combo = self.combo

        self.draw_arc_list.append(NoteArc(note_type, game_screen.current_ms, self.player_number))
        self.current_notes.popleft()

        if note in self.current_notes_draw:
            index = self.current_notes_draw.index(note)
            self.current_notes_draw.pop(index)

    def check_drumroll(self, game_screen, drum_type):
        note_type = game_screen.note_type_dict[str(int(drum_type)+self.drumroll_big)]
        self.draw_arc_list.append(NoteArc(note_type, game_screen.current_ms, self.player_number))
        self.curr_drumroll_count += 1
        self.score += 100
        self.base_score_list.append(ScoreCounterAnimation(game_screen.current_ms, 100))
        color = 255 - (self.curr_drumroll_count*10)
        if color < 0:
            self.current_notes_draw[0]['color'] = 0
        else:
            self.current_notes_draw[0]['color'] = color

    def check_balloon(self, game_screen, drum_type):
        current_note = self.current_notes[0]
        if current_note['note'] == '7':
            current_note = self.current_notes[1]
        if len(self.balloon_list) < 1:
            self.balloon_list.append(BalloonAnimation(game_screen.current_ms, current_note['balloon']))
        self.curr_balloon_count += 1
        self.score += 100
        self.base_score_list.append(ScoreCounterAnimation(game_screen.current_ms, 100))
        self.current_notes_draw[0]['popped'] = False
        if self.curr_balloon_count == current_note['balloon']:
            self.is_balloon = False
            self.current_notes_draw[0]['popped'] = True
            audio.play_sound(game_screen.sound_balloon_pop)
            self.note_correct(game_screen, self.current_notes[0])

    def check_note(self, game_screen, drum_type):
        if self.is_drumroll:
            self.check_drumroll(game_screen, drum_type)
        elif self.is_balloon and drum_type == '1':
            self.check_balloon(game_screen, drum_type)
        elif len(self.current_notes) != 0:
            self.curr_drumroll_count = 0
            self.curr_balloon_count = 0
            current_note = self.current_notes[0]
            #Fix later
            i = 0
            while current_note['note'] in {'5', '6', '7', '8'}:
                i += 1
                current_note = self.current_notes[i]
            note_type = current_note['note']
            note_ms = current_note['ms']
            #If the wrong key was hit, stop checking
            if drum_type == '1' and note_type not in {'1', '3'}:
                return
            if drum_type == '2' and note_type not in {'2', '4'}:
                return
            #If the note is too far away, stop checking
            if game_screen.current_ms > (note_ms + self.timing_bad):
                return
            if note_type in ('3','4'):
                big = True
            else:
                big = False
            if (note_ms - self.timing_good) + self.judge_offset <= game_screen.current_ms <= (note_ms + self.timing_good) + self.judge_offset:
                self.draw_judge_list.append(Judgement(game_screen.current_ms, 'GOOD', big))
                self.draw_effect_list.pop()
                self.draw_effect_list.append(LaneHitEffect(game_screen.current_ms, 'GOOD'))
                self.good_count += 1
                self.score += self.base_score
                self.base_score_list.append(ScoreCounterAnimation(game_screen.current_ms, self.base_score))
                self.note_correct(game_screen, current_note)

            elif (note_ms - self.timing_ok) + self.judge_offset <= game_screen.current_ms <= (note_ms + self.timing_ok) + self.judge_offset:
                self.draw_judge_list.append(Judgement(game_screen.current_ms, 'OK', big))
                self.ok_count += 1
                self.score += 10 * math.floor(self.base_score / 2 / 10)
                self.base_score_list.append(ScoreCounterAnimation(game_screen.current_ms, 10 * math.floor(self.base_score / 2 / 10)))
                self.note_correct(game_screen, current_note)

            elif (note_ms - self.timing_bad) + self.judge_offset <= game_screen.current_ms <= (note_ms + self.timing_bad) + self.judge_offset:
                self.draw_judge_list.append(Judgement(game_screen.current_ms, 'BAD', big))
                self.bad_count += 1
                self.combo = 0
                self.current_notes.popleft()

    def drumroll_counter_manager(self, game_screen):
        if self.is_drumroll and self.curr_drumroll_count > 0:
            if len(self.drumroll_counter) == 0 or self.drumroll_counter[-1].is_finished:
                self.drumroll_counter.append(DrumrollCounter(game_screen.current_ms))

        if len(self.drumroll_counter) <= 0:
            return

        if self.drumroll_counter[0].is_finished and not self.is_drumroll:
            self.drumroll_counter.pop(0)
        else:
            self.drumroll_counter[0].update(game_screen, game_screen.current_ms, self.curr_drumroll_count)

    def balloon_animation_manager(self, game_screen):
        if len(self.balloon_list) <= 0:
            return

        if self.balloon_list[0].is_finished:
            self.balloon_list.pop(0)
        else:
            if self.is_balloon:
                self.balloon_list[0].update(game_screen, game_screen.current_ms, self.curr_balloon_count, False)
            else:
                self.balloon_list[0].update(game_screen, game_screen.current_ms, self.curr_balloon_count, True)

    def combo_manager(self, game_screen):
        if self.combo >= 3 and len(self.combo_list) == 0:
            self.combo_list.append(Combo(self.combo, game_screen.current_ms))
        elif self.combo < 3 and len(self.combo_list) != 0:
            self.combo_list.pop(0)
        elif len(self.combo_list) == 1:
            self.combo_list[0].update(game_screen, game_screen.current_ms, self.combo)

    def score_manager(self, game_screen):
        if len(self.score_list) == 0:
            self.score_list.append(ScoreCounter(self.score, game_screen.current_ms))
        elif len(self.score_list) == 1:
            self.score_list[0].update(game_screen.current_ms, self.score)

    def key_manager(self, game_screen):
        left_kat = ord(get_config()["keybinds"]["left_kat"])
        left_don = ord(get_config()["keybinds"]["left_don"])
        right_don = ord(get_config()["keybinds"]["right_don"])
        right_kat = ord(get_config()["keybinds"]["right_kat"])
        if ray.is_key_pressed(left_don):
            self.draw_effect_list.append(LaneHitEffect(game_screen.current_ms, 'DON'))
            self.draw_drum_hit_list.append(DrumHitEffect(game_screen.current_ms, 'DON', 'L'))
            audio.play_sound(game_screen.sound_don)
            self.check_note(game_screen, '1')
        if ray.is_key_pressed(right_don):
            self.draw_effect_list.append(LaneHitEffect(game_screen.current_ms, 'DON'))
            self.draw_drum_hit_list.append(DrumHitEffect(game_screen.current_ms, 'DON', 'R'))
            audio.play_sound(game_screen.sound_don)
            self.check_note(game_screen, '1')
        if ray.is_key_pressed(left_kat):
            self.draw_effect_list.append(LaneHitEffect(game_screen.current_ms, 'KAT'))
            self.draw_drum_hit_list.append(DrumHitEffect(game_screen.current_ms, 'KAT', 'L'))
            audio.play_sound(game_screen.sound_kat)
            self.check_note(game_screen, '2')
        if ray.is_key_pressed(right_kat):
            self.draw_effect_list.append(LaneHitEffect(game_screen.current_ms, 'KAT'))
            self.draw_drum_hit_list.append(DrumHitEffect(game_screen.current_ms, 'KAT', 'R'))
            audio.play_sound(game_screen.sound_kat)
            self.check_note(game_screen, '2')

    def update(self, game_screen):
        self.note_manager(game_screen)
        self.combo_manager(game_screen)
        self.drumroll_counter_manager(game_screen)
        self.balloon_animation_manager(game_screen)
        self.animation_manager(game_screen, self.draw_judge_list)
        self.animation_manager(game_screen, self.draw_effect_list)
        self.animation_manager(game_screen, self.draw_drum_hit_list)
        self.animation_manager(game_screen, self.draw_arc_list)
        self.animation_manager(game_screen, self.base_score_list)
        self.score_manager(game_screen)
        self.key_manager(game_screen)

    def draw_animation_list(self, game_screen, animation_list):
        for animation in animation_list:
            animation.draw(game_screen)

    def draw_drumroll(self, game_screen, big, position, index, color):
        drumroll_start_position = position
        tail = self.current_notes_draw[index+1]
        i = 0
        while tail['note'] != '8':
            i += 1
            tail = self.current_notes_draw[index+i]
        if big:
            drumroll_body = 'dai_drumroll_body'
            drumroll_tail = 'dai_drumroll_tail'
        else:
            drumroll_body = 'drumroll_body'
            drumroll_tail = 'drumroll_tail'
        drumroll_end_position = self.get_position(game_screen, tail['load_ms'], tail['ppf'])
        length = (drumroll_end_position - drumroll_start_position - 50)
        self.draw_note(game_screen, drumroll_body, (drumroll_start_position+64), color, 8, drumroll_length=length)
        self.draw_note(game_screen, drumroll_tail, drumroll_end_position, color, 10, drumroll_length=None)

    def draw_balloon(self, game_screen, note, position, index):
        if self.current_notes_draw[0].get('popped', None):
            return
        end_time = self.current_notes_draw[index+1]
        i = 0
        while end_time['note'] != '8':
            i += 1
            end_time = self.current_notes_draw[index+i]
        end_time_position = self.get_position(game_screen, end_time['load_ms'], end_time['ppf'])
        if game_screen.current_ms >= end_time['ms']:
            position = end_time_position
        elif game_screen.current_ms >= note['ms']:
            position = 349
        self.draw_note(game_screen, '7', position, 255, 9)

    def draw_note(self, game_screen, note, position, color, se_note, drumroll_length=None):
        note_padding = 64
        if note == 'barline':
            y = 184
            ray.draw_texture(game_screen.texture_barline, position+note_padding-4, y+6, ray.WHITE)
            return
        if note not in game_screen.note_type_dict:
            return

        eighth_in_ms = (60000 * 4 / game_screen.tja.bpm) / 8
        if self.combo >= 50:
            current_eighth = int((game_screen.current_ms - game_screen.start_ms) // eighth_in_ms)
        else:
            current_eighth = 0
        if note in {'5', '6', 'drumroll_tail', 'dai_drumroll_tail', 'drumroll_body', 'dai_drumroll_body'}:
            draw_color = color
        else:
            draw_color = 255
        if note == '7':
            offset = 12
            balloon = True
        else:
            offset = 0
            balloon = False
        if drumroll_length is None:
            drumroll_length = game_screen.note_type_dict[note][0].width
        source_rect = ray.Rectangle(0,0,game_screen.note_type_dict[note][0].width,game_screen.note_type_dict[note][0].height)
        dest_rect = ray.Rectangle(position-offset, 192, drumroll_length,game_screen.note_type_dict['1'][0].height)
        ray.draw_texture_pro(game_screen.note_type_dict[note][current_eighth % 2], source_rect, dest_rect, ray.Vector2(0,0), 0, ray.Color(255, draw_color, draw_color, 255))
        if balloon:
            ray.draw_texture(game_screen.note_type_dict['balloon_tail'][current_eighth % 2], position-offset+128, 192, ray.Color(255, draw_color, draw_color, 255))
        if se_note is not None:
            if drumroll_length == game_screen.note_type_dict[note][0].width:
                drumroll_length = game_screen.texture_se_moji[se_note].width
                offset = 0
            else:
                offset = 30
            source_rect = ray.Rectangle(0,0,game_screen.texture_se_moji[se_note].width,game_screen.texture_se_moji[se_note].height)
            dest_rect = ray.Rectangle(position-offset - (game_screen.texture_se_moji[se_note].width // 2) + 64, 323, drumroll_length,game_screen.texture_se_moji[se_note].height)
            ray.draw_texture_pro(game_screen.texture_se_moji[se_note], source_rect, dest_rect, ray.Vector2(0,0), 0, ray.WHITE)

    def draw_bars(self, game_screen):
        if len(self.current_bars) <= 0:
            return

        for i in range(len(self.current_bars)-1, -1, -1):
            bar = self.current_bars[i]
            load_ms, pixels_per_frame = bar['load_ms'], bar['ppf']
            position = self.get_position(game_screen, load_ms, pixels_per_frame)
            self.draw_note(game_screen, 'barline', position, 255, None)

    def draw_notes(self, game_screen):
        if len(self.current_notes_draw) <= 0:
            return

        for i in range(len(self.current_notes_draw)-1, -1, -1):
            note = self.current_notes_draw[i]
            note_type, load_ms, pixels_per_frame = note['note'], note['load_ms'], note['ppf']
            position = self.get_position(game_screen, load_ms, pixels_per_frame)
            if 'popped' in note:
                continue
            if note_type == '5':
                self.draw_drumroll(game_screen, False, position, i, note['color'])
            elif note_type == '6':
                self.draw_drumroll(game_screen, True, position, i, note['color'])
            if note_type == '7':
                self.draw_balloon(game_screen, note, position, i)
            else:
                self.draw_note(game_screen, note_type, position, 255, note['se_note'])
                #ray.draw_text(str(i), position+64, 192, 25, ray.GREEN)

    def draw(self, game_screen):
        ray.draw_texture(game_screen.texture_lane, 332, 184, ray.WHITE)
        self.draw_animation_list(game_screen, self.draw_effect_list)
        ray.draw_texture(game_screen.texture_judge_circle, 342, 184, ray.WHITE)
        self.draw_animation_list(game_screen, self.draw_judge_list)
        self.draw_bars(game_screen)
        self.draw_notes(game_screen)
        ray.draw_texture(game_screen.texture_lane_cover, 0, 184, ray.WHITE)
        ray.draw_texture(game_screen.texture_drum, 211, 206, ray.WHITE)
        self.draw_animation_list(game_screen, self.draw_drum_hit_list)
        self.draw_animation_list(game_screen, self.combo_list)
        ray.draw_texture(game_screen.texture_score_cover, 0, 184, ray.WHITE)
        ray.draw_texture(game_screen.texture_1p_emblem, 0, 225, ray.WHITE)
        ray.draw_texture(game_screen.texture_difficulty[self.difficulty], 50, 222, ray.WHITE)
        self.draw_animation_list(game_screen, self.drumroll_counter)
        self.draw_animation_list(game_screen, self.draw_arc_list)
        self.draw_animation_list(game_screen, self.balloon_list)
        self.draw_animation_list(game_screen, self.score_list)
        self.draw_animation_list(game_screen, self.base_score_list)

class Judgement:
    def __init__(self, current_ms, type, big):
        self.type = type
        self.big = big
        self.is_finished = False

        self.fade_animation_1 = Animation(current_ms, 132, 'fade')
        self.fade_animation_1.params['initial_opacity'] = 0.5
        self.fade_animation_1.params['delay'] = 100

        self.fade_animation_2 = Animation(current_ms, 316 - 233.3, 'fade')
        self.fade_animation_2.params['delay'] = 233.3

        self.move_animation = Animation(current_ms, 83, 'move')
        self.move_animation.params['total_distance'] = 15
        self.move_animation.params['start_position'] = 144

        self.texture_animation = Animation(current_ms, 100, 'texture_change')
        self.texture_animation.params['textures'] = [(33, 50, 1), (50, 83, 2), (83, 100, 3), (100, float('inf'), 4)]

    def update(self, current_ms):
        self.fade_animation_1.update(current_ms)
        self.fade_animation_2.update(current_ms)
        self.move_animation.update(current_ms)
        self.texture_animation.update(current_ms)

        if self.fade_animation_2.is_finished:
            self.is_finished = True

    def draw(self, game_screen):
        y = self.move_animation.attribute
        index = self.texture_animation.attribute
        hit_color = ray.fade(ray.WHITE, self.fade_animation_1.attribute)
        color = ray.fade(ray.WHITE, self.fade_animation_2.attribute)
        if self.type == 'GOOD':
            if self.big:
                ray.draw_texture(game_screen.texture_good_hit_center_big, 342, 184, color)
                ray.draw_texture(game_screen.texture_good_hit_effect_big[index], 304, 143, hit_color)
            else:
                ray.draw_texture(game_screen.texture_good_hit_center, 342, 184, color)
                ray.draw_texture(game_screen.texture_good_hit_effect[index], 304, 143, hit_color)
            ray.draw_texture(game_screen.texture_good, 370, int(y), color)
        elif self.type == 'OK':
            if self.big:
                ray.draw_texture(game_screen.texture_ok_hit_center_big, 342, 184, color)
                ray.draw_texture(game_screen.texture_ok_hit_effect_big[index], 304, 143, hit_color)
            else:
                ray.draw_texture(game_screen.texture_ok_hit_center, 342, 184, color)
                ray.draw_texture(game_screen.texture_ok_hit_effect[index], 304, 143, hit_color)
            ray.draw_texture(game_screen.texture_ok, 370, int(y), color)
        elif self.type == 'BAD':
            ray.draw_texture(game_screen.texture_bad, 370, int(y), color)

class LaneHitEffect:
    def __init__(self, current_ms, type):
        self.type = type
        self.color = ray.fade(ray.WHITE, 0.5)
        self.animation = Animation(current_ms, 150, 'fade')
        self.animation.params['delay'] = 83
        self.animation.params['initial_opacity'] = 0.5
        self.is_finished = False

    def update(self, current_ms):
        self.animation.update(current_ms)
        fade_opacity = self.animation.attribute
        self.color = ray.fade(ray.WHITE, fade_opacity)
        if self.animation.is_finished:
            self.is_finished = True

    def draw(self, game_screen):
        if self.type == 'GOOD':
            ray.draw_texture(game_screen.texture_lane_effect_good, 328, 192, self.color)
        elif self.type == 'DON':
            ray.draw_texture(game_screen.texture_lane_effect_don, 328, 192, self.color)
        elif self.type == 'KAT':
            ray.draw_texture(game_screen.texture_lane_effect_kat, 328, 192, self.color)

class DrumHitEffect:
    def __init__(self, current_ms, type, side):
        self.type = type
        self.side = side
        self.color = ray.fade(ray.WHITE, 1)
        self.is_finished = False
        self.animation = Animation(current_ms, 100, 'fade')
        self.animation.params['delay'] = 67

    def update(self, current_ms):
        self.animation.update(current_ms)
        fade_opacity = self.animation.attribute
        self.color = ray.fade(ray.WHITE, fade_opacity)
        if self.animation.is_finished:
            self.is_finished = True

    def draw(self, game_screen):
        x, y = 211, 206
        if self.type == 'DON':
            if self.side == 'L':
                ray.draw_texture(game_screen.texture_don_L, x, y, self.color)
            elif self.side == 'R':
                ray.draw_texture(game_screen.texture_don_R, x, y, self.color)
        elif self.type == 'KAT':
            if self.side == 'L':
                ray.draw_texture(game_screen.texture_kat_L, x, y, self.color)
            elif self.side == 'R':
                ray.draw_texture(game_screen.texture_kat_R, x, y, self.color)

class NoteArc:
    def __init__(self, note_type, current_ms, player_number):
        self.note_type = note_type
        self.arc_points = 25
        self.create_ms = current_ms
        self.player_number = player_number
        self.x_i = 414 - 64
        self.y_i = 168
        self.is_finished = False

    def update(self, current_ms):
        if self.x_i >= 1150:
            self.is_finished = True
        radius = 414
        #Start at 180 degrees, end at 0
        theta_start = 3.14
        if self.player_number == 1:
            theta_end = 2 * 3.14
            #center of circle that does not exist
            center_x, center_y = 785, 168
        else:
            theta_end = 0
            center_x, center_y = 785, 468

        ms_since_call = (current_ms - self.create_ms) / 16.67
        if ms_since_call < 0:
            ms_since_call = 0
        if ms_since_call > self.arc_points:
            ms_since_call = self.arc_points
        angle_change = (theta_end - theta_start) / self.arc_points
        theta_i = theta_start + ms_since_call * angle_change
        self.x_i = center_x + radius * math.cos(theta_i)
        self.y_i = center_y + radius * 0.5 * math.sin(theta_i)

    def draw(self, game_screen):
        if self.note_type is None:
            return
        eighth_in_ms = (60000 * 4 / game_screen.tja.bpm) / 8
        current_eighth = int(game_screen.current_ms // eighth_in_ms)
        ray.draw_texture(self.note_type[current_eighth % 2], int(self.x_i), int(self.y_i), ray.WHITE)

class DrumrollCounter:
    def __init__(self, current_ms):
        self.create_ms = current_ms
        self.is_finished = False
        self.total_duration = 1349
        self.drumroll_count = 0
        self.fade_animation = Animation(current_ms, 166, 'fade')
        self.fade_animation.params['delay'] = self.total_duration - 166
        self.stretch_animation = Animation(current_ms, 0, 'text_stretch')

    def update_count(self, current_ms, count, elapsed_time):
        self.total_duration = elapsed_time + 1349
        if self.drumroll_count != count:
            self.drumroll_count = count
            self.stretch_animation = Animation(current_ms, 50, 'text_stretch')

    def update(self, game_screen, current_ms, drumroll_count):
        self.stretch_animation.update(current_ms)
        self.fade_animation.update(current_ms)

        elapsed_time = current_ms - self.create_ms
        if drumroll_count != 0:
            self.update_count(current_ms, drumroll_count, elapsed_time)
        if self.fade_animation.is_finished:
            self.is_finished = True

    def draw(self, game_screen):
        color = ray.fade(ray.WHITE, self.fade_animation.attribute)
        ray.draw_texture(game_screen.texture_drumroll_count, 200, 0, color)
        counter = str(self.drumroll_count)
        total_width = len(counter) * 52
        start_x = 344 - (total_width // 2)
        source_rect = ray.Rectangle(0, 0, game_screen.texture_drumroll_number[0].width, game_screen.texture_drumroll_number[0].height)
        for i in range(len(counter)):
            dest_rect = ray.Rectangle(start_x + (i * 52), 50 - self.stretch_animation.attribute, game_screen.texture_drumroll_number[0].width, game_screen.texture_drumroll_number[0].height + self.stretch_animation.attribute)
            ray.draw_texture_pro(game_screen.texture_balloon_number[int(counter[i])], source_rect, dest_rect, ray.Vector2(0,0), 0, color)

class BalloonAnimation:
    def __init__(self, current_ms, balloon_total):
        self.create_ms = current_ms
        self.is_finished = False
        self.total_duration = 83.33
        self.color = ray.fade(ray.WHITE, 1.0)
        self.balloon_count = 0
        self.balloon_total = balloon_total
        self.is_popped = False
        self.fade_animation = Animation(current_ms, 166, 'fade')
        self.stretch_animation = Animation(current_ms, 0, 'text_stretch')

    def update_count(self, current_ms, balloon_count):
        if self.balloon_count != balloon_count:
            self.balloon_count = balloon_count
            self.stretch_animation = Animation(current_ms, 50, 'text_stretch')

    def update(self, game_screen, current_ms, balloon_count, is_popped):
        self.update_count(current_ms, balloon_count)
        self.stretch_animation.update(current_ms)
        self.is_popped = is_popped

        elapsed_time = current_ms - self.create_ms
        if self.is_popped:
            self.fade_animation.update(current_ms)
            self.color = ray.fade(ray.WHITE, self.fade_animation.attribute)
        else:
            self.total_duration = elapsed_time + 166
            self.fade_animation.params['delay'] = self.total_duration - 166
        if self.fade_animation.is_finished:
            self.is_finished = True

    def draw(self, game_screen):
        if self.is_popped:
            ray.draw_texture(game_screen.texture_balloon[7], 460, 130, self.color)
        elif self.balloon_count >= 1:
            balloon_index = (self.balloon_count - 1) * 7 // self.balloon_total
            ray.draw_texture(game_screen.texture_balloon[balloon_index], 460, 130, self.color)
        if self.balloon_count > 0:
            ray.draw_texture(game_screen.texture_balloon_speech_bubble_p1, 414, 40, ray.WHITE)
            counter = str(self.balloon_total - self.balloon_count + 1)
            x, y = 493, 68
            margin = 52
            total_width = len(counter) * margin
            start_x = x - (total_width // 2)
            source_rect = ray.Rectangle(0, 0, game_screen.texture_balloon_number[0].width, game_screen.texture_balloon_number[0].height)
            for i in range(len(counter)):
                dest_rect = ray.Rectangle(start_x + (i * margin), y - self.stretch_animation.attribute, game_screen.texture_balloon_number[0].width, game_screen.texture_balloon_number[0].height + self.stretch_animation.attribute)
                ray.draw_texture_pro(game_screen.texture_balloon_number[int(counter[i])], source_rect, dest_rect, ray.Vector2(0,0), 0, self.color)

class Combo:
    def __init__(self, combo, current_ms):
        self.combo = combo
        self.stretch_animation = Animation(current_ms, 0, 'text_stretch')
        self.color = [ray.fade(ray.WHITE, 1), ray.fade(ray.WHITE, 1), ray.fade(ray.WHITE, 1)]
        self.glimmer_dict = {0: 0, 1: 0, 2: 0}
        self.total_time = 250
        self.cycle_time = self.total_time * 2
        self.start_times = [
                    current_ms,
                    current_ms + (2 / 3) * self.cycle_time,
                    current_ms + (4 / 3) * self.cycle_time
                ]

    def update_count(self, current_ms, combo):
        if self.combo != combo:
            self.combo = combo
            self.stretch_animation = Animation(current_ms, 50, 'text_stretch')

    def update(self, game_screen, current_ms, combo):
        self.update_count(current_ms, combo)
        self.stretch_animation.update(current_ms)

        for i in range(3):
            elapsed_time = current_ms - self.start_times[i]
            if elapsed_time > self.cycle_time:
                cycles_completed = elapsed_time // self.cycle_time
                self.start_times[i] += cycles_completed * self.cycle_time
                elapsed_time = current_ms - self.start_times[i]
            if elapsed_time <= self.total_time:
                self.glimmer_dict[i] = -int(elapsed_time // 16.67)
                fade_start_time = self.total_time - 164
                if elapsed_time >= fade_start_time:
                    fade = 1 - (elapsed_time - fade_start_time) / 164
                else:
                    fade = 1
            else:
                self.glimmer_dict[i] = 0
                fade = 0
            self.color[i] = ray.fade(ray.WHITE, fade)

    def draw(self, game_screen):
        if self.combo < 100:
            text_color = 0
            margin = 30
        else:
            text_color = 1
            margin = 35
        ray.draw_texture(game_screen.texture_combo_text[text_color], 234, 265, ray.WHITE)
        counter = str(self.combo)
        total_width = len(counter) * margin
        x, y = 262, 220
        start_x = x - (total_width // 2)
        source_rect = ray.Rectangle(0, 0, game_screen.texture_combo_numbers[0].width, game_screen.texture_combo_numbers[0].height)
        for i in range(len(counter)):
            dest_rect = ray.Rectangle(start_x + (i * margin), y - self.stretch_animation.attribute, game_screen.texture_combo_numbers[0].width, game_screen.texture_combo_numbers[0].height + self.stretch_animation.attribute)
            ray.draw_texture_pro(game_screen.texture_combo_numbers[int(counter[i]) + (text_color*10)], source_rect, dest_rect, ray.Vector2(0,0), 0, ray.WHITE)
        glimmer_positions = [(225, 210), (200, 230), (250, 230)]
        if self.combo >= 100:
            for j, (x, y) in enumerate(glimmer_positions):
                for i in range(3):
                    ray.draw_texture(game_screen.texture_combo_glimmer, x + (i * 30), y + self.glimmer_dict[j], self.color[j])

class ScoreCounter:
    def __init__(self, score, current_ms):
        self.score = score
        self.create_ms = current_ms
        self.stretch_animation = Animation(current_ms, 0, 'text_stretch')

    def update_count(self, current_ms, score):
        if self.score != score:
            self.score = score
            self.stretch_animation = Animation(current_ms, 50, 'text_stretch')

    def update(self, current_ms, score):
        self.update_count(current_ms, score)
        self.stretch_animation.update(current_ms)

    def draw(self, game_screen):
        counter = str(self.score)
        x, y = 150, 185
        margin = 20
        total_width = len(counter) * margin
        start_x = x - total_width
        source_rect = ray.Rectangle(0, 0, game_screen.texture_score_numbers[0].width, game_screen.texture_score_numbers[0].height)
        for i in range(len(counter)):
            dest_rect = ray.Rectangle(start_x + (i * margin), y - self.stretch_animation.attribute, game_screen.texture_score_numbers[0].width, game_screen.texture_score_numbers[0].height + self.stretch_animation.attribute)
            ray.draw_texture_pro(game_screen.texture_score_numbers[int(counter[i])], source_rect, dest_rect, ray.Vector2(0,0), 0, ray.WHITE)

class ScoreCounterAnimation:
    def __init__(self, current_ms, counter):
        self.counter = int(counter)
        self.fade_animation_1 = Animation(current_ms, 50, 'fade')
        self.fade_animation_1.params['initial_opacity'] = 0.0
        self.fade_animation_1.params['final_opacity'] = 1.0

        self.move_animation_1 = Animation(current_ms, 80, 'move')
        self.move_animation_1.params['total_distance'] = -20
        self.move_animation_1.params['start_position'] = 175

        self.fade_animation_2 = Animation(current_ms, 80, 'fade')
        self.fade_animation_2.params['delay'] = 366.74

        self.move_animation_2 = Animation(current_ms, 66, 'move')
        self.move_animation_2.params['total_distance'] = 5
        self.move_animation_2.params['start_position'] = 145
        self.move_animation_2.params['delay'] = 80

        self.move_animation_3 = Animation(current_ms, 66, 'move')
        self.move_animation_3.params['delay'] = 279.36
        self.move_animation_3.params['total_distance'] = -2
        self.move_animation_3.params['start_position'] = 146

        self.move_animation_4 = Animation(current_ms, 80, 'move')
        self.move_animation_4.params['delay'] = 366.74
        self.move_animation_4.params['total_distance'] = 10
        self.move_animation_4.params['start_position'] = 148

        self.color = ray.fade(ray.Color(254, 102, 0, 255), 1.0)
        self.is_finished = False
        self.y_pos_list = []

    def update(self, current_ms):
        self.fade_animation_1.update(current_ms)
        self.move_animation_1.update(current_ms)
        self.move_animation_2.update(current_ms)
        self.move_animation_3.update(current_ms)
        self.move_animation_4.update(current_ms)
        self.fade_animation_2.update(current_ms)

        if self.fade_animation_1.is_finished:
            self.color = ray.fade(ray.Color(254, 102, 0, 255), self.fade_animation_2.attribute)
        else:
            self.color = ray.fade(ray.Color(254, 102, 0, 255), self.fade_animation_1.attribute)
        if self.fade_animation_2.is_finished:
            self.is_finished = True
        self.y_pos_list = []
        for i in range(1, len(str(self.counter))+1):
            self.y_pos_list.append(self.move_animation_4.attribute + i*5)

    def draw(self, game_screen):
        if self.move_animation_1.is_finished:
            x = self.move_animation_2.attribute
        else:
            x = self.move_animation_1.attribute
        if x == 0:
            return
        counter = str(self.counter)
        margin = 20
        total_width = len(counter) * margin
        start_x = x - total_width
        source_rect = ray.Rectangle(0, 0, game_screen.texture_base_score_numbers[0].width, game_screen.texture_base_score_numbers[0].height)
        for i in range(len(counter)):
            if self.move_animation_3.is_finished:
                y = self.y_pos_list[i]
            elif self.move_animation_2.is_finished:
                y = self.move_animation_3.attribute
            else:
                y = 148
            dest_rect = ray.Rectangle(start_x + (i * margin), y, game_screen.texture_base_score_numbers[0].width, game_screen.texture_base_score_numbers[0].height)
            ray.draw_texture_pro(game_screen.texture_base_score_numbers[int(counter[i])], source_rect, dest_rect, ray.Vector2(0,0), 0, self.color)
