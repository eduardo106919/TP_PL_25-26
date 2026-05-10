class ErrorManager:
    """Acumula erros e avisos encontrados durante a compilação."""

    def __init__(self):
        self.errors = []

    def _format_error(self, err: dict) -> str:
        """Formata uma entrada de erro para apresentação no terminal."""
        kind = err.get("type", "Error")
        line = err.get("line")
        column = err.get("column")
        message = err.get("message", "")

        if line is None:
            return f"[{kind}] {message}"
        if column is None:
            return f"[{kind}] Line {line}: {message}"
        return f"[{kind}] Line {line}, Col {column}: {message}"

    def _store(self, line, column, message, error_type, emitted=False):
        """Guarda uma entrada de erro ou aviso na lista interna."""
        entry = {
            "line": line,
            "column": column,
            "message": message,
            "type": error_type,
            "emitted": emitted,
        }
        self.errors.append(entry)
        return entry

    def add_error(
        self,
        line,
        column,
        message,
        error_type="Syntax Error",
        emit_immediately=False,
    ):
        """Regista um erro. Se emit_immediately=True, imprime-o de imediato."""
        entry = self._store(line, column, message, error_type, emitted=False)
        if emit_immediately:
            print(self._format_error(entry))
            entry["emitted"] = True

    def add_warning(
        self,
        line,
        column,
        message,
        warning_type="Semantic Warning",
        emit_immediately=False,
    ):
        """Regista um aviso. Se emit_immediately=True, imprime-o de imediato."""
        entry = self._store(line, column, message, warning_type, emitted=False)
        if emit_immediately:
            print(self._format_error(entry))
            entry["emitted"] = True

    def report(self):
        """Imprime todos os erros e avisos que ainda não foram mostrados."""
        pending = [err for err in self.errors if not err.get("emitted", False)]
        if not pending:
            return
        print("\n--- Compilation Errors ---")
        for err in pending:
            print(self._format_error(err))
            err["emitted"] = True

    def has_errors(self):
        """Devolve True se houver pelo menos um erro registado."""
        return len(self.errors) > 0
