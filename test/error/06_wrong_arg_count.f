      PROGRAM ERRARG
      INTEGER X, Y, CONVRT
      X = 10
      Y = CONVRT(X)
      PRINT *, Y
      END

      INTEGER FUNCTION CONVRT(A, B)
      INTEGER A, B
      CONVRT = A + B
      RETURN
      END
