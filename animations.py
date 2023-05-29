import itertools
from typing import Iterable


def load_spaceship_frames() -> Iterable[str]:
    spaceship_frame_files = [
        'animations/rocket_frame_1.txt',
        'animations/rocket_frame_2.txt',
    ]
    frames = []
    for path in spaceship_frame_files:
        with open(path) as f:
            spaceship_frame = f.read()
            frames.extend([spaceship_frame, spaceship_frame])
    return itertools.cycle(frames)


def load_garbage_frames() -> list[str]:
    garbage_frame_files = [
        'animations/trash_small.txt',
        'animations/trash_large.txt',
        'animations/trash_x1.txt',
        'animations/duck.txt',
        'animations/hubble.txt',
        'animations/lamp.txt',
    ]
    frames = []
    for path in garbage_frame_files:
        with open(path) as f:
            garbage_frame = f.read()
            frames.append(garbage_frame)
    return frames
