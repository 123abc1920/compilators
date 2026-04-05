from dataclasses import dataclass
from typing import Any


@dataclass
class Token:
    type: str
    value: Any
    line: int
    column: int


class Lexer:
    def __init__(self, code: str):
        self.code = code
        self.pos = 0
        self.line = 1
        self.column = 1

    def tokenize(self):
        tokens = []
        while self.pos < len(self.code):
            ch = self.code[self.pos]

            if ch in " \t\r":
                self.pos += 1
                self.column += 1
                continue

            if ch == "\n":
                tokens.append(Token("NEWLINE", "\n", self.line, self.column))
                self.pos += 1
                self.line += 1
                self.column = 1
                continue

            if ch == "-":
                if self.pos + 1 < len(self.code) and self.code[self.pos + 1] == "-":
                    self.pos += 2
                    while self.pos < len(self.code) and self.code[self.pos] != "\n":
                        self.pos += 1
                    continue

            if ch.isdigit():
                start = self.pos
                while self.pos < len(self.code) and (
                    self.code[self.pos].isdigit() or self.code[self.pos] == "."
                ):
                    self.pos += 1
                num_str = self.code[start : self.pos]
                if "." in num_str:
                    value = float(num_str)
                else:
                    value = int(num_str)
                tokens.append(Token("NUMBER", value, self.line, self.column))
                self.column += self.pos - start
                continue

            if ch in "\"'":
                quote = ch
                self.pos += 1
                start = self.pos
                while self.pos < len(self.code) and self.code[self.pos] != quote:
                    self.pos += 1
                string_value = self.code[start : self.pos]
                self.pos += 1
                tokens.append(Token("STRING", string_value, self.line, self.column))
                self.column += len(string_value) + 2
                continue

            if ch.isalpha() or ch == "_":
                start = self.pos
                while self.pos < len(self.code) and (
                    self.code[self.pos].isalnum() or self.code[self.pos] == "_"
                ):
                    self.pos += 1
                name = self.code[start : self.pos]

                keywords = {
                    "and",
                    "or",
                    "not",
                    "if",
                    "then",
                    "else",
                    "elseif",
                    "end",
                    "while",
                    "do",
                    "repeat",
                    "until",
                    "for",
                    "in",
                    "break",
                    "continue",
                    "return",
                    "local",
                    "nil",
                    "true",
                    "false",
                    "function",
                    "print",
                    "read",
                }

                if name in keywords:
                    tokens.append(Token("KEYWORD", name, self.line, self.column))
                else:
                    tokens.append(Token("NAME", name, self.line, self.column))
                self.column += self.pos - start
                continue

            if ch in "+-*/%<>":
                op = ch
                self.pos += 1
                if self.pos < len(self.code) and self.code[self.pos] == "=":
                    op += self.code[self.pos]
                    self.pos += 1
                tokens.append(Token("OPERATOR", op, self.line, self.column))
                self.column += len(op)
                continue

            if ch == "=":
                tokens.append(Token("PUNCT", "=", self.line, self.column))
                self.pos += 1
                self.column += 1
                continue

            if ch == "~":
                self.pos += 1
                if self.pos < len(self.code) and self.code[self.pos] == "=":
                    tokens.append(Token("OPERATOR", "~=", self.line, self.column))
                    self.pos += 1
                    self.column += 2
                continue

            if ch in "(){}[],.;:":
                tokens.append(Token("PUNCT", ch, self.line, self.column))
                self.pos += 1
                self.column += 1
                continue

            self.pos += 1

        tokens.append(Token("EOF", None, self.line, self.column))
        return tokens
