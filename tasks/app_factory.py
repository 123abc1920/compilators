from print_ast import print_ast_from_tuples
import subprocess
import os


class WithAntlr:
    def parse(self, code):
        from gen.LuaLexer import LuaLexer
        from gen.LuaParser import LuaParser
        from antlr_parser.lua_inter import Compilator
        from antlr_parser.errors import Errors
        from antlr4 import InputStream, CommonTokenStream

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
        from antlr_parser.ast_lua import ASTBuilder

        print("AST дерево:")
        builder = ASTBuilder()
        ast = builder.visit(tree)
        print_ast_from_tuples(ast)
        print()

    def print_tree(self, tree, parser):
        print("Дерево разбора:")
        print(tree.toStringTree(recog=parser))
        print()


from my_parser.lexer import Lexer
from my_parser.parser import Parser
from my_parser.lua_not_antlr_inter import Compilator
from my_parser.semantic import SemanticAnalizator, ASTModifier
from my_parser.ast_lua import ast_to_tuple
from my_parser.nodes import tree_to_string


class WithoutAntlr:
    def parse(self, code):
        lexer = Lexer(code)
        tokens = lexer.tokenize()

        parser = Parser(tokens)
        ast = parser.parse()

        analyzer = SemanticAnalizator()
        errors = analyzer.analyze(ast)

        if errors:
            print("Ошибки семантического анализа:")
            for err in errors:
                print(f"  {err}")
            return False

        modifier = ASTModifier(analyzer.symbols)
        modified_ast = modifier.modify(ast)

        compilator = Compilator()
        compilator.visit(modified_ast)

        self.print_tree(modified_ast)
        self.print_ast_tree(modified_ast)

        self.generate_exe(modified_ast)

        return True

    def print_ast_tree(self, ast):
        ast_tuple = ast_to_tuple(ast)
        print_ast_from_tuples(ast_tuple)
        print()

    def print_tree(self, node):
        print(tree_to_string(node))
        print()

    def generate_exe(self, modified_ast):
        from my_parser.exe_gen import CodeGen

        generator = CodeGen()
        c_code = generator.generate_code(modified_ast)

        with open("output.c", "w", encoding="utf-8") as f:
            f.write(c_code)
        print("Сгенерирован output.c")

        result = subprocess.run(
            ["gcc", "output.c", "-o", "program.exe"], capture_output=True, text=True
        )

        if result.returncode == 0:
            print("Скомпилирован program.exe")
        else:
            print("Ошибка компиляции:")
            print(result.stderr)
