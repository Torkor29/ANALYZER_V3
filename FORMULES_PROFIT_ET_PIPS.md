# Formules de Calcul des Profits et Définition des Pips/Points

## 1. Formules de Calcul du Profit (USD) par Type d'Instrument

### FOREX (Paires normales : EURUSD, GBPUSD, USDCHF, etc.)

**Formule :**
```
Profit USD = Pips × Volume × 10
```

**Détails :**
- **Pips** = (différence_prix / pip_size)
- **Pip size** = 0.0001 (4 décimales) pour la plupart des paires
- **Valeur par pip** = 10 USD par pip par 0.1 lot
- **Exemple** : Si différence = 0.0010, volume = 0.1 lot
  - Pips = 0.0010 / 0.0001 = 10 pips
  - Profit = 10 × 0.1 × 10 = **10 USD**

---

### FOREX (Paires JPY : USDJPY, EURJPY, etc.)

**Formule :**
```
Profit USD = Pips × (Volume × 1000) / Prix_JPY
```

**Détails :**
- **Pips** = (différence_prix / pip_size)
- **Pip size** = 0.01 (2-3 décimales) pour les paires JPY
- **Valeur par pip** = (Volume × 1000) / Prix_JPY (formule standard FX)
- **Exemple** : Si différence = 0.10, volume = 0.1 lot, Prix_IN = 150.00
  - Pips = 0.10 / 0.01 = 10 pips
  - Valeur pip = (0.1 × 1000) / 150.00 = 0.6667 USD/pip
  - Profit = 10 × 0.6667 = **6.67 USD**

---

### INDICES

#### UK100 spécifiquement

**Formule :**
```
Profit USD = (entry - exit) × Volume × 1.17
```

**Détails :**
- **Points** = différence_prix directement (pas de division)
- **Valeur par point** = 1.17 USD par point par 0.1 lot
- **Exemple** : Si entry = 7500, exit = 7520, volume = 0.1 lot
  - Différence = 20 points
  - Profit = 20 × 0.1 × 1.17 = **2.34 USD**

#### Autres Indices (DAX, CAC, SP500, etc.)

**Formule :**
```
Profit USD = (entry - exit) × Volume × 1
```

**Détails :**
- **Points** = différence_prix directement
- **Valeur par point** = 1 USD par point par 0.1 lot
- **Exemple** : Si entry = 15000, exit = 15050, volume = 0.1 lot
  - Différence = 50 points
  - Profit = 50 × 0.1 × 1 = **5 USD**

---

### MÉTAUX

#### Or (XAUUSD, GOLD)

**Formule :**
```
Profit USD = (entry - exit) × Volume × 1
```

**Détails :**
- **Points** = différence_prix directement
- **Valeur par point** = 1 USD par point par 0.1 lot
- **Exemple** : Si entry = 2000, exit = 2010, volume = 0.1 lot
  - Différence = 10 points
  - Profit = 10 × 0.1 × 1 = **1 USD**

#### Argent (XAGUSD, SILVER)

**Formule :**
```
Profit USD = (entry - exit) × Volume × 0.5
```

**Détails :**
- **Points** = différence_prix directement
- **Valeur par point** = 0.5 USD par point par 0.1 lot
- **Exemple** : Si entry = 25, exit = 26, volume = 0.1 lot
  - Différence = 1 point
  - Profit = 1 × 0.1 × 0.5 = **0.05 USD**

---

### ÉNERGIE (Pétrole)

**Formule :**
```
Profit USD = (entry - exit) × Volume × 1
```

**Détails :**
- **Points** = différence_prix directement
- **Valeur par point** = 1 USD par point par 0.1 lot

---

### CRYPTO

**Formule :**
```
Profit USD = (entry - exit) × Volume × 0.1
```

**Détails :**
- **Points** = différence_prix directement
- **Valeur par point** = 0.1 USD par point par 0.1 lot

---

## 2. Définition du Pip/Point

### UK100 (Indice)

**Type :** Point (pas un pip)

**Définition :**
- **1 point** = 1 unité de prix (ex: 7500 → 7501 = 1 point)
- **Pas de conversion** : 5 points = 5 points (pas multiplié par 10)
- **Valeur** : 1.17 USD par point par 0.1 lot

**Exemple :**
- Prix entry : 7500.00
- Prix exit : 7505.00
- Points : 5 points (directement 7505 - 7500)

---

### USDCHF (Forex - Paire normale)

**Type :** Pip

**Définition :**
- **1 pip** = 0.0001 (4e décimale)
- **Pip size** : 0.0001
- **Valeur** : 10 USD par pip par 0.1 lot

**Exemple :**
- Prix entry : 0.9000
- Prix exit : 0.9010
- Différence : 0.0010
- Pips : 0.0010 / 0.0001 = **10 pips**

---

### USDJPY (Forex - Paire JPY)

**Type :** Pip

**Définition :**
- **1 pip** = 0.01 (2e décimale)
- **Pip size** : 0.01
- **Valeur** : (Volume × 1000) / Prix_JPY USD par pip (dépend du prix)

**Exemple :**
- Prix entry : 150.00
- Prix exit : 150.10
- Différence : 0.10
- Pips : 0.10 / 0.01 = **10 pips**
- Valeur pip (volume 0.1 lot) : (0.1 × 1000) / 150.00 = 0.6667 USD/pip
- Profit : 10 × 0.6667 = **6.67 USD**

---

## Résumé des Formules

| Type | Formule | Exemple |
|------|---------|---------|
| **Forex (normal)** | `Pips × Volume × 10` | 10 pips × 0.1 × 10 = 10 USD |
| **Forex (JPY)** | `Pips × (Volume × 1000) / Prix` | 10 pips × (0.1 × 1000) / 150 = 6.67 USD |
| **Indices (UK100)** | `(entry - exit) × Volume × 1.17` | 20 points × 0.1 × 1.17 = 2.34 USD |
| **Indices (autres)** | `(entry - exit) × Volume × 1` | 50 points × 0.1 × 1 = 5 USD |
| **Métaux (Or)** | `(entry - exit) × Volume × 1` | 10 points × 0.1 × 1 = 1 USD |
| **Métaux (Argent)** | `(entry - exit) × Volume × 0.5` | 1 point × 0.1 × 0.5 = 0.05 USD |
| **Énergie** | `(entry - exit) × Volume × 1` | 5 points × 0.1 × 1 = 0.5 USD |
| **Crypto** | `(entry - exit) × Volume × 0.1` | 100 points × 0.1 × 0.1 = 1 USD |

---

## Notes Importantes

1. **Pour les paires JPY** : La valeur du pip dépend du prix d'entrée (formule standard FX)
2. **Pour UK100** : Utilise 1.17 USD/point au lieu de 1 USD/point (basé sur analyse empirique)
3. **Tous les calculs sont en USD** (pas de conversion EUR)
4. **Volume** : Les formules supposent que le volume est en lots (0.1 lot = 0.1)


