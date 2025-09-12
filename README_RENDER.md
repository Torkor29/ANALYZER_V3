# 🚀 Guide de Déploiement Render - Trading Analyzer

## ✅ Configuration Optimisée pour Render

Cette version est spécialement optimisée pour un déploiement simple et fiable sur Render.

### 📋 Fichiers de Configuration

| Fichier | Description |
|---------|-------------|
| `requirements.txt` | Dépendances Python stables |
| `runtime.txt` | Python 3.10.11 (compatible Render) |
| `Procfile` | Configuration Gunicorn |
| `render.yaml` | Configuration automatique |

### 🔧 Versions Utilisées (Testées et Stables)

- **Python:** 3.10.11
- **Flask:** 2.2.5
- **Pandas:** 1.5.3
- **OpenPyXL:** 3.0.10
- **Gunicorn:** 20.1.0

## 🚀 Instructions de Déploiement

### Étape 1 : Créer le Service Render

1. **Connexion à Render**
   - Allez sur [render.com](https://render.com)
   - Connectez-vous avec GitHub

2. **Nouveau Web Service**
   - Cliquez sur **"New +"** → **"Web Service"**
   - Sélectionnez le repository `Torkor29/New-Analyzer`
   - Branche : `main`

### Étape 2 : Configuration Automatique

Render détectera automatiquement :
- ✅ **Runtime :** Python 3.10.11
- ✅ **Build Command :** `pip install -r requirements.txt`
- ✅ **Start Command :** `gunicorn app:app --bind 0.0.0.0:$PORT --workers 1`

### Étape 3 : Paramètres du Service

**Nom du service :** `trading-analyzer` (ou votre choix)
**Plan :** Free (0$/mois)
**Région :** Frankfurt ou Oregon

### Étape 4 : Variables d'Environnement

Render configurera automatiquement :
- `PORT` (automatique)
- `SECRET_KEY` (générée automatiquement)
- `FLASK_ENV=production`

## 📊 Temps de Déploiement

- **Build :** 2-3 minutes
- **Démarrage :** 30-60 secondes
- **URL générée :** `https://trading-analyzer-xxx.onrender.com`

## ✅ Vérification du Succès

Logs de succès à surveiller :
```
==> Using Python version 3.10.11
==> Installing dependencies from requirements.txt
==> Successfully installed Flask pandas openpyxl gunicorn
==> Starting server with gunicorn
==> Your service is live at https://...
```

## 🔄 Redéploiement

- **Automatique :** À chaque push sur GitHub
- **Manuel :** Bouton "Manual Deploy" sur Render

## 🌐 Fonctionnalités de l'Application

Une fois déployée, l'application offre :
- 📁 Upload de fichiers Excel par glisser-déposer
- 🔍 Analyse Forex, indices, métaux, crypto
- 📊 Rapports Excel détaillés avec graphiques
- 💰 Calculs d'intérêts composés et drawdown
- 📱 Interface responsive

## 🛠️ Maintenance

- **Plan gratuit :** 500 heures/mois
- **Endormissement :** Après 15min d'inactivité
- **Réveil :** 1-2 minutes au premier accès
- **SSL :** Automatique et gratuit

---

**Configuration testée et validée pour Render ✅**