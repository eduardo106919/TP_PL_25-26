class ErrorManager:
    def __init__(self):
        self.errors = []

    def add_error(self, line, column, message, error_type="Syntax"):
        self.errors.append(
            {"line": line, "column": column, "message": message, "type": error_type}
        )

    def report(self):
        if not self.errors:
            return
        print("\n--- Compilation Errors ---")
        for err in self.errors:
            print(
                f"[{err['type']} Error] Line {err['line']}, Col {err['column']}: {err['message']}"
            )

    def has_errors(self):
        return len(self.errors) > 0
