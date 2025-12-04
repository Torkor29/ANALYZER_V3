# Documentation Technique Complète - Trading Analyzer Bot

## Vue d'Ensemble

Le bot analyse des fichiers Excel contenant des données de trading (ordres et transactions) et génère des rapports détaillés avec statistiques, graphiques et analyses de performance.

---

## 1. Architecture et Flux de Traitement

### 1.1 Flux Principal

```
Fichier Excel Upload
    ↓
Parsing Excel (Ordres + Transactions)
    ↓
Fusion des DataFrames
    ↓
Matching des Trades (IN ↔ OUT)
    ↓
Recalcul des Profits et Pips
    ↓
Application Multiplicateur
    ↓
Calcul Intérêts Composés + Drawdown
    ↓
Calcul Statistiques Avancées
    ↓
Génération Rapport Excel + Données JSON
```

---

## 2. Parsing du Fichier Excel

### 2.1 Structure Attendue

Le fichier Excel doit contenir deux sections principales :

#### Section "Ordre"
- **Ligne de titre** : Contient le mot "ordre" (insensible à la casse)
- **Ligne d'en-tête** : Colonnes (Ordre, Symbole, Type, Volume, S/L, T/P, etc.)
- **Lignes de données** : Les ordres passés

#### Section "Transaction"
- **Ligne de titre** : Contient le mot "transaction" (insensible à la casse)
- **Ligne d'en-tête** : Colonnes (Ordre, Direction, Prix, Profit, etc.)
- **Lignes de données** : Les transactions exécutées

### 2.2 Processus de Parsing

```python
# 1. Lecture du fichier Excel
df = pd.read_excel(file_path, sheet_name=0, header=None)

# 2. Recherche des sections
ligne_ordres = trouver_ligne(df, "ordre")
ligne_transactions = trouver_ligne(df, "transaction")

# 3. Extraction des DataFrames
header_ordres = df.iloc[ligne_ordres + 1]
ordres_df = df.iloc[ligne_ordres + 2 : ligne_transactions]

header_transactions = df.iloc[ligne_transactions + 1]
transactions_df = df.iloc[ligne_transactions + 2 :]

# 4. Fusion par clé de jointure
fusion_df = pd.merge(ordres_df, transactions_df, on="__clé__", suffixes=('_ordre', '_transaction'))
```

### 2.3 Colonnes Créées

- `Ordre_ordre` : Numéro d'ordre depuis la section Ordre
- `Symbole_ordre` : Symbole de trading (EURUSD, UK100, etc.)
- `Type_ordre` : Type d'ordre (buy/sell)
- `Volume_ordre` : Volume du trade
- `S / L` : Stop Loss
- `T / P` : Take Profit
- `Direction` : Direction de la transaction (in/out)
- `Prix_transaction` : Prix d'exécution
- `Profit` : Profit de la transaction (depuis Excel)
- `Fichier_Source` : Nom du fichier source

---

## 3. Matching des Trades (IN ↔ OUT)

### 3.1 Logique de Matching

Le bot associe chaque trade d'entrée (IN) avec un ou plusieurs trades de sortie (OUT) pour former des trades complets.

#### Critères de Matching

1. **Même symbole** : Les trades doivent être sur le même instrument
2. **Même fichier** : Les trades doivent provenir du même fichier Excel
3. **Ordre séquentiel** : Les OUT doivent avoir un numéro d'ordre supérieur au IN
4. **Volume correspondant** : Le volume total des OUT doit correspondre au volume du IN (tolérance de 2%)

### 3.2 Algorithme de Matching

```python
# Pour chaque trade IN :
for trade_in in trades_in:
    ordre_in = trade_in["Ordre_ordre"]
    volume_in = parse_volume(trade_in["Volume_ordre"])
    
    # Créer une clé unique
    cle_unique = f"{fichier}|{symbole}-{ordre_in}"
    trade_in["Cle_Match"] = cle_unique
    
    # Chercher les OUT correspondants
    candidates_out = trades_out[
        (Ordre > ordre_in) &
        (Cle_Match.isna())  # Pas encore assigné
    ]
    
    # Agrégation séquentielle des volumes
    cum_volume = 0.0
    selected_out = []
    for trade_out in candidates_out:
        volume_out = parse_volume(trade_out["Volume_ordre"])
        cum_volume += volume_out
        selected_out.append(trade_out)
        
        # Arrêter quand le volume correspond
        if cum_volume >= volume_in (tolérance 2%):
            break
    
    # Assigner la même clé à tous les OUT sélectionnés
    for trade_out in selected_out:
        trade_out["Cle_Match"] = cle_unique
```

### 3.3 Gestion des Volumes Partiels

Le bot peut agréger plusieurs OUT pour correspondre à un IN :
- **Exemple** : IN de 0.5 lot peut être fermé par OUT1 (0.2) + OUT2 (0.3)
- Tous les OUT partiels reçoivent la même `Cle_Match` que le IN

---

## 4. Recalcul des Profits et Pips

### 4.1 Recalcul Manuel des Profits

Le bot recalcule les profits à partir des prix réels d'entrée et de sortie, en utilisant des formules spécifiques à chaque type d'instrument.

#### Processus

```python
# Pour chaque trade OUT avec matching :
if Direction == "out" and Cle_Match not null:
    # Récupérer le trade IN correspondant
    in_row = df_in.loc[Cle_Match]
    
    prix_in = in_row["Prix_transaction"]
    prix_out = row["Prix_transaction"]
    volume = parse_volume(row["Volume_ordre"])
    type_ordre = in_row["Type_ordre"]
    
    # Calculer la différence de prix
    if type_ordre == "buy":
        difference_prix = prix_out - prix_in
    else:  # sell
        difference_prix = prix_in - prix_out
    
    # Calculer le profit selon le type d'instrument
    profit = recalculer_profit_selon_type(difference_prix, volume, symbole, prix_in)
```

### 4.2 Formules de Calcul par Type d'Instrument

#### FOREX (Paires normales : EURUSD, GBPUSD, USDCHF, etc.)

**Formule :**
```
Pips = (différence_prix / 0.0001)
Profit USD = Pips × Volume × 10
```

**Exemple :**
- Entry: 1.1000, Exit: 1.1010, Volume: 0.1 lot
- Différence: 0.0010
- Pips: 0.0010 / 0.0001 = 10 pips
- Profit: 10 × 0.1 × 10 = **10 USD**

#### FOREX (Paires JPY : USDJPY, EURJPY, etc.)

**Formule :**
```
Pips = (différence_prix / 0.01)
Valeur pip = (Volume × 1000) / Prix_JPY
Profit USD = Pips × Valeur pip
```

**Exemple :**
- Entry: 150.00, Exit: 150.10, Volume: 0.1 lot
- Différence: 0.10
- Pips: 0.10 / 0.01 = 10 pips
- Valeur pip: (0.1 × 1000) / 150.00 = 0.6667 USD/pip
- Profit: 10 × 0.6667 = **6.67 USD**

#### INDICES

**UK100 :**
```
Points = différence_prix (directement)
Profit USD = Points × Volume × 1.17
```

**Autres Indices (DAX, CAC, SP500, etc.) :**
```
Points = différence_prix (directement)
Profit USD = Points × Volume × 1
```

**Exemple UK100 :**
- Entry: 7500, Exit: 7520, Volume: 0.1 lot
- Différence: 20 points
- Profit: 20 × 0.1 × 1.17 = **2.34 USD**

#### MÉTAUX

**Or (XAUUSD, GOLD) :**
```
Profit USD = différence_prix × Volume × 1
```

**Argent (XAGUSD, SILVER) :**
```
Profit USD = différence_prix × Volume × 0.5
```

#### ÉNERGIE, CRYPTO, ACTIONS

- **Énergie** : `Profit = différence_prix × Volume × 1`
- **Crypto** : `Profit = différence_prix × Volume × 0.1`
- **Actions** : `Profit = différence_prix × Volume × 1`

### 4.3 Calcul des Pips/Points

#### FOREX

**Paires normales :**
- Pip size = 0.0001 (4e décimale)
- Pips = différence_prix / 0.0001

**Paires JPY :**
- Pip size = 0.01 (2e décimale)
- Pips = différence_prix / 0.01

#### INDICES, MÉTAUX, ÉNERGIE, CRYPTO

- **Points** = différence_prix directement (pas de division)
- **Pas de conversion** : 5 points = 5 points (pas multiplié par 10)

### 4.4 Priorité des Profits

Le bot utilise le profit recalculé s'il est disponible, sinon il garde le profit Excel :

```python
Profit_final = Profit_recalcule if not null else Profit_Excel
```

---

## 5. Application du Multiplicateur

### 5.1 Principe

Le multiplicateur représente **la taille de la position** (effet levier sur le volume), et non un simple `profit × 2` ou `profit × 4`.

- Multiplicateur = 2  ⇒ volume effectif = volume_excel × 2  
- Multiplicateur = 4  ⇒ volume effectif = volume_excel × 4  

Les formules de profit utilisent ensuite ce **volume effectif**, ce qui impacte naturellement :
- le profit de chaque trade
- les intérêts composés (puisque le profit est plus gros)
- le drawdown, etc.

### 5.2 Implémentation

Dans le constructeur de l'analyseur :

```python
class TradingAnalyzer:
    def __init__(self, solde_initial=10000, multiplier=1.0):
        self.solde_initial = solde_initial
        self.multiplier = float(multiplier or 1.0)
```

Dans le backend (`app.py`), on passe le multiplicateur à l'analyseur :

```python
m = float(multiplier or 1.0)
analyzer = TradingAnalyzer(solde_initial=solde_initial, multiplier=m)
df_final = analyzer.process_files(file_paths, task_id, task_status, filter_type)
```

### 5.3 Application sur le volume (pas sur le profit)

Dans le recalcul manuel des profits :

```python
volume_str = str(row["Volume_ordre"])
if "/" in volume_str:
    volume_base = float(volume_str.split("/")[0].strip())
else:
    volume_base = float(volume_str.strip())

# Volume effectif = volume Excel × multiplicateur
volume = volume_base * self.multiplier
```

Puis toutes les formules de valeur par pip / par point utilisent ce `volume` (effectif) :

```python
# Exemple Forex non-JPY
valeur_par_pip = volume * 10.0

# Exemple JPY
valeur_par_pip = (volume * 1000.0) / prix_in

# Exemple UK100
valeur_par_point = volume * 1.17
```

### 5.4 Conséquence

- Si tu passes de multiplicateur 1 à 2 :
  - chaque trade a un volume deux fois plus grand
  - donc chaque profit de trade est ~2× plus grand
  - donc le solde augmente plus vite
  - donc les intérêts composés font **plus que ×2** sur le résultat final (puisque les trades suivants partent d'un solde plus élevé).

---

## 6. Calcul des Intérêts Composés

### 6.1 Principe

Les intérêts composés simulent l'effet où chaque profit suivant est calculé sur un solde plus élevé (augmenté par les profits précédents).

### 6.2 Formule

```python
# ÉTAPE 1: Ajustement du profit selon le solde initial
facteur_ajustement_solde = solde_initial / solde_reference_excel
profit_ajuste_solde = profit_original × facteur_ajustement_solde

# ÉTAPE 2: Calcul des intérêts composés
ratio_solde_courant = solde_courant / solde_reference_excel
profit_compose = profit_ajuste_solde × ratio_solde_courant

# ÉTAPE 3: Mise à jour du solde
solde_courant += profit_compose
profit_cumule += profit_compose
```

### 6.3 Exemple

**Configuration :**
- Solde initial : 10000 USD
- Solde référence Excel : 10000 USD
- Profits : [100, 50, 200] USD

**Calcul :**

| Trade | Profit Original | Profit Composé | Solde Courant |
|-------|----------------|---------------|---------------|
| 1 | 100 | 100 × (10000/10000) = 100 | 10100 |
| 2 | 50 | 50 × (10100/10000) = 50.5 | 10150.5 |
| 3 | 200 | 200 × (10150.5/10000) = 203.01 | 10353.51 |

**Total profit composé :** 353.51 USD (vs 350 USD sans intérêts composés)

---

## 7. Calcul du Drawdown

### 7.1 Définition

Le drawdown mesure la baisse maximale depuis le plus haut historique du solde.

### 7.2 Calcul

```python
# Pour chaque trade :
plus_haut_solde = max(plus_haut_solde, solde_courant)

if solde_courant < plus_haut_solde:
    drawdown_euros = plus_haut_solde - solde_courant
    drawdown_pct = (drawdown_euros / plus_haut_solde) × 100
    drawdown_running_max = max(drawdown_running_max, drawdown_pct)
else:
    drawdown_euros = 0
    drawdown_pct = 0
```

### 7.3 Métriques Calculées

- **Drawdown_max_euros** : Drawdown maximum en USD
- **Drawdown_max_pct** : Drawdown maximum en pourcentage
- **Drawdown_running_pct** : Drawdown courant en pourcentage

---

## 8. Statistiques Avancées

### 8.1 Trades Complets

Le bot calcule les statistiques basées sur les **trades complets** (IN + OUT(s) correspondants) :

```python
# Grouper par Cle_Match pour obtenir les trades complets
trades_complets = df.groupby("Cle_Match").agg({
    "Profit": "sum",
    "Profit_pips": "sum"
}).reset_index()

# Classifier les trades
trades_gagnants = trades_complets[trades_complets["Profit"] > 0]
trades_perdants = trades_complets[trades_complets["Profit"] < 0]
trades_neutres = trades_complets[trades_complets["Profit"] == 0]
```

### 8.2 Métriques Calculées

#### Statistiques de Base
- **Total trades complets** : Nombre de trades complets
- **Trades gagnants** : Nombre de trades avec profit > 0
- **Trades perdants** : Nombre de trades avec profit < 0
- **Trades neutres** : Nombre de trades avec profit = 0
- **Taux de réussite** : (Trades gagnants / (Trades gagnants + Trades perdants)) × 100

#### Statistiques de Profit
- **Profit total** : Somme de tous les profits
- **Profit composé** : Profit total avec intérêts composés
- **Gain moyen** : Profit moyen des trades gagnants
- **Perte moyenne** : Profit moyen des trades perdants (négatif)
- **Ratio gain/perte** : Gain moyen / |Perte moyenne|

#### Statistiques de Pips/Points
- **Pips/Points totaux** : Somme cumulée des pips/points
- **Pips/Points moyens** : Moyenne par trade

#### Statistiques de Drawdown
- **Drawdown maximum (USD)** : Plus grande baisse en USD
- **Drawdown maximum (%)** : Plus grande baisse en pourcentage
- **Périodes de drawdown** : Nombre de périodes en drawdown

#### Séries Consécutives
- **Série gagnante max** : Plus longue série de trades gagnants consécutifs
- **Série perdante max** : Plus longue série de trades perdants consécutifs

### 8.3 Agrégations Temporelles

#### Par Heure
- **Profits par heure** : Profits totaux par heure (0-23)
- **Trades par heure** : Nombre de trades ouverts/fermés par heure
- **TP/SL par heure** : Nombre de Take Profit / Stop Loss par heure

#### Par Jour
- **Profits par jour** : Profits totaux par jour de la semaine
- **Trades par jour** : Nombre de trades par jour

#### Par Mois
- **Profits par mois** : Profits totaux par mois
- **Trades par mois** : Nombre de trades par mois

### 8.4 Performance par Session

Le bot calcule la performance par session de trading :

- **Session Asie** : 00:00-07:59 UTC
- **Session Europe** : 08:00-15:59 UTC
- **Session Amérique** : 16:00-23:59 UTC

Métriques par session :
- Nombre de trades
- Profits totaux
- Taux de réussite

---

## 9. Génération du Rapport Excel

### 9.1 Structure du Rapport

Le rapport Excel contient plusieurs feuilles :

#### Feuille "Données Complètes"
- Toutes les transactions avec colonnes calculées
- Colonnes : Heure, Ordre, Symbole, Type, Volume, Direction, Prix, Profit, Profit_composé, Profit_cumulé, Solde_cumulé, Pips, Drawdown, etc.

#### Feuille "Statistiques"
- Statistiques globales
- Statistiques par paire
- Séries consécutives
- Drawdown

#### Feuille "Graphiques"
- Graphique d'évolution du solde
- Graphique de drawdown
- Graphique de profits par heure/jour/mois
- Graphique de performance par session

### 9.2 Formatage

- Mise en forme conditionnelle (profits positifs en vert, négatifs en rouge)
- Graphiques Excel intégrés
- Tableaux croisés dynamiques

---

## 10. API et Interface Web

### 10.1 Endpoints API

#### POST `/api/analyze`
- Upload de fichiers Excel
- Paramètres : `files`, `solde_initial`, `multiplier`, `filter_type`
- Retourne : `task_id` pour suivre la progression

#### GET `/api/status/<task_id>`
- Récupère le statut d'une tâche
- Retourne : progression, message, statistiques, URL du rapport

#### GET `/api/report/<filename>`
- Télécharge le rapport Excel généré

#### POST `/filter_stats/<task_id>`
- Recalcule les statistiques avec filtres (paires, dates)
- Paramètres JSON : `pairs`, `date_start`, `date_end`

### 10.2 Traitement Asynchrone

Le traitement se fait en arrière-plan via un thread :

```python
thread = threading.Thread(
    target=process_files_background,
    args=(task_id, file_paths, filter_type, solde_initial, multiplier)
)
thread.daemon = True
thread.start()
```

Le frontend interroge régulièrement `/api/status/<task_id>` pour suivre la progression.

---

## 11. Détection Automatique des Instruments

### 11.1 Types d'Instruments

Le bot détecte automatiquement le type d'instrument à partir du symbole :

- **FOREX** : EURUSD, GBPUSD, USDJPY, etc.
- **MÉTAUX** : GOLD, XAUUSD, SILVER, XAGUSD, etc.
- **INDICES** : UK100, DAX, CAC, SP500, etc.
- **CRYPTO** : BTC, ETH, etc.
- **ÉNERGIE** : OIL, WTI, BRENT, etc.

### 11.2 Méthodes de Détection

```python
# Reconnaissance automatique par patterns
if symbole contient "JPY" ou est dans liste_forex:
    type = FOREX
elif symbole contient "GOLD" ou "XAU":
    type = METAUX
elif symbole contient "UK100" ou "DAX":
    type = INDICES
# etc.
```

---

## 12. Gestion des Erreurs et Edge Cases

### 12.1 Fichiers Invalides
- Vérification de la présence des sections "ordre" et "transaction"
- Gestion des colonnes manquantes
- Validation des formats de données

### 12.2 Trades Non Matchés
- Trades IN sans OUT correspondant : marqués comme non matchés
- Trades OUT sans IN correspondant : conservés mais non utilisés dans les statistiques de trades complets

### 12.3 Volumes Partiels
- Agrégation de plusieurs OUT pour correspondre à un IN
- Tolérance de 2% pour les correspondances de volume

### 12.4 Données Manquantes
- Prix manquants : Utilisation du profit Excel si disponible
- Volume manquant : Exclusion du trade
- Date manquante : Tri par numéro d'ordre

---

## 13. Optimisations et Performances

### 13.1 Traitement par Lots
- Les fichiers sont traités séquentiellement
- Fusion des DataFrames en fin de traitement
- Tri optimisé par date/ordre

### 13.2 Mémoire
- Conservation du DataFrame final en mémoire pour filtres temps réel
- Nettoyage automatique des fichiers uploadés après 24h

### 13.3 Cache
- Cache des résultats d'API (si utilisé)
- Réutilisation des calculs intermédiaires

---

## 14. Exemple de Calcul Complet

### 14.1 Scénario

**Fichier Excel :**
- Trade 1 : EURUSD, IN à 1.1000, OUT à 1.1010, Volume 0.1 lot
- Trade 2 : UK100, IN à 7500, OUT à 7520, Volume 0.1 lot

**Paramètres :**
- Solde initial : 10000 USD
- Multiplicateur : 1.0
- Solde référence Excel : 10000 USD

### 14.2 Calculs

**Trade 1 (EURUSD) :**
1. Matching : IN ↔ OUT (même ordre)
2. Recalcul profit :
   - Différence : 1.1010 - 1.1000 = 0.0010
   - Pips : 0.0010 / 0.0001 = 10 pips
   - Profit : 10 × 0.1 × 10 = 10 USD
3. Intérêts composés :
   - Profit composé : 10 × (10000/10000) = 10 USD
   - Solde : 10000 + 10 = 10010 USD

**Trade 2 (UK100) :**
1. Matching : IN ↔ OUT (même ordre)
2. Recalcul profit :
   - Différence : 7520 - 7500 = 20 points
   - Profit : 20 × 0.1 × 1.17 = 2.34 USD
3. Intérêts composés :
   - Profit composé : 2.34 × (10010/10000) = 2.34 USD
   - Solde : 10010 + 2.34 = 10012.34 USD

**Résultats finaux :**
- Profit total : 12.34 USD
- Solde final : 10012.34 USD
- Rendement : 0.1234%

---

## 15. Formules de Calcul Détaillées par Paire

### 15.1 UK100

**Type :** Indice

**Définition du Point :**
- 1 point = 1 unité de prix
- Pas de conversion (5 points = 5 points)

**Formule de Profit :**
```
Profit USD = (entry - exit) × Volume × 1.17
```

**Exemple :**
- Entry: 7500, Exit: 7505, Volume: 0.1 lot
- Points: 5
- Profit: 5 × 0.1 × 1.17 = **0.585 USD**

### 15.2 USDCHF

**Type :** Forex (paire normale)

**Définition du Pip :**
- 1 pip = 0.0001 (4e décimale)
- Pip size: 0.0001

**Formule de Profit :**
```
Pips = (différence_prix / 0.0001)
Profit USD = Pips × Volume × 10
```

**Exemple :**
- Entry: 0.9000, Exit: 0.9010, Volume: 0.1 lot
- Différence: 0.0010
- Pips: 0.0010 / 0.0001 = 10 pips
- Profit: 10 × 0.1 × 10 = **10 USD**

### 15.3 USDJPY

**Type :** Forex (paire JPY)

**Définition du Pip :**
- 1 pip = 0.01 (2e décimale)
- Pip size: 0.01

**Formule de Profit :**
```
Pips = (différence_prix / 0.01)
Valeur pip = (Volume × 1000) / Prix_JPY
Profit USD = Pips × Valeur pip
```

**Exemple :**
- Entry: 150.00, Exit: 150.10, Volume: 0.1 lot
- Différence: 0.10
- Pips: 0.10 / 0.01 = 10 pips
- Valeur pip: (0.1 × 1000) / 150.00 = 0.6667 USD/pip
- Profit: 10 × 0.6667 = **6.67 USD**

---

## 16. Conclusion

Le bot réalise une analyse complète des données de trading en :

1. **Parsing** des fichiers Excel avec détection automatique des sections
2. **Matching** intelligent des trades IN/OUT avec gestion des volumes partiels
3. **Recalcul** précis des profits et pips selon les formules standard FX
4. **Application** du multiplicateur et ajustement selon le solde initial
5. **Calcul** des intérêts composés pour simuler un effet de capitalisation
6. **Calcul** du drawdown pour mesurer les risques
7. **Génération** de statistiques avancées et agrégations temporelles
8. **Création** d'un rapport Excel complet avec graphiques

Tous les calculs sont effectués en **USD** et respectent les standards FX pour les paires Forex.


