# Script PowerShell pour démarrer le backend ET le frontend simultanément
# Utilise des fenêtres séparées pour chaque serveur

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Démarrage Backend + Frontend" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$scriptDir = $PSScriptRoot

# Démarrer le backend dans une nouvelle fenêtre
Write-Host "Démarrage du backend Flask..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-File", (Join-Path $scriptDir "start_backend.ps1") -WindowStyle Normal

# Attendre un peu avant de démarrer le frontend
Start-Sleep -Seconds 2

# Démarrer le frontend dans une nouvelle fenêtre
Write-Host "Démarrage du frontend React/Vite..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-File", (Join-Path $scriptDir "start_frontend.ps1") -WindowStyle Normal

Write-Host ""
Write-Host "✅ Les deux serveurs sont en cours de démarrage dans des fenêtres séparées" -ForegroundColor Green
Write-Host ""
Write-Host "Backend:  http://localhost:5000" -ForegroundColor Cyan
Write-Host "Frontend: http://localhost:5173" -ForegroundColor Cyan
Write-Host ""
Write-Host "Fermez les fenêtres PowerShell pour arrêter les serveurs" -ForegroundColor Yellow

