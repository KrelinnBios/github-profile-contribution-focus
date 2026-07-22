"""Month range helpers for GitHub contribution collections."""

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone


@dataclass(frozen=True)
class MonthWindow:
    """One UTC calendar month included in the contribution chart."""

    key: str
    label: str
    start: datetime
    end: datetime
    current: bool = False


def _shift_month(year: int, month: int, offset: int) -> tuple[int, int]:
    absolute = year * 12 + (month - 1) + offset
    shifted_year, zero_based_month = divmod(absolute, 12)
    return shifted_year, zero_based_month + 1


def github_datetime(value: datetime) -> str:
    """Format an aware datetime for a GitHub GraphQL DateTime variable."""

    return value.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace(
        "+00:00", "Z"
    )


def month_windows(now: datetime | None = None, count: int = 12) -> list[MonthWindow]:
    """Return the current UTC month and the preceding calendar months."""

    if count <= 0:
        raise ValueError("count must be greater than zero")

    current_time = now or datetime.now(timezone.utc)
    if current_time.tzinfo is None:
        current_time = current_time.replace(tzinfo=timezone.utc)
    current_time = current_time.astimezone(timezone.utc)

    first_year, first_month = _shift_month(
        current_time.year, current_time.month, -(count - 1)
    )
    windows = []
    for index in range(count):
        year, month = _shift_month(first_year, first_month, index)
        next_year, next_month = _shift_month(year, month, 1)
        start = datetime(year, month, 1, tzinfo=timezone.utc)
        next_start = datetime(next_year, next_month, 1, tzinfo=timezone.utc)
        is_current = year == current_time.year and month == current_time.month
        end = current_time if is_current else next_start - timedelta(seconds=1)
        windows.append(
            MonthWindow(
                key=f"{year:04d}-{month:02d}",
                label=f"{month:02d}",
                start=start,
                end=end,
                current=is_current,
            )
        )
    return windows


def month_windows_between(start: datetime, end: datetime) -> list[MonthWindow]:
    """Split an inclusive GitHub contribution range into UTC month buckets."""

    if start.tzinfo is None:
        start = start.replace(tzinfo=timezone.utc)
    if end.tzinfo is None:
        end = end.replace(tzinfo=timezone.utc)
    start = start.astimezone(timezone.utc)
    end = end.astimezone(timezone.utc)
    if start > end:
        raise ValueError("start must not be after end")

    windows = []
    year, month = start.year, start.month
    while (year, month) <= (end.year, end.month):
        next_year, next_month = _shift_month(year, month, 1)
        calendar_start = datetime(year, month, 1, tzinfo=timezone.utc)
        next_start = datetime(next_year, next_month, 1, tzinfo=timezone.utc)
        window_start = max(start, calendar_start)
        window_end = min(end, next_start - timedelta(seconds=1))
        windows.append(
            MonthWindow(
                key=f"{year:04d}-{month:02d}",
                label=f"{month:02d}",
                start=window_start,
                end=window_end,
                current=(year, month) == (end.year, end.month),
            )
        )
        year, month = next_year, next_month
    return windows
