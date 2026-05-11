# 📚 Оглавление

- [main.py](#mainpy)
- [app_factory.py](#app_factorypy)
- [Lexer](#lexer)
- [Parser](#parser)
- [Semantic Analyzer](#общее-понятие-семантический-анализ)
- [ASTModifier](#класс-astmodifier--модификация-дерева)
- [Compilator](#compilator)
- [CodeGen](#что-такое-codegen-генератор-кода)
- [BytecodeCreator](#что-такое-байткод-и-генератор-байткода)
- [VM](#что-такое-виртуальная-машина-vm)

### `main.py`

**Точка входа в приложение** — выполняет следующие действия:

| Функция                     | Назначение                                                                                         |
| --------------------------- | -------------------------------------------------------------------------------------------------- |
| `read_code()`               | Читает содержимое файла `tasks/input.lua` как строку с кодировкой UTF-8                            |
| `main()`                    | Инициализирует парсер `WithoutAntlr()` (можно заменить на `WithAntlr()`), вызывает метод `parse()` |
| `if __name__ == "__main__"` | Защита от импорта, перехватывает `SystemExit` для корректного завершения                           |

**`try-except SystemExit`** сделан, чтобы при вызове `sys.exit()` внутри парсера программа не выводила красный стек ошибок в консоль — только сообщение о завершении.

### `app_factory.py`

**Модуль фабрики приложений** — содержит два класса-парсера:

#### `class WithAntlr`

Парсер на основе грамматики Lua, сгенерированной ANTLR4. Есть просто для примера. Сам генерирует Parser, Lexer и тд.

#### `class WithoutAntlr`

Ручная реализация парсера без внешних зависимостей.

Класс объединяет все этапы трансформации исходного кода в исполняемую программу:

1. Лексический анализ
2. Синтаксический анализ
3. Семантический анализ
4. Модификация AST
5. Генерация C-кода и компиляция в `.exe`
6. Генерация байткода
7. Исполнение в виртуальной машине

## Lexer

**Лексер** (или токенизатор, сканер) — это первый этап компиляции или интерпретации. Он принимает на вход **исходный код как строку символов** и разбивает его на осмысленные фрагменты — **токены**.

### Класс `Token` — контейнер для токена

```python
class Token:
    def __init__(self, type, value, line, column):
        self.type = type      # "NUMBER", "KEYWORD", "NAME" и т.д.
        self.value = value    # само значение (42, "x", "if")
        self.line = line      # номер строки в исходном коде
        self.column = column  # позиция в строке
```

---

### Класс `Lexer`

```python
class Lexer:
    def __init__(self, code: str):
        self.code = code      # исходный код как строка
        self.pos = 0          # текущая позиция (индекс в строке)
        self.line = 1         # текущая строка
        self.column = 1       # текущая колонка
```

---

### Главный метод `tokenize()`

Проходит по всему коду и возвращает список токенов:

```python
def tokenize(self):
    tokens = []
    while self.pos < len(self.code):
        symbol = self.code[self.pos]

        # ... обработка символа ...

    tokens.append(Token("EOF", None, self.line, self.column))
    return tokens
```

**Логика:** на каждом шаге смотрим на текущий символ и решаем, что это за токен.

### Виды обработки символов

#### 1. Пропуск пробелов и табуляции

```python
if symbol in " \t\r":
    self.pos += 1
    self.column += 1
    continue
```

- Ничего не добавляем в токены
- Просто двигаемся дальше

#### 2. Обработка перевода строки

```python
if symbol == "\n":
    tokens.append(Token("NEWLINE", "\n", self.line, self.column))
    self.pos += 1
    self.line += 1
    self.column = 1
    continue
```

- Добавляем токен `NEWLINE`
- Увеличиваем номер строки, сбрасываем колонку

#### 3. Комментарии (-- до конца строки)

```python
if symbol == "-":
    if self.pos + 1 < len(self.code) and self.code[self.pos + 1] == "-":
        self.pos += 2
        while self.pos < len(self.code) and self.code[self.pos] != "\n":
            self.pos += 1
        continue
```

- Если видим `--`, пропускаем всё до конца строки
- Комментарии полностью игнорируются (не создаются токены)

#### 4. Числа (целые и с плавающей точкой)

```python
if symbol.isdigit():
    start = self.pos
    while self.pos < len(self.code) and (
        self.code[self.pos].isdigit() or self.code[self.pos] == "."
    ):
        self.pos += 1
    num_str = self.code[start:self.pos]
    if "." in num_str:
        value = float(num_str)
    else:
        value = int(num_str)
    tokens.append(Token("NUMBER", value, self.line, self.column))
```

- Собираем все цифры и точки подряд
- Если есть точка — `float`, иначе — `int`

#### 5. Строки в кавычках

```python
if symbol in "\"'":
    quote = symbol
    self.pos += 1
    start = self.pos
    while self.pos < len(self.code) and self.code[self.pos] != quote:
        self.pos += 1
    string_value = self.code[start:self.pos]
    self.pos += 1
    tokens.append(Token("STRING", string_value, self.line, self.column))
```

- Запоминаем тип кавычки (`'` или `"`)
- Читаем до закрывающей кавычки
- Кавычки НЕ включаются в значение токена

**Пример:** `"hello"` → `Token("STRING", "hello", ...)`

#### 6. Идентификаторы и ключевые слова

```python
if symbol.isalpha() or symbol == "_":
    start = self.pos
    while self.pos < len(self.code) and (
        self.code[self.pos].isalnum() or self.code[self.pos] == "_"
    ):
        self.pos += 1
    name = self.code[start:self.pos]

    keywords = {"and", "or", "not", "if", "then", "else", ...}

    if name in keywords:
        tokens.append(Token("KEYWORD", name, ...))
    else:
        tokens.append(Token("NAME", name, ...))
```

- Собираем буквы, цифры и подчёркивания
- Проверяем по словарю: если слово в списке ключевых слов — `KEYWORD`, иначе `NAME`

#### 7. Операторы (односимвольные и двухсимвольные)

```python
if symbol in "+-*/%<>":
    op = symbol
    self.pos += 1
    if self.pos < len(self.code) and self.code[self.pos] == "=":
        op += self.code[self.pos]
        self.pos += 1
    tokens.append(Token("OPERATOR", op, self.line, self.column))
```

- Проверяем, не идёт ли после символа знак `=`
- Если идёт — это составной оператор `>=`, `<=`, `==`, `~=` и т.д.

#### 8. Специальная обработка `~=`

```python
if symbol == "~":
    self.pos += 1
    if self.pos < len(self.code) and self.code[self.pos] == "=":
        tokens.append(Token("OPERATOR", "~=", self.line, self.column))
        self.pos += 1
```

- `~=` — это оператор "не равно" в Lua
- Обрабатываем отдельно, так как `~` не входит в основной набор операторов

#### 9. Пунктуация

```python
if symbol in "(){}[].,;:":
    tokens.append(Token("PUNCT", symbol, self.line, self.column))
    self.pos += 1
```

- Скобки, фигурные скобки, квадратные скобки, запятые, точки, точки с запятой, двоеточия

#### 10. Конец файла

```python
tokens.append(Token("EOF", None, self.line, self.column))
```

- Всегда добавляем в конце, чтобы парсер знал, когда остановиться

### Результат — список токенов:

```python
[
    Token("KEYWORD", "function", line=1, col=1),
    Token("NAME", "add", line=1, col=10),
    Token("PUNCT", "(", line=1, col=13),
    Token("NAME", "a", line=1, col=14),
    Token("PUNCT", ",", line=1, col=15),
    Token("NAME", "b", line=1, col=16),
    Token("PUNCT", ")", line=1, col=17),
    Token("NEWLINE", "\n", line=1, col=18),
    Token("KEYWORD", "return", line=2, col=5),
    Token("NAME", "a", line=2, col=12),
    Token("OPERATOR", "+", line=2, col=14),
    Token("NAME", "b", line=2, col=16),
    Token("NEWLINE", "\n", line=2, col=17),
    Token("KEYWORD", "end", line=3, col=1),
    Token("EOF", None, line=3, col=4)
]
```

## Parser

**Парсер** — это компонент компилятора или интерпретатора, который принимает на вход **поток токенов** (результат работы лексера) и строит по нему **абстрактное синтаксическое дерево (AST)**.

---

## Зачем нужен парсер

| Задача                     | Что делает парсер                                                                                                  |
| -------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| **Проверка синтаксиса**    | Определяет, соответствует ли код правилам языка (например, правильно ли закрыты скобки, есть ли `then` после `if`) |
| **Структурирование кода**  | Превращает линейный список токенов в иерархическое дерево, где видна вложенность блоков                            |
| **Подготовка к семантике** | AST удобно обходить для проверки типов, поиска переменных и генерации кода                                         |
| **Сохранение позиции**     | Запоминает для каждого узла строку и колонку — для вывода ошибок компиляции                                        |
| **Приоритет операций**     | Реализует правила старшинства (`*` раньше `+`, `and` раньше `or`)                                                  |

---

## Как работает парсер (общий принцип)

Рекурсивный спуск

- Каждому правилу грамматики соответствует свой метод
- Методы вызывают друг друга рекурсивно
- Движение по токенам — указателем `self.pos`

Каждый метод (`prog`, `statement`, `expr`, `atom`) разбирает свою конструкцию языка. Создает Nodes.

### Класс `Parser`

```python
class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens   # список токенов от лексера
        self.pos = 0           # текущая позиция в списке
```

### Основные методы

| Метод                                       | Что делает                                                                                                      |
| ------------------------------------------- | --------------------------------------------------------------------------------------------------------------- |
| `current_token()`                           | Возвращает текущий токен или `EOF` если достигнут конец                                                         |
| `read_token(expected_type, expected_value)` | Проверяет, что текущий токен нужного типа, и продвигает `pos` вперёд. Если не совпадает — бросает `SyntaxError` |

**Пример работы `read_token`:**

```python
# Токены: [KEYWORD('if'), NAME('x'), ...]
self.read_token("KEYWORD", "if")  # проходит, pos становится 1
self.read_token("NAME")            # проходит, берёт 'x'
```

---

## Грамматика языка (что умеет разбирать парсер)

### Корневой уровень — `prog()`

```python
def prog(self):
    statements = []
    while self.current_token().type != "EOF":
        stmt = self.statement()   # разбираем одно выражение
        if stmt:
            statements.append(stmt)
        while self.current_token().type == "NEWLINE":
            self.read_token("NEWLINE")  # пропускаем пустые строки
    return ProgNode(statements, ...)
```

- Читает выражения, пока не встретит конец файла (`EOF`)
- Пропускает символы новой строки
- Возвращает корневой узел программы

---

### Уровень выражений — `statement()`

Определяет, что за конструкция начинается с текущего токена:

```python
def statement(self):
    token = self.current_token()

    if token.type == "KEYWORD":
        if token.value == "print": return self.print_stmt()
        if token.value == "function": return self.fun_stmt()
        if token.value == "for": return self.for_stmt()
        if token.value == "while": return self.while_stmt()
        if token.value == "if": return self.if_stmt()
        if token.value == "break": return self.break_stmt()
        if token.value == "return": return self.return_stmt()
        # ... и так далее

    if token.type == "NAME":
        # если следующий токен "=" → присваивание, иначе выражение
        if self.tokens[self.pos + 1].value == "=":
            return self.assign()
        else:
            return self.expr()

    return self.expr()
```

- `print "hello"` или `print("hello")`
- Определения функций (`function foo(x, y) ... end`)
- Циклы: `for`, `while`, `repeat ... until`
- Условный оператор: `if-then-elseif-else-end`
- `break`, `continue`, `return`
- Присваивания (`x = 5`)
- Вызовы функций (`foo(1, 2)`)
- Таблицы (массивы): `{1, 2, 3}`

---

### Уровень арифметики и логики (приоритет операций)

Парсер реализует иерархию приоритетов через цепочку методов:

| Метод          | Приоритет     | Операции                          |
| -------------- | ------------- | --------------------------------- |
| `or_expr()`    | самый низкий  | `or`                              |
| `and_expr()`   |               | `and`                             |
| `not_expr()`   |               | `not`                             |
| `comparison()` |               | `<`, `>`, `<=`, `>=`, `==`, `~=`  |
| `add_expr()`   |               | `+`, `-`                          |
| `mul_expr()`   |               | `*`, `/`, `%`                     |
| `atom()`       | самый высокий | числа, строки, переменные, скобки |

```python
def add_expr(self):
    left = self.mul_expr()           # сначала разбираем умножение
    while current_token() in ["+", "-"]:
        op = read_token()
        right = self.mul_expr()      # правая часть — снова умножение
        left = AddExprNode(left, op, right)
    return left
```

### Самый низкий уровень — `atom()`

Разбирает неделимые элементы:

```python
def atom(self):
    if token.type == "NUMBER":    → число (42, 3.14)
    if token.type == "STRING":    → строка ("hello")
    if token.value in ["true", "false", "nil"]: → литералы
    if token.value == "{":        → таблица (массив)
    if token.type == "NAME":      → переменная
    if token.value == "(":        → выражение в скобках
    if token.value == "-":        → унарный минус
```

---

## Пример работы парсера

### Входные токены (от лексера):

```
[KEYWORD('if'), NAME('x'), OPERATOR('>'), NUMBER(5),
 KEYWORD('then'), NAME('print'), PUNCT('('), STRING('ok'), PUNCT(')'),
 KEYWORD('end'), EOF]
```

### Процесс разбора:

1. `prog()` → вызывает `statement()`
2. `statement()` видит `KEYWORD('if')` → вызывает `if_stmt()`
3. `if_stmt()`:
   - читает `if`
   - вызывает `expr()` → читает `x > 5` → возвращает `ComparisonNode`
   - читает `then`
   - вызывает `block()` → внутри читает `print("ok")`
   - читает `end`

**Результат — AST**

Вот подробное описание **семантического анализатора** и **модификатора AST** — что это такое, как они работают и зачем нужны.

## Общее понятие: Семантический анализ

**Семантический анализатор** — это компонент компилятора, который проверяет **смысловую корректность** программы после того, как парсер проверил синтаксис.

### Что проверяет семантический анализатор

| Проверка                      | Пример ошибки                                                  |
| ----------------------------- | -------------------------------------------------------------- |
| Объявление переменных         | Использование `x` до того, как написали `x = 5`                |
| Типы данных                   | Сложение строки и числа: `"hello" + 5`                         |
| Количество аргументов функции | Вызов `foo(1, 2)`, но функция определена как `function foo(x)` |
| Выход из циклов               | `break` вне цикла или `return` вне функции                     |
| Повторное объявление          | Две переменные с одинаковым именем в одной области видимости   |

### Класс `CodeObject` — хранение информации об объекте

```python
class CodeObject:
    def __init__(self, name, type_, line, col):
        self.name = name          # имя переменной/функции
        self.type = type_         # тип: "number", "string", "function" и т.д.
        self.line = line          # где объявлена
        self.col = col
        self.num_params = None    # для функций: количество параметров
```

**Назначение:** Хранит все метаданные о переменной или функции в программе.

---

### Класс `CodeObjectsTable` — таблица символов

```python
class CodeObjectsTable:
    def __init__(self):
        self.stack = [{}]        # стек областей видимости
        self.in_loop = False     # флаг: мы внутри цикла?
        self.in_function = False # флаг: мы внутри функции?
```

- Это структура данных, которая хранит информацию о всех именах в программе (переменные, функции)
- Поддерживает **вложенные области видимости** (стек областей)

#### Методы таблицы символов

| Метод                            | Что делает                                                     |
| -------------------------------- | -------------------------------------------------------------- |
| `append_stack()`                 | Создаёт новую область видимости (при входе в функцию или блок) |
| `pop_stack()`                    | Удаляет текущую область видимости (при выходе из функции)      |
| `define(name, type_, line, col)` | Добавляет новый объект в текущую область видимости             |
| `find_code_obj(name)`            | Ищет объект во всех областях (от текущей к глобальной)         |

---

### Класс `SemanticAnalizator` — основной анализатор

```python
class SemanticAnalizator:
    def __init__(self):
        self.symbols = CodeObjectsTable()  # таблица символов
        self.errors = []                   # список ошибок
```

#### Метод `analyze(node)` — входная точка

```python
def analyze(self, node):
    self.visit(node)      # обход AST
    return self.errors    # возвращает список ошибок (если пусто — ошибок нет)
```

#### Паттерн "Visitor" (Посетитель)

```python
def visit(self, node):
    # Берём имя класса узла: "ProgNode" -> "visitProgNode"
    method_name = f"visit{node.__class__.__name__}"
    method = getattr(self, method_name, self.generic_visit)
    return method(node)
```

- Для каждого типа узла вызывается свой метод
- Если метода для узла нет — вызывается `generic_visit` (обходит все атрибуты рекурсивно)

---

### Конкретные проверки семантики

#### 1. Проверка переменных при присваивании

```python
def visitAssignNode(self, node):
    self.visit(node.value)  # сначала проверяем правую часть

    sym = self.symbols.find_code_obj(node.name)
    if sym is None:
        # Переменная не существует → создаём её с типом правой части
        var_type = self.get_expr_type(node.value)
        self.symbols.define(node.name, var_type, node.line, node.col)
```

**Логика:** Если переменной нет в таблице символов — она создаётся автоматически (как в Lua).

#### 2. Проверка использования переменных

```python
def visitAtomNode(self, node):
    if node.type == "name":
        sym = self.symbols.find_code_obj(node.value)
        if sym is None:
            self.error(f"Variable '{node.value}' not defined", node.line, node.col)
```

**Логика:** Если используется переменная, а она не объявлена — ошибка.

#### 3. Проверка функций

```python
def visitFunStmtNode(self, node):
    # Регистрируем функцию в таблице символов
    self.symbols.define(node.name, "function", node.line, node.col)

    # Запоминаем количество параметров
    sym = self.symbols.find_code_obj(node.name)
    if sym:
        sym.num_params = len(node.params.params) if node.params else 0

    # Создаём новую область видимости для тела функции
    self.symbols.append_stack()
    self.symbols.in_function = True

    # Параметры функции становятся локальными переменными
    if node.params:
        for param in node.params.params:
            self.symbols.define(param, "any", node.line, node.col)

    # Анализируем тело функции
    if node.block:
        self.visit(node.block)

    # Выходим из области видимости
    self.symbols.pop_stack()
    self.symbols.in_function = False
```

#### 4. Проверка вызова функций

```python
def visitCallFunNode(self, node):
    sym = self.symbols.find_code_obj(node.name)

    # Функция не объявлена?
    if sym is None:
        self.error(f"Function '{node.name}' not defined", ...)
        return

    # Проверяем количество аргументов
    if sym.num_params is not None:
        num_args = len(node.args.args) if node.args else 0
        if num_args != sym.num_params:
            self.error(
                f"Function '{node.name}' expects {sym.num_params} argument(s), "
                f"but got {num_args}", ...
            )
```

#### 5. Проверка `break` и `continue`

```python
def visitBreakStmtNode(self, node):
    if not self.symbols.in_loop:
        self.error("'break' outside of loop", node.line, node.col)

def visitContinueStmtNode(self, node):
    if not self.symbols.in_loop:
        self.error("'continue' outside of loop", node.line, node.col)
```

**Логика:** `break` и `continue` разрешены только внутри циклов (`for`, `while`, `repeat`).

#### 6. Проверка `return`

```python
def visitReturnStmtNode(self, node):
    if not self.symbols.in_function:
        self.error("'return' outside of function", node.line, node.col)
```

---

### Метод `get_expr_type` — определение типа выражения

```python
def get_expr_type(self, node):
    node_name = node.__class__.__name__

    if node_name == "AtomNode":
        if node.type == "number":   return "number"
        if node.type == "string":   return "string"
        if node.type == "literal":
            if node.value in ("true", "false"): return "boolean"
            return "nil"
        if node.type == "name":
            sym = self.symbols.find_code_obj(node.value)
            return sym.type if sym else "unknown"

    if node_name in ("AddExprNode", "MulExprNode"):
        return "number"    # результат сложения/умножения — число

    if node_name == "ComparisonNode":
        return "boolean"   # результат сравнения — true/false

    return "unknown"
```

---

## Класс `ASTModifier` — модификация дерева

### Зачем нужен модификатор AST

Модификатор изменяет AST **до генерации кода** для:

- **Оптимизации** (например, вычисление констант на этапе компиляции)
- **Приведения типов** (автоматическое преобразование числа в строку)
- **Раскрытия синтаксического сахара**

```python
class ASTModifier:
    def __init__(self, symbol_table):
        self.symbols = symbol_table
```

#### Основной метод — обход и модификация

```python
def modify(self, node):
    return self.visit(node)

def visit(self, node):
    if node is None:
        return None

    node_name = node.__class__.__name__

    # Специальная обработка для сложения
    if node_name == "AddExprNode":
        return self.modifyAddExprNode(node)

    # Обход всех атрибутов узла
    for attr_name, attr_value in node.__dict__.items():
        if attr_name in ("line", "col"):
            continue
        if isinstance(attr_value, list):
            for i, item in enumerate(attr_value):
                if hasattr(item, "__dict__"):
                    attr_value[i] = self.visit(item)
        elif hasattr(attr_value, "__dict__"):
            setattr(node, attr_name, self.visit(attr_value))

    return node
```

#### Ключевое -- приведение типов при сложении

```python
def modifyAddExprNode(self, node):
    node.left = self.visit(node.left)
    node.right = self.visit(node.right)

    left_type = self.get_type(node.left)
    right_type = self.get_type(node.right)

    # Если оба числа — оставляем как есть
    if left_type == "number" and right_type == "number":
        return node

    # Если строка + число → преобразуем число в строку
    if left_type == "string" and right_type == "number":
        node.right = CastNode(node.right, "string", ...)

    # Если число + строка → преобразуем число в строку
    if left_type == "number" and right_type == "string":
        node.left = CastNode(node.left, "string", ...)

    return node
```

- В языке динамическая типизация (как в Lua)
- `"Hello" + 5` должно превратиться в `"Hello5"`
- Модификатор **вставляет узел `CastNode`** — явное преобразование типа

## Compilator

**`Compilator`** — это **интерпретатор**, который выполняет программу, обходя AST и вычисляя значения. Несмотря на название "Compilator", этот класс **не компилирует** код, а **интерпретирует** его напрямую.

## Зачем нужен интерпретатор (Compilator)

| Задача                   | Что делает                                  |
| ------------------------ | ------------------------------------------- |
| **Вычисление выражений** | `2 + 3 * 4` → `14`                          |
| **Управление потоком**   | Выполнение `if`, `while`, `for`, `repeat`   |
| **Вызов функций**        | Поиск функции по имени, передача аргументов |
| **Работа с переменными** | Чтение и запись значений в стек вызовов     |
| **Ввод/вывод**           | `print()` и `read()`                        |

### Паттерн "Visitor" (Посетитель)

```python
class Compilator(LuaVisitor):
    def __init__(self):
        self.call_stack = [{}]  # стек вызовов (области видимости)
```

- `LuaVisitor` — базовый класс, который определяет методы `visitИмяУзла()`
- `Compilator` наследует его и переопределяет методы для каждого типа узла
- При обходе AST автоматически вызывается нужный метод

### Стек вызовов (`call_stack`)

```python
self.call_stack = [{}]  # список словарей, каждый словарь — область видимости
```

**Как работает:**

```python
# Глобальная область
call_stack = [{"x": 10, "y": 20}]

# Вход в функцию
self.call_stack.append({})  # call_stack = [{"x":10,"y":20}, {}]

# Добавляем локальную переменную
self.call_stack[-1]["param1"] = 5  # call_stack = [{"x":10,"y":20}, {"param1":5}]

# Выход из функции
self.call_stack.pop()  # call_stack = [{"x":10,"y":20}]
```

---

## Детальный разбор методов

### 1. Программа и блоки

#### `visitProgNode` — корневой узел программы

```python
def visitProgNode(self, node):
    results = []
    for stmt in node.statements:
        res = self.visit(stmt)
        if res is not None:
            results.append(res)
    return results[-1] if results else None
```

- Обходит все выражения программы
- Сохраняет результаты (например, `return` из функции)
- Возвращает последний результат

#### `visitBlockNode` — блок кода

```python
def visitBlockNode(self, node):
    result = None
    for stmt in node.statements:
        result = self.visit(stmt)
    return result
```

- Выполняет все выражения блока последовательно
- Возвращает результат последнего выражения

---

### 2. Переменные и присваивание

#### `visitAssignNode` — присваивание

```python
def visitAssignNode(self, node):
    value = self.visit(node.value)  # вычисляем правую часть
    self.call_stack[-1][node.name] = value  # сохраняем в текущей области
    return value
```

**Пример:**

```lua
x = 5 + 3
```

1. Вычисляется `5 + 3` → `8`
2. В текущей области видимости создаётся/обновляется `x = 8`

#### `visitAtomNode` — чтение переменных и литералов

```python
def visitAtomNode(self, node):
    if node.type == "number":   return node.value    # 42 → 42
    if node.type == "string":   return node.value    # "hello" → "hello"
    if node.type == "literal":
        if node.value == "true":   return True
        if node.value == "false":  return False
        if node.value == "nil":    return None
    if node.type == "name":
        # ищем переменную в стеке вызовов
        return self.call_stack[-1].get(node.value, 0)  # если нет — 0
```

---

### 3. Арифметические и логические операции

#### Сложение и вычитание

```python
def visitAddExprNode(self, node):
    left = self.visit(node.left)
    right = self.visit(node.right)
    if node.op == "+":
        return left + right
    else:
        return left - right
```

#### Умножение, деление, остаток

```python
def visitMulExprNode(self, node):
    left = self.visit(node.left)
    right = self.visit(node.right)
    if node.op == "*":   return left * right
    elif node.op == "/": return left / right
    else:                return left % right
```

#### Сравнения

```python
def visitComparisonNode(self, node):
    left = self.visit(node.left)
    right = self.visit(node.right)
    if node.op == "<":   return left < right
    elif node.op == ">": return left > right
    # ... и так далее
```

#### Логические операции

```python
def visitOrExprNode(self, node):
    return self.visit(node.left) or self.visit(node.right)

def visitAndExprNode(self, node):
    return self.visit(node.left) and self.visit(node.right)

def visitNotExprNode(self, node):
    return not self.visit(node.expr)
```

**Важно:** Python сам реализует короткое замыкание — если `left` в `or` истинно, `right` не вычисляется.

---

### 4. Управляющие конструкции

#### Условный оператор `if-then-elseif-else`

```python
def visitIfStmtNode(self, node):
    for i, condition in enumerate(node.conditions):
        if self.visit(condition):           # проверяем условие
            for stmt in node.blocks[i].statements:
                result = self.visit(stmt)   # выполняем блок
            return result
    if len(node.blocks) > len(node.conditions):  # есть else?
        for stmt in node.blocks[-1].statements:
            result = self.visit(stmt)
        return result
    return None
```

#### Цикл `for`

```python
def visitForStmtNode(self, node):
    var_name = node.name
    start = int(self.visit(node.start))
    end = int(self.visit(node.end))
    result = None
    try:
        for i in range(start, end):
            self.call_stack[-1][var_name] = i     # переменная цикла
            try:
                for stmt in node.statements:
                    result = self.visit(stmt)
            except BreakException:      # обработка break
                break
            except ContinueException:   # обработка continue
                continue
    except BreakException:
        return result
    return result
```

#### Цикл `while`

```python
def visitWhileStmtNode(self, node):
    result = None
    try:
        while self.visit(node.condition):   # проверка условия
            try:
                for stmt in node.statements:
                    result = self.visit(stmt)
            except BreakException:
                break
            except ContinueException:
                continue
    except BreakException:
        return result
    return result
```

#### Цикл `repeat-until`

```python
def visitRepeatStmtNode(self, node):
    result = None
    try:
        while True:
            try:
                for stmt in node.statements:
                    result = self.visit(stmt)
            except BreakException:
                break
            except ContinueException:
                continue
            if self.visit(node.condition):  # условие выхода
                break
    except BreakException:
        return result
    return result
```

**Особенность `repeat-until`:** тело цикла выполняется **хотя бы один раз**, условие проверяется в конце.

---

### 5. Обработка `break` и `continue`

Используются **исключения** для нелокального выхода:

```python
class BreakException(Exception):
    pass

class ContinueException(Exception):
    pass

def visitBreakStmtNode(self, node):
    raise BreakException()

def visitContinueStmtNode(self, node):
    raise ContinueException()
```

**Зачем исключения?**  
`break` может находиться глубоко внутри вложенных `if` или других конструкций. Исключение позволяет "выпрыгнуть" из всех уровней и попасть прямо в обработчик цикла.

---

### 6. Функции

#### Определение функции

```python
def visitFunStmtNode(self, node):
    self.call_stack[-1][node.name] = {
        "params": node.params.params if node.params else [],
        "block": node.block,
    }
    return None
```

- **Не выполняет** тело функции сразу
- Сохраняет информацию о функции в текущей области видимости

#### Вызов функции

```python
def visitCallFunNode(self, node):
    name = node.name

    # Вычисляем аргументы
    args = []
    if node.args:
        args = self.visit(node.args)

    # Ищем функцию
    func = self.call_stack[-1].get(name)
    if not func:
        errors.error(f"функция '{name}' не определена")

    # Создаём новую область видимости
    self.call_stack.append({})

    # Связываем параметры с аргументами
    for i in range(len(func["params"])):
        if i < len(args):
            self.call_stack[-1][func["params"][i]] = args[i]

    # Выполняем тело функции
    block = func["block"]
    result = self.visit(block)

    # Восстанавливаем предыдущую область
    self.call_stack.pop()
    return result
```

**Пример вызова:**

```lua
function add(a, b)
    return a + b
end

result = add(5, 3)
```

1. При определении `add` сохраняется: `{"params": ["a","b"], "block": ...}`
2. При вызове `add(5,3)`:
   - Создаётся новая область видимости
   - `a = 5`, `b = 3`
   - Выполняется `return a + b` → `8`
   - Область удаляется, возвращается `8`

---

### 7. Ввод/вывод

#### `print`

```python
def visitPrintStmtNode(self, node):
    values = []
    if node.args:
        for atom_node in node.args.args:
            val = self.visit(atom_node)
            values.append(val)
    output = " ".join(str(v) for v in values)
    print(output)
    return None
```

#### `read`

```python
def visitReadStmtNode(self, node):
    value = input()  # читаем строку из консоли
    try:
        return int(value)      # пытаемся превратить в число
    except:
        try:
            return float(value)  # или в число с плавающей точкой
        except:
            return value         # оставляем строкой
```

---

### 8. Таблицы (массивы)

#### Создание таблицы

```python
def visitTableNode(self, node):
    result = []
    for el in node.elements:
        result.append(self.visit(el))
    return result
```

#### Доступ к полям (таблица.поле)

```python
if node.type == "field":
    table_name, field_name = node.value
    table = self.call_stack[-1].get(table_name, {})
    if isinstance(table, list):
        for item in table:
            if isinstance(item, dict) and field_name in item:
                return item[field_name]
    return None
```

#### Доступ по индексу (таблица[индекс])

```python
if node.type == "index":
    table_name, index_node = node.value
    table = self.call_stack[-1].get(table_name, [])
    index = self.visit(index_node) - 1  # Lua индексация с 1
    if 0 <= index < len(table):
        return table[index]
    return None
```

---

### 9. Приведение типов (узел `CastNode`)

```python
def visitCastNode(self, node):
    value = self.visit(node.expr)

    if node.target_type == 'number':
        try:
            return float(value) if '.' in str(value) else int(value)
        except (ValueError, TypeError):
            return 0
    elif node.target_type == 'string':
        return str(value)

    return value
```

Этот метод используется после того, как `ASTModifier` вставил узлы приведения типов.

---

## Что такое CodeGen (Генератор кода)

**CodeGen** — это компонент компилятора, который превращает **AST (абстрактное синтаксическое дерево)** в **исходный код на другом языке** и в exe.

---

## Зачем нужен генератор кода

| Задача                       | Что делает CodeGen                                           |
| ---------------------------- | ------------------------------------------------------------ |
| **Трансляция в другой язык** | Превращает lua в C-код, который можно скомпилировать в .exe  |
| **Управление памятью**       | Объявляет переменные нужных типов (int, char[], массивы)     |
| **Преобразование типов**     | Числа → строки и обратно (через sprintf/atoi)                |
| **Генерация функций**        | Создаёт C-функции                                            |
| **Оптимизация**              | Определяет тип переменных (число/строка/массив) до генерации |

### Основные компоненты класса

```python
class CodeGen:
    def __init__(self):
        self.code = []              # список строк C-кода
        self.indent = 0             # текущий уровень отступа
        self.temp_count = 0         # счётчик для временных переменных
        self.all_vars = set()       # все переменные
        self.string_vars = set()    # строковые переменные
        self.array_vars = set()     # массивовые переменные
        self.array_sizes = {}       # размеры массивов
        self.declared_vars = set()  # уже объявленные переменные
        self.functions = []         # список имён функций
```

### Сбор переменных (`collect_vars`)

Перед генерацией кода **проходим по всему AST** и собираем информацию о всех переменных:

```python
def collect_vars(self, node):
    if node.__class__.__name__ == "AssignNode":
        self.all_vars.add(node.name)           # переменная существует
        if node.value.__class__.__name__ == "ReadStmtNode":
            self.string_vars.add(node.name)    # read() → строка
        elif node.value.__class__.__name__ == "TableNode":
            self.array_vars.add(node.name)     # таблица → массив
            self.array_sizes[node.name] = len(node.value.elements)
```

**Что определяется на этом этапе:**

| Конструкция                         | Тип в C         |
| ----------------------------------- | --------------- |
| `x = 5`                             | `int x`         |
| `s = read()`                        | `char s[100]`   |
| `arr = {1, 2, 3}`                   | `int arr[3]`    |
| `str = "hello"`                     | `char str[100]` |
| `str = a + b` (если a или b строка) | `char str[100]` |

---

### Генерация заголовков и объявлений

```python
def generate_code(self, node):
    # Сначала собираем все переменные
    self.collect_vars(node)

    # Добавляем заголовочные файлы
    self.add_code_line("#include <stdio.h>")
    self.add_code_line("#include <stdlib.h>")
    self.add_code_line("#include <string.h>")

    # Прототипы функций (чтобы можно было вызывать до определения)
    for func_name in self.functions:
        self.add_code_line(f"int {func_name}(int a, int b);")

    # Начало main()
    self.add_code_line("int main() {")
    self.indent += 1

    # Объявляем все переменные
    for var in sorted(self.all_vars):
        if var in self.array_vars:
            size = self.array_sizes.get(var, 100)
            self.add_code_line(f"int {var}[{size}];")    # массив
        elif var in self.string_vars:
            self.add_code_line(f"char {var}[100];")      # строка
        else:
            self.add_code_line(f"int {var};")            # число

    # Обходим и генерируем код для всех выражений
    self.visit(node)

    # Завершаем main()
    self.add_code_line("return 0;")
    self.indent -= 1
    self.add_code_line("}")

    # Генерируем тела функций
    self.generate_functions(node)
```

### Основные методы генерации

#### Присваивание (`genAssignNode`)

```python
def genAssignNode(self, node):
    value = self.expr_to_str(node.value)  # преобразуем правую часть в строку C

    if node.value.__class__.__name__ == "ReadStmtNode":
        # read() → копируем строку
        self.add_code_line(f"strcpy({node.name}, {value});")

    elif node.value.__class__.__name__ == "TableNode":
        # таблица → инициализация массива
        elements = node.value.elements
        for i, elem in enumerate(elements):
            val = self.expr_to_str(elem.value)
            self.add_code_line(f"{node.name}[{i}] = {val};")

    elif node.name in self.string_vars:
        # строковая переменная → strcpy
        self.add_code_line(f"strcpy({node.name}, {value});")

    else:
        # число
        self.add_code_line(f"{node.name} = {value};")
```

---

#### Вывод (`genPrintStmtNode`)

```python
def genPrintStmtNode(self, node):
    if node.args:
        for arg in node.args.args:
            val = self.expr_to_str(arg)
            if val.startswith('"') or (arg.type == "name" and arg.value in self.string_vars):
                self.add_code_line(f'printf("%s\\n", {val});')  # строка
            else:
                self.add_code_line(f'printf("%d\\n", {val});')  # число
    else:
        self.add_code_line('printf("\\n");')
```

---

#### Ввод (`genReadStmtNode`)

```python
def genReadStmtNode(self, node):
    temp_var = f"read_temp_{self.temp_count}"
    self.temp_count += 1

    self.add_code_line(f"char {temp_var}[100];")
    self.add_code_line(f"fgets({temp_var}, 100, stdin);")
    self.add_code_line(f'{temp_var}[strcspn({temp_var}, "\\n")] = 0;')

    return temp_var
```

---

#### Управляющие конструкции

**Цикл `while`:**

```python
def genWhileStmtNode(self, node):
    cond = self.expr_to_str(node.condition)
    self.add_code_line(f"while ({cond}) {{")
    self.indent += 1
    for stmt in node.statements:
        self.visit(stmt)
    self.indent -= 1
    self.add_code_line("}")
```

**Цикл `for`:**

```python
def genForStmtNode(self, node):
    start = self.expr_to_str(node.start)
    end = self.expr_to_str(node.end)
    self.add_code_line(f"for ({node.name} = {start}; {node.name} < {end}; {node.name}++) {{")
    # ... тело ...
    self.add_code_line("}")
```

**Условный оператор `if`:**

```python
def genIfStmtNode(self, node):
    for i, cond in enumerate(node.conditions):
        cond_str = self.expr_to_str(cond)
        if i == 0:
            self.add_code_line(f"if ({cond_str}) {{")
        else:
            self.add_code_line(f"}} else if ({cond_str}) {{")
        self.indent += 1
        for stmt in node.blocks[i].statements:
            self.visit(stmt)
        self.indent -= 1

    if len(node.blocks) > len(node.conditions):
        self.add_code_line("} else {")
        # ... тело else ...
    self.add_code_line("}")
```

---

### Этап 4: Преобразование выражений (`expr_to_str`)

Это самый сложный метод — он превращает узел AST в строку C-кода.

#### Числа и строки

```python
if node.type == "number":
    return str(node.value)           # 42 → "42"
if node.type == "string":
    return f'"{node.value}"'         # hello → "\"hello\""
if node.type == "literal":
    if node.value == "true": return "1"
    if node.value == "false": return "0"
```

#### Переменные и массивы

```python
if node.type == "name":
    return node.value                # x → "x"
if node.type == "index":
    table_name, index_node = node.value
    index = self.expr_to_str(index_node)
    return f"{table_name}[{index} - 1]"  # Lua индексация с 1 → C с 0
```

#### Арифметические операции

```python
if node_name == "AddExprNode":
    left = self.expr_to_str(node.left)
    right = self.expr_to_str(node.right)

    # Если хотя бы один операнд — строка, то конкатенация
    if left.startswith('"') or right.startswith('"'):
        # ... сложная логика конкатенации через sprintf ...
        return result_var  # возвращаем имя временной переменной
    else:
        return f"({left} + {right})"  # обычное сложение
```

**Конкатенация строк (сложение строки и числа):**

```c
// Исходный lua: "x = " + 5
// Генерируется C-код:
char temp_str_0[100];
sprintf(temp_str_0, "%d", 5);
char concat_1[200];
sprintf(concat_1, "%s%s", "x = ", temp_str_0);
// результат: "x = 5"
```

#### Логические операции

```python
if node_name == "OrExprNode":
    left = self.expr_to_str(node.left)
    right = self.expr_to_str(node.right)
    return f"({left} || {right})"

if node_name == "AndExprNode":
    return f"({left} && {right})"

if node_name == "NotExprNode":
    return f"(!{expr})"
```

#### Сравнения

```python
if node_name == "ComparisonNode":
    left = self.expr_to_str(node.left)
    right = self.expr_to_str(node.right)
    op = "!=" if node.op == "~=" else node.op  # ~= → !=
    return f"({left} {op} {right})"
```

---

### Генерация функций

Функции генерируются **после** `main()`:

```python
def genFunStmtNode_body(self, node):
    params = node.params.params if node.params else []
    param_str = ", ".join([f"int {p}" for p in params])  # int a, int b

    self.add_code_line(f"int {node.name}({param_str}) {{")
    self.indent += 1

    if node.block:
        old_vars = self.declared_vars.copy()
        self.declared_vars = set()
        for p in params:
            self.declared_vars.add(p)      # параметры — локальные переменные
        self.visit(node.block)              # генерируем тело
        self.declared_vars = old_vars

    self.indent -= 1
    self.add_code_line("}")
```

#### Вызов функции

```python
def genCallFunNode(self, node):
    args = []
    if node.args:
        for arg in node.args.args:
            args.append(self.expr_to_str(arg))
    return f'{node.name}({", ".join(args)})'
```

## Что такое байткод и генератор байткода

**Байткод** — это низкоуровневое представление программы, состоящее из последовательности инструкций (опкодов), которые выполняются **виртуальной машиной (VM)**. |

### Чем отличается от CodeGen

| CodeGen (C-код)                | BytecodeCreator (байткод)     |
| ------------------------------ | ----------------------------- |
| Генерирует текст (C-код)       | Генерирует числа (инструкции) |
| Нужен GCC для компиляции       | Выполняется на VM             |
| Медленнее (запуск компилятора) | Быстрее (прямое исполнение)   |
| Нативный .exe                  | Интерпретируемый байткод      |

---

## Зачем нужен байткод

| Задача                  | Что даёт байткод                                          |
| ----------------------- | --------------------------------------------------------- |
| **Переносимость**       | Один байткод работает на любой платформе с VM             |
| **Безопасность**        | VM контролирует выполнение (нет прямого доступа к памяти) |
| **Простота реализации** | 100 инструкций проще, чем генерация C-кода                |
| **Быстрая загрузка**    | Не нужно компилировать, байткод сразу готов к выполнению  |
| **Отладка**             | Легко трассировать выполнение инструкция за инструкцией   |

---

## Система команд

### Класс `Cmds` — все инструкции байткода

```python
class Cmds:
    # Работа со стеком и переменными (1-9)
    PUSH = 1          # положить значение на стек
    PUSH_CONST = 2    # положить константу из пула
    LOAD = 4          # загрузить переменную на стек
    STORE = 5         # сохранить значение со стека в переменную

    # Арифметика (10-19)
    ADD = 10          # сложение (a + b)
    SUB = 11          # вычитание
    MUL = 12          # умножение
    DIV = 13          # деление
    MOD = 14          # остаток от деления
    UNARY_MINUS = 15  # унарный минус (-a)

    # Логика (20-29)
    OR = 20           # логическое ИЛИ
    AND = 21          # логическое И
    NOT = 22          # логическое НЕ
    LT = 23           # меньше (<)
    GT = 24           # больше (>)
    LTE = 25          # меньше или равно (<=)
    GTE = 26          # больше или равно (>=)
    EQ = 27           # равно (==)
    NEQ = 28          # не равно (~=)

    # Управление потоком (30-39)
    JMP = 30          # безусловный переход
    JMP_IF = 31       # переход, если вершина стека истинна
    JMP_IF_NOT = 32   # переход, если вершина стека ложна

    # Функции (40-59)
    CALL = 40         # вызов функции
    RET = 41          # возврат из функции

    # Ввод/вывод (60-79)
    PRINT = 60        # печать значений (сколько — в аргументе)
    READ = 61         # чтение строки

    # Работа с таблицами (70-79)
    MAKE_TABLE = 70   # создание таблицы (массива)
    TABLE_GET = 71    # получение элемента таблицы

    # Завершение
    HALT = 99         # остановка программы
```

---

## Детальный разбор BytecodeCreator

### Структура класса

```python
class BytecodeCreator:
    def __init__(self):
        self.bytecode = []      # список инструкций (числа)
        self.constants = []     # пул констант (строки, числа)
        self.constants_map = {} # для быстрого поиска констант
        self.labels = {}        # метки для переходов
        self.label_counter = 0  # счётчик меток
        self.functions = {}     # информация о функциях
        self.current_break = None    # метка для break
        self.current_continue = None # метка для continue
```

### Основной метод `compile`

```python
def compile(self, ast_node):
    self.bytecode = []
    self.constants = []
    self.constants_map = {}
    self.labels = {}
    self.label_counter = 0
    self.functions = {}

    self._generate(ast_node)        # генерируем инструкции
    self.bytecode.append(Cmds.HALT) # добавляем остановку
    self._resolve_labels()          # заменяем метки на адреса

    return self.bytecode, self.constants, self.functions
```

---

## Как работает байткод: стековая машина

VM использует **стековую архитектуру**:

```
Перед выполнением:          После PUSH 5:          После ADD:
    Стек: []                    Стек: [5]               Стек: [8]

                             После PUSH 3:
                                 Стек: [5, 3]
```

**Пример: выражение `2 + 3`**

| Инструкция | Что делает                                    | Стек     |
| ---------- | --------------------------------------------- | -------- |
| `PUSH 2`   | положить 2                                    | `[2]`    |
| `PUSH 3`   | положить 3                                    | `[2, 3]` |
| `ADD`      | взять 2 значения, сложить, положить результат | `[5]`    |

---

## Генерация инструкций для разных конструкций

### 1. Литералы и переменные (`gen_AtomNode`)

```python
def gen_AtomNode(self, node):
    if node.type == "number":
        self.bytecode.append(Cmds.PUSH)
        self.bytecode.append(node.value)     # PUSH 42

    elif node.type == "string":
        self.bytecode.append(Cmds.PUSH_CONST)
        idx = self._add_constant(node.value) # PUSH_CONST 0
        self.bytecode.append(idx)

    elif node.type == "name":
        self.bytecode.append(Cmds.LOAD)
        self.bytecode.append(node.value)     # LOAD x
```

**Пример: `x = 5`**

```python
# Генерируется:
PUSH 5      # положить 5 на стек
STORE x     # сохранить в переменную x
```

---

### 2. Арифметические операции (`gen_AddExprNode`)

```python
def gen_AddExprNode(self, node):
    self._generate(node.left)   # генерируем код для левой части
    self._generate(node.right)  # генерируем код для правой части
    self.bytecode.append(Cmds.ADD if node.op == "+" else Cmds.SUB)
```

**Пример: `x + y * 2`**

```python
# Генерируется байткод:
LOAD x      # положить x
LOAD y      # положить y
PUSH 2      # положить 2
MUL         # умножить (y * 2) → на стеке [x, результат умножения]
ADD         # сложить → на стеке [результат]
```

---

### 3. Условный оператор `if` (`gen_IfStmtNode`)

```python
def gen_IfStmtNode(self, node):
    end_labels = []

    for i, cond in enumerate(node.conditions):
        self._generate(cond)                    # вычисляем условие
        else_lbl = self._new_label()
        self.bytecode.append(Cmds.JMP_IF_NOT)   # если ложь → переход на else
        self.bytecode.append(else_lbl)

        # Тело then
        for stmt in node.blocks[i].statements:
            self._generate(stmt)

        skip_lbl = self._new_label()
        self.bytecode.append(Cmds.JMP)          # после then прыгаем в конец
        self.bytecode.append(skip_lbl)

        self.labels[else_lbl] = len(self.bytecode)  # метка else
        end_labels.append(skip_lbl)

    # else-блок (если есть)
    if len(node.blocks) > len(node.conditions):
        for stmt in node.blocks[-1].statements:
            self._generate(stmt)

    # Заполняем метки конца
    for lbl in end_labels:
        self.labels[lbl] = len(self.bytecode)
```

**Пример: `if x > 5 then print("big") end`**

Генерируется байткод:

```
LOAD x          # положить x
PUSH 5          # положить 5
GT              # сравнить (x > 5) → на стеке true/false
JMP_IF_NOT lbl_0  # если false → прыгаем на lbl_0
PUSH_CONST 0    # положить строку "big" (индекс 0 в пуле констант)
PRINT 1         # напечатать 1 значение
JMP lbl_1       # прыгаем в конец
lbl_0:          # метка (адрес подставится при resolve)
lbl_1:          # конец if
```

---

### 4. Цикл `while` (`gen_WhileStmtNode`)

```python
def gen_WhileStmtNode(self, node):
    start = self._new_label()
    self.labels[start] = len(self.bytecode)   # метка начала

    self._generate(node.condition)            # вычисляем условие
    end = self._new_label()
    self.bytecode.append(Cmds.JMP_IF_NOT)     # если ложь → выход
    self.bytecode.append(end)

    # Сохраняем старые метки для break/continue
    old_break = self.current_break
    old_continue = self.current_continue
    self.current_break = end
    self.current_continue = start

    # Тело цикла
    for stmt in node.statements:
        self._generate(stmt)

    self.current_break = old_break
    self.current_continue = old_continue

    self.bytecode.append(Cmds.JMP)            # прыгаем обратно
    self.bytecode.append(start)

    self.labels[end] = len(self.bytecode)     # метка выхода
```

**Пример: `while x < 10 do x = x + 1 end`**

```
lbl_start:      # метка начала (адрес 0)
LOAD x
PUSH 10
LT              # x < 10 → на стеке true/false
JMP_IF_NOT lbl_end  # если false → выход
LOAD x
PUSH 1
ADD
STORE x         # x = x + 1
JMP lbl_start   # прыгаем обратно
lbl_end:        # выход из цикла
```

---

### 5. Функции (`gen_FunStmtNode` и `gen_CallFunNode`)

**Определение функции:** не генерирует байткод сейчас, а сохраняет информацию

```python
def gen_FunStmtNode(self, node):
    self.functions[node.name] = {
        "params": node.params.params if node.params else [],
        "block": node.block,
    }
```

**Вызов функции:**

```python
def gen_CallFunNode(self, node):
    # Аргументы кладём на стек в обратном порядке
    if node.args and node.args.args:
        for arg in reversed(node.args.args):
            self._generate(arg)

    self.bytecode.append(Cmds.CALL)
    self.bytecode.append(node.name)
    self.bytecode.append(len(node.args.args) if node.args else 0)
```

**Пример: `sum(5, 3)`**

```
PUSH 3          # правый аргумент (обратный порядок)
PUSH 5          # левый аргумент
CALL sum 2      # вызвать sum с 2 аргументами
```

---

### 6. `break` и `continue`

Используют сохранённые метки:

```python
def gen_BreakStmtNode(self, node):
    if self.current_break is not None:
        self.bytecode.append(Cmds.JMP)
        self.bytecode.append(self.current_break)

def gen_ContinueStmtNode(self, node):
    if self.current_continue is not None:
        self.bytecode.append(Cmds.JMP)
        self.bytecode.append(self.current_continue)
```

---

### 7. Таблицы (массивы)

```python
def gen_TableNode(self, node):
    for el in node.elements:
        self._generate(el.value)      # кладём элементы на стек
    self.bytecode.append(Cmds.MAKE_TABLE)
    self.bytecode.append(len(node.elements))  # сколько элементов
```

**Пример: `{1, 2, 3}`**

```
PUSH 1
PUSH 2
PUSH 3
MAKE_TABLE 3    # создаёт массив [1, 2, 3]
```

---

### 8. Приведение типов (`gen_CastNode`)

```python
def gen_CastNode(self, node):
    self._generate(node.expr)   # просто передаём дальше
    # Преобразование типов произойдёт в VM при выполнении
```

---

## Что такое виртуальная машина (VM)

**Виртуальная машина** — это программа, которая выполняет байткод инструкцию за инструкцией, имитируя работу реального процессора.

---

## Зачем нужна виртуальная машина

| Задача                  | Что даёт VM                                            |
| ----------------------- | ------------------------------------------------------ |
| **Исполнение байткода** | Запускает программу, сгенерированную `BytecodeCreator` |
| **Управление памятью**  | Стек для временных значений, call_stack для переменных |
| **Безопасность**        | Код не может выйти за пределы VM (нет segfault)        |
| **Переносимость**       | Одна VM работает на Windows, Linux, macOS              |
| **Отладка**             | Можно добавить трассировку выполнения                  |
| **Простота**            | 30 инструкций вместо тысяч в x86                       |

---

### Класс `VM`

```python
class VM:
    def __init__(self, bytecode, constants=None, functions=None):
        self.bytecode = bytecode      # список инструкций
        self.constants = constants    # пул констант (строки)
        self.functions = functions    # таблица функций
        self.pc = 0                   # Program Counter (счётчик команд)
        self.stack = []               # стек значений
        self.call_stack = [{}]        # стек областей видимости
        self.running = True
```

### Основные компоненты

| Компонент        | Назначение                           | Пример                           |
| ---------------- | ------------------------------------ | -------------------------------- |
| **`bytecode`**   | Массив инструкций                    | `[PUSH, 5, LOAD, 'x', ADD, ...]` |
| **`pc`**         | Указатель на текущую инструкцию      | `0` → выполняем `PUSH`           |
| **`stack`**      | Стек для временных значений          | `[5, 10, 15]`                    |
| **`call_stack`** | Стек областей видимости (переменные) | `[{'x':5, 'y':10}, {'a':3}]`     |

---

## Как работает VM: цикл выполнения

```python
def _execute(self, bytecode, constants, return_to_stack=True):
    self.pc = 0
    ret_val = None

    while self.pc < len(self.bytecode):
        op = self.bytecode[self.pc]
        self.pc += 1

        if op == Cmds.PUSH:
            # ... выполнить инструкцию ...
        elif op == Cmds.ADD:
            # ... и так далее ...

    return ret_val
```

**Цикл выполнения:**

1. Прочитать опкод по адресу `pc`
2. Увеличить `pc` на 1
3. Выполнить соответствующий код
4. Повторять, пока не встретим `HALT`

### 1. Работа со стеком и переменными

#### `PUSH` — положить значение на стек

```python
elif op == Cmds.PUSH:
    self.stack.append(self.bytecode[self.pc])
    self.pc += 1
```

**Пример:**

```python
# Байткод: [PUSH, 42]
# Стек до: []
# Стек после: [42]
```

#### `PUSH_CONST` — положить константу из пула

```python
elif op == Cmds.PUSH_CONST:
    idx = self.bytecode[self.pc]
    self.pc += 1
    self.stack.append(self.constants[idx])
```

**Пример:**

```python
# constants = ["hello", "world"]
# Байткод: [PUSH_CONST, 0]
# Стек после: ["hello"]
```

#### `LOAD` — загрузить переменную на стек

```python
elif op == Cmds.LOAD:
    name = self.bytecode[self.pc]
    self.pc += 1
    self.stack.append(self.call_stack[-1].get(name, 0))
```

**Пример:**

```python
# call_stack = [{"x": 10, "y": 20}]
# Байткод: [LOAD, "x"]
# Стек после: [10] (если нет — 0)
```

#### `STORE` — сохранить значение со стека в переменную

```python
elif op == Cmds.STORE:
    name = self.bytecode[self.pc]
    self.pc += 1
    if self.stack:
        self.call_stack[-1][name] = self.stack.pop()
```

**Пример:**

```python
# Стек: [42]
# call_stack: [{}]
# Байткод: [STORE, "x"]
# Результат: call_stack = [{"x": 42}]
```

---

### 2. Арифметические операции

#### `ADD` — сложение (с поддержкой строк)

```python
elif op == Cmds.ADD:
    b = self.stack.pop()
    a = self.stack.pop()
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        self.stack.append(a + b)      # числа: 5 + 3 = 8
    else:
        self.stack.append(str(a) + str(b))  # строки: "A" + 5 = "A5"
```

**Важно:** VM поддерживает **неявное преобразование** — если один из операндов строка, результат — конкатенация.

#### `SUB`, `MUL`, `DIV`, `MOD`

```python
elif op == Cmds.SUB:
    b = self.stack.pop()
    a = self.stack.pop()
    self.stack.append(a - b)
```

**Пример для `5 - 3`:**

```
Стек до: [5, 3]
SUB: pop → 3, pop → 5, вычисляем 5 - 3 = 2
Стек после: [2]
```

---

### 3. Логические операции и сравнения

#### `OR` и `AND` (с коротким замыканием)

```python
elif op == Cmds.OR:
    b = self.stack.pop()
    a = self.stack.pop()
    self.stack.append(a or b)
```

#### `LT`, `GT`, `LTE`, `GTE`, `EQ`, `NEQ`

```python
elif op == Cmds.LT:
    b = self.stack.pop()
    a = self.stack.pop()
    self.stack.append(a < b)
```

---

### 4. Управление потоком (переходы)

#### `JMP` — безусловный переход

```python
elif op == Cmds.JMP:
    target = self.bytecode[self.pc]
    self.pc = target   # прыгаем на указанный адрес
```

#### `JMP_IF_NOT` — переход, если условие ложно

```python
elif op == Cmds.JMP_IF_NOT:
    cond = self.stack.pop()
    target = self.bytecode[self.pc]
    if not cond:
        self.pc = target    # условие ложно → прыгаем
    else:
        self.pc += 1        # условие истинно → идём дальше
```

### 5. Функции (`CALL` и `RET`)

#### `CALL` — вызов функции

```python
elif op == Cmds.CALL:
    name = self.bytecode[self.pc]
    self.pc += 1
    num_args = self.bytecode[self.pc]
    self.pc += 1

    # Забираем аргументы со стека
    args = []
    for _ in range(num_args):
        args.append(self.stack.pop())
    args.reverse()  # восстанавливаем порядок

    # Создаём новый фрейм (область видимости)
    new_frame = {}
    for i, param in enumerate(func["params"]):
        if i < len(args):
            new_frame[param] = args[i]

    self.call_stack.append(new_frame)

    # Компилируем тело функции в байткод
    bc_creator = BytecodeCreator()
    func_bytecode, func_constants, _ = bc_creator.compile(func["block"])

    # Рекурсивно выполняем байткод функции
    ret_val = self._execute(func_bytecode, func_constants, return_to_stack=False)

    # Восстанавливаем предыдущий фрейм
    self.call_stack.pop()

    # Возвращаемое значение кладём на стек (если есть)
    if ret_val is not None:
        self.stack.append(ret_val)
```

#### `RET` — возврат из функции

```python
elif op == Cmds.RET:
    if self.stack:
        ret_val = self.stack.pop()
    # Восстанавливаем сохранённое состояние
    self.bytecode = saved_bytecode
    self.constants = saved_constants
    self.pc = saved_pc
    return ret_val
```

**Пример вызова `sum(5, 3)`:**

```
# До вызова: стек = [3, 5] (аргументы в обратном порядке)
CALL sum 2
    # Создаётся новый фрейм: {'a': 5, 'b': 3}
    # Выполняется тело sum: a + b → 8
    # RET возвращает 8
# После вызова: стек = [8]
```

---

### 6. Ввод/вывод

#### `PRINT`

```python
elif op == Cmds.PRINT:
    cnt = self.bytecode[self.pc]
    self.pc += 1
    values = []
    for _ in range(cnt):
        if self.stack:
            values.append(self.stack.pop())
    print(" ".join(str(v) for v in values))
```

**Пример:**

```
# Байткод: PUSH_CONST 0, PUSH 42, PRINT 2
# Стек: ["hello", 42] → print "hello 42"
```

#### `READ`

```python
elif op == Cmds.READ:
    val = input()
    try:
        val = int(val)      # пытаемся сделать числом
    except:
        try:
            val = float(val)
        except:
            pass
    self.stack.append(val)
```

---

### 7. Таблицы (массивы)

#### `MAKE_TABLE` — создание таблицы

```python
elif op == Cmds.MAKE_TABLE:
    size = self.bytecode[self.pc]
    self.pc += 1
    table = []
    for _ in range(size):
        if self.stack:
            table.append(self.stack.pop())
    table.reverse()  # восстанавливаем порядок
    self.stack.append(table)
```

**Пример:**

```
# Байткод: PUSH 1, PUSH 2, PUSH 3, MAKE_TABLE 3
# Стек до: [1, 2, 3]
# Стек после: [[1, 2, 3]] (массив)
```

#### `TABLE_GET` — получение элемента

```python
elif op == Cmds.TABLE_GET:
    table = self.stack.pop()
    index = self.stack.pop()
    if isinstance(table, list) and isinstance(index, (int, float)):
        idx = int(index) - 1  # Lua использует индексацию с 1
        if 0 <= idx < len(table):
            self.stack.append(table[idx])
```

**Пример:**

```
# Стек: [массив = [10, 20, 30], индекс = 2]
# TABLE_GET: берём индекс 2 → элемент с позиции 1 (0-based) → 20
# Стек после: [20]
```
