from parser_base import BaseParser

"""
    NUMBER  ->   <число>
    group   ->   "(" add ")" | NUMBER
    mult    ->   group  ( ( "*" | "/" ) group )*
    add     ->   mult   ( ( "+" | "-" ) mult  )*
    result  ->   add
"""

"""
Шаг 2 - добавление функций

    NUMBER  ->   <число>
    IDENT   ->   <идентификатор>
    group   ->   "(" expr ")" | NUMBER | IDENT "(" params ")"
    mult    ->   group  ( ( "*" | "/" ) group )*
    add     ->   mult   ( ( "+" | "-" ) mult  )*
    expr    ->   add
    params  ->   ( expr ( ", " expr )* )?
    result  ->   expr
"""

"""
Шаг 3 - примитивный язык

    NUMBER  ->   <число>
    IDENT   ->   <идентификатор>
    group   ->   "(" expr ")" | NUMBER | ident | call
    mult    ->   group  ( ( "*" | "/" ) group )*
    add     ->   mult   ( ( "+" | "-" ) mult  )*
    expr    ->   add
    params  ->   ( expr ( ", " expr )* )?
    call    ->   IDENT "(" params ")"
    stmt    ->   IDENT "=" expr | call
    stmts   ->   stmt*
    program ->   stmts
"""


class MathExprParser(BaseParser):
    def __init__(self, expr: str):
        super().__init__(expr)

    def NUMBER(self) -> float:
        """ NUMBER  ->   <число> """
        self.ws()
        result = ''
        while self.curr.isdecimal() or self.curr == '.':
            result += self.curr
            self.pos += 1
        result = float(result)
        self.ws()
        return result

    def group(self) -> float:
        """ group   ->   "("  add  ")" | NUMBER """
        if self.is_parse('('):
            self.parse('(')
            result = self.add()
            self.parse(')')
        else:
            result = self.NUMBER()
        return result

    def mult(self) -> float:
        """ mult    ->   group  ( ( "*" | "/" ) group )* """
        result = self.group()
        while self.is_parse('*', '/'):
            op = self.parse('*', '/')
            tmp = self.group()
            result = result * tmp if op == '*' else result / tmp
        return result

    def add(self) -> float:
        """ add     ->   mult   ( ( "+" | "-" ) mult  )* """
        result = self.mult()
        while self.is_parse('+', '-'):
            op = self.parse('+', '-')
            tmp = self.mult()
            result = result + tmp if op == '+' else result - tmp
        return result

    def result(self) -> float:
        """ result  ->   add """
        result = self.add()
        if self.pos < len(self.text) - 1:
            raise Exception(f'Лишний символ {self.curr} в позиции [{self.pos}]')
        return result


expr = '''
    3 + 2*  (5 +2
       -2 * ( 1 +   1.05 )  )

       + 10 * (5 + 5)
'''
p = MathExprParser(expr)
res = p.result()
print(res)
