class Node:
    def __init__(self, line=0, col=0):
        self.line = line
        self.col = col


class ProgNode(Node):
    def __init__(self, statements, line=0, col=0):
        super().__init__(line, col)
        self.statements = statements


class ParamsNode(Node):
    def __init__(self, params, line=0, col=0):
        super().__init__(line, col)
        self.params = params


class FunStmtNode(Node):
    def __init__(self, name, params, block, line=0, col=0):
        super().__init__(line, col)
        self.name = name
        self.params = params
        self.block = block


class PrintStmtNode(Node):
    def __init__(self, args, line=0, col=0):
        super().__init__(line, col)
        self.args = args


class ArgListNode(Node):
    def __init__(self, args, line=0, col=0):
        super().__init__(line, col)
        self.args = args


class BlockNode(Node):
    def __init__(self, statements, line=0, col=0):
        super().__init__(line, col)
        self.statements = statements


class ForStmtNode(Node):
    def __init__(self, name, start, end, statements, line=0, col=0):
        super().__init__(line, col)
        self.name = name
        self.start = start
        self.end = end
        self.statements = statements


class WhileStmtNode(Node):
    def __init__(self, condition, statements, line=0, col=0):
        super().__init__(line, col)
        self.condition = condition
        self.statements = statements


class RepeatStmtNode(Node):
    def __init__(self, statements, condition, line=0, col=0):
        super().__init__(line, col)
        self.statements = statements
        self.condition = condition


class IfStmtNode(Node):
    def __init__(self, conditions, blocks, line=0, col=0):
        super().__init__(line, col)
        self.conditions = conditions
        self.blocks = blocks


class BreakStmtNode(Node):
    pass


class ContinueStmtNode(Node):
    pass


class ReturnStmtNode(Node):
    def __init__(self, expr, line=0, col=0):
        super().__init__(line, col)
        self.expr = expr


class ReadStmtNode(Node):
    pass


class AssignNode(Node):
    def __init__(self, name, value, line=0, col=0):
        super().__init__(line, col)
        self.name = name
        self.value = value


class CallFunNode(Node):
    def __init__(self, name, args, line=0, col=0):
        super().__init__(line, col)
        self.name = name
        self.args = args


class ArgsNode(Node):
    def __init__(self, args, line=0, col=0):
        super().__init__(line, col)
        self.args = args


class OrExprNode(Node):
    def __init__(self, left, right, line=0, col=0):
        super().__init__(line, col)
        self.left = left
        self.right = right


class AndExprNode(Node):
    def __init__(self, left, right, line=0, col=0):
        super().__init__(line, col)
        self.left = left
        self.right = right


class NotExprNode(Node):
    def __init__(self, expr, line=0, col=0):
        super().__init__(line, col)
        self.expr = expr


class ComparisonNode(Node):
    def __init__(self, left, op, right, line=0, col=0):
        super().__init__(line, col)
        self.left = left
        self.op = op
        self.right = right


class AddExprNode(Node):
    def __init__(self, left, op, right, line=0, col=0):
        super().__init__(line, col)
        self.left = left
        self.op = op
        self.right = right


class MulExprNode(Node):
    def __init__(self, left, op, right, line=0, col=0):
        super().__init__(line, col)
        self.left = left
        self.op = op
        self.right = right


class UnaryMinusNode(Node):
    def __init__(self, expr, line=0, col=0):
        super().__init__(line, col)
        self.expr = expr


class AtomNode(Node):
    def __init__(self, type_, value, line=0, col=0):
        super().__init__(line, col)
        self.type = type_
        self.value = value


class TableNode(Node):
    def __init__(self, elements, line=0, col=0):
        super().__init__(line, col)
        self.elements = elements


class TableElementNode(Node):
    def __init__(self, key, value, line=0, col=0):
        super().__init__(line, col)
        self.key = key
        self.value = value


class LuaVisitor:
    def visit(self, node):
        method_name = f"visit{node.__class__.__name__}"
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        pass


def tree_to_string(node):
    if node is None:
        return ""

    node_name = node.__class__.__name__.replace("Node", "")
    result = node_name

    if hasattr(node, "name"):
        result += f" [{node.name}]"
    if hasattr(node, "value") and not isinstance(node.value, (list, dict)):
        if hasattr(node.value, "__dict__"):
            pass
        else:
            result += f" = {repr(node.value)}"
    if hasattr(node, "op"):
        result += f" {node.op}"

    children = []

    for attr_name, attr_value in node.__dict__.items():
        if attr_name == "value" and hasattr(attr_value, "__dict__"):
            children.append(tree_to_string(attr_value))
        elif isinstance(attr_value, list):
            for item in attr_value:
                if hasattr(item, "__dict__"):
                    children.append(tree_to_string(item))
                elif item is not None:
                    children.append(repr(item))
        elif hasattr(attr_value, "__dict__"):
            children.append(tree_to_string(attr_value))
        elif attr_value is not None and attr_name not in ["op", "name", "value"]:
            if not isinstance(attr_value, (str, int, float, bool)):
                children.append(repr(attr_value))

    if children:
        result += " ( " + " ".join(children) + " )"

    return result
