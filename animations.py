import itertools
from typing import Iterable


def load_starship_frames() -> Iterable[str]:
    starship_frame_files = [
        'animations/rocket_frame_1.txt',
        'animations/rocket_frame_2.txt',
    ]
    frames = []
    for path in starship_frame_files:
        with open(path) as f:
            starship_frame = f.read()
            frames.extend([starship_frame, starship_frame])
    return itertools.cycle(frames)
