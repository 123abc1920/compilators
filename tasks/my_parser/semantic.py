from .nodes import CastNode


class CodeObject:
    def __init__(self, name, type_, line, col):
        self.name = name
        self.type = type_
        self.line = line
        self.col = col
        self.num_params = None


class CodeObjectsTable:
    def __init__(self):
        self.stack = [{}]
        self.in_loop = False
        self.in_function = False

    def append_stack(self):
        self.stack.append({})

    def pop_stack(self):
        self.stack.pop()

    def define(self, name, type_, line, col):
        if name in self.stack[-1]:
            return False
        self.stack[-1][name] = CodeObject(name, type_, line, col)
        return True

    def find_code_obj(self, name):
        for code_obj in reversed(self.stack):
            if name in code_obj:
                return code_obj[name]
        return None


class SemanticAnalizator:
    def __init__(self):
        self.symbols = CodeObjectsTable()
        self.errors = []

    def error(self, message, line, col):
        self.errors.append(f"Semantic error at {line}:{col}: {message}")

    def analyze(self, node):
        self.visit(node)
        return self.errors

    def visit(self, node):
        method_name = f"visit{node.__class__.__name__}"
        method = getattr(self, method_name, self.generic_visit)
        return method(node)

    def generic_visit(self, node):
        for attr in dir(node):
            if attr.startswith("_"):
                continue
            value = getattr(node, attr)
            if isinstance(value, list):
                for item in value:
                    if hasattr(item, "__dict__"):
                        self.visit(item)
            elif hasattr(value, "__dict__"):
                self.visit(value)

    def visitProgNode(self, node):
        for stmt in node.statements:
            self.visit(stmt)

    def visitAssignNode(self, node):
        self.visit(node.value)

        sym = self.symbols.find_code_obj(node.name)
        if sym is None:
            var_type = self.get_expr_type(node.value)
            self.symbols.define(node.name, var_type, node.line, node.col)

    def visitAtomNode(self, node):
        if node.type == "name":
            sym = self.symbols.find_code_obj(node.value)
            if sym is None:
                self.error(f"Variable '{node.value}' not defined", node.line, node.col)

    def visitAddExprNode(self, node):
        self.visit(node.left)
        self.visit(node.right)

    def visitComparisonNode(self, node):
        self.visit(node.left)
        self.visit(node.right)

    def visitFunStmtNode(self, node):
        self.symbols.define(node.name, "function", node.line, node.col)

        sym = self.symbols.find_code_obj(node.name)
        if sym:
            sym.num_params = len(node.params.params) if node.params else 0

        self.symbols.append_stack()
        self.symbols.in_function = True

        if node.params:
            for param in node.params.params:
                self.symbols.define(param, "any", node.line, node.col)

        if node.block:
            self.visit(node.block)

        self.symbols.pop_stack()
        self.symbols.in_function = False

    def visitWhileStmtNode(self, node):
        old_in_loop = self.symbols.in_loop
        self.symbols.in_loop = True

        self.visit(node.condition)
        for stmt in node.statements:
            self.visit(stmt)

        self.symbols.in_loop = old_in_loop

    def visitForStmtNode(self, node):
        old_in_loop = self.symbols.in_loop
        self.symbols.in_loop = True

        self.visit(node.start)
        self.visit(node.end)

        self.symbols.append_stack()
        self.symbols.define(node.name, "number", node.line, node.col)

        for stmt in node.statements:
            self.visit(stmt)

        self.symbols.pop_stack()
        self.symbols.in_loop = old_in_loop

    def visitBreakStmtNode(self, node):
        if not self.symbols.in_loop:
            self.error("'break' outside of loop", node.line, node.col)

    def visitContinueStmtNode(self, node):
        if not self.symbols.in_loop:
            self.error("'continue' outside of loop", node.line, node.col)

    def visitReturnStmtNode(self, node):
        if not self.symbols.in_function:
            self.error("'return' outside of function", node.line, node.col)
        if node.expr:
            self.visit(node.expr)

    def visitCallFunNode(self, node):
        sym = self.symbols.find_code_obj(node.name)
        if sym is None:
            self.error(f"Function '{node.name}' not defined", node.line, node.col)
            return node

        if sym.num_params is not None:
            num_args = len(node.args.args) if node.args else 0
            if num_args != sym.num_params:
                self.error(
                    f"Function '{node.name}' expects {sym.num_params} argument(s), "
                    f"but got {num_args}",
                    node.line,
                    node.col,
                )

        if node.args:
            for arg in node.args.args:
                self.visit(arg)

    def get_expr_type(self, node):
        node_name = node.__class__.__name__

        if node_name == "AtomNode":
            if node.type == "number":
                return "number"
            if node.type == "string":
                return "string"
            if node.type == "literal":
                if node.value in ("true", "false"):
                    return "boolean"
                return "nil"
            if node.type == "name":
                sym = self.symbols.find_code_obj(node.value)
                return sym.type if sym else "unknown"

        if node_name in ("AddExprNode", "MulExprNode"):
            return "number"

        if node_name == "ComparisonNode":
            return "boolean"

        return "unknown"


class ASTModifier:
    def __init__(self, symbol_table):
        self.symbols = symbol_table

    def modify(self, node):
        return self.visit(node)

    def visit(self, node):
        if node is None:
            return None

        node_name = node.__class__.__name__

        if node_name == "AddExprNode":
            return self.modifyAddExprNode(node)

        for attr_name, attr_value in node.__dict__.items():
            if attr_name in ("line", "col"):
                continue
            if isinstance(attr_value, list):
                for i, item in enumerate(attr_value):
                    if hasattr(item, "__dict__"):
                        attr_value[i] = self.visit(item)
            elif hasattr(attr_value, "__dict__"):
                setattr(node, attr_name, self.visit(attr_value))

        return node

    def modifyAddExprNode(self, node):
        node.left = self.visit(node.left)
        node.right = self.visit(node.right)

        left_type = self.get_type(node.left)
        right_type = self.get_type(node.right)

        if left_type == "number" and right_type == "number":
            return node

        if left_type == "string" and right_type == "number":
            node.right = CastNode(node.right, "string", node.right.line, node.right.col)
        elif left_type == "number" and right_type == "string":
            node.left = CastNode(node.left, "string", node.left.line, node.left.col)

        return node

    def get_type(self, node):
        node_name = node.__class__.__name__

        if node_name == "AtomNode":
            if node.type == "number":
                return "number"
            if node.type == "string":
                return "string"
            if node.type == "name":
                sym = self.symbols.find_code_obj(node.value)
                return sym.type if sym else "unknown"

        if node_name == "CastNode":
            return node.target_type

        return "unknown"
