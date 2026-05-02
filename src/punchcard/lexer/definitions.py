KEYWORDS = {
    "PROGRAM": "PROGRAM",
    "FUNCTION": "FUNCTION",
    "SUBROUTINE": "SUBROUTINE",
    "RETURN": "RETURN",
    "END": "END",
    "GOTO": "GOTO",
    "CALL": "CALL",
    "DO": "DO",
    "CONTINUE": "CONTINUE",
    "IF": "IF",
    "ELSE": "ELSE",
    "ENDIF": "ENDIF",
    "THEN": "THEN",
    "PRINT": "PRINT",
    "READ": "READ",
    "STOP": "STOP",
    "DOUBLE": "DT_DOUBLE_PRECISION",
    "INTEGER": "DT_INTEGER",
    "REAL": "DT_REAL",
    "LOGICAL": "DT_LOGICAL",
    "CHARACTER": "DT_CHARACTER",
}

TOKENS = (
    # operators
    "OP_POWER",
    # logical operators
    "LOP_EQ",
    "LOP_NE",
    "LOP_LE",
    "LOP_LT",
    "LOP_GE",
    "LOP_GT",
    "LOP_AND",
    "LOP_OR",
    "LOP_NOT",
    # literal values
    "LIT_INT",
    "LIT_FLOAT",
    "LIT_DOUBLE",
    "LIT_STRING",
    "LIT_BOOLEAN",
    # identifiers
    "IDENTIFIER",
) + tuple(KEYWORDS.values())

LITERALS = "(),=+-*/"
