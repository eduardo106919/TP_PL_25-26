# Fortan 77 CFG

Fortran 77 Context Free Grammar:

```
program : program_unit_list

program_unit_list : program_unit
                  | program_unit_list program_unit

program_unit : main_program
             | function_subprogram
             | subroutine_subprogram

main_program : PROGRAM IDENTIFIER body END

function_subprogram : type_spec FUNCTION IDENTIFIER '(' param_list ')' body END

subroutine_subprogram : SUBROUTINE IDENTIFIER '(' param_list ')' body END

body : declaration_section statement_section

declaration_section : declaration_section declaration
                    |

declaration : type_spec var_list

type_spec : DT_INTEGER
          | DT_REAL
          | DT_DOUBLE_PRECISION
          | DT_LOGICAL
          | DT_CHARACTER

var_list : var_decl
         | var_list ',' var_decl

var_decl : IDENTIFIER
         | IDENTIFIER '(' dim_list ')'

dim_list : expr
         | dim_list ',' expr

statement_section : statement_section statement
                  |

statement : LIT_INT statement_body
          | statement_body

statement_body : assignment_stmt
               | goto_stmt
               | if_stmt
               | do_stmt
               | continue_stmt
               | print_stmt
               | read_stmt
               | stop_stmt
               | return_stmt
               | call_stmt

assignment_stmt : lvalue '=' expr

lvalue : IDENTIFIER
       | IDENTIFIER '(' arg_list ')'

goto_stmt : GOTO LIT_INT

if_stmt : IF '(' expr ')' THEN statement_section ENDIF
        | IF '(' expr ')' THEN statement_section ELSE statement_section ENDIF
        | IF '(' expr ')' statement_body

do_stmt : DO LIT_INT IDENTIFIER '=' expr ',' expr statement_section LIT_INT CONTINUE
        | DO LIT_INT IDENTIFIER '=' expr ',' expr ',' expr statement_section LIT_INT CONTINUE

continue_stmt : CONTINUE

print_stmt : PRINT '*' ',' output_list
           | PRINT LIT_STRING ',' output_list
           | PRINT '*'

read_stmt : READ '*' ',' input_list
          | READ '*'

stop_stmt : STOP

return_stmt : RETURN

param_list : param_list_mult
           |

param_list_mult : IDENTIFIER
                 | param_list_mult ',' IDENTIFIER

arg_list : arg_list_mult
         |

arg_list_mult : expr
              | arg_list_mult ',' expr

output_list : expr
            | output_list ',' expr

input_list : lvalue
           | input_list ',' lvalue

expr : logical_expr

logical_expr : logical_expr LOP_OR  logical_and
             | logical_and

logical_and : logical_and LOP_AND logical_not
            | logical_not

logical_not : LOP_NOT logical_not
            | comparison

comparison : arith_expr relop arith_expr
           | arith_expr

relop : LOP_EQ | LOP_NE | LOP_LE | LOP_LT | LOP_GE | LOP_GT

arith_expr : arith_expr arith_op term
           | term

arith_op : '+'
         | '-'

term : term term_op factor
     | factor

term_op : '*'
        | '/'

factor : unary OP_POWER factor
       | unary

unary : '-' unary
      | '+' unary
      | primary

primary : '(' expr ')'
        | LIT_INT | LIT_FLOAT | LIT_DOUBLE
        | LIT_STRING | LIT_BOOLEAN
        | IDENTIFIER
        | IDENTIFIER '(' arg_list ')'

```
