#!/bin/bash
# Script de build pour Render
# Build le frontend React puis installe les dépendances Python

set -e  # Arrêter en cas d'erreur

echo "=== Build du Frontend React ==="
cd frontend

# Vérifier si Node.js est disponible
if command -v node &> /dev/null; then
    echo "Node.js version: $(node --version)"
    echo "npm version: $(npm --version)"
    
    # Installer les dépendances
    echo "Installation des dépendances npm..."
    npm install
    
    # Builder le frontend
    echo "Build du frontend React..."
    npm run build
    
    echo "✅ Frontend buildé avec succès"
else
    echo "⚠️  Node.js non trouvé, le frontend ne sera pas buildé"
    echo "   Le frontend devra être buildé manuellement ou via un service séparé"
fi

cd ..

echo "=== Installation des dépendances Python ==="
pip install --upgrade pip
pip install -r requirements.txt

echo "✅ Build terminé"

