class PunchCardEmitter:
    """
    Guarda as instruções EWVM geradas e depois imprime-as.
    """

    def __init__(self):
        self._lines: list[str] = []
        self._label_counter = 0

    def emit(self, instruction: str) -> None:
        """
        Emite uma instrução. 
        Se for uma label (termina em :) ou início/fim de programa, não indenta.
        Caso contrário, adiciona indentação.
        """
        instr = instruction.strip()
        if not instr:
            return

        if instr.endswith(":") or instr in ("START", "STOP"):
            self._lines.append(instr)
        else:
            self._lines.append(f"    {instr}")

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