from antlr4 import *
from LuaLexer import LuaLexer
from LuaParser import LuaParser
from LuaVisitor import LuaVisitor


class Compilator(LuaVisitor):
    def visitAtom(self, ctx):
        if ctx.NUMBER():
            return int(ctx.NUMBER().getText())
        if ctx.STRING():
            return ctx.STRING().getText()[1:-1]
        if ctx.NAME():
            return 0
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


code = "6*4/2"

lexer = LuaLexer(InputStream(code))
stream = CommonTokenStream(lexer)
parser = LuaParser(stream)
tree = parser.expr()

evaluator = Compilator()
result = evaluator.visit(tree)
print(result)

tree = parser.prog()

print("Дерево разбора:")
print(tree.toStringTree(recog=parser))
