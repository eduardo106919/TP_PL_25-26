class ASTNode:
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


class Program(ASTNode):
    def __init__(self, units):
        self.units = units


class MainProgram(ASTNode):
    def __init__(self, name, body):
        self.name = name
        self.body = body


class FunctionSubprogram(ASTNode):
    def __init__(self, name, params, body, return_type=None):
        self.name = name
        self.return_type = return_type
        self.params = params
        self.body = body


class SubroutineSubprogram(ASTNode):
    def __init__(self, name, params, body):
        self.name = name
        self.params = params
        self.body = body


class Body(ASTNode):
    def __init__(self, declarations, statements):
        self.declarations = declarations
        self.statements = statements


class Declaration(ASTNode):
    def __init__(self, type_spec, variables):
        self.type_spec = type_spec
        self.variables = variables


class VarDecl(ASTNode):
    def __init__(self, name, dimensions=None):
        self.name = name
        self.dimensions = dimensions


class LabeledStatement(ASTNode):
    def __init__(self, label, statement):
        self.label = label
        self.statement = statement


class AssignmentStmt(ASTNode):
    def __init__(self, lvalue, value):
        self.lvalue = lvalue
        self.value = value


class GotoStmt(ASTNode):
    def __init__(self, label):
        self.label = label


class IfStmt(ASTNode):
    def __init__(self, condition, then_body, else_body=None):
        self.condition = condition
        self.then_body = then_body
        self.else_body = else_body


class DoStmt(ASTNode):
    def __init__(self, label, var, start, stop, body, go_label, step=None):
        self.label = label
        self.var = var
        self.start = start
        self.stop = stop
        self.go_label = go_label
        self.step = step
        self.body = body


class ContinueStmt(ASTNode):
    def __init__(self):
        pass


class PrintStmt(ASTNode):
    def __init__(self, fmt, items):
        self.fmt = fmt
        self.items = items


class ReadStmt(ASTNode):
    def __init__(self, fmt, items):
        self.fmt = fmt
        self.items = items


class StopStmt(ASTNode):
    def __init__(self):
        pass


class ReturnStmt(ASTNode):
    def __init__(self):
        pass


class BinaryOp(ASTNode):
    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right


class UnaryOp(ASTNode):
    def __init__(self, op, operand):
        self.op = op
        self.operand = operand


class Identifier(ASTNode):
    def __init__(self, name):
        self.name = name


class ArrayAccess(ASTNode):
    def __init__(self, name, indices):
        self.name = name
        self.indices = indices


class Literal(ASTNode):
    def __init__(self, type, value):
        self.type = type
        self.value = value
