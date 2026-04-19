import ply.lex as lex
import re

from .definitions import TOKENS, KEYWORDS, LITERALS


class Forrtran77Lexer:

    tokens = TOKENS
    literals = LITERALS
    t_ignore = " \t"

    def __init__(self, error_manager=None):
        self.lexer = None
        self.error_manager = error_manager

    def t_DT_DOUBLE_PRECISION(self, t):
        r"\bDOUBLE PRECISION\b"
        return t

    def t_OP_POWER(self, t):
        r"\*\*"
        return t

    def t_LOP_LE(self, t):
        r"\.LE\."
        return t

    def t_LOP_AND(self, t):
        r"\.AND\."
        return t

    def t_LOP_EQ(self, t):
        r"\.EQ\."
        return t

    def t_LOP_NE(self, t):
        r"\.NE\."
        return t

    def t_LOP_NOT(self, t):
        r"\.NOT\."
        return t

    def t_LOP_GT(self, t):
        r"\.GT\."
        return t

    def t_LOP_GE(self, t):
        r"\.GE\."
        return t

    def t_LOP_LT(self, t):
        r"\.LT\."
        return t

    def t_LOP_OR(self, t):
        r"\.OR\."
        return t

    def t_LIT_BOOLEAN(self, t):
        r"\.(TRUE|FALSE)\."
        t.value = t.value.upper()
        t.value = True if t.value == ".TRUE." else False
        return t

    def t_LIT_STRING(self, t):
        r"'[^']*'"
        t.value = t.value[1:-1]
        return t

    def t_LIT_DOUBLE(self, t):
        r"\b[+-]?(\d+\.\d*|\.\d+|\d+)[Dd][+-]?\d+\b"
        normalized_value = t.value.replace("D", "E").replace("d", "e")
        t.value = float(normalized_value)
        return t

    def t_LIT_FLOAT(self, t):
        r"\b[+-]?((\d+\.\d*|\.\d+)([Ee][+-]?\d+)?|\d+[Ee][+-]?\d+)\b"
        t.value = float(t.value)
        return t

    def t_LIT_INT(self, t):
        r"\b[+-]?\d+\b"
        t.value = int(t.value)
        return t

    def t_IDENTIFIER(self, t):
        # must start with a letter and can have numbers
        r"\b[a-zA-Z][a-zA-Z0-9]*\b"
        t.value = t.value.upper()

        # check for reserved words
        t.type = KEYWORDS.get(t.value, "IDENTIFIER")

        # identifiers can't have more than 6 characters
        if t.type == "IDENTIFIER" and len(t.value) > 6:
            column = self.find_column(t.lexer.lexdata, t)
            if self.error_manager:
                self.error_manager.add_error(
                    t.lineno,
                    column,
                    f"Identifier '{t.value}' exceeds 6 characters",
                    "Lexical",
                )
            t.type = "ILLEGAL"
            return None

        return t

    def t_newline(self, t):
        r"\n"
        t.lexer.lineno += 1

    @staticmethod
    def find_column(data, token):
        line_start = data.rfind("\n", 0, token.lexpos) + 1
        return (token.lexpos - line_start) + 1

    def t_error(self, t):
        # Calculate column for better UX
        column = self.find_column(t.lexer.lexdata, t)

        self.error_manager.add_error(
            t.lineno, column, f"Illegal character '{t.value[0]}'", "Lexical"
        )

        t.lexer.skip(1)

    def build(self, **kwargs):
        self.lexer = lex.lex(module=self, reflags=re.IGNORECASE, **kwargs)
        return self.lexer
