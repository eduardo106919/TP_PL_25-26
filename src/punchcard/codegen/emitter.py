class Emitter:
    """
    Guarda as instruções EWVM geradas e depois imprime-as.
    Simples: é só uma lista de strings.
    """

    def __init__(self):
        self._lines: list[str] = []
        self._label_counter = 0

    def emit(self, instruction: str) -> None:
        self._lines.append(instruction)

    def emit_label(self, label: str) -> None:
        """Emite uma label (sem indentação)."""
        self._lines.append(f"{label}:")

    def new_label(self, prefix: str = "L") -> str:
        """Gera uma label única, ex: L0, L1, L2..."""
        label = f"{prefix}{self._label_counter}"
        self._label_counter += 1
        return label

    def get_code(self) -> str:
        return "\n".join(self._lines)

    def __str__(self) -> str:
        return self.get_code()