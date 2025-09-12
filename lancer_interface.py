#!/usr/bin/env python3
"""
Script de lancement pour l'interface graphique du Trading Analyzer
"""

import sys
import os

def check_dependencies():
    """Vérifie que toutes les dépendances sont installées"""
    required_packages = ['pandas', 'openpyxl', 'tkinter']
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'tkinter':
                import tkinter
            else:
                __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Dépendances manquantes:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n📦 Installation des dépendances:")
        print("pip install pandas openpyxl")
        return False
    
    return True

def main():
    """Fonction principale"""
    print("🚀 Lancement de l'interface Trading Analyzer...")
    
    # Vérifier les dépendances
    if not check_dependencies():
        input("\nAppuyez sur Entrée pour quitter...")
        return
    
    # Vérifier que le script principal existe
    if not os.path.exists('trading_analyzer_unified.py'):
        print("❌ Erreur: Le fichier 'trading_analyzer_unified.py' est manquant.")
        print("Assurez-vous qu'il est dans le même dossier que ce script.")
        input("\nAppuyez sur Entrée pour quitter...")
        return
    
    # Vérifier que l'interface existe
    if not os.path.exists('interface_trading_analyzer.py'):
        print("❌ Erreur: Le fichier 'interface_trading_analyzer.py' est manquant.")
        print("Assurez-vous qu'il est dans le même dossier que ce script.")
        input("\nAppuyez sur Entrée pour quitter...")
        return
    
    print("✅ Toutes les vérifications sont passées!")
    print("📱 Lancement de l'interface graphique...")
    
    try:
        # Importer et lancer l'interface
        from interface_trading_analyzer import main as launch_gui
        launch_gui()
    except Exception as e:
        print(f"❌ Erreur lors du lancement: {str(e)}")
        input("\nAppuyez sur Entrée pour quitter...")

if __name__ == "__main__":
    main() 