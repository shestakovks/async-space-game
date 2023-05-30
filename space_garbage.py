import asyncio
from typing import TYPE_CHECKING

from obstacles import Obstacle
from utils import draw_frame, get_frame_size

obstacles = []
obstacles_in_last_collision: list[Obstacle] = []

if TYPE_CHECKING:
    import curses


async def fly_garbage(
    canvas: 'curses.window',
    column: int,
    garbage_frame: str,
    speed: int | float = 0.5,
) -> None:
    """Animate garbage, flying from top to bottom.
    Column position will stay same, as specified on start."""
    rows_number, columns_number = canvas.getmaxyx()

    column = max(column, 0)
    column = min(column, columns_number - 1)

    row: int | float = 0

    rows_size, columns_size = get_frame_size(garbage_frame)
    obstacle = Obstacle(round(row), column, rows_size, columns_size)
    obstacles.append(obstacle)

    try:
        while row < rows_number:
            if obstacle in obstacles_in_last_collision:
                obstacles_in_last_collision.remove(obstacle)
                break

            draw_frame(canvas, row, column, garbage_frame)
            await asyncio.sleep(0)
            draw_frame(canvas, row, column, garbage_frame, negative=True)
            row += speed
            obstacle.row = round(row)
    finally:
        obstacles.remove(obstacle)
