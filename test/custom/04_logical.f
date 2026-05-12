      PROGRAM LOGIC
      LOGICAL A, B, C
      A = .TRUE.
      B = .FALSE.
      C = A .AND. B
      IF (C) THEN
         PRINT *, 'TRUE AND FALSE = TRUE'
      ELSE
         PRINT *, 'TRUE AND FALSE = FALSE'
      ENDIF
      C = A .OR. B
      IF (C) THEN
         PRINT *, 'TRUE OR FALSE = TRUE'
      ENDIF
      IF (.NOT. B) THEN
         PRINT *, 'NOT FALSE = TRUE'
      ENDIF
      END
