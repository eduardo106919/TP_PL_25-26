class ASTNode:
    """Classe base de todos os nós da árvore sintática (AST).

    Implementa o padrão Visitor: cada nó chama o método visit_<NomeClasse>
    do visitante recebido, permitindo percorrer a AST sem alterar as classes.
    """

    def __repr__(self, indent=0):
        pad = "  " * indent
        lines = [f"{pad}{self.__class__.__name__}"]
        for key, val in self.__dict__.items():
            if isinstance(val, ASTNode):
                lines.append(f"{pad}  {key}:")
                lines.append(val.__repr__(indent + 2))
            elif isinstance(val, list):
                lines.append(f"{pad}  {key}:")
                for item in val:
                    if isinstance(item, ASTNode):
                        lines.append(item.__repr__(indent + 2))
                    else:
                        lines.append(f"{'  ' * (indent + 2)}{item!r}")
            else:
                lines.append(f"{pad}  {key}: {val!r}")
        return "\n".join(lines)

    def accept(self, visitor):
        method_name = f"visit_{self.__class__.__name__}"
        method = getattr(visitor, method_name, visitor.generic_visit)
        return method(self)


# --- Program units ---

class Program(ASTNode):
    """Raiz da AST. Contém todos os program units (programa principal + subprogramas)."""

    def __init__(self, units):
        self.units = units


class MainProgram(ASTNode):
    """Programa principal: PROGRAM nome ... END."""

    def __init__(self, name, body):
        self.name = name
        self.body = body


class FunctionSubprogram(ASTNode):
    """Função Fortran: [tipo] FUNCTION nome(params) ... END."""

    def __init__(self, name, params, body, return_type=None):
        self.name = name
        self.return_type = return_type
        self.params = params
        self.body = body


class SubroutineSubprogram(ASTNode):
    """Subrotina Fortran: SUBROUTINE nome(params) ... END."""

    def __init__(self, name, params, body):
        self.name = name
        self.params = params
        self.body = body


# --- Declarações ---

class Body(ASTNode):
    """Corpo de um program unit: lista de declarações seguida de statements."""

    def __init__(self, declarations, statements):
        self.declarations = declarations
        self.statements = statements


class Declaration(ASTNode):
    """Declaração de tipo: INTEGER A, B ou REAL X(10)."""

    def __init__(self, type_spec, variables):
        self.type_spec = type_spec
        self.variables = variables


class VarDecl(ASTNode):
    """Nome de variável dentro de uma declaração, com dimensões opcionais para arrays."""

    def __init__(self, name, dimensions=None):
        self.name = name
        self.dimensions = dimensions


# --- Statements ---

class LabeledStatement(ASTNode):
    """Statement com label numérico: 10 CONTINUE."""

    def __init__(self, label, statement):
        self.label = label
        self.statement = statement


class AssignmentStmt(ASTNode):
    """Atribuição: variável = expressão."""

    def __init__(self, lvalue, value):
        self.lvalue = lvalue
        self.value = value


class GotoStmt(ASTNode):
    """Salto incondicional: GOTO label."""

    def __init__(self, label):
        self.label = label


class IfStmt(ASTNode):
    """IF (condição) THEN ... [ELSE ...] ENDIF."""

    def __init__(self, condition, then_body, else_body=None):
        self.condition = condition
        self.then_body = then_body
        self.else_body = else_body


class DoStmt(ASTNode):
    """Ciclo DO: DO label var = start, stop [, step] ... label CONTINUE."""

    def __init__(self, label, var, start, stop, body, go_label=None, step=None):
        self.label = label
        self.var = var
        self.start = start
        self.stop = stop
        self.step = step
        self.body = body
        self.go_label = go_label


class ContinueStmt(ASTNode):
    def __init__(self):
        pass


class PrintStmt(ASTNode):
    """PRINT *, item1, item2, ..."""

    def __init__(self, fmt, items):
        self.fmt = fmt
        self.items = items


class ReadStmt(ASTNode):
    """READ *, var1, var2, ..."""

    def __init__(self, fmt, items):
        self.fmt = fmt
        self.items = items


class StopStmt(ASTNode):
    def __init__(self):
        pass


class ReturnStmt(ASTNode):
    def __init__(self):
        pass


class CallStmt(ASTNode):
    """Chamada a subrotina: CALL nome(args)."""

    def __init__(self, name, args):
        self.name = name
        self.args = args


# --- Expressões ---

class BinaryOp(ASTNode):
    """Operação binária: left op right (ex: A + B, I .LE. N)."""

    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right


class UnaryOp(ASTNode):
    """Operação unária: -expr ou .NOT. expr."""

    def __init__(self, op, operand):
        self.op = op
        self.operand = operand


class Identifier(ASTNode):
    """Referência a uma variável pelo nome."""

    def __init__(self, name):
        self.name = name


class ArrayAccess(ASTNode):
    """Acesso a array: nome(índice).
    A análise semântica pode converter este nó em FunctionCall
    se o nome corresponder a uma função declarada.
    """

    def __init__(self, name, indices):
        self.name = name
        self.indices = indices


class FunctionCall(ASTNode):
    """Chamada de função como expressão: nome(args)."""

    def __init__(self, name, args):
        self.name = name
        self.args = args


class Literal(ASTNode):
    """Valor literal: inteiro, real, double, string ou booleano."""

    def __init__(self, type, value):
        self.type = type
        self.value = value
