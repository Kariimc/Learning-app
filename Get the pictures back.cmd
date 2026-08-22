@echo off
title Reading Land - get the pictures back
cd /d "%~dp0"
echo.
echo   Bringing the app's pictures and voices down to this laptop.
echo   This can take a couple of minutes the first time.
echo.
git lfs pull
echo.
echo   Done. Checking what arrived...
echo.
powershell -NoProfile -Command "$i=(Get-ChildItem 'assets\images' -Recurse -File ^| Where-Object {$_.Length -gt 5000}).Count; $a=(Get-ChildItem 'assets\audio' -Recurse -File ^| Where-Object {$_.Length -gt 5000}).Count; Write-Host ('   ' + $i + ' real pictures and ' + $a + ' real voice clips are now on this laptop.')"
echo.
echo   If those numbers are 0, tell Claude. Otherwise you are good.
echo.
pause
