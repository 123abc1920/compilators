"""
    NUMBER  ->   <число>
    group   ->   "(" add ")" | NUMBER
    mult    ->   group  ( ( "*" | "/" ) group )*
    add     ->   mult   ( ( "+" | "-" ) mult  )*
    result  ->   add
"""

class MathExprSimpleParser:
    def __init__(self, expr: str):
        self.expr = expr
        self.pos = 0

    @property
    def curr(self) -> str:
        if self.pos < len(self.expr):
            return self.expr[self.pos]
        else:
            return '$'

    def NUMBER(self) -> float:
        """ NUMBER  ->   <число> """
        result = ''
        while self.curr.isdigit() or self.curr == '.':
            result += self.curr
            self.pos += 1
        result = float(result)
        return result

    def group(self) -> float:
        """ group   ->   "(" add ")" | NUMBER """
        if self.curr == '(':
            self.pos += 1
            result = self.add()
            self.pos += 1
        else:
            result = self.NUMBER()
        return result

    def mult(self) -> float:
        """ mult    ->   group  ( ( "*" | "/" ) group )* """
        result = self.group()
        while self.curr in ('*', '/'):
            op = self.curr
            self.pos += 1
            tmp = self.group()
            result = result * tmp if op == '*' else result / tmp
        return result

    def add(self) -> float:
        """ add     ->   mult   ( ( "+" | "-" ) mult  )* """
        result = self.mult()
        while self.curr in ('+', '-'):
            op = self.curr
            self.pos += 1
            tmp = self.mult()
            result = result + tmp if op == '+' else result - tmp
        return result

    def result(self) -> float:
        """ result  ->   add """
        result = self.add()
        if self.pos != len(self.expr):
            raise Exception(f'Лишний символ {self.curr} в позиции [{self.pos}]')
        return result


expr = '3+2*(5+2-2*(1+1.05))+10*(5+5)'
p = MathExprSimpleParser(expr)
res = p.result()
print(res)
