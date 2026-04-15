from __future__ import annotations

from app.api.schemas import NormalizedRecord
from app.normalizers.canonical import split_name


def should_pair(left: NormalizedRecord, right: NormalizedRecord) -> bool:
    left_first, left_last = split_name(left.name)
    right_first, right_last = split_name(right.name)

    if not left_last or not right_last or left_last != right_last:
        return False

    if left_first == right_first:
        return True

    return bool(left_first and right_first and left_first[0] == right_first[0])


def generate_candidate_pairs(
    left_records: list[NormalizedRecord],
    right_records: list[NormalizedRecord],
) -> list[tuple[NormalizedRecord, NormalizedRecord]]:
    pairs: list[tuple[NormalizedRecord, NormalizedRecord]] = []
    for left in left_records:
        for right in right_records:
            if should_pair(left, right):
                pairs.append((left, right))
    return pairs
