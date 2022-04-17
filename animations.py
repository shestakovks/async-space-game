import itertools
from typing import Iterable


def load_starship_animations() -> Iterable[str]:
    starship_animations_files = [
        'animations/rocket_frame_1.txt',
        'animations/rocket_frame_2.txt',
    ]
    animations = []
    for path in starship_animations_files:
        with open(path) as f:
            animations.append(f.read())
    return itertools.cycle(animations)
