from typing import Any
import parser.expr as expr
from runtime.ploxRuntimeError import PloxRuntimeError


def stringify(obj: Any) -> str:
    if obj is None:
        return "nil"
    if isinstance(obj, float):
        text = str(obj)
        if text.endswith(".0"):
            text = text[:-2]
        return text
    return str(obj)


def maybeZeroDivision(expr: expr.Binary, left: Any, right: Any) -> float:
    if right == 0:
        raise PloxRuntimeError(expr.operator, "Cannot divide by zero.")
    return float(left) / float(right)


def isEqual(a: Any, b: Any) -> bool:
    if a is None and b is None:
        return True
    if a is None:
        return False
    return a == b
