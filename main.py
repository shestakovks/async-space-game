import asyncio
import curses
import itertools
import random
import time
from contextlib import suppress
from typing import Iterable

from animations import load_spaceship_frames, load_garbage_frames
from constants import (
    TIC_TIMEOUT,
    STAR_SYMBOLS,
    YEAR_BLOCK_HEIGHT,
    YEAR_BLOCK_WIDTH,
    BORDER_OFFSET,
    GUN_AVAILABLE_YEAR,
)
from explosion import explode
from game_over import GAME_OVER_FRAME
from game_scenario import get_garbage_delay_tics, PHRASES
from physics import update_speed
from space_garbage import fly_garbage, obstacles, obstacles_in_last_collision
from utils import get_frame_size, read_controls, draw_frame, get_canvas_borders

coroutines = []
year = 1957


async def sleep(counter: int = 1) -> None:
    for _ in range(counter):
        await asyncio.sleep(0)


async def show_game_over(canvas: curses.window) -> None:
    max_height, max_width = canvas.getmaxyx()
    frame_height, frame_width = get_frame_size(GAME_OVER_FRAME)
    row = max_height // 2 - frame_height // 2
    col = max_width // 2 - frame_width // 2
    while True:
        draw_frame(canvas, row, col, GAME_OVER_FRAME)
        await sleep()


async def fire(
    canvas: curses.window,
    row_start: int | float,
    col_start: int | float,
    row_speed: int | float = -0.3,
    col_speed: int | float = 0,
) -> None:
    """Display animation of gun shot, direction and speed can be specified."""

    row, col = row_start, col_start

    draw_frame(canvas, row, col, '*')
    await sleep()

    draw_frame(canvas, row, col, '0')
    await sleep()

    draw_frame(canvas, row, col, '0', negative=True)

    row += row_speed
    col += col_speed

    curses.beep()

    symbol = '-' if col_speed else '|'

    await animate_fire(canvas, row, col, row_speed, col_speed, symbol)


async def animate_fire(
    canvas: curses.window,
    row: int | float,
    col: int | float,
    row_speed: int | float,
    col_speed: int | float,
    symbol: str,
) -> None:
    row_min, row_max, col_min, col_max = get_canvas_borders(canvas)
    while row_min < row < row_max and col_min < col < col_max:

        for obstacle in obstacles:
            if obstacle.has_collision(round(row), round(col)):
                obstacles_in_last_collision.append(obstacle)
                coroutines.append(explode(canvas, row, col))
                return

        draw_frame(canvas, row, col, symbol)
        await asyncio.sleep(0)
        draw_frame(canvas, row, col, symbol, negative=True)
        row += row_speed
        col += col_speed


async def fill_sky_with_stars(canvas: curses.window) -> None:
    for _ in range(random.randint(75, 150)):
        row_min, row_max, col_min, col_max = get_canvas_borders(canvas)
        row = random.randint(row_min, row_max)
        col = random.randint(col_min, col_max)
        symbol = random.choice(STAR_SYMBOLS)
        initial_blink_delay = random.randint(0, 30)

        coroutines.append(blink(canvas, row, col, symbol, initial_blink_delay))


async def blink(
    canvas: curses.window, row: int, col: int, symbol: str, initial_blink_delay: int,
) -> None:
    blinking_params = [
        (int(2 / TIC_TIMEOUT), curses.A_DIM),
        (int(0.3 / TIC_TIMEOUT), curses.A_NORMAL),
        (int(0.5 / TIC_TIMEOUT), curses.A_BOLD),
        (int(0.3 / TIC_TIMEOUT), curses.A_NORMAL),
    ]

    _, initial_display_option = blinking_params[0]
    canvas.addstr(row, col, symbol, initial_display_option)
    await sleep(initial_blink_delay)
    await animate_blink(canvas, row, col, symbol, blinking_params)


async def animate_blink(
    canvas: curses.window,
    row: int,
    col: int,
    symbol: str,
    blinking_params: list[tuple[int, int]],
) -> None:
    for blink_timeout, display_option in itertools.cycle(blinking_params):
        canvas.addstr(row, col, symbol, display_option)
        await sleep(blink_timeout)


async def draw_spaceship(
    canvas: curses.window,
    row_start: int,
    col_start: int,
    spaceship_frames: Iterable[str],
) -> None:
    row_speed, col_speed = 0, 0
    await animate_spaceship(
        canvas, row_start, col_start, row_speed, col_speed, spaceship_frames,
    )


async def animate_spaceship(
    canvas: curses.window,
    row: int | float,
    col: int | float,
    row_speed: int | float,
    col_speed: int | float,
    spaceship_frames: Iterable[str],
) -> None:
    row_min, row_max, col_min, col_max = get_canvas_borders(canvas)
    for starship_frame in spaceship_frames:

        for obstacle in obstacles:
            if obstacle.has_collision(round(row), round(col)):
                await show_game_over(canvas)
                return

        frame_row, frame_col = get_frame_size(starship_frame)
        rows_dir, cols_dir, space_pressed = read_controls(canvas)

        row_speed, col_speed = update_speed(
            row_speed, col_speed, rows_dir, cols_dir,
        )
        row, col = row + row_speed, col + col_speed

        row = min(max(row, row_min), row_max - frame_row)
        col = min(max(col, col_min), col_max - frame_col)

        if space_pressed and year >= GUN_AVAILABLE_YEAR:
            coroutines.append(fire(canvas, row, col + 2))

        draw_frame(canvas, row, col, starship_frame)
        await sleep()
        draw_frame(canvas, row, col, starship_frame, negative=True)


async def fill_orbit_with_garbage(
    canvas: curses.window, garbage_frames: list[str],
) -> None:
    _, _, col_min, col_max = get_canvas_borders(canvas)
    await add_garbage_to_space(canvas, col_min, col_max, garbage_frames)


async def add_garbage_to_space(
    canvas: curses.window, col_min: int, col_max: int, garbage_frames: list[str],
) -> None:
    while True:
        if (garbage_delay_ticks := get_garbage_delay_tics(year)) is None:
            await sleep()
            continue

        col = random.randint(col_min, col_max)
        garbage_frame = random.choice(garbage_frames)
        coroutines.append(fly_garbage(canvas, col, garbage_frame))
        await sleep(garbage_delay_ticks)


async def show_year(year_block: curses.window) -> None:
    global year
    while True:
        year_block.addstr(
            BORDER_OFFSET,
            YEAR_BLOCK_WIDTH - len(str(year)) - BORDER_OFFSET,
            str(year),
            curses.A_BOLD,
        )
        if (phrase := PHRASES.get(year)) is not None:
            draw_frame(
                year_block,
                BORDER_OFFSET * 2,
                YEAR_BLOCK_WIDTH - len(phrase) - BORDER_OFFSET,
                phrase,
            )
        await sleep(15)
        if phrase is not None:
            draw_frame(
                year_block,
                BORDER_OFFSET * 2,
                YEAR_BLOCK_WIDTH - len(phrase) - BORDER_OFFSET,
                phrase,
                negative=True,
            )
        year += 1


def setup_canvas(canvas: curses.window) -> None:
    curses.curs_set(False)
    canvas.border()
    canvas.nodelay(True)
    canvas.refresh()


def create_year_block(canvas: curses.window) -> curses.window:
    max_height, max_width = canvas.getmaxyx()

    year_block = canvas.derwin(
        YEAR_BLOCK_HEIGHT,
        YEAR_BLOCK_WIDTH,
        BORDER_OFFSET,
        max_width - YEAR_BLOCK_WIDTH - 2 * BORDER_OFFSET,
    )

    year_block.immedok(True)
    year_block.nodelay(True)
    year_block.refresh()

    return year_block


def draw(canvas: curses.window) -> None:
    setup_canvas(canvas)

    max_height, max_width = canvas.getmaxyx()
    row_center = max_height // 2
    col_center = max_width // 2

    spaceship_frames = load_spaceship_frames()
    garbage_frames = load_garbage_frames()

    year_block = create_year_block(canvas)

    coroutines.append(show_year(year_block))
    coroutines.append(
        draw_spaceship(canvas, row_center, col_center, spaceship_frames),
    )
    coroutines.append(fill_orbit_with_garbage(canvas, garbage_frames))
    coroutines.append(fill_sky_with_stars(canvas))

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
