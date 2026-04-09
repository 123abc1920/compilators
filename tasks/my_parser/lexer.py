class Token:
    def __init__(self, type, value, line, column):
        self.type = type
        self.value = value
        self.line = line
        self.column = column


class Lexer:
    def __init__(self, code: str):
        self.code = code
        self.pos = 0
        self.line = 1
        self.column = 1

    def tokenize(self):
        tokens = []
        while self.pos < len(self.code):
            symbol = self.code[self.pos]

            if symbol in " \t\r":
                self.pos += 1
                self.column += 1
                continue

            if symbol == "\n":
                tokens.append(Token("NEWLINE", "\n", self.line, self.column))
                self.pos += 1
                self.line += 1
                self.column = 1
                continue

            if symbol == "-":
                if self.pos + 1 < len(self.code) and self.code[self.pos + 1] == "-":
                    self.pos += 2
                    while self.pos < len(self.code) and self.code[self.pos] != "\n":
                        self.pos += 1
                    continue

            if symbol.isdigit():
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

            if symbol in "\"'":
                quote = symbol
                self.pos += 1
                start = self.pos
                while self.pos < len(self.code) and self.code[self.pos] != quote:
                    self.pos += 1
                string_value = self.code[start : self.pos]
                self.pos += 1
                tokens.append(Token("STRING", string_value, self.line, self.column))
                self.column += len(string_value) + 2
                continue

            if symbol.isalpha() or symbol == "_":
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

            if symbol in "+-*/%<>":
                op = symbol
                self.pos += 1
                if self.pos < len(self.code) and self.code[self.pos] == "=":
                    op += self.code[self.pos]
                    self.pos += 1
                tokens.append(Token("OPERATOR", op, self.line, self.column))
                self.column += len(op)
                continue

            if symbol == "=":
                tokens.append(Token("PUNCT", "=", self.line, self.column))
                self.pos += 1
                self.column += 1
                continue

            if symbol == "~":
                self.pos += 1
                if self.pos < len(self.code) and self.code[self.pos] == "=":
                    tokens.append(Token("OPERATOR", "~=", self.line, self.column))
                    self.pos += 1
                    self.column += 2
                continue

            if symbol in "(){}[],.;:":
                tokens.append(Token("PUNCT", symbol, self.line, self.column))
                self.pos += 1
                self.column += 1
                continue

            self.pos += 1

        tokens.append(Token("EOF", None, self.line, self.column))
        return tokens
