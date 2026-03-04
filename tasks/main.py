from antlr4 import *
from LuaLexer import LuaLexer
from LuaParser import LuaParser
from LuaVisitor import LuaVisitor


class Compilator(LuaVisitor):
    def __init__(self):
        self.vars = {}

    def visitProg(self, ctx):
        results = []
        for stmt in ctx.statement():
            res = self.visit(stmt)
            results.append(res)
        return results[-1] if results else None

    def visitStatement(self, ctx):
        if ctx.expr():
            return self.visit(ctx.expr())
        if ctx.assign():
            return self.visit(ctx.assign())
        if ctx.forStmt():
            return self.visit(ctx.forStmt())
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

        last_result = None
        for i in range(start, end):
            self.vars[var_name] = i
            for stmt in ctx.statement():
                last_result = self.visit(stmt)

        return last_result

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
    for i=1, 10 do
        a=a+1
    end
    i
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
