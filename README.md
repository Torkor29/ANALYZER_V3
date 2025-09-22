# 🚀 Trading Analyzer - Application Web

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

## 📊 Description

**Trading Analyzer** est une application web professionnelle pour analyser vos performances de trading. Cette interface moderne et intuitive vous permet d'analyser vos fichiers Excel de trading et d'obtenir des rapports détaillés avec statistiques avancées.

🌐 **[Démo en ligne](https://new-analyzer.onrender.com)** *(bientôt disponible)*

## ✨ Fonctionnalités

### 📈 Analyses Disponibles
- **📊 Tous les instruments** - Analyse complète de tous vos trades
- **💱 Forex uniquement** - Analyse spécialisée des paires de devises  
- **📈 Autres instruments** - Indices, métaux, crypto, énergie, actions

### 🎯 Statistiques Calculées
- 💰 **Profit total** (linéaire et composé)
- 📈 **Rendement global** en pourcentage
- 🎯 **Taux de réussite** des trades
- 📉 **Drawdown maximum** et périodes
- 🔥 **Séries gagnantes/perdantes** consécutives
- 📊 **Pips/Points totaux** par instrument

### 🛠️ Interface
- ✨ **Design moderne et responsive** 
- 🎨 **Glisser-déposer** de fichiers
- ⚡ **Traitement en temps réel** avec barre de progression
- 📱 **Compatible mobile et desktop**
- 📋 **Rapports Excel détaillés** avec graphiques

## 🚀 Déploiement sur Render

### Déploiement Automatique
[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/Torkor29/New-Analyzer.git)

### Déploiement Manuel
1. **Fork ce repository**
2. **Connectez-vous à [Render](https://render.com)**
3. **Créez un nouveau Web Service**
4. **Connectez votre repository GitHub**
5. **Configurez les paramètres :**
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
   - **Environment:** `python`

### Variables d'Environnement
Render configurera automatiquement :
- `PORT` - Port d'écoute (automatique)
- `SECRET_KEY` - Clé secrète Flask (générée automatiquement)
- `FLASK_ENV=production` - Mode production

## 💻 Installation Locale

### Prérequis
- Python 3.11+
- Git

### Installation
```bash
# Cloner le repository
git clone https://github.com/Torkor29/New-Analyzer.git
cd New-Analyzer

# Installer les dépendances
pip install -r requirements.txt

# Lancer l'application
python app.py
```

L'application sera accessible sur : **http://localhost:5000**

## 📁 Structure du Projet

```
trading-analyzer/
├── app.py                          # Application Flask principale
├── trading_analyzer_unified.py     # Moteur d'analyse
├── requirements.txt                # Dépendances Python
├── runtime.txt                     # Version Python pour Render
├── Procfile                        # Configuration Render/Heroku
├── render.yaml                     # Configuration Render
├── templates/
│   └── index.html                  # Interface web
├── uploads/                        # Dossier temporaire des fichiers
└── reports/                        # Rapports générés
```

## 📊 Format des Fichiers Excel

### Sections Requises
1. **Section "Ordre"** - Informations sur les ordres passés
2. **Section "Transaction"** - Détails des transactions exécutées

### Colonnes Importantes
- **Symbole** : Nom de l'instrument (EURUSD, GOLD, DAX, etc.)
- **Type** : Type d'ordre (buy/sell)
- **Volume** : Taille de la position
- **Profit** : Résultat en euros
- **Prix** : Prix d'exécution
- **T/P** : Take Profit
- **S/L** : Stop Loss

## 🛡️ Sécurité

- ✅ **Validation des fichiers** : seuls les fichiers Excel sont acceptés
- 🗑️ **Nettoyage automatique** : fichiers supprimés après 24h
- 🔒 **Traitement sécurisé** : vos données restent privées
- 📁 **Stockage temporaire** : uploads et rapports isolés

## 🔧 Configuration

### Paramètres Modifiables
- **Limite de fichier** : 50MB par défaut
- **Solde initial** : 10,000€ par défaut (modifiable via interface)
- **Extensions autorisées** : .xlsx, .xls

## 📈 Exemple d'Utilisation

1. **Ouvrez l'application** dans votre navigateur
2. **Déposez vos fichiers Excel** dans la zone de glisser-déposer
3. **Choisissez le type d'analyse** : Tous, Forex, ou Autres instruments
4. **Définissez votre solde initial**
5. **Cliquez sur "Lancer l'analyse"**
6. **Suivez la progression** en temps réel
7. **Consultez les résultats** et téléchargez votre rapport Excel

## 🚨 Support & Problèmes

### Erreurs Communes
- **"Aucune donnée trouvée"** : Vérifiez la structure de vos fichiers Excel
- **"Fichier trop volumineux"** : Limite de 50MB par fichier
- **"Erreur de traitement"** : Vérifiez le format et les colonnes requises

### Obtenir de l'Aide
- 📋 Créez une [Issue](https://github.com/Torkor29/New-Analyzer/issues)
- 📧 Contactez le support via GitHub

## 🔄 Contributions

Les contributions sont les bienvenues ! 

1. **Fork** le projet
2. **Créez** une branche pour votre fonctionnalité
3. **Commitez** vos changements
4. **Push** vers la branche
5. **Ouvrez** une Pull Request

## 📜 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 🎯 Roadmap

- [ ] 📊 Graphiques interactifs
- [ ] 🔄 Import automatique depuis MT4/MT5
- [ ] 📱 Application mobile
- [ ] 🤖 Analyse IA avancée
- [ ] 📈 Alertes en temps réel

---

**Développé avec ❤️ pour optimiser vos analyses de trading**

⭐ **N'oubliez pas de mettre une étoile au projet si vous le trouvez utile !**