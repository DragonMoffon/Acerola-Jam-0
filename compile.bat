@echo off
%~dp0\libs\Scripts\python.exe -m nuitka --windows-force-stderr-spec=error_output.txt --remove-output --standalone --output-filename=optics %~dp0\engine >output.txt
