import asyncio
import curses
import random
import time
from contextlib import suppress
import itertools
from typing import Coroutine, Union, Any, Iterable

from animations import load_starship_frames
from constants import TIC_TIMEOUT, BORDER_OFFSET, STAR_SYMBOLS
from utils import get_frame_size, read_controls, draw_frame


async def sleep(counter: int = 1) -> None:
    for _ in range(counter):
        await asyncio.sleep(0)


async def fire(
    canvas: curses.window,
    start_row: Union[int, float],
    start_column: Union[int, float],
    rows_speed: Union[int, float] = -0.3,
    columns_speed: Union[int, float] = 0,
) -> None:
    """Display animation of gun shot, direction and speed can be specified."""

    row, column = start_row, start_column

    canvas.addstr(round(row), round(column), '*')
    await asyncio.sleep(0)

    canvas.addstr(round(row), round(column), 'O')
    await asyncio.sleep(0)
    canvas.addstr(round(row), round(column), ' ')

    row += rows_speed
    column += columns_speed

    symbol = '-' if columns_speed else '|'

    rows, columns = canvas.getmaxyx()
    max_row, max_column = rows - 1, columns - 1

    curses.beep()

    while 0 < row < max_row and 0 < column < max_column:
        canvas.addstr(round(row), round(column), symbol)
        await asyncio.sleep(0)
        canvas.addstr(round(row), round(column), ' ')
        row += rows_speed
        column += columns_speed


async def blink(
    canvas: curses.window,
    row: int,
    column: int,
    initial_blink_delay: int,
    symbol: str = '*',
) -> None:
    blinking_params = [
        (int(2 / TIC_TIMEOUT), curses.A_DIM),
        (int(0.3 / TIC_TIMEOUT), curses.A_NORMAL),
        (int(0.5 / TIC_TIMEOUT), curses.A_BOLD),
        (int(0.3 / TIC_TIMEOUT), curses.A_NORMAL),
    ]

    _, initial_display_option = blinking_params[0]
    canvas.addstr(row, column, symbol, initial_display_option)
    await sleep(initial_blink_delay)

    for blink_timeout, display_option in itertools.cycle(blinking_params):
        canvas.addstr(row, column, symbol, display_option)
        await sleep(blink_timeout)


async def animate_spaceship(
    canvas: curses.window,
    start_row: int,
    start_column: int,
    starship_frames: Iterable[str],
) -> None:
    row, col = start_row, start_column
    row_speed, col_speed = 3, 3
    row_min, col_min = BORDER_OFFSET, BORDER_OFFSET
    row_max, col_max = canvas.getmaxyx()
    for starship_frame in starship_frames:
        frame_row, frame_col = get_frame_size(starship_frame)
        rows_dir, cols_dir, space_pressed = read_controls(canvas)
        row = row + rows_dir * row_speed
        col = col + cols_dir * col_speed

        row = min(max(row, row_min), row_max - frame_row - BORDER_OFFSET)
        col = min(max(col, col_min), col_max - frame_col - BORDER_OFFSET)

        draw_frame(canvas, row, col, starship_frame)
        await sleep()
        draw_frame(canvas, row, col, starship_frame, negative=True)


def get_blink_coroutine(
        canvas: curses.window, max_height: int, max_width: int,
) -> Coroutine[Any, Any, None]:
    row = random.randint(BORDER_OFFSET, max_height - BORDER_OFFSET)
    col = random.randint(BORDER_OFFSET, max_width - BORDER_OFFSET)
    symbol = random.choice(STAR_SYMBOLS)
    initial_blink_delay = random.randint(0, 30)
    return blink(canvas, row, col, initial_blink_delay, symbol)


def setup_canvas(canvas: curses.window) -> None:
    curses.curs_set(False)
    canvas.border()
    canvas.nodelay(True)
    canvas.refresh()


def draw(canvas: curses.window) -> None:
    setup_canvas(canvas)

    coroutines = []
    max_height, max_width = canvas.getmaxyx()
    row_center = max_height // 2
    col_center = max_width // 2

    starship_frames = load_starship_frames()
    coroutines.append(
        animate_spaceship(canvas, row_center, col_center, starship_frames)
    )
    coroutines.append(fire(canvas, row_center, col_center))
    for _ in range(random.randint(75, 150)):
        coroutines.append(get_blink_coroutine(canvas, max_height, max_width))

    while True:
        for coroutine in coroutines.copy():
            try:
                coroutine.send(None)
            except StopIteration:
                coroutines.remove(coroutine)
        canvas.refresh()
        time.sleep(TIC_TIMEOUT)


if __name__ == '__main__':
    curses.update_lines_cols()
    with suppress(KeyboardInterrupt):
        curses.wrapper(draw)
