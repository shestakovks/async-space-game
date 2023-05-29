import asyncio
from typing import Generator, TYPE_CHECKING

from utils import draw_frame

if TYPE_CHECKING:
    import curses


class Obstacle:

    def __init__(
            self,
            row: int,
            column: int,
            rows_size: int = 1,
            columns_size: int = 1,
            uid: str | None = None,
    ) -> None:
        self.row = row
        self.column = column
        self.rows_size = rows_size
        self.columns_size = columns_size
        self.uid = uid

    def get_bounding_box_frame(self) -> str:
        # increment box size to compensate obstacle movement
        rows, columns = self.rows_size, self.columns_size
        return '\n'.join(_get_bounding_box_lines(rows, columns))

    def get_bounding_box_corner_pos(self) -> tuple[int, int]:
        return self.row - 1, self.column - 1

    def dump_bounding_box(self) -> tuple[int, int, str]:
        row, column = self.get_bounding_box_corner_pos()
        return row, column, self.get_bounding_box_frame()

    def has_collision(
            self,
            obj_corner_row: int,
            obj_corner_column: int,
            obj_size_rows: int = 1,
            obj_size_columns: int = 1,
    ) -> bool:
        """Determine if collision has occurred. Return True or False."""
        return has_collision(
            (self.row, self.column),
            (self.rows_size, self.columns_size),
            (obj_corner_row, obj_corner_column),
            (obj_size_rows, obj_size_columns),
        )


def _get_bounding_box_lines(rows: int, columns: int) -> Generator[str, None, None]:
    yield ' ' + '-' * columns + ' '
    for _ in range(rows):
        yield '|' + ' ' * columns + '|'
    yield ' ' + '-' * columns + ' '


async def show_obstacles(canvas: 'curses.window', obstacles: list[Obstacle]) -> None:
    """Display bounding boxes of every obstacle in a list"""

    while True:
        boxes = []

        for obstacle in obstacles:
            boxes.append(obstacle.dump_bounding_box())

        for row, column, frame in boxes:
            draw_frame(canvas, row, column, frame)

        await asyncio.sleep(0)

        for row, column, frame in boxes:
            draw_frame(canvas, row, column, frame, negative=True)


def _is_point_inside(
        corner_row: int,
        corner_column: int,
        size_rows: int,
        size_columns: int,
        point_row: int,
        point_row_column: int,
) -> bool:
    rows_flag = corner_row <= point_row < corner_row + size_rows
    columns_flag = corner_column <= point_row_column < corner_column + size_columns

    return rows_flag and columns_flag


def has_collision(
        obstacle_corner: tuple[int, int],
        obstacle_size: tuple[int, int],
        obj_corner: tuple[int, int],
        obj_size: tuple[int, int] = (1, 1),
) -> bool:
    """Determine if collision has occurred. Return True or False."""

    opposite_obstacle_corner = (
        obstacle_corner[0] + obstacle_size[0] - 1,
        obstacle_corner[1] + obstacle_size[1] - 1,
    )

    opposite_obj_corner = (
        obj_corner[0] + obj_size[0] - 1,
        obj_corner[1] + obj_size[1] - 1,
    )

    return any([
        _is_point_inside(*obstacle_corner, *obstacle_size, *obj_corner),
        _is_point_inside(*obstacle_corner, *obstacle_size, *opposite_obj_corner),

        _is_point_inside(*obj_corner, *obj_size, *obstacle_corner),
        _is_point_inside(*obj_corner, *obj_size, *opposite_obstacle_corner),
    ])
