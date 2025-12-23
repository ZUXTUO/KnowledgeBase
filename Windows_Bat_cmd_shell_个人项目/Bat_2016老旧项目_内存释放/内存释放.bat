@echo off
mode con cols=40 lines=10
title 内存加速器
echo 本程序挂着就行
:a
empty *>nul
empty %%~a>nul
empty.exe task-*>nul
ping 127.0.0.1 -n 10 >nul
goto a