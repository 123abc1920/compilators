from antlr4 import *
from gen.LuaLexer import LuaLexer
from gen.LuaParser import LuaParser
from ast_lua import ASTBuilder, print_ast
from lua_inter import Compilator
from errors import Errors


def print_ast_tree(tree):
    print("AST дерево:")
    builder = ASTBuilder()
    ast = builder.visit(tree)
    print_ast(ast)
    print()


def print_tree(tree, parser):
    print("Дерево разбора:")
    print(tree.toStringTree(recog=parser))
    print()


def main():
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

    errors = Errors()
    parser.removeErrorListeners()
    parser.addErrorListener(errors)

    try:
        tree = parser.prog()
        if not errors.errors:
            evaluator = Compilator()
            result = evaluator.visit(tree)

            print(result)

            print_tree(tree, parser)
            print_ast_tree(tree)
    except Exception as e:
        print(f"{e}")


if __name__ == "__main__":
    main()
