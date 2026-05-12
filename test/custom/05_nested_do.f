      PROGRAM NESTDO
      INTEGER I, J
      DO 20 I = 1, 3
         DO 10 J = 1, 3
            PRINT *, I, ' x ', J, ' = ', I * J
   10    CONTINUE
   20 CONTINUE
      END
