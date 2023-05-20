from parser.stmt import Stmt
from typing import Any
from parser.expr import ExprVisitor
from parser.stmt import StmtVisitor
import parser.expr as expr
import parser.stmt as stmt
from runtime.ploxRuntimeError import PloxRuntimeError
from runtime.ploxReturnException import PloxReturnException
from scanner.token import TokenType
from scanner.token import Token
from runtime.environment import Environment
from runtime.ploxFunction import PloxFunction
from runtime.native.natives import functions as NATIVE_FUNCTIONS
from runtime.ploxInstance import PloxInstance
from runtime.ploxCallable import PloxCallable


class Interpreter(ExprVisitor, StmtVisitor):
    def __init__(self, __runtime):
        self.__runtime = __runtime
        self.__result = None
        self.__globals = Environment()
        self.__environment = self.__globals
        self.__locals = {}
        self.__defineNativeFunctions()

    @property
    def result(self) -> Any:
        return self.__result

    def resolve(self, expr: expr.Expr, depth: int):
        self.__locals[expr] = depth

    def run(self, program: list[Stmt]):
        try:
            for stmt in program:
                self.__result = self.__execute(stmt)
        except PloxRuntimeError as error:
            self.__runtime.reportError(error)

    def __execute(self, stmt: Stmt) -> Any:
        return stmt.accept(self)

    def visit_assign_expr(self, expression: expr.Assign):
        value = self.evaluate(expression.value)
        distance = self.__locals.get(expression)
        if distance is not None:
            self.__environment.assignAt(distance, expression.name, value)
        else:
            self.__globals.assign(expression.name, value)
        return value

    def visit_binary_expr(self, expr: expr.Binary) -> Any:
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
            TokenType.BANG_EQUAL: lambda: not isEqual(left, right),
            TokenType.EQUAL_EQUAL: lambda: isEqual(left, right),
            TokenType.MINUS: lambda: float(left) - float(right),
            TokenType.SLASH: lambda: maybeZeroDivision(expr, left, right),
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

    def overloadedPlus(self, expr: expr.Binary, left: Any, right: Any) -> Any:
        if (type(left) == type(right)) and type(left) in [str, float]:
            return left + right
        if type(left) == str or type(right) == str:
            return str(left) + str(right)
        raise PloxRuntimeError(
            expr.operator,
            "Operands must be either a string and any type or two numbers.",
        )

    def visit_call_expr(self, expr: expr.Call):
        function = self.evaluate(expr.callee)
        arguments = []
        for argument in expr.arguments:
            arguments.append(self.evaluate(argument))
        if not isinstance(function, PloxCallable):
            raise PloxRuntimeError(expr.paren, "Can only call functions and classes.")
        if len(arguments) != function.arity():
            raise PloxRuntimeError(
                expr.paren,
                f"Expected {function.arity()} arguments but got {len(arguments)}.",
            )
        return function.call(self, arguments)

    def visit_comma_expr(self, expr: expr.Comma):
        values = []
        for expression in expr.expressions:
            values.append(self.evaluate(expression))
        return values[-1]

    def visit_get_expr(self, expr: expr.Get):
        obj = self.evaluate(expr.obj)
        if isinstance(obj, PloxInstance):
            return obj.getAttr(expr.name)
        raise PloxRuntimeError(expr.name, "Only instances have properties.")

    def visit_grouping_expr(self, expr: expr.Grouping) -> Any:
        return self.evaluate(expr.expression)

    def visit_literal_expr(self, expr: expr.Literal) -> Any:
        return expr.value

    def visit_logical_expr(self, expr: expr.Logical):
        left = self.evaluate(expr.left)
        op = expr.operator.tokenType
        match (op, self.isTruthy(left)):
            case (TokenType.OR, True):
                return left
            case (TokenType.AND, False):
                return left
        return self.evaluate(expr.right)

    def visit_set_expr(self, expr: expr.Set):
        obj = self.evaluate(expr.obj)
        if not isinstance(obj, PloxInstance):
            raise PloxRuntimeError(expr.name, "Only instances have fields.")
        value = self.evaluate(expr.value)
        obj.setAttr(expr.name, value)
        return value

    def visit_super_expr(self, expr: expr.Super):
        distance = self.__locals[expr]
        superclass = self.__environment.getAt(distance, "super")
        obj = self.__environment.getAt(distance - 1, "this")
        method = superclass.findMethod(expr.method.lexeme)
        if method is None:
            raise PloxRuntimeError(
                expr.method, f"Undefined property {expr.method.lexeme}."
            )

    def visit_this_expr(self, expr: expr.This):
        return self.__lookUpVariable(expr.keyword, expr)

    def __lookUpVariable(self, name: Token, expr: expr.Expr):
        distance = self.__locals.get(expr)
        if distance is not None:
            return self.__environment.getAt(distance, name.lexeme)
        else:
            return self.__globals.get(name)

    def visit_unary_expr(self, expr: expr.Unary) -> Any:
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

    def visit_variable_expr(self, expr: expr.Variable) -> Any:
        return self.__lookUpVariable(expr.name, expr)

    def evaluate(self, expr: expr.Expr) -> Any:
        return expr.accept(self)

    def isTruthy(self, obj: Any) -> bool:
        if obj is None:
            return False
        if isinstance(obj, bool):
            return obj
        return True

    def visit_block_stmt(self, stmt: stmt.Block) -> Any:
        self.executeBlock(stmt.statements, Environment(self.__environment))

    def executeBlock(self, statements: list[Stmt], environment: Environment):
        previous = self.__environment
        try:
            self.__environment = environment
            for statement in statements:
                self.__execute(statement)
        finally:
            self.__environment = previous

    def visit_class_stmt(self, stmt: stmt.Class):
        raise NotImplementedError

    def visit_expression_stmt(self, stmt: stmt.Expression) -> Any:
        return self.evaluate(stmt.expression)

    def visit_function_stmt(self, stmt: stmt.Function):
        function = PloxFunction(stmt, self.__environment, False)
        self.__environment.define(stmt.name.lexeme, function)

    def visit_if_stmt(self, stmt: stmt.If):
        if self.isTruthy(self.evaluate(stmt.condition)):
            self.__execute(stmt.thenBranch)
        elif stmt.elseBranch is not None:
            self.__execute(stmt.elseBranch)

    def visit_print_stmt(self, stmt: stmt.Print):
        value = self.evaluate(stmt.expression)
        print(stringify(value))

    def visit_return_stmt(self, stmt: stmt.Return):
        value = None
        if stmt.value is not None:
            value = self.evaluate(stmt.value)
        raise PloxReturnException(value)

    def visit_var_stmt(self, stmt: stmt.Var):
        value = None
        if stmt.initializer is not None:
            value = self.evaluate(stmt.initializer)
        self.__environment.define(stmt.name.lexeme, value)

    def visit_while_stmt(self, stmt: stmt.While):
        while self.isTruthy(self.evaluate(stmt.condition)):
            self.__execute(stmt.body)

    def __defineNativeFunctions(self):
        for name, function in NATIVE_FUNCTIONS.items():
            self.__environment.define(name, function)


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


def stringify(obj: Any) -> str:
    if obj is None:
        return "nil"
    if isinstance(obj, float):
        text = str(obj)
        if text.endswith(".0"):
            text = text[:-2]
        return text
    return str(obj)
