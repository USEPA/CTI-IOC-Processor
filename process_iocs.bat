@ECHO OFF
SETLOCAL
set output_dir="%~dp0output\%date:~-4,4%-%date:~-10,2%-%date:~-7,2%"
process_iocs.exe
echo.
echo Opening the output directory
echo ioc_summary.txt contains the list of IOCs
start explorer.exe "%output_dir%"
ENDLOCAL
pause>nul|set/p =Press any key to exit ...