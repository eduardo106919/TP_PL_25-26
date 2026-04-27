class ErrorManager:
    def __init__(self):
        self.errors = []

    def _format_error(self, err: dict) -> str:
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
        entry = self._store(line, column, message, warning_type, emitted=False)
        if emit_immediately:
            print(self._format_error(entry))
            entry["emitted"] = True

    def report(self):
        pending = [err for err in self.errors if not err.get("emitted", False)]
        if not pending:
            return
        print("\n--- Compilation Errors ---")
        for err in pending:
            print(self._format_error(err))
            err["emitted"] = True

    def has_errors(self):
        return len(self.errors) > 0
