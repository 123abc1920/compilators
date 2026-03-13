from antlr4 import *
from LuaLexer import LuaLexer
from LuaParser import LuaParser
from ast_lua import ASTBuilder, print_ast
from lua_inter import Compilator
from errors import Errors


code = """
    functi func(a, b)
        return a+b
    end

    a=func(20,3)
    a
"""

lexer = LuaLexer(InputStream(code))
stream = CommonTokenStream(lexer)
parser = LuaParser(stream)

errors = Errors()
parser.removeErrorListeners()
parser.addErrorListener(errors)

try:
    tree = parser.prog()
    if not errors.errors:
        print("Ошибок нет")

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
except Exception as e:
    print(f"Критическая ошибка: {e}")
