import sys


from punchcard.errors import ErrorManager
from punchcard.lexer.lexer import PunchCardLexer
from punchcard.parser.parser import PunchCardParser


def test_lexer(filename: str) -> None:
    with open(filename, "r") as f:
        code = f.read()

    errors = ErrorManager()
    lexer = PunchCardLexer(errors).build()
    lexer.input(code)

    while True:
        tok = lexer.token()
        if not tok:
            break
        print(tok)

    if errors.has_errors():
        errors.report()


def test_parser(filename: str) -> None:
    with open(filename, "r") as f:
        code = f.read()
    errors = ErrorManager()
    lexer = PunchCardLexer(errors).build()
    parser = PunchCardParser(lexer, errors)
    ast = parser.parse(code)
    if errors.has_errors():
        errors.report()
    else:
        print(ast)


def main():
    if len(sys.argv) != 2:
        print(f"Usage: python {sys.argv[0]} <filename>")
        sys.exit(1)

    filename = sys.argv[1]
    # test_lexer(filename)
    test_parser(filename)


if __name__ == "__main__":
    main()
