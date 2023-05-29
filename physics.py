import math


def _limit(
        value: int | float, min_value: int | float, max_value: int | float,
) -> int | float:
    """Limit value by min_value and max_value."""

    if value < min_value:
        return min_value
    if value > max_value:
        return max_value
    return value


def _apply_acceleration(
        speed: int | float, speed_limit: int | float, forward: bool = True,
) -> int | float:
    """Change speed — accelerate or brake — according to force direction."""

    speed_limit = abs(speed_limit)

    speed_fraction = speed / speed_limit

    # If ships is stationary, accelerate fast
    # If it's already going fast, add speed slowly
    delta = math.cos(speed_fraction) * 0.75

    if forward:
        result_speed = speed + delta
    else:
        result_speed = speed - delta

    result_speed = _limit(result_speed, -speed_limit, speed_limit)

    # If speed is close to zero, stop the ship
    if abs(result_speed) < 0.1:
        result_speed = 0

    return result_speed


def update_speed(
    row_speed: int | float,
    column_speed: int | float,
    rows_direction: int,
    columns_direction: int,
    row_speed_limit=2,
    column_speed_limit=2,
    fading=0.8,
) -> tuple[int | float, int | float]:
    """Update speed smoothly to make control handy for player.
    Return new speed value (row_speed, column_speed)

    rows_direction — is a force direction by rows' axis. Possible values:
       -1 — if force pulls up
       0  — if force has no effect
       1  — if force pulls down

    columns_direction — is a force direction by columns' axis. Possible values:
       -1 — if force pulls left
       0  — if force has no effect
       1  — if force pulls right
    """

    if rows_direction not in (-1, 0, 1):
        raise ValueError(
            f'Wrong rows_direction value {rows_direction}. Expects -1, 0 or 1.',
        )

    if columns_direction not in (-1, 0, 1):
        raise ValueError(
            f'Wrong columns_direction value {columns_direction}. Expects -1, 0 or 1.',
        )

    if fading < 0 or fading > 1:
        raise ValueError(
            f'Wrong columns_direction value {fading}. Expects float between 0 and 1.',
        )

    # Fading ship's speed so it slow-downs slowly
    row_speed *= fading
    column_speed *= fading

    row_speed_limit, column_speed_limit = abs(row_speed_limit), abs(column_speed_limit)

    if rows_direction != 0:
        row_speed = _apply_acceleration(row_speed, row_speed_limit, rows_direction > 0)

    if columns_direction != 0:
        column_speed = _apply_acceleration(
            column_speed, column_speed_limit, columns_direction > 0,
        )

    return row_speed, column_speed
