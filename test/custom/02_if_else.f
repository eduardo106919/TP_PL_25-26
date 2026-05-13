      PROGRAM IFTEST
      INTEGER X
      X = 15
      IF (X .GT. 10) THEN
         PRINT *, 'X e maior que 10'
      ELSE
         PRINT *, 'X e menor ou igual a 10'
      ENDIF
      IF (X .EQ. 15) THEN
         PRINT *, 'X e igual a 15'
      ENDIF
      END
