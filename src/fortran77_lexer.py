import ply.lex as lex
import sys
import re

states = (("COMMENT", "exclusive"),)

tokens = (
    "ILLEGAL",
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
    "STOP",
    "INTEGER",
    "REAL",
    "DOUBLE_PRECISION",
    "LOGICAL",
    "CHARACTER",
    "BOOLEAN",
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


def t_COMMENT_comment(t):
    r"[Cc*][^\n]*"
    pass


def t_COMMENT_newline(t):
    r"\n"
    t.lexer.lineno += 1


def t_COMMENT_other(t):
    r"."
    t.lexer.lexpos -= 1
    t.lexer.begin("INITIAL")


def t_COMMENT_error(t):
    t.type = "ILLEGAL"
    t.value = t.value[0]
    t.lexer.skip(1)
    return t


t_COMMENT_ignore = ""


def t_PROGRAM(t):
    r"\bPROGRAM\b"
    return t


def t_SUBROUTINE(t):
    r"\bSUBROUTINE\b"
    return t


def t_FUNCTION(t):
    r"\bFUNCTION\b"
    return t


def t_RETURN(t):
    r"\bRETURN\b"
    return t


def t_GOTO(t):
    r"\bGOTO\b"
    return t


def t_DO(t):
    r"\bDO\b"
    return t


def t_CONTINUE(t):
    r"\bCONTINUE\b"
    return t


def t_IF(t):
    r"\bIF\b"
    return t


def t_ENDIF(t):
    r"\bENDIF\b"
    return t


def t_END(t):
    r"\bEND\b"
    return t


def t_ELSE(t):
    r"\bELSE\b"
    return t


def t_THEN(t):
    r"\bTHEN\b"
    return t


def t_PRINT(t):
    r"\bPRINT\b"
    return t


def t_READ(t):
    r"\bREAD\b"
    return t


def t_STOP(t):
    r"\bSTOP\b"
    return t


def t_INTEGER(t):
    r"\bINTEGER\b"
    return t


def t_REAL(t):
    r"\bREAL\b"
    return t


def t_DOUBLE_PRECISION(t):
    r"\bDOUBLE\s+PRECISION\b"
    return t


def t_LOGICAL(t):
    r"\bLOGICAL\b"
    return t


def t_CHARACTER(t):
    r"\bCHARACTER\b"
    return t


def t_BOOLEAN(t):
    r"\.(TRUE|FALSE)\."
    t.value = True if t.value == ".TRUE." else False
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


def t_NE(t):
    r"\.NE\."
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
    r"\b[+-]?(\d+\.\d*|\.\d+|\d+)[Dd][+-]?\d+\b"
    normalized_value = t.value.replace("D", "E").replace("d", "e")
    t.value = float(normalized_value)
    return t


def t_FLOAT(t):
    r"\b[+-]?((\d+\.\d*|\.\d+)([Ee][+-]?\d+)?|\d+[Ee][+-]?\d+)\b"
    t.value = float(t.value)
    return t


def t_INT(t):
    r"\b[+-]?\d+\b"
    t.value = int(t.value)
    return t


def t_IDENTIFIER(t):
    # must start with a letter and can have numbers
    r"\b[a-zA-Z][a-zA-Z0-9]{,5}\b"
    t.value = t.value.upper()
    return t


t_ignore = " \t"


def t_newline(t):
    r"\n"
    t.lexer.lineno += 1
    t.lexer.begin("COMMENT")


def t_error(t):
    t.type = "ILLEGAL"
    t.value = t.value[0]
    t.lexer.skip(1)
    return t


def tokenize(input):
    lexer = lex.lex(reflags=re.IGNORECASE)
    lexer.input(input)
    lexer.begin("COMMENT")
    return lexer


if __name__ == "__main__":
    with open(sys.argv[1]) as file:
        content = file.read()
    lexer = tokenize(content)
    for tok in lexer:
        print(tok)
