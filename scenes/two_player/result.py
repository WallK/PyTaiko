from libs.utils import get_current_ms
from scenes.result import Background, FadeIn, ResultPlayer, ResultScreen

class TwoPlayerResultScreen(ResultScreen):
    def __init__(self):
        super().__init__()

    def on_screen_start(self):
        if not self.screen_init:
            super().on_screen_start()
            self.background = Background('3', self.width)
            self.fade_in = FadeIn('3')
            self.player_1 = ResultPlayer('1', True, False)
            self.player_2 = ResultPlayer('2', True, True)

    def update(self):
        self.on_screen_start()
        current_time = get_current_ms()
        self.fade_in.update(current_time)
        self.player_1.update(current_time, self.fade_in.is_finished, self.is_skipped)
        self.player_2.update(current_time, self.fade_in.is_finished, self.is_skipped)

        if current_time >= self.start_ms + 5000 and not self.fade_out.is_started:
            self.handle_input()

        self.fade_out.update(current_time)
        if self.fade_out.is_finished:
            self.fade_out.update(current_time)
            return self.on_screen_end("SONG_SELECT_2P")

    def draw(self):
        self.background.draw()
        self.draw_song_info()
        self.player_1.draw()
        self.player_2.draw()
        self.draw_overlay()
