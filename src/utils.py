from typing import Any


def stringify(obj: Any) -> str:
    if obj is None:
        return "nil"
    if isinstance(obj, float):
        text = str(obj)
        if text.endswith(".0"):
            text = text[:-2]
        return text
    return str(obj)
