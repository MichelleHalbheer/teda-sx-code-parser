@ECHO OFF
COPY "%~1" "H:\Software\Trimble Line Code Parser\Input" /-y
pushd "H:\Software\Trimble Line Code Parser"
START /WAIT "Trimble Line Code Converter" "H:\Software\Trimble Line Code Parser\Trimble_Line_Code_Converter.exe"
popd
COPY "H:\Software\Trimble Line Code Parser\Output\%~nx1" "%~1" /y
