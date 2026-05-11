# Palavras reservadas do Fortran 77 e o tipo de token correspondente.
# O lexer usa este dicionário para distinguir identificadores de keywords.
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

# Lista completa de tokens reconhecidos pelo lexer.
# O PLY exige que esta variável exista com este nome exato.
TOKENS = (
    # operador de potência
    "OP_POWER",
    # operadores relacionais e lógicos
    "LOP_EQ",
    "LOP_NE",
    "LOP_LE",
    "LOP_LT",
    "LOP_GE",
    "LOP_GT",
    "LOP_AND",
    "LOP_OR",
    "LOP_NOT",
    # literais
    "LIT_INT",
    "LIT_FLOAT",
    "LIT_DOUBLE",
    "LIT_STRING",
    "LIT_BOOLEAN",
    # identificadores
    "IDENTIFIER",
) + tuple(KEYWORDS.values())

# Caracteres simples tratados diretamente como tokens pelo PLY.
LITERALS = "(),=+-*/"
