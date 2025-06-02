@echo off & color 1b & setlocal enabledelayedexpansion & set
:load
echo ��ӭʹ�ü�����������>news.BDR
title ���������������V1.1
if exist "animation.BDR" goto animation ) else (goto maxice51236)

:maxice51236
 mode con cols=48 lines=17
Set HomeDrive=C:
Set WinDir=%HomeDrive%\WINDOWS
Set SysDir=%WinDir%\System32
Set ProgFile=%HomeDrive%\Program Files
Set CurUser=%HomeDrive%\Documents and Settings\Administrator
Set AllUser=%HomeDrive%\Documents and Settings\All Users
set st=%time%
set /p systemen=<system.BDR
set /p news=<news.BDR
if "%PROCESSOR_ARCHITECTURE%"=="x86" goto X86
if "%PROCESSOR_ARCHITECTURE%"=="AMD64" goto X64

:x86
set xitongweishu=32λ
goto varxitong

:x64
set xitongweishu=64λ
goto varxitong

:varxitong
ver | find "1.04." > NUL &&  goto win1
ver | find "2.11." > NUL &&  goto win2
ver | find "3." > NUL &&  goto win3
ver | find "3.10.528." > NUL &&  goto winnt3
ver | find "3.11." > NUL &&  goto win311
ver | find "3.5.807." > NUL &&  goto win35
ver | find "3.51.1057." > NUL &&  goto win351
ver | find "4.0.950." > NUL &&  goto win95
ver | find "4.0.1381." > NUL &&  goto winnt4
ver | find "4.1.1998." > NUL &&  goto win98
ver | find "4.1.2222." > NUL &&  goto win98s
ver | find "4.90.3000." > NUL &&  goto winme
ver | find "5.0." > NUL &&  goto win2000
ver | find "5.1." > NUL &&  goto winxp
ver | find "5.2.3790." > NUL &&  goto winxpp
ver | find "5.2." > NUL &&  goto wins3
ver | find "6.0.6000." > NUL &&  goto winvs
ver | find "6.0." > NUL &&  goto wins2008
ver | find "6.1." > NUL &&  goto wins2008r2
ver | find "6.1." > NUL &&  goto win7
ver | find "6.2." > NUL &&  goto win8
ver | find "6.4." > NUL &&  goto win10
ver | find "10.0." > NUL &&  goto win10


:ilovejy
set systemen=��
echo %systemen%>>system.BDR
goto maxice

:win1
set systemen=Windows 1.0
echo %systemen%>>system.BDR
goto maxice

:win2
set systemen=Windows 2.0
echo %systemen%>>system.BDR
goto maxice

:win3
set systemen=Windows 3.0
echo %systemen%>>system.BDR
goto maxice

:winnt3
set systemen=Windows NT 3.1
echo %systemen%>>system.BDR
goto maxice

:win311
set systemen=Windows for Workgroups 3.11
echo %systemen%>>system.BDR
goto maxice

:win35
set systemen=Windows NT Workstation 3.5
echo %systemen%>>system.BDR
goto maxice

:win351
set systemen=Windows NT Workstation 3.51
echo %systemen%>>system.BDR
goto maxice

:win95
set systemen=Windows 95
echo %systemen%>>system.BDR
goto maxice

:winnt4
set systemen=Windows NT Workstation 4.0
echo %systemen%>>system.BDR
goto maxice

:win98
set systemen=Windows 98
echo %systemen%>>system.BDR
goto maxice

:win98s
set systemen=Windows 98 Second Edition
echo %systemen%>>system.BDR
goto maxice

:winme
set systemen=Windows Me
echo %systemen%>>system.BDR
goto maxice

:win2000
set systemen=Windows 2000 Professional
echo %systemen%>>system.BDR
goto maxice

:winxp
set systemen=Windows XP
echo %systemen%>>system.BDR
goto maxice

:winxpp
set systemen=Windows XP Professional x64 Edition
echo %systemen%>>system.BDR
goto maxice

:wins3
set systemen=Windows Server 2003
echo %systemen%>>system.BDR
goto maxice

:winvs
set systemen=Windows Vista
echo %systemen%>>system.BDR
goto maxice

:wins2008
set systemen=Windows Server 2008
echo %systemen%>>system.BDR
goto maxice

:wins2008r2
set systemen=Windows Server 2008 R2
echo %systemen%>>system.BDR
goto maxice

:win7
set systemen=Windows 7
echo %systemen%>>system.BDR
goto maxice

:win8
set systemen=Windows 8
echo %systemen%>>system.BDR
goto maxice

:win10
set systemen=Windows 10
echo %systemen%>>system.BDR
goto maxice


:maxice
title ���������������V1.1
cls
cd /d save\money.BDR
cd /d save\system.BDR
cd /d save\news.BDR
cls
echo ��Ϣ�� %news%
echo ------------------------------------------------
echo                                  ��ǰ�汾��V1.1
echo                   ��    ��   
echo                 ���ߩ����ߩ�     
echo                 ��        ��      
echo                 �� ��  �� ��      
echo                 ��        ��             
echo                 ������������     
echo  ���ϵͳ��%systemen% %xitongweishu%
echo                                �����ߣ�����
echo  �������������1  ������������2  ����������3
echo                ��������������4
set choice= 
set /p choice=����������ָ�
if /i '%choice%'=='1' goto tijian123

if /i '%choice%'=='2' goto putongqingli 

if /i '%choice%'=='3' goto tools520

if /i '%choice%'=='4' goto fankuion

if /i '%choice%'=='greeneyes' goto greeneyes

if /i '%choice%'=='HI' goto mingxuanshu1

if /i '%choice%'=='HELLO' goto mingxuanshu1


:mingxuanshu
set news=δ��ʶ������ָ���
cls
goto maxice


:mingxuanshu1
set news=���ã����ǻ�����С��
cls
goto maxice

:animation
mode con cols=65 lines=33
cls
echo.
echo                                ��
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo                               ����
ping -n 1 127.1>nul
cls
echo.
echo                                ��
echo                             ��������
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo                             ��������
echo                               ����
ping -n 1 127.1>nul
cls
echo.
echo                                ��
echo                             ��������
echo                          ������  ������
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo                           ����    ����
echo                             ��������
echo                               ����
ping -n 1 127.1>nul
cls
echo.
echo                                ��
echo                             ��������
echo                          ������  ������
echo      ������������������������      ������������������������
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo          ������������������         ������������������
echo                           ����    ����
echo                             ��������
echo                               ����
ping -n 1 127.1>nul
cls
echo.
echo                                ��
echo                             ��������
echo                          ������  ������
echo      ������������������������      ������������������������
echo       ����          ������            ������          ����
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo          ����        ����             ����        ����
echo          ������������������         ������������������
echo                           ����    ����
echo                             ��������
echo                               ����
ping -n 1 127.1>nul
cls
echo.
echo                                ��
echo                             ��������
echo                          ������  ������
echo      ������������������������      ������������������������
echo       ����          ������            ������          ����
echo        ����        ����                  ����        ����
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo          ����      ����                 ����      ����
echo          ����        ����             ����        ����
echo          ������������������         ������������������
echo                           ����    ����
echo                             ��������
echo                               ����
ping -n 1 127.1>nul
cls
echo.
echo                                ��
echo                             ��������
echo                          ������  ������
echo      ������������������������      ������������������������
echo       ����          ������            ������          ����
echo        ����        ����                  ����        ����
echo          ����     ����                     ����     ����
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo          ����     ����                    ����    ����
echo          ����      ����                 ����      ����
echo          ����        ����             ����        ����
echo          ������������������         ������������������
echo                           ����    ����
echo                             ��������
echo                               ����
ping -n 1 127.1>nul
cls
echo.
echo                                ��
echo                             ��������
echo                          ������  ������
echo      ������������������������      ������������������������
echo       ����          ������            ������          ����
echo        ����        ����                  ����        ����
echo          ����     ����                    ����     ����
echo            ����  ����                       ����  ����
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo          ����   ����                       ����   ����
echo          ����     ����                    ����    ����
echo          ����      ����                 ����      ����
echo          ����        ����             ����        ����
echo          ������������������         ������������������
echo                           ����    ����
echo                             ��������
echo                               ����
ping -n 1 127.1>nul
cls
echo.
echo                                ��
echo                             ��������
echo                          ������  ������
echo      ������������������������      ������������������������
echo       ����          ������            ������          ����
echo        ����        ����                  ����        ����
echo          ����     ����                    ����     ����
echo            ����  ��                          ����  ��
echo             ������                            ������
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo          ����  ����                         ����  ����
echo          ����   ����                       ����   ����
echo          ����     ����                    ����    ����
echo          ����      ����                 ����      ����
echo          ����        ����             ����        ����
echo          ������������������         ������������������
echo                           ����    ����
echo                             ��������
echo                               ����
ping -n 1 127.1>nul
cls
echo.
echo                                ��
echo                             ��������
echo                          ������  ������
echo      ������������������������      ������������������������
echo       ����          ������            ������          ����
echo        ����        ����                  ����        ����
echo          ����     ����                    ����     ����
echo            ����  ��                          ����  ��
echo             ������                            ������
echo           ������                                ������
echo.
echo.
echo.
echo                                ��
echo                                ��
echo.
echo.
echo.
echo.
echo          ��������                             ��������
echo          ����  ����                         ����  ����
echo          ����   ����                       ����   ����
echo          ����     ����                    ����    ����
echo          ����      ����                 ����      ����
echo          ����        ����             ����        ����
echo          ������������������         ������������������
echo                           ����    ����
echo                             ��������
echo                               ����
ping -n 1 127.1>nul
cls
echo.
echo                                ��
echo                             ��������
echo                          ������  ������
echo      ������������������������      ������������������������
echo       ����          ������            ������          ����
echo        ����        ����                  ����        ����
echo          ����     ����                    ����     ����
echo            ����  ��                          ����  ��
echo             ������                            ������
echo           ������                                ������
echo.
echo.
echo                               ����
echo                                ��
echo                                ��
echo                               ����
echo.
echo.
echo.
echo          ��������                             ��������
echo          ����  ����                         ����  ����
echo          ����   ����                       ����   ����
echo          ����     ����                    ����    ����
echo          ����      ����                 ����      ����
echo          ����        ����             ����        ����
echo          ������������������         ������������������
echo                           ����    ����
echo                             ��������
echo                               ����
ping -n 1 127.1>nul
cls
echo.
echo                                ��
echo                             ��������
echo                          ������  ������
echo      ������������������������      ������������������������
echo       ����          ������            ������          ����
echo        ����        ����                  ����        ����
echo          ����     ����                    ����     ����
echo            ����  ��                          ����  ��
echo             ������                            ������
echo           ������                                ������
echo         ������                                    ������
echo.
echo                               ����
echo                              ������
echo                              ������
echo                               ����
echo.
echo.
echo.
echo          ��������                             ��������
echo          ����  ����                         ����  ����
echo          ����   ����                       ����   ����
echo          ����     ����                    ����    ����
echo          ����      ����                 ����      ����
echo          ����        ����             ����        ����
echo          ������������������         ������������������
echo                           ����    ����
echo                             ��������
echo                               ����
ping -n 1 127.1>nul
cls
echo.
echo                                ��
echo                             ��������
echo                          ������  ������
echo      ������������������������      ������������������������
echo       ����          ������            ������          ����
echo        ����        ����                  ����        ����
echo          ����     ����                    ����     ����
echo            ����  ��                          ����  ��
echo             ������                            ������
echo           ������                                ������
echo         ������                                    ������
echo.
echo                               ����
echo                            ����������
echo                            ����������
echo                               ����
echo.
echo.
echo          ������                                 ������
echo          ��������                             ��������
echo          ����  ����                         ����  ����
echo          ����   ����                       ����   ����
echo          ����     ����                    ����    ����
echo          ����      ����                 ����      ����
echo          ����        ����             ����        ����
echo          ������������������         ������������������
echo                           ����    ����
echo                             ��������
echo                               ����
ping -n 1 127.1>nul
cls
echo.
echo                                ��
echo                             ��������
echo                          ������  ������
echo      ������������������������      ������������������������
echo       ����          ������            ������          ����
echo        ����        ����                  ����        ����
echo          ����     ����                    ����     ����
echo            ����  ��                          ����  ��
echo             ������                            ������
echo           ������                                ������
echo         ������                                    ������
echo.
echo                               ����
echo                          ��������������
echo                          ��������������
echo                               ����
echo.
echo.
echo          ������                                 ������
echo          ��������                             ��������
echo          ����  ����                         ����  ����
echo          ����   ����                       ����   ����
echo          ����     ����                    ����    ����
echo          ����      ����                 ����      ����
echo          ����        ����             ����        ����
echo          ������������������         ������������������
echo                           ����    ����
echo                             ��������
echo                               ����
ping -n 1 127.1>nul
cls
echo.
echo                                ��
echo                             ��������
echo                          ������  ������
echo      ������������������������      ������������������������
echo       ����          ������            ������          ����
echo        ����        ����                  ����        ����
echo          ����     ����                    ����     ����
echo            ����  ��                          ����  ��
echo             ������                            ������
echo           ������                                ������
echo         ������                                    ������
echo                               ����
echo                               ����
echo                        ������������������
echo                        ������������������
echo                               ����
echo.
echo.
echo          ������                                 ������
echo          ��������                             ��������
echo          ����  ����                         ����  ����
echo          ����   ����                       ����   ����
echo          ����     ����                    ����    ����
echo          ����      ����                 ����      ����
echo          ����        ����             ����        ����
echo          ������������������         ������������������
echo                           ����    ����
echo                             ��������
echo                               ����
ping -n 1 127.1>nul
cls
echo.
echo                                ��
echo                             ��������
echo                          ������  ������
echo      ������������������������      ������������������������
echo       ����          ������            ������          ����
echo        ����        ����                  ����        ����
echo          ����     ����                    ����     ����
echo            ����  ��                          ����  ��
echo             ������                            ������
echo           ������                                ������
echo         ������                                    ������
echo                               ����
echo                               ����
echo                      ����������������������
echo                      ����������������������
echo                               ����
echo.
echo        ������                                     ������
echo          ������                                 ������
echo          ��������                             ��������
echo          ����  ����                         ����  ����
echo          ����   ����                       ����   ����
echo          ����     ����                    ����    ����
echo          ����      ����                 ����      ����
echo          ����        ����             ����        ����
echo          ������������������         ������������������
echo                           ����    ����
echo                             ��������
echo                               ����
ping -n 1 127.1>nul
cls
echo.
echo                                ��
echo                             ��������
echo                          ������  ������
echo      ������������������������      ������������������������
echo       ����          ������            ������          ����
echo        ����        ����                  ����        ����
echo          ����     ����                    ����     ����
echo            ����  ��                          ����  ��
echo             ������                            ������
echo           ������                                ������
echo         ������                                    ������
echo       ������                  ����                  ������
echo                               ����
echo                    ��������������������������
echo                    ��������������������������
echo                               ����
echo      ������                   ����                  ������
echo        ������                                     ������
echo          ������                                 ������
echo          ��������                             ��������
echo          ����  ����                         ����  ����
echo          ����   ����                       ����   ����
echo          ����     ����                    ����    ����
echo          ����      ����                 ����      ����
echo          ����        ����             ����        ����
echo          ������������������         ������������������
echo                           ����    ����
echo                             ��������
echo                               ����
ping -n 1 127.1>nul
cls
echo.
echo                                ��
echo                             ��������
echo                          ������  ������
echo      ������������������������      ������������������������
echo       ����          ������            ������          ����
echo        ����        ����                  ����        ����
echo          ����     ����                    ����     ����
echo            ����  ��                          ����  ��
echo             ������                            ������
echo           ������                                ������
echo         ������                ����                ������
echo       ������                  ����                  ������
echo                               ����
echo                    ��������������������������
echo                    ��������������������������
echo                               ����
echo       ������                  ����                  ������
echo         ������                ����                ������
echo          ������                                 ������
echo          ��������                             ��������
echo          ����  ����                         ����  ����
echo          ����   ����                       ����   ����
echo          ����     ����                    ����    ����
echo          ����      ����                 ����      ����
echo          ����        ����             ����        ����
echo          ������������������         ������������������
echo                           ����    ����
echo                             ��������
echo                               ����
ping -n 1 127.1>nul
cls
echo.
echo                                ��
echo                             ��������
echo                          ������  ������
echo      ������������������������      ������������������������
echo       ����          ������            ������          ����
echo        ����        ����                  ����        ����
echo          ����     ����                    ����     ����
echo            ����  ��                          ����  ��
echo             ������                            ������
echo           ������              ����              ������
echo         ������                ����                ������
echo       ������                  ����                  ������
echo                               ����
echo                  ������������������������������
echo                  ������������������������������
echo                               ����
echo       ������                  ����                  ������
echo         ������                ����                ������
echo          ������               ����              ������
echo          ��������                             ��������
echo          ����  ����                         ����  ����
echo          ����   ����                       ����   ����
echo          ����     ����                    ����    ����
echo          ����      ����                 ����      ����
echo          ����        ����             ����        ����
echo          ������������������         ������������������
echo                           ����    ����
echo                             ��������
echo                               ����
ping -n 1 127.1>nul
cls
echo.
echo                                ��
echo                             ��������
echo                          ������  ������
echo      ������������������������      ������������������������
echo       ����          ������            ������          ����
echo        ����        ����                  ����        ����
echo          ����     ����                    ����     ����
echo            ����  ��                          ����  ��
echo             ������            ����            ������
echo           ������              ����              ������
echo         ������                ����                ������
echo       ������                  ����                  ������
echo                               ����
echo                ����������������������������������
echo                ����������������������������������
echo                               ����
echo       ������                  ����                  ������
echo         ������                ����                ������
echo          ������               ����              ������
echo          ��������             ����            ��������
echo          ����  ����                         ����  ����
echo          ����   ����                       ����   ����
echo          ����     ����                    ����    ����
echo          ����      ����                 ����      ����
echo          ����        ����             ����        ����
echo          ������������������         ������������������
echo                           ����    ����
echo                             ��������
echo                               ����
ping -n 1 127.1>nul
cls
echo.
echo                                ��
echo                             ��������
echo                          ������  ������
echo      ������������������������      ������������������������
echo       ����          ������            ������          ����
echo        ����        ����                  ����        ����
echo          ����     ����                    ����     ����
echo            ����  ��           ����           ����  ��
echo             ������            ����            ������
echo           ������              ����              ������
echo         ������                ����                ������
echo       ������                  ����                  ������
echo                               ����
echo              ��������������������������������������
echo              ��������������������������������������
echo                               ����
echo       ������                  ����                  ������
echo         ������                ����                ������
echo          ������               ����              ������
echo          ��������             ����            ��������
echo          ����  ����           ����          ����  ����
echo          ����   ����                       ����   ����
echo          ����     ����                    ����    ����
echo          ����      ����                 ����      ����
echo          ����        ����             ����        ����
echo          ������������������         ������������������
echo                           ����    ����
echo                             ��������
echo                               ����
ping -n 1 127.1>nul
cls
echo.
echo                                ��
echo                             ��������
echo                          ������  ������
echo      ������������������������      ������������������������
echo       ����          ������            ������          ����
echo        ����        ����                  ����        ����
echo          ����     ����        ����        ����     ����
echo            ����  ��           ����           ����  ��
echo             ������            ����            ������
echo           ������              ����              ������
echo         ������                ����                ������
echo       ������                  ����                  ������
echo                               ����
echo              ��������������������������������������
echo              ��������������������������������������
echo                               ����
echo       ������                  ����                  ������
echo         ������                ����                ������
echo          ������               ����              ������
echo          ��������             ����            ��������
echo          ����  ����           ����          ����  ����
echo          ����   ����          ����         ����   ����
echo          ����     ����                    ����    ����
echo          ����      ����                 ����      ����
echo          ����        ����             ����        ����
echo          ������������������         ������������������
echo                           ����    ����
echo                             ��������
echo                               ����
ping -n 1 127.1>nul
cls
echo.
echo                                ��
echo                             ��������
echo                          ������  ������
echo      ������������������������      ������������������������
echo       ����          ������            ������          ����
echo        ����        ����                  ����        ����
echo          ����     ����        ����        ����     ����
echo            ����  ��           ����           ����  ��
echo             ������            ����            ������
echo           ������              ����              ������
echo         ������                ����                ������
echo       ������                  ����                  ������
echo                               ����
echo              ��������������������������������������
echo              ��������������������������������������
echo                               ����
echo       ������                  ����                  ������
echo         ������                ����                ������
echo          ������               ����              ������
echo          ��������             ����            ��������
echo          ����  ����           ����          ����  ����
echo          ����   ����          ����         ����   ����
echo          ����     ����                    ����    ����
echo          ����      ����                 ����      ����
echo          ����        ����             ����        ����
echo          ������������������         ������������������
echo                           ����    ����
echo                             ��������
echo                               ����
ping -n 1 127.1>nul
cls
echo.
echo                                ��
echo                             ��������
echo                          ������  ������
echo      ������������������������      ������������������������
echo       ����          ������            ������          ����
echo        ����        ����       ����       ����        ����
echo          ����     ����        ����        ����     ����
echo            ����  ��           ����           ����  ��
echo             ������            ����            ������
echo           ������              ����              ������
echo         ������                ����                ������
echo       ������                  ����                  ������
echo                               ����
echo              ��������������������������������������
echo              ��������������������������������������
echo                               ����
echo       ������                  ����                  ������
echo         ������                ����                ������
echo          ������               ����              ������
echo          ��������             ����            ��������
echo          ����  ����           ����          ����  ����
echo          ����   ����          ����         ����   ����
echo          ����     ����        ����        ����    ����
echo          ����      ����                 ����      ����
echo          ����        ����             ����        ����
echo          ������������������         ������������������
echo                           ����    ����
echo                             ��������
echo                               ����
ping -n 1 127.1>nul
cls
echo.
echo                                ��
echo                             ��������
echo                          ������  ������
echo      ������������������������      ������������������������
echo       ����          ������            ������          ����
echo        ����        ����       ����       ����        ����
echo          ����     ����        ����        ����     ����
echo            ����  ��           ����           ����  ��
echo             ������            ����            ������
echo           ������              ����              ������
echo         ������                ����                ������
echo       ������                  ����                  ������
echo                               ����
echo            ������������������������������������������
echo            ������������������������������������������
echo                               ����
echo       ������                  ����                  ������
echo         ������                ����                ������
echo          ������               ����              ������
echo          ��������             ����            ��������
echo          ����  ����           ����          ����  ����
echo          ����   ����          ����         ����   ����
echo          ����     ����        ����        ����    ����
echo          ����      ����                 ����      ����
echo          ����        ����             ����        ����
echo          ������������������         ������������������
echo                           ����    ����
echo                             ��������
echo                               ����
ping -n 1 127.1>nul
cls
echo.
echo                                ��
echo                             ��������
echo                          ������  ������
echo      ������������������������      ������������������������
echo       ����          ������            ������          ����
echo        ����        ����       ����       ����        ����
echo          ����     ����        ����        ����     ����
echo            ����  ��           ����           ����  ��
echo             ������            ����            ������
echo           ������              ����              ������
echo         ������                ����                ������
echo       ������                  ����                  ������
echo                               ����
echo            ������������������������������������������
echo            ������������������������������������������
echo                               ����
echo       ������                  ����                  ������
echo         ������                ����                ������
echo          ������               ����              ������
echo          ��������             ����            ��������
echo          ����  ����           ����          ����  ����
echo          ����   ����          ����         ����   ����
echo          ����     ����        ����        ����    ����
echo          ����      ����                 ����      ����
echo          ����        ����             ����        ����
echo          ������������������         ������������������
echo                           ����    ����
echo                             ��������
echo                               ����
ping -n 1 127.1>nul
cls
echo.
echo                                ��
echo                             ��������
echo                          ������  ������
echo      ������������������������      ������������������������
echo       ����          ������            ������          ����
echo        ����        ����       ����       ����        ����
echo          ����     ����        ����        ����     ����
echo            ����  ��           ����           ����  ��
echo             ������            ����            ������
echo           ������              ����              ������
echo         ������                ����                ������
echo       ������                  ����                  ������
echo     ������                    ����                    ������
echo            ������������������������������������������
echo            ������������������������������������������
echo     ������                    ����                    ������
echo       ������                  ����                  ������
echo         ������                ����                ������
echo          ������               ����              ������
echo          ��������             ����            ��������
echo          ����  ����           ����          ����  ����
echo          ����   ����          ����         ����   ����
echo          ����     ����        ����        ����    ����
echo          ����      ����                 ����      ����
echo          ����        ����             ����        ����
echo          ������������������         ������������������
echo                           ����    ����
echo                             ��������
echo                               ����
ping -n 1 127.1>nul
cls
echo.
echo                                ��
echo                             ��������
echo                          ������  ������
echo      ������������������������      ������������������������
echo       ����          ������            ������          ����
echo        ����        ����       ����       ����        ����
echo          ����     ����        ����        ����     ����
echo            ����  ��           ����           ����  ��
echo             ������            ����            ������
echo           ������              ����              ������
echo         ������                ����                ������
echo       ������                  ����                  ������
echo     ������                    ����                    ������
echo       ��   ������������������������������������������   ��
echo            ������������������������������������������
echo     ������                    ����                    ������
echo       ������                  ����                  ������
echo         ������                ����                ������
echo          ������               ����              ������
echo          ��������             ����            ��������
echo          ����  ����           ����          ����  ����
echo          ����   ����          ����         ����   ����
echo          ����     ����        ����        ����    ����
echo          ����      ����                 ����      ����
echo          ����        ����             ����        ����
echo          ������������������         ������������������
echo                           ����    ����
echo                             ��������
echo                               ����
ping -n 1 127.1>nul
cls
echo.
echo                                ��
echo                             ��������
echo                          ������  ������
echo      ������������������������      ������������������������
echo       ����          ������            ������          ����
echo        ����        ����       ����       ����        ����
echo          ����     ����        ����        ����     ����
echo            ����  ��           ����           ����  ��
echo             ������            ����            ������
echo           ������              ����              ������
echo         ������                ����                ������
echo       ������                  ����                  ������
echo     ������                    ����                    ������
echo       ��   ������������������������������������������   ��
echo       ��   ������������������������������������������   ��
echo     ������                    ����                    ������
echo       ������                  ����                  ������
echo         ������                ����                ������
echo          ������               ����              ������
echo          ��������             ����            ��������
echo          ����  ����           ����          ����  ����
echo          ����   ����          ����         ����   ����
echo          ����     ����        ����        ����    ����
echo          ����      ����                 ����      ����
echo          ����        ����             ����        ����
echo          ������������������         ������������������
echo                           ����    ����
echo                             ��������
echo                               ����
ping -n 1 127.1>nul
cls
echo.
echo                                ��
echo                             ��������
echo                          ������  ������
echo      ������������������������      ������������������������
echo       ����          ������            ������          ����
echo        ����        ����       ����       ����        ����
echo          ����     ����        ����        ����     ����
echo            ����  ��           ����           ����  ��
echo             ������            ����            ������
echo           ������              ����              ������
echo         ������                ����                ������
echo       ������                  ����                  ������
echo     ������                    ����                    ������
echo     ����   ������������������������������������������    ����
echo     ����   ������������������������������������������    ����
echo     ������                    ����                    ������
echo       ������                  ����                  ������
echo         ������                ����                ������
echo          ������               ����              ������
echo          ��������             ����            ��������
echo          ����  ����           ����          ����  ����
echo          ����   ����          ����         ����   ����
echo          ����     ����        ����        ����    ����
echo          ����      ����       ����      ����      ����
echo          ����        ����             ����        ����
echo          ������������������         ������������������
echo                           ����    ����
echo                             ��������
echo                               ����
ping -n 1 127.1>nul
cls
echo.
echo                                ��
echo                             ��������
echo                          ������  ������
echo      ������������������������      ������������������������
echo       ����          ������            ������          ����
echo        ����        ����       ����       ����        ����
echo          ����     ����        ����        ����     ����
echo            ����  ��           ����           ����  ��
echo             ������            ����            ������
echo           ������              ����              ������
echo         ������                ����                ������
echo       ������                  ����                  ������
echo     ������                    ����                    ������
echo   ������   ������������������������������������������    ������
echo   ������   ������������������������������������������    ������
echo     ������                    ����                    ������
echo       ������                  ����                  ������
echo         ������                ����                ������
echo          ������               ����              ������
echo          ��������             ����            ��������
echo          ����  ����           ����          ����  ����
echo          ����   ����          ����         ����   ����
echo          ����     ����        ����        ����    ����
echo          ����      ����       ����      ����      ����
echo          ����        ����             ����        ����
echo          ������������������         ������������������
echo                           ����    ����
echo                             ��������
echo                               ����
ping -n 1 127.1>nul
cls
echo.
echo                                ��
echo                             ��������
echo                          ������  ������
echo      ������������������������      ������������������������
echo       ����          ������            ������          ����
echo        ����        ����       ����       ����        ����
echo          ����     ����        ����        ����     ����
echo            ����  ��           ����           ����  ��
echo             ������            ����            ������
echo           ������              ����              ������
echo         ������                ����                ������
echo       ������                  ����                  ������
echo     ������                    ����                    ������
echo   ������   ������������������������������������������    ������
echo   ������   ������������������������������������������    ������
echo     ������                    ����                    ������
echo       ������                  ����                  ������
echo         ������                ����                ������
echo          ������               ����              ������
echo          ��������             ����            ��������
echo          ����  ����           ����          ����  ����
echo          ����   ����          ����         ����   ����
echo          ����     ����        ����        ����    ����
echo          ����      ����       ����      ����      ����
echo          ����        ����             ����        ����
echo          ������������������         ������������������
echo                           ����    ����
echo                             ��������
echo                               ����
ping -n 1 127.1>nul
cls
echo.
echo                                ��
echo                             ��������
echo                          ������  ������
echo      ������������������������      ������������������������
echo       ����          ������            ������          ����
echo        ����        ����       ����       ����        ����
echo          ����     ����        ����        ����     ����
echo            ����  ��           ����           ����  ��
echo             ������            ����            ������
echo           ������              ����              ������
echo         ������                ����                ������
echo       ������                  ����                  ������
echo     ������                    ����                    ������
echo   ������   ������������������������������������������    ������
echo   ������   ������������������������������������������    ������
echo     ������                    ����                    ������
echo       ������                  ����                  ������
echo         ������                ����                ������
echo          ������               ����              ������
echo          ��������             ����            ��������
echo          ����  ����           ����          ����  ����
echo          ����   ����          ����         ����   ����
echo          ����     ����        ����        ����    ����
echo          ����      ����       ����      ����      ����
echo          ����        ����             ����        ����
echo          ������������������         ������������������
echo                           ����    ����
echo                             ��������
echo                               ����
ping -n 1 127.1>nul
cls
echo.
echo                                ��
echo                             ��������
echo                          ������  ������
echo      ������������������������      ������������������������
echo       ����          ������            ������          ����
echo        ����        ����       ����       ����        ����
echo          ����     ����        ����        ����     ����
echo            ����  ��           ����           ����  ��
echo             ������            ����            ������
echo           ������              ����              ������
echo         ������                ����                ������
echo       ������                  ����                  ������
echo     ������                    ����                    ������
echo   ������   ������������������������������������������    ������
echo   ������   ������������������������������������������    ������
echo     ������                    ����                    ������
echo       ������                  ����                  ������
echo         ������                ����                ������
echo          ������               ����              ������
echo          ��������             ����            ��������
echo          ����  ����           ����          ����  ����
echo          ����   ����          ����         ����   ����
echo          ����     ����        ����        ����    ����
echo          ����      ����       ����      ����      ����
echo          ����        ����             ����        ����
echo          ������������������         ������������������
echo                           ����    ����
echo                             ��������
echo                               ����
ping -n 1 127.1>nul
cls
echo.
echo                                ��
echo                             ��������
echo                          ������  ������
echo      ������������������������      ������������������������
echo       ����          ������            ������          ����
echo        ����        ����       ����       ����        ����
echo          ����     ����        ����        ����     ����
echo            ����  ��           ����           ����  ��
echo             ������            ����            ������
echo           ������              ����              ������
echo         ������                ����                ������
echo       ������                  ����                  ������
echo     ������                    ����                    ������
echo   ������   ������������������������������������������    ������
echo   ������   ������������������������������������������    ������
echo     ������                    ����                    ������
echo       ������                  ����                  ������
echo         ������                ����                ������
echo          ������               ����              ������
echo          ��������             ����            ��������
echo          ����  ����           ����          ����  ����
echo          ����   ����          ����         ����   ����
echo          ����     ����        ����        ����    ����
echo          ����      ����       ����      ����      ����
echo          ����        ����             ����        ����
echo          ������������������         ������������������
echo                           ����    ����
echo                             ��������
echo                               ����
ping -n 1 127.1>nul
cls
echo.
echo                                ��
echo                             ��������
echo                          ������  ������
echo      ������������������������      ������������������������
echo       ����          ������            ������          ����
echo        ����        ����       ����       ����        ����
echo          ����     ����        ����        ����     ����
echo            ����  ��           ����           ����  ��
echo             ������            ����            ������
echo           ������              ����              ������
echo         ������                ����                ������
echo       ������                  ����                  ������
echo     ������                    ����                    ������
echo   ������   ������������������������������������������    ������
echo   ������   ������������������������������������������    ������
echo     ������                    ����                    ������
echo       ������                  ����                  ������
echo         ������                ����                ������
echo          ������               ����              ������
echo          ��������             ����            ��������
echo          ����  ����           ����          ����  ����
echo          ����   ����          ����         ����   ����
echo          ����     ����        ����        ����    ����
echo          ����      ����       ����      ����      ����
echo          ����        ����             ����        ����
echo          ������������������         ������������������
echo                           ����    ����
echo                             ��������
echo                               ����
ping -n 1 127.1>nul
echo                       ��ӭʹ�ü���������
ping -n 3 127.1>nul
goto maxice51236

:fankuion
set news=�������䣺mr.dawei@outlook.com
cls
goto maxice


:greeneyes
color 29
set news=����ģʽ��������
cls
goto maxice

:putongqingli
cls
Rd /s/q "%AllUser%\Documents\My Videos
Rd /s/q "%AllUser%\Documents\My Pictures
Rd /s/q "%AllUser%\Documents\My Music
cls
Rd /s/q "%ProgFile%\Windows Media Player\Icons
Rd /s/q "%ProgFile%\Windows Media Player\Sample Playlists
Rd /s/q "%ProgFile%\Windows Media Player\Skins
Rd /s/q "%ProgFile%\Windows Media Player\Vis lizations
Del /a/f/s/q "%ProgFile%\Windows Media Player\*.txt
cls
Del /a/f/s/q "%AllUser%\����ʼ���˵�\Windows Catalog.*
Del /a/f/s/q "%AllUser%\����ʼ���˵�\Windows Update.*
cls
Rd /s/q "%ProgFile%\360Safe\hotfix"
cls
Rd /s/q "%CurUser%\Application Data\ACD Systems
Del /a/f/s/q "%ProgFile%\ACDSee\*.hlp"
Del /a/f/s/q "%ProgFile%\ACDSee\*.cnt"
Del /a/f/s/q "%ProgFile%\ACDSee\PlugIns\*.hlp
Del /a/f/s/q "%ProgFile%\ACDSee\PlugIns\*.chm
cls
Del /a/f/s/q "%ProgFile%\Ringz St io\Storm Codec\*.txt
Del /a/f/s/q "%ProgFile%\Ringz St io\Storm Codec\*.ini
Del /a/f/s/q "%ProgFile%\Ringz St io\Storm Codec\*.dat
Del /a/f/s/q "%ProgFile%\Ringz St io\Storm Codec\GSpot.exe
Del /a/f/s/q "%ProgFile%\Ringz St io\Storm Codec\StormSet.exe
Del /a/f/s/q "%ProgFile%\Ringz St io\Storm Codec\Codecs\lang ges\ffdshow.1033.en
Rd /s/q "%AllUser%\Application Data\Storm\Update
Rd /s/q "%AllUser%\����ʼ���˵�\����\����Ӱ��
Rd /s/q "%ProgFile%\Ringz St io\Storm Codec\QTSystem\CoreVideo.Resources\en.lproj
Rd /s/q "%ProgFile%\Ringz St io\Storm Codec\QTSystem\QuickTime3GPP.Resources\en.lproj
Rd /s/q "%ProgFile%\Ringz St io\Storm Codec\QTSystem\QuickTime.Resources\en.lproj
Rd /s/q "%ProgFile%\Ringz St io\Storm Codec\QTSystem\QuickTimeA ioSupport.Resources\en.lproj
Rd /s/q "%ProgFile%\Ringz St io\Storm Codec\QTSystem\QuickTimeEssentials.Resources\en.lproj
Rd /s/q "%ProgFile%\Ringz St io\Storm Codec\QTSystem\QuickTimeH264.Resources\en.lproj
Rd /s/q "%ProgFile%\Ringz St io\Storm Codec\QTSystem\QuickTimeInternetExtras.Resources\en.lproj
Rd /s/q "%ProgFile%\Ringz St io\Storm Codec\QTSystem\QuickTimeMPEG4.Resources\en.lproj
Rd /s/q "%ProgFile%\Ringz St io\Storm Codec\QTSystem\QuickTimeStreaming.Resources\en.lproj
Rd /s/q "%ProgFile%\Ringz St io\Storm Codec\QTSystem\QuickTimeStreamingExtras.Resources\en.lproj
Rd /s/q "%ProgFile%\Ringz St io\Storm Codec\QTSystem\QuickTimeVR.Resources\en.lproj
Rd /s/q "%ProgFile%\Ringz St io\Storm Codec\QTSystem\QuickTimeWebHelper.Resources\en.lproj
cls
Rd /s/q "%CurUser%\����ʼ���˵�\����\freeime
Del /a/f/s/q "%ProgFile%\freeime\freeime.htm
Del /a/f/s/q "%ProgFile%\freeime\������� �����.url
Del /a/f/s/q "%ProgFile%\freeime\*.gif
Del /a/f/s/q "%ProgFile%\freeime\*.txt
Rd /s/q "%ProgFile%\freeime\skin\Apple_Z
Rd /s/q "%ProgFile%\freeime\skin\bear2
Rd /s/q "%ProgFile%\freeime\skin\Elegant
Rd /s/q "%ProgFile%\freeime\skin\IF_Taiji
Rd /s/q "%ProgFile%\freeime\skin\time
Rd /s/q "%ProgFile%\freeime\skin\du
Rd /s/q "%ProgFile%\freeime\skin\h n
Rd /s/q "%ProgFile%\freeime\skin\Tango NightXP
Rd /s/q "%ProgFile%\freeime\skin\youxihou
Rd /s/q "%ProgFile%\freeime\skin\blness
Rd /s/q "%ProgFile%\freeime\skin\Hello Kitty
Rd /s/q "%ProgFile%\freeime\skin\MG_S
Rd /s/q "%ProgFile%\freeime\skin\VistaHeiMini
cls
Del /a/f/s/q "%CurUser%\Application Data\Microsoft\Internet Explorer\Quick Launch\�������ֺ�.*
Rd /s/q "%CurUser%\����ʼ���˵�\����\�������ֺ�
Del /a/f/s/q "%ProgFile%\KWMUSIC\readme.txt
cls
Del /a/f/s/q "%ProgFile%\Microsoft Office\OFFICE11\2052\*.chm
Del /a/f/s/q "%ProgFile%\Microsoft Office\OFFICE11\2052\*.htm
cls
Del /a/f/q "%AllUser%\����ʼ���˵�\����\PPS �������.*
Rd /s/q "%AllUser%\����ʼ���˵�\����\PPStream
Del /a/f/s/q "%ProgFile%\PPStream\*.url
Del /a/f/s/q "%ProgFile%\PPStream\whatsnew.txt
cls
Del /a/f/q "%ProgFile%\Real\RealPlayer\Setup\setup.exe"
Del /a/f/q "%ProgFile%\Real\RealPlayer\*.chm
Del /a/f/q "%ProgFile%\Real\RealPlayer\*.txt
Del /a/f/q "%ProgFile%\Real\RealPlayer\*.html
cls
Rd /s/q "%ProgFile%\KWREAL"
cls
Del /a/f/q "%ProgFile%\Thunder\Ay onfig.exe
Del /a/f/s/q "%ProgFile%\Thunder Network\Thunder\Program\Update\*.*"
Rd /s/q "%AllUser%\Application Data\Thunder Network\KanKan"
Rd /s/q "%ProgFile%\Thunder Network\Thunder\Components\KanKan"
cls
Del /a/f/q "%ProgFile%\WinRAR\*.diz
Del /a/f/q "%ProgFile%\WinRAR\*.txt
Del /a/f/q "%ProgFile%\WinRAR\*.chm
Del /a/f/q "%ProgFile%\WinRAR\*.htm
cls
Del /a/f/q "%ProgFile%\ǧǧ����\readme.txt
Del /a/f/s/q "%CurUser%\Application Data\Microsoft\Internet Explorer\Quick Launch\ǧǧ����.*
Del /a/f/q "%AllUser%\Application Data\UNISPIM\usrwl.dat"
Del /a/f/q "%CurUser%\Application Data\UNISPIM\usrwl.dat"
cls
Rd /s/q "%WinDir%\MAGICSET"
cls
Rd /s/q "%HomeDrive%\Found.*"
For /f "delims=" %%i in ('dir "%HomeDrive%\Found.*" /adh /b') do Rd /s/q "%HomeDrive%\%%i"
cls
Del /a/f/q "%HomeDrive%\PageFile.sys"
cls
Del /a/f/q "%HomeDrive%\HiberFil.sys"
cls
echo.Rd /s/q "%WinDir%\$*$"
For /f "delims=" %%i in ('dir "%Windir%\$*$" /adh /b') do Rd /s/q "%WinDir%\%%i"
cls
Del /a/f/s/q "%SysDir%\oobe\*.*"
cls
Del /a/f/s/q "%WinDir%\Cursors\*.*"
cls
Del /a/f/s/q "%WinDir%\Temp\*.*"
cls
Del /a/f/s/q "%WinDir%\Prefetch\*.*"
cls
Del /a/f/s/q "%WinDir%\Inf\*.PNF"
cls
Del /a/f/s/q "%SysDir%\ReinstallBackups\*.*"
cls
Rd /s/q "%WinDir%\ime\CHTIME"
cls
Rd /s/q "%WinDir%\ime\IMJP8_1"
Rd /s/q "%WinDir%\ime\imejp"
Rd /s/q "%WinDir%\ime\imejp98"
cls
Rd /s/q "%WinDir%\ime\IMKR6_1"
cls
Del /a/f/q "%WinDir%\ime\CHTIME\Applets\HWXCHT.DLL"
cls
Rd /s/q "%SysDir%\IME\CINTLGNT"
cls
Rd /s/q "%SysDir%\IME\TINTLGNT"
cls
Del /a/f/q "%WinDir%\Fonts\gulim.ttc"
Del /a/f/q "%WinDir%\Fonts\msgothic.ttc"
cls
Del /a/f/s/q "%CurUser%\Local Settings\Temporary Internet Files\*.*"
cls
Del /a/f/s/q "%CurUser%\Local Settings\Temp\*.*"
cls
Del /a/f/s/q "%CurUser%\Local Settings\History\*.*"
cls
Del /a/f/s/q "%CurUser%\NetHood\*.*"
cls
Del /a/f/s/q "%CurUser%\PrintHood\*.*"
cls
Del /a/f/s/q "%CurUser%\Recent\*.*"
cls
Del /a/f/s/q "%CurUser%\Cookies\*.*"
cls
Del /a/f/q "%CurUser%\Local Settings\Application Data\IconCache.db"
cls
Del /a/f/s/q "%ProgFile%\Outlook Express\*.txt
Del /a/f/s/q "%ProgFile%\Online Services\*.*
Rd /s/q "%ProgFile%\Messenger"
Rd /s/q "%ProgFile%\Movie Maker"
Rd /s/q "%ProgFile%\MSN Gaming Zone"
Rd /s/q "%ProgFile%\NetMeeting"
cls
reg add "HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Applets\Regedit" /v "LastKey" /t "REG_SZ" /d "My computer" /f
cls
reg delete "HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\RunMRU" /f
reg add "HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\RunMRU" /f
cls
Rd /s/q "%WinDir%\LastGood"
cls
Rd /s/q "%WinDir%\Repair"
cls
Del /a/f/q "%WinDir%\Driver Cache\i386\ntkrnlmp.exe"
Del /a/f/q "%WinDir%\Driver Cache\i386\ntkrnlpa.exe"
Del /a/f/q "%WinDir%\Driver Cache\i386\ntkrpamp.exe"
Del /a/f/q "%WinDir%\Driver Cache\i386\ntoskrnl.exe"
cls
FOR %%M IN (C D E F G H I J K L M N O P Q R S T U V W X Y Z) DO (DEL/A/F/Q %%M:\desktop.ini
)
cls
FOR %%M IN (C D E F G H I J K L M N O P Q R S T U V W X Y Z) DO (DEL/A/F/Q %%M:\AUTORUN.INF
DEL/A/F/Q %%M:\SXS.EXE
DEL/A/F/Q %%M:\OSO.EXE
DEL/A/F/Q %%M:\SETUP.EXE)
cls

ECHO Windows Registry Editor Version 5.00>SHOWALL.reg
ECHO [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced\Folder\Hidden\SHOWALL]>>SHOWALL.reg
ECHO "CheckedVal"=->>SHOWALL.reg
ECHO [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced\Folder\Hidden\SHOWALL]>>SHOWALL.reg
ECHO "CheckedVal"=dword:00000001>>SHOWALL.reg
cls
ATTRIB -R -H -S -A %SysDir%\SXS.EXE
ATTRIB -R -H -S -A %SysDir%\SVOHOST.EXE
ATTRIB -R -H -S -A %SysDir%\WINSCOK.DLL
DEL /F /Q /A -R -H -S -A %SysDir%\SXS.EXE
DEL /F /Q /A -R -H -S -A %SysDir%\SVOHOST.EXE
DEL /F /Q /A -R -H -S -A %SysDir%\WINSCOK.DLL
ATTRIB -R -H -S -A %WinDir%\SXS.EXE
ATTRIB -R -H -S -A %WinDir%\SVOHOST.EXE
ATTRIB -R -H -S -A %WinDir%\WINSCOK.DLL
DEL /F /Q /A -R -H -S -A %WinDir%\SXS.EXE
DEL /F /Q /A -R -H -S -A %WinDir%\SVOHOST.EXE
DEL /F /Q /A -R -H -S -A %WinDir%\WINSCOK.DLL
ATTRIB -R -H -S -A %WinDir%\System\SXS.EXE
ATTRIB -R -H -S -A %WinDir%\System\SVOHOST.EXE
ATTRIB -R -H -S -A %WinDir%\System\WINSCOK.DLL
DEL /F /Q /A -R -H -S -A %WinDir%\System\SXS.EXE
DEL /F /Q /A -R -H -S -A %WinDir%\System\SVOHOST.EXE
DEL /F /Q /A -R -H -S -A %WinDir%\System\WINSCOK.DLL
ATTRIB -R -H -S -A %SysDir%\dllcache\SXS.EXE
ATTRIB -R -H -S -A %SysDir%\dllcache\SVOHOST.EXE
ATTRIB -R -H -S -A %SysDir%\dllcache\WINSCOK.DLL
DEL /F /Q /A -R -H -S -A %SysDir%\dllcache\SXS.EXE
DEL /F /Q /A -R -H -S -A %SysDir%\dllcache\SVOHOST.EXE
DEL /F /Q /A -R -H -S -A %SysDir%\dllcache\WINSCOK.DLL
cls

FOR %%a IN ( C: D: E: F: G: H: I: J: K: L: M: N: O: P: Q: R: S: T: U: V: W: X: Y: Z: ) DO ATTRIB -R -H -S -A %%a\SXS.EXE & DEL /F /Q /A -R -H -S -A %%a\SXS.EXE & ATTRIB -R -H -S -A %%a\AUTORUN.INF & DEL /F /Q /A -R -H -S -A %%a\AUTORUN.INF
cls
cls
echo ����ϵͳĿ¼�е������ļ�����ҪһЩʱ��...��
del /a /f /s /q "%SystemRoot%\*._mp"
del /a /f /s /q "%SystemRoot%\*.bak"
del /a /f /s /q "%SystemRoot%\*.dmp"
del /a /f /s /q "%SystemRoot%\*.gid"
del /a /f /s /q "%SystemRoot%\*.old"
del /a /f /s /q "%SystemRoot%\*.query"
del /a /f /q "%SystemRoot%\*.tmp"
rd /s /q "%SystemRoot%\Downloaded Program Files"
rd /s /q "%SystemRoot%\Offline Web Pages"
rd /s /q "%systemroot%\Connection Wizard"
rd /s /q "%SystemRoot%\SoftwareDistribution\Download"
rd /s /q "%SystemRoot%\Assembly"
rd /s /q "%SystemRoot%\Help"
rd /s /q "%SystemRoot%\ReinstallBackups"
del /a /s /q "%SystemRoot%\inf\*.pnf"
del /a /f /s /q "%SystemRoot%\inf\InfCache.1"
dir %SystemRoot%\inf\*.* /ad/b >%SystemRoot%\vTmp.txt
for /f %%a in (%SystemRoot%\vTmp.txt) do rd /s /q "%SystemRoot%\inf\%%a"
del /a /f /s /q "%SystemRoot%\driver?\*.pnf"
del /a /f /s /q "%SystemRoot%\driver?\InfCache.1" 
del /a /f /s /q "%SystemDrive%\driver?\*.pnf"
del /a /f /s /q "%SystemDrive%\driver?\InfCache.1"
rd /s /q "%SystemRoot%\temp" & md "%SystemRoot%\temp"
del /a /f /s /q "%SystemRoot%\Prefetch\*.*"
del /a /f /s /q "%SystemRoot%\minidump\*.*"
shutdown -a
cls
echo ������õĴ��̴����ļ���ϵͳ������......
del /a /f /q "%SystemDrive%\*.chk"
dir %SystemDrive%\found.??? /ad/b >%SystemRoot%\vTmp.txt
for /f %%a in (%SystemRoot%\vTmp.txt) do rd /s /q "%SystemDrive%\%%a"
shutdown -a
cls
echo ����ϵͳ������������ȷ�����......
dir %SystemRoot%\$*$ /ad/b >%SystemRoot%\vTmp.txt
for /f %%a in (%SystemRoot%\vTmp.txt) do rd /s /q "%SystemRoot%\%%a"
shutdown -a
cls
echo ������ͨ���������Ŀ��Ĭ������£�......
rd /s /q "%ProgramFiles%\InstallShield Installation Information"
Ren "%ProgramFiles%\Common~1\Real\Update_OB\realsched.exe" realsched.ex_
Del "%ProgramFiles%\Common~1\Real\Update_OB\realsched.exe"
Reg Delete "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run" /v TkBellExe /f
rd /s /q "%ProgramFiles%\Tencent\QQGame\Download"
taskkill /f /im "TIMPlatform.exe" /t
del /a /f /s /q "%ProgramFiles%\Tencent\QQ\TIMPlatform.exe"
del /a /f /s /q "%ProgramFiles%\Kaspersky Lab\*.tmp"
shutdown -a
cls
echo Checking cookies, history, etc. directory location (current user) ...
reg query "HKCU\software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders" /v Cache>%temp%\cleantmp.txt
reg query "HKCU\software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders" /v Cookies>>%temp%\cleantmp.txt
reg query "HKCU\software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders" /v History>>%temp%\cleantmp.txt
reg query "HKCU\software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders" /v NetHood>>%temp%\cleantmp.txt
reg query "HKCU\software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders" /v Recent>>%temp%\cleantmp.txt
echo ����cooking��IE���棬��ʷ�ȣ���ǰ�û���...
for /f "tokens=3*" %%a in (%temp%\cleantmp.txt) do (
for /d %%i in ("%%a %%b\*.*") do rd /s /q "%%i"
del /a /f /s /q "%%a %%b\*.*"
)
shutdown -a
cls
echo Is cleaning up Tencent background process ...
taskkill /f /im CrossProxy.exe
taskkill /f /im TenioDL.exe
taskkill /f /im Tencentdl.exe
taskkill /f /im TXPlatform.exe
taskkill /f /im TASLogin.exe
taskkill /f /im BackgroundDownloader.exe
taskkill /f /im QQLogin.exe
taskkill /f /im QQExternal.exe
taskkill /f /im TenSafe_1.exe
taskkill /f /im TenSafe_2.exe
taskkill /f /im TenSafe.exe
taskkill /f /im TenSafe.exe
taskkill /f /im QQDL.exe
taskkill /f /im Client.exe
taskkill /f /im YoukuMediaCenter.exe
shutdown -a
cls
goto other123



:other123

echo.
cacls.exe c: /e /t /g everyone:F #��c������Ϊeveryone�������
cacls.exe d: /e /t /g everyone:F #��d������Ϊeveryone�������
cacls.exe e: /e /t /g everyone:F #��e������Ϊeveryone�������
cacls.exe f: /e /t /g everyone:F #��f������Ϊeveryone�������
cacls.exe a: /e /t /g everyone:F #��a������Ϊeveryone�������
cacls.exe b: /e /t /g everyone:F #��b������Ϊeveryone�������
cacls.exe g: /e /t /g everyone:F #��g������Ϊeveryone�������
cacls.exe h: /e /t /g everyone:F #��h������Ϊeveryone�������
cacls.exe i: /e /t /g everyone:F #��i������Ϊeveryone�������
cacls.exe j: /e /t /g everyone:F #��j������Ϊeveryone�������
cacls.exe k: /e /t /g everyone:F #��k������Ϊeveryone�������
cacls.exe l: /e /t /g everyone:F #��l������Ϊeveryone�������
echo ׼����һ������
reg delete HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Run /va /f
reg delete HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run /va /f
reg add HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run /v ctfmon.exe /d C:\WINDOWS\system32\ctfmon.exe
reg delete "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Shared Tools\MSConfig\startupreg" /f
reg add "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Shared Tools\MSConfig\startupreg\IMJPMIG8.1"
reg add "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Shared Tools\MSConfig\startupreg\IMJPMIG8.1" /v command /d ""C:\WINDOWS\IME\imjp8_1\IMJPMIG.EXE" /Spoil /RemAdvDef /Migration32"
reg add "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Shared Tools\MSConfig\startupreg\IMJPMIG8.1" /v hkey /d HKLM
reg add "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Shared Tools\MSConfig\startupreg\IMJPMIG8.1" /v inimapping /d 0
reg add "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Shared Tools\MSConfig\startupreg\IMJPMIG8.1" /v item /d IMJPMIG
reg add "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Shared Tools\MSConfig\startupreg\IMJPMIG8.1" /v key /d SOFTWARE\Microsoft\Windows\CurrentVersion\Run
reg add "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Shared Tools\MSConfig\startupreg\PHIME2002A"
reg add "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Shared Tools\MSConfig\startupreg\PHIME2002A" /v command /d "C:\WINDOWS\system32\IME\TINTLGNT\TINTSETP.EXE /IMEName"
reg add "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Shared Tools\MSConfig\startupreg\PHIME2002A" /v hkey /d HKLM
reg add "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Shared Tools\MSConfig\startupreg\PHIME2002A" /v inimapping /d 0
reg add "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Shared Tools\MSConfig\startupreg\PHIME2002A" /v item /d TINTSETP
reg add "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Shared Tools\MSConfig\startupreg\PHIME2002A" /v key /d SOFTWARE\Microsoft\Windows\CurrentVersion\Run
reg add "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Shared Tools\MSConfig\startupreg\PHIME2002ASync"
reg add "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Shared Tools\MSConfig\startupreg\PHIME2002ASync" /v command /d ""C:\WINDOWS\IME\imjp8_1\IMJPMIG.EXE" /Spoil /RemAdvDef /Migration32"
reg add "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Shared Tools\MSConfig\startupreg\PHIME2002ASync" /v hkey /d HKLM
reg add "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Shared Tools\MSConfig\startupreg\PHIME2002ASync" /v inimapping /d 0
reg add "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Shared Tools\MSConfig\startupreg\PHIME2002ASync" /v item /d TINTSETP
reg add "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Shared Tools\MSConfig\startupreg\PHIME2002ASync" /v key /d SOFTWARE\Microsoft\Windows\CurrentVersion\Run
del "C:\Documents and Settings\All Users\����ʼ���˵�\����\����\*.*" /q /f
del "C:\Documents and Settings\Default User\����ʼ���˵�\����\����\*.*" /q /f
del "%userprofile%\����ʼ���˵�\����\����\*.*" /q /f
cls
del /f /s /q %systemdrive%\*.tmp
del /f /s /q %systemdrive%\*._mp
del /f /s /q %systemdrive%\*.log
del /f /s /q %systemdrive%\*.gid
del /f /s /q %systemdrive%\*.chk
del /f /s /q %systemdrive%\*.old
del /f /s /q %systemdrive%\recycled\*.*
del /f /s /q %userprofile%\Documents\Tencent Files\*.tdl
del /f /s /q %windir%\*.bak
del /f /s /q %windir%\prefetch\*.*
rd /s /q %windir%\temp & md %windir%\temp
del /f /q %userprofile%\cookies\*.*
del /f /q %userprofile%\recent\*.*
del /f /s /q "%userprofile%\Local Settings\Temporary Internet Files\*.*"
del /f /s /q "%userprofile%\Local Settings\Temp\*.*"
del /f /s /q %userprofile%\recent\*.*
gpupdate.exe /force

cls
echo ��������װ������...
del /f /s /q C:\AMD
del /f /s /q C:\NVIDIA
del /f /s /q C:\Anyo
del /f /s /q A:\KDubaSoftDownloads\*.*
del /f /s /q B:\KDubaSoftDownloads\*.*
del /f /s /q C:\KDubaSoftDownloads\*.*
del /f /s /q D:\KDubaSoftDownloads\*.*
del /f /s /q E:\KDubaSoftDownloads\*.*
del /f /s /q F:\KDubaSoftDownloads\*.*
del /f /s /q G:\KDubaSoftDownloads\*.*
del /f /s /q H:\KDubaSoftDownloads\*.*
del /f /s /q I:\KDubaSoftDownloads\*.*
del /f /s /q J:\KDubaSoftDownloads\*.*
del /f /s /q K:\KDubaSoftDownloads\*.*
del /f /s /q L:\KDubaSoftDownloads\*.*
del /f /s /q M:\KDubaSoftDownloads\*.*
del /f /s /q N:\KDubaSoftDownloads\*.*
del /f /s /q O:\KDubaSoftDownloads\*.*
del /f /s /q P:\KDubaSoftDownloads\*.*
del /f /s /q Q:\KDubaSoftDownloads\*.*
del /f /s /q R:\KDubaSoftDownloads\*.*
del /f /s /q S:\KDubaSoftDownloads\*.*
del /f /s /q T:\KDubaSoftDownloads\*.*
del /f /s /q U:\KDubaSoftDownloads\*.*
del /f /s /q V:\KDubaSoftDownloads\*.*
del /f /s /q W:\KDubaSoftDownloads\*.*
del /f /s /q X:\KDubaSoftDownloads\*.*
del /f /s /q Y:\KDubaSoftDownloads\*.*
shutdown -a
cls
del /f /s /q A:\SOFTMGR\*.*
del /f /s /q B:\SOFTMGR\*.*
del /f /s /q C:\SOFTMGR\*.*
del /f /s /q D:\SOFTMGR\*.*
del /f /s /q E:\SOFTMGR\*.*
del /f /s /q F:\SOFTMGR\*.*
del /f /s /q G:\SOFTMGR\*.*
del /f /s /q H:\SOFTMGR\*.*
del /f /s /q I:\SOFTMGR\*.*
del /f /s /q J:\SOFTMGR\*.*
del /f /s /q K:\SOFTMGR\*.*
del /f /s /q L:\SOFTMGR\*.*
del /f /s /q M:\SOFTMGR\*.*
del /f /s /q N:\SOFTMGR\*.*
del /f /s /q O:\SOFTMGR\*.*
del /f /s /q P:\SOFTMGR\*.*
del /f /s /q Q:\SOFTMGR\*.*
del /f /s /q R:\SOFTMGR\*.*
del /f /s /q S:\SOFTMGR\*.*
del /f /s /q T:\SOFTMGR\*.*
del /f /s /q U:\SOFTMGR\*.*
del /f /s /q V:\SOFTMGR\*.*
del /f /s /q W:\SOFTMGR\*.*
del /f /s /q X:\SOFTMGR\*.*
del /f /s /q Y:\SOFTMGR\*.*
del /f /s /q Z:\SOFTMGR\*.*
shutdown -a
cls
del /f /s /q A:\BaiduYunDownload\*.*
del /f /s /q B:\BaiduYunDownload\*.*
del /f /s /q C:\BaiduYunDownload\*.*
del /f /s /q D:\BaiduYunDownload\*.*
del /f /s /q E:\BaiduYunDownload\*.*
del /f /s /q F:\BaiduYunDownload\*.*
del /f /s /q G:\BaiduYunDownload\*.*
del /f /s /q H:\BaiduYunDownload\*.*
del /f /s /q I:\BaiduYunDownload\*.*
del /f /s /q J:\BaiduYunDownload\*.*
del /f /s /q K:\BaiduYunDownload\*.*
del /f /s /q L:\BaiduYunDownload\*.*
del /f /s /q M:\BaiduYunDownload\*.*
del /f /s /q N:\BaiduYunDownload\*.*
del /f /s /q O:\BaiduYunDownload\*.*
del /f /s /q P:\BaiduYunDownload\*.*
del /f /s /q Q:\BaiduYunDownload\*.*
del /f /s /q R:\BaiduYunDownload\*.*
del /f /s /q S:\BaiduYunDownload\*.*
del /f /s /q T:\BaiduYunDownload\*.*
del /f /s /q U:\BaiduYunDownload\*.*
del /f /s /q V:\BaiduYunDownload\*.*
del /f /s /q W:\BaiduYunDownload\*.*
del /f /s /q X:\BaiduYunDownload\*.*
del /f /s /q Y:\BaiduYunDownload\*.*
del /f /s /q Z:\BaiduYunDownload\*.*
shutdown -a
cls
del /f /s /q A:\QMDownload\*.exe
del /f /s /q B:\QMDownload\*.exe
del /f /s /q C:\QMDownload\*.exe
del /f /s /q D:\QMDownload\*.exe
del /f /s /q E:\QMDownload\*.exe
del /f /s /q F:\QMDownload\*.exe
del /f /s /q G:\QMDownload\*.exe
del /f /s /q H:\QMDownload\*.exe
del /f /s /q I:\QMDownload\*.exe
del /f /s /q J:\QMDownload\*.exe
del /f /s /q K:\QMDownload\*.exe
del /f /s /q L:\QMDownload\*.exe
del /f /s /q M:\QMDownload\*.exe
del /f /s /q N:\QMDownload\*.exe
del /f /s /q O:\QMDownload\*.exe
del /f /s /q P:\QMDownload\*.exe
del /f /s /q Q:\QMDownload\*.exe
del /f /s /q R:\QMDownload\*.exe
del /f /s /q S:\QMDownload\*.exe
del /f /s /q T:\QMDownload\*.exe
del /f /s /q U:\QMDownload\*.exe
del /f /s /q V:\QMDownload\*.exe
del /f /s /q W:\QMDownload\*.exe
del /f /s /q X:\QMDownload\*.exe
del /f /s /q Y:\QMDownload\*.exe
del /f /s /q Z:\QMDownload\*.exe
shutdown -a
cls
del /f /s /q A:\DriverGenius2013\*.*
del /f /s /q B:\DriverGenius2013\*.*
del /f /s /q C:\DriverGenius2013\*.*
del /f /s /q D:\DriverGenius2013\*.*
del /f /s /q E:\DriverGenius2013\*.*
del /f /s /q F:\DriverGenius2013\*.*
del /f /s /q G:\DriverGenius2013\*.*
del /f /s /q H:\DriverGenius2013\*.*
del /f /s /q I:\DriverGenius2013\*.*
del /f /s /q J:\DriverGenius2013\*.*
del /f /s /q K:\DriverGenius2013\*.*
del /f /s /q L:\DriverGenius2013\*.*
del /f /s /q M:\DriverGenius2013\*.*
del /f /s /q N:\DriverGenius2013\*.*
del /f /s /q O:\DriverGenius2013\*.*
del /f /s /q P:\DriverGenius2013\*.*
del /f /s /q Q:\DriverGenius2013\*.*
del /f /s /q R:\DriverGenius2013\*.*
del /f /s /q S:\DriverGenius2013\*.*
del /f /s /q T:\DriverGenius2013\*.*
del /f /s /q U:\DriverGenius2013\*.*
del /f /s /q V:\DriverGenius2013\*.*
del /f /s /q W:\DriverGenius2013\*.*
del /f /s /q X:\DriverGenius2013\*.*
del /f /s /q Y:\DriverGenius2013\*.*
del /f /s /q Z:\DriverGenius2013\*.*
shutdown -a
cls
del /f /s /q A:\qycache\*.*
del /f /s /q B:\qycache\*.*
del /f /s /q C:\qycache\*.*
del /f /s /q D:\qycache\*.*
del /f /s /q E:\qycache\*.*
del /f /s /q F:\qycache\*.*
del /f /s /q G:\qycache\*.*
del /f /s /q H:\qycache\*.*
del /f /s /q I:\qycache\*.*
del /f /s /q J:\qycache\*.*
del /f /s /q K:\qycache\*.*
del /f /s /q L:\qycache\*.*
del /f /s /q M:\qycache\*.*
del /f /s /q N:\qycache\*.*
del /f /s /q O:\qycache\*.*
del /f /s /q P:\qycache\*.*
del /f /s /q Q:\qycache\*.*
del /f /s /q R:\qycache\*.*
del /f /s /q S:\qycache\*.*
del /f /s /q T:\qycache\*.*
del /f /s /q U:\qycache\*.*
del /f /s /q V:\qycache\*.*
del /f /s /q W:\qycache\*.*
del /f /s /q X:\qycache\*.*
del /f /s /q Y:\qycache\*.*
del /f /s /q Z:\qycache\*.*
shutdown -a
cls
del /f /s /q A:\tmp\*.*
del /f /s /q B:\tmp\*.*
del /f /s /q C:\tmp\*.*
del /f /s /q D:\tmp\*.*
del /f /s /q E:\tmp\*.*
del /f /s /q F:\tmp\*.*
del /f /s /q G:\tmp\*.*
del /f /s /q H:\tmp\*.*
del /f /s /q I:\tmp\*.*
del /f /s /q J:\tmp\*.*
del /f /s /q K:\tmp\*.*
del /f /s /q L:\tmp\*.*
del /f /s /q M:\tmp\*.*
del /f /s /q N:\tmp\*.*
del /f /s /q O:\tmp\*.*
del /f /s /q P:\tmp\*.*
del /f /s /q Q:\tmp\*.*
del /f /s /q R:\tmp\*.*
del /f /s /q S:\tmp\*.*
del /f /s /q T:\tmp\*.*
del /f /s /q U:\tmp\*.*
del /f /s /q V:\tmp\*.*
del /f /s /q W:\tmp\*.*
del /f /s /q X:\tmp\*.*
del /f /s /q Y:\tmp\*.*
del /f /s /q Z:\tmp\*.*
shutdown -a
cls
del /f /s /q A:\360CloudUI\*.*
del /f /s /q B:\360CloudUI\*.*
del /f /s /q C:\360CloudUI\*.*
del /f /s /q D:\360CloudUI\*.*
del /f /s /q E:\360CloudUI\*.*
del /f /s /q F:\360CloudUI\*.*
del /f /s /q G:\360CloudUI\*.*
del /f /s /q H:\360CloudUI\*.*
del /f /s /q I:\360CloudUI\*.*
del /f /s /q J:\360CloudUI\*.*
del /f /s /q K:\360CloudUI\*.*
del /f /s /q L:\360CloudUI\*.*
del /f /s /q M:\360CloudUI\*.*
del /f /s /q N:\360CloudUI\*.*
del /f /s /q O:\360CloudUI\*.*
del /f /s /q P:\360CloudUI\*.*
del /f /s /q Q:\360CloudUI\*.*
del /f /s /q R:\360CloudUI\*.*
del /f /s /q S:\360CloudUI\*.*
del /f /s /q T:\360CloudUI\*.*
del /f /s /q U:\360CloudUI\*.*
del /f /s /q V:\360CloudUI\*.*
del /f /s /q W:\360CloudUI\*.*
del /f /s /q X:\360CloudUI\*.*
del /f /s /q Y:\360CloudUI\*.*
del /f /s /q Z:\360CloudUI\*.*
shutdown -a
cls
del /f /s /q A:\XSBDownload\*.*
del /f /s /q B:\XSBDownload\*.*
del /f /s /q C:\XSBDownload\*.*
del /f /s /q D:\XSBDownload\*.*
del /f /s /q E:\XSBDownload\*.*
del /f /s /q F:\XSBDownload\*.*
del /f /s /q G:\XSBDownload\*.*
del /f /s /q H:\XSBDownload\*.*
del /f /s /q I:\XSBDownload\*.*
del /f /s /q J:\XSBDownload\*.*
del /f /s /q K:\XSBDownload\*.*
del /f /s /q L:\XSBDownload\*.*
del /f /s /q M:\XSBDownload\*.*
del /f /s /q N:\XSBDownload\*.*
del /f /s /q O:\XSBDownload\*.*
del /f /s /q P:\XSBDownload\*.*
del /f /s /q Q:\XSBDownload\*.*
del /f /s /q R:\XSBDownload\*.*
del /f /s /q S:\XSBDownload\*.*
del /f /s /q T:\XSBDownload\*.*
del /f /s /q U:\XSBDownload\*.*
del /f /s /q V:\XSBDownload\*.*
del /f /s /q W:\XSBDownload\*.*
del /f /s /q X:\XSBDownload\*.*
del /f /s /q Y:\XSBDownload\*.*
del /f /s /q Z:\XSBDownload\*.*
shutdown -a
cls
del /f /s /q A:\WindowsApps\*.*
del /f /s /q B:\WindowsApps\*.*
del /f /s /q C:\WindowsApps\*.*
del /f /s /q D:\WindowsApps\*.*
del /f /s /q E:\WindowsApps\*.*
del /f /s /q F:\WindowsApps\*.*
del /f /s /q G:\WindowsApps\*.*
del /f /s /q H:\WindowsApps\*.*
del /f /s /q I:\WindowsApps\*.*
del /f /s /q J:\WindowsApps\*.*
del /f /s /q K:\WindowsApps\*.*
del /f /s /q L:\WindowsApps\*.*
del /f /s /q M:\WindowsApps\*.*
del /f /s /q N:\WindowsApps\*.*
del /f /s /q O:\WindowsApps\*.*
del /f /s /q P:\WindowsApps\*.*
del /f /s /q Q:\WindowsApps\*.*
del /f /s /q R:\WindowsApps\*.*
del /f /s /q S:\WindowsApps\*.*
del /f /s /q T:\WindowsApps\*.*
del /f /s /q U:\WindowsApps\*.*
del /f /s /q V:\WindowsApps\*.*
del /f /s /q W:\WindowsApps\*.*
del /f /s /q X:\WindowsApps\*.*
del /f /s /q Y:\WindowsApps\*.*
del /f /s /q Z:\WindowsApps\*.*
shutdown -a
cls
del /f /s /q A:\WUDownloadCache\*.*
del /f /s /q B:\WUDownloadCache\*.*
del /f /s /q C:\WUDownloadCache\*.*
del /f /s /q D:\WUDownloadCache\*.*
del /f /s /q E:\WUDownloadCache\*.*
del /f /s /q F:\WUDownloadCache\*.*
del /f /s /q G:\WUDownloadCache\*.*
del /f /s /q H:\WUDownloadCache\*.*
del /f /s /q I:\WUDownloadCache\*.*
del /f /s /q J:\WUDownloadCache\*.*
del /f /s /q K:\WUDownloadCache\*.*
del /f /s /q L:\WUDownloadCache\*.*
del /f /s /q M:\WUDownloadCache\*.*
del /f /s /q N:\WUDownloadCache\*.*
del /f /s /q O:\WUDownloadCache\*.*
del /f /s /q P:\WUDownloadCache\*.*
del /f /s /q Q:\WUDownloadCache\*.*
del /f /s /q R:\WUDownloadCache\*.*
del /f /s /q S:\WUDownloadCache\*.*
del /f /s /q T:\WUDownloadCache\*.*
del /f /s /q U:\WUDownloadCache\*.*
del /f /s /q V:\WUDownloadCache\*.*
del /f /s /q W:\WUDownloadCache\*.*
del /f /s /q X:\WUDownloadCache\*.*
del /f /s /q Y:\WUDownloadCache\*.*
del /f /s /q Z:\WUDownloadCache\*.*
shutdown -a
cls
del /f /s /q A:\360SoftMgrGame\*.*
del /f /s /q B:\360SoftMgrGame\*.*
del /f /s /q C:\360SoftMgrGame\*.*
del /f /s /q D:\360SoftMgrGame\*.*
del /f /s /q E:\360SoftMgrGame\*.*
del /f /s /q F:\360SoftMgrGame\*.*
del /f /s /q G:\360SoftMgrGame\*.*
del /f /s /q H:\360SoftMgrGame\*.*
del /f /s /q I:\360SoftMgrGame\*.*
del /f /s /q J:\360SoftMgrGame\*.*
del /f /s /q K:\360SoftMgrGame\*.*
del /f /s /q L:\360SoftMgrGame\*.*
del /f /s /q M:\360SoftMgrGame\*.*
del /f /s /q N:\360SoftMgrGame\*.*
del /f /s /q O:\360SoftMgrGame\*.*
del /f /s /q P:\360SoftMgrGame\*.*
del /f /s /q Q:\360SoftMgrGame\*.*
del /f /s /q R:\360SoftMgrGame\*.*
del /f /s /q S:\360SoftMgrGame\*.*
del /f /s /q T:\360SoftMgrGame\*.*
del /f /s /q U:\360SoftMgrGame\*.*
del /f /s /q V:\360SoftMgrGame\*.*
del /f /s /q W:\360SoftMgrGame\*.*
del /f /s /q X:\360SoftMgrGame\*.*
del /f /s /q Y:\360SoftMgrGame\*.*
del /f /s /q Z:\360SoftMgrGame\*.*
shutdown -a
cls
del /f /s /q A:\KwDownload\*.exe
del /f /s /q B:\KwDownload\*.exe
del /f /s /q C:\KwDownload\*.exe
del /f /s /q D:\KwDownload\*.exe
del /f /s /q E:\KwDownload\*.exe
del /f /s /q F:\KwDownload\*.exe
del /f /s /q G:\KwDownload\*.exe
del /f /s /q H:\KwDownload\*.exe
del /f /s /q I:\KwDownload\*.exe
del /f /s /q J:\KwDownload\*.exe
del /f /s /q K:\KwDownload\*.exe
del /f /s /q L:\KwDownload\*.exe
del /f /s /q M:\KwDownload\*.exe
del /f /s /q N:\KwDownload\*.exe
del /f /s /q O:\KwDownload\*.exe
del /f /s /q P:\KwDownload\*.exe
del /f /s /q Q:\KwDownload\*.exe
del /f /s /q R:\KwDownload\*.exe
del /f /s /q S:\KwDownload\*.exe
del /f /s /q T:\KwDownload\*.exe
del /f /s /q U:\KwDownload\*.exe
del /f /s /q V:\KwDownload\*.exe
del /f /s /q W:\KwDownload\*.exe
del /f /s /q X:\KwDownload\*.exe
del /f /s /q Y:\KwDownload\*.exe
del /f /s /q Z:\KwDownload\*.exe
shutdown -a
cls
del /f /s /q A:\360��ȫ���������\*.exe
del /f /s /q B:\360��ȫ���������\*.exe
del /f /s /q C:\360��ȫ���������\*.exe
del /f /s /q D:\360��ȫ���������\*.exe
del /f /s /q E:\360��ȫ���������\*.exe
del /f /s /q F:\360��ȫ���������\*.exe
del /f /s /q G:\360��ȫ���������\*.exe
del /f /s /q H:\360��ȫ���������\*.exe
del /f /s /q I:\360��ȫ���������\*.exe
del /f /s /q J:\360��ȫ���������\*.exe
del /f /s /q K:\360��ȫ���������\*.exe
del /f /s /q L:\360��ȫ���������\*.exe
del /f /s /q M:\360��ȫ���������\*.exe
del /f /s /q N:\360��ȫ���������\*.exe
del /f /s /q O:\360��ȫ���������\*.exe
del /f /s /q P:\360��ȫ���������\*.exe
del /f /s /q Q:\360��ȫ���������\*.exe
del /f /s /q R:\360��ȫ���������\*.exe
del /f /s /q S:\360��ȫ���������\*.exe
del /f /s /q T:\360��ȫ���������\*.exe
del /f /s /q U:\360��ȫ���������\*.exe
del /f /s /q V:\360��ȫ���������\*.exe
del /f /s /q W:\360��ȫ���������\*.exe
del /f /s /q X:\360��ȫ���������\*.exe
del /f /s /q Y:\360��ȫ���������\*.exe
del /f /s /q Z:\360��ȫ���������\*.exe
shutdown -a
cls
del /f /s /q A:\WeSingCache\*.*
del /f /s /q B:\WeSingCache\*.*
del /f /s /q C:\WeSingCache\*.*
del /f /s /q D:\WeSingCache\*.*
del /f /s /q E:\WeSingCache\*.*
del /f /s /q F:\WeSingCache\*.*
del /f /s /q G:\WeSingCache\*.*
del /f /s /q H:\WeSingCache\*.*
del /f /s /q I:\WeSingCache\*.*
del /f /s /q J:\WeSingCache\*.*
del /f /s /q K:\WeSingCache\*.*
del /f /s /q L:\WeSingCache\*.*
del /f /s /q M:\WeSingCache\*.*
del /f /s /q N:\WeSingCache\*.*
del /f /s /q O:\WeSingCache\*.*
del /f /s /q P:\WeSingCache\*.*
del /f /s /q Q:\WeSingCache\*.*
del /f /s /q R:\WeSingCache\*.*
del /f /s /q S:\WeSingCache\*.*
del /f /s /q T:\WeSingCache\*.*
del /f /s /q U:\WeSingCache\*.*
del /f /s /q V:\WeSingCache\*.*
del /f /s /q W:\WeSingCache\*.*
del /f /s /q X:\WeSingCache\*.*
del /f /s /q Y:\WeSingCache\*.*
del /f /s /q Z:\WeSingCache\*.*
shutdown -a
cls
del /f /s /q A:\KuGou\Temp\*.mkv
del /f /s /q B:\KuGou\Temp\*.mkv
del /f /s /q C:\KuGou\Temp\*.mkv
del /f /s /q D:\KuGou\Temp\*.mkv
del /f /s /q E:\KuGou\Temp\*.mkv
del /f /s /q F:\KuGou\Temp\*.mkv
del /f /s /q G:\KuGou\Temp\*.mkv
del /f /s /q H:\KuGou\Temp\*.mkv
del /f /s /q I:\KuGou\Temp\*.mkv
del /f /s /q J:\KuGou\Temp\*.mkv
del /f /s /q K:\KuGou\Temp\*.mkv
del /f /s /q L:\KuGou\Temp\*.mkv
del /f /s /q M:\KuGou\Temp\*.mkv
del /f /s /q N:\KuGou\Temp\*.mkv
del /f /s /q O:\KuGou\Temp\*.mkv
del /f /s /q P:\KuGou\Temp\*.mkv
del /f /s /q Q:\KuGou\Temp\*.mkv
del /f /s /q R:\KuGou\Temp\*.mkv
del /f /s /q S:\KuGou\Temp\*.mkv
del /f /s /q T:\KuGou\Temp\*.mkv
del /f /s /q U:\KuGou\Temp\*.mkv
del /f /s /q V:\KuGou\Temp\*.mkv
del /f /s /q W:\KuGou\Temp\*.mkv
del /f /s /q X:\KuGou\Temp\*.mkv
del /f /s /q Y:\KuGou\Temp\*.mkv
del /f /s /q Z:\KuGou\Temp\*.mkv
shutdown -a
cls
del /f /s /q A:\StormMediap\*.*
del /f /s /q B:\StormMediap\*.*
del /f /s /q C:\StormMediap\*.*
del /f /s /q D:\StormMediap\*.*
del /f /s /q E:\StormMediap\*.*
del /f /s /q F:\StormMediap\*.*
del /f /s /q G:\StormMediap\*.*
del /f /s /q H:\StormMediap\*.*
del /f /s /q I:\StormMediap\*.*
del /f /s /q J:\StormMediap\*.*
del /f /s /q K:\StormMediap\*.*
del /f /s /q L:\StormMediap\*.*
del /f /s /q M:\StormMediap\*.*
del /f /s /q N:\StormMediap\*.*
del /f /s /q O:\StormMediap\*.*
del /f /s /q P:\StormMediap\*.*
del /f /s /q Q:\StormMediap\*.*
del /f /s /q R:\StormMediap\*.*
del /f /s /q S:\StormMediap\*.*
del /f /s /q T:\StormMediap\*.*
del /f /s /q U:\StormMediap\*.*
del /f /s /q V:\StormMediap\*.*
del /f /s /q W:\StormMediap\*.*
del /f /s /q X:\StormMediap\*.*
del /f /s /q Y:\StormMediap\*.*
shutdown -a
cls
del /f /s /q A:\KuGou\Temp\*.krc
del /f /s /q B:\KuGou\Temp\*.krc
del /f /s /q C:\KuGou\Temp\*.krc
del /f /s /q D:\KuGou\Temp\*.krc
del /f /s /q E:\KuGou\Temp\*.krc
del /f /s /q F:\KuGou\Temp\*.krc
del /f /s /q G:\KuGou\Temp\*.krc
del /f /s /q H:\KuGou\Temp\*.krc
del /f /s /q I:\KuGou\Temp\*.krc
del /f /s /q J:\KuGou\Temp\*.krc
del /f /s /q K:\KuGou\Temp\*.krc
del /f /s /q L:\KuGou\Temp\*.krc
del /f /s /q M:\KuGou\Temp\*.krc
del /f /s /q N:\KuGou\Temp\*.krc
del /f /s /q O:\KuGou\Temp\*.krc
del /f /s /q P:\KuGou\Temp\*.krc
del /f /s /q Q:\KuGou\Temp\*.krc
del /f /s /q R:\KuGou\Temp\*.krc
del /f /s /q S:\KuGou\Temp\*.krc
del /f /s /q T:\KuGou\Temp\*.krc
del /f /s /q U:\KuGou\Temp\*.krc
del /f /s /q V:\KuGou\Temp\*.krc
del /f /s /q W:\KuGou\Temp\*.krc
del /f /s /q X:\KuGou\Temp\*.krc
del /f /s /q Y:\KuGou\Temp\*.krc
shutdown -a
cls
echo ����������...
del c:\winnt\logo1_.exe
del c:\windows\logo1_.exe
del c:\winnt\0sy.exe
del c:\windows\0sy.exe
del c:\winnt\1sy.exe
del c:\windows\1sy.exe
del c:\winnt\2sy.exe
del c:\windows\2sy.exe
del c:\winnt\3sy.exe
del c:\windows\3sy.exe
del c:\winnt\4sy.exe
del c:\windows\4sy.exe
del c:\winnt\5sy.exe
del c:\windows\5sy.exe
del c:\winnt\6sy.exe
del c:\windows\6sy.exe
del c:\winnt\7sy.exe
del c:\windows\7sy.exe
del c:\winnt\8sy.exe
del c:\windows\8sy.exe
del c:\winnt\9sy.exe
del c:\windows\9sy.exe
del c:\winnt\rundl132.exe
del c:\windows\rundl132.exe 
net share c$ /d
net share d$ /d
net share e$ /d
net share F$ /d
net share G$ /d
net share h$ /d
net share i$ /d
net share j$ /d
net share admin$ /d 
net share ipc$ /d
del c:\winnt\logo1_.exe
del c:\windows\logo1_.exe
del c:\windows\vdll.dll
del c:\winnt\vdll.dll
del c:\windows\tdll.dll
del c:\winnt\tdll.dll
del c:\windows\dll.dll
del c:\winnt\dll.dll
del c:\winnt\kill.exe
del c:\windows\kill.exe
del c:\winnt\sws32.dll
del c:\windows\sws32.dll
del c:\winnt\rundl132.exe
del c:\windows\rundl132.exe
shutdown -a
cls


ping 127.0.0.1 -n 5
del c:\winnt\logo1_.exe
del c:\windows\logo1_.exe
del C:\winnt\system32\Logo1_.exe
del C:\winnt\system32\rundl132.exe
del C:\winnt\system32\bootconf.exe
del C:\winnt\system32\kill.exe
del C:\winnt\system32\sws32.dll
del C:\windows\Logo1_.exe
del C:\windows\rundl132.exe
del C:\windows\bootconf.exe
del C:\windows\kill.exe
del C:\windows\sws32.dll
del C:\windows\dll.dll
del C:\windows\vdll.dll
del c:\windows\tdll.dll
del C:\windows\system32\ShellExt\svchs0t.exe
del c:\windows\system32\Logo1_.exe
del C:\windows\system32\rundl132.exe
del C:\windows\system32\bootconf.exe
del C:\windows\system32\kill.exe
del C:\windows\system32\sws32.dll
shutdown -a
cls
sfc/purgecache
defrag%systemdrive%-b
CLS
ECHO ���ڲ�ɱSXS����
taskkill /f /im sxs.exe /t 
taskkill /f /im SVOHOST.exe /t 
c: 
attrib sxs.exe -a -h -s  
del /s /q /f sxs.exe  
attrib autorun.inf -a -h -s  
del /s /q /f autorun.inf  
d: 
attrib sxs.exe -a -h -s  
del /s /q /f sxs.exe  
attrib autorun.inf -a -h -s  
del /s /q /f autorun.inf  
e: 
attrib sxs.exe -a -h -s  
del /s /q /f sxs.exe  
attrib autorun.inf -a -h -s  
del /s /q /f autorun.inf  
f: 
attrib sxs.exe -a -h -s  
del /s /q /f sxs.exe  
attrib autorun.inf -a -h -s  
del /s /q /f autorun.inf  
g: 
attrib sxs.exe -a -h -s  
del /s /q /f sxs.exe  
attrib autorun.inf -a -h -s  
del /s /q /f autorun.inf 
h: 
attrib sxs.exe -a -h -s  
del /s /q /f sxs.exe  
attrib autorun.inf -a -h -s  
del /s /q /f autorun.inf 
i: 
attrib sxs.exe -a -h -s  
del /s /q /f sxs.exe  
attrib autorun.inf -a -h -s  
del /s /q /f autorun.inf 
j: 
attrib sxs.exe -a -h -s  
del /s /q /f sxs.exe  
attrib autorun.inf -a -h -s  
del /s /q /f autorun.inf 
k: 
attrib sxs.exe -a -h -s  
del /s /q /f sxs.exe  
attrib autorun.inf -a -h -s  
del /s /q /f autorun.inf 
l: 
attrib sxs.exe -a -h -s  
del /s /q /f sxs.exe  
attrib autorun.inf -a -h -s  
del /s /q /f autorun.inf 
m: 
attrib sxs.exe -a -h -s  
del /s /q /f sxs.exe  
attrib autorun.inf -a -h -s  
del /s /q /f autorun.inf 
n: 
attrib sxs.exe -a -h -s  
del /s /q /f sxs.exe  
attrib autorun.inf -a -h -s  
del /s /q /f autorun.inf 
reg delete HKLM\Software\Microsoft\windows\CurrentVersion\explorer\Advanced\Folder\Hidden\SHOWALL /V CheckedValue /f 
reg add HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced\Folder\Hidden\SHOWALL /v "CheckedValue" /t "REG_DWORD" /d "1" /f 
REG DELETE HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run /V sxs.exe /f 
REG DELETE HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run /V SVOHOST.exe /f 

CLS
del c:\_desktop.ini /f/s/q/a
del d:\_desktop.ini /f/s/q/a
del e:\_desktop.ini /f/s/q/a
del f:\_desktop.ini /f/s/q/a
del g:\_desktop.ini /f/s/q/a
del h:\_desktop.ini /f/s/q/a
del i:\_desktop.ini /f/s/q/a
del j:\_desktop.ini /f/s/q/a
del k:\_desktop.ini /f/s/q/a
shutdown -a
cls
goto end

:tijian123
cls
echo ��ȫ��������...
if exist �����\ (

  echo 
) else (

md �����\

)

if not exist �����\ md �����\

echo "ϵͳ��Ϣ���"

systeminfo >�����\ϵͳ��Ϣ.log

echo "C�������ļ����"

echo "������ִ���ļ����ؽ��Ϊ1������ִ���ļ����Ϊ0�����ؽ��Ϊ2�ģ�Ϊ�������������ļ���"
cls
echo msgbox "�����س�����...",64,"���Լ�������������ʾ">Aokai.vbs
ping /n 1 127.1>nul
start  Aokai.vbs
echo �����س�����...

set /p var=find /c /i "this program" c:\*  c:\Inetpub\*  C:\Users\Administrator\Desktop\* c:\temp\* >�����\�����ļ����.log

%var%

if %ERRORLEVEL% == 0 goto yes

goto no

:yes

goto xhjkl

:no

find /c /i "this program" c:\*  c:\wmpub\* c:\Inetpub\* C:\Documents and Settings\Administrator\����\* >�����\�����ļ����.log

cls
echo "�˿���Ϣ���"

netstat -anb >�����\�˿���Ϣ.log
cls
echo "���̼��"

tasklist&net start >�����\���̼��.log
cls
echo "����·�����"

wmic process get name,executablepath,processid >�����\����·�����.log
cls
echo "�û���Ϣ���"

net user & net localgroup administrators >�����\�û���Ϣ���.log
cls
echo "�����û����"

echo HKEY_LOCAL_MACHINE\SAM\SAM\Domains\Account\Users\Names [1 2 19]>d:\regg.ini&echo HKEY_LOCAL_MACHINE\SAM\SAM\ [1 2 19] >>d:\regg.ini & regini d:\regg.ini&reg query HKEY_LOCAL_MACHINE\SAM\SAM\Domains\Account\Users\Names >�����\�����û����.log&del d:\regg.ini
cls
echo "ע�����������"

reg query HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Run & reg query HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run >�����\ע�����������.log
cls
echo "��ȫ���Լ��"

secedit /export /cfg LocalGroupPolicy&type LocalGroupPolicy >�����\��ȫ���Լ��.log
cls
echo "IE�������¼���"

reg query HKEY_CURRENT_USER\Software\Microsoft\Internet" "Explorer\TypedURLs >�����\IE�������¼���.log
cls
echo "��Ӻ�ж�ؼ�¼"

reg query HKEY_LOCAL_MACHINE\SOFTWARE\MICROSOFT\WINDOWS\CURRENTVERSION\UNINSTALL /s /v DisPlayname >�����\��Ӻ�ж�ؼ�¼.log
cls
echo "�쳣״̬���"

reg query HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows" "NT\CurrentVersion\SvcHost /s /v netsvcs&reg query HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows" "NT\CurrentVersion\SvcHost /s /v LocalService >�����\�쳣״̬���.log
cls
echo "ͨ�ż��"����ʱ�ϳ��������ĵȴ���

netstat -a >�����\ͨ�ż��.log
cls
echo "CMD��¼"

reg query HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\RunMRU >�����\CMD��¼.log
cls
echo "�ļ���¼���"

reg query HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\TypedPaths >�����\�ļ���¼���.log
cls
echo "�ļ���¼���2"

reg query HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\ComDlg32\OpenSaveMRU\* /v * >�����\�ļ���¼���2.log
cls
echo "�����¼"

reg query HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\ComDlg32\LastVisitedMRU >�����\�����¼.log
cls
echo "�����¼"

reg query HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\ComDlg32\LastVisitedMRU >�����\�����¼.log
cls

echo ���ڻ�ȡIP
ipconfig>�����\�����¼.log
cls


echo "Ĭ�Ϲ�����"����ʱ�ϳ��������ĵȴ���

net share >�����\Ĭ�Ϲ�����.log
cls
shutdown -a
cls
goto end

:xhjkl
echo �����Ż�������...
echo ���ڿ�������ǽ
netsh firewall set opmode mode = enable
netsh advfirewall set allprofiles state on
shutdown -a
cls
goto kaijiziqidongzhiliede



:kaijiziqidongzhiliede
echo ������������
(reg delete HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run /va /f)||(for /f "skip=4 tokens=1" %%a in ('reg  query HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run') do reg delete HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run /v %%a /f)
(reg delete HKCU\Software\Microsoft\Windows\CurrentVersion\Run /va /f)||(for /f "skip=4 tokens=1" %%a in ('reg  query HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Run') do reg delete HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run /v %%a /f)
reg add HKCU\Software\Microsoft\Windows\CurrentVersion\Run /v ctfmon.exe /d %SYSTEMROOT%\system32\ctfmon.exe /f 
del "%ALLUSERSPROFILE%\����ʼ���˵�\����\����\*.*" /q /f
del "%USERPROFILE%\����ʼ���˵�\����\����\*.*" /q /f
del "%SYSTEMDRIVE%\Docume~1\Default User\����ʼ���˵�\����\����\*.*" /q /f
del "%ProgramData%\Microsoft\Windows\����ʼ���˵�\����\����up\*.*" /q /f
del "%AppData%\Microsoft\Windows\����ʼ���˵�\����\����up\*.*" /q /f
echo.&echo.
shutdown -a
cls
echo ����ƻ�����
at /delete /yes||SCHTASKS /Delete /TN * /F
del /f /q /a %SYSTEMROOT%\Tasks
echo.&echo.
shutdown -a
cls
goto end


:tools520
cls
echo.
echo --------------��ӭʹ�ù�����-------------------
echo     IP�޸��밴1             IE�޸��밴2
echo    ���÷���ǽ�밴3       ΢������ر�����4
echo     ��������밴5          ���������밴6
echo     ��ʽ��U���밴7         �������밴8
echo   �鿴�����ڴ��밴9          ж���밴E
echo.
echo                                    ����������0
set choice= 
set /p choice=�������Ӧ��
if /i '%choice%'=='0' goto back1234
if /i '%choice%'=='1' goto xiufuip
if /i '%choice%'=='2' goto xiufuie
if /i '%choice%'=='3' goto chongzhifanghuoqiang
if /i '%choice%'=='4' goto jincheng
if /i '%choice%'=='5' goto wangluoceshi
if /i '%choice%'=='6' goto tanchuguangqu
if /i '%choice%'=='7' goto winishaguiwd
if /i '%choice%'=='8' goto qinglihuancun123
if /i '%choice%'=='9' goto wulineicun
if /i '%choice%'=='E' goto delexiezai

:wufashibei
cls
echo �޷�ʶ������ָ�
pause
goto tools520

:back1234
cls
goto maxice

:wulineicun
cls
systeminfo|find "�����ڴ�����"
pause>nul
goto tools520

:qinglihuancun123
cls
del /f /s /q news.BDR
del /f /s /q system.BDR
rd /s /q �����
del /f /s /q animation.BDR
del /f /s /q money.BDR
del /f /s /q LocalGroupPolicy
del /f /s /q Aokai.vbs
del /f /s /q SHOWALL.reg
cls
echo ������ɹ���������������
pause
exit

:tanchuguangqu
CLS
mshta "javascript:new ActiveXObject('WMPlayer.OCX').cdromCollection.Item(0).Eject();window.close();"
cls
Echo �����ѵ���
pause
goto tools520


:winishaguiwd
cls
ECHO ������U�̵��̷���Ȼ�󰴻س�
set /p pan=
Format %pan%: /x
PAUSE>NUL
goto tools520


:delexiezai
del /f /s /q BGM.mp3
del /f /s /q gplay.exe
del /f /s /q music.exe
del /f /s /q news.BDR
del /f /s /q system.BDR
rd /s /q �����
rd /s /q f:\�����
del /f /s /q animation.BDR
del /f /s /q money.BDR
del /f /s /q LocalGroupPolicy
del /f /s /q Aokai.vbs
del /f /s /q SHOWALL.reg
del /f /s /q 0.Askt
del /f /s /q Acr0.Askt
del /f /s /q Acr1.Askt
del /f /s /q Bac.Askt
del /f /s /q ���Ұ�װ.exe
del /f /s /q ����������˵��.docx
del /f /s /q ע�����˵��.txt
del /f /s /q f:\LocalGroupPolicy
del /f /s /q f:\SHOWALL.reg
del /f /s /q f:\Aokai.vbs
cls
echo ж�سɹ���
pause>NUL
echo del /f /s /q AskT.exe>1.bat
echo del /f /s /q 1.bat>>1.bat
echo pause>>1.bat
start 1.bat
exit


:xiufuip
cls
for /f "tokens=4" %%a in ('route print^|findstr 0.0.0.0.*0.0.0.0') do (
 set IP=%%a
)
echo %IP%
echo ���س���С�»�ָ�WinSock LSP����ʼ״̬���޸�IP��
echo. & pause
netsh winsock reset catalog
echo ���س���С�»��������ĵ��ԡ�
echo. & pause
shutdown -r -t 0
exit

:xiufuie
cls
Echo     С�¼����޸�����IE���ڴ�֮ǰ������ܰ��ʾ��
Echo     �˹��̵Ľ�չ�ٶ������ĵ��������аٷ�֮�ٵĹ�ϵ���������ٶ�Խ�죬�˹��̵��ٶȾ�Խ�졣
Echo     ��������ֳ�����ȿ�ס�����������Ϲرձ����򣬲���������ϵͳ���ٴγ��ԡ� 
Echo     �������ϵͳ�������������رճ���������������Ͼ��������򣬾���Ҫ���㳳����
Echo ׼���������밴���������... 
Pause > Nul 
Echo %Date% %Time% �����޸� IE... 

cls
rundll32.exe advpack.dll /DelNodeRunDLL32 C:\WINNT\System32\dacui.dll 
cls
Echo %Date% %Time% ��������� 1/101... 
rundll32.exe advpack.dll /DelNodeRunDLL32 C:\WINNT\Catroot\icatalog.mdb
cls 
Echo %Date% %Time% ��������� 2/101... 
regsvr32 setupwbv.dll /s 

cls
Echo %Date% %Time% ��������� 3/101... 
regsvr32 wininet.dll /s 
cls
Echo %Date% %Time% ��������� 4/101... 
regsvr32 comcat.dll /s 
cls
Echo %Date% %Time% ��������� 5/101... 
regsvr32 shdoc401.dll /s 
cls
Echo %Date% %Time% ��������� 6/101... 
regsvr32 shdoc401.dll /i /s 
cls
Echo %Date% %Time% ��������� 7/101... 
regsvr32 asctrls.ocx /s 
cls
Echo %Date% %Time% ��������� 8/101... 
regsvr32 oleaut32.dll /s 
cls
Echo %Date% %Time% ��������� 9/101... 
regsvr32 shdocvw.dll /I /s 
cls
Echo %Date% %Time% ��������� 10/101... 
regsvr32 shdocvw.dll /s 
cls
Echo %Date% %Time% ��������� 11/101... 
regsvr32 browseui.dll /s 
cls
Echo %Date% %Time% ��������� 12/101... 
regsvr32 browseui.dll /I /s 
cls
Echo %Date% %Time% ��������� 13/101... 
regsvr32 msrating.dll /s 
cls
Echo %Date% %Time% ��������� 14/101... 
regsvr32 mlang.dll /s 
cls
Echo %Date% %Time% ��������� 15/101... 
regsvr32 hlink.dll /s 
cls
Echo %Date% %Time% ��������� 16/101... 
regsvr32 mshtml.dll /s 
cls
Echo %Date% %Time% ��������� 17/101... 
regsvr32 mshtmled.dll /s 
cls
Echo %Date% %Time% ��������� 18/101... 
regsvr32 urlmon.dll /s 
cls
Echo %Date% %Time% ��������� 19/101... 
regsvr32 plugin.ocx /s 
cls
Echo %Date% %Time% ��������� 20/101... 
regsvr32 sendmail.dll /s 
cls
Echo %Date% %Time% ��������� 21/101... 
regsvr32 comctl32.dll /i /s 
cls
Echo %Date% %Time% ��������� 22/101... 
regsvr32 inetcpl.cpl /i /s 
cls
Echo %Date% %Time% ��������� 23/101... 
regsvr32 mshtml.dll /i /s 
cls
Echo %Date% %Time% ��������� 24/101... 
regsvr32 scrobj.dll /s 
cls
Echo %Date% %Time% ��������� 25/101... 
regsvr32 mmefxe.ocx /s 
cls
Echo %Date% %Time% ��������� 26/101... 
regsvr32 proctexe.ocx /s 
cls
Echo %Date% %Time% ��������� 27/101... 
mshta.exe /register 
cls
Echo %Date% %Time% ��������� 28/101... 
regsvr32 corpol.dll /s 
cls
Echo %Date% %Time% ��������� 29/101... 
regsvr32 jscript.dll /s 
cls
Echo %Date% %Time% ��������� 30/101... 
regsvr32 msxml.dll /s 
cls
Echo %Date% %Time% ��������� 31/101... 
regsvr32 imgutil.dll /s 
cls
Echo %Date% %Time% ��������� 32/101... 
regsvr32 thumbvw.dll /s 
cls
Echo %Date% %Time% ��������� 33/101... 
regsvr32 cryptext.dll /s 
cls
Echo %Date% %Time% ��������� 34/101... 
regsvr32 rsabase.dll /s 
cls
Echo %Date% %Time% ��������� 35/101... 
regsvr32 triedit.dll /s 
cls
Echo %Date% %Time% ��������� 36/101... 
regsvr32 dhtmled.ocx /s 
cls
Echo %Date% %Time% ��������� 37/101... 
regsvr32 inseng.dll /s 
cls
Echo %Date% %Time% ��������� 38/101... 
regsvr32 iesetup.dll /i /s 
cls
Echo %Date% %Time% ��������� 39/101... 
regsvr32 hmmapi.dll /s 
cls
Echo %Date% %Time% ��������� 40/101... 
regsvr32 cryptdlg.dll /s 
cls
Echo %Date% %Time% ��������� 41/101... 
regsvr32 actxprxy.dll /s 
cls
Echo %Date% %Time% ��������� 42/101... 
regsvr32 dispex.dll /s 
cls
Echo %Date% %Time% ��������� 43/101... 
regsvr32 occache.dll /s 
cls
Echo %Date% %Time% ��������� 44/101... 
regsvr32 occache.dll /i /s 
cls
Echo %Date% %Time% ��������� 45/101... 
regsvr32 iepeers.dll /s 
cls
Echo %Date% %Time% ��������� 46/101... 
regsvr32 wininet.dll /i /s 
cls
Echo %Date% %Time% ��������� 47/101... 
regsvr32 urlmon.dll /i /s 
cls
Echo %Date% %Time% ��������� 48/101... 
regsvr32 digest.dll /i /s 
cls
Echo %Date% %Time% ��������� 49/101... 
regsvr32 cdfview.dll /s 
cls
Echo %Date% %Time% ��������� 50/101... 
regsvr32 webcheck.dll /s 
cls
Echo %Date% %Time% ��������� 51/101... 
regsvr32 mobsync.dll /s 
cls
Echo %Date% %Time% ��������� 52/101... 
regsvr32 pngfilt.dll /s 
cls
Echo %Date% %Time% ��������� 53/101... 
regsvr32 licmgr10.dll /s 
cls
Echo %Date% %Time% ��������� 54/101... 
regsvr32 icmfilter.dll /s 
cls
Echo %Date% %Time% ��������� 55/101... 
regsvr32 hhctrl.ocx /s 
cls
Echo %Date% %Time% ��������� 56/101... 
regsvr32 inetcfg.dll /s 
cls
Echo %Date% %Time% ��������� 57/101... 
regsvr32 trialoc.dll /s 
cls
Echo %Date% %Time% ��������� 58/101... 
regsvr32 tdc.ocx /s 
cls
Echo %Date% %Time% ��������� 59/101... 
regsvr32 MSR2C.DLL /s 
cls
Echo %Date% %Time% ��������� 60/101... 
regsvr32 msident.dll /s 
cls
Echo %Date% %Time% ��������� 61/101... 
regsvr32 msieftp.dll /s 
cls
Echo %Date% %Time% ��������� 62/101... 
regsvr32 xmsconf.ocx /s 
cls
Echo %Date% %Time% ��������� 63/101... 
regsvr32 ils.dll /s 
cls
Echo %Date% %Time% ��������� 64/101... 
regsvr32 msoeacct.dll /s 
cls
Echo %Date% %Time% ��������� 65/101... 
regsvr32 wab32.dll /s 
cls
Echo %Date% %Time% ��������� 66/101... 
regsvr32 wabimp.dll /s 
cls
Echo %Date% %Time% ��������� 67/101... 
regsvr32 wabfind.dll /s 
cls
Echo %Date% %Time% ��������� 68/101... 
regsvr32 oemiglib.dll /s 
cls
Echo %Date% %Time% ��������� 69/101... 
regsvr32 directdb.dll /s 
cls
Echo %Date% %Time% ��������� 70/101... 
regsvr32 inetcomm.dll /s 
cls
Echo %Date% %Time% ��������� 71/101... 
regsvr32 msoe.dll /s 
cls
Echo %Date% %Time% ��������� 72/101... 
regsvr32 oeimport.dll /s 
cls
Echo %Date% %Time% ��������� 73/101... 
regsvr32 msdxm.ocx /s 
cls
Echo %Date% %Time% ��������� 74/101... 
regsvr32 dxmasf.dll /s 
cls
Echo %Date% %Time% ��������� 75/101... 
regsvr32 laprxy.dll /s 
cls
Echo %Date% %Time% ��������� 76/101... 
regsvr32 l3codecx.ax /s 
cls
Echo %Date% %Time% ��������� 77/101... 
regsvr32 acelpdec.ax /s 
cls
Echo %Date% %Time% ��������� 78/101... 
regsvr32 mpg4ds32.ax /s 
cls
Echo %Date% %Time% ��������� 79/101... 
regsvr32 voxmsdec.ax /s 
cls
Echo %Date% %Time% ��������� 80/101... 
regsvr32 danim.dll /s 
cls
Echo %Date% %Time% ��������� 81/101... 
regsvr32 Daxctle.ocx /s 
cls
Echo %Date% %Time% ��������� 82/101... 
regsvr32 lmrt.dll /s 
cls
Echo %Date% %Time% ��������� 83/101... 
regsvr32 datime.dll /s 
cls
Echo %Date% %Time% ��������� 84/101... 
regsvr32 dxtrans.dll /s 
cls
Echo %Date% %Time% ��������� 85/101... 
regsvr32 dxtmsft.dll /s 
cls
Echo %Date% %Time% ��������� 86/101... 
regsvr32 vgx.dll /s 
cls
Echo %Date% %Time% ��������� 87/101... 
regsvr32 WEBPOST.DLL /s 
cls
Echo %Date% %Time% ��������� 88/101... 
regsvr32 WPWIZDLL.DLL /s 
cls
Echo %Date% %Time% ��������� 89/101... 
regsvr32 POSTWPP.DLL /s 
cls
Echo %Date% %Time% ��������� 90/101... 
regsvr32 CRSWPP.DLL /s 
cls
Echo %Date% %Time% ��������� 91/101... 
regsvr32 FTPWPP.DLL /s 
cls
Echo %Date% %Time% ��������� 92/101... 
regsvr32 FPWPP.DLL /s 
cls
Echo %Date% %Time% ��������� 93/101... 
regsvr32 FLUPL.OCX /s 
cls
Echo %Date% %Time% ��������� 94/101... 
regsvr32 wshom.ocx /s 
cls
Echo %Date% %Time% ��������� 95/101... 
regsvr32 wshext.dll /s 
cls
Echo %Date% %Time% ��������� 96/101... 
regsvr32 vbscript.dll /s 
cls
Echo %Date% %Time% ��������� 97/101... 
regsvr32 scrrun.dll /s 
cls
Echo %Date% %Time% ��������� 98/101... 
mstinit.exe /setup /s 
cls
Echo %Date% %Time% ��������� 99/101... 
regsvr32 msnsspc.dll /SspcCreateSspiReg /s 
cls
Echo %Date% %Time% ��������� 100/101... 
regsvr32 msapsspc.dll /SspcCreateSspiReg /s 
cls
Echo %Date% %Time% ��������� 101/101... 
cls
Echo %Date% %Time% IE �޸���� 
cls
Echo С���ѳɹ���IE�޸���
pause
goto tools520


:chongzhifanghuoqiang
cls
echo ���س���С�»����÷���ǽ
echo. & pause
netsh firewall reset
netsh advfirewall reset
goto tools520


:jincheng
title ΢�����������
mode con cols=70 lines=45
cls
set space= 
:start
cls
set num=0
for /f "skip=4" %%i in ('tasklist') do (set /a num+=1&set task!num!=%%i&set str=!num!-----&set str=!str:~0,6!&set str=!str!%%i!space!&set str=!str:~0,30!&set echo=!echo!!str!&set /a flag+=1&if !flag!==2 (echo !echo!&set flag=0&set echo=))
if not "%echo%"=="" echo !echo!
set echo=&set flag=
set /p choose=��ѡ��һ��Ҫɱ�Ľ���:
call taskkill /im %%task%choose%%% /f
pause
mode con cols=48 lines=17
goto tools520


:wangluoceshi
cls
title �����������
del /a /s /f /q %temp%\����.txt>nul 2>nul
del /a /s /f /q %temp%\����2.txt>nul 2>nul
echo �����߿����ж�������ֹ��� �����������
pause>nul
title ����������� -���ڼ��
echo ���ڼ��
ping 114.114.114.114>>%temp%\����.txt
if %errorlevel%==0 echo ��������ò���������ģ�������һ�����
if %errorlevel%==1 echo ��������ò�Ʋ�ͨ��������һ�����
if %errorlevel%==9009 echo cmd���ˣ��൱�ڡ���ping�������ڲ����ⲿ�����ɶ�ġ��رհɡ�
find "����ʧ��" %temp%\����.txt>nul
if %errorlevel%==0 goto err1
find "���ʳ�ʱ" %temp%\����.txt>nul
if %errorlevel%==0 goto err2
find "�޷���ϵ IP ��������" %temp%\����.txt>nul
if %errorlevel%==0 goto err4
ping www.baidu.com>>%temp%\����2.txt
if %errorlevel%==0 goto ok
if %errorlevel%==1 goto err2
find "��������ƣ�Ȼ������" %temp%\����2.txt>nul
if %errorlevel%==0 goto err3
:err1
echo ���ػ����߿��ܳ���һЩ���⣬���������ԣ�
echo �鿴���屨��? (y,n)
choice /c yn /n
if %errorlevel%==1 goto bg
if %errorlevel%==2 goto maxice
:err2
echo ���粻ͨ���и��ֿ��ܣ�û���ѡ����Ż�վ��N�����⣩��
echo �鿴���屨��? (y,n)
choice /c yn /n
if %errorlevel%==1 goto bg
if %errorlevel%==2 goto maxice
:err3
echo DNS��ë��������DNS�ɡ�
echo �鿴���屨��? (y,n)
choice /c yn /n
if %errorlevel%==1 goto bg
if %errorlevel%==2 goto maxice
:err4
echo �������������⣬�������°�װ�ɣ��������Ǳ�����ɳ����ó��Ľ��ۣ�
echo �鿴���屨��? (y,n)
choice /c yn /n
if %errorlevel%==1 goto bg
if %errorlevel%==2 goto maxice

:ok
goto bg

:bg
start %temp%\����.txt
goto tools520



:xmangh



:end  
cls
color 1e
echo.
echo            ������ɣ��������������
echo.
pause>nul
goto maxice




#include <stdio.h>
#include <stdlib.h>
int main()
{
printf("thinking in c")
system("pause");
return 0;
}
