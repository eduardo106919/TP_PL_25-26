from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional


class FortranType(Enum):
    INTEGER = auto()
    REAL = auto()
    DOUBLE = auto()
    LOGICAL = auto()
    CHARACTER = auto()
    # tipo especial para subrotinas (não têm valor de retorno)
    SUBROUTINE = auto()
    # tipo ainda desconhecido (e.g. parâmetro antes de declaração explícita)
    UNKNOWN = auto()

    @staticmethod
    def from_token(token: str) -> "FortranType":
        """Converte o token do lexer (DT_INTEGER, etc.) para FortranType."""
        mapping = {
            "INTEGER": FortranType.INTEGER,
            "DT_INTEGER": FortranType.INTEGER,
            "REAL": FortranType.REAL,
            "DT_REAL": FortranType.REAL,
            "DOUBLE PRECISION": FortranType.DOUBLE,
            "DT_DOUBLE_PRECISION": FortranType.DOUBLE,
            "LOGICAL": FortranType.LOGICAL,
            "DT_LOGICAL": FortranType.LOGICAL,
            "CHARACTER": FortranType.CHARACTER,
            "DT_CHARACTER": FortranType.CHARACTER,
        }
        result = mapping.get(token.upper())
        if result is None:
            raise ValueError(f"Tipo Fortran desconhecido: '{token}'")
        return result


class SymbolKind(Enum):
    VARIABLE = auto()  # variável escalar
    ARRAY = auto()  # variável array
    FUNCTION = auto()  # INTEGER FUNCTION FOO(...)
    SUBROUTINE = auto()  # SUBROUTINE BAR(...)
    PARAMETER = auto()  # parâmetro formal de função/subrotina


@dataclass
class Symbol:
    name: str
    kind: SymbolKind
    type: FortranType = FortranType.UNKNOWN

    # Para arrays: lista de expressões de dimensão (guardadas como strings
    # ou inteiros — a semântica resolve; None = escalar)
    dimensions: Optional[list] = None

    # Para funções e subrotinas: lista de nomes dos parâmetros formais
    params: Optional[list[str]] = None

    # Linha de declaração (útil para mensagens de erro)
    declared_at: Optional[int] = None

    def is_callable(self) -> bool:
        return self.kind in (SymbolKind.FUNCTION, SymbolKind.SUBROUTINE)

    def is_array(self) -> bool:
        return self.kind == SymbolKind.ARRAY

    def __repr__(self) -> str:
        parts = [f"{self.kind.name} {self.type.name} {self.name!r}"]
        if self.dimensions:
            parts.append(f"dims={self.dimensions}")
        if self.params is not None:
            parts.append(f"params={self.params}")
        return f"Symbol({', '.join(parts)})"


class Scope:
    """
    Um scope corresponde a um program unit: programa principal,
    função ou subrotina. Em Fortran 77 não existem escopos aninhados
    dentro de um mesmo program unit (sem módulos nem blocos internos),
    por isso um dicionário plano por scope é suficiente.

    Labels são guardados separadamente porque são um espaço de nomes
    distinto dos identificadores (um label '10' e uma variável '10'
    não colidem, embora em F77 os labels sejam sempre inteiros).
    """

    def __init__(self, name: str, kind: str):
        self.name = name  # nome do program unit (e.g. 'HELLO')
        self.kind = kind  # 'program' | 'function' | 'subroutine'
        self._symbols: dict[str, Symbol] = {}
        self._labels: set[int] = set()

    def declare(self, symbol: Symbol) -> None:
        """
        Regista um símbolo neste scope.
        Lança SymbolError se o nome já estiver declarado.
        """
        key = symbol.name.upper()
        if key in self._symbols:
            existing = self._symbols[key]
            raise SymbolError(
                f"'{symbol.name}' já declarado neste scope "
                f"(linha {existing.declared_at})"
            )
        self._symbols[key] = symbol

    def lookup(self, name: str) -> Optional[Symbol]:
        """Devolve o Symbol ou None se não existir."""
        return self._symbols.get(name.upper())

    def lookup_or_raise(self, name: str) -> Symbol:
        """Devolve o Symbol ou lança SymbolError."""
        sym = self.lookup(name)
        if sym is None:
            raise SymbolError(f"'{name}' não declarado neste scope")
        return sym

    def all_symbols(self) -> list[Symbol]:
        return list(self._symbols.values())

    def declare_label(self, label: int) -> None:
        """Regista um label. Lança SymbolError se duplicado."""
        if label in self._labels:
            raise SymbolError(f"Label {label} declarado mais do que uma vez")
        self._labels.add(label)

    def has_label(self, label: int) -> bool:
        return label in self._labels

    def check_label(self, label: int) -> None:
        """Lança SymbolError se o label não existir."""
        if not self.has_label(label):
            raise SymbolError(f"Label {label} referenciado mas não declarado")

    def __repr__(self) -> str:
        syms = ", ".join(repr(s) for s in self._symbols.values())
        return f"Scope({self.kind} {self.name!r}, [{syms}], labels={self._labels})"


class SymbolTable:
    """
    Tabela de símbolos global do compilador.

    Estrutura:
    - _scopes: pilha de Scope activos durante a travessia da AST.
      O topo (_scopes[-1]) é sempre o scope corrente.
    - _global: dicionário de program units (programa, funções, subrotinas)
      acessível de qualquer scope para resolver chamadas externas.

    Uso típico na análise semântica:

        st = SymbolTable()
        st.enter_scope("HELLO", "program")
        st.declare(Symbol("N", SymbolKind.VARIABLE, FortranType.INTEGER))
        st.lookup("N")          # → Symbol(...)
        st.declare_label(10)
        st.check_label(10)
        st.exit_scope()
    """

    def __init__(self):
        self._scopes: list[Scope] = []
        # program units globais: nome → Symbol (FUNCTION ou SUBROUTINE)
        self._global: dict[str, Symbol] = {}

    def enter_scope(self, name: str, kind: str) -> Scope:
        """Cria e empurra um novo scope para a pilha."""
        scope = Scope(name, kind)
        self._scopes.append(scope)
        return scope

    def exit_scope(self) -> Scope:
        """Remove e devolve o scope do topo."""
        if not self._scopes:
            raise SymbolError("exit_scope chamado sem scope activo")
        return self._scopes.pop()

    @property
    def current_scope(self) -> Scope:
        if not self._scopes:
            raise SymbolError("Nenhum scope activo")
        return self._scopes[-1]

    def declare(self, symbol: Symbol) -> None:
        """Declara um símbolo no scope corrente."""
        self.current_scope.declare(symbol)

    def declare_global(self, symbol: Symbol) -> None:
        """
        Regista um program unit (FUNCTION, SUBROUTINE) no espaço global,
        tornando-o visível a todos os scopes.
        Lança SymbolError se o nome já estiver registado.
        """
        key = symbol.name.upper()
        if key in self._global:
            raise SymbolError(
                f"Program unit '{symbol.name}' definido mais do que uma vez"
            )
        self._global[key] = symbol

    def lookup(self, name: str) -> Optional[Symbol]:
        """
        Pesquisa primeiro no scope corrente, depois no global.
        Devolve None se não encontrado.
        """
        sym = self.current_scope.lookup(name)
        if sym is not None:
            return sym
        return self._global.get(name.upper())

    def lookup_or_raise(self, name: str) -> Symbol:
        """Como lookup mas lança SymbolError se não encontrado."""
        sym = self.lookup(name)
        if sym is None:
            raise SymbolError(
                f"'{name}' não declarado " f"(scope: '{self.current_scope.name}')"
            )
        return sym

    def is_function(self, name: str) -> bool:
        """True se o nome estiver declarado como FUNCTION (global ou local)."""
        sym = self.lookup(name)
        return sym is not None and sym.kind == SymbolKind.FUNCTION

    def is_array(self, name: str) -> bool:
        """True se o nome estiver declarado como ARRAY no scope corrente."""
        sym = self.lookup(name)
        return sym is not None and sym.kind == SymbolKind.ARRAY

    def declare_label(self, label: int) -> None:
        self.current_scope.declare_label(label)

    def has_label(self, label: int) -> bool:
        return self.current_scope.has_label(label)

    def check_label(self, label: int) -> None:
        self.current_scope.check_label(label)

    def __repr__(self) -> str:
        lines = ["SymbolTable:"]
        lines.append(f"  global: {list(self._global.keys())}")
        for scope in self._scopes:
            lines.append(f"  {scope!r}")
        return "\n".join(lines)


class SymbolError(Exception):
    """Erro semântico relacionado com a tabela de símbolos."""

    pass
