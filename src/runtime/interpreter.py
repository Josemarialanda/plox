from parser.stmt import Stmt
from typing import Any
from parser.expr import ExprVisitor
from parser.stmt import StmtVisitor
import parser.expr as expr
import parser.stmt as stmt


class Interpreter(ExprVisitor, StmtVisitor):
    def __init__(self, program: list[Stmt]) -> None:
        self.__hadError = False
        self.__result = program

    @property
    def result(self) -> Any:
        return self.__result

    @property
    def hadError(self) -> bool:
        return self.__hadError

    def run(self):
        pass

    def visit_assign_expr(self, expr: expr.Assign):
        raise NotImplementedError

    def visit_binary_expr(self, expr: expr.Binary):
        raise NotImplementedError

    def visit_call_expr(self, expr: expr.Call):
        raise NotImplementedError

    def visit_comma_expr(self, expr: expr.Comma):
        raise NotImplementedError

    def visit_get_expr(self, expr: expr.Get):
        raise NotImplementedError

    def visit_grouping_expr(self, expr: expr.Grouping):
        raise NotImplementedError

    def visit_literal_expr(self, expr: expr.Literal):
        raise NotImplementedError

    def visit_logical_expr(self, expr: expr.Logical):
        raise NotImplementedError

    def visit_set_expr(self, expr: expr.Set):
        raise NotImplementedError

    def visit_super_expr(self, expr: expr.Super):
        raise NotImplementedError

    def visit_this_expr(self, expr: expr.This):
        raise NotImplementedError

    def visit_unary_expr(self, expr: expr.Unary):
        raise NotImplementedError

    def visit_variable_expr(self, expr: expr.Variable):
        raise NotImplementedError
    
    def visit_block_stmt(self, stmt: stmt.Block):
        raise NotImplementedError

    def visit_class_stmt(self, stmt: stmt.Class):
        raise NotImplementedError

    def visit_expression_stmt(self, stmt: stmt.Expression):
        raise NotImplementedError

    def visit_function_stmt(self, stmt: stmt.Function):
        raise NotImplementedError

    def visit_if_stmt(self, stmt: stmt.If):
        raise NotImplementedError

    def visit_print_stmt(self, stmt: stmt.Print):
        raise NotImplementedError

    def visit_return_stmt(self, stmt: stmt.Return):
        raise NotImplementedError

    def visit_var_stmt(self, stmt: stmt.Var):
        raise NotImplementedError

    def visit_while_stmt(self, stmt: stmt.While):
        raise NotImplementedError