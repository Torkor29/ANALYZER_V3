# 🚀 Trading Analyzer - Version Web

## 📊 Description

Trading Analyzer est une application web professionnelle pour analyser vos performances de trading. Cette interface moderne et intuitive vous permet de :

- 📁 **Déposer facilement vos fichiers Excel** de trading par glisser-déposer
- 🔍 **Analyser différents types d'instruments** : Forex, indices, métaux, crypto, énergie
- 📈 **Obtenir des rapports détaillés** avec statistiques avancées et graphiques
- 💰 **Calculer les intérêts composés** et le drawdown
- 📊 **Visualiser vos performances** de manière claire et professionnelle

## 🛠️ Installation et Lancement

### Prérequis
- Python 3.7 ou plus récent
- Les packages listés dans `requirements.txt`

### Installation des dépendances

```bash
pip install -r requirements.txt
```

### Lancement de l'application

```bash
python app.py
```

L'application sera accessible sur : **http://localhost:5000**

## 🎯 Fonctionnalités

### Interface Web
- ✨ **Design moderne et responsive** adapté à tous les écrans
- 🎨 **Interface intuitive** avec glisser-déposer
- ⚡ **Traitement en temps réel** avec barre de progression
- 📱 **Compatible mobile et desktop**

### Analyses Disponibles
1. **📊 Tous les instruments** - Analyse complète de tous vos trades
2. **💱 Forex uniquement** - Analyse spécialisée des paires de devises
3. **📈 Autres instruments** - Indices, métaux, crypto, énergie, actions

### Rapports Générés
- 📋 **Résumé global** avec statistiques clés
- 📊 **Données complètes** exportées vers Excel
- 🔍 **Analyse par instrument** détaillée
- 🏷️ **Analyse par type d'instrument**
- 📈 **Graphiques et visualisations** intégrés

### Statistiques Calculées
- 💰 **Profit total** (linéaire et composé)
- 📈 **Rendement global** en pourcentage
- 🎯 **Taux de réussite** des trades
- 📉 **Drawdown maximum** et périodes
- 🔥 **Séries gagnantes/perdantes** consécutives
- 📊 **Pips/Points totaux** par instrument

## 📁 Structure des Fichiers

```
trading-analyzer-web/
├── app.py                          # Application Flask principale
├── trading_analyzer_unified.py     # Moteur d'analyse
├── requirements.txt                # Dépendances Python
├── README_WEB.md                   # Documentation
├── templates/
│   └── index.html                  # Interface web
├── uploads/                        # Dossier temporaire des fichiers
└── reports/                        # Rapports générés
```

## 🔧 Configuration

### Paramètres modifiables dans `app.py`

```python
# Limite de taille des fichiers (défaut: 50MB)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

# Extensions de fichiers autorisées
ALLOWED_EXTENSIONS = {'xlsx', 'xls'}

# Port d'écoute (défaut: 5000)
app.run(debug=True, host='0.0.0.0', port=5000)
```

### Solde Initial
- Par défaut : **10 000 €**
- Modifiable via l'interface web
- Utilisé pour calculer les rendements et intérêts composés

## 🛡️ Sécurité

- ✅ **Validation des fichiers** : seuls les fichiers Excel sont acceptés
- 🗑️ **Nettoyage automatique** : fichiers supprimés après 24h
- 🔒 **Traitement local** : vos données restent sur votre machine
- 📁 **Dossiers temporaires** : uploads et rapports isolés

## 📊 Format des Fichiers Excel

L'application analyse les fichiers Excel avec la structure suivante :

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

## 🚨 Résolution des Problèmes

### Erreurs Communes

1. **"Aucune donnée trouvée"**
   - Vérifiez que vos fichiers contiennent les sections "Ordre" et "Transaction"
   - Assurez-vous que les colonnes requises sont présentes

2. **"Fichier trop volumineux"**
   - Limite actuelle : 50MB par fichier
   - Divisez les gros fichiers en plusieurs parties

3. **"Erreur de traitement"**
   - Vérifiez le format de vos fichiers Excel
   - Consultez les logs de l'application pour plus de détails

### Support
En cas de problème, vérifiez :
- Les logs dans la console où vous avez lancé `python app.py`
- La structure de vos fichiers Excel
- Les permissions d'écriture dans les dossiers `uploads/` et `reports/`

## 🔄 Mises à Jour

Pour mettre à jour l'application :

1. Sauvegardez vos fichiers importants
2. Remplacez les fichiers de l'application
3. Vérifiez les nouvelles dépendances dans `requirements.txt`
4. Relancez l'application

## 📈 Exemple d'Utilisation

1. **Lancez l'application** : `python app.py`
2. **Ouvrez votre navigateur** : http://localhost:5000
3. **Déposez vos fichiers Excel** dans la zone de glisser-déposer
4. **Choisissez le type d'analyse** : Tous, Forex, ou Autres instruments
5. **Définissez votre solde initial**
6. **Cliquez sur "Lancer l'analyse"**
7. **Suivez la progression** en temps réel
8. **Consultez les résultats** et téléchargez votre rapport Excel

## 🎯 Avantages de la Version Web

- 🌐 **Accessible depuis n'importe quel navigateur**
- 🖱️ **Interface graphique intuitive** (vs ligne de commande)
- 📊 **Visualisation en temps réel** des résultats
- 📱 **Design responsive** pour tous les appareils
- ⚡ **Traitement asynchrone** avec feedback visuel
- 📁 **Gestion automatique des fichiers**
- 🔄 **Pas d'installation complexe** pour les utilisateurs finaux

---

**Développé avec ❤️ pour optimiser vos analyses de trading**