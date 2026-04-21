class CodeGen:
    def __init__(self):
        self.code = []
        self.indent = 0
        self.temp_count = 0
        self.all_vars = set()
        self.string_vars = set()
        self.declared_vars = set()
        self.functions = []

    def emit(self, line):
        self.code.append("    " * self.indent + line)

    def generate(self, node):
        self.all_vars = set()
        self.string_vars = set()
        self.declared_vars = set()
        self.functions = []

        self.collect_vars(node)

        self.emit("#include <stdio.h>")
        self.emit("#include <stdlib.h>")
        self.emit("#include <string.h>")
        self.emit("")

        for func_name in self.functions:
            self.emit(f"int {func_name}(int a, int b);")
        if self.functions:
            self.emit("")

        self.emit("int main() {")
        self.indent += 1

        for var in sorted(self.all_vars):
            if var in self.string_vars:
                self.emit(f"char {var}[100];")
            else:
                self.emit(f"int {var};")
        if self.all_vars:
            self.emit("")

        self.declared_vars = self.all_vars.copy()

        self.visit(node)

        self.emit("return 0;")
        self.indent -= 1
        self.emit("}")

        self.emit("")
        self.generate_functions(node)

        return "\n".join(self.code)

    def generate_functions(self, node):
        if node is None:
            return

        if node.__class__.__name__ == "FunStmtNode":
            self.gen_FunStmtNode_body(node)

        for attr in dir(node):
            if attr.startswith("_"):
                continue
            value = getattr(node, attr)
            if isinstance(value, list):
                for item in value:
                    if hasattr(item, "__dict__"):
                        self.generate_functions(item)
            elif hasattr(value, "__dict__"):
                self.generate_functions(value)

    def collect_vars(self, node):
        if node is None:
            return

        if node.__class__.__name__ == "AssignNode":
            self.all_vars.add(node.name)
            if node.value.__class__.__name__ == "ReadStmtNode":
                self.string_vars.add(node.name)

        elif node.__class__.__name__ == "ForStmtNode":
            self.all_vars.add(node.name)

        elif node.__class__.__name__ == "FunStmtNode":
            self.functions.append(node.name)
            if node.params:
                for param in node.params.params:
                    self.all_vars.add(param)

        elif node.__class__.__name__ == "AtomNode":
            if node.type == "name":
                self.all_vars.add(node.value)

        for attr in dir(node):
            if attr.startswith("_"):
                continue
            value = getattr(node, attr)
            if isinstance(value, list):
                for item in value:
                    if hasattr(item, "__dict__"):
                        self.collect_vars(item)
            elif hasattr(value, "__dict__"):
                self.collect_vars(value)

    def visit(self, node):
        if node is None:
            return
        method_name = f"gen_{node.__class__.__name__}"
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

    def gen_ProgNode(self, node):
        for stmt in node.statements:
            if stmt.__class__.__name__ != "FunStmtNode":
                self.visit(stmt)

    def gen_AssignNode(self, node):
        value = self.expr_to_str(node.value)

        if node.value.__class__.__name__ == "ReadStmtNode":
            self.emit(f"strcpy({node.name}, {value});")
        else:
            self.emit(f"{node.name} = {value};")

    def gen_PrintStmtNode(self, node):
        if node.args:
            for arg in node.args.args:
                val = self.expr_to_str(arg)
                if val.startswith('"') or (
                    hasattr(arg, "type")
                    and arg.type == "name"
                    and arg.value in self.string_vars
                ):
                    self.emit(f'printf("%s\\n", {val});')
                else:
                    self.emit(f'printf("%d\\n", {val});')
        else:
            self.emit('printf("\\n");')

    def gen_ReadStmtNode(self, node):
        temp_var = f"read_temp_{self.temp_count}"
        self.temp_count += 1

        self.emit(f"char {temp_var}[100];")
        self.emit(f"fgets({temp_var}, 100, stdin);")
        self.emit(f'{temp_var}[strcspn({temp_var}, "\\n")] = 0;')

        return temp_var

    def gen_WhileStmtNode(self, node):
        cond = self.expr_to_str(node.condition)
        self.emit(f"while ({cond}) {{")
        self.indent += 1
        for stmt in node.statements:
            self.visit(stmt)
        self.indent -= 1
        self.emit("}")

    def gen_ForStmtNode(self, node):
        start = self.expr_to_str(node.start)
        end = self.expr_to_str(node.end)
        self.emit(f"for ({node.name} = {start}; {node.name} < {end}; {node.name}++) {{")
        self.indent += 1
        for stmt in node.statements:
            self.visit(stmt)
        self.indent -= 1
        self.emit("}")

    def gen_IfStmtNode(self, node):
        for i, cond in enumerate(node.conditions):
            cond_str = self.expr_to_str(cond)
            if i == 0:
                self.emit(f"if ({cond_str}) {{")
            else:
                self.emit(f"}} else if ({cond_str}) {{")
            self.indent += 1
            for stmt in node.blocks[i].statements:
                self.visit(stmt)
            self.indent -= 1

        if len(node.blocks) > len(node.conditions):
            self.emit("} else {")
            self.indent += 1
            for stmt in node.blocks[-1].statements:
                self.visit(stmt)
            self.indent -= 1
        self.emit("}")

    def gen_BreakStmtNode(self, node):
        self.emit("break;")

    def gen_ContinueStmtNode(self, node):
        self.emit("continue;")

    def gen_ReturnStmtNode(self, node):
        if node.expr:
            self.emit(f"return {self.expr_to_str(node.expr)};")
        else:
            self.emit("return;")

    def gen_FunStmtNode_body(self, node):
        params = []
        if node.params:
            params = node.params.params
        param_str = ", ".join([f"int {p}" for p in params])
        self.emit(f"int {node.name}({param_str}) {{")
        self.indent += 1
        if node.block:
            old_vars = self.declared_vars.copy()
            self.declared_vars = set()
            for p in params:
                self.declared_vars.add(p)
            self.visit(node.block)
            self.declared_vars = old_vars
        self.indent -= 1
        self.emit("}")

    def gen_FunStmtNode(self, node):
        pass

    def gen_CallFunNode(self, node):
        args = []
        if node.args:
            for arg in node.args.args:
                args.append(self.expr_to_str(arg))
        return f'{node.name}({", ".join(args)})'

    def expr_to_str(self, node):
        if node is None:
            return "0"

        node_name = node.__class__.__name__

        if node_name == "AtomNode":
            if node.type == "number":
                return str(node.value)
            if node.type == "string":
                return f'"{node.value}"'
            if node.type == "literal":
                if node.value == "true":
                    return "1"
                if node.value == "false":
                    return "0"
                return "0"
            if node.type == "name":
                return node.value

        elif node_name == "ReadStmtNode":
            return self.gen_ReadStmtNode(node)

        elif node_name == "AddExprNode":
            left = self.expr_to_str(node.left)
            right = self.expr_to_str(node.right)
            return f"({left} + {right})"

        elif node_name == "MulExprNode":
            left = self.expr_to_str(node.left)
            right = self.expr_to_str(node.right)
            return f"({left} {node.op} {right})"

        elif node_name == "ComparisonNode":
            left = self.expr_to_str(node.left)
            right = self.expr_to_str(node.right)
            op = node.op
            if op == "~=":
                op = "!="
            return f"({left} {op} {right})"

        elif node_name == "OrExprNode":
            left = self.expr_to_str(node.left)
            right = self.expr_to_str(node.right)
            return f"({left} || {right})"

        elif node_name == "AndExprNode":
            left = self.expr_to_str(node.left)
            right = self.expr_to_str(node.right)
            return f"({left} && {right})"

        elif node_name == "NotExprNode":
            expr = self.expr_to_str(node.expr)
            return f"(!{expr})"

        elif node_name == "CallFunNode":
            return self.gen_CallFunNode(node)

        elif node_name == "CastNode":
            expr = self.expr_to_str(node.expr)
            if node.target_type == "number":
                return f"atoi({expr})"
            return expr

        return "0"
