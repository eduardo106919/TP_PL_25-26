class PunchCardEmitter:
    """Acumula as instruções EWVM geradas e produz o código final como texto."""

    def __init__(self):
        self._lines: list[str] = []
        self._label_counter = 0

    def emit(self, instruction: str) -> None:
        """Adiciona uma instrução. Labels e START/STOP ficam sem indentação."""
        instr = instruction.strip()
        if not instr:
            return

        if instr.endswith(":") or instr in ("START", "STOP"):
            self._lines.append(instr)
        else:
            self._lines.append(f"    {instr}")

    def emit_label(self, label: str) -> None:
        """Emite uma label sem indentação."""
        self._lines.append(f"{label}:")

    def new_label(self, prefix: str = "L") -> str:
        """Gera uma label única com o prefixo dado (ex: L0, L1, ...)."""
        label = f"{prefix}{self._label_counter}"
        self._label_counter += 1
        return label

    def get_code(self) -> str:
        """Devolve todo o código gerado como uma string."""
        return "\n".join(self._lines)

    def __str__(self) -> str:
        return self.get_code()
