@ECHO OFF
XCOPY .\*.py .\dist\Python\ /y
XCOPY .\*.cfg .\dist\Python\ /y
XCOPY .\Utilities\*.py .\dist\Python\Utilities\ /iy
XCOPY .\Setups\*.py .\dist\Python\Setups\ /iy
XCOPY .\Networking\*.py .\dist\Python\Networking\ /iy
XCOPY .\Documentation\*.py .\dist\Python\Documentation\ /iy
XCOPY .\Documentation\*.mel .\dist\Python\Documentation\ /iy
XCOPY .\Dialogs\*.py .\dist\Python\Dialogs\ /iy
XCOPY .\CompiledUI\*.py .\dist\Python\CompiledUI\ /iy
XCOPY .\Images .\dist\Python\Images\ /isy
PAUSE
