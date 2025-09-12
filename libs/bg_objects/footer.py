from libs.texture import TextureWrapper

class Footer:
    def __init__(self, tex: TextureWrapper, index: int):
        self.index = index
        if self.index == -1:
            return
        tex.load_zip('background/regular', 'footer')
    def draw(self, tex: TextureWrapper):
        if self.index == -1:
            return
        tex.draw_texture('footer', str(self.index))
