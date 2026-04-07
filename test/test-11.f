C      OPERATOR SYNTX ERRORS
       PROGRAM ERR4
       LOGICAL FLAG
       FLAG = .TRUE.
C      ERROR: Missing closing dot on logical operator
       IF (A .GT 5) THEN
C      ERROR: Invalid operator sequence (F77 doesn't have ==)
       IF (A == B) STOP
C      ERROR: Invalid use of '.' (not part of a number or operator)
       A = B . C
       END IF
       STOP
       END