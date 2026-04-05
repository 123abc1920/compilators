from antlr4.error.ErrorListener import ErrorListener


class Errors(ErrorListener):
    def __init__(self):
        super().__init__()
        self.errors = []

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        token_text = offendingSymbol.text if offendingSymbol else "конец файла"
        error_msg = f"Ошибка в строке {line}, позиция {column}:"
        error_msg += f"\n  Неожиданный токен: '{token_text}'"
        error_msg += f"\n  {msg}"
        self.errors.append(error_msg)
        print(error_msg)
