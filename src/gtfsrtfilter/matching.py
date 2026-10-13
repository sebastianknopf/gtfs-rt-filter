"""Match declared filter groups without inferring missing fields."""
from collections import defaultdict
from fnmatch import fnmatchcase
from typing import Any

def groups(filters: list[dict[str, Any]]) -> dict[str, list[str]]:
    result: dict[str, list[str]] = defaultdict(list)
    for item in filters:
        key, value = next(iter(item.items()))
        result[key].append(str(value))
    return dict(result)

def matches(value: Any, patterns: list[str]) -> bool:
    if value is None:
        return False
    return any(fnmatchcase(str(value), pattern) for pattern in patterns)

def match_fields(values: dict[str, Any], criteria: dict[str, list[str]]) -> bool:
    return all(matches(values.get(key), patterns) for key, patterns in criteria.items())
