import re
from dataclasses import dataclass
from typing import Any, List, Optional, Dict, Union


class BreakException(Exception):
    pass


class ContinueException(Exception):
    pass


@dataclass
class Token:
    type: str
    value: Any
    line: int
    column: int


class Lexer:
    def __init__(self, code: str):
        self.code = code
        self.pos = 0
        self.line = 1
        self.column = 1

    def tokenize(self):
        tokens = []
        while self.pos < len(self.code):
            ch = self.code[self.pos]

            if ch in " \t\r":
                self.pos += 1
                self.column += 1
                continue

            if ch == "\n":
                tokens.append(Token("NEWLINE", "\n", self.line, self.column))
                self.pos += 1
                self.line += 1
                self.column = 1
                continue

            if ch == "-":
                if self.pos + 1 < len(self.code) and self.code[self.pos + 1] == "-":
                    self.pos += 2
                    while self.pos < len(self.code) and self.code[self.pos] != "\n":
                        self.pos += 1
                    continue

            if ch.isdigit():
                start = self.pos
                while self.pos < len(self.code) and (
                    self.code[self.pos].isdigit() or self.code[self.pos] == "."
                ):
                    self.pos += 1
                num_str = self.code[start : self.pos]
                if "." in num_str:
                    value = float(num_str)
                else:
                    value = int(num_str)
                tokens.append(Token("NUMBER", value, self.line, self.column))
                self.column += self.pos - start
                continue

            if ch in "\"'":
                quote = ch
                self.pos += 1
                start = self.pos
                while self.pos < len(self.code) and self.code[self.pos] != quote:
                    self.pos += 1
                string_value = self.code[start : self.pos]
                self.pos += 1
                tokens.append(Token("STRING", string_value, self.line, self.column))
                self.column += len(string_value) + 2
                continue

            if ch.isalpha() or ch == "_":
                start = self.pos
                while self.pos < len(self.code) and (
                    self.code[self.pos].isalnum() or self.code[self.pos] == "_"
                ):
                    self.pos += 1
                name = self.code[start : self.pos]

                keywords = {
                    "and",
                    "or",
                    "not",
                    "if",
                    "then",
                    "else",
                    "elseif",
                    "end",
                    "while",
                    "do",
                    "repeat",
                    "until",
                    "for",
                    "in",
                    "break",
                    "continue",
                    "return",
                    "local",
                    "nil",
                    "true",
                    "false",
                    "function",
                    "print",
                    "read",
                }

                if name in keywords:
                    tokens.append(Token("KEYWORD", name, self.line, self.column))
                else:
                    tokens.append(Token("NAME", name, self.line, self.column))
                self.column += self.pos - start
                continue

            if ch in "+-*/%<>":
                op = ch
                self.pos += 1
                if self.pos < len(self.code) and self.code[self.pos] == "=":
                    op += self.code[self.pos]
                    self.pos += 1
                tokens.append(Token("OPERATOR", op, self.line, self.column))
                self.column += len(op)
                continue

            if ch == "=":
                tokens.append(Token("PUNCT", "=", self.line, self.column))
                self.pos += 1
                self.column += 1
                continue

            if ch == "~":
                self.pos += 1
                if self.pos < len(self.code) and self.code[self.pos] == "=":
                    tokens.append(Token("OPERATOR", "~=", self.line, self.column))
                    self.pos += 1
                    self.column += 2
                continue

            if ch in "(){}[],.;:":
                tokens.append(Token("PUNCT", ch, self.line, self.column))
                self.pos += 1
                self.column += 1
                continue

            self.pos += 1

        tokens.append(Token("EOF", None, self.line, self.column))
        return tokens


class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0

    def current_token(self) -> Token:
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return Token("EOF", None, 0, 0)

    def eat(self, expected_type: str, expected_value: Any = None):
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
                self.eat("NEWLINE")
        return ProgNode(statements)

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
            self.eat("NEWLINE")
            return None

        return self.expr()

    def print_stmt(self):
        self.eat("KEYWORD", "print")
        args = None
        if self.current_token().type == "PUNCT" and self.current_token().value == "(":
            self.eat("PUNCT", "(")
            if (
                self.current_token().type != "PUNCT"
                or self.current_token().value != ")"
            ):
                args = self.arg_list()
            self.eat("PUNCT", ")")
        return PrintStmtNode(args)

    def arg_list(self):
        args = []
        args.append(self.atom())
        while (
            self.current_token().type == "PUNCT" and self.current_token().value == ","
        ):
            self.eat("PUNCT", ",")
            args.append(self.atom())
        return ArgListNode(args)

    def fun_stmt(self):
        self.eat("KEYWORD", "function")
        name = self.eat("NAME")
        self.eat("PUNCT", "(")
        params = None
        if self.current_token().type == "NAME":
            params = self.params()
        self.eat("PUNCT", ")")
        block = self.block()
        self.eat("KEYWORD", "end")
        return FunStmtNode(name.value, params, block)

    def params(self):
        params = [self.eat("NAME").value]
        while (
            self.current_token().type == "PUNCT" and self.current_token().value == ","
        ):
            self.eat("PUNCT", ",")
            params.append(self.eat("NAME").value)
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
                self.eat("NEWLINE")
                continue
            stmt = self.statement()
            if stmt:
                statements.append(stmt)
        return BlockNode(statements)

    def for_stmt(self):
        self.eat("KEYWORD", "for")
        name = self.eat("NAME")
        self.eat("PUNCT", "=")
        start = self.expr()
        self.eat("PUNCT", ",")
        end = self.expr()
        self.eat("KEYWORD", "do")
        statements = []
        while (
            self.current_token().type != "KEYWORD"
            or self.current_token().value != "end"
        ):
            if self.current_token().type == "EOF":
                break
            if self.current_token().type == "NEWLINE":
                self.eat("NEWLINE")
                continue
            stmt = self.statement()
            if stmt:
                statements.append(stmt)
        self.eat("KEYWORD", "end")
        return ForStmtNode(name.value, start, end, statements)

    def while_stmt(self):
        self.eat("KEYWORD", "while")
        condition = self.expr()
        self.eat("KEYWORD", "do")
        statements = []
        while (
            self.current_token().type != "KEYWORD"
            or self.current_token().value != "end"
        ):
            if self.current_token().type == "EOF":
                break
            if self.current_token().type == "NEWLINE":
                self.eat("NEWLINE")
                continue
            stmt = self.statement()
            if stmt:
                statements.append(stmt)
        self.eat("KEYWORD", "end")
        return WhileStmtNode(condition, statements)

    def repeat_stmt(self):
        self.eat("KEYWORD", "repeat")
        statements = []
        while (
            self.current_token().type != "KEYWORD"
            or self.current_token().value != "until"
        ):
            if self.current_token().type == "EOF":
                break
            if self.current_token().type == "NEWLINE":
                self.eat("NEWLINE")
                continue
            stmt = self.statement()
            if stmt:
                statements.append(stmt)
        self.eat("KEYWORD", "until")
        condition = self.expr()
        return RepeatStmtNode(statements, condition)

    def if_stmt(self):
        self.eat("KEYWORD", "if")
        conditions = []
        blocks = []

        condition = self.expr()
        self.eat("KEYWORD", "then")
        block = self.block()
        conditions.append(condition)
        blocks.append(block)

        while (
            self.current_token().type == "KEYWORD"
            and self.current_token().value == "elseif"
        ):
            self.eat("KEYWORD", "elseif")
            condition = self.expr()
            self.eat("KEYWORD", "then")
            block = self.block()
            conditions.append(condition)
            blocks.append(block)

        if (
            self.current_token().type == "KEYWORD"
            and self.current_token().value == "else"
        ):
            self.eat("KEYWORD", "else")
            block = self.block()
            blocks.append(block)

        self.eat("KEYWORD", "end")
        return IfStmtNode(conditions, blocks)

    def break_stmt(self):
        self.eat("KEYWORD", "break")
        return BreakStmtNode()

    def continue_stmt(self):
        self.eat("KEYWORD", "continue")
        return ContinueStmtNode()

    def return_stmt(self):
        self.eat("KEYWORD", "return")
        expr = None
        if self.current_token().type not in [
            "NEWLINE",
            "KEYWORD",
        ] or self.current_token().value not in ["end", "else", "elseif"]:
            expr = self.expr()
        return ReturnStmtNode(expr)

    def read_stmt(self):
        self.eat("KEYWORD", "read")
        self.eat("PUNCT", "(")
        self.eat("PUNCT", ")")
        return ReadStmtNode()

    def assign(self):
        name = self.eat("NAME")
        self.eat("PUNCT", "=")

        if (
            self.current_token().type == "KEYWORD"
            and self.current_token().value == "read"
        ):
            read_node = self.read_stmt()
            return AssignNode(name.value, read_node)
        else:
            value = self.expr()
            return AssignNode(name.value, value)

    def expr(self):
        return self.or_expr()

    def or_expr(self):
        left = self.and_expr()
        while (
            self.current_token().type == "KEYWORD"
            and self.current_token().value == "or"
        ):
            self.eat("KEYWORD", "or")
            right = self.and_expr()
            left = OrExprNode(left, right)
        return left

    def and_expr(self):
        left = self.not_expr()
        while (
            self.current_token().type == "KEYWORD"
            and self.current_token().value == "and"
        ):
            self.eat("KEYWORD", "and")
            right = self.not_expr()
            left = AndExprNode(left, right)
        return left

    def not_expr(self):
        if (
            self.current_token().type == "KEYWORD"
            and self.current_token().value == "not"
        ):
            self.eat("KEYWORD", "not")
            expr = self.not_expr()
            return NotExprNode(expr)
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
            op = self.eat("OPERATOR").value
            right = self.add_expr()
            return ComparisonNode(left, op, right)
        return left

    def add_expr(self):
        left = self.mul_expr()
        while (
            self.current_token().type == "OPERATOR"
            and self.current_token().value in ["+", "-"]
        ):
            op = self.eat("OPERATOR").value
            right = self.mul_expr()
            left = AddExprNode(left, op, right)
        return left

    def mul_expr(self):
        left = self.atom()
        while (
            self.current_token().type == "OPERATOR"
            and self.current_token().value in ["*", "/", "%"]
        ):
            op = self.eat("OPERATOR").value
            right = self.atom()
            left = MulExprNode(left, op, right)
        return left

    def atom(self):
        token = self.current_token()

        if token.type == "NUMBER":
            self.eat("NUMBER")
            return AtomNode("number", token.value)
        elif token.type == "STRING":
            self.eat("STRING")
            return AtomNode("string", token.value)
        elif token.type == "KEYWORD" and token.value in ["true", "false", "nil"]:
            self.eat("KEYWORD")
            return AtomNode("literal", token.value)
        elif (
            token.type == "PUNCT" and token.value == "{"
        ):  # Добавить проверку на таблицу
            return self.table()
        elif token.type == "NAME":
            self.eat("NAME")
            # Check for function call
            if (
                self.current_token().type == "PUNCT"
                and self.current_token().value == "("
            ):
                return self.call_fun(token.value)
            # Check for table access
            elif (
                self.current_token().type == "PUNCT"
                and self.current_token().value == "."
            ):
                self.eat("PUNCT", ".")
                field = self.eat("NAME")
                return AtomNode("field", (token.value, field.value))
            elif (
                self.current_token().type == "PUNCT"
                and self.current_token().value == "["
            ):
                self.eat("PUNCT", "[")
                index = self.expr()
                self.eat("PUNCT", "]")
                return AtomNode("index", (token.value, index))
            else:
                return AtomNode("name", token.value)
        elif token.type == "PUNCT" and token.value == "(":
            self.eat("PUNCT", "(")
            expr = self.expr()
            self.eat("PUNCT", ")")
            return expr
        elif token.type == "OPERATOR" and token.value == "-":
            self.eat("OPERATOR", "-")
            expr = self.atom()
            return UnaryMinusNode(expr)

        return AtomNode("none", None)


def table(self):
    self.eat("PUNCT", "{")
    elements = []
    if self.current_token().type != "PUNCT" or self.current_token().value != "}":
        elements = self.table_elements()
    self.eat("PUNCT", "}")
    return TableNode(elements)


def table_elements(self):
    elements = [self.table_element()]
    while self.current_token().type == "PUNCT" and self.current_token().value == ",":
        self.eat("PUNCT", ",")
        if self.current_token().type != "PUNCT" or self.current_token().value != "}":
            elements.append(self.table_element())
    return elements


def table_element(self):
    # Значение без ключа
    return TableElementNode(None, self.expr())

    def call_fun(self, name):
        self.eat("PUNCT", "(")
        args = None
        if self.current_token().type != "PUNCT" or self.current_token().value != ")":
            args = self.args()
        self.eat("PUNCT", ")")
        return CallFunNode(name, args)

    def args(self):
        args = []
        args.append(self.expr())
        while (
            self.current_token().type == "PUNCT" and self.current_token().value == ","
        ):
            self.eat("PUNCT", ",")
            args.append(self.expr())
        return ArgsNode(args)


class ProgNode:
    def __init__(self, statements):
        self.statements = statements


class ParamsNode:
    def __init__(self, params):
        self.params = params


class FunStmtNode:
    def __init__(self, name, params, block):
        self.name = name
        self.params = params
        self.block = block


class PrintStmtNode:
    def __init__(self, args):
        self.args = args


class ArgListNode:
    def __init__(self, args):
        self.args = args


class BlockNode:
    def __init__(self, statements):
        self.statements = statements


class ForStmtNode:
    def __init__(self, name, start, end, statements):
        self.name = name
        self.start = start
        self.end = end
        self.statements = statements


class WhileStmtNode:
    def __init__(self, condition, statements):
        self.condition = condition
        self.statements = statements


class RepeatStmtNode:
    def __init__(self, statements, condition):
        self.statements = statements
        self.condition = condition


class IfStmtNode:
    def __init__(self, conditions, blocks):
        self.conditions = conditions
        self.blocks = blocks


class BreakStmtNode:
    pass


class ContinueStmtNode:
    pass


class ReturnStmtNode:
    def __init__(self, expr):
        self.expr = expr


class ReadStmtNode:
    pass


class AssignNode:
    def __init__(self, name, value):
        self.name = name
        self.value = value


class CallFunNode:
    def __init__(self, name, args):
        self.name = name
        self.args = args


class ArgsNode:
    def __init__(self, args):
        self.args = args


class OrExprNode:
    def __init__(self, left, right):
        self.left = left
        self.right = right


class AndExprNode:
    def __init__(self, left, right):
        self.left = left
        self.right = right


class NotExprNode:
    def __init__(self, expr):
        self.expr = expr


class ComparisonNode:
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right


class AddExprNode:
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right


class MulExprNode:
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right


class UnaryMinusNode:
    def __init__(self, expr):
        self.expr = expr


class AtomNode:
    def __init__(self, type_, value):
        self.type = type_
        self.value = value


class TableNode:
    def __init__(self, elements):
        self.elements = elements


class TableElementNode:
    def __init__(self, key, value):
        self.key = key
        self.value = value


class LuaVisitor:
    def visit(self, node):
        method_name = f"visit{node.__class__.__name__}"
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        pass


class Compilator(LuaVisitor):
    def __init__(self):
        self.call_stack = [{}]

    def visitProgNode(self, node):
        results = []
        for stmt in node.statements:
            res = self.visit(stmt)
            if res is not None:
                results.append(res)
        return results[-1] if results else None

    def visitParamsNode(self, node):
        return node.params

    def visitFunStmtNode(self, node):
        self.call_stack[-1][node.name] = {
            "params": node.params.params if node.params else [],
            "block": node.block,
        }
        return None

    def visitReadStmtNode(self, node):
        value = input()
        try:
            return int(value)
        except:
            try:
                return float(value)
            except:
                return value

    def visitPrintStmtNode(self, node):
        values = []
        if node.args:
            for atom_node in node.args.args:
                val = self.visit(atom_node)
                values.append(val)
        output = " ".join(str(v) for v in values)
        print(output)
        return None

    def visitArgListNode(self, node):
        result = []
        for arg in node.args:
            result.append(self.visit(arg))
        return result

    def visitReturnStmtNode(self, node):
        return self.visit(node.expr) if node.expr else None

    def visitBlockNode(self, node):
        result = None
        for stmt in node.statements:
            result = self.visit(stmt)
        return result

    def visitForStmtNode(self, node):
        var_name = node.name
        start = int(self.visit(node.start))
        end = int(self.visit(node.end))
        result = None
        try:
            for i in range(start, end):
                self.call_stack[-1][var_name] = i
                try:
                    for stmt in node.statements:
                        result = self.visit(stmt)
                except BreakException:
                    break
                except ContinueException:
                    continue
        except BreakException:
            return result
        return result
    
    def visitTableNode(self, node):
        result = []
        for el in node.elements:
            result.append(self.visit(el))
        return result

    def visitTableElementNode(self, node):
        return self.visit(node.value)  # Просто возвращаем значение

    def visitWhileStmtNode(self, node):
        result = None
        try:
            while self.visit(node.condition):
                try:
                    for stmt in node.statements:
                        result = self.visit(stmt)
                except BreakException:
                    break
                except ContinueException:
                    continue
        except BreakException:
            return result
        return result

    def visitRepeatStmtNode(self, node):
        result = None
        try:
            while True:
                try:
                    for stmt in node.statements:
                        result = self.visit(stmt)
                except BreakException:
                    break
                except ContinueException:
                    continue
                if self.visit(node.condition):
                    break
        except BreakException:
            return result
        return result

    def visitIfStmtNode(self, node):
        for i, condition in enumerate(node.conditions):
            if self.visit(condition):
                for stmt in node.blocks[i].statements:
                    result = self.visit(stmt)
                return result
        if len(node.blocks) > len(node.conditions):
            for stmt in node.blocks[-1].statements:
                result = self.visit(stmt)
            return result
        return None

    def visitBreakStmtNode(self, node):
        raise BreakException()

    def visitContinueStmtNode(self, node):
        raise ContinueException()

    def visitAssignNode(self, node):
        value = self.visit(node.value)
        self.call_stack[-1][node.name] = value
        return value

    def visitCallFunNode(self, node):
        name = node.name
        args = []
        if node.args:
            args = self.visit(node.args)

        func = self.call_stack[-1].get(name)
        if not func:
            return None

        self.call_stack.append({})

        for i in range(len(func["params"])):
            if i < len(args):
                self.call_stack[-1][func["params"][i]] = args[i]

        block = func["block"]
        result = self.visit(block)

        self.call_stack.pop()
        return result

    def visitArgsNode(self, node):
        result = []
        for arg in node.args:
            result.append(self.visit(arg))
        return result

    def visitOrExprNode(self, node):
        return self.visit(node.left) or self.visit(node.right)

    def visitAndExprNode(self, node):
        return self.visit(node.left) and self.visit(node.right)

    def visitNotExprNode(self, node):
        return not self.visit(node.expr)

    def visitComparisonNode(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)
        if node.op == "<":
            return left < right
        elif node.op == ">":
            return left > right
        elif node.op == "<=":
            return left <= right
        elif node.op == ">=":
            return left >= right
        elif node.op == "==":
            return left == right
        elif node.op == "~=":
            return left != right

    def visitAddExprNode(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)
        if node.op == "+":
            return left + right
        else:
            return left - right

    def visitMulExprNode(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)
        if node.op == "*":
            return left * right
        elif node.op == "/":
            return left / right
        else:
            return left % right

    def visitUnaryMinusNode(self, node):
        return -self.visit(node.expr)

    def visitAtomNode(self, node):
        if node.type == "number":
            return node.value
        if node.type == "string":
            return node.value
        if node.type == "literal":
            if node.value == "true":
                return True
            if node.value == "false":
                return False
            if node.value == "nil":
                return None
        if node.type == "name":
            return self.call_stack[-1].get(node.value, 0)
        if node.type == "field":
            table_name, field_name = node.value
            table = self.call_stack[-1].get(table_name, {})
            if isinstance(table, list):
                for item in table:
                    if isinstance(item, dict) and field_name in item:
                        return item[field_name]
            return None
        if node.type == "index":
            table_name, index_node = node.value
            table = self.call_stack[-1].get(table_name, [])
            index = self.visit(index_node) - 1
            if 0 <= index < len(table):
                val = table[index]
                if isinstance(val, dict):
                    for k in val:
                        return val[k]
                return val
            return None
        return 0


def run_lua_code(code):
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    compilator = Compilator()
    return compilator.visit(ast)


if __name__ == "__main__":
    test_code = """
function add(a, b)
    return a+b
end

print(add(1,2))

for i=1,10 do
    print(i)
end

a=0
while a<6 and true do
    print(a)
    a=a+1
end

b=5
repeat
    print(b)
    b=b+1
until b>10

y=0
while true do
    print(y)
    y=y+1
    if y>7 then
        print("stop")
        break
    end
end

the_t={1, 2, 3}
for i=1,3 do
    print(the_t[i])
end

k=read()
print("read:", k)
"""
    run_lua_code(test_code)
