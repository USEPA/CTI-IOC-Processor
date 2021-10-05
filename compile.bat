@ECHO OFF
REM Compile process_iocs.py into a .exe file for Windows
REM Use the option --collect-submodules cybox to
REM force pyinstaller to include all cybox modules to avoid
REM runtime errors when processing cybox tags in the XML files
pyinstaller --onefile --collect-submodules cybox process_iocs.py