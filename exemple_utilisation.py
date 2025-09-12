#!/usr/bin/env python3
"""
Exemple d'utilisation du TradingAnalyzer unifié
Montre comment analyser Forex, autres instruments, ou tous les instruments
"""

import os
from datetime import datetime
from trading_analyzer_unified import TradingAnalyzer

def exemple_analyse_forex():
    """Exemple d'analyse Forex uniquement"""
    print("=== ANALYSE FOREX ===")
    
    # Créer l'analyseur
    analyzer = TradingAnalyzer(solde_initial=10000)
    
    # Simuler des fichiers à traiter
    file_paths = [
        "chemin/vers/fichier1.xlsx",
        "chemin/vers/fichier2.xlsx"
    ]
    
    # Simuler le suivi de tâche
    task_id = "forex_analysis"
    task_status = {
        task_id: {
            'progress': 0,
            'message': 'Démarrage...'
        }
    }
    
    try:
        # Traiter les fichiers pour Forex uniquement
        df_forex = analyzer.process_files(
            file_paths, 
            task_id, 
            task_status, 
            instrument_filter='forex'
        )
        
        if df_forex is not None:
            # Créer le rapport Excel
            reports_folder = "reports"
            os.makedirs(reports_folder, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            rapport_path = analyzer.create_excel_report(
                df_forex, 
                reports_folder, 
                timestamp, 
                'forex'
            )
            
            print(f"✅ Rapport Forex créé: {rapport_path}")
            print(f"📊 {len(df_forex)} trades analysés")
        else:
            print("❌ Aucune donnée Forex trouvée")
            
    except Exception as e:
        print(f"❌ Erreur lors de l'analyse Forex: {str(e)}")

def exemple_analyse_autres():
    """Exemple d'analyse autres instruments uniquement"""
    print("\n=== ANALYSE AUTRES INSTRUMENTS ===")
    
    # Créer l'analyseur
    analyzer = TradingAnalyzer(solde_initial=10000)
    
    # Simuler des fichiers à traiter
    file_paths = [
        "chemin/vers/fichier1.xlsx",
        "chemin/vers/fichier2.xlsx"
    ]
    
    # Simuler le suivi de tâche
    task_id = "autres_analysis"
    task_status = {
        task_id: {
            'progress': 0,
            'message': 'Démarrage...'
        }
    }
    
    try:
        # Traiter les fichiers pour autres instruments uniquement
        df_autres = analyzer.process_files(
            file_paths, 
            task_id, 
            task_status, 
            instrument_filter='autres'
        )
        
        if df_autres is not None:
            # Créer le rapport Excel
            reports_folder = "reports"
            os.makedirs(reports_folder, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            rapport_path = analyzer.create_excel_report(
                df_autres, 
                reports_folder, 
                timestamp, 
                'autres'
            )
            
            print(f"✅ Rapport Autres instruments créé: {rapport_path}")
            print(f"📊 {len(df_autres)} trades analysés")
        else:
            print("❌ Aucune donnée autres instruments trouvée")
            
    except Exception as e:
        print(f"❌ Erreur lors de l'analyse autres instruments: {str(e)}")

def exemple_analyse_complete():
    """Exemple d'analyse de tous les instruments"""
    print("\n=== ANALYSE COMPLÈTE (TOUS INSTRUMENTS) ===")
    
    # Créer l'analyseur
    analyzer = TradingAnalyzer(solde_initial=10000)
    
    # Simuler des fichiers à traiter
    file_paths = [
        "chemin/vers/fichier1.xlsx",
        "chemin/vers/fichier2.xlsx"
    ]
    
    # Simuler le suivi de tâche
    task_id = "complete_analysis"
    task_status = {
        task_id: {
            'progress': 0,
            'message': 'Démarrage...'
        }
    }
    
    try:
        # Traiter les fichiers pour tous les instruments
        df_complet = analyzer.process_files(
            file_paths, 
            task_id, 
            task_status, 
            instrument_filter=None  # Pas de filtre = tous les instruments
        )
        
        if df_complet is not None:
            # Créer le rapport Excel
            reports_folder = "reports"
            os.makedirs(reports_folder, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            rapport_path = analyzer.create_excel_report(
                df_complet, 
                reports_folder, 
                timestamp, 
                None  # Pas de filtre = rapport unifié
            )
            
            print(f"✅ Rapport complet créé: {rapport_path}")
            print(f"📊 {len(df_complet)} trades analysés")
            
            # Afficher la répartition par type d'instrument
            if 'Type_Instrument' in df_complet.columns:
                repartition = df_complet['Type_Instrument'].value_counts()
                print("\n📈 Répartition par type d'instrument:")
                for type_inst, count in repartition.items():
                    print(f"  - {type_inst.value}: {count} trades")
        else:
            print("❌ Aucune donnée trouvée")
            
    except Exception as e:
        print(f"❌ Erreur lors de l'analyse complète: {str(e)}")

def exemple_analyse_par_type():
    """Exemple d'analyse par type d'instrument spécifique"""
    print("\n=== ANALYSE PAR TYPE D'INSTRUMENT ===")
    
    # Créer l'analyseur
    analyzer = TradingAnalyzer(solde_initial=10000)
    
    # Simuler des fichiers à traiter
    file_paths = [
        "chemin/vers/fichier1.xlsx",
        "chemin/vers/fichier2.xlsx"
    ]
    
    # Simuler le suivi de tâche
    task_id = "type_analysis"
    task_status = {
        task_id: {
            'progress': 0,
            'message': 'Démarrage...'
        }
    }
    
    try:
        # Traiter tous les fichiers
        df_complet = analyzer.process_files(
            file_paths, 
            task_id, 
            task_status, 
            instrument_filter=None
        )
        
        if df_complet is not None and 'Type_Instrument' in df_complet.columns:
            # Analyser par type d'instrument
            from trading_analyzer_unified import InstrumentType
            
            for instrument_type in InstrumentType:
                df_type = df_complet[df_complet['Type_Instrument'] == instrument_type]
                
                if len(df_type) > 0:
                    print(f"\n📊 Analyse {instrument_type.value.upper()}:")
                    print(f"  - Nombre de trades: {len(df_type)}")
                    print(f"  - Profit total: {df_type['Profit'].sum():.2f} €")
                    print(f"  - Profit moyen: {df_type['Profit'].mean():.2f} €")
                    
                    # Créer un rapport spécifique pour ce type
                    reports_folder = "reports"
                    os.makedirs(reports_folder, exist_ok=True)
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    
                    rapport_path = analyzer.create_excel_report(
                        df_type, 
                        reports_folder, 
                        f"{timestamp}_{instrument_type.value}", 
                        None
                    )
                    
                    print(f"  - Rapport créé: {os.path.basename(rapport_path)}")
        else:
            print("❌ Aucune donnée trouvée")
            
    except Exception as e:
        print(f"❌ Erreur lors de l'analyse par type: {str(e)}")

def afficher_statistiques_avancees(df):
    """Affiche des statistiques avancées sur le DataFrame"""
    if df is None or len(df) == 0:
        print("❌ Aucune donnée à analyser")
        return
    
    print("\n📊 STATISTIQUES AVANCÉES:")
    print(f"  - Total trades: {len(df)}")
    print(f"  - Trades gagnants: {len(df[df['Profit'] > 0])}")
    print(f"  - Trades perdants: {len(df[df['Profit'] < 0])}")
    print(f"  - Trades neutres: {len(df[df['Profit'] == 0])}")
    
    if len(df[df['Profit'] != 0]) > 0:
        taux_reussite = len(df[df['Profit'] > 0]) / len(df[df['Profit'] != 0]) * 100
        print(f"  - Taux de réussite: {taux_reussite:.1f}%")
    
    print(f"  - Profit total: {df['Profit'].sum():.2f} €")
    print(f"  - Profit moyen: {df['Profit'].mean():.2f} €")
    print(f"  - Profit max: {df['Profit'].max():.2f} €")
    print(f"  - Profit min: {df['Profit'].min():.2f} €")
    
    if 'Drawdown_pct' in df.columns:
        print(f"  - Drawdown max: {df['Drawdown_pct'].max():.2f}%")
    
    if 'Type_Instrument' in df.columns:
        print("\n📈 Répartition par type:")
        repartition = df['Type_Instrument'].value_counts()
        for type_inst, count in repartition.items():
            print(f"    - {type_inst.value}: {count} trades")

def main():
    """Fonction principale avec menu interactif"""
    print("🚀 TRADING ANALYZER UNIFIÉ")
    print("=" * 50)
    
    while True:
        print("\n📋 MENU PRINCIPAL:")
        print("1. Analyser Forex uniquement")
        print("2. Analyser autres instruments uniquement")
        print("3. Analyser tous les instruments")
        print("4. Analyser par type d'instrument")
        print("5. Afficher les types d'instruments supportés")
        print("6. Quitter")
        
        choix = input("\n🎯 Votre choix (1-6): ").strip()
        
        if choix == "1":
            exemple_analyse_forex()
        elif choix == "2":
            exemple_analyse_autres()
        elif choix == "3":
            exemple_analyse_complete()
        elif choix == "4":
            exemple_analyse_par_type()
        elif choix == "5":
            print("\n📚 TYPES D'INSTRUMENTS SUPPORTÉS:")
            from trading_analyzer_unified import InstrumentType
            for inst_type in InstrumentType:
                print(f"  - {inst_type.value.upper()}")
        elif choix == "6":
            print("👋 Au revoir !")
            break
        else:
            print("❌ Choix invalide. Veuillez choisir 1-6.")

if __name__ == "__main__":
    main() 