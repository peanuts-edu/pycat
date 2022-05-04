class Animator:
    def __init__(self, animations = None):
        self._animations = {} if animations is None else animations
        self._timer = 0
        self._frame = None
        self._frame_idx = 0
        self._current_animation = None
        self._speed = 0.2

        self._is_playing = False

    def tick(self, dt: float):
        if not self._is_playing:
            return self._frame

        self._timer += dt
        
        if self._timer > self._speed:
            self._timer = 0            

            animation = self._animations[self._current_animation]
            if self._frame_idx == len(animation)-1:
                self._frame_idx = 0
            else:
                self._frame_idx += 1
            self._frame = animation[self._frame_idx]

        return self._frame

    def add(self, name: str, images):
        self._animations[name] = images

    def play(self, name: str):        
        if self._current_animation == name:
            return
        self._current_animation = name
        self.reset_to_first_frame()
        self._is_playing = True

    def stop(self):
        self._is_playing = False

    def reset_to_first_frame(self):
        self._timer = 0  
        self._frame_idx = 0
        self._frame = self._animations[self._current_animation][self._frame_idx]


    @property
    def speed(self):
        return self._speed

    @speed.setter
    def speed(self, speed):
        self._speed = speed