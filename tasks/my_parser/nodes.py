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
