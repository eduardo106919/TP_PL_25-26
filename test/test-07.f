c     TESTING DO LOOPS AND RELATIONALS
      PROGRAM LOOPTEST
      INTEGER N, SUM
      SUM = 0
      READ *, N
*     one more comment
      DO 20 I = 1, N
          IF (I .GT. 5) THEN
              SUM = SUM + I
          ENDIF
20    CONTINUE
      PRINT *, 'SUM OF ELEMENTS ABOVE 5:', SUM
      END