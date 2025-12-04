# Script PowerShell pour démarrer le frontend et le maintenir actif
# Ce script redémarre automatiquement le frontend s'il s'arrête

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Démarrage du Frontend React/Vite" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$frontendDir = Join-Path $PSScriptRoot "frontend"

if (-not (Test-Path $frontendDir)) {
    Write-Host "ERREUR: Le dossier frontend n'existe pas!" -ForegroundColor Red
    exit 1
}

Set-Location $frontendDir

# Vérifier si node_modules existe
if (-not (Test-Path "node_modules")) {
    Write-Host "Installation des dépendances npm..." -ForegroundColor Yellow
    npm install
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERREUR: Échec de l'installation des dépendances" -ForegroundColor Red
        exit 1
    }
}

Write-Host "Démarrage du serveur de développement Vite..." -ForegroundColor Green
Write-Host "Le frontend sera accessible sur http://localhost:5173" -ForegroundColor Green
Write-Host ""
Write-Host "Appuyez sur Ctrl+C pour arrêter le serveur" -ForegroundColor Yellow
Write-Host ""

# Boucle infinie pour redémarrer automatiquement en cas d'arrêt
while ($true) {
    try {
        # Démarrer npm run dev
        npm run dev
        
        # Si on arrive ici, le processus s'est arrêté
        Write-Host ""
        Write-Host "Le serveur s'est arrêté. Redémarrage dans 3 secondes..." -ForegroundColor Yellow
        Start-Sleep -Seconds 3
    }
    catch {
        Write-Host "Erreur détectée: $_" -ForegroundColor Red
        Write-Host "Redémarrage dans 5 secondes..." -ForegroundColor Yellow
        Start-Sleep -Seconds 5
    }
}

