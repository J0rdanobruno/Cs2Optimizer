@echo off
title CS2 Windows Optimizer
color 0B

:: Sprawdzenie czy skrypt jest uruchomiony jako Administrator
net session >nul 2>&1
if %errorLevel% == 0 (
    goto :run
) else (
    echo.
    echo  ========================================
    echo   Need permisions!
    echo   Open again as Administrator!
    echo  ========================================
    echo.
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit
)

:run
cd /d "%~dp0"

echo.
echo  ========================================
echo       CS2 Windows Optimizer
echo  ========================================
echo.
echo  Opening files...
echo.

:: Sprawdza czy jest python czy py
where python >nul 2>&1
if %errorLevel% == 0 (
    python "OptiCS2.py"
) else (
    where py >nul 2>&1
    if %errorLevel% == 0 (
        py "OptiCS2.py"
    ) else (
        echo.
        echo  ERROR PYTHON NOT FOUND!
        echo.
        pause
        exit
    )
)

echo.
pause