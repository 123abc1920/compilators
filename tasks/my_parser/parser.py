from .lexer import Token
from .nodes import *
from typing import Any, List


class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0

    def current_token(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return Token("EOF", None, 0, 0)

    def read_token(self, expected_type, expected_value=None):
        token = self.current_token()
        if token.type != expected_type:
            raise SyntaxError(
                f"Expected {expected_type}, got {token.type} at line {token.line}"
            )
        if expected_value and token.value != expected_value:
            raise SyntaxError(f"Expected {expected_value}, got {token.value}")
        self.pos += 1
        return token

    def parse(self):
        return self.prog()

    def prog(self):
        statements = []
        while self.current_token().type != "EOF":
            stmt = self.statement()
            if stmt:
                statements.append(stmt)
            while self.current_token().type == "NEWLINE":
                self.read_token("NEWLINE")
        line = statements[0].line if statements else 0
        col = statements[0].col if statements else 0
        return ProgNode(statements, line, col)

    def statement(self):
        token = self.current_token()

        if token.type == "KEYWORD":
            if token.value == "print":
                return self.print_stmt()
            elif token.value == "function":
                return self.fun_stmt()
            elif token.value == "for":
                return self.for_stmt()
            elif token.value == "while":
                return self.while_stmt()
            elif token.value == "repeat":
                return self.repeat_stmt()
            elif token.value == "if":
                return self.if_stmt()
            elif token.value == "break":
                return self.break_stmt()
            elif token.value == "continue":
                return self.continue_stmt()
            elif token.value == "return":
                return self.return_stmt()
            elif token.value == "read":
                return self.read_stmt()

        if token.type == "NAME":
            if (
                self.pos + 1 < len(self.tokens)
                and self.tokens[self.pos + 1].value == "="
            ):
                return self.assign()
            else:
                return self.expr()

        if token.type == "NEWLINE":
            self.read_token("NEWLINE")
            return None

        return self.expr()

    def print_stmt(self):
        token = self.read_token("KEYWORD", "print")
        args = None
        if self.current_token().type == "PUNCT" and self.current_token().value == "(":
            self.read_token("PUNCT", "(")
            if (
                self.current_token().type != "PUNCT"
                or self.current_token().value != ")"
            ):
                args = self.arg_list()
            self.read_token("PUNCT", ")")
        return PrintStmtNode(args, line=token.line, col=token.column)

    def arg_list(self):
        args = []
        args.append(self.atom())
        while (
            self.current_token().type == "PUNCT" and self.current_token().value == ","
        ):
            self.read_token("PUNCT", ",")
            args.append(self.atom())
        return ArgListNode(args)

    def fun_stmt(self):
        token = self.read_token("KEYWORD", "function")
        name = self.read_token("NAME")
        self.read_token("PUNCT", "(")
        params = None
        if self.current_token().type == "NAME":
            params = self.params()
        self.read_token("PUNCT", ")")
        block = self.block()
        self.read_token("KEYWORD", "end")
        return FunStmtNode(name.value, params, block, line=token.line, col=token.column)

    def params(self):
        params = [self.read_token("NAME").value]
        while (
            self.current_token().type == "PUNCT" and self.current_token().value == ","
        ):
            self.read_token("PUNCT", ",")
            params.append(self.read_token("NAME").value)
        return ParamsNode(params)

    def block(self):
        statements = []
        while (
            self.current_token().type != "KEYWORD"
            or self.current_token().value not in ["end", "else", "elseif", "until"]
        ):
            if self.current_token().type == "EOF":
                break
            if self.current_token().type == "NEWLINE":
                self.read_token("NEWLINE")
                continue
            stmt = self.statement()
            if stmt:
                statements.append(stmt)
        return BlockNode(statements)

    def for_stmt(self):
        token = self.read_token("KEYWORD", "for")
        name = self.read_token("NAME")
        self.read_token("PUNCT", "=")
        start = self.expr()
        self.read_token("PUNCT", ",")
        end = self.expr()
        self.read_token("KEYWORD", "do")
        statements = []
        while (
            self.current_token().type != "KEYWORD"
            or self.current_token().value != "end"
        ):
            if self.current_token().type == "EOF":
                break
            if self.current_token().type == "NEWLINE":
                self.read_token("NEWLINE")
                continue
            stmt = self.statement()
            if stmt:
                statements.append(stmt)
        self.read_token("KEYWORD", "end")
        return ForStmtNode(
            name.value, start, end, statements, line=token.line, col=token.column
        )

    def while_stmt(self):
        token = self.read_token("KEYWORD", "while")
        condition = self.expr()
        self.read_token("KEYWORD", "do")
        statements = []
        while (
            self.current_token().type != "KEYWORD"
            or self.current_token().value != "end"
        ):
            if self.current_token().type == "EOF":
                break
            if self.current_token().type == "NEWLINE":
                self.read_token("NEWLINE")
                continue
            stmt = self.statement()
            if stmt:
                statements.append(stmt)
        self.read_token("KEYWORD", "end")
        return WhileStmtNode(condition, statements, line=token.line, col=token.column)

    def repeat_stmt(self):
        token = self.read_token("KEYWORD", "repeat")
        statements = []
        while (
            self.current_token().type != "KEYWORD"
            or self.current_token().value != "until"
        ):
            if self.current_token().type == "EOF":
                break
            if self.current_token().type == "NEWLINE":
                self.read_token("NEWLINE")
                continue
            stmt = self.statement()
            if stmt:
                statements.append(stmt)
        self.read_token("KEYWORD", "until")
        condition = self.expr()
        return RepeatStmtNode(statements, condition, line=token.line, col=token.column)

    def if_stmt(self):
        token = self.read_token("KEYWORD", "if")
        conditions = []
        blocks = []

        condition = self.expr()
        self.read_token("KEYWORD", "then")
        block = self.block()
        conditions.append(condition)
        blocks.append(block)

        while (
            self.current_token().type == "KEYWORD"
            and self.current_token().value == "elseif"
        ):
            self.read_token("KEYWORD", "elseif")
            condition = self.expr()
            self.read_token("KEYWORD", "then")
            block = self.block()
            conditions.append(condition)
            blocks.append(block)

        if (
            self.current_token().type == "KEYWORD"
            and self.current_token().value == "else"
        ):
            self.read_token("KEYWORD", "else")
            block = self.block()
            blocks.append(block)

        self.read_token("KEYWORD", "end")
        return IfStmtNode(conditions, blocks, line=token.line, col=token.column)

    def break_stmt(self):
        token = self.read_token("KEYWORD", "break")
        return BreakStmtNode(line=token.line, col=token.column)

    def continue_stmt(self):
        token = self.read_token("KEYWORD", "continue")
        return ContinueStmtNode(line=token.line, col=token.column)

    def return_stmt(self):
        token = self.read_token("KEYWORD", "return")
        expr = None
        if self.current_token().type not in [
            "NEWLINE",
            "KEYWORD",
        ] or self.current_token().value not in ["end", "else", "elseif"]:
            expr = self.expr()
        return ReturnStmtNode(expr, line=token.line, col=token.column)

    def read_stmt(self):
        token = self.read_token("KEYWORD", "read")
        self.read_token("PUNCT", "(")
        self.read_token("PUNCT", ")")
        return ReadStmtNode(line=token.line, col=token.column)

    def assign(self):
        name_token = self.read_token("NAME")
        self.read_token("PUNCT", "=")

        if (
            self.current_token().type == "KEYWORD"
            and self.current_token().value == "read"
        ):
            read_node = self.read_stmt()
            return AssignNode(
                name_token.value, read_node, line=name_token.line, col=name_token.column
            )
        else:
            value = self.expr()
            return AssignNode(
                name_token.value, value, line=name_token.line, col=name_token.column
            )

    def expr(self):
        return self.or_expr()

    def or_expr(self):
        left = self.and_expr()
        while (
            self.current_token().type == "KEYWORD"
            and self.current_token().value == "or"
        ):
            op_token = self.read_token("KEYWORD", "or")
            right = self.and_expr()
            left = OrExprNode(left, right, line=op_token.line, col=op_token.column)
        return left

    def and_expr(self):
        left = self.not_expr()
        while (
            self.current_token().type == "KEYWORD"
            and self.current_token().value == "and"
        ):
            op_token = self.read_token("KEYWORD", "and")
            right = self.not_expr()
            left = AndExprNode(left, right, line=op_token.line, col=op_token.column)
        return left

    def not_expr(self):
        if (
            self.current_token().type == "KEYWORD"
            and self.current_token().value == "not"
        ):
            op_token = self.read_token("KEYWORD", "not")
            expr = self.not_expr()
            return NotExprNode(expr, line=op_token.line, col=op_token.column)
        return self.comparison()

    def comparison(self):
        left = self.add_expr()
        if self.current_token().type == "OPERATOR" and self.current_token().value in [
            "<",
            ">",
            "<=",
            ">=",
            "==",
            "~=",
        ]:
            op_token = self.read_token("OPERATOR")
            right = self.add_expr()
            return ComparisonNode(
                left, op_token.value, right, line=op_token.line, col=op_token.column
            )
        return left

    def add_expr(self):
        left = self.mul_expr()
        while (
            self.current_token().type == "OPERATOR"
            and self.current_token().value in ["+", "-"]
        ):
            op_token = self.read_token("OPERATOR")
            right = self.mul_expr()
            left = AddExprNode(
                left, op_token.value, right, line=op_token.line, col=op_token.column
            )
        return left

    def mul_expr(self):
        left = self.atom()
        while (
            self.current_token().type == "OPERATOR"
            and self.current_token().value in ["*", "/", "%"]
        ):
            op_token = self.read_token("OPERATOR")
            right = self.atom()
            left = MulExprNode(
                left, op_token.value, right, line=op_token.line, col=op_token.column
            )
        return left

    def atom(self):
        token = self.current_token()

        if token.type == "NUMBER":
            self.read_token("NUMBER")
            return AtomNode("number", token.value, line=token.line, col=token.column)

        elif token.type == "STRING":
            self.read_token("STRING")
            return AtomNode("string", token.value, line=token.line, col=token.column)

        elif token.type == "KEYWORD" and token.value in ["true", "false", "nil"]:
            self.read_token("KEYWORD")
            return AtomNode("literal", token.value, line=token.line, col=token.column)

        elif token.type == "PUNCT" and token.value == "{":
            return self.table()

        elif token.type == "NAME":
            name_token = token
            self.read_token("NAME")
            if (
                self.current_token().type == "PUNCT"
                and self.current_token().value == "("
            ):
                return self.call_fun(name_token.value)
            elif (
                self.current_token().type == "PUNCT"
                and self.current_token().value == "."
            ):
                self.read_token("PUNCT", ".")
                field = self.read_token("NAME")
                return AtomNode(
                    "field",
                    (name_token.value, field.value),
                    line=name_token.line,
                    col=name_token.column,
                )
            elif (
                self.current_token().type == "PUNCT"
                and self.current_token().value == "["
            ):
                self.read_token("PUNCT", "[")
                index = self.expr()
                self.read_token("PUNCT", "]")
                return AtomNode(
                    "index",
                    (name_token.value, index),
                    line=name_token.line,
                    col=name_token.column,
                )
            else:
                return AtomNode(
                    "name",
                    name_token.value,
                    line=name_token.line,
                    col=name_token.column,
                )

        elif token.type == "PUNCT" and token.value == "(":
            paren_token = token
            self.read_token("PUNCT", "(")
            expr = self.expr()
            self.read_token("PUNCT", ")")
            if hasattr(expr, "line") and expr.line:
                return expr
            return expr

        elif token.type == "OPERATOR" and token.value == "-":
            op_token = token
            self.read_token("OPERATOR", "-")
            expr = self.atom()
            return UnaryMinusNode(expr, line=op_token.line, col=op_token.column)

        return AtomNode("none", None, line=token.line, col=token.column)

    def table(self):
        brace_token = self.read_token("PUNCT", "{")
        elements = []
        if self.current_token().type != "PUNCT" or self.current_token().value != "}":
            elements = self.table_elements()
        self.read_token("PUNCT", "}")
        return TableNode(elements, line=brace_token.line, col=brace_token.column)

    def table_elements(self):
        elements = [self.table_element()]
        while (
            self.current_token().type == "PUNCT" and self.current_token().value == ","
        ):
            self.read_token("PUNCT", ",")
            if (
                self.current_token().type != "PUNCT"
                or self.current_token().value != "}"
            ):
                elements.append(self.table_element())
        return elements

    def table_element(self):
        return TableElementNode(None, self.expr())

    def call_fun(self, name):
        paren_token = self.current_token()
        self.read_token("PUNCT", "(")
        args = None
        if self.current_token().type != "PUNCT" or self.current_token().value != ")":
            args = self.args()
        self.read_token("PUNCT", ")")
        return CallFunNode(name, args, line=paren_token.line, col=paren_token.column)

    def args(self):
        args = [self.expr()]
        while (
            self.current_token().type == "PUNCT" and self.current_token().value == ","
        ):
            self.read_token("PUNCT", ",")
            args.append(self.expr())
        return ArgsNode(args)
