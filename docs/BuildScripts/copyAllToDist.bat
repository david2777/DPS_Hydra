@ECHO OFF
XCOPY .\*.py .\dist\Python\ /y
XCOPY .\*.cfg .\dist\Python\ /y
XCOPY .\utils\*.py .\dist\Python\utils\ /iy
XCOPY .\hydra\*.py .\dist\Python\hydra\ /iy
XCOPY .\networking\*.py .\dist\Python\networking\ /iy
XCOPY .\docs\*.py .\dist\Python\docs\ /iy
XCOPY .\docs\*.mel .\dist\Python\docs\ /iy
XCOPY .\dialogs_qt\*.py .\dist\Python\dialogs_qt\ /iy
XCOPY .\compiled_qt\*.py .\dist\Python\compiled_qt\ /iy
XCOPY .\assets .\dist\Python\assets\ /isy
PAUSE
