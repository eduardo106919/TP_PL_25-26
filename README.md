# Trabalho Prático PL 2025/2026

Trabalho Prático de **Processamento de Linguagens** do ano letivo 2025/2026.

## 📘 Descrição Geral

Este projeto consiste no desenvolvimento de um **compilador para a linguagem Fortran 77 (ANSI X3.9‑1978)**, realizado no âmbito da unidade curricular de _Processamento de Linguagens_. O objetivo central é implementar todas as fases essenciais de um compilador moderno - desde a análise do código‑fonte até à geração de código executável para a máquina virtual fornecida.

O compilador foi desenvolvido em **Python**, recorrendo à biblioteca **PLY (Python Lex-Yacc)** para a construção do analisador léxico e sintático, seguindo uma abordagem modular e extensível.

## 🎯 Objetivos

- Implementar um **analisador léxico** capaz de reconhecer tokens da linguagem Fortran 77.
- Construir um **analisador sintático** que valide a estrutura gramatical dos programas.
- Realizar **análise semântica**, garantindo coerência de tipos, declarações e estruturas de controlo.
- Gerar **código intermédio** ou **código da máquina virtual**, assegurando correção e eficiência.
- Disponibilizar um conjunto de **testes** que validem o funcionamento do compilador em programas reais.

## 🛠️ Instruções de Utilização

### Requisitos

- Python 3.10 ou superior.
- Dependências listadas em `requirements.txt`.

Instale as dependências com:

```bash
pip install -r requirements.txt
```

### Compilar um programa Fortran

Para compilar um ficheiro `.f` e obter o código EWVM, execute o seguinte comando a partir da pasta `src`:

```bash
python -m punchcard.main <caminho/para/ficheiro.f>
```

Exemplo:

```bash
python -m punchcard.main ../test/basic/01_hello.f
```

O código EWVM será impresso para o _stdout_. Também pode passar código através do _stdin_:

```bash
cat programa.f | python -m punchcard.main
```

### Executar os testes

Para executar todos os testes, utilize o _script_ `run_tests.sh`:

```bash
bash run_tests.sh all
```

Pode também executar grupos específicos de testes:

```bash
bash run_tests.sh basic   # Exemplos do enunciado
bash run_tests.sh custom  # Testes de funcionalidades individuais
```

## 👥 Grupo de Trabalho

Constituintes do grupo de trabalho:

| Nome                      | Número  |
| ------------------------- | ------- |
| Eduardo Freitas Fernandes | a106919 |
| Gonçalo Rodrigues Ribeiro | a106842 |
| José Mário Raimundo Lima  | a106888 |
