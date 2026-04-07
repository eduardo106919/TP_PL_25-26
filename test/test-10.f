C      STRING AND HOLLERITH ERRORS
       PROGRAM ERR3
       CHARACTER*10 MSG
C      ERROR: Unclosed string literal
       MSG = 'HELLO
C      ERROR: Hollerith count does not match following characters
C      (4H only takes 'TEST', leaving 'ING' as a syntax error)
       WRITE(*,*) 4HTESTING
C      ERROR: Using double quotes (Standard F77 uses single quotes only)
       MSG = "WORLD"
       STOP
       END