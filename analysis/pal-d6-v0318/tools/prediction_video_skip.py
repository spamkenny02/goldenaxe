"""Optional secondary-core video suppression; primary gameplay is unchanged.

This keeps audio and the normal snapshot format. Every selected prediction
still needs the existing full-RAM check and an official cold input replay.
"""
import ctypes as c
from natural_boss_lookahead import Secondary
from run_core import ENV


def enable_prediction_video_skip(secondary):
    original = secondary.callbacks[0]

    @ENV
    def environment(command, data):
        if command & 65535 == 47:
            # Audio enabled; video and fast/altered audio states disabled.
            c.cast(data, c.POINTER(c.c_int))[0] = 2
            return True
        return original(command, data)

    secondary.callbacks.append(environment)
    secondary.dll.retro_set_environment(environment)


class PredictionVideoSkip(Secondary):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        enable_prediction_video_skip(self)
