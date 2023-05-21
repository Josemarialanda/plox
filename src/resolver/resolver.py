from parser.stmt import Stmt
from scanner.token import Token
from parser.expr import ExprVisitor
from parser.stmt import StmtVisitor
import parser.expr as expr
import parser.stmt as stmt
from resolver.functionType import FunctionType
from resolver.classType import ClassType
from runtime.ploxRuntimeError import PloxRuntimeError
from resolver.resolveError import ResolveError


class Resolver(ExprVisitor, StmtVisitor):
    def __init__(self, interpreter, runtime):
        self.__interpreter = interpreter
        self.__runtime = runtime
        self.__scopes = []
        self.__currentFunction = FunctionType.NONE
        self.__currentClass = ClassType.NONE

    def run(self, program: list[Stmt]):
        self.__resolve(program)

    def __resolve(self, statements: list[Stmt]):
        self.__resolveStatements(statements)

    def __resolveStatements(self, statements: list[Stmt]):
        for statement in statements:
            self.__resolveStatement(statement)

    def __resolveStatement(self, statement: Stmt):
        statement.accept(self)

    def __resolveExpression(self, expression: expr.Expr):
        expression.accept(self)

    def __resolveLocal(self, expr: expr.Expr, name: Token):
        for idx, scope in enumerate(reversed(self.__scopes)):
            if name.lexeme in scope:
                self.__interpreter.resolve(expr, idx)
                return

    def __resolveFunction(self, function: stmt.Function, type: FunctionType):
        enclosingFunction = self.__currentFunction
        self.__currentFunction = type
        self.__beginScope()
        for param in function.params:
            self.__declare(param)
            self.__define(param)

        self.__resolveStatements(function.body)
        self.__endScope()
        self.current_function = enclosingFunction

    def __beginScope(self):
        self.__scopes.append({})

    def __endScope(self):
        self.__scopes.pop()

    def __declare(self, name: Token):
        if len(self.__scopes) == 0:
            return
        scope = self.__scopes[-1]
        if name.lexeme in scope:
            self.__throwResolveError(
                name, "Variable with this name already declared in this scope."
            )
        scope[name.lexeme] = False

    def __define(self, name: Token):
        if len(self.__scopes) == 0:
            return
        scope = self.__scopes[-1]
        scope[name.lexeme] = True

    def visit_assign_expr(self, expr: expr.Assign):
        self.__resolveExpression(expr.value)
        self.__resolveLocal(expr, expr.name)

    def visit_binary_expr(self, expr: expr.Binary):
        self.__resolveExpression(expr.left)
        self.__resolveExpression(expr.right)

    def visit_call_expr(self, expr: expr.Call):
        self.__resolveExpression(expr.callee)
        for argument in expr.arguments:
            self.__resolveExpression(argument)

    def visit_comma_expr(self, expr: expr.Comma):
        for expression in expr.expressions:
            self.__resolveExpression(expression)

    def visit_get_expr(self, expr: expr.Get):
        self.__resolveExpression(expr.obj)

    def visit_grouping_expr(self, expr: expr.Grouping):
        self.__resolveExpression(expr.expression)

    def visit_literal_expr(self, expr: expr.Literal):
        return

    def visit_logical_expr(self, expr: expr.Logical):
        self.__resolveExpression(expr.left)
        self.__resolveExpression(expr.right)

    def visit_set_expr(self, expr: expr.Set):
        self.__resolveExpression(expr.value)
        self.__resolveExpression(expr.obj)

    def visit_super_expr(self, expr: expr.Super):
        if self.__currentClass == ClassType.NONE:
            self.__throwResolveError(expr.keyword, "Cannot use 'super' outside of a class.")
        elif self.__currentClass != ClassType.SUBCLASS:
            self.__throwResolveError(
                expr.keyword, "Cannot use 'super' in a class with no superclass."
            )
        self.__resolveLocal(expr, expr.keyword)

    def visit_this_expr(self, expr: expr.This):
        if self.__currentClass == ClassType.NONE:
            self.__throwResolveError(expr.keyword, "Cannot use 'this' outside of a class.")
        self.__resolveLocal(expr, expr.keyword)

    def visit_unary_expr(self, expr: expr.Unary):
        self.__resolveExpression(expr.right)

    def visit_variable_expr(self, expr: expr.Variable):
        if len(self.__scopes) != 0 and self.__scopes[-1].get(expr.name.lexeme) == False:
            self.__throwRuntimeError(
                expr.name, "Cannot read local variable in its own initializer."
            )
        self.__resolveLocal(expr, expr.name)

    def visit_block_stmt(self, stmt: stmt.Block):
        self.__beginScope()
        self.__resolveStatements(stmt.statements)
        self.__endScope()

    def visit_class_stmt(self, stmt: stmt.Class):
        enclosingClass = self.__currentClass
        self.__currentClass = ClassType.CLASS
        self.__declare(stmt.name)
        self.__define(stmt.name)
        if stmt.superclass and stmt.name.lexeme == stmt.superclass.name.lexeme:
            self.__throwResolveError(
                stmt.superclass.name, "A class cannot inherit from itself."
            )
        if stmt.superclass is not None:
            self.__currentClass = ClassType.SUBCLASS
            self.__resolveExpression(stmt.superclass)
        if stmt.superclass is not None:
            self.__beginScope()
            self.__scopes[-1]["super"] = True
        self.__beginScope()
        self.__scopes[-1]["this"] = True
        for method in stmt.methods:
            declaration = FunctionType.METHOD
            if method.name.lexeme == "init":
                declaration = FunctionType.INITIALIZER
            self.__resolveFunction(method, declaration)
        self.__endScope()
        if stmt.superclass is not None:
            self.__endScope()
        self.__currentClass = enclosingClass

    def visit_expression_stmt(self, stmt: stmt.Expression):
        self.__resolveExpression(stmt.expression)

    def visit_function_stmt(self, stmt: stmt.Function):
        self.__declare(stmt.name)
        self.__define(stmt.name)
        self.__resolveFunction(stmt, FunctionType.FUNCTION)

    def visit_if_stmt(self, stmt: stmt.If):
        self.__resolveExpression(stmt.condition)
        self.__resolveStatement(stmt.thenBranch)
        if stmt.elseBranch is not None:
            self.__resolveStatement(stmt.elseBranch)

    def visit_print_stmt(self, stmt: stmt.Print):
        self.__resolveExpression(stmt.expression)

    def visit_return_stmt(self, stmt: stmt.Return):
        if self.__currentFunction == FunctionType.NONE:
            self.__throwResolveError(stmt.keyword, "Cannot return from top-level code.")
        if stmt.value is not None:
            if self.__currentFunction == FunctionType.INITIALIZER:
                self.__throwResolveError(
                    stmt.keyword, "Cannot return a value from an initializer."
                )
            self.__resolveExpression(stmt.value)

    def visit_var_stmt(self, stmt: stmt.Var):
        self.__declare(stmt.name)
        if stmt.initializer is not None:
            self.__resolveExpression(stmt.initializer)
        self.__define(stmt.name)

    def visit_while_stmt(self, stmt: stmt.While):
        self.__resolveExpression(stmt.condition)
        self.__resolveStatement(stmt.body)

    def __throwRuntimeError(self, token: Token, message: str):
        error = PloxRuntimeError(token, message)
        self.__runtime.reportError(error)

    def __throwResolveError(self, token: Token, message: str):
        error = ResolveError(token, message)
        self.__runtime.reportError(error)