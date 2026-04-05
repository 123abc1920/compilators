from antlr4 import *
from gen.LuaLexer import LuaLexer
from gen.LuaParser import LuaParser
from antlr_parser.ast_lua import ASTBuilder, print_ast
from antlr_parser.lua_inter import Compilator
from antlr_parser.errors import Errors


class WithAntlr:
    def __init__(self, code):
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
                print()

                self.print_tree(tree, parser)
                self.print_ast_tree(tree)
        except Exception as e:
            print(f"{e}")

    def print_ast_tree(self, tree):
        print("AST дерево:")
        builder = ASTBuilder()
        ast = builder.visit(tree)
        print_ast(ast)
        print()

    def print_tree(self, tree, parser):
        print("Дерево разбора:")
        print(tree.toStringTree(recog=parser))
        print()
