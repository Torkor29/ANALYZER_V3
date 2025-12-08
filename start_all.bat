@echo off
REM Script batch pour démarrer le backend ET le frontend simultanément
REM Compatible avec Windows

echo ========================================
echo   Demarrage Backend + Frontend
echo ========================================
echo.

REM Démarrer le backend dans une nouvelle fenêtre
echo Demarrage du backend Flask...
start "Backend Flask" powershell -NoExit -File "%~dp0start_backend.ps1"

REM Attendre un peu
timeout /t 2 /nobreak >nul

REM Démarrer le frontend dans une nouvelle fenêtre
echo Demarrage du frontend React/Vite...
start "Frontend React" powershell -NoExit -File "%~dp0start_frontend.ps1"

echo.
echo Les deux serveurs sont en cours de demarrage dans des fenetres separees
echo.
echo Backend:  http://localhost:5000
echo Frontend: http://localhost:5173
echo.
echo Fermez les fenetres pour arreter les serveurs
echo.
pause


