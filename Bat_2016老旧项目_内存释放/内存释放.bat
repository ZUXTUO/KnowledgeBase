@echo off
mode con cols=40 lines=10
title �ڴ������
echo ��������ž���
:a
empty *>nul
empty %%~a>nul
empty.exe task-*>nul
ping 127.0.0.1 -n 10 >nul
goto a