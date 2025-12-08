#!/usr/bin/env python3
"""
Script pour convertir le fichier symbols_metadata_summary.txt en JSON
pour un broker donné.
"""

import json
import re
import sys
import os

def parse_broker_file(file_path, broker_name):
    """
    Parse le fichier symbols_metadata_summary.txt et crée un JSON structuré.
    
    Args:
        file_path: Chemin vers le fichier symbols_metadata_summary.txt
        broker_name: Nom du broker (ex: "avatrade")
    
    Returns:
        dict: Dictionnaire avec les métadonnées des symboles
    """
    symbols = {}
    
    if not os.path.exists(file_path):
        print(f"Erreur: Le fichier {file_path} n'existe pas.")
        return None
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Diviser par les séparateurs "--------------------------------------------------------------------------------"
    sections = re.split(r'-{50,}', content)
    
    for section in sections:
        if not section.strip():
            continue
        
        symbol_data = {}
        lines = section.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('RÉFÉRENTIEL') or line.startswith('='):
                continue
            
            # Parser les lignes clé: valeur
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()
                
                # Mapping des clés
                if key == 'Symbole':
                    symbol_name = value.upper()
                elif key == 'Classe':
                    symbol_data['class'] = value
                elif key == 'Path MT5':
                    symbol_data['path_mt5'] = value
                elif key == 'Digits':
                    try:
                        symbol_data['digits'] = int(value)
                    except ValueError:
                        symbol_data['digits'] = 0
                elif key == 'Point':
                    try:
                        symbol_data['point'] = float(value)
                    except ValueError:
                        symbol_data['point'] = 0.0
                elif key == 'Pip size':
                    try:
                        symbol_data['pip_size'] = float(value)
                    except ValueError:
                        symbol_data['pip_size'] = 0.0
                elif key == 'Contract size':
                    try:
                        symbol_data['contract_size'] = float(value)
                    except ValueError:
                        symbol_data['contract_size'] = 0.0
                elif key == 'Devise compte':
                    symbol_data['account_currency'] = value
                elif key == 'Valeur 1 pip / lot (devise compte)':
                    try:
                        symbol_data['pip_value_account_currency'] = float(value)
                    except ValueError:
                        symbol_data['pip_value_account_currency'] = 0.0
                elif key == 'Valeur 1 pip / lot en EUR':
                    try:
                        symbol_data['pip_value_eur'] = float(value)
                    except ValueError:
                        symbol_data['pip_value_eur'] = 0.0
                elif key == 'Valeur 1 pip / lot en USD':
                    try:
                        symbol_data['pip_value_usd'] = float(value)
                    except ValueError:
                        symbol_data['pip_value_usd'] = 0.0
                elif key == 'Spread moyen (pips)':
                    try:
                        symbol_data['spread_avg_pips'] = float(value)
                    except ValueError:
                        symbol_data['spread_avg_pips'] = 0.0
                elif key == 'Valeur spread / lot (devise compte)':
                    try:
                        symbol_data['spread_value_account_currency'] = float(value)
                    except ValueError:
                        symbol_data['spread_value_account_currency'] = 0.0
                elif key == 'Valeur spread / lot en EUR':
                    try:
                        symbol_data['spread_value_eur'] = float(value)
                    except ValueError:
                        symbol_data['spread_value_eur'] = 0.0
                elif key == 'Valeur spread / lot en USD':
                    try:
                        symbol_data['spread_value_usd'] = float(value)
                    except ValueError:
                        symbol_data['spread_value_usd'] = 0.0
        
        # Ajouter le symbole au dictionnaire si on a trouvé un nom de symbole
        if 'symbol_name' in locals() and symbol_name:
            symbols[symbol_name] = symbol_data
            del symbol_name
    
    # Créer la structure finale
    result = {
        'broker': broker_name,
        'symbols': symbols
    }
    
    return result

def main():
    if len(sys.argv) < 3:
        print("Usage: python parse_broker_metadata.py <fichier_texte> <nom_broker>")
        print("Exemple: python parse_broker_metadata.py symbols_metadata_summary.txt avatrade")
        sys.exit(1)
    
    file_path = sys.argv[1]
    broker_name = sys.argv[2]
    
    # Créer le dossier brokers s'il n'existe pas
    brokers_dir = os.path.join(os.path.dirname(file_path), 'brokers')
    if not os.path.exists(brokers_dir):
        os.makedirs(brokers_dir)
    
    # Parser le fichier
    print(f"Parsing du fichier {file_path} pour le broker {broker_name}...")
    data = parse_broker_file(file_path, broker_name)
    
    if data is None:
        print("Erreur lors du parsing.")
        sys.exit(1)
    
    # Sauvegarder en JSON
    output_file = os.path.join(brokers_dir, f"{broker_name}.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Fichier JSON créé: {output_file}")
    print(f"   Nombre de symboles: {len(data['symbols'])}")

if __name__ == '__main__':
    main()


