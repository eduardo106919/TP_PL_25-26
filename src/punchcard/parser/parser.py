import ply.yacc as yacc

from punchcard.errors import ErrorManager
from punchcard.lexer.definitions import TOKENS
from punchcard.lexer.lexer import PunchCardLexer
from punchcard.parser.ast import *


precedence = (
    ("left", "LOP_OR"),
    ("left", "LOP_AND"),
    ("right", "LOP_NOT"),
    ("left", "LOP_EQ", "LOP_NE", "LOP_LE", "LOP_LT", "LOP_GE", "LOP_GT"),
    ("left", "+", "-"),
    ("left", "*", "/"),
    ("right", "UMINUS", "UPLUS"),
    ("right", "OP_POWER"),
)


class PunchCardParser:
    def __init__(self, lexer: PunchCardLexer, error_manager: ErrorManager = None):
        self.lexer = lexer
        self.error_manager = error_manager
        self.tokens = TOKENS
        self.parser = yacc.yacc(module=self)

    def p_program(self, p):
        """
        program : program_unit_list
        """
        p[0] = Program(p[1])

    def p_program_unit_list_single(self, p):
        """
        program_unit_list : program_unit
        """
        p[0] = [p[1]]

    def p_program_unit_list_multiple(self, p):
        """
        program_unit_list : program_unit_list program_unit
        """
        p[0] = p[1] + [p[2]]

    def p_program_unit_main(self, p):
        """
        program_unit : main_program
        """
        p[0] = p[1]

    def p_program_unit_function(self, p):
        """
        program_unit : function_subprogram
        """
        p[0] = p[1]

    def p_program_unit_subroutine(self, p):
        """
        program_unit : subroutine_subprogram
        """
        p[0] = p[1]

    def p_main_program(self, p):
        """
        main_program : PROGRAM IDENTIFIER body END
        """
        p[0] = MainProgram(p[2], p[3])

    def p_function_subprogram(self, p):
        """
        function_subprogram : type_spec FUNCTION IDENTIFIER '(' param_list ')' body END
        """
        p[0] = FunctionSubprogram(p[3], p[5], p[7], p[1])

    def p_subroutine_subprogram(self, p):
        """
        subroutine_subprogram : SUBROUTINE IDENTIFIER '(' param_list ')' body END
        """
        p[0] = SubroutineSubprogram(p[2], p[4], p[6])

    def p_body(self, p):
        """
        body : declaration_section statement_section
        """
        p[0] = Body(p[1], p[2])

    def p_declaration_section_empty(self, p):
        """
        declaration_section : empty
        """
        p[0] = []

    def p_declaration_section_list(self, p):
        """
        declaration_section : declaration_section declaration
        """
        p[0] = p[1] + [p[2]]

    def p_declaration(self, p):
        """
        declaration : type_spec var_list
        """
        p[0] = Declaration(p[1], p[2])

    def p_type_spec_integer(self, p):
        """
        type_spec : DT_INTEGER
        """
        p[0] = p[1]

    def p_type_spec_real(self, p):
        """
        type_spec : DT_REAL
        """
        p[0] = p[1]

    def p_type_spec_double(self, p):
        """
        type_spec : DT_DOUBLE_PRECISION
        """
        p[0] = p[1]

    def p_type_spec_logical(self, p):
        """
        type_spec : DT_LOGICAL
        """
        p[0] = p[1]

    def p_type_spec_character(self, p):
        """
        type_spec : DT_CHARACTER
        """
        p[0] = p[1]

    def p_var_list_single(self, p):
        """
        var_list : var_decl
        """
        p[0] = [p[1]]

    def p_var_list_multiple(self, p):
        """
        var_list : var_list ',' var_decl
        """
        p[0] = p[1] + [p[3]]

    def p_var_decl_scalar(self, p):
        """
        var_decl : IDENTIFIER
        """
        p[0] = p[1]

    def p_var_decl_array(self, p):
        """
        var_decl : IDENTIFIER '(' dim_list ')'
        """
        p[0] = VarDecl(p[1], p[3])

    def p_dim_list_single(self, p):
        """
        dim_list : expr
        """
        p[0] = [p[1]]

    def p_dim_list_multiple(self, p):
        """
        dim_list : dim_list ',' expr
        """
        p[0] = p[1] + [p[3]]

    def p_statement_section_empty(self, p):
        """
        statement_section : empty
        """
        p[0] = []

    def p_statement_section_list(self, p):
        """
        statement_section : statement_section statement
        """
        p[0] = p[1] + [p[2]]

    def p_statement_labeled(self, p):
        """
        statement : LIT_INT statement_body
        """
        p[0] = LabeledStatement(p[1], p[2])

    def p_statement_unlabeled(self, p):
        """
        statement : statement_body
        """
        p[0] = p[1]

    def p_statement_body_assignment(self, p):
        """
        statement_body : assignment_stmt
        """
        p[0] = p[1]

    def p_statement_body_goto(self, p):
        """
        statement_body : goto_stmt
        """
        p[0] = p[1]

    def p_statement_body_if(self, p):
        """
        statement_body : if_stmt
        """
        p[0] = p[1]

    def p_statement_body_do(self, p):
        """
        statement_body : do_stmt
        """
        p[0] = p[1]

    def p_statement_body_continue(self, p):
        """
        statement_body : continue_stmt
        """
        p[0] = p[1]

    def p_statement_body_print(self, p):
        """
        statement_body : print_stmt
        """
        p[0] = p[1]

    def p_statement_body_read(self, p):
        """
        statement_body : read_stmt
        """
        p[0] = p[1]

    def p_statement_body_stop(self, p):
        """
        statement_body : stop_stmt
        """
        p[0] = p[1]

    def p_statement_body_return(self, p):
        """
        statement_body : return_stmt
        """
        p[0] = p[1]

    # TODO: investigar isto
    def p_statement_body_call(self, p):
        """
        statement_body : call_stmt
        """
        p[0] = p[1]

    # TODO: investigar isto
    def p_call_stmt(self, p):
        """
        call_stmt : CALL IDENTIFIER '(' arg_list ')'
        """
        # p[0] = CallStmt(p[2], p[4])

    def p_assignment_stmt(self, p):
        """
        assignment_stmt : lvalue '=' expr
        """
        p[0] = AssignmentStmt(p[1], p[3])

    def p_lvalue_scalar(self, p):
        """
        lvalue : IDENTIFIER
        """
        p[0] = p[1]

    def p_lvalue_array(self, p):
        """
        lvalue : IDENTIFIER '(' arg_list ')'
        """
        p[0] = ArrayAccess(p[1], p[3])

    def p_goto_stmt(self, p):
        """
        goto_stmt : GOTO LIT_INT
        """
        p[0] = GotoStmt(p[2])

    def p_if_stmt_block(self, p):
        """
        if_stmt : IF '(' expr ')' THEN statement_section ENDIF
        """
        p[0] = IfStmt(p[3], p[6], None)

    def p_if_stmt_block_else(self, p):
        """
        if_stmt : IF '(' expr ')' THEN statement_section ELSE statement_section ENDIF
        """
        p[0] = IfStmt(p[3], p[6], p[8])

    def p_if_stmt_inline(self, p):
        """
        if_stmt : IF '(' expr ')' statement_body
        """
        p[0] = IfStmt(p[3], [p[5]], None)

    def p_do_stmt(self, p):
        """
        do_stmt : DO LIT_INT IDENTIFIER '=' expr ',' expr statement_section LIT_INT CONTINUE
        """
        p[0] = DoStmt(p[2], p[3], p[5], p[7], p[8], p[9])

    def p_do_stmt_step(self, p):
        """
        do_stmt : DO LIT_INT IDENTIFIER '=' expr ',' expr ',' expr statement_section LIT_INT CONTINUE
        """
        p[0] = DoStmt(p[2], p[3], p[5], p[7], p[9], p[10])

    def p_continue_stmt(self, p):
        """
        continue_stmt : CONTINUE
        """
        p[0] = ContinueStmt()

    def p_print_stmt_star_list(self, p):
        """
        print_stmt : PRINT '*' ',' output_list
        """
        p[0] = PrintStmt("*", p[4])

    def p_print_stmt_fmt_list(self, p):
        """
        print_stmt : PRINT LIT_STRING ',' output_list
        """
        p[0] = PrintStmt(p[2], p[4])

    def p_print_stmt_star_only(self, p):
        """
        print_stmt : PRINT '*'
        """
        p[0] = PrintStmt("*", [])

    def p_read_stmt_star_list(self, p):
        """
        read_stmt : READ '*' ',' input_list
        """
        p[0] = ReadStmt("*", p[4])

    def p_read_stmt_star_only(self, p):
        """
        read_stmt : READ '*'
        """
        p[0] = ReadStmt("*", [])

    def p_stop_stmt(self, p):
        """
        stop_stmt : STOP
        """
        p[0] = StopStmt()

    def p_return_stmt(self, p):
        """
        return_stmt : RETURN
        """
        p[0] = ReturnStmt()

    def p_param_list_empty(self, p):
        """
        param_list : empty
        """
        p[0] = []

    def p_param_list_single(self, p):
        """
        param_list : IDENTIFIER
        """
        p[0] = [p[1]]

    def p_param_list_multiple(self, p):
        """
        param_list : param_list ',' IDENTIFIER
        """
        p[0] = p[1] + [p[3]]

    def p_arg_list_empty(self, p):
        """
        arg_list : empty
        """
        p[0] = []

    def p_arg_list_single(self, p):
        """
        arg_list : expr
        """
        p[0] = [p[1]]

    def p_arg_list_multiple(self, p):
        """
        arg_list : arg_list ',' expr
        """
        p[0] = p[1] + [p[3]]

    def p_output_list_single(self, p):
        """
        output_list : expr
        """
        p[0] = [p[1]]

    def p_output_list_multiple(self, p):
        """
        output_list : output_list ',' expr
        """
        p[0] = p[1] + [p[3]]

    def p_input_list_single(self, p):
        """
        input_list : lvalue
        """
        p[0] = [p[1]]

    def p_input_list_multiple(self, p):
        """
        input_list : input_list ',' lvalue
        """
        p[0] = p[1] + [p[3]]

    def p_expr(self, p):
        """
        expr : logical_expr
        """
        p[0] = p[1]

    def p_logical_expr_or(self, p):
        """
        logical_expr : logical_expr LOP_OR logical_and
        """
        p[0] = BinaryOp(p[2], p[1], p[3])

    def p_logical_expr_passthrough(self, p):
        """
        logical_expr : logical_and
        """
        p[0] = p[1]

    def p_logical_and_and(self, p):
        """
        logical_and : logical_and LOP_AND logical_not
        """
        p[0] = BinaryOp(p[2], p[1], p[3])

    def p_logical_and_passthrough(self, p):
        """
        logical_and : logical_not
        """
        p[0] = p[1]

    def p_logical_not_not(self, p):
        """
        logical_not : LOP_NOT logical_not
        """
        p[0] = UnaryOp(p[1], p[2])

    def p_logical_not_passthrough(self, p):
        """
        logical_not : comparison
        """
        p[0] = p[1]

    def p_comparison_eq(self, p):
        """
        comparison : arith_expr LOP_EQ arith_expr
        """
        p[0] = BinaryOp(p[2], p[1], p[3])

    def p_comparison_ne(self, p):
        """
        comparison : arith_expr LOP_NE arith_expr
        """
        p[0] = BinaryOp(p[2], p[1], p[3])

    def p_comparison_le(self, p):
        """
        comparison : arith_expr LOP_LE arith_expr
        """
        p[0] = BinaryOp(p[2], p[1], p[3])

    def p_comparison_lt(self, p):
        """
        comparison : arith_expr LOP_LT arith_expr
        """
        p[0] = BinaryOp(p[2], p[1], p[3])

    def p_comparison_ge(self, p):
        """
        comparison : arith_expr LOP_GE arith_expr
        """
        p[0] = BinaryOp(p[2], p[1], p[3])

    def p_comparison_gt(self, p):
        """
        comparison : arith_expr LOP_GT arith_expr
        """
        p[0] = BinaryOp(p[2], p[1], p[3])

    def p_comparison_passthrough(self, p):
        """
        comparison : arith_expr
        """
        p[0] = p[1]

    def p_arith_expr_add(self, p):
        """
        arith_expr : arith_expr '+' term
        """
        p[0] = BinaryOp(p[2], p[1], p[3])

    def p_arith_expr_sub(self, p):
        """
        arith_expr : arith_expr '-' term
        """
        p[0] = BinaryOp(p[2], p[1], p[3])

    def p_arith_expr_passthrough(self, p):
        """
        arith_expr : term
        """
        p[0] = p[1]

    def p_term_mul(self, p):
        """
        term : term '*' factor
        """
        p[0] = BinaryOp(p[2], p[1], p[3])

    def p_term_div(self, p):
        """
        term : term '/' factor
        """
        p[0] = BinaryOp(p[2], p[1], p[3])

    def p_term_passthrough(self, p):
        """
        term : factor
        """
        p[0] = p[1]

    def p_factor_power(self, p):
        """
        factor : unary OP_POWER factor
        """
        p[0] = BinaryOp(p[2], p[1], p[3])

    def p_factor_passthrough(self, p):
        """
        factor : unary
        """
        p[0] = p[1]

    def p_unary_passthrough(self, p):
        """
        unary : primary
        """
        p[0] = p[1]

    def p_primary_paren(self, p):
        """
        primary : '(' expr ')'
        """
        p[0] = p[2]

    def p_primary_int(self, p):
        """
        primary : LIT_INT
        """
        p[0] = Literal("int", p[1])

    def p_primary_float(self, p):
        """
        primary : LIT_FLOAT
        """
        p[0] = Literal("float", p[1])

    def p_primary_double(self, p):
        """
        primary : LIT_DOUBLE
        """
        p[0] = Literal("double", p[1])

    def p_primary_string(self, p):
        """
        primary : LIT_STRING
        """
        p[0] = Literal("string", p[1])

    def p_primary_boolean(self, p):
        """
        primary : LIT_BOOLEAN
        """
        p[0] = Literal("boolean", p[1])

    def p_primary_identifier(self, p):
        """
        primary : IDENTIFIER
        """
        p[0] = Identifier(p[1])

    def p_primary_call_or_array(self, p):
        """
        primary : IDENTIFIER '(' arg_list ')'
        """
        # NOTE: ambiguity will be resolved in semantic phase
        p[0] = ArrayAccess(p[1], p[3])

    def p_empty(self, p):
        """
        empty :
        """
        p[0] = None

    def p_error(self, p):
        if p:
            print(f"Syntax error at token '{p.value}' (type={p.type}, line={p.lineno})")
        else:
            print("Syntax error: unexpected end of input")

    def parse(self, code: str):
        return self.parser.parse(code, lexer=self.lexer)
