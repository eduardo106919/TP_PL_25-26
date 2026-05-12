      PROGRAM GOTOLBL
      INTEGER I
      I = 0
   10 I = I + 1
      IF (I .LT. 5) GOTO 10
      PRINT *, 'Contagem final: ', I
      END
