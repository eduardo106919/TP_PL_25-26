import sys
import argparse

from punchcard.errors import ErrorManager
from punchcard.lexer.lexer import PunchCardLexer
from punchcard.parser.parser import PunchCardParser
from punchcard.semantic.semantic_analyser import PunchCardSemanticAnalyser
from punchcard.codegen.codegen import PunchCardCodeGenerator


def compile_code(code: str, show_tokens: bool = False, show_ast: bool = False):
    """
    Executa todo o pipeline do compilador: Lexer -> Parser -> Semantic -> CodeGen.
    Imprime o código EWVM resultante ou reporta erros.
    """
    errors = ErrorManager()

    lexer = PunchCardLexer(errors).build()

    if show_tokens:
        lexer.input(code)
        print("--- Tokens ---")
        for token in lexer:
            print(token)
        print("--- End Tokens ---")
        # Reset lexer for the parser
        lexer = PunchCardLexer(errors).build()

    parser = PunchCardParser(lexer, errors)
    ast = parser.parse(code)

    if show_ast:
        print("--- AST ---")
        print(ast)
        print("--- End AST ---")

    if errors.has_errors():
        errors.report()
        return

    analyzer = PunchCardSemanticAnalyser(errors)
    analyzer.analyse(ast)

    if errors.has_errors():
        errors.report()
        return

    codegen = PunchCardCodeGenerator()
    ewvm_code = codegen.generate(ast)

    print(ewvm_code)


def main():
    parser = argparse.ArgumentParser(
        description="PunchCard Fortran 77 to EWVM Compiler"
    )
    parser.add_argument(
        "file",
        nargs="?",
        help="Caminho para o ficheiro .f (opcional; se omitido lê do stdin)",
    )
    parser.add_argument(
        "--show-ast",
        action="store_true",
        help="Mostra a Árvore Sintática Abstrata (AST) gerada pelo parser.",
    )
    parser.add_argument(
        "--show-tokens",
        action="store_true",
        help="Mostra os tokens gerados pelo analisador léxico.",
    )

    args = parser.parse_args()

    if args.file:
        try:
            with open(args.file, "r") as f:
                code = f.read()
            compile_code(code, args.show_tokens, args.show_ast)
        except FileNotFoundError:
            print(f"Erro: Ficheiro '{args.file}' não encontrado.")
            sys.exit(1)
        except Exception as e:
            print(f"Erro ao ler ficheiro: {e}")
            sys.exit(1)
    else:
        if sys.stdin.isatty():
            print(
                "PunchCard Compiler - Introduza o código Fortran (Ctrl+D para terminar):"
            )

        code = sys.stdin.read()
        if code.strip():
            compile_code(code, args.show_tokens, args.show_ast)


if __name__ == "__main__":
    main()
