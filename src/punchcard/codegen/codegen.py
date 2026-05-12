"""PunchCard code generator module."""

from typing import Optional

from punchcard.parser.ast import (
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
    FunctionCall,
    BinaryOp,
    UnaryOp,
    Identifier,
    ArrayAccess,
    Literal,
)
from punchcard.codegen.emitter import PunchCardEmitter
from punchcard.semantic.symbol_table import SymbolKind, FortranType, Symbol


class PunchCardCodeGenerator:
    """Gera código EWVM percorrendo a AST com o padrão Visitor.

    O programa principal é emitido entre START e STOP.
    Funções e subrotinas são emitidas a seguir, cada uma com o seu label.
    """

    def __init__(self):
        self.emitter = PunchCardEmitter()
        self.current_scope = None
        self.global_symbols = {}
        self._label_count = 0

    def _new_label(self, prefix="l"):
        self._label_count += 1
        return f"{prefix}{self._label_count}".lower()

    def generate(self, program: Program) -> str:
        """Ponto de entrada: recebe a AST e devolve o código EWVM como string."""
        self.visit_Program(program)
        return self.emitter.get_code()

    def visit_Program(self, node: Program):
        self.global_symbols = getattr(node, "global_symbols", {})

        main = next((u for u in node.units if isinstance(u, MainProgram)), None)
        if main:
            self.emitter.emit("START")
            main.accept(self)
            self.emitter.emit("STOP")

        for unit in node.units:
            if not isinstance(unit, MainProgram):
                unit.accept(self)

    def visit_MainProgram(self, node: MainProgram):
        self.current_scope = getattr(node, "scope", None)
        node.body.accept(self)

    def visit_Body(self, node: Body):
        for decl in node.declarations:
            decl.accept(self)
        for stmt in node.statements:
            stmt.accept(self)

    def visit_Declaration(self, node: Declaration):
        for var in node.variables:
            var.accept(self)

    def visit_VarDecl(self, node: VarDecl):
        """Reserva espaço no stack para cada variável declarada."""
        sym = self.current_scope.lookup(node.name)
        if not sym or sym.kind == SymbolKind.PARAMETER:
            return

        if sym.kind == SymbolKind.ARRAY:
            self.emitter.emit(f"PUSHN {sym.size}")
        elif sym.type in (FortranType.REAL, FortranType.DOUBLE):
            self.emitter.emit("PUSHF 0.0")
        else:
            self.emitter.emit("PUSHI 0")

    def visit_FunctionSubprogram(self, node: FunctionSubprogram):
        self.current_scope = getattr(node, "scope", None)
        self.emitter.emit(f"{node.name.lower()}:")
        node.body.accept(self)
        # Se não houver RETURN explícito, o END implica retorno
        if not self.emitter.get_code().strip().endswith("RETURN"):
            self.visit_ReturnStmt(None)

    def visit_SubroutineSubprogram(self, node: SubroutineSubprogram):
        self.current_scope = getattr(node, "scope", None)
        self.emitter.emit(f"{node.name.lower()}:")
        node.body.accept(self)
        if not self.emitter.get_code().strip().endswith("RETURN"):
            self.visit_ReturnStmt(None)

    def visit_AssignmentStmt(self, node: AssignmentStmt):
        node.value.accept(self)  # valor fica no topo do stack

        if isinstance(node.lvalue, str):
            sym = self.current_scope.lookup(node.lvalue)
            self._emit_store(sym)
        elif isinstance(node.lvalue, ArrayAccess):
            sym = self.current_scope.lookup(node.lvalue.name)
            self._emit_addr(sym)
            # F77 usa indexação 1-based; subtrai 1 para obter offset 0-based
            node.lvalue.indices[0].accept(self)
            self.emitter.emit("PUSHI 1")
            self.emitter.emit("SUB")
            self.emitter.emit("PADD")
            self.emitter.emit("SWAP")
            self.emitter.emit("STORE 0")

    def visit_PrintStmt(self, node: PrintStmt):
        for item in node.items:
            item.accept(self)
            itype = self._get_expr_type(item)
            if itype == FortranType.CHARACTER:
                self.emitter.emit("WRITES")
            elif itype in (FortranType.REAL, FortranType.DOUBLE):
                self.emitter.emit("WRITEF")
            else:
                self.emitter.emit("WRITEI")
        self.emitter.emit("WRITELN")

    def visit_ReadStmt(self, node: ReadStmt):
        for item in node.items:
            self.emitter.emit("READ")
            # Converte consoante o tipo da variável
            name = item if isinstance(item, str) else item.name
            sym = self.current_scope.lookup(name)

            if sym.type == FortranType.INTEGER:
                self.emitter.emit("ATOI")
            elif sym.type in (FortranType.REAL, FortranType.DOUBLE):
                self.emitter.emit("ATOF")

            # Guarda na variável
            if isinstance(item, str):
                self._emit_store(sym)
            else:
                # ArrayAccess
                self._emit_addr(sym)
                item.indices[0].accept(self)
                self.emitter.emit("PUSHI 1")
                self.emitter.emit("SUB")
                self.emitter.emit("PADD")
                self.emitter.emit("SWAP")
                self.emitter.emit("STORE 0")

    def visit_DoStmt(self, node: DoStmt):
        """DO label var = start, stop [, step]: inicializa, testa e incrementa."""
        start_label = self._new_label("dostart")
        end_label = self._new_label("doend")

        sym = self.current_scope.lookup(node.var)

        node.start.accept(self)
        self._emit_store(sym)

        self.emitter.emit(f"{start_label}:")
        self._emit_push(sym)
        node.stop.accept(self)
        self.emitter.emit("INFEQ")
        self.emitter.emit(f"JZ {end_label}")

        for stmt in node.body:
            stmt.accept(self)

        self._emit_push(sym)
        if node.step:
            node.step.accept(self)
        else:
            self.emitter.emit("PUSHI 1")
        self.emitter.emit("ADD")
        self._emit_store(sym)

        self.emitter.emit(f"JUMP {start_label}")
        self.emitter.emit(f"{end_label}:")

    def visit_LabeledStatement(self, node: LabeledStatement):
        # Gera o label (e.g. l10)
        self.emitter.emit(f"l{node.label}:")
        node.statement.accept(self)

    def visit_ContinueStmt(self, node: ContinueStmt):
        self.emitter.emit("NOP")

    def visit_GotoStmt(self, node: GotoStmt):
        self.emitter.emit(f"JUMP l{node.label}")

    def visit_IfStmt(self, node: IfStmt):
        # Versão simplificada: assume que IF sempre tem THEN e opcional ELSE
        else_label = self._new_label("ifelse")
        end_label = self._new_label("ifend")

        node.condition.accept(self)
        self.emitter.emit(f"JZ {else_label}")

        for stmt in node.then_body:
            stmt.accept(self)
        self.emitter.emit(f"JUMP {end_label}")

        self.emitter.emit(f"{else_label}:")
        if node.else_body:
            for stmt in node.else_body:
                stmt.accept(self)

        self.emitter.emit(f"{end_label}:")

    def visit_ReturnStmt(self, node: Optional[ReturnStmt]):
        """Remove as variáveis locais do stack antes de fazer RETURN."""
        if self.current_scope.kind in ("function", "subroutine"):
            local_vars = [
                s
                for s in self.current_scope.all_symbols()
                if s.kind in (SymbolKind.VARIABLE, SymbolKind.ARRAY)
                and s.name.upper() != self.current_scope.name.upper()
            ]
            total_size = sum(s.size for s in local_vars)
            if total_size > 0:
                self.emitter.emit(f"POP {total_size}")
        self.emitter.emit("RETURN")

    def visit_StopStmt(self, node: StopStmt):
        self.emitter.emit("STOP")

    def visit_CallStmt(self, node: CallStmt):
        for arg in node.args:
            arg.accept(self)
        self.emitter.emit(f"PUSHA {node.name.lower()}")
        self.emitter.emit("CALL")
        # Limpa argumentos. Se for subrotina, limpamos tudo.
        if node.args:
            self.emitter.emit(f"POP {len(node.args)}")

    def visit_FunctionCall(self, node: FunctionCall):
        """Chamada de função como expressão. Built-ins são tratados diretamente."""
        name = node.name.upper()

        # Built-ins mapeados para instruções EWVM
        if name == "MOD":
            node.args[0].accept(self)
            node.args[1].accept(self)
            self.emitter.emit("MOD")
            return
        elif name == "SIN":
            node.args[0].accept(self)
            self.emitter.emit("FSIN")
            return
        elif name == "COS":
            node.args[0].accept(self)
            self.emitter.emit("FCOS")
            return

        func_sym = self.global_symbols.get(node.name.upper())
        if func_sym and func_sym.kind == SymbolKind.FUNCTION:
            if func_sym.type in (FortranType.REAL, FortranType.DOUBLE):
                self.emitter.emit("PUSHF 0.0")
            else:
                self.emitter.emit("PUSHI 0")

        for arg in node.args:
            arg.accept(self)
        self.emitter.emit(f"PUSHA {node.name.lower()}")
        self.emitter.emit("CALL")

        if func_sym and func_sym.kind == SymbolKind.SUBROUTINE and node.args:
            self.emitter.emit(f"POP {len(node.args)}")
        elif len(node.args) > 0:
            self.emitter.emit(f"POP {len(node.args)}")

    # Expressões
    def visit_Literal(self, node: Literal):
        if node.type == "int":
            self.emitter.emit(f"PUSHI {node.value}")
        elif node.type in ("float", "double"):
            self.emitter.emit(f"PUSHF {node.value}")
        elif node.type == "string":
            escaped = str(node.value).replace("'", "\\'")
            self.emitter.emit(f'PUSHS "{escaped}"')
        elif node.type == "boolean":
            self.emitter.emit(f"PUSHI {1 if node.value else 0}")

    def visit_Identifier(self, node: Identifier):
        sym = self.current_scope.lookup(node.name)
        if sym:
            self._emit_push(sym)
        else:
            # Pode ser uma chamada de função sem argumentos
            pass

    def visit_ArrayAccess(self, node: ArrayAccess):
        sym = self.current_scope.lookup(node.name)
        if sym:
            self._emit_addr(sym)
            node.indices[0].accept(self)
            self.emitter.emit("PUSHI 1")
            self.emitter.emit("SUB")
            self.emitter.emit("PADD")
            self.emitter.emit("LOAD 0")

    def visit_BinaryOp(self, node: BinaryOp):
        node.left.accept(self)
        node.right.accept(self)

        # Determina o tipo da expressão para escolher as instruções corretas
        left_type = self._get_expr_type(node.left)
        right_type = self._get_expr_type(node.right)
        is_float = left_type in (FortranType.REAL, FortranType.DOUBLE) or \
                   right_type in (FortranType.REAL, FortranType.DOUBLE)

        op = node.op.upper()

        if is_float:
            op_map = {
                "+": "FADD",
                "-": "FSUB",
                "*": "FMUL",
                "/": "FDIV",
                ".EQ.": "EQUAL",
                ".NE.": lambda: (self.emitter.emit("EQUAL"), self.emitter.emit("NOT")),
                ".LT.": "FINF",
                ".LE.": "FINFEQ",
                ".GT.": "FSUP",
                ".GE.": "FSUPEQ",
                ".AND.": "AND",
                ".OR.": "OR",
            }
        else:
            op_map = {
                "+": "ADD",
                "-": "SUB",
                "*": "MUL",
                "/": "DIV",
                ".EQ.": "EQUAL",
                ".NE.": lambda: (self.emitter.emit("EQUAL"), self.emitter.emit("NOT")),
                ".LT.": "INF",
                ".LE.": "INFEQ",
                ".GT.": "SUP",
                ".GE.": "SUPEQ",
                ".AND.": "AND",
                ".OR.": "OR",
            }

        instr = op_map.get(op)
        if callable(instr):
            instr()
        elif instr:
            self.emitter.emit(instr)

    def visit_UnaryOp(self, node: UnaryOp):
        node.operand.accept(self)
        if node.op == "-":
            self.emitter.emit("PUSHI -1")
            self.emitter.emit("MUL")
        elif node.op == ".NOT.":
            self.emitter.emit("NOT")

    # --- Helpers de emissão ---

    def _emit_store(self, sym: Symbol):
        """Emite STOREG (programa principal) ou STOREL (função/subrotina)."""
        if self.current_scope.kind == "program":
            self.emitter.emit(f"STOREG {sym.index}")
        else:
            idx = self._get_local_index(sym)
            self.emitter.emit(f"STOREL {idx}")

    def _emit_push(self, sym: Symbol):
        """Emite PUSHG (programa principal) ou PUSHL (função/subrotina)."""
        if self.current_scope.kind == "program":
            self.emitter.emit(f"PUSHG {sym.index}")
        else:
            idx = self._get_local_index(sym)
            self.emitter.emit(f"PUSHL {idx}")

    def _emit_addr(self, sym: Symbol):
        """Coloca no stack o endereço de uma variável (para acesso a arrays)."""
        if self.current_scope.kind == "program":
            self.emitter.emit("PUSHGP")
            self.emitter.emit(f"PUSHI {sym.index}")
        else:
            idx = self._get_local_index(sym)
            self.emitter.emit("PUSHFP")
            self.emitter.emit(f"PUSHI {idx}")
        self.emitter.emit("PADD")

    def _get_local_index(self, sym: Symbol) -> int:
        """Converte o índice da symbol table para índice relativo ao fp."""
        params = [
            s
            for s in self.current_scope.all_symbols()
            if s.kind == SymbolKind.PARAMETER
        ]
        local_index = sym.index - len(params)
        if self.current_scope.kind == "function":
            local_index -= 1
        return local_index

    def _get_expr_type(self, expr):
        if isinstance(expr, Literal):
            mapping = {
                "int": FortranType.INTEGER,
                "float": FortranType.REAL,
                "double": FortranType.DOUBLE,
                "string": FortranType.CHARACTER,
            }
            return mapping.get(expr.type, FortranType.UNKNOWN)
        if isinstance(expr, (Identifier, str)):
            name = expr.name if hasattr(expr, "name") else expr
            sym = self.current_scope.lookup(name)
            return sym.type if sym else FortranType.UNKNOWN
        if isinstance(expr, ArrayAccess):
            sym = self.current_scope.lookup(expr.name)
            return sym.type if sym else FortranType.UNKNOWN
        return FortranType.UNKNOWN

    def generic_visit(self, node):
        print(f"[CodeGen] Aviso: nó não suportado: {node.__class__.__name__}")
