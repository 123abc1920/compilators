from gen.LuaVisitor import LuaVisitor


class ASTBuilder(LuaVisitor):
    def visitProg(self, ctx):
        statements = []
        for stmt in ctx.statement():
            node = self.visit(stmt)
            statements.append(node)

        return ("prog", statements)

    def visitParams(self, ctx):
        result = []

        names = ctx.NAME()
        for n in names:
            result.append(n.getText())

        return ("params", result)

    def visitFunStmt(self, ctx):
        name = ctx.NAME().getText()

        params_node = None
        if ctx.params():
            params_node = self.visit(ctx.params())

        body_node = self.visit(ctx.block())

        func_node = ("function", name, params_node, body_node)

        return func_node

    def visitArgs(self, ctx):
        result = []

        exprs = ctx.expr()
        for e in exprs:
            result.append(self.visit(e))

        return result

    def visitReturnStmt(self, ctx):
        if ctx.expr():
            value_node = self.visit(ctx.expr())
            return ("return", value_node)
        else:
            return ("return", None)

    def visitBlock(self, ctx):
        statements = []

        for stmt in ctx.statement():
            node = self.visit(stmt)
            if node is not None:
                statements.append(node)

        if ctx.returnStmt():
            return_node = self.visit(ctx.returnStmt())
            statements.append(return_node)

        return ("block", statements)

    def visitCallFun(self, ctx):
        name = ctx.NAME().getText()

        args_node = None
        if ctx.args():
            args_node = self.visit(ctx.args())

        return ("call", name, args_node)

    def visitBreakStmt(self, ctx):
        return ("break", None)

    def visitContinueStmt(self, ctx):
        return ("continue", None)

    def visitTable(self, ctx):
        elements = []

        for i in range(len(ctx.tableEl())):
            el_node = self.visit(ctx.tableEl(i))
            elements.append(el_node)

        return ("table", elements)

    def visitTableEl(self, ctx):
        if not ctx.key():
            value_node = self.visit(ctx.value())
            return ("array_elem", value_node)
        else:
            key_node = self.visit(ctx.key())
            value_node = self.visit(ctx.value())
            return ("field", key_node, value_node)

    def visitKey(self, ctx):
        if ctx.NUMBER():
            return ("number", int(ctx.NUMBER().getText()))

        if ctx.STRING():
            return ("string", ctx.STRING().getText()[1:-1])

        if ctx.NAME():
            name = ctx.NAME().getText()
            return ("var", name)

        if ctx.table():
            return self.visit(ctx.table())

        if ctx.expr():
            return self.visit(ctx.expr())

        return ("nil", None)

    def visitValue(self, ctx):
        if ctx.atom():
            return self.visit(ctx.atom())
        if ctx.table():
            return self.visit(ctx.table())
        return ("nil", None)

    def visitStatement(self, ctx):
        if ctx.expr():
            return self.visit(ctx.expr())
        if ctx.assign():
            return self.visit(ctx.assign())
        if ctx.forStmt():
            return self.visit(ctx.forStmt())
        if ctx.whileStmt():
            return self.visit(ctx.whileStmt())
        if ctx.repeatStmt():
            return self.visit(ctx.repeatStmt())
        if ctx.ifStmt():
            return self.visit(ctx.ifStmt())
        if ctx.breakStmt():
            return self.visit(ctx.breakStmt())
        if ctx.continueStmt():
            return self.visit(ctx.continueStmt())
        if ctx.funStmt():
            return self.visit(ctx.funStmt())
        return None

    def visitAssign(self, ctx):
        name = ctx.NAME().getText()

        if ctx.expr():
            value_node = self.visit(ctx.expr())
        elif ctx.table():
            value_node = self.visit(ctx.table())
        else:
            value_node = ("nil", None)

        return ("assign", name, value_node)

    def visitForStmt(self, ctx):
        var_name = ctx.NAME().getText()

        start_node = self.visit(ctx.expr(0))
        end_node = self.visit(ctx.expr(1))

        body_nodes = []
        for stmt in ctx.statement():
            body_nodes.append(self.visit(stmt))

        return ("for", var_name, start_node, end_node, ("block", body_nodes))

    def visitIfStmt(self, ctx):
        conditions = [self.visit(e) for e in ctx.expr()]

        bodies = []
        for stmt_ctx in ctx.statement():
            body = [self.visit(c) for c in stmt_ctx.getChildren() if self.visit(c)]
            bodies.append(("block", body))

        result = []
        for i, cond in enumerate(conditions):
            result.append(("if", cond, bodies[i]))

        if len(bodies) > len(conditions):
            result.append(("else", bodies[-1]))

        return ("if", result)

    def visitRepeatStmt(self, ctx):
        body_nodes = []
        for stmt in ctx.statement():
            node = self.visit(stmt)
            if node is not None:
                body_nodes.append(node)

        condition_node = self.visit(ctx.expr())

        return ("repeat", ("block", body_nodes), condition_node)

    def visitWhileStmt(self, ctx):
        condition_node = self.visit(ctx.expr())

        body_nodes = []
        for stmt in ctx.statement():
            node = self.visit(stmt)
            if node is not None:
                body_nodes.append(node)

        return ("while", condition_node, ("block", body_nodes))

    def visitExpr(self, ctx):
        if ctx.orExpr():
            return self.visit(ctx.orExpr())
        if ctx.callFun():
            return self.visit(ctx.callFun())
        return None

    def visitOrExpr(self, ctx):
        operands = []
        for i in range(len(ctx.andExpr())):
            operands.append(self.visit(ctx.andExpr(i)))

        if len(operands) == 1:
            return operands[0]

        result = operands[0]
        for i in range(1, len(operands)):
            result = ("or", result, operands[i])
        return result

    def visitNotExpr(self, ctx):
        if ctx.notExpr():
            operand = self.visit(ctx.notExpr())
            return ("not", operand)
        if ctx.comparison():
            return self.visit(ctx.comparison())
        return None

    def visitAndExpr(self, ctx):
        operands = []
        for i in range(len(ctx.notExpr())):
            operands.append(self.visit(ctx.notExpr(i)))

        if len(operands) == 1:
            return operands[0]

        result = operands[0]
        for i in range(1, len(operands)):
            result = ("and", result, operands[i])

        return result

    def visitComparison(self, ctx):
        left = self.visit(ctx.addExpr(0))

        if ctx.getChildCount() == 1:
            return left

        op = ctx.getChild(1).getText()

        right = self.visit(ctx.addExpr(1))

        return ("compare", op, left, right)

    def visitAtom(self, ctx):
        if ctx.NUMBER():
            return ("number", int(ctx.NUMBER().getText()))

        if ctx.STRING():
            return ("string", ctx.STRING().getText()[1:-1])

        if ctx.getChildCount() == 4 and ctx.getChild(1).getText() == "[":
            table_name = ctx.getChild(0).getText()
            index_node = self.visit(ctx.getChild(2))
            return ("index", ("var", table_name), index_node)

        if ctx.NAME() and len(ctx.NAME()) == 1:
            name = ctx.NAME()[0].getText()
            return ("var", name)

        if ctx.expr():
            return self.visit(ctx.expr())

        if ctx.atom() and ctx.getChild(0).getText() == "-":
            return ("unary", "-", self.visit(ctx.atom()))

        if ctx.table():
            return self.visit(ctx.table())

        if ctx.getText() == "true":
            return ("boolean", True)
        if ctx.getText() == "false":
            return ("boolean", False)
        if ctx.getText() == "nil":
            return ("nil", None)

        if len(ctx.NAME()) >= 2:
            table_name = ctx.NAME(0).getText()
            field_name = ctx.NAME(1).getText()
            return ("dot", ("var", table_name), field_name)

        return ("nil", None)

    def visitMulExpr(self, ctx):
        left = self.visit(ctx.atom(0))

        if len(ctx.atom()) == 1:
            return left

        result = left
        for i in range(1, len(ctx.atom())):
            op = ctx.getChild(2 * i - 1).getText()
            right = self.visit(ctx.atom(i))
            result = ("binop", op, result, right)

        return result

    def visitAddExpr(self, ctx):
        left = self.visit(ctx.mulExpr(0))

        if len(ctx.mulExpr()) == 1:
            return left

        result = left
        for i in range(1, len(ctx.mulExpr())):
            op = ctx.getChild(2 * i - 1).getText()
            right = self.visit(ctx.mulExpr(i))
            result = ("binop", op, result, right)

        return result


def print_ast(node, level=0):
    indent = "  " * level

    if not isinstance(node, tuple):
        print(f"{indent}{node}")
        return

    node_type = node[0]

    if node_type == "prog":
        print(f"{indent}prog")
        for stmt in node[1]:
            print_ast(stmt, level + 1)

    elif node_type == "function":
        print(f"{indent}function {node[1]} {node[2]}")
        print_ast(node[3], level + 1)

    elif node_type == "params":
        print(f"{indent}params {node[1]}")

    elif node_type == "block":
        print(f"{indent}block")
        for stmt in node[1]:
            print_ast(stmt, level + 1)

    elif node_type == "return":
        print(f"{indent}return")
        print_ast(node[1], level + 1)

    elif node_type == "assign":
        print(f"{indent}assign {node[1]}")
        print_ast(node[2], level + 1)

    elif node_type == "call":
        print(f"{indent}call {node[1]}")
        for arg in node[2]:
            print_ast(arg, level + 1)

    elif node_type == "binop":
        print(f"{indent}{node[1]}")
        print_ast(node[2], level + 1)
        print_ast(node[3], level + 1)

    elif node_type == "var":
        print(f"{indent}{node[1]}")

    elif node_type == "number":
        print(f"{indent}{node[1]}")

    elif node_type == "string":
        print(f'{indent}"{node[1]}"')

    elif node_type == "boolean":
        print(f"{indent}{node[1]}")

    elif node_type == "nil":
        print(f"{indent}nil")

    else:
        print(f"{indent}unknown: {node}")
