from typing import Optional
from parser.expr import Expr


class PloxReturnException(Exception):
    def __init__(self, value: Optional[Expr]):
        super().__init__()
        self.value = value
