from antlr4 import *
from LuaLexer import LuaLexer
from LuaParser import LuaParser
from ast_lua import ASTBuilder, print_ast
from lua_inter import Compilator


code = """
    function func(a, b)
        return a+b
    end

    a=func(20,3)
    a
"""

lexer = LuaLexer(InputStream(code))
stream = CommonTokenStream(lexer)
parser = LuaParser(stream)
tree = parser.prog()

evaluator = Compilator()
result = evaluator.visit(tree)
print(evaluator.call_stack)
print(result)

print("Дерево разбора:")
print(tree.toStringTree(recog=parser))

print("AST дерево:")
builder = ASTBuilder()
ast = builder.visit(tree)
print_ast(ast)
