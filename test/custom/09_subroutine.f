      PROGRAM SUBTEST
      INTEGER X, Y, RES
      X = 8
      Y = 3
      CALL SOMA(X, Y, RES)
      PRINT *, 'Soma: ', RES
      END

      SUBROUTINE SOMA(A, B, C)
      INTEGER A, B, C
      C = A + B
      RETURN
      END
