# Script PowerShell pour démarrer le backend Flask
# Ce script redémarre automatiquement le backend s'il s'arrête

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Démarrage du Backend Flask" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$scriptDir = $PSScriptRoot

if (-not (Test-Path (Join-Path $scriptDir "app.py"))) {
    Write-Host "ERREUR: Le fichier app.py n'existe pas!" -ForegroundColor Red
    exit 1
}

Set-Location $scriptDir

Write-Host "Démarrage du serveur Flask..." -ForegroundColor Green
Write-Host "Le backend sera accessible sur http://localhost:5000" -ForegroundColor Green
Write-Host ""
Write-Host "Appuyez sur Ctrl+C pour arrêter le serveur" -ForegroundColor Yellow
Write-Host ""

# Boucle infinie pour redémarrer automatiquement en cas d'arrêt
while ($true) {
    try {
        # Démarrer Flask
        python app.py
        
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

