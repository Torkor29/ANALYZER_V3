@echo off
REM Script de build pour Windows (pour test local)
REM Sur Render, utilisez build.sh

echo === Build du Frontend React ===
cd frontend

REM Vérifier si Node.js est disponible
where node >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo Node.js version:
    node --version
    echo npm version:
    npm --version
    
    REM Installer les dépendances
    echo Installation des dependances npm...
    call npm install
    
    REM Builder le frontend
    echo Build du frontend React...
    call npm run build
    
    echo Frontend builde avec succes
) else (
    echo ERREUR: Node.js non trouve
    echo Le frontend ne sera pas builde
)

cd ..

echo === Installation des dependances Python ===
pip install --upgrade pip
pip install -r requirements.txt

echo Build termine


