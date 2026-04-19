from lexer.lexer import Forrtran77Lexer
from errors import ErrorManager

import sys

def test_lexer(filename : str) -> None:
    with open(filename, "r") as f:
        code = f.read()

    errors = ErrorManager()
    lexer = Forrtran77Lexer(errors).build()
    lexer.input(code)

    while True:
        tok = lexer.token()
        if not tok:
            break
        print(tok)

    if errors.has_errors():
        errors.report()


def main():
    test_lexer(sys.argv[1])

if __name__ == "__main__":
    main()
