@ECHO OFF

@REM Push the directory of the code to make it active
PUSHD "H:\Software\Trimble_Line_Code_Parser"

@REM Start the progra and pass the path of the input file as a system argument
START /WAIT "Trimble Line Code Converter" ".\\Trimble_Line_Code_Converter.exe" "%~1"

@REM Pop the directory to return to the original directory of execution
POPD