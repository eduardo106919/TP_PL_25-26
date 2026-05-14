      PROGRAM STARWARS
      INTEGER REP
      REP = 3
      
      CALL KENOBI(REP)
      CALL VADER(REP)

      END

      SUBROUTINE KENOBI(REP)
      INTEGER REP, I
      DO 10 I = 1, REP
            PRINT *, 'Hello there!'
   10 CONTINUE
      END

      SUBROUTINE VADER(REP)
      INTEGER REP, I
      DO 20 I = 1, REP
            PRINT *, 'i am your father'
   20 CONTINUE
      END