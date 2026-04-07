C      ILLEGAL CHARACTERS AND MALFORMED TOKENS
       PROGRAM ERR1
       INTEGER A, B
C      ERROR: '@' is not a valid character in F77
       A = 10 @ 5
C      ERROR: Multiple decimal points in a real constant
       B = 1.2.3
C      ERROR: Lowercase letters (Standard F77 is uppercase only)
       c = 20
C      ERROR: Unexpected character '!' 
       A = A + 1 ! incrementing
       STOP
       END