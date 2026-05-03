from __future__ import annotations
from platform import node
from typing import Optional

from punchcard.parser.ast import (
    ASTNode,
    Program,
    MainProgram,
    FunctionSubprogram,
    SubroutineSubprogram,
    Body,
    Declaration,
    VarDecl,
    LabeledStatement,
    AssignmentStmt,
    GotoStmt,
    IfStmt,
    DoStmt,
    ContinueStmt,
    PrintStmt,
    ReadStmt,
    StopStmt,
    ReturnStmt,
    CallStmt,
    BinaryOp,
    UnaryOp,
    Identifier,
    ArrayAccess,
    FunctionCall,
    Literal,
)

from punchcard.semantic.symbol_table import (
    SymbolTable,
    Symbol,
    SymbolKind,
    FortranType,
    SymbolError,
    Scope,
)

from punchcard.errors import ErrorManager

# ---------------------------------------------------------------------------
# Tabela de compatibilidade de tipos para operações binárias
#
# Em Fortran 77 a hierarquia numérica é: INTEGER < REAL < DOUBLE PRECISION.
# Quando dois operandos têm tipos diferentes, o resultado é promovido ao
# tipo mais "alto" (type coercion implícita). Operações lógicas só aceitam
# LOGICAL. Operações relacionais produzem sempre LOGICAL.
# ---------------------------------------------------------------------------

_NUMERIC = {FortranType.INTEGER, FortranType.REAL, FortranType.DOUBLE}

_NUMERIC_PROMOTION = {
    (FortranType.INTEGER, FortranType.INTEGER): FortranType.INTEGER,
    (FortranType.INTEGER, FortranType.REAL): FortranType.REAL,
    (FortranType.INTEGER, FortranType.DOUBLE): FortranType.DOUBLE,
    (FortranType.REAL, FortranType.INTEGER): FortranType.REAL,
    (FortranType.REAL, FortranType.REAL): FortranType.REAL,
    (FortranType.REAL, FortranType.DOUBLE): FortranType.DOUBLE,
    (FortranType.DOUBLE, FortranType.INTEGER): FortranType.DOUBLE,
    (FortranType.DOUBLE, FortranType.REAL): FortranType.DOUBLE,
    (FortranType.DOUBLE, FortranType.DOUBLE): FortranType.DOUBLE,
}

_RELATIONAL_OPS = {".EQ.", ".NE.", ".LT.", ".LE.", ".GT.", ".GE."}
_LOGICAL_OPS = {".AND.", ".OR."}
_ARITH_OPS = {"+", "-", "*", "/", "**"}


def _result_type(
    op: str, left: FortranType, right: FortranType
) -> Optional[FortranType]:
    """
    Devolve o tipo resultante de (left op right), ou None se a combinação
    for inválida. Usado pela verificação de tipos em BinaryOp.
    """
    if op in _RELATIONAL_OPS:
        # ambos os operandos têm de ser numéricos ou ambos LOGICAL (para .EQ./.NE.)
        if left in _NUMERIC and right in _NUMERIC:
            return FortranType.LOGICAL
        if op in {".EQ.", ".NE."} and left == right == FortranType.LOGICAL:
            return FortranType.LOGICAL
        return None
    if op in _LOGICAL_OPS:
        if left == right == FortranType.LOGICAL:
            return FortranType.LOGICAL
        return None
    if op in _ARITH_OPS:
        return _NUMERIC_PROMOTION.get((left, right))
    return None


class SemanticAnalyser:
    """
    Realiza a análise semântica do programa Fortran 77 percorrendo a AST
    com o padrão Visitor.

    Responsabilidades:
    - Construir a symbol table (declaração de variáveis, funções, subrotinas)
    - Verificar uso de variáveis não declaradas
    - Verificar tipos em expressões e atribuições
    - Validar labels (GOTO para label existente; DO label == CONTINUE label)
    - Resolver a ambiguidade ArrayAccess vs FunctionCall
    - Reportar todos os erros ao ErrorManager com emit_immediately=True
    """

    def __init__(self, error_manager: ErrorManager):
        self.st = SymbolTable()
        self.em = error_manager
        # tipo inferido da última expressão visitada — usado para verificação
        # de tipos em atribuições e chamadas
        self._expr_type: Optional[FortranType] = None

    def analyse(self, tree: ASTNode) -> None:
        """Ponto de entrada: recebe a raiz da AST e arranca a travessia."""
        tree.accept(self)

    def _error(self, message: str, line: int = None, col: int = None) -> None:
        self.em.add_error(line, col, message, "Semantic Error", emit_immediately=True)

    def _warning(self, message: str, line: int = None, col: int = None) -> None:
        self.em.add_warning(
            line, col, message, "Semantic Warning", emit_immediately=True
        )

    def _safe(self, fn, *args, **kwargs):
        """
        Executa fn(*args, **kwargs) absorvendo SymbolError e reportando-a
        ao ErrorManager. Devolve o resultado ou None em caso de erro.
        Permite que a análise continue após um erro sem propagar a excepção.
        """
        try:
            return fn(*args, **kwargs)
        except SymbolError as e:
            self._error(str(e))
            return None

    def _visit_list(self, nodes: list) -> None:
        for node in nodes:
            if isinstance(node, ASTNode):
                node.accept(self)

    def _expr(self, node: ASTNode) -> Optional[FortranType]:
        """
        Visita um nó de expressão e devolve o seu tipo inferido.
        Guarda também em self._expr_type para conveniência.
        """
        node.accept(self)
        return self._expr_type

    def generic_visit(self, node: ASTNode) -> None:
        """Fallback: visita todos os filhos sem verificações adicionais."""
        for val in node.__dict__.values():
            if isinstance(val, ASTNode):
                val.accept(self)
            elif isinstance(val, list):
                self._visit_list(val)

    def visit_Program(self, node: Program) -> None:
        # Primeiro passo: regista globalmente todos os program units para que
        # chamadas entre unidades funcionem independentemente da ordem no ficheiro.
        for unit in node.units:
            if isinstance(unit, FunctionSubprogram):
                self._safe(
                    self.st.declare_global,
                    Symbol(
                        name=unit.name,
                        kind=SymbolKind.FUNCTION,
                        type=FortranType.from_token(unit.return_type),
                        params=unit.params,
                    ),
                )
            elif isinstance(unit, SubroutineSubprogram):
                self._safe(
                    self.st.declare_global,
                    Symbol(
                        name=unit.name,
                        kind=SymbolKind.SUBROUTINE,
                        type=FortranType.SUBROUTINE,
                        params=unit.params,
                    ),
                )

        # Segundo passo: analisa cada unidade no seu próprio scope.
        for unit in node.units:
            unit.accept(self)

    def visit_MainProgram(self, node: MainProgram) -> None:
        self.st.enter_scope(node.name, "program")
        self._process_body(node.body)
        self.st.exit_scope()

    def visit_FunctionSubprogram(self, node: FunctionSubprogram) -> None:
        self.st.enter_scope(node.name, "function")

        # Parâmetros formais entram no scope local com tipo UNKNOWN —
        # as Declaration dentro da função atribuirão o tipo correcto.
        for param in node.params:
            self._safe(
                self.st.declare,
                Symbol(
                    name=param,
                    kind=SymbolKind.PARAMETER,
                    type=FortranType.UNKNOWN,
                ),
            )

        # O nome da função é válido como lvalue dentro da própria função
        # (é assim que F77 devolve o valor de retorno: CONVRT = VAL).
        self._safe(
            self.st.declare,
            Symbol(
                name=node.name,
                kind=SymbolKind.VARIABLE,
                type=FortranType.from_token(node.return_type),
            ),
        )

        self._process_body(node.body)
        self.st.exit_scope()

    def visit_SubroutineSubprogram(self, node: SubroutineSubprogram) -> None:
        self.st.enter_scope(node.name, "subroutine")

        for param in node.params:
            self._safe(
                self.st.declare,
                Symbol(
                    name=param,
                    kind=SymbolKind.PARAMETER,
                    type=FortranType.UNKNOWN,
                ),
            )

        self._process_body(node.body)
        self.st.exit_scope()

    def _process_body(self, body: Body) -> None:
        """
        Em Fortran 77 todas as declarações precedem os statements.
        Processamos as declarações primeiro para que qualquer statement
        possa referenciar qualquer variável declarada no mesmo scope.
        """
        for decl in body.declarations:
            decl.accept(self)
        for stmt in body.statements:
            stmt.accept(self)

    def visit_Declaration(self, node: Declaration) -> None:
        ftype = FortranType.from_token(node.type_spec)
        for var in node.variables:  # cada var é sempre VarDecl
            existing = self.st.current_scope.lookup(var.name)
            if existing and existing.kind == SymbolKind.PARAMETER:
                # parâmetro formal já declarado — apenas actualiza o tipo
                existing.type = ftype
                if var.dimensions:
                    existing.kind = SymbolKind.ARRAY
                    existing.dimensions = var.dimensions
            else:
                kind = SymbolKind.ARRAY if var.dimensions else SymbolKind.VARIABLE
                self._safe(
                    self.st.declare,
                    Symbol(
                        name=var.name,
                        kind=kind,
                        type=ftype,
                        dimensions=var.dimensions,
                    ),
                )

    def visit_LabeledStatement(self, node: LabeledStatement) -> None:
        self._safe(self.st.declare_label, node.label)
        node.statement.accept(self)

    def visit_AssignmentStmt(self, node: AssignmentStmt) -> None:
        # Determina o tipo do lado esquerdo
        ltype = self._resolve_lvalue_type(node.lvalue)
        # Determina o tipo do lado direito
        rtype = self._expr(node.value)

        if ltype and rtype:
            self._check_assignment_compat(ltype, rtype)

    def _resolve_lvalue_type(self, lvalue) -> Optional[FortranType]:
        """
        Resolve o tipo do lvalue de uma atribuição.
        lvalue é uma string (escalar) ou um ArrayAccess.
        """
        if isinstance(lvalue, str):
            sym = self._safe(self.st.lookup_or_raise, lvalue)
            return sym.type if sym else None
        if isinstance(lvalue, ArrayAccess):
            sym = self._safe(self.st.lookup_or_raise, lvalue.name)
            if sym and sym.kind != SymbolKind.ARRAY:
                self._error(f"'{lvalue.name}' não é um array")
                return None
            self._visit_list(lvalue.indices)
            return sym.type if sym else None
        return None

    def _check_assignment_compat(self, ltype: FortranType, rtype: FortranType) -> None:
        """Verifica compatibilidade de tipos numa atribuição."""
        # numérico ← numérico: sempre permitido (coerção implícita em F77)
        if ltype in _NUMERIC and rtype in _NUMERIC:
            if ltype != rtype:
                self._warning(
                    f"Atribuição com coerção implícita: " f"{rtype.name} → {ltype.name}"
                )
            return
        # lógico ← lógico
        if ltype == FortranType.LOGICAL and rtype == FortranType.LOGICAL:
            return
        # character ← character
        if ltype == FortranType.CHARACTER and rtype == FortranType.CHARACTER:
            return
        self._error(
            f"Tipos incompatíveis na atribuição: " f"{ltype.name} ← {rtype.name}"
        )

    def visit_GotoStmt(self, node: GotoStmt) -> None:
        self._safe(self.st.check_label, node.label)

    def visit_IfStmt(self, node: IfStmt) -> None:
        ctype = self._expr(node.condition)
        if ctype and ctype != FortranType.LOGICAL:
            self._warning(f"Condição do IF tem tipo {ctype.name}; esperado LOGICAL")
        self._visit_list(node.then_body)
        if node.else_body:
            self._visit_list(node.else_body)

    def visit_DoStmt(self, node: DoStmt) -> None:
        # Variável de controlo
        sym = self._safe(self.st.lookup_or_raise, node.var)
        if sym and sym.type not in _NUMERIC:
            self._error(
                f"Variável de controlo '{node.var}' do DO tem tipo "
                f"{sym.type.name}; esperado numérico"
            )

        # Expressões de controlo
        self._expr(node.start)
        self._expr(node.stop)
        if node.step is not None:
            self._expr(node.step)

        # Coerência do label: DO label == CONTINUE label
        if node.label != node.go_label:
            self._error(
                f"Label do DO ({node.label}) não coincide com o label "
                f"do CONTINUE ({node.go_label})"
            )

        # Corpo do loop
        self._visit_list(node.body)

    def visit_ContinueStmt(self, node: ContinueStmt) -> None:
        pass  # nada a verificar — o label é tratado em visit_LabeledStatement

    def visit_PrintStmt(self, node: PrintStmt) -> None:
        for item in node.items:
            item.accept(self)

    def visit_ReadStmt(self, node: ReadStmt) -> None:
        for item in node.items:
            if isinstance(item, (str, ArrayAccess)):
                self._resolve_lvalue_type(item)
            else:
                # Identifier ou qualquer outro nó — visita normalmente;
                # visit_Identifier faz lookup_or_raise automaticamente.
                item.accept(self)

    def visit_StopStmt(self, node: StopStmt) -> None:
        pass

    def visit_ReturnStmt(self, node: ReturnStmt) -> None:
        if self.st.current_scope.kind not in ("function", "subroutine"):
            self._error("RETURN fora de uma função ou subrotina")

    def visit_CallStmt(self, node: CallStmt) -> None:
        sym = self._safe(self.st.lookup_or_raise, node.name)
        if sym and sym.kind != SymbolKind.SUBROUTINE:
            self._error(f"'{node.name}' não é uma subrotina")
            return
        if sym and sym.params is not None:
            self._check_arg_count(node.name, sym.params, node.args)
        for arg in node.args:
            arg.accept(self)

    def visit_Literal(self, node: Literal) -> None:
        mapping = {
            "int": FortranType.INTEGER,
            "float": FortranType.REAL,
            "double": FortranType.DOUBLE,
            "boolean": FortranType.LOGICAL,
            "string": FortranType.CHARACTER,
        }
        self._expr_type = mapping.get(node.type, FortranType.UNKNOWN)

    def visit_Identifier(self, node: Identifier) -> None:
        sym = self._safe(self.st.lookup_or_raise, node.name)
        self._expr_type = sym.type if sym else FortranType.UNKNOWN

    def visit_ArrayAccess(self, node: ArrayAccess) -> None:
        """
        Resolve a ambiguidade ArrayAccess vs FunctionCall consultando a
        symbol table. Se o nome estiver declarado como FUNCTION, trata
        como chamada de função.
        """
        sym = self._safe(self.st.lookup_or_raise, node.name)
        if sym is None:
            self._expr_type = FortranType.UNKNOWN
            return

        if sym.kind == SymbolKind.FUNCTION:
            node.__class__ = FunctionCall
            node.args = node.indices
            del node.indices

            if sym.params is not None:
                self._check_arg_count(node.name, sym.params, node.indices)
            for arg in node.indices:
                arg.accept(self)
            self._expr_type = sym.type

        elif sym.kind == SymbolKind.ARRAY:
            if sym.dimensions and len(node.indices) != len(sym.dimensions):
                self._error(
                    f"Array '{node.name}' tem {len(sym.dimensions)} dimensão(ões), "
                    f"mas foi acedido com {len(node.indices)} índice(s)"
                )
            for idx in node.indices:
                idx.accept(self)
            self._expr_type = sym.type

        else:
            self._error(f"'{node.name}' não é um array nem uma função")
            self._expr_type = FortranType.UNKNOWN

    def visit_FunctionCall(self, node: FunctionCall) -> None:
        sym = self._safe(self.st.lookup_or_raise, node.name)
        if sym and sym.kind != SymbolKind.FUNCTION:
            self._error(f"'{node.name}' não é uma função")
        if sym and sym.params is not None:
            self._check_arg_count(node.name, sym.params, node.args)
        for arg in node.args:
            arg.accept(self)
        self._expr_type = sym.type if sym else FortranType.UNKNOWN

    def visit_BinaryOp(self, node: BinaryOp) -> None:
        ltype = self._expr(node.left)
        rtype = self._expr(node.right)

        if ltype is None or rtype is None:
            self._expr_type = FortranType.UNKNOWN
            return

        result = _result_type(node.op, ltype, rtype)
        if result is None:
            self._error(
                f"Operador '{node.op}' não aplicável a " f"{ltype.name} e {rtype.name}"
            )
            self._expr_type = FortranType.UNKNOWN
        else:
            self._expr_type = result

    def visit_UnaryOp(self, node: UnaryOp) -> None:
        operand_type = self._expr(node.operand)
        if node.op in ("+", "-"):
            if operand_type not in _NUMERIC:
                self._error(
                    f"Operador unário '{node.op}' não aplicável a "
                    f"{operand_type.name if operand_type else '?'}"
                )
                self._expr_type = FortranType.UNKNOWN
            else:
                self._expr_type = operand_type
        elif node.op == ".NOT.":
            if operand_type != FortranType.LOGICAL:
                self._error(
                    f".NOT. não aplicável a "
                    f"{operand_type.name if operand_type else '?'}"
                )
                self._expr_type = FortranType.UNKNOWN
            else:
                self._expr_type = FortranType.LOGICAL

    def _check_arg_count(self, name: str, params: list, args: list) -> None:
        if len(args) != len(params):
            self._error(
                f"'{name}' espera {len(params)} argumento(s), "
                f"mas recebeu {len(args)}"
            )
