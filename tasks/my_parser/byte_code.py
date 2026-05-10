class Cmds:
    PUSH = 1
    PUSH_CONST = 2
    POP = 3
    ADD = 10
    SUB = 11
    MUL = 12
    DIV = 13
    LOAD = 20
    STORE = 21
    JMP = 30
    JMP_IF = 31
    CALL = 40
    RET = 41
    PRINT = 50
    READ = 51
    HALT = 99


class BytecodeCreator:
    def __init__(self):
        self.bytecode = []
        self.constants = []
        self.constants_map = {}
        self.labels = {}
        self.label_counter = 0

    def compile(self, ast_node):
        self.bytecode = []
        self.constants = []
        self.constants_map = {}
        self.generate(ast_node)
        self.bytecode.append(Cmds.HALT)

        return self.bytecode, self.constants

    def _add_constant(self, value):
        if value in self.constants_map:
            return self.constants_map[value]

        idx = len(self.constants)
        self.constants.append(value)
        self.constants_map[value] = idx
        return idx

    def generate(self, node):
        if node is None:
            return

        node_name = node.__class__.__name__

        method_name = f"gen_{node_name}"
        if hasattr(self, method_name):
            method = getattr(self, method_name)
            method(node)
        else:
            for attr in dir(node):
                if attr.startswith("_"):
                    continue
                value = getattr(node, attr)
                if isinstance(value, list):
                    for item in value:
                        if hasattr(item, "__dict__"):
                            self.generate(item)
                elif hasattr(value, "__dict__"):
                    self.generate(value)

    def gen_ProgNode(self, node):
        for stmt in node.statements:
            self.generate(stmt)

    def gen_AssignNode(self, node):
        self.generate(node.value)
        self.bytecode.append(Cmds.STORE)
        self.bytecode.append(node.name)

    def gen_PrintStmtNode(self, node):
        if node.args and node.args.args:
            for arg in node.args.args:
                self.generate(arg)
                self.bytecode.append(Cmds.PRINT)

    def gen_AtomNode(self, node):
        if node.type == "number":
            self.bytecode.append(Cmds.PUSH)
            self.bytecode.append(node.value)

        elif node.type == "string":
            const_idx = self._add_constant(node.value)
            self.bytecode.append(Cmds.PUSH_CONST)
            self.bytecode.append(const_idx)

        elif node.type == "name":
            self.bytecode.append(Cmds.LOAD)
            self.bytecode.append(node.value)

        elif node.type == "literal":
            if node.value == "true":
                self.bytecode.append(Cmds.PUSH)
                self.bytecode.append(1)
            elif node.value == "false":
                self.bytecode.append(Cmds.PUSH)
                self.bytecode.append(0)
            elif node.value == "nil":
                self.bytecode.append(Cmds.PUSH)
                self.bytecode.append(None)

    def gen_AddExprNode(self, node):
        self.generate(node.left)
        self.generate(node.right)
        if node.op == "+":
            self.bytecode.append(Cmds.ADD)
        elif node.op == "-":
            self.bytecode.append(Cmds.SUB)

    def gen_MulExprNode(self, node):
        self.generate(node.left)
        self.generate(node.right)
        if node.op == "*":
            self.bytecode.append(Cmds.MUL)
        elif node.op == "/":
            self.bytecode.append(Cmds.DIV)

    def gen_ReadStmtNode(self, node):
        self.bytecode.append(Cmds.READ)
