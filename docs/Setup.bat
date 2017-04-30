@ECHO OFF
ECHO This script will help you setup the python enviroment for DPS_Hydra
PAUSE

:PythonInstall
ECHO.
python -c ""
IF NOT %ERRORLEVEL% == 1 GOTO PipCheck
	ECHO.
	ECHO Download and install Python 2.7 32 bit and try again.
	PAUSE
	GOTO :EOF

:PipCheck
ECHO.
pip freeze
IF NOT %ERRORLEVEL% == 1 GOTO :PyQtCheck
	ECHO.
	ECHO Download and install Pip for your version of Python. If installed make sure it is in your system PATH variable.
	PAUSE
	GOTO :EOF

:PyQtCheck
ECHO.
python -c "import PyQt4"
IF NOT %ERRORLEVEL% == 1 GOTO :MySQLCheck
	ECHO.
	ECHO Download and install PyQt4 from http://www.lfd.uci.edu/~gohlke/pythonlibs/#pyqt4 and install using "pip install C:/Path/To/whl File"
	PAUSE
	GOTO :EOF

:MySQLCheck
ECHO.
python -c "import MySQLdb"
IF NOT %ERRORLEVEL% == 1 GOTO :InstallReqs
	ECHO.
	ECHO Download and install MySQL from http://www.lfd.uci.edu/~gohlke/pythonlibs/#mysql-python and install using "pip install C:/Path/To/whl File"
	PAUSE
	GOTO :EOF

:InstallReqs
ECHO.
pip install -r requirements.txt
IF NOT %ERRORLEVEL% == 1 GOTO :Done
	ECHO.
	ECHO Error. Pip could not install all of the requirements for some reason.
	PAUSE
	GOTO :EOF

:Done
ECHO.
ECHO Done setting up enviroment for DPS_Hydra!
PAUSE