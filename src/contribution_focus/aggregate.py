"""Aggregate repository contributions into five named rows and Other."""

from dataclasses import dataclass
from typing import Mapping, Sequence

MAX_NAMED_REPOSITORIES = 5
OTHER_LABEL = "Other"


@dataclass(frozen=True)
class FocusRow:
    """One repository row in the contribution focus chart."""

    name: str
    monthly: tuple[int, ...]
    is_other: bool = False

    @property
    def total(self) -> int:
        return sum(self.monthly)


def _add_monthly(target: list[int], source: Sequence[int]) -> None:
    if len(target) != len(source):
        raise ValueError("all contribution series must use the same month count")
    for index, value in enumerate(source):
        target[index] += int(value)


def build_rows(
    repositories: Mapping[str, Sequence[int]],
    unattributed: Sequence[int] | None = None,
    max_named: int = MAX_NAMED_REPOSITORIES,
) -> list[FocusRow]:
    """Return ranked repository rows plus a monthly Other aggregate."""

    if not 1 <= max_named <= MAX_NAMED_REPOSITORIES:
        raise ValueError(f"max_named must be between 1 and {MAX_NAMED_REPOSITORIES}")

    month_count = 0
    if repositories:
        month_count = len(next(iter(repositories.values())))
    elif unattributed is not None:
        month_count = len(unattributed)

    normalized = []
    for name, values in repositories.items():
        monthly = tuple(max(0, int(value)) for value in values)
        if len(monthly) != month_count:
            raise ValueError("all contribution series must use the same month count")
        if sum(monthly) > 0:
            normalized.append(FocusRow(name=name, monthly=monthly))

    normalized.sort(key=lambda row: (-row.total, row.name.casefold()))
    visible = normalized[:max_named]

    other = [0] * month_count
    for row in normalized[max_named:]:
        _add_monthly(other, row.monthly)
    if unattributed is not None:
        _add_monthly(other, unattributed)

    if any(other):
        visible.append(FocusRow(name=OTHER_LABEL, monthly=tuple(other), is_other=True))
    return visible
