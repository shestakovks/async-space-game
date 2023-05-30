import itertools
import os.path
from os import listdir
from typing import Iterable

from constants import GARBAGE_DIR


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
    garbage_frame_files = [os.path.join(GARBAGE_DIR, f) for f in listdir(GARBAGE_DIR)]
    frames = []

    for garbage_frame_file in garbage_frame_files:
        with open(garbage_frame_file) as f:
            frames.append(f.read())

    return frames
