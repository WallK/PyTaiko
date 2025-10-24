from libs.file_navigator import SongFile
from libs.transition import Transition
from scenes.song_select import DiffSortSelect, SongSelectPlayer, SongSelectScreen, State
from libs.utils import get_current_ms, global_data
from libs.audio import audio

class TwoPlayerSongSelectScreen(SongSelectScreen):
    def on_screen_start(self):
        if not self.screen_init:
            super().on_screen_start()
            self.player_1 = SongSelectPlayer('1', self.text_fade_in)
            self.player_2 = SongSelectPlayer('2', self.text_fade_in)

    def finalize_song(self):
        global_data.selected_song = self.navigator.get_current_item().path
        global_data.session_data[0].genre_index = self.navigator.get_current_item().box.name_texture_index

    def handle_input_browsing(self):
        """Handle input for browsing songs."""
        action = self.player_1.handle_input_browsing(self.last_moved, self.navigator.items[self.navigator.selected_index] if self.navigator.items else None)
        if action is None:
            action = self.player_2.handle_input_browsing(self.last_moved, self.navigator.items[self.navigator.selected_index] if self.navigator.items else None)
            if action is None:
                return

        current_time = get_current_ms()
        if action == "skip_left":
            self.reset_demo_music()
            for _ in range(10):
                self.navigator.navigate_left()
            self.last_moved = current_time
        elif action == "skip_right":
            self.reset_demo_music()
            for _ in range(10):
                self.navigator.navigate_right()
            self.last_moved = current_time
        elif action == "navigate_left":
            self.reset_demo_music()
            self.navigator.navigate_left()
            self.last_moved = current_time
        elif action == "navigate_right":
            self.reset_demo_music()
            self.navigator.navigate_right()
            self.last_moved = current_time
        elif action == "go_back":
            self.navigator.go_back()
        elif action == "diff_sort":
            self.state = State.DIFF_SORTING
            self.diff_sort_selector = DiffSortSelect(self.navigator.diff_sort_statistics, self.navigator.diff_sort_diff, self.navigator.diff_sort_level)
            self.text_fade_in.start()
            self.text_fade_out.start()
        elif action == "select_song":
            selected_song = self.navigator.select_current_item()
            if selected_song:
                self.state = State.SONG_SELECTED
                self.player_1.on_song_selected(selected_song)
                audio.play_sound('don', 'sound')
                audio.play_sound('voice_select_diff', 'voice')
                self.move_away.start()
                self.diff_fade_out.start()
                self.text_fade_out.start()
                self.text_fade_in.start()
                self.player_1.selected_diff_bounce.start()
                self.player_1.selected_diff_fadein.start()
                self.player_2.selected_diff_bounce.start()
                self.player_2.selected_diff_fadein.start()
        elif action == "add_favorite":
            self.navigator.add_favorite()
            current_box = self.navigator.get_current_item().box
            current_box.is_favorite = not current_box.is_favorite

    def handle_input_selected(self):
        """Handle input for selecting difficulty."""
        p2_result = False
        result = self.player_1.handle_input_selected(self.navigator.get_current_item())
        if result is None:
            result = self.player_2.handle_input_selected(self.navigator.get_current_item())
            if result is None:
                return
            p2_result = True
        if result is not None:
            print(result, p2_result)
        if result == "cancel":
            self._cancel_selection()
        elif result == "confirm":
            if p2_result:
                self._confirm_selection(2)
            else:
                self._confirm_selection(1)
        elif result == "ura_toggle":
            if p2_result:
                self.ura_switch_animation.start(not self.player_2.is_ura)
            else:
                self.ura_switch_animation.start(not self.player_1.is_ura)

    def handle_input_diff_sort(self):
        """
        Handle input for sorting difficulty.
        """
        if self.diff_sort_selector is None:
            raise Exception("Diff sort selector was not able to be created")

        result = self.player_1.handle_input_diff_sort(self.diff_sort_selector)

        if result is not None:
            diff, level = result
            self.diff_sort_selector = None
            self.state = State.BROWSING
            self.text_fade_out.reset()
            self.text_fade_in.reset()
            if diff != -1:
                if level != -1:
                    self.navigator.diff_sort_diff = diff
                    self.navigator.diff_sort_level = level
                self.navigator.select_current_item()

    def _cancel_selection(self):
        """Reset to browsing state"""
        super()._cancel_selection()
        self.player_2.selected_song = None

    def _confirm_selection(self, player_selected: int):
        """Confirm song selection and create game transition"""
        audio.play_sound('don', 'sound')
        audio.play_sound(f'voice_start_song_{global_data.player_num}p', 'voice')
        if player_selected == 1:
            global_data.session_data[0].selected_difficulty = self.player_1.selected_difficulty
            self.player_1.selected_diff_highlight_fade.start()
            self.player_1.selected_diff_text_resize.start()
            self.player_1.selected_diff_text_fadein.start()
        elif player_selected == 2:
            global_data.session_data[1].selected_difficulty = self.player_2.selected_difficulty
            self.player_2.selected_diff_highlight_fade.start()
            self.player_2.selected_diff_text_resize.start()
            self.player_2.selected_diff_text_fadein.start()

    def check_for_selection(self):
        if (self.player_1.selected_diff_highlight_fade.is_finished and
            self.player_2.selected_diff_highlight_fade.is_finished and
            not audio.is_sound_playing(f'voice_start_song_{global_data.player_num}p') and self.game_transition is None):
            selected_song = self.navigator.get_current_item()
            if not isinstance(selected_song, SongFile):
                raise Exception("picked directory")

            title = selected_song.tja.metadata.title.get(
                global_data.config['general']['language'], '')
            subtitle = selected_song.tja.metadata.subtitle.get(
                global_data.config['general']['language'], '')
            self.game_transition = Transition(title, subtitle)
            self.game_transition.start()

    def update_players(self, current_time):
        self.player_1.update(current_time)
        self.player_2.update(current_time)
        if self.text_fade_out.is_finished:
            self.player_1.selected_song = True
            self.player_2.selected_song = True
        return "GAME_2P"

    def draw_background_diffs(self):
        self.player_1.draw_background_diffs(self.state)
        self.player_2.draw_background_diffs(self.state)

    def draw_players(self):
        self.player_1.draw(self.state)
        self.player_2.draw(self.state)
