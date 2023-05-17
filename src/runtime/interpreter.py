from parser.stmt import Stmt
from typing import Any
from parser.expr import ExprVisitor
from parser.stmt import StmtVisitor
import parser.expr as expr
import parser.stmt as stmt
from runtime.ploxRuntimeError import PloxRuntimeError
from scanner.token import TokenType
from scanner.token import Token
from runtime.environment import Environment


class Interpreter(ExprVisitor, StmtVisitor):
    def __init__(self, __runtime):
        self.__runtime = __runtime
        self.__result = None
        self.globals = Environment()
        self.environment = self.globals
        self.locals = {}

    @property
    def result(self) -> Any:
        return self.__result

    def run(self, program: list[Stmt]):
        try:
            for stmt in program:
                self.__result = self.__execute(stmt)
        except PloxRuntimeError as error:
            self.__runtime.reportError(error)

    def __execute(self, stmt: Stmt) -> Any:
        return stmt.accept(self)

    def visit_assign_expr(self, expr: expr.Assign) -> Any:
        value = self.evaluate(expr.value)
        self.environment.assign(expr.name, value)
        return value

    def visit_binary_expr(self, expr: expr.Binary):
        left = self.evaluate(expr.left)
        right = self.evaluate(expr.right)
        tokenType = expr.operator.tokenType
        if tokenType in (
            TokenType.GREATER,
            TokenType.GREATER_EQUAL,
            TokenType.LESS,
            TokenType.LESS_EQUAL,
            TokenType.MINUS,
            TokenType.SLASH,
            TokenType.STAR,
        ):
            self.checkNumberOperands(expr.operator, left, right)
        choices = {
            TokenType.GREATER: lambda: float(left) > float(right),
            TokenType.GREATER_EQUAL: lambda: float(left) >= float(right),
            TokenType.LESS: lambda: float(left) < float(right),
            TokenType.LESS_EQUAL: lambda: float(left) <= float(right),
            TokenType.BANG_EQUAL: lambda: not self.isEqual(left, right),
            TokenType.EQUAL_EQUAL: lambda: self.isEqual(left, right),
            TokenType.MINUS: lambda: float(left) - float(right),
            TokenType.SLASH: self.maybeZeroDivision(expr, left, right),
            TokenType.STAR: lambda: float(left) * float(right),
            TokenType.PLUS: lambda: self.overloadedPlus(expr, left, right),
        }
        try:
            choice = choices[tokenType]
            result = choice()
            return result
        except KeyError:
            raise PloxRuntimeError(
                expr.operator, f"Unknown operator {expr.operator.lexeme}"
            )

    def maybeZeroDivision(self, expr: expr.Binary, left: Any, right: Any) -> Any:
        if right == 0:
            raise PloxRuntimeError(expr.operator, "Cannot divide by zero.")
        return float(left) / float(right)

    def overloadedPlus(self, expr: expr.Binary, left: Any, right: Any) -> Any:
        if (type(left) == type(right)) and type(left) in [str, float]:
            return left + right
        if type(left) == str or type(right) == str:
            return str(left) + str(right)
        raise PloxRuntimeError(
            expr.operator, "Operands must be either a string and any type or two numbers."
        )

    def isEqual(self, a: Any, b: Any) -> bool:
        if a is None and b is None:
            return True
        if a is None:
            return False
        return a == b

    def visit_call_expr(self, expr: expr.Call):
        raise NotImplementedError

    def visit_comma_expr(self, expr: expr.Comma):
        raise NotImplementedError

    def visit_get_expr(self, expr: expr.Get):
        raise NotImplementedError

    def visit_grouping_expr(self, expr: expr.Grouping):
        return self.evaluate(expr.expression)

    def visit_literal_expr(self, expr: expr.Literal) -> Any:
        return expr.value

    def visit_logical_expr(self, expr: expr.Logical):
        raise NotImplementedError

    def visit_set_expr(self, expr: expr.Set):
        raise NotImplementedError

    def visit_super_expr(self, expr: expr.Super):
        raise NotImplementedError

    def visit_this_expr(self, expr: expr.This):
        raise NotImplementedError

    def visit_unary_expr(self, expr: expr.Unary):
        right = self.evaluate(expr.right)
        match expr.operator.tokenType:
            case TokenType.MINUS:
                self.checkNumberOperand(expr.operator, right)
                return -float(right)
            case TokenType.BANG:
                return not self.isTruthy(right)

    def checkNumberOperand(self, operator: Token, operand: Any):
        if isinstance(operand, (float, int)):
            return
        raise RuntimeError(operator, "Operand must be a number.")

    def checkNumberOperands(self, operator: Token, left: Any, right: Any):
        if not (isinstance(left, (float, int)) and isinstance(right, (float, int))):
            raise RuntimeError(operator, "Operands must be numbers.")

    def visit_variable_expr(self, expr: expr.Variable):
        return self.environment.get(expr.name)

    def evaluate(self, expr: expr.Expr) -> Any:
        return expr.accept(self)

    def isTruthy(self, obj: Any) -> bool:
        if obj is None:
            return False
        if isinstance(obj, bool):
            return obj
        return True

    def visit_block_stmt(self, stmt: stmt.Block):
        self.executeBlock(stmt.statements, Environment(self.environment))
        
    def executeBlock(self, statements: list[Stmt], environment: Environment):
        previous = self.environment
        try:
            self.environment = environment
            for statement in statements:
                self.__execute(statement)
        finally:
            self.environment = previous

    def visit_class_stmt(self, stmt: stmt.Class):
        raise NotImplementedError

    def visit_expression_stmt(self, stmt: stmt.Expression):
        self.evaluate(stmt.expression)

    def visit_function_stmt(self, stmt: stmt.Function):
        raise NotImplementedError

    def visit_if_stmt(self, stmt: stmt.If):
        raise NotImplementedError

    def visit_print_stmt(self, stmt: stmt.Print):
        value = self.evaluate(stmt.expression)
        print(value)

    def visit_return_stmt(self, stmt: stmt.Return):
        raise NotImplementedError

    def visit_var_stmt(self, stmt: stmt.Var):
        value = None
        if stmt.initializer is not None:
            value = self.evaluate(stmt.initializer)
        self.environment.define(stmt.name.lexeme, value)

    def visit_while_stmt(self, stmt: stmt.While):
        raise NotImplementedError
