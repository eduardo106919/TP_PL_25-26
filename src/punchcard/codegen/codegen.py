from punchcard.parser.ast import *
from punchcard.codegen.emitter import Emitter
 
 
class CodeGen:
    """
    Percorre a AST com o padrão Visitor e gera instruções EWVM.
 
    Para cada nó da AST existe um método visit_NomeDoNo(node).
    Se não existir método para um nó, generic_visit lança um aviso.
    """
 
    def __init__(self):
        self.emitter = Emitter()
        # symbol table simples: nome -> posição no stack frame (índice gp para globals)
        self.globals: dict[str, int] = {}
        self._next_global = 0
 
    # Entrada principal
    def generate(self, program: Program) -> str:
        self.visit_Program(program)
        return self.emitter.get_code()
 
    # Programa
    def visit_Program(self, node: Program):
        self.emitter.emit("START")
        for unit in node.units:
            unit.accept(self)
        self.emitter.emit("STOP")
 
    def visit_MainProgram(self, node: MainProgram):
        node.body.accept(self)
 
    def visit_Body(self, node: Body):
        # Primeiro as declarações (reserva espaço no stack)
        for decl in node.declarations:
            decl.accept(self)
        # Depois os statements
        for stmt in node.statements:
            stmt.accept(self)

    # Fallback
    def generic_visit(self, node):
        print(f"[CodeGen] Aviso: nó não suportado: {node.__class__.__name__}")
