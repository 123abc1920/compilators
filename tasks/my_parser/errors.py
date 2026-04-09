import sys


class Errors:
    def __init__(self):
        self.has_error = False

    def error(self, message, line=None, column=None):
        self.has_error = True
        if line and column:
            print(f"ОШИБКА [строка {line}, колонка {column}]: {message}")
        elif line:
            print(f"ОШИБКА [строка {line}]: {message}")
        else:
            print(f"ОШИБКА: {message}")
        sys.exit(1)

    def reset(self):
        self.has_error = False


errors = Errors()
