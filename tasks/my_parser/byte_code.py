class Cmds:
    PUSH = 1
    PUSH_CONST = 2
    LOAD = 4
    STORE = 5
    ADD = 10
    SUB = 11
    MUL = 12
    DIV = 13
    MOD = 14
    UNARY_MINUS = 15
    OR = 20
    AND = 21
    NOT = 22
    LT = 23
    GT = 24
    LTE = 25
    GTE = 26
    EQ = 27
    NEQ = 28
    JMP = 30
    JMP_IF = 31
    JMP_IF_NOT = 32
    CALL = 40
    RET = 41
    PRINT = 60
    READ = 61
    MAKE_TABLE = 70
    TABLE_GET = 71
    HALT = 99


class BytecodeCreator:
    def __init__(self):
        self.bytecode = []
        self.constants = []
        self.constants_map = {}
        self.labels = {}
        self.label_counter = 0
        self.functions = {}
        self.current_break = None
        self.current_continue = None

    def compile(self, ast_node):
        self.bytecode = []
        self.constants = []
        self.constants_map = {}
        self.labels = {}
        self.label_counter = 0
        self.functions = {}
        self._generate(ast_node)
        self.bytecode.append(Cmds.HALT)
        self._resolve_labels()
        return self.bytecode, self.constants, self.functions

    def _resolve_labels(self):
        i = 0
        while i < len(self.bytecode):
            op = self.bytecode[i]
            if op in (Cmds.JMP, Cmds.JMP_IF, Cmds.JMP_IF_NOT):
                label = self.bytecode[i + 1]
                if label in self.labels:
                    self.bytecode[i + 1] = self.labels[label]
            i += 1

    def _add_constant(self, value):
        if value in self.constants_map:
            return self.constants_map[value]
        idx = len(self.constants)
        self.constants.append(value)
        self.constants_map[value] = idx
        return idx

    def _new_label(self):
        lbl = self.label_counter
        self.label_counter += 1
        return lbl

    def _generate(self, node):
        if node is None:
            return
        node_name = node.__class__.__name__
        method = getattr(self, f"gen_{node_name}", None)
        if method:
            method(node)
        else:
            for attr in dir(node):
                if attr.startswith("_"):
                    continue
                val = getattr(node, attr)
                if isinstance(val, list):
                    for item in val:
                        if hasattr(item, "__dict__"):
                            self._generate(item)
                elif hasattr(val, "__dict__"):
                    self._generate(val)

    def gen_ProgNode(self, node):
        for stmt in node.statements:
            self._generate(stmt)

    def gen_BlockNode(self, node):
        for stmt in node.statements:
            self._generate(stmt)

    def gen_AssignNode(self, node):
        self._generate(node.value)
        self.bytecode.append(Cmds.STORE)
        self.bytecode.append(node.name)

    def gen_AtomNode(self, node):
        if node.type == "number":
            self.bytecode.append(Cmds.PUSH)
            self.bytecode.append(node.value)
        elif node.type == "string":
            self.bytecode.append(Cmds.PUSH_CONST)
            idx = self._add_constant(node.value)
            self.bytecode.append(idx)
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
        elif node.type == "index":
            table_name, index_node = node.value
            self._generate(index_node)
            self.bytecode.append(Cmds.LOAD)
            self.bytecode.append(table_name)
            self.bytecode.append(Cmds.TABLE_GET)

    def gen_PrintStmtNode(self, node):
        if node.args and node.args.args:
            for arg in reversed(node.args.args):
                self._generate(arg)
            self.bytecode.append(Cmds.PRINT)
            self.bytecode.append(len(node.args.args))

    def gen_ReadStmtNode(self, node):
        self.bytecode.append(Cmds.READ)

    def gen_BinOpNode(self, node):
        self._generate(node.left)
        self._generate(node.right)
        ops = {
            '+': Cmds.ADD,
            '-': Cmds.SUB,
            '*': Cmds.MUL,
            '/': Cmds.DIV,
            '%': Cmds.MOD,
        }
        self.bytecode.append(ops.get(node.op, Cmds.ADD))

    def gen_AddExprNode(self, node):
        self._generate(node.left)
        self._generate(node.right)
        self.bytecode.append(Cmds.ADD if node.op == "+" else Cmds.SUB)

    def gen_MulExprNode(self, node):
        self._generate(node.left)
        self._generate(node.right)
        if node.op == "*":
            self.bytecode.append(Cmds.MUL)
        elif node.op == "/":
            self.bytecode.append(Cmds.DIV)
        else:
            self.bytecode.append(Cmds.MOD)

    def gen_UnaryMinusNode(self, node):
        self._generate(node.expr)
        self.bytecode.append(Cmds.UNARY_MINUS)

    def gen_ComparisonNode(self, node):
        self._generate(node.left)
        self._generate(node.right)
        ops = {
            "<": Cmds.LT,
            ">": Cmds.GT,
            "<=": Cmds.LTE,
            ">=": Cmds.GTE,
            "==": Cmds.EQ,
            "~=": Cmds.NEQ,
        }
        self.bytecode.append(ops[node.op])

    def gen_OrExprNode(self, node):
        self._generate(node.left)
        self._generate(node.right)
        self.bytecode.append(Cmds.OR)

    def gen_AndExprNode(self, node):
        self._generate(node.left)
        self._generate(node.right)
        self.bytecode.append(Cmds.AND)

    def gen_NotExprNode(self, node):
        self._generate(node.expr)
        self.bytecode.append(Cmds.NOT)

    def gen_IfStmtNode(self, node):
        end_labels = []
        for i, cond in enumerate(node.conditions):
            self._generate(cond)
            else_lbl = self._new_label()
            self.bytecode.append(Cmds.JMP_IF_NOT)
            self.bytecode.append(else_lbl)
            for stmt in node.blocks[i].statements:
                self._generate(stmt)
            skip_lbl = self._new_label()
            self.bytecode.append(Cmds.JMP)
            self.bytecode.append(skip_lbl)
            self.labels[else_lbl] = len(self.bytecode)
            end_labels.append(skip_lbl)
        
        if len(node.blocks) > len(node.conditions):
            for stmt in node.blocks[-1].statements:
                self._generate(stmt)
        
        for lbl in end_labels:
            self.labels[lbl] = len(self.bytecode)

    def gen_WhileStmtNode(self, node):
        start = self._new_label()
        self.labels[start] = len(self.bytecode)
        self._generate(node.condition)
        end = self._new_label()
        self.bytecode.append(Cmds.JMP_IF_NOT)
        self.bytecode.append(end)
        old_break = self.current_break
        old_continue = self.current_continue
        self.current_break = end
        self.current_continue = start
        for stmt in node.statements:
            self._generate(stmt)
        self.current_break = old_break
        self.current_continue = old_continue
        self.bytecode.append(Cmds.JMP)
        self.bytecode.append(start)
        self.labels[end] = len(self.bytecode)

    def gen_RepeatStmtNode(self, node):
        start = self._new_label()
        self.labels[start] = len(self.bytecode)
        old_continue = self.current_continue
        self.current_continue = start
        for stmt in node.statements:
            self._generate(stmt)
        self.current_continue = old_continue
        self._generate(node.condition)
        self.bytecode.append(Cmds.JMP_IF_NOT)
        self.bytecode.append(start)

    def gen_ForStmtNode(self, node):
        self._generate(node.start)
        self.bytecode.append(Cmds.STORE)
        self.bytecode.append(node.name)
        
        self._generate(node.end)
        limit_var = f"__limit_{node.name}"
        self.bytecode.append(Cmds.STORE)
        self.bytecode.append(limit_var)
        
        self.bytecode.append(Cmds.PUSH)
        self.bytecode.append(1)
        step_var = f"__step_{node.name}"
        self.bytecode.append(Cmds.STORE)
        self.bytecode.append(step_var)
        
        start_label = self._new_label()
        self.labels[start_label] = len(self.bytecode)
        
        self.bytecode.append(Cmds.LOAD)
        self.bytecode.append(node.name)
        self.bytecode.append(Cmds.LOAD)
        self.bytecode.append(limit_var)
        self.bytecode.append(Cmds.LT)
        end_label = self._new_label()
        self.bytecode.append(Cmds.JMP_IF_NOT)
        self.bytecode.append(end_label)
        
        old_break = self.current_break
        old_continue = self.current_continue
        self.current_break = end_label
        self.current_continue = start_label
        
        for stmt in node.statements:
            self._generate(stmt)
        
        self.current_break = old_break
        self.current_continue = old_continue
        
        self.bytecode.append(Cmds.LOAD)
        self.bytecode.append(node.name)
        self.bytecode.append(Cmds.LOAD)
        self.bytecode.append(step_var)
        self.bytecode.append(Cmds.ADD)
        self.bytecode.append(Cmds.STORE)
        self.bytecode.append(node.name)
        
        self.bytecode.append(Cmds.JMP)
        self.bytecode.append(start_label)
        self.labels[end_label] = len(self.bytecode)

    def gen_BreakStmtNode(self, node):
        if self.current_break is not None:
            self.bytecode.append(Cmds.JMP)
            self.bytecode.append(self.current_break)

    def gen_ContinueStmtNode(self, node):
        if self.current_continue is not None:
            self.bytecode.append(Cmds.JMP)
            self.bytecode.append(self.current_continue)

    def gen_FunStmtNode(self, node):
        self.functions[node.name] = {
            "params": node.params.params if node.params else [],
            "block": node.block,
        }

    def gen_CallFunNode(self, node):
        if node.args and node.args.args:
            for arg in reversed(node.args.args):
                self._generate(arg)
        self.bytecode.append(Cmds.CALL)
        self.bytecode.append(node.name)
        self.bytecode.append(len(node.args.args) if node.args else 0)

    def gen_ReturnStmtNode(self, node):
        if node.expr:
            self._generate(node.expr)
        else:
            self.bytecode.append(Cmds.PUSH)
            self.bytecode.append(None)
        self.bytecode.append(Cmds.RET)

    def gen_TableNode(self, node):
        for el in node.elements:
            self._generate(el.value)
        self.bytecode.append(Cmds.MAKE_TABLE)
        self.bytecode.append(len(node.elements))

    def gen_TableElementNode(self, node):
        self._generate(node.value)

    def gen_ArgsNode(self, node):
        for arg in node.args:
            self._generate(arg)

    def gen_ArgListNode(self, node):
        for arg in node.args:
            self._generate(arg)

    def gen_CastNode(self, node):
        self._generate(node.expr)

