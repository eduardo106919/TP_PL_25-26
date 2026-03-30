import ply.lex as lex
import sys
import re

states = (("FIXED", "exclusive"),)

tokens = (
    "LABEL",
    "PROGRAM",
    "FUNCTION",
    "SUBROUTINE",
    "RETURN",
    "END",
    "GOTO",
    "DO",
    "CONTINUE",
    "IF",
    "ELSE",
    "ENDIF",
    "THEN",
    "PRINT",
    "READ",
    "INTEGER",
    "REAL",
    "DOUBLE_PRECISION",
    "LOGICAL",
    "CHARACTER",
    "FALSE",
    "TRUE",
    "EQ",
    "NE",
    "LE",
    "LT",
    "GE",
    "GT",
    "AND",
    "OR",
    "NOT",
    "STRING",
    "IDENTIFIER",
    "INT",
    "FLOAT",
    "DOUBLE",
)

literals = "(),=+-*/"


def t_FIXED_comment(t):
    # ignore comments
    r"[Cc\*][^\n]*"


def t_FIXED_LABEL(t):
    r"[ \t]*\d{1,5}"
    t.value = int(t.value.strip())
    t.lexer.begin("INITIAL")
    return t


def t_FIXED_nolabel(t):
    r"[ \t]+"
    t.lexer.begin("INITIAL")


def t_FIXED_newline(t):
    r"\n"
    t.lexer.lineno += 1


def t_FIXED_error(t):
    t.lexer.skip(1)


t_FIXED_ignore = r""


def t_PROGRAM(t):
    r"PROGRAM\s+[a-zA-Z][a-zA-Z0-9]*"
    # get the name of the program
    t.value = t.value.split()[-1]
    return t


def t_SUBROUTINE(t):
    r"SUBROUTINE\s+[a-zA-Z][a-zA-Z0-9]*"
    # get the name of the sub routine
    t.value = t.value.split()[-1]
    return t


def t_FUNCTION(t):
    r"FUNCTION\s+[a-zA-Z][a-zA-Z0-9]*"
    # get the name of the function
    t.value = t.value.split()[-1]
    return t


def t_RETURN(t):
    r"RETURN"
    return t


def t_GOTO(t):
    r"GOTO\s+\d+"
    # get the label value
    t.value = int(t.value.split()[-1])
    return t


def t_DO(t):
    r"DO\s+\d+"
    # get the label value
    t.value = int(t.value.split()[-1])
    return t


def t_CONTINUE(t):
    r"CONTINUE"
    return t


def t_IF(t):
    r"IF"
    return t


def t_ENDIF(t):
    r"ENDIF"
    return t


def t_END(t):
    r"END"
    return t


def t_ELSE(t):
    r"ELSE"
    return t


def t_THEN(t):
    r"THEN"
    return t


def t_PRINT(t):
    r"PRINT"
    return t


def t_READ(t):
    r"READ"
    return t


def t_INTEGER(t):
    r"INTEGER"
    return t


def t_REAL(t):
    r"REAL"
    return t


def t_DOUBLE_PRECISION(t):
    r"DOUBLE\s+PRECISION"
    return t


def t_LOGICAL(t):
    r"LOGICAL"
    return t


def t_CHARACTER(t):
    r"CHARACTER"
    return t


def t_FALSE(t):
    r"\.FALSE\."
    t.value = False
    return t


def t_TRUE(t):
    r"\.TRUE\."
    t.value = True
    return t


def t_LE(t):
    r"\.LE\."
    return t


def t_AND(t):
    r"\.AND\."
    return t


def t_EQ(t):
    r"\.EQ\."
    return t


def t_NOT(t):
    r"\.NOT\."
    return t


def t_GT(t):
    r"\.GT\."
    return t


def t_GE(t):
    r"\.GE\."
    return t


def t_LT(t):
    r"\.LT\."
    return t


def t_OR(t):
    r"\.OR\."
    return t


def t_STRING(t):
    r"'[^']*'"
    t.value = t.value[1:-1]
    return t


def t_DOUBLE(t):
    r"[+-]?(\d+\.\d*|\.\d+|\d+)[Dd][+-]?\d+"
    normalized_value = t.value.replace("D", "E").replace("d", "e")
    t.value = float(normalized_value)
    return t


def t_FLOAT(t):
    r"[+-]?((\d+\.\d*|\.\d+)([Ee][+-]?\d+)?|\d+[Ee][+-]?\d+)"
    t.value = float(t.value)
    return t


def t_INT(t):
    r"[+-]?\d+"
    t.value = int(t.value)
    return t


def t_IDENTIFIER(t):
    # must start with a letter and can have numbers
    r"[a-zA-Z][a-zA-Z0-9]*"
    t.value = t.value.upper()
    return t


t_ignore = " \t"


def t_newline(t):
    r"\n"
    t.lexer.lineno += 1
    t.lexer.begin("FIXED")


def t_error(t):
    print("Invalid symbol:", t.value[0])
    t.lexer.skip(1)


def tokenize(input):
    lexer = lex.lex(reflags=re.IGNORECASE)
    lexer.begin("FIXED")
    lexer.input(input)
    return lexer


if __name__ == "__main__":
    with open(sys.argv[1]) as file:
        content = file.read()
    lexer = tokenize(content)
    for tok in lexer:
        print(tok)
