@ECHO OFF
::START
::python -m pip install -U Red-DiscordBot
python -O -m redbot nword

::IF %ERRORLEVEL% == 1 GOTO RESTART
::IF %ERRORLEVEL% == 26 GOTO RESTART
::EXIT /B %ERRORLEVEL%

::RESTART
::ECHO Restarting...
::GOTO START