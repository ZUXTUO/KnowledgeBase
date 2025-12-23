@echo off

set /p commitMessage=update: 

git add .
git commit -m "%commitMessage%"
git push
git push

pause