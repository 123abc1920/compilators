from app_factory import WithAntlr, WithoutAntlr

FILE = "tasks/input.lua"


def read_code():
    code = ""

    with open(FILE, "r", encoding="utf-8") as f:
        code = f.read()

    return code


def main():
    code = read_code()
    parser = WithoutAntlr()
    parser.parse(code)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        pass
