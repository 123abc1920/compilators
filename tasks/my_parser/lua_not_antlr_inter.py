from .nodes import LuaVisitor
from .lexer import Lexer
from .parser import Parser


class BreakException(Exception):
    pass


class ContinueException(Exception):
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
        return self.visit(node.value)

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
