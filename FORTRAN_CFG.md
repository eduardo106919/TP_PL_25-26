# Fortan 77 CFG

Program structure:

```
program       : PROGRAM IDENTIFIER
                decl_list
                stmt_list
                END

program       : program subprogram_list
```

Funções e Sub rotinas:

```
subprogram    : type_kw FUNCTION IDENTIFIER "(" param_list ")"
                  decl_list stmt_list END

              | SUBROUTINE IDENTIFIER "(" param_list ")"
                  decl_list stmt_list END

param_list    : param_list "," IDENTIFIER | IDENTIFIER | empty
```

Declarations:

```
decl_list     : decl_list decl | empty

decl          : type_kw var_list

type_kw       : INTEGER | REAL | LOGICAL | CHARACTER | DOUBLE_PRECISION

var_list      : var_list "," var | var

var           : IDENTIFIER
              | IDENTIFIER "(" expr ")"
```

Statements:

```
stmt_list     : stmt_list stmt | empty

stmt          : label stmt_body | stmt_body

label         : INTEGER_LIT

stmt_body     : assign_stmt
              | if_stmt
              | do_stmt
              | goto_stmt
              | read_stmt
              | print_stmt
              | continue_stmt
              | return_stmt
```

Assignment:

```
assign_stmt   : lvalue "=" expr

lvalue        : IDENTIFIER
              | IDENTIFIER "(" expr ")"
```

If statements:

```
if_stmt       : IF "(" expr ")" THEN
                  stmt_list
                ENDIF

              | IF "(" expr ")" THEN
                  stmt_list
                ELSE
                  stmt_list
                ENDIF

              | IF "(" expr ")" stmt_body
```

Do loop:

```
do_stmt       : DO INTEGER_LIT IDENTIFIER "=" expr "," expr
                  stmt_list
                INTEGER_LIT CONTINUE
```

Goto:

```
goto_stmt     : GOTO INTEGER_LIT
```

I/O:

```
print_stmt    : PRINT COMMA print_list
              | PRINT STAR COMMA print_list

read_stmt     : READ COMMA lvalue_list
              | READ STAR COMMA lvalue_list

print_list    : print_list COMMA expr | expr
lvalue_list   : lvalue_list COMMA lvalue | lvalue
```

> [!Warning]
> Verificar este tipo de _syntax_.

Expressões:

```
expr          : expr OR expr2
expr2         : expr2 AND expr3
expr3         : NOT expr4
expr4         : expr4 rel_op expr5
expr5         : expr5 "+" expr6 | expr5 "-" expr6
expr6         : expr6 "*" expr7 | expr6 "/" expr7
expr7         : "-" expr8
expr8         : expr8 "**" expr9
expr9         : INTEGER_LIT | REAL_LIT | STRING_LIT | BOOLEAN
              | IDENTIFIER
              | IDENTIFIER "(" arg_list ")"
              | "(" expr ")"
```
