from app_factory import WithAntlr

FILE = "tasks/input.lua"


def read_code():
    code = ""

    with open(FILE, "r", encoding="utf-8") as f:
        code = f.read()

    return code


def main():
    code = read_code()

    parser = WithAntlr(code)


if __name__ == "__main__":
    main()
