@ECHO OFF

IF NOT [%1] == [] GOTO Convert
  ECHO No UI File Given!
  PAUSE
  GOTO :EOF

:Convert
  pyuic4 -x -o ../../CompiledUI/%1.py %1.ui
