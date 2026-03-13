from LuaVisitor import LuaVisitor


class BreakException(Exception):
    pass


class ContinueException(Exception):
    pass


class Compilator(LuaVisitor):
    def __init__(self):
        self.call_stack = [{}]

    def visitProg(self, ctx):
        results = []
        for stmt in ctx.statement():
            res = self.visit(stmt)
            results.append(res)
        return results[-1] if results else None

    def visitParams(self, ctx):
        result = []

        names = ctx.NAME()
        for n in names:
            result.append(n.getText())

        return result

    def visitFunStmt(self, ctx):
        name = ctx.NAME().getText()
        params = []
        if ctx.params():
            params = self.visit(ctx.params())
        self.call_stack[-1][name] = {"params": params, "block": ctx.block()}
        return None

    def visitArgs(self, ctx):
        result = []

        exprs = ctx.expr()
        for e in exprs:
            result.append(self.visit(e))

        return result

    def visitReturnStmt(self, ctx):
        return self.visit(ctx.expr())

    def visitBlock(self, ctx):
        statements = ctx.statement()

        result = None
        for s in statements:
            result = self.visit(s)

        if ctx.returnStmt():
            return self.visit(ctx.returnStmt())

        return None

    def visitCallFun(self, ctx):
        name = ctx.NAME().getText()
        args = []
        if ctx.args():
            args = self.visit(ctx.args())

        func = self.call_stack[-1].get(name)
        self.call_stack.append({})

        for i in range(len(func["params"])):
            self.call_stack[-1][func["params"][i]] = args[i]

        block = func["block"]
        result = self.visit(block)

        self.call_stack.pop()
        return result

    def visitBreakStmt(self, ctx):
        raise BreakException()

    def visitContinueStmt(self, ctx):
        raise ContinueException()

    def visitTable(self, ctx):
        result = []
        for i in range(len(ctx.tableEl())):
            el = self.visit(ctx.tableEl(i))
            result.append(el)
        return result

    def visitTableEl(self, ctx):
        if not ctx.key():
            return self.visit(ctx.value())
        else:
            return {self.visit(ctx.key()): self.visit(ctx.value())}

    def visitKey(self, ctx):
        if ctx.NUMBER():
            return int(ctx.NUMBER().getText())
        if ctx.STRING():
            return ctx.STRING().getText()[1:-1]
        if ctx.NAME():
            name = ctx.NAME().getText()
            return self.call_stack[-1].get(name, 0)
        if ctx.table():
            return self.visit(ctx.table())
        if ctx.expr():
            return self.visit(ctx.expr())

    def visitValue(self, ctx):
        if ctx.atom():
            return self.visit(ctx.atom())
        if ctx.table():
            return self.visit(ctx.table())

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
        if ctx.expr():
            name = ctx.NAME().getText()
            value = self.visit(ctx.expr())
            self.call_stack[-1][name] = value
            return value
        if ctx.table():
            name = ctx.NAME().getText()
            value = self.visit(ctx.table())
            self.call_stack[-1][name] = value
            return value

    def visitForStmt(self, ctx):
        var_name = ctx.NAME().getText()
        start = int(self.visit(ctx.expr(0)))
        end = int(self.visit(ctx.expr(1)))

        result = None
        try:
            for i in range(start, end):
                self.call_stack[-1][var_name] = i
                try:
                    for stmt in ctx.statement():
                        result = self.visit(stmt)
                except BreakException:
                    break
                except ContinueException:
                    continue
        except BreakException:
            return result

        return result

    def visitIfStmt(self, ctx):
        result = None

        exprs = ctx.expr()
        statements = ctx.statement()

        for i in range(len(exprs)):
            if self.visit(exprs[i]):
                for s in statements[i].getChildren():
                    result = self.visit(s)
                return result

        if len(statements) > len(exprs):
            for stmt in statements[-1].getChildren():
                result = self.visit(stmt)

        return result

    def visitRepeatStmt(self, ctx):
        statements = ctx.statement()
        exprs = ctx.expr()
        result = None

        try:
            while True:
                try:
                    for s in statements:
                        result = self.visit(s)
                except BreakException:
                    break
                except ContinueException:
                    continue
                if self.visit(exprs):
                    break
        except BreakException:
            return result

        return result

    def visitWhileStmt(self, ctx):
        result = None

        try:
            while self.visit(ctx.expr()):
                try:
                    for stmt in ctx.statement():
                        result = self.visit(stmt)
                except BreakException:
                    break
                except ContinueException:
                    continue
        except BreakException:
            return result

        return result

    def visitExpr(self, ctx):
        if ctx.orExpr():
            return self.visit(ctx.orExpr())
        if ctx.callFun():
            return self.visit(ctx.callFun())

    def visitOrExpr(self, ctx):
        left = self.visit(ctx.andExpr(0))
        result = left

        for i in range(1, len(ctx.andExpr())):
            right = self.visit(ctx.andExpr(i))
            result = result or right

        return result

    def visitNotExpr(self, ctx):
        if ctx.notExpr():
            return not self.visit(ctx.notExpr())
        if ctx.comparison():
            return self.visit(ctx.comparison())

    def visitAndExpr(self, ctx):
        left = self.visit(ctx.notExpr(0))

        result = left
        for i in range(1, len(ctx.notExpr())):
            right = self.visit(ctx.notExpr(i))
            result = result and right

        return result

    def visitComparison(self, ctx):
        left = self.visit(ctx.addExpr(0))
        if ctx.getChildCount() == 1:
            return left
        op = ctx.getChild(1).getText()
        right = self.visit(ctx.addExpr(1))

        if op == "<":
            return left < right
        elif op == ">":
            return left > right
        elif op == "<=":
            return left <= right
        elif op == ">=":
            return left >= right
        elif op == "==":
            return left == right
        elif op == "~=":
            return left != right

    def visitAtom(self, ctx):
        if ctx.NUMBER():
            return int(ctx.NUMBER().getText())
        if ctx.STRING():
            return ctx.STRING().getText()[1:-1]
        if ctx.getChildCount() == 4 and ctx.getChild(1).getText() == "[":
            table_name = ctx.getChild(0).getText()
            table = self.call_stack[-1].get(table_name)
            index = self.visit(ctx.getChild(2)) - 1
            if index < 0:
                index = 0

            val = table[index]
            if isinstance(val, dict):
                for k in val:
                    return val[k]

            return val
        if ctx.NAME() and not ctx.expr() and len(ctx.NAME()) == 1:
            name = ctx.NAME()[0].getText()
            return self.call_stack[-1].get(name, 0)
        if ctx.expr():
            return self.visit(ctx.expr())
        if ctx.atom():
            if ctx.getChild(0).getText() == "-":
                return -self.visit(ctx.atom())
        if ctx.table():
            return self.visit(ctx.table())
        if ctx.getText() == "true":
            return True
        if ctx.getText() == "false":
            return False
        if ctx.getText() == "nil":
            return None
        if ctx.NAME(0) and ctx.NAME(1):
            table_name = ctx.NAME(0).getText()
            field_name = ctx.NAME(1).getText()
            table = self.call_stack[-1].get(table_name)
            for i in table:
                if isinstance(i, dict):
                    if field_name in i:
                        return i[field_name]
            return None
        return 0

    def visitMulExpr(self, ctx):
        result = self.visit(ctx.atom(0))
        for i in range(1, len(ctx.atom())):
            op = ctx.getChild(2 * i - 1).getText()
            if op == "*":
                result *= self.visit(ctx.atom(i))
            elif op == "/":
                result /= self.visit(ctx.atom(i))
            elif op == "%":
                result %= self.visit(ctx.atom(i))
        return result

    def visitAddExpr(self, ctx):
        result = self.visit(ctx.mulExpr(0))
        for i in range(1, len(ctx.mulExpr())):
            op = ctx.getChild(2 * i - 1).getText()
            if op == "+":
                result += self.visit(ctx.mulExpr(i))
            elif op == "-":
                result -= self.visit(ctx.mulExpr(i))
        return result
