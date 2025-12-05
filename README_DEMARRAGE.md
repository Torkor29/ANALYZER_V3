# Guide de Démarrage - Trading Analyzer

Ce guide explique comment démarrer le backend et le frontend de l'application Trading Analyzer.

## 🚀 Démarrage Rapide

### Option 1 : Démarrer les deux serveurs ensemble (Recommandé)

**Windows (PowerShell) :**
```powershell
.\start_all.ps1
```

**Windows (CMD/Batch) :**
```batch
start_all.bat
```

Cela ouvrira deux fenêtres séparées :
- Une pour le backend Flask (port 5000)
- Une pour le frontend React/Vite (port 5173)

### Option 2 : Démarrer séparément

#### Backend Flask uniquement

**PowerShell :**
```powershell
.\start_backend.ps1
```

**Ou manuellement :**
```bash
python app.py
```

Le backend sera accessible sur : **http://localhost:5000**

#### Frontend React/Vite uniquement

**PowerShell :**
```powershell
.\start_frontend.ps1
```

**Ou manuellement :**
```bash
cd frontend
npm install  # Si première fois
npm run dev
```

Le frontend sera accessible sur : **http://localhost:5173**

## 📋 Prérequis

1. **Python 3.8+** installé
2. **Node.js et npm** installés
3. **Dépendances Python** installées :
   ```bash
   pip install -r requirements.txt
   ```
4. **Dépendances Node.js** installées (automatique au premier démarrage) :
   ```bash
   cd frontend
   npm install
   ```

## 🔄 Redémarrage Automatique

Les scripts PowerShell (`start_backend.ps1` et `start_frontend.ps1`) incluent une fonctionnalité de redémarrage automatique :
- Si le serveur s'arrête pour une raison quelconque, il redémarre automatiquement après 3 secondes
- Utile pour maintenir les serveurs actifs en permanence

## 🛑 Arrêter les Serveurs

Pour arrêter les serveurs :
- Fermez les fenêtres PowerShell où ils tournent
- Ou appuyez sur `Ctrl+C` dans chaque fenêtre

## 🌐 Accès à l'Application

Une fois les deux serveurs démarrés :
- **Interface Web** : http://localhost:5173
- **API Backend** : http://localhost:5000
- **API Health Check** : http://localhost:5000/api/health
- **Liste des Brokers** : http://localhost:5000/api/brokers

## ⚙️ Configuration

### Variables d'environnement (optionnel)

Vous pouvez créer un fichier `.env` à la racine du projet pour configurer :
- `PORT` : Port du backend Flask (défaut: 5000)
- `FLASK_ENV` : Environnement Flask (development/production)

## 📝 Notes

- Le frontend utilise Vite qui redémarre automatiquement lors des modifications de code
- Le backend Flask doit être redémarré manuellement après modification du code Python
- Les scripts PowerShell fonctionnent sur Windows 10/11
- Pour Linux/Mac, utilisez les commandes manuelles ou adaptez les scripts

## 🐛 Dépannage

### Le frontend ne démarre pas
1. Vérifiez que Node.js est installé : `node --version`
2. Installez les dépendances : `cd frontend && npm install`
3. Vérifiez qu'aucun autre processus n'utilise le port 5173

### Le backend ne démarre pas
1. Vérifiez que Python est installé : `python --version`
2. Installez les dépendances : `pip install -r requirements.txt`
3. Vérifiez qu'aucun autre processus n'utilise le port 5000

### Erreur "Port already in use"
Arrêtez le processus qui utilise le port :
```powershell
# Pour le port 5000 (backend)
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Pour le port 5173 (frontend)
netstat -ano | findstr :5173
taskkill /PID <PID> /F
```

