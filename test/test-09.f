C      LABEL AND IDENTIFIER VIOLATIONS
       PROGRAM ERR2
C      ERROR: Label is too long (Max 5 digits)
123456 A = 5.0
C      ERROR: Identifier is too long (Max 6 characters)
       LONGRUNVARIABLE = 10.0
C      ERROR: Identifier starts with a digit
       1VAR = 2.0
C      ERROR: Label contains a non-digit character
12A45  CONTINUE
       STOP
       END