# Documentation

## Base Operations

### Integer Operations

- `ADD` — takes `n` and `m` from the pile and stacks the result `m + n`.
- `SUB` — takes `n` and `m` from the pile and stacks the result `m - n`.
- `MUL` — takes `n` and `m` from the pile and stacks the result `m × n`.
- `DIV` — takes `n` and `m` from the pile and stacks the result `m / n`.
- `MOD` — takes `n` and `m` from the pile and stacks the result `m mod n`.
- `NOT` — takes `n` from the pile and stacks the result `n = 0`.
- `INF` — takes `n` and `m` from the pile and stacks the result `m < n`.
- `INFEQ` — takes `n` and `m` from the pile and stacks the result `m <= n`.
- `SUP` — takes `n` and `m` from the pile and stacks the result `m > n`.
- `SUPEQ` — takes `n` and `m` from the pile and stacks the result `m >= n`.

### Float Operations

- `FADD` — takes `n` and `m` from the pile and stacks the result `m + n`.
- `FSUB` — takes `n` and `m` from the pile and stacks the result `m - n`.
- `FMUL` — takes `n` and `m` from the pile and stacks the result `m × n`.
- `FDIV` — takes `n` and `m` from the pile and stacks the result `m / n`.
- `FCOS` — takes `n` from the pile and stacks the result `cos(n)`.
- `FSIN` — takes `n` from the pile and stacks the result `sin(n)`.
- `FINF` — takes `n` and `m` from the pile and stacks the result `m < n`.
- `FINFEQ` — takes `n` and `m` from the pile and stacks the result `m <= n`.
- `FSUP` — takes `n` and `m` from the pile and stacks the result `m > n`.
- `FSUPEQ` — takes `n` and `m` from the pile and stacks the result `m >= n`.

### Address Operations

- `PADD` — takes an integer `n` and an address `a` from the pile and stacks the address `a + n`.

### String Operations

- `CONCAT` — takes `n` and `m` from the pile and stacks the concatenated strings (string `n` + string `m`) address.
- `CHRCODE` — takes `n` from the pile (must be a string) and stacks the ASCII code of the first character.
- `STRLEN` — takes `n` from the pile and stacks the length of the string.
- `CHARAT` — takes `n` and `m` from the pile and stacks the ASCII code of the character in string `m` at position `n`.

### Heap Operations

- `ALLOC integer_n` — allocates a structured block sized `n` and stacks its address.
- `ALLOCN` — takes an integer `n` from the pile, allocates a structured block sized `n`, and stacks its address.
- `FREE` — takes an address `a` from the pile and frees its allocated structured block.
- `POPST` — removes the last structured block from the heap.

### Equality

- `EQUAL` — takes `n` and `m` from the pile and stacks the result `n = m`.

### Conversions

- `ATOI` — takes a String Heap address from the pile and stacks its string's conversion to an integer (fails if not an integer).
- `ATOF` — takes a String Heap address from the pile and stacks its string's conversion to a real number (fails if not a real number).
- `ITOF` — takes an integer from the pile and stacks its conversion to a real number.
- `FTOI` — takes a real number from the pile and stacks its conversion to an integer by truncating decimals.
- `STRI` — takes an integer from the pile, converts it to a string, and stacks its address.
- `STRF` — takes a real number from the pile, converts it to a string, and stacks its address.

## Data Manipulation

### Stacking

- `PUSHI integer_n` — stacks `n`.
- `PUSHN integer_n` — stacks `n` zeros.
- `PUSHF real_number_n` — stacks the real number `n`.
- `PUSHS string_n` — stores string `s` in the String Heap and stacks its address.
- `PUSHG integer_n` — stacks the value found in `gp[n]`.
- `PUSHL integer_n` — stacks the value found in `fp[n]`.
- `PUSHSP` — stacks the value of the register `sp`.
- `PUSHFP` — stacks the value of the register `fp`.
- `PUSHGP` — stacks the value of the register `gp`.
- `PUSHST integer_n` — pushes the address of the struct heap at index `n` to the stack.
- `LOAD integer_n` — takes an address `a` from the pile and stacks the value found in `a[n]` (either on the pile or in the heap, depending on `a`).
- `LOADN` — takes an integer `n` and an address `a` from the pile and stacks the value found in `a[n]`.
- `DUP integer_n` — duplicates and stacks `n` times the top value of the pile.
- `DUPN` — takes integer `n` from the pile and duplicates the top value `n` times.
- `COPY integer_n` — copies the top `n` values of the pile and stacks them in the same order.
- `COPYN` — takes integer `n` from the pile and copies the top `n` values in the same order.

### Taking from Stack

- `POP integer_n` — removes `n` values from the pile.
- `POPN` — takes integer `n` from the pile and then pops `n` values.

### Archiving

- `STOREL integer_n` — takes a value from the pile and stores it in `fp[n]`.
- `STOREG integer_n` — takes a value from the pile and stores it in `gp[n]`.
- `STORE integer_n` — takes a value `v` and an address `a` and stores `v` in `a[n]` (pile or heap depending on `a`).
- `STOREN` — takes a value `v`, an integer `n`, and an address `a` and stores `v` in `a[n]`.

### Miscellaneous

- `CHECK integer_n, integer_p` — verifies the top of the pile contains an integer `i` such that `n <= i <= p` (throws an error otherwise).
- `SWAP` — takes values `v` and `m` from the pile and stacks `m` followed by `v`.
- `AND` — takes `n` and `m` from the pile and stacks the result `n && m`.
- `OR` — takes `n` and `m` from the pile and stacks the result `n || m`.

## Input / Output

- `WRITEI` — takes an integer from the pile and prints its value.
- `WRITEF` — takes a real number from the pile and prints its value.
- `WRITES` — takes a String Heap address from the pile and prints its string.
- `WRITELN` — prints a newline.
- `WRITECHR` — takes an integer from the pile and prints its corresponding ASCII character.
- `READ` — reads a string from the keyboard, stores it in the String Heap, and stacks its address.

## Control Operations

### Program Counter / Jumps

- `PUSHA label` — stacks the label's code address.
- `JUMP label` — assigns the label's code address to the program counter (`pc`).
- `JZ label` — pops a value `v` and if `v == 0` sets `pc` to the label's address; otherwise continues (increments `pc`).

### Procedures

- `CALL` — takes a label's address `a` from the pile, saves `pc` and `fp` on the Call Stack, sets `pc` to `a`, and sets `fp` to the current `sp`.
- `RETURN` — restores `sp` from `fp`, reinstates `fp` and `pc` from the Call Stack, and increments `pc`.

## Program Start / Termination

- `START` — sets `fp` to the current `sp`.
- `NOP` — no operation.
- `ERR string_x` — throws an error with message `x`.
- `STOP` — halts program execution.
