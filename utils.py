import curses

from constants import (
    UP_KEY_CODE,
    DOWN_KEY_CODE,
    RIGHT_KEY_CODE,
    LEFT_KEY_CODE,
    SPACE_KEY_CODE,
    BORDER_OFFSET,
)


def get_frame_size(text: str) -> tuple[int, int]:
    """Calculate size of multiline text fragment,
    return pair — number of rows and columns."""

    lines = text.splitlines()
    rows = len(lines)
    columns = max([len(line) for line in lines])
    return rows, columns


def get_canvas_borders(canvas: curses.window) -> tuple[int, int, int, int]:
    """Returns coordinates of canvas borders in order:
    row_min, row_max, col_min, col_max."""
    rows, cols = canvas.getmaxyx()
    return BORDER_OFFSET, rows - BORDER_OFFSET, BORDER_OFFSET, cols - BORDER_OFFSET


def read_controls(canvas: curses.window) -> tuple[int, int, bool]:
    """Read keys pressed and returns tuple with controls state."""

    rows_direction = columns_direction = 0
    space_pressed = False

    while True:
        pressed_key_code = canvas.getch()

        if pressed_key_code == -1:
            # https://docs.python.org/3/library/curses.html#curses.window.getch
            break

        if pressed_key_code == UP_KEY_CODE:
            rows_direction = -1

        if pressed_key_code == DOWN_KEY_CODE:
            rows_direction = 1

        if pressed_key_code == RIGHT_KEY_CODE:
            columns_direction = 1

        if pressed_key_code == LEFT_KEY_CODE:
            columns_direction = -1

        if pressed_key_code == SPACE_KEY_CODE:
            space_pressed = True

    return rows_direction, columns_direction, space_pressed


def draw_frame(
    canvas: curses.window,
    start_row: int | float,
    start_column: int | float,
    text: str,
    negative: bool = False,
) -> None:
    """Draw multiline text fragment on canvas,
    erase text instead of drawing if negative=True is specified."""

    rows_number, columns_number = canvas.getmaxyx()

    for row, line in enumerate(text.splitlines(), round(start_row)):
        if row < 0:
            continue

        if row >= rows_number:
            break

        for column, symbol in enumerate(line, round(start_column)):
            if column < 0:
                continue

            if column >= columns_number:
                break

            if symbol == ' ':
                continue

            # Check that current position is not in a lower right corner of the window
            # Curses will raise exception in that case. Don`t ask why...
            # https://docs.python.org/3/library/curses.html#curses.window.addch
            if row == rows_number - 1 and column == columns_number - 1:
                continue

            symbol = symbol if not negative else ' '
            canvas.addch(row, column, symbol)
