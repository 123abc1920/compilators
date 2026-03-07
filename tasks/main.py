from antlr4 import *
from LuaLexer import LuaLexer
from LuaParser import LuaParser
from LuaVisitor import LuaVisitor


class BreakException(Exception):
    pass


class ContinueException(Exception):
    pass


class Compilator(LuaVisitor):
    def __init__(self):
        self.vars = {}

    def visitProg(self, ctx):
        results = []
        for stmt in ctx.statement():
            res = self.visit(stmt)
            results.append(res)
        return results[-1] if results else None

    def visitBreakStmt(self, ctx):
        raise BreakException()

    def visitContinueStmt(self, ctx):
        raise ContinueException()

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
        return None

    def visitAssign(self, ctx):
        name = ctx.NAME().getText()
        value = self.visit(ctx.expr())
        self.vars[name] = value
        return value

    def visitForStmt(self, ctx):
        var_name = ctx.NAME().getText()
        start = int(self.visit(ctx.expr(0)))
        end = int(self.visit(ctx.expr(1)))

        result = None
        try:
            for i in range(start, end):
                self.vars[var_name] = i
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
        if ctx.getText() == "true":
            return True
        if ctx.getText() == "false":
            return False
        if ctx.getText() == "nil":
            return None
        return self.visit(ctx.orExpr())

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
        if ctx.NAME():
            name = ctx.NAME().getText()
            return self.vars.get(name, 0)
        if ctx.expr():
            return self.visit(ctx.expr())
        if ctx.atom():
            if ctx.getChild(0).getText() == "-":
                return -self.visit(ctx.atom())
        if ctx.boolAtom():
            return self.visit(ctx.boolAtom())
        if ctx.nilAtom():
            return self.visit(ctx.nilAtom())
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


code = """
    a=0
    i=0
    while i<10
        i=i+1
        if i%2==0 then
            continue
        end
        a=a+1
    end
    a
"""

lexer = LuaLexer(InputStream(code))
stream = CommonTokenStream(lexer)
parser = LuaParser(stream)
tree = parser.prog()

evaluator = Compilator()
result = evaluator.visit(tree)
print(result)

print("Дерево разбора:")
print(tree.toStringTree(recog=parser))
