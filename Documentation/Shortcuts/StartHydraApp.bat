@ECHO OFF
REM Todo: Make a window popup for errors

CD %~dp0

:Check1
  IF DEFINED HYDRA GOTO Check2
    ECHO Could Not Find HYDRA Enviromental Variable!
    PAUSE
    GOTO :EOF

:Check2
  IF NOT [%1] == [] GOTO Check3
    ECHO No App Given!
    PAUSE
    GOTO :EOF

:Check3
  IF EXIST %HYDRA%\%1.exe GOTO Start
    ECHO Bad App Given!
    PAUSE
    GOTO :EOF

:Start
  IF NOT [%2] == [] TIMEOUT /t %2
  START /d %HYDRA% %1.exe
