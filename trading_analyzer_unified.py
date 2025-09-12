#!/usr/bin/env python3
"""
Analyseur de Trading Unifié
Combine l'analyse Forex et autres instruments dans un seul script
"""

import pandas as pd
import os
import re
import math
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.chart import LineChart, Reference, PieChart, BarChart
from datetime import datetime
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from enum import Enum

class InstrumentType(Enum):
    FOREX = "forex"
    METAUX = "metaux"
    INDICES = "indices"
    CRYPTO = "crypto"
    ENERGIE = "energie"
    ACTIONS = "actions"

class TradingAnalyzer:
    def __init__(self, solde_initial=10000):
        self.solde_initial = solde_initial
        self.statistiques_fichiers = {}
        
        # Configuration des symboles par type
        self.symboles_forex = [
            "eurusd", "gbpusd", "usdchf", "usdjpy", "usdcad", "audusd", "nzdusd",
            "eurjpy", "gbpjpy", "audjpy", "cadjpy", "chfjpy", "nzdjpy",
            "eurgbp", "euraud", "eurcad", "eurchf", "eurnzd",
            "gbpaud", "gbpcad", "gbpchf", "gbpnzd",
            "audcad", "audchf", "audnzd", "cadchf", "nzdcad", "nzdchf"
        ]
        
        self.symboles_metaux = ["gold", "xauusd", "xau", "or", "silver", "xagusd", "xag", "argent", "platinum", "xptusd", "palladium", "xpdusd"]
        self.symboles_indices = ["dax", "cac", "sp500", "dow", "nasdaq", "ftse", "nikkei", "asx", "us30", "us500", "ger30", "fra40", "uk100", "ger40"]
        self.symboles_crypto = ["btc", "eth", "ltc", "xrp", "ada", "dot", "bitcoin", "ethereum", "crypto"]
        self.symboles_energie = ["oil", "wti", "brent", "petrol", "crude", "gas", "natural"]
    
    def process_files(self, file_paths, task_id, task_status, filter_type=None):
        """
        Traite une liste de fichiers Excel
        filter_type: 'forex', 'autres', ou None (tous)
        """
        try:
            print(f"[DEBUG] Starting unified analysis with {len(file_paths)} files, filter: {filter_type}")
            tous_les_resultats = []
            total_files = len(file_paths)
            
            for i, file_path in enumerate(file_paths):
                progress = 20 + (i / total_files) * 40
                task_status[task_id]['progress'] = int(progress)
                task_status[task_id]['message'] = f'Traitement du fichier {i+1}/{total_files}...'
                
                print(f"[DEBUG] Processing file {i+1}/{total_files}: {os.path.basename(file_path)}")
                
                df_result, erreur, exclus, doublons = self.process_single_file(file_path, filter_type)
                
                if df_result is not None and len(df_result) > 0:
                    tous_les_resultats.append(df_result)
                    
                    filename = os.path.basename(file_path)
                    # Compter les trades complets (clés uniques) au lieu des opérations
                    nb_trades_complets = df_result["Cle_Match"].nunique() if "Cle_Match" in df_result.columns else len(df_result)
                    self.statistiques_fichiers[filename] = {
                        'trades': nb_trades_complets,
                        'exclus': exclus,
                        'doublons': doublons,
                        'erreur': erreur
                    }
                    print(f"[DEBUG] File processed successfully: {len(df_result)} trades, {exclus} excluded")
                else:
                    filename = os.path.basename(file_path)
                    self.statistiques_fichiers[filename] = {
                        'trades': 0,
                        'exclus': 0,
                        'doublons': 0,
                        'erreur': erreur or "Aucune donnée trouvée"
                    }
                    print(f"[DEBUG] File failed: {erreur}")
            
            if not tous_les_resultats:
                print(f"[DEBUG] No valid data found in any file")
                return None
            
            task_status[task_id]['progress'] = 60
            task_status[task_id]['message'] = 'Fusion des données et calculs des intérêts composés...'
            
            print(f"[DEBUG] Starting fusion and compound interest calculations")
            df_final = self.fusionner_et_calculer_cumuls(tous_les_resultats)
            print(f"[DEBUG] Fusion completed: {len(df_final)} total trades")
            
            task_status[task_id]['progress'] = 75
            task_status[task_id]['message'] = 'Calculs des statistiques avancées...'
            
            return df_final
            
        except Exception as e:
            print(f"[ERROR] Error in process_files: {str(e)}")
            import traceback
            print(f"[ERROR] Traceback: {traceback.format_exc()}")
            raise Exception(f"Erreur lors du traitement des fichiers: {str(e)}")
    
    def process_single_file(self, file_path, filter_type=None):
        """Traite un seul fichier Excel avec filtrage optionnel"""
        try:
            print(f"[DEBUG] Starting to process file: {file_path}")
            df = pd.read_excel(file_path, sheet_name=0, header=None)
            print(f"[DEBUG] File read successfully, shape: {df.shape}")
            
            # Trouver les lignes "ordre" et "transaction"
            ligne_ordres = self.trouver_ligne(df, "ordre")
            ligne_transactions = self.trouver_ligne(df, "transaction")
            print(f"[DEBUG] Found ordre line at: {ligne_ordres}, transaction line at: {ligne_transactions}")

            # Extraire les DataFrames ordres et transactions
            header_ordres = df.iloc[ligne_ordres + 1]
            ordres_df = df.iloc[ligne_ordres + 2 : ligne_transactions].copy()
            ordres_df.columns = header_ordres
            ordres_df.reset_index(drop=True, inplace=True)

            header_transactions = df.iloc[ligne_transactions + 1]
            transactions_df = df.iloc[ligne_transactions + 2 :].copy()
            transactions_df.columns = header_transactions
            transactions_df = transactions_df[transactions_df.iloc[:, 0].notna()]
            transactions_df.reset_index(drop=True, inplace=True)
            
            print(f"[DEBUG] Ordres shape: {ordres_df.shape}, Transactions shape: {transactions_df.shape}")

            if len(ordres_df.columns) < 2 or len(transactions_df.columns) < 2:
                return None, "Pas assez de colonnes dans les données", 0, 0

            # Créer la clé de jointure
            ordres_df["__clé__"] = ordres_df.iloc[:, 1].astype(str)
            transactions_df["__clé__"] = transactions_df.iloc[:, 1].astype(str)

            # Ajouter la colonne d'origine du fichier pour désambiguïser les clés
            fichier_source = os.path.basename(file_path)
            ordres_df["Fichier_Source"] = fichier_source
            transactions_df["Fichier_Source"] = fichier_source
            
            # Renommer la colonne Prix si elle existe
            if "Prix" in transactions_df.columns:
                transactions_df.rename(columns={"Prix": "Prix_transaction"}, inplace=True)

            # Fusionner les DataFrames
            fusion_df = pd.merge(ordres_df, transactions_df, on="__clé__", suffixes=('_ordre', '_transaction'))
            print(f"[DEBUG] Merged dataframe shape: {fusion_df.shape}")

            # Unifier la colonne Fichier_Source après merge
            if "Fichier_Source_ordre" in fusion_df.columns:
                fusion_df["Fichier_Source"] = fusion_df["Fichier_Source_ordre"]
            elif "Fichier_Source_transaction" in fusion_df.columns:
                fusion_df["Fichier_Source"] = fusion_df["Fichier_Source_transaction"]
            # Nettoyer les colonnes intermédiaires si présentes
            colonnes_a_supprimer_tmp = []
            for col_tmp in ["Fichier_Source_ordre", "Fichier_Source_transaction"]:
                if col_tmp in fusion_df.columns:
                    colonnes_a_supprimer_tmp.append(col_tmp)
            if colonnes_a_supprimer_tmp:
                fusion_df.drop(columns=colonnes_a_supprimer_tmp, inplace=True)
            
            avant_filtrage = len(fusion_df)

            # Filtrage selon le type demandé
            apres_filtrage = avant_filtrage  # Initialisation par défaut
            
            if "Symbole_ordre" in fusion_df.columns and filter_type:
                print(f"[DEBUG] Applying {filter_type} filter...")
                if filter_type == 'forex':
                    fusion_df = fusion_df[fusion_df["Symbole_ordre"].apply(self.est_forex)]
                elif filter_type == 'autres':
                    fusion_df = fusion_df[fusion_df["Symbole_ordre"].apply(self.est_autre_instrument)]
                
                apres_filtrage = len(fusion_df)
                print(f"[DEBUG] After filtering: {apres_filtrage} rows (excluded: {avant_filtrage - apres_filtrage})")
                
                if len(fusion_df) == 0:
                    return None, f"Aucun instrument {filter_type} trouvé", avant_filtrage - apres_filtrage, 0

            # Conversions des colonnes numériques
            print(f"[DEBUG] Converting numeric columns...")
            fusion_df["Profit"] = self.safe_convert_to_float(fusion_df["Profit"])
            fusion_df["Prix_transaction"] = self.safe_convert_to_float(fusion_df["Prix_transaction"])
            
            if "T / P" in fusion_df.columns:
                fusion_df["T / P"] = self.safe_convert_to_float(fusion_df["T / P"])
            if "S / L" in fusion_df.columns:
                fusion_df["S / L"] = self.safe_convert_to_float(fusion_df["S / L"])

            fusion_df["Volume_ordre"] = fusion_df["Volume_ordre"].astype(str)
            fusion_df["Symbole_ordre"] = fusion_df["Symbole_ordre"].astype(str)
            fusion_df["Cle_Match"] = None

            # Logique de matching des trades
            print(f"[DEBUG] Applying matching logic...")
            self.apply_matching_logic(fusion_df)
            
            # Créer l'index des trades d'entrée
            df_in = fusion_df[(fusion_df["Direction"] == "in") & (fusion_df["Cle_Match"].notna())].copy()
            if len(df_in) > 0:
                df_in = df_in.set_index("Cle_Match")

            # Calcul des pips/points selon le type d'instrument
            print(f"[DEBUG] Calculating pips/points...")
            fusion_df["Profit_pips"] = fusion_df.apply(lambda row: self.calculer_pips_ou_points(row, df_in), axis=1)
            
            # Nettoyage et sélection des colonnes finales
            colonnes_a_garder = [
                "Heure d'ouverture", "Ordre_ordre", "Symbole_ordre", "Type_ordre", 
                "Volume_ordre", "S / L", "T / P", "Direction", "Prix_transaction",
                "Profit", "Cle_Match", "Profit_pips", "Fichier_Source"
            ]
            
            colonnes_finales = [col for col in colonnes_a_garder if col in fusion_df.columns]
            fusion_df = fusion_df[colonnes_finales]
            
            # Suppression des doublons
            avant_dedoublonnage = len(fusion_df)
            fusion_df = fusion_df.drop_duplicates().reset_index(drop=True)
            apres_dedoublonnage = len(fusion_df)
            doublons_supprimes = avant_dedoublonnage - apres_dedoublonnage
            
            print(f"[DEBUG] File processing completed: {len(fusion_df)} final trades")
            
            # Calculer le nombre d'exclus
            exclus = avant_filtrage - apres_filtrage
            
            return fusion_df, "Succès", exclus, doublons_supprimes
            
        except Exception as e:
            print(f"[ERROR] Error processing file {file_path}: {str(e)}")
            import traceback
            print(f"[ERROR] Traceback: {traceback.format_exc()}")
            return None, str(e), 0, 0
    
    def trouver_ligne(self, df, mot_approx):
        """Trouve une ligne contenant un mot approximatif"""
        for i, row in df.iterrows():
            texte = row.astype(str).str.lower().str.replace(" ", "").str.replace(":", "")
            if texte.str.contains(mot_approx.lower()).any():
                return i
        raise ValueError(f"Ligne avec '{mot_approx}' non trouvée.")
    
    def safe_convert_to_float(self, series):
        """Convertit une série en float en gérant les valeurs NaN"""
        return pd.to_numeric(series.astype(str).str.replace(",", ".").replace("nan", ""), errors='coerce')
    
    def detecter_type_instrument(self, symbole):
        """Détecte automatiquement le type d'instrument financier"""
        symbole = str(symbole).upper()
        
        # Reconnaissance automatique Forex
        if self.est_forex_automatique(symbole):
            return InstrumentType.FOREX
        
        # Reconnaissance automatique Métaux
        if self.est_metal_automatique(symbole):
            return InstrumentType.METAUX
        
        # Reconnaissance automatique Indices
        if self.est_indice_automatique(symbole):
            return InstrumentType.INDICES
        
        # Reconnaissance automatique Crypto
        if self.est_crypto_automatique(symbole):
            return InstrumentType.CRYPTO
        
        # Reconnaissance automatique Énergie
        if self.est_energie_automatique(symbole):
            return InstrumentType.ENERGIE
        
        # Fallback sur les listes existantes
        symbole_lower = symbole.lower()
        if any(metal in symbole_lower for metal in self.symboles_metaux):
            return InstrumentType.METAUX
        elif any(index in symbole_lower for index in self.symboles_indices):
            return InstrumentType.INDICES
        elif any(c in symbole_lower for c in self.symboles_crypto):
            return InstrumentType.CRYPTO
        elif any(e in symbole_lower for e in self.symboles_energie):
            return InstrumentType.ENERGIE
        elif any(forex_pair in symbole_lower for forex_pair in self.symboles_forex):
            return InstrumentType.FOREX
        else:
            return InstrumentType.ACTIONS
    
    def est_forex_automatique(self, symbole):
        """Reconnaissance automatique des paires Forex"""
        # Devises connues
        devises = ["USD", "EUR", "GBP", "JPY", "CHF", "CAD", "AUD", "NZD"]
        
        # Pattern Forex : 6 lettres (3+3) avec des devises connues
        if len(symbole) == 6:
            devise1 = symbole[:3]
            devise2 = symbole[3:]
            if devise1 in devises and devise2 in devises:
                return True
        
        # Pattern Forex : 7 lettres (3+4) comme EURJPY
        if len(symbole) == 7:
            devise1 = symbole[:3]
            devise2 = symbole[3:]
            if devise1 in devises and devise2 in devises:
                return True
        
        return False
    
    def est_metal_automatique(self, symbole):
        """Reconnaissance automatique des métaux"""
        mots_cles_metaux = ["GOLD", "SILVER", "XAU", "XAG", "PLATINUM", "PALLADIUM"]
        return any(mot in symbole for mot in mots_cles_metaux)
    
    def est_indice_automatique(self, symbole):
        """Reconnaissance automatique des indices"""
        mots_cles_indices = ["DAX", "CAC", "SP500", "NASDAQ", "FTSE", "NIKKEI", "DOW"]
        patterns_indices = ["US30", "US500", "GER30", "FRA40", "UK100", "GER40"]
        
        return any(mot in symbole for mot in mots_cles_indices) or any(pattern in symbole for pattern in patterns_indices)
    
    def est_crypto_automatique(self, symbole):
        """Reconnaissance automatique des cryptos"""
        mots_cles_crypto = ["BTC", "ETH", "LTC", "XRP", "ADA", "DOT", "BITCOIN", "ETHEREUM"]
        return any(mot in symbole for mot in mots_cles_crypto)
    
    def est_energie_automatique(self, symbole):
        """Reconnaissance automatique des énergies"""
        mots_cles_energie = ["OIL", "WTI", "BRENT", "GAS", "NATURAL"]
        return any(mot in symbole for mot in mots_cles_energie)
    
    def est_forex(self, symbole):
        """Vérifie si un symbole est une paire Forex"""
        symbole = str(symbole).lower()
        return any(forex_pair in symbole for forex_pair in self.symboles_forex)
    
    def est_autre_instrument(self, symbole):
        """Vérifie si un symbole N'EST PAS une paire Forex"""
        return not self.est_forex(symbole)
    
    def apply_matching_logic(self, fusion_df):
        """LOGIQUE DE MATCHING RESPECTANT TOUS LES CRITÈRES - N° ordre, volumes, TP/SL"""
        print(f"[DEBUG] Starting CRITERIA-BASED matching logic for {len(fusion_df)} rows")
        
        # TRIER CHRONOLOGIQUEMENT AVANT LE MATCHING
        if "Date_ordre" in fusion_df.columns:
            fusion_df = fusion_df.sort_values("Date_ordre").reset_index(drop=True)
            print(f"[DEBUG] DataFrame trié chronologiquement par Date_ordre")
        elif "Date_transaction" in fusion_df.columns:
            fusion_df = fusion_df.sort_values("Date_transaction").reset_index(drop=True)
            print(f"[DEBUG] DataFrame trié chronologiquement par Date_transaction")
        else:
            print(f"[WARNING] Aucune colonne de date trouvée pour le tri chronologique")
        
        # ÉTAPE 1: Créer les clés pour TOUS les trades "in"
        trades_in = fusion_df[fusion_df["Direction"] == "in"].copy()
        print(f"[DEBUG] Creating keys for {len(trades_in)} 'in' trades")
        
        for idx, row in trades_in.iterrows():
            ordre = row["Ordre_ordre"]
            symbole = row["Symbole_ordre"]
            fichier = row.get("Fichier_Source", "")
            
            # Créer une clé UNIQUE basée sur le fichier + symbole + ordre
            cle_unique = f"{fichier}|{symbole}-{ordre}"
            fusion_df.at[idx, "Cle_Match"] = cle_unique
            print(f"[DEBUG] Created key for {fichier} / {symbole} order {ordre}: {cle_unique}")

        # ÉTAPE 2: MATCHING RESPECTANT TOUS LES CRITÈRES
        print(f"[DEBUG] Starting CRITERIA-BASED matching for all symbols")
        
        # Grouper par (symbole, fichier) pour éviter toute collision inter-fichiers
        if "Fichier_Source" in fusion_df.columns:
            groupes = fusion_df[["Symbole_ordre", "Fichier_Source"]].drop_duplicates()
            iter_groupes = [(row.Symbole_ordre, row.Fichier_Source) for _, row in groupes.iterrows()]
        else:
            iter_groupes = [(symb, None) for symb in fusion_df["Symbole_ordre"].unique()]

        for symbole, fichier in iter_groupes:
            print(f"[DEBUG] Processing symbol: {symbole} (file: {fichier})")
            
            # Récupérer tous les trades pour ce symbole
            if fichier is not None:
                trades_symbole = fusion_df[(fusion_df["Symbole_ordre"] == symbole) & (fusion_df["Fichier_Source"] == fichier)].copy()
            else:
                trades_symbole = fusion_df[fusion_df["Symbole_ordre"] == symbole].copy()
            trades_in_symbole = trades_symbole[trades_symbole["Direction"] == "in"].copy()
            trades_out_symbole = trades_symbole[trades_symbole["Direction"] == "out"].copy()
            
            print(f"[DEBUG] {symbole}: {len(trades_in_symbole)} IN trades, {len(trades_out_symbole)} OUT trades")
            
            # Pour chaque trade "in", chercher TOUS les trades "out" correspondants
            for _, trade_in in trades_in_symbole.iterrows():
                ordre_in = trade_in["Ordre_ordre"]
                volume_in = self.parse_volume(trade_in["Volume_ordre"])
                cle_in = trade_in["Cle_Match"]
                tp_in = trade_in.get("T / P", None)
                sl_in = trade_in.get("S / L", None)
                
                print(f"[DEBUG] Processing IN trade: {symbole} order {ordre_in}, volume: {volume_in}")
                
                # Nouvelle logique: agréger séquentiellement les OUT jusqu'à atteindre le volume IN
                candidates_out = trades_out_symbole[
                    (trades_out_symbole["Ordre_ordre"] > ordre_in) &
                    (trades_out_symbole["Cle_Match"].isna())
                ].copy()

                if len(candidates_out) == 0:
                    print(f"[DEBUG] No OUT trades after IN {ordre_in}")
                    continue

                candidates_out = candidates_out.sort_values("Ordre_ordre").reset_index(drop=True)

                cum_volume = 0.0
                selected_out_rows = []
                for _, trade_out in candidates_out.iterrows():
                    volume_out = self.parse_volume(trade_out["Volume_ordre"])
                    cum_volume += volume_out
                    selected_out_rows.append(trade_out)
                    if math.isclose(cum_volume, volume_in, rel_tol=0.02, abs_tol=1e-6) or cum_volume > volume_in:
                        break

                print(f"[DEBUG] Aggregated OUT volume: {cum_volume} for IN {volume_in} with {len(selected_out_rows)} outs")

                if math.isclose(cum_volume, volume_in, rel_tol=0.02, abs_tol=1e-6):
                    print(f"[DEBUG] ✅ Aggregated volume matches IN within tolerance. Assigning {len(selected_out_rows)} OUT trades")
                    for trade_out in selected_out_rows:
                        if fichier is not None:
                            idx_out = fusion_df[
                                (fusion_df["Symbole_ordre"] == symbole) &
                                (fusion_df["Ordre_ordre"] == trade_out["Ordre_ordre"]) &
                                (fusion_df["Direction"] == "out") &
                                (fusion_df["Fichier_Source"] == fichier)
                            ].index[0]
                        else:
                            idx_out = fusion_df[
                                (fusion_df["Symbole_ordre"] == symbole) &
                                (fusion_df["Ordre_ordre"] == trade_out["Ordre_ordre"]) &
                                (fusion_df["Direction"] == "out")
                            ].index[0]
                        fusion_df.at[idx_out, "Cle_Match"] = cle_in
                        print(f"[DEBUG] ✅ Assigned {cle_in} to {symbole} order {trade_out['Ordre_ordre']}")
                else:
                    print(f"[DEBUG] ❌ Aggregated volume does not match. Trying 1:1 fallback")
                    # Fallback: 1:1 sur le premier OUT proche
                    for _, trade_out in candidates_out.iterrows():
                        volume_out = self.parse_volume(trade_out["Volume_ordre"])
                        if math.isclose(volume_out, volume_in, rel_tol=0.02, abs_tol=1e-6):
                            print(f"[DEBUG] 🔄 Fallback: Simple 1:1 match found")
                            if fichier is not None:
                                idx_out = fusion_df[
                                    (fusion_df["Symbole_ordre"] == symbole) &
                                    (fusion_df["Ordre_ordre"] == trade_out["Ordre_ordre"]) &
                                    (fusion_df["Direction"] == "out") &
                                    (fusion_df["Fichier_Source"] == fichier)
                                ].index[0]
                            else:
                                idx_out = fusion_df[
                                    (fusion_df["Symbole_ordre"] == symbole) &
                                    (fusion_df["Ordre_ordre"] == trade_out["Ordre_ordre"]) &
                                    (fusion_df["Direction"] == "out")
                                ].index[0]
                            fusion_df.at[idx_out, "Cle_Match"] = cle_in
                            break
        
        # ÉTAPE 3: VÉRIFICATION FINALE - Assigner les trades OUT restants
        print(f"[DEBUG] Final verification and cleanup")
        
        trades_out_sans_cle = fusion_df[(fusion_df["Direction"] == "out") & (fusion_df["Cle_Match"].isna())]
        if len(trades_out_sans_cle) > 0:
            print(f"[DEBUG] ⚠️ {len(trades_out_sans_cle)} OUT trades still without key - applying emergency matching")
            
            for _, trade_out in trades_out_sans_cle.iterrows():
                symbole = trade_out["Symbole_ordre"]
                ordre_out = trade_out["Ordre_ordre"]
                fichier = trade_out.get("Fichier_Source", None)
                
                # Chercher le trade IN le plus proche (avant ou après)
                if fichier is not None:
                    trades_in_symbole = fusion_df[
                        (fusion_df["Symbole_ordre"] == symbole) & 
                        (fusion_df["Direction"] == "in") &
                        (fusion_df["Fichier_Source"] == fichier)
                    ].copy()
                else:
                    trades_in_symbole = fusion_df[
                        (fusion_df["Symbole_ordre"] == symbole) & 
                        (fusion_df["Direction"] == "in")
                    ].copy()
                
                if len(trades_in_symbole) > 0:
                    # Trouver le trade IN le plus proche en numéro d'ordre
                    trades_in_symbole["Distance"] = abs(trades_in_symbole["Ordre_ordre"] - ordre_out)
                    trade_in_proche = trades_in_symbole.loc[trades_in_symbole["Distance"].idxmin()]
                    
                    print(f"[DEBUG] 🚨 Emergency match: OUT {ordre_out} -> IN {trade_in_proche['Ordre_ordre']}")
                    
                    if fichier is not None:
                        idx_out = fusion_df[
                            (fusion_df["Symbole_ordre"] == symbole) & 
                            (fusion_df["Ordre_ordre"] == ordre_out) & 
                            (fusion_df["Direction"] == "out") &
                            (fusion_df["Fichier_Source"] == fichier)
                        ].index[0]
                    else:
                        idx_out = fusion_df[
                            (fusion_df["Symbole_ordre"] == symbole) & 
                            (fusion_df["Ordre_ordre"] == ordre_out) & 
                            (fusion_df["Direction"] == "out")
                        ].index[0]
                    fusion_df.at[idx_out, "Cle_Match"] = trade_in_proche["Cle_Match"]
        
        # RÉSULTATS FINAUX
        trades_in_avec_cle = len(fusion_df[(fusion_df["Direction"] == "in") & (fusion_df["Cle_Match"].notna())])
        trades_out_avec_cle = len(fusion_df[(fusion_df["Direction"] == "out") & (fusion_df["Cle_Match"].notna())])
        total_avec_cle = trades_in_avec_cle + trades_out_avec_cle
        
        print(f"[DEBUG] 🎯 CRITERIA-BASED MATCHING RESULTS:")
        print(f"[DEBUG]   - IN trades with keys: {trades_in_avec_cle}")
        print(f"[DEBUG]   - OUT trades with keys: {trades_out_avec_cle}")
        print(f"[DEBUG]   - Total with keys: {total_avec_cle}/{len(fusion_df)} ({(total_avec_cle/len(fusion_df)*100):.1f}%)")
        
        # Vérification finale
        if total_avec_cle == len(fusion_df):
            print(f"[DEBUG] ✅ SUCCESS: ALL trades have keys!")
        else:
            print(f"[DEBUG] ❌ WARNING: {len(fusion_df) - total_avec_cle} trades still without keys!")
    
    def parse_volume(self, volume_str):
        """Parse le volume depuis une chaîne comme '0.56 / 0.56' ou '0.56'"""
        try:
            volume_str = str(volume_str).strip()
            if "/" in volume_str:
                # Format "executed / total"
                return float(volume_str.split("/")[0].strip())
            else:
                return float(volume_str)
        except:
            return 0.0
    
    def extract_price_from_comment(self, commentaire):
        """Extrait le prix d'un commentaire TP/SL"""
        import re
        commentaire = str(commentaire).lower()
        match = re.search(r'(tp|sl)[^\d]*(\d+[.,]?\d*)', commentaire)
        if match:
            try:
                return float(match.group(2).replace(",", "."))
            except:
                return 0.0
        return 0.0
    
    def extraire_prix_commentaire(self, commentaire):
        """Extrait le prix du commentaire"""
        commentaire = str(commentaire).lower()
        match = re.search(r'(tp|sl)[^\d]*(\d+[.,]?\d+)', commentaire)
        if match:
            try:
                prix = float(match.group(2).replace(",", "."))
                return round(prix, 5)
            except:
                return None
        return None
    
    def calculer_pips_ou_points(self, row, df_in):
        """Calcul des pips (Forex) ou points (autres instruments) avec détection d'incohérences"""
        symbole = str(row["Symbole_ordre"]).lower()
        profit = row["Profit"]
        type_instrument = self.detecter_type_instrument(symbole)
        
        # Gestion du volume
        volume_str = str(row["Volume_ordre"])
        if "/" in volume_str:
            volume = float(volume_str.split("/")[0].strip())
        else:
            volume = float(volume_str.strip())
        
        try:
            # Si c'est un trade de sortie avec matching
            if row["Direction"] == "out":
                cle = row["Cle_Match"]
                if pd.notna(cle) and len(df_in) > 0 and cle in df_in.index:
                    in_row = df_in.loc[cle]
                    prix_in = in_row["Prix_transaction"]
                    prix_out = row["Prix_transaction"]
                    
                    if "Type_ordre" in in_row.index:
                        type_ordre = in_row["Type_ordre"]
                        if type_ordre == "buy":
                            points_bruts = prix_out - prix_in
                        else:
                            points_bruts = prix_in - prix_out
                        
                        # Conversion pips/points selon règles demandées
                        if type_instrument == InstrumentType.FOREX:
                            # Déterminer la taille de pip à partir du nombre de décimales des prix
                            def _decimals(x):
                                try:
                                    s = f"{float(x):.10f}".rstrip("0").rstrip(".")
                                    return len(s.split(".")[1]) if "." in s else 0
                                except Exception:
                                    return 0
                            nb_dec = max(_decimals(prix_in), _decimals(prix_out))
                            if nb_dec >= 4:
                                pip_size = 0.0001  # 4e décimale, 5e ignorée (pipette)
                            elif nb_dec in (2, 3):
                                pip_size = 0.01    # 2e décimale
                            else:
                                # Fallback: par défaut considérer 0.0001
                                pip_size = 0.0001

                            pips_floats = abs(points_bruts) / pip_size
                            pips_entiers = int(pips_floats)  # ignorer les pipettes (pipettes non comptées)
                            signe = 1 if points_bruts >= 0 else -1
                            return signe * pips_entiers
                        else:
                            # Pour les autres instruments, conserver les points bruts
                            return round(points_bruts, 2)
            
            # Fallback : calcul basé sur le profit avec valeurs réalistes
            if type_instrument == InstrumentType.FOREX:
                # Valeurs réalistes pour le Forex (basées sur des spreads typiques)
                # On garde l'approximation de 10€/pip par 0.1 lot comme fallback
                valeur_pip = volume * 10.0
                
                if valeur_pip != 0:
                    pips_calcules = round(profit / valeur_pip, 2)
                    print(f"[INFO] Calcul fallback pour {symbole}: {profit}€ / {valeur_pip}€ = {pips_calcules} pips")
                    return pips_calcules
            else:
                # Valeurs réalistes pour les autres instruments
                if type_instrument == InstrumentType.METAUX:
                    # Or/Argent : 1 point = ~1€ pour 0.1 lot
                    valeur_point = volume * 1.0
                elif type_instrument == InstrumentType.INDICES:
                    if "dax" in symbole or "ger30" in symbole or "ger40" in symbole:
                        # DAX/GER30/GER40 : 1 point = ~1€ pour 0.1 lot
                        valeur_point = volume * 1.0
                    elif "cac" in symbole or "fra40" in symbole:
                        # CAC40 : 1 point = ~1€ pour 0.1 lot
                        valeur_point = volume * 1.0
                    elif "sp500" in symbole or "us500" in symbole:
                        # SP500 : 1 point = ~1€ pour 0.1 lot
                        valeur_point = volume * 1.0
                    else:
                        # Autres indices : 1 point = ~1€ pour 0.1 lot
                        valeur_point = volume * 1.0
                elif type_instrument == InstrumentType.CRYPTO:
                    # Crypto : 1 point = ~0.1€ pour 0.1 lot
                    valeur_point = volume * 0.1
                elif type_instrument == InstrumentType.ENERGIE:
                    # Pétrole : 1 point = ~1€ pour 0.1 lot
                    valeur_point = volume * 1.0
                else:
                    # Actions : 1 point = ~1€ pour 0.1 lot
                    valeur_point = volume * 1.0
                
                if valeur_point != 0:
                    return round(profit / valeur_point, 2)
            
            return None
                
        except Exception as e:
            print(f"[ERROR] Erreur calcul pips pour {symbole}: {str(e)}")
            return None
    
    def fusionner_et_calculer_cumuls(self, tous_les_df):
        """Fusionne tous les DataFrames et calcule les intérêts composés + drawdown"""
        print(f"[DEBUG] Starting fusion and compound calculations...")
        
        # Fusionner tous les DataFrames
        df_complet = pd.concat(tous_les_df, ignore_index=True)
        print(f"[DEBUG] Merged {len(tous_les_df)} dataframes into {len(df_complet)} total trades")
        
        # Tri par date
        if "Heure d'ouverture" in df_complet.columns:
            df_complet["Date_parsed"] = pd.to_datetime(df_complet["Heure d'ouverture"], errors='coerce')
            df_complet = df_complet.sort_values("Date_parsed").reset_index(drop=True)
            df_complet = df_complet.drop("Date_parsed", axis=1)
        
        # Calculs cumulés avec intérêts composés
        df_complet["Profit_compose"] = 0.0
        df_complet["Profit_cumule"] = 0.0
        df_complet["Solde_cumule"] = 0.0
        df_complet["Profit_pips_cumule"] = 0.0
        df_complet["Drawdown_pct"] = 0.0
        df_complet["Drawdown_euros"] = 0.0
        df_complet["Drawdown_running_pct"] = 0.0
        
        solde_courant = self.solde_initial
        profit_cumule_reel = 0.0
        pips_cumule = 0.0
        plus_haut_solde = self.solde_initial
        drawdown_running_max = 0.0
        
        print(f"[DEBUG] Starting compound interest calculations...")
        
        for idx, row in df_complet.iterrows():
            profit_original = row["Profit"] if pd.notna(row["Profit"]) else 0
            pips = row["Profit_pips"] if pd.notna(row["Profit_pips"]) else 0
            
            # Calculer le rendement en pourcentage
            if profit_original != 0 and self.solde_initial != 0:
                rendement_trade_pct = (profit_original / self.solde_initial) * 100
                profit_compose = (rendement_trade_pct / 100) * solde_courant
            else:
                profit_compose = 0
            
            # Mise à jour des cumuls
            solde_courant += profit_compose
            profit_cumule_reel += profit_compose
            pips_cumule += pips
            
            # Mise à jour du plus haut solde historique
            if solde_courant > plus_haut_solde:
                plus_haut_solde = solde_courant
            
            # Calcul du drawdown CLASSIQUE
            if solde_courant < plus_haut_solde:
                drawdown_euros = plus_haut_solde - solde_courant
                drawdown_pct = (drawdown_euros / plus_haut_solde * 100)
            else:
                drawdown_euros = 0.0
                drawdown_pct = 0.0
            
            # Calcul du drawdown RUNNING (lissé)
            drawdown_actuel = (plus_haut_solde - solde_courant) / plus_haut_solde * 100
            if drawdown_actuel > drawdown_running_max:
                drawdown_running_max = drawdown_actuel
            
            if drawdown_actuel < drawdown_running_max:
                if profit_original > 0:
                    drawdown_running_max = max(drawdown_actuel, drawdown_running_max * 0.9)
                else:
                    drawdown_running_max = max(drawdown_actuel, drawdown_running_max)
            
            # Enregistrer les valeurs
            df_complet.at[idx, "Profit_compose"] = round(profit_compose, 2)
            df_complet.at[idx, "Profit_cumule"] = round(profit_cumule_reel, 2)
            df_complet.at[idx, "Solde_cumule"] = round(solde_courant, 2)
            df_complet.at[idx, "Profit_pips_cumule"] = round(pips_cumule, 2)
            df_complet.at[idx, "Drawdown_pct"] = round(drawdown_pct, 2)
            df_complet.at[idx, "Drawdown_euros"] = round(drawdown_euros, 2)
            df_complet.at[idx, "Drawdown_running_pct"] = round(drawdown_running_max, 2)
        
        print(f"[DEBUG] Compound calculations completed. Final solde: {solde_courant:.2f}")
        print(f"[DEBUG] Max drawdown: {df_complet['Drawdown_pct'].max():.2f}%")
        
        return df_complet
    
    def calculer_trades_complets(self, df):
        """Calcule le nombre de trades complets (1 IN + 1 ou plusieurs OUT)"""
        print(f"[DEBUG] Calculating complete trades from {len(df)} rows")
        
        # Compter les clés de jointure uniques (chaque clé = 1 trade complet)
        trades_complets = df["Cle_Match"].nunique()
        
        # Compter les trades IN et OUT uniques (pour debug)
        trades_in_uniques = df[df["Direction"] == "in"]["Cle_Match"].nunique()
        trades_out_uniques = df[df["Direction"] == "out"]["Cle_Match"].nunique()
        
        print(f"[DEBUG] Found {trades_complets} complete trades (unique keys), {trades_in_uniques} unique IN trades, {trades_out_uniques} unique OUT trades")
        
        # Le nombre de trades complets = nombre de clés de jointure uniques
        return trades_complets
    
    def calculer_trades_par_resultat(self, df):
        """Calcule les trades gagnants/perdants basés sur les trades complets"""
        print(f"[DEBUG] Calculating trades by result")
        
        # Grouper par clé de trade et calculer le profit total de chaque trade complet
        trades_complets = df.groupby("Cle_Match").agg({
            "Profit": "sum"
        }).reset_index()
        
        # Compter par résultat (tous les trades complets, pas seulement les IN)
        trades_gagnants = len(trades_complets[trades_complets["Profit"] > 0])
        trades_perdants = len(trades_complets[trades_complets["Profit"] < 0])
        trades_neutres = len(trades_complets[trades_complets["Profit"] == 0])
        
        print(f"[DEBUG] Complete trades: {len(trades_complets)} total, {trades_gagnants} winners, {trades_perdants} losers")
        
        return trades_gagnants, trades_perdants, trades_neutres, len(trades_complets)
    
    def calculer_statistiques_avancees(self, df):
        """Calcule les statistiques avancées basées sur les trades complets"""
        stats = {}
        
        # Calculer les trades complets par résultat
        trades_gagnants, trades_perdants, trades_neutres, total_trades_complets = self.calculer_trades_par_resultat(df)
        
        # Calculer les profits moyens basés sur les trades complets
        trades_complets = df.groupby("Cle_Match").agg({
            "Profit": "sum"
        }).reset_index()
        
        profits_gagnants = trades_complets[trades_complets["Profit"] > 0]["Profit"]
        profits_perdants = trades_complets[trades_complets["Profit"] < 0]["Profit"]
        
        # Moyennes basées sur les trades complets
        stats["gain_moyen"] = profits_gagnants.mean() if len(profits_gagnants) > 0 else 0
        stats["perte_moyenne"] = profits_perdants.mean() if len(profits_perdants) > 0 else 0
        
        # Calcul des séries consécutives basées sur les trades complets
        series_gagnantes = []
        series_perdantes = []
        
        serie_gagnante_actuelle = 0
        serie_perdante_actuelle = 0
        
        # Trier par ordre chronologique pour les séries
        if "Heure d'ouverture" in df.columns:
            df_triee = df.sort_values("Heure d'ouverture")
        elif "Ordre_ordre" in df.columns:
            df_triee = df.sort_values("Ordre_ordre")
        else:
            df_triee = df
        
        # Parcourir les trades complets dans l'ordre chronologique
        for _, row in trades_complets.iterrows():
            profit = row["Profit"]
            
            if profit > 0:
                serie_gagnante_actuelle += 1
                if serie_perdante_actuelle > 0:
                    series_perdantes.append(serie_perdante_actuelle)
                    serie_perdante_actuelle = 0
            elif profit < 0:
                serie_perdante_actuelle += 1
                if serie_gagnante_actuelle > 0:
                    series_gagnantes.append(serie_gagnante_actuelle)
                    serie_gagnante_actuelle = 0
            else:
                # Trade neutre
                if serie_gagnante_actuelle > 0:
                    series_gagnantes.append(serie_gagnante_actuelle)
                    serie_gagnante_actuelle = 0
                if serie_perdante_actuelle > 0:
                    series_perdantes.append(serie_perdante_actuelle)
                    serie_perdante_actuelle = 0
        
        # Ajouter la dernière série
        if serie_gagnante_actuelle > 0:
            series_gagnantes.append(serie_gagnante_actuelle)
        if serie_perdante_actuelle > 0:
            series_perdantes.append(serie_perdante_actuelle)
        
        stats["gains_consecutifs_max"] = max(series_gagnantes) if series_gagnantes else 0
        stats["pertes_consecutives_max"] = max(series_perdantes) if series_perdantes else 0
        
        # Statistiques du drawdown (basées sur toutes les lignes pour la continuité)
        stats["drawdown_max_pct"] = df["Drawdown_pct"].max()
        stats["drawdown_max_euros"] = df["Drawdown_euros"].max()
        
        # Nombre de périodes de drawdown
        periodes_drawdown = len(df[df["Drawdown_pct"] > 0])
        stats["periodes_drawdown"] = periodes_drawdown
        
        # Ajouter les statistiques de trades complets
        stats["total_trades_complets"] = total_trades_complets
        stats["trades_gagnants_complets"] = trades_gagnants
        stats["trades_perdants_complets"] = trades_perdants
        stats["trades_neutres_complets"] = trades_neutres
        
        return stats
    
    def create_excel_report(self, df_final, reports_folder, timestamp, filter_type=None):
        """Crée un rapport Excel complet avec graphiques"""
        try:
            print(f"[DEBUG] Starting Excel report creation")
            
            # Calculer les statistiques avancees
            stats_avancees = self.calculer_statistiques_avancees(df_final)
            
            wb = Workbook()
            wb.remove(wb.active)
            
            # === ONGLET 1: RÉSUMÉ GLOBAL ===
            ws_resume = wb.create_sheet("📊 Résumé Global")
            
            # Titre principal
            ws_resume.merge_cells('A1:H1')
            cell_titre = ws_resume['A1']
            titre_type = "FOREX" if filter_type == 'forex' else "AUTRES INSTRUMENTS" if filter_type == 'autres' else "TOUS INSTRUMENTS"
            cell_titre.value = f"RAPPORT {titre_type} - {datetime.now().strftime('%d/%m/%Y')}"
            cell_titre.font = Font(size=16, bold=True, color="FFFFFF")
            cell_titre.fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
            cell_titre.alignment = Alignment(horizontal="center", vertical="center")
            
            # Statistiques globales basées sur les trades complets
            total_trades = stats_avancees["total_trades_complets"]
            trades_gagnants = stats_avancees["trades_gagnants_complets"]
            trades_perdants = stats_avancees["trades_perdants_complets"]
            trades_neutres = stats_avancees["trades_neutres_complets"]
            trades_avec_resultat = trades_gagnants + trades_perdants
            
            # Calculer le profit total basé sur les trades complets
            trades_complets = df_final.groupby("Cle_Match").agg({
                "Profit": "sum"
            }).reset_index()
            profit_total_lineaire = trades_complets["Profit"].sum()
            
            profit_total_compose = df_final['Profit_cumule'].iloc[-1] if len(df_final) > 0 else 0

            # Pips totaux et statistiques de pips calculés PAR TRADE COMPLET
            trades_complets_pips = df_final.groupby("Cle_Match").agg({
                "Profit_pips": "sum"
            }).reset_index()
            pips_totaux = trades_complets_pips["Profit_pips"].sum() if len(trades_complets_pips) > 0 else 0
            pips_moyen_par_trade = (pips_totaux / total_trades) if total_trades > 0 else 0
            pips_pertes_total = abs(trades_complets_pips[trades_complets_pips["Profit_pips"] < 0]["Profit_pips"].sum()) if len(trades_complets_pips) > 0 else 0
            pips_moyen_pertes = abs(trades_complets_pips[trades_complets_pips["Profit_pips"] < 0]["Profit_pips"].mean()) if len(trades_complets_pips[trades_complets_pips["Profit_pips"] < 0]) > 0 else 0
            solde_final = df_final['Solde_cumule'].iloc[-1] if len(df_final) > 0 else self.solde_initial
            rendement_pct = ((solde_final - self.solde_initial) / self.solde_initial * 100)
            
            difference_compose = profit_total_compose - profit_total_lineaire
            gain_compose_pct = ((profit_total_compose / profit_total_lineaire - 1) * 100) if profit_total_lineaire != 0 else 0
            taux_reussite = (trades_gagnants / trades_avec_resultat * 100) if trades_avec_resultat > 0 else 0
            
            # Tableau des statistiques
            stats_data = [
                ["📊 STATISTIQUES PRINCIPALES", ""],
                ["", ""],
                ["💰 Solde initial", f"{self.solde_initial:,.2f} €"],
                ["💳 Solde final (composé)", f"{solde_final:,.2f} €"],
                ["📈 Profit total (linéaire)", f"{profit_total_lineaire:,.2f} €"],
                ["🚀 Profit total (composé)", f"{profit_total_compose:,.2f} €"],
                ["⚡ Profits liés aux intérêts composés", f"{difference_compose:,.2f} € (+{gain_compose_pct:.2f}%)"],
                ["📊 Rendement global", f"{rendement_pct:.2f} %"],
                ["🎯 Pips/Points totaux", f"{pips_totaux:,.2f}"],
                ["🎯 Pips moyens par trade", f"{pips_moyen_par_trade:,.2f}"],
                ["❌ Pips perdus (total)", f"{pips_pertes_total:,.2f}"],
                ["❌ Pips moyens lors des pertes", f"{pips_moyen_pertes:,.2f}"],
                ["", ""],
                ["📉 ANALYSE DU DRAWDOWN", ""],
                ["", ""],
                ["📉 Drawdown maximum", f"{stats_avancees['drawdown_max_pct']:.2f} %"],
                ["💸 Drawdown max (euros)", f"{stats_avancees['drawdown_max_euros']:,.2f} €"],
                ["", ""],
                ["🔢 ANALYSE DES TRADES (hors neutres)", ""],
                ["", ""],
                ["📈 Total trades", total_trades],
                ["✅ Trades gagnants", trades_gagnants],
                ["❌ Trades perdants", trades_perdants],
                ["⚪ Trades neutres (exclus)", f"{trades_neutres} (non comptés)"],
                ["🎯 Taux de réussite", f"{taux_reussite:.1f} % (sur {trades_avec_resultat} trades)"],
                ["", ""],
                ["📊 DÉTAIL DES OPÉRATIONS", ""],
                ["", ""],
                ["📈 Total opérations", f"{len(df_final)} (toutes les lignes)"],
                ["📈 Total trades complets", f"{total_trades} (1 IN + 1 ou plusieurs OUT)"],
                ["📈 Trades avec management dynamique", f"{len(df_final[df_final['Direction'] == 'out']) - total_trades} opérations partielles"],
                ["", ""],
                ["📈 SÉRIES ET MOYENNES", ""],
                ["", ""],
                ["🔥 Gains consécutifs max", f"{stats_avancees['gains_consecutifs_max']} trades"],
                ["💔 Pertes consécutives max", f"{stats_avancees['pertes_consecutives_max']} trades"],
                ["💚 Gain moyen", f"{stats_avancees['gain_moyen']:,.2f} €"],
                ["💔 Perte moyenne", f"{stats_avancees['perte_moyenne']:,.2f} €"],
            ]
            
            # Ajout des statistiques par fichier si disponibles
            if self.statistiques_fichiers:
                stats_data.extend([
                    ["", ""],
                    ["📁 DÉTAIL PAR FICHIER", ""],
                    ["", ""]
                ])
                for fichier, stats in self.statistiques_fichiers.items():
                    stats_data.append([f"📄 {fichier[:30]}...", f"{stats['trades']} trades complets, {stats['exclus']} exclus"])
            
            for row_idx, (label, value) in enumerate(stats_data, 3):
                ws_resume[f'A{row_idx}'] = label
                ws_resume[f'B{row_idx}'] = value
                
                # Formatage des en-têtes
                if any(word in label for word in ["STATISTIQUES", "ANALYSE", "DRAWDOWN", "SÉRIES", "DÉTAIL"]):
                    ws_resume[f'A{row_idx}'].font = Font(bold=True, color="366092")
                    ws_resume[f'A{row_idx}'].fill = PatternFill(start_color="E6F3FF", end_color="E6F3FF", fill_type="solid")
                
                ws_resume[f'A{row_idx}'].alignment = Alignment(horizontal="left")
                ws_resume[f'B{row_idx}'].alignment = Alignment(horizontal="right")
            
            print(f"[DEBUG] Summary sheet created with {len(stats_data)} rows")
            
            # === ONGLET 2: DONNÉES BRUTES COMPLÈTES ===
            ws_data = wb.create_sheet("📋 Données Complètes")
            
            # Adapter les noms de colonnes selon le contenu
            df_final_copy = df_final.copy()
            colonnes_adaptees = {}
            
            # Vérifier s'il y a du Forex et des autres instruments
            if "Symbole_ordre" in df_final.columns:
                types_instruments = set()
                for symbole in df_final["Symbole_ordre"].unique():
                    type_inst = self.detecter_type_instrument(symbole)
                    types_instruments.add(type_inst)
                
                # Si on a seulement du Forex -> "Profit_pips"
                # Si on a seulement des autres -> "Profit_points"  
                # Si on a les deux -> "Profit_pips_points"
                if len(types_instruments) == 1:
                    type_unique = list(types_instruments)[0]
                    if type_unique == InstrumentType.FOREX:
                        colonnes_adaptees["Profit_pips"] = "Profit_pips"
                    else:
                        colonnes_adaptees["Profit_pips"] = "Profit_points"
                else:
                    # Mélange de types
                    colonnes_adaptees["Profit_pips"] = "Profit_pips_points"
            
            # Renommer les colonnes si nécessaire
            for ancienne, nouvelle in colonnes_adaptees.items():
                if ancienne in df_final_copy.columns:
                    df_final_copy = df_final_copy.rename(columns={ancienne: nouvelle})
            
            # Insérer toutes les données
            for r in dataframe_to_rows(df_final_copy, index=False, header=True):
                ws_data.append(r)
            
            # Formatage des en-têtes
            for cell in ws_data[1]:
                cell.font = Font(bold=True, color="FFFFFF")
                cell.fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
                cell.alignment = Alignment(horizontal="center")
            
            print(f"[DEBUG] Data sheet created with {len(df_final)} rows")
            
            # === ONGLET 3: ANALYSE PAR INSTRUMENT ===
            if "Symbole_ordre" in df_final.columns:
                ws_instruments = wb.create_sheet("📈 Analyse par Instrument")
                
                # Analyser les performances par instrument
                # Compter les trades complets par instrument (clés uniques)
                trades_par_instrument = df_final.groupby("Symbole_ordre")["Cle_Match"].nunique()
                
                # Calculer les profits par instrument
                profits_par_instrument = df_final.groupby("Symbole_ordre").agg({
                    'Profit': ['sum', 'mean'],
                    'Profit_pips': ['sum', 'mean']
                }).round(2)
                
                # Combiner les résultats
                analyse_instruments = pd.DataFrame({
                    'Nb_Trades': trades_par_instrument,
                    'Profit_Total': profits_par_instrument[('Profit', 'sum')],
                    'Profit_Moyen': profits_par_instrument[('Profit', 'mean')],
                    'Pips_Total': profits_par_instrument[('Profit_pips', 'sum')],
                    'Pips_Moyen': profits_par_instrument[('Profit_pips', 'mean')]
                }).reset_index()
                
                analyse_instruments = analyse_instruments.sort_values('Profit_Total', ascending=False)
                
                # Ajouter le type d'instrument
                analyse_instruments['Type_Instrument'] = analyse_instruments['Symbole_ordre'].apply(self.detecter_type_instrument)
                
                # En-têtes
                headers_instruments = ['Instrument', 'Type', 'Nb Trades', 'Profit Total (€)', 'Profit Moyen (€)', 'Pips/Points Total', 'Pips/Points Moyen']
                for col_idx, header in enumerate(headers_instruments, 1):
                    cell = ws_instruments.cell(row=1, column=col_idx, value=header)
                    cell.font = Font(bold=True, color="FFFFFF")
                    cell.fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
                    cell.alignment = Alignment(horizontal="center")
                
                # Données
                for row_idx, (_, row) in enumerate(analyse_instruments.iterrows(), 2):
                    ws_instruments.cell(row=row_idx, column=1, value=row['Symbole_ordre'])
                    ws_instruments.cell(row=row_idx, column=2, value=str(row['Type_Instrument'].value).upper())
                    ws_instruments.cell(row=row_idx, column=3, value=int(row['Nb_Trades']))
                    ws_instruments.cell(row=row_idx, column=4, value=float(row['Profit_Total']))
                    ws_instruments.cell(row=row_idx, column=5, value=float(row['Profit_Moyen']))
                    ws_instruments.cell(row=row_idx, column=6, value=float(row['Pips_Total']))
                    ws_instruments.cell(row=row_idx, column=7, value=float(row['Pips_Moyen']))
                
                print(f"[DEBUG] Instruments analysis sheet created")
            
            # === ONGLET 4: ANALYSE PAR TYPE D'INSTRUMENT ===
            if "Symbole_ordre" in df_final.columns:
                ws_types = wb.create_sheet("🏷️ Analyse par Type")
                
                # Ajouter une colonne temporaire pour le type d'instrument
                df_final_copy = df_final.copy()
                df_final_copy['Type_Instrument'] = df_final_copy['Symbole_ordre'].apply(self.detecter_type_instrument)
                
                # Convertir les enums en chaînes pour le groupby
                df_final_copy['Type_Instrument_Str'] = df_final_copy['Type_Instrument'].apply(lambda x: x.value)
                
                # Analyser par type d'instrument
                # Compter les trades complets par type (clés uniques)
                trades_par_type = df_final_copy.groupby("Type_Instrument_Str")["Cle_Match"].nunique()
                
                # Calculer les profits par type
                profits_par_type = df_final_copy.groupby("Type_Instrument_Str").agg({
                    'Profit': ['sum', 'mean'],
                    'Profit_pips': ['sum', 'mean']
                }).round(2)
                
                # Combiner les résultats
                analyse_types = pd.DataFrame({
                    'Nb_Trades': trades_par_type,
                    'Profit_Total': profits_par_type[('Profit', 'sum')],
                    'Profit_Moyen': profits_par_type[('Profit', 'mean')],
                    'Pips_Total': profits_par_type[('Profit_pips', 'sum')],
                    'Pips_Moyen': profits_par_type[('Profit_pips', 'mean')]
                }).reset_index()
                
                analyse_types = analyse_types.sort_values('Profit_Total', ascending=False)
                
                # En-têtes
                headers_types = ['Type d\'Instrument', 'Nb Trades', 'Profit Total (€)', 'Profit Moyen (€)', 'Pips/Points Total', 'Pips/Points Moyen']
                for col_idx, header in enumerate(headers_types, 1):
                    cell = ws_types.cell(row=1, column=col_idx, value=header)
                    cell.font = Font(bold=True, color="FFFFFF")
                    cell.fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
                    cell.alignment = Alignment(horizontal="center")
                
                # Données avec icônes selon le type
                type_icons = {
                    InstrumentType.FOREX: '💱',
                    InstrumentType.METAUX: '🥇',
                    InstrumentType.INDICES: '📊',
                    InstrumentType.CRYPTO: '₿',
                    InstrumentType.ENERGIE: '🛢️',
                    InstrumentType.ACTIONS: '📈'
                }
                
                for row_idx, (_, row) in enumerate(analyse_types.iterrows(), 2):
                    type_inst_str = str(row['Type_Instrument_Str'])  # Prendre la vraie valeur du type
                    # Trouver l'enum correspondant pour l'icône
                    type_inst_enum = None
                    for enum_val in InstrumentType:
                        if enum_val.value == type_inst_str:
                            type_inst_enum = enum_val
                            break
                    
                    icon = type_icons.get(type_inst_enum, '📈')
                    
                    # Afficher le nom complet avec l'icône
                    nom_complet = {
                        'forex': 'FOREX',
                        'metaux': 'MÉTAUX', 
                        'indices': 'INDICES',
                        'crypto': 'CRYPTO',
                        'energie': 'ÉNERGIE',
                        'actions': 'ACTIONS'
                    }.get(type_inst_str, type_inst_str.upper())
                    
                    ws_types.cell(row=row_idx, column=1, value=f"{icon} {nom_complet}")
                    ws_types.cell(row=row_idx, column=2, value=int(row['Nb_Trades']))
                    ws_types.cell(row=row_idx, column=3, value=float(row['Profit_Total']))
                    ws_types.cell(row=row_idx, column=4, value=float(row['Profit_Moyen']))
                    ws_types.cell(row=row_idx, column=5, value=float(row['Pips_Total']))
                    ws_types.cell(row=row_idx, column=6, value=float(row['Pips_Moyen']))
                
                print(f"[DEBUG] Instrument types analysis sheet created")
            
            # === ONGLET 5: DÉTAIL PAR INSTRUMENT ===
            if "Symbole_ordre" in df_final.columns:
                # Obtenir la liste unique des instruments
                instruments_uniques = df_final["Symbole_ordre"].unique()
                
                for instrument in instruments_uniques:
                    # Créer un nom d'onglet sécurisé (Excel limite à 31 caractères)
                    nom_onglet = f"📊 {instrument[:25]}" if len(instrument) > 25 else f"📊 {instrument}"
                    
                    # Éviter les doublons d'onglets
                    if nom_onglet in [ws.title for ws in wb.worksheets]:
                        nom_onglet = f"📊 {instrument[:20]}_{hash(instrument) % 1000}"
                    
                    try:
                        ws_instrument = wb.create_sheet(nom_onglet)
                        
                        # Filtrer les données pour cet instrument
                        df_instrument = df_final[df_final["Symbole_ordre"] == instrument].copy()
                        
                        # Titre de l'instrument
                        ws_instrument.merge_cells('A1:H1')
                        cell_titre = ws_instrument['A1']
                        cell_titre.value = f"ANALYSE DÉTAILLÉE - {instrument.upper()}"
                        cell_titre.font = Font(size=14, bold=True, color="FFFFFF")
                        cell_titre.fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
                        cell_titre.alignment = Alignment(horizontal="center", vertical="center")
                        
                        # Déterminer le type d'instrument pour l'affichage
                        type_instrument = self.detecter_type_instrument(instrument)
                        is_forex = (type_instrument == InstrumentType.FOREX)
                        unite_mesure = "Pips" if is_forex else "Points"
                        
                        # Statistiques de l'instrument (basées sur les trades complets)
                        nb_trades_complets = df_instrument["Cle_Match"].nunique()
                        nb_operations = len(df_instrument)
                        
                        # Calculer les trades gagnants/perdants basés sur les trades complets
                        trades_complets_instrument = df_instrument.groupby("Cle_Match").agg({
                            "Profit": "sum"
                        }).reset_index()
                        
                        trades_gagnants = len(trades_complets_instrument[trades_complets_instrument["Profit"] > 0])
                        trades_perdants = len(trades_complets_instrument[trades_complets_instrument["Profit"] < 0])
                        profit_total = df_instrument["Profit"].sum()
                        pips_total = df_instrument["Profit_pips"].sum()
                        taux_reussite = (trades_gagnants / nb_trades_complets * 100) if nb_trades_complets > 0 else 0
                        
                        # Tableau des statistiques
                        stats_instrument = [
                            ["📊 STATISTIQUES DE L'INSTRUMENT", ""],
                            ["", ""],
                            ["📈 Nombre total de trades complets", nb_trades_complets],
                            ["📈 Nombre total d'opérations", nb_operations],
                            ["✅ Trades gagnants", trades_gagnants],
                            ["❌ Trades perdants", trades_perdants],
                            ["🎯 Taux de réussite", f"{taux_reussite:.1f} %"],
                            ["💰 Profit total", f"{profit_total:,.2f} €"],
                            [f"🎯 {unite_mesure} totaux", f"{pips_total:,.2f}"],
                            ["", ""],
                            ["📋 DÉTAIL DES TRADES", ""],
                            ["", ""]
                        ]
                        
                        for row_idx, (label, value) in enumerate(stats_instrument, 3):
                            ws_instrument[f'A{row_idx}'] = label
                            ws_instrument[f'B{row_idx}'] = value
                            
                            if any(word in label for word in ["STATISTIQUES", "DÉTAIL"]):
                                ws_instrument[f'A{row_idx}'].font = Font(bold=True, color="366092")
                                ws_instrument[f'A{row_idx}'].fill = PatternFill(start_color="E6F3FF", end_color="E6F3FF", fill_type="solid")
                        
                        # En-têtes des colonnes de données (adapter selon le type)
                        headers_data = list(df_instrument.columns)
                        headers_adaptes = []
                        for header in headers_data:
                            if header == "Profit_pips":
                                header_adapte = f"Profit_{unite_mesure.lower()}"
                            else:
                                header_adapte = header
                            headers_adaptes.append(header_adapte)
                        
                        for col_idx, header in enumerate(headers_adaptes, 1):
                            cell = ws_instrument.cell(row=len(stats_instrument) + 3, column=col_idx, value=header)
                            cell.font = Font(bold=True, color="FFFFFF")
                            cell.fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
                            cell.alignment = Alignment(horizontal="center")
                        
                        # Données
                        for row_idx, (_, row) in enumerate(df_instrument.iterrows(), len(stats_instrument) + 4):
                            for col_idx, value in enumerate(row, 1):
                                ws_instrument.cell(row=row_idx, column=col_idx, value=value)
                        
                        print(f"[DEBUG] Created detailed sheet for {instrument}")
                        
                    except Exception as e:
                        print(f"[WARNING] Could not create sheet for {instrument}: {str(e)}")
                        continue
            
            # Ajuster la largeur des colonnes
            for ws in wb.worksheets:
                for column in ws.columns:
                    max_length = 0
                    column_letter = get_column_letter(column[0].column)
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = min(max_length + 2, 30)
                    ws.column_dimensions[column_letter].width = adjusted_width
            
            # Sauvegarder
            suffix = f"_{filter_type.upper()}" if filter_type else "_UNIFIED"
            fichier_rapport = os.path.join(reports_folder, f"RAPPORT_TRADING{suffix}_{timestamp}.xlsx")
            wb.save(fichier_rapport)
            
            print(f"[DEBUG] Excel report saved successfully: {fichier_rapport}")
            return fichier_rapport
            
        except Exception as e:
            print(f"[ERROR] Error creating Excel report: {str(e)}")
            import traceback
            print(f"[ERROR] Traceback: {traceback.format_exc()}")
            raise Exception(f"Erreur lors de la création du rapport Excel: {str(e)}")

def main():
    """Fonction principale pour tester le script"""
    analyzer = TradingAnalyzer(solde_initial=10000)
    
    # Exemple d'utilisation
    print("=== ANALYSEUR DE TRADING UNIFIÉ ===")
    print("1. Analyse Forex uniquement")
    print("2. Analyse autres instruments uniquement")
    print("3. Analyse complète (tous instruments)")
    print("4. Quitter")
    
    choix = input("\nChoisissez une option (1-4): ")
    
    if choix == "1":
        print("Analyse Forex sélectionnée")
        # Ici vous ajouteriez la logique pour sélectionner les fichiers
    elif choix == "2":
        print("Analyse autres instruments sélectionnée")
    elif choix == "3":
        print("Analyse complète sélectionnée")
    elif choix == "4":
        print("Au revoir!")
    else:
        print("Option invalide")

if __name__ == "__main__":
    main()