import pyray as ray

class DevScreen:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.screen_init = False
        self.model = ray.load_model("model/mikudon.obj")
        self.model_position = ray.Vector3(-450.0, 100.0, -180.0)
        self.model_scale = 1000.0
        self.model_rotation_y = 45.0  # Face towards camera (rotate 180 degrees on Y-axis)
        self.model_rotation_x = 0.0    # No up/down tilt
        self.model_rotation_z = 0.0    # No roll

    def on_screen_start(self):
        if not self.screen_init:
            self.screen_init = True

    def on_screen_end(self, next_screen: str):
        self.screen_init = False
        ray.unload_model(self.model)
        return next_screen

    def update(self):
        self.on_screen_start()

        if ray.is_key_pressed(ray.KeyboardKey.KEY_ENTER):
            return self.on_screen_end('GAME')

    def draw(self):
        pass

    def draw_3d(self):
        # Method 1: Using draw_model_ex for full control over rotation
        rotation_axis = ray.Vector3(0.0, 1.0, 0.0)  # Y-axis for horizontal rotation
        ray.draw_model_ex(
            self.model,
            self.model_position,
            rotation_axis,
            self.model_rotation_y,
            ray.Vector3(self.model_scale, self.model_scale, self.model_scale),
            ray.WHITE
        )
