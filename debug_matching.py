#!/usr/bin/env python3
"""
Script de debug pour analyser les lignes sans clé dans le rapport Excel
"""

import pandas as pd
import os
from datetime import datetime

def analyze_excel_report(file_path):
    """Analyse le fichier Excel pour identifier les lignes sans clé"""
    
    print(f"🔍 ANALYSE DU FICHIER: {os.path.basename(file_path)}")
    print("=" * 80)
    
    try:
        # Lire le fichier Excel
        df = pd.read_excel(file_path, sheet_name="📋 Données Complètes")
        print(f"✅ Fichier lu avec succès: {len(df)} lignes")
        
        # Vérifier les colonnes disponibles
        print(f"\n📊 COLONNES DISPONIBLES:")
        for i, col in enumerate(df.columns):
            print(f"  {i+1}. {col}")
        
        # Identifier les lignes sans clé
        lignes_sans_cle = df[df["Cle_Match"].isna()].copy()
        lignes_avec_cle = df[df["Cle_Match"].notna()].copy()
        
        print(f"\n🔑 ANALYSE DES CLÉS:")
        print(f"  - Total lignes: {len(df)}")
        print(f"  - Lignes avec clé: {len(lignes_avec_cle)}")
        print(f"  - Lignes sans clé: {len(lignes_sans_cle)}")
        print(f"  - Taux de réussite: {(len(lignes_avec_cle)/len(df)*100):.1f}%")
        
        if len(lignes_sans_cle) > 0:
            print(f"\n❌ LIGNES SANS CLÉ ({len(lignes_sans_cle)} lignes):")
            print("-" * 80)
            
            for idx, row in lignes_sans_cle.iterrows():
                print(f"\n🔍 Ligne {idx+1}:")
                print(f"  - Symbole: {row.get('Symbole_ordre', 'N/A')}")
                print(f"  - Direction: {row.get('Direction', 'N/A')}")
                print(f"  - Ordre: {row.get('Ordre_ordre', 'N/A')}")
                print(f"  - Volume: {row.get('Volume_ordre', 'N/A')}")
                print(f"  - Type: {row.get('Type_ordre', 'N/A')}")
                print(f"  - T/P: {row.get('T / P', 'N/A')}")
                print(f"  - S/L: {row.get('S / L', 'N/A')}")
                print(f"  - Commentaire: {row.get('Commentaire_ordre', 'N/A')}")
                print(f"  - Profit: {row.get('Profit', 'N/A')}")
                print(f"  - Clé: {row.get('Cle_Match', 'VIDE')}")
        
        # Analyser par symbole
        print(f"\n📈 ANALYSE PAR SYMBOLE:")
        print("-" * 80)
        
        for symbole in df["Symbole_ordre"].unique():
            df_symbole = df[df["Symbole_ordre"] == symbole]
            sans_cle = df_symbole[df_symbole["Cle_Match"].isna()]
            avec_cle = df_symbole[df_symbole["Cle_Match"].notna()]
            
            print(f"\n💱 {symbole}:")
            print(f"  - Total: {len(df_symbole)} trades")
            print(f"  - Avec clé: {len(avec_cle)}")
            print(f"  - Sans clé: {len(sans_cle)}")
            print(f"  - Taux: {(len(avec_cle)/len(df_symbole)*100):.1f}%")
            
            if len(sans_cle) > 0:
                print(f"  - Détail sans clé:")
                for _, row in sans_cle.iterrows():
                    print(f"    * {row.get('Direction', 'N/A')} - Ordre {row.get('Ordre_ordre', 'N/A')} - Vol {row.get('Volume_ordre', 'N/A')}")
        
        # Analyser par direction
        print(f"\n🔄 ANALYSE PAR DIRECTION:")
        print("-" * 80)
        
        for direction in df["Direction"].unique():
            df_direction = df[df["Direction"] == direction]
            sans_cle = df_direction[df_direction["Cle_Match"].isna()]
            avec_cle = df_direction[df_direction["Cle_Match"].notna()]
            
            print(f"\n📊 {direction.upper()}:")
            print(f"  - Total: {len(df_direction)} trades")
            print(f"  - Avec clé: {len(avec_cle)}")
            print(f"  - Sans clé: {len(sans_cle)}")
            print(f"  - Taux: {(len(avec_cle)/len(df_direction)*100):.1f}%")
        
        # Analyser les patterns de volumes
        print(f"\n📊 ANALYSE DES VOLUMES:")
        print("-" * 80)
        
        volumes_uniques = df["Volume_ordre"].value_counts()
        print(f"Volumes uniques trouvés:")
        for volume, count in volumes_uniques.head(10).items():
            print(f"  - {volume}: {count} fois")
        
        # Analyser les commentaires
        if "Commentaire_ordre" in df.columns:
            print(f"\n💬 ANALYSE DES COMMENTAIRES:")
            print("-" * 80)
            
            commentaires_sans_cle = lignes_sans_cle["Commentaire_ordre"].value_counts()
            print(f"Commentaires des lignes sans clé:")
            for commentaire, count in commentaires_sans_cle.head(10).items():
                print(f"  - '{commentaire}': {count} fois")
        
        # Créer un rapport de debug
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        debug_file = f"DEBUG_MATCHING_{timestamp}.txt"
        
        with open(debug_file, 'w', encoding='utf-8') as f:
            f.write(f"RAPPORT DE DEBUG - {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
            f.write("=" * 80 + "\n\n")
            
            f.write(f"FICHIER ANALYSÉ: {file_path}\n")
            f.write(f"TOTAL LIGNES: {len(df)}\n")
            f.write(f"LIGNES AVEC CLÉ: {len(lignes_avec_cle)}\n")
            f.write(f"LIGNES SANS CLÉ: {len(lignes_sans_cle)}\n")
            f.write(f"TAUX DE RÉUSSITE: {(len(lignes_avec_cle)/len(df)*100):.1f}%\n\n")
            
            if len(lignes_sans_cle) > 0:
                f.write("DÉTAIL DES LIGNES SANS CLÉ:\n")
                f.write("-" * 80 + "\n")
                
                for idx, row in lignes_sans_cle.iterrows():
                    f.write(f"\nLigne {idx+1}:\n")
                    for col in df.columns:
                        f.write(f"  {col}: {row.get(col, 'N/A')}\n")
        
        print(f"\n✅ Rapport de debug sauvegardé: {debug_file}")
        
        return lignes_sans_cle
        
    except Exception as e:
        print(f"❌ Erreur lors de l'analyse: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return None

def main():
    """Fonction principale"""
    # Chercher le fichier de rapport le plus récent
    reports_dir = "."
    excel_files = [f for f in os.listdir(reports_dir) if f.startswith("RAPPORT_TRADING_UNIFIED") and f.endswith(".xlsx")]
    
    if not excel_files:
        print("❌ Aucun fichier de rapport trouvé")
        return
    
    # Prendre le plus récent
    latest_file = max(excel_files, key=lambda x: os.path.getctime(os.path.join(reports_dir, x)))
    file_path = os.path.join(reports_dir, latest_file)
    
    print(f"🎯 Fichier sélectionné: {latest_file}")
    
    # Analyser le fichier
    lignes_sans_cle = analyze_excel_report(file_path)
    
    if lignes_sans_cle is not None and len(lignes_sans_cle) > 0:
        print(f"\n🚨 PROBLÈME IDENTIFIÉ: {len(lignes_sans_cle)} lignes sans clé!")
        print("Ces lignes empêchent le calcul correct des cumuls chronologiques.")
        print("Il faut corriger la logique de matching pour capturer TOUS les trades.")
    else:
        print(f"\n✅ SUCCÈS: Toutes les lignes ont une clé!")

if __name__ == "__main__":
    main()

