#!/usr/bin/env python3
"""
Module de gestion des brokers et de leurs métadonnées de symboles.
"""

import json
import os
from typing import Dict, Optional, Any

class BrokerManager:
    """Gère les métadonnées des brokers pour les calculs de trading."""
    
    def __init__(self, brokers_dir: str = None):
        """
        Initialise le gestionnaire de brokers.
        
        Args:
            brokers_dir: Chemin vers le dossier contenant les fichiers JSON des brokers.
                        Par défaut: 'brokers' dans le répertoire courant.
        """
        if brokers_dir is None:
            brokers_dir = os.path.join(os.path.dirname(__file__), 'brokers')
        self.brokers_dir = brokers_dir
        self._brokers_cache: Dict[str, Dict] = {}
    
    def get_broker_data(self, broker_name: str) -> Optional[Dict]:
        """
        Charge les données d'un broker depuis son fichier JSON.
        
        Args:
            broker_name: Nom du broker (ex: "avatrade")
        
        Returns:
            Dict avec les métadonnées du broker, ou None si non trouvé
        """
        if broker_name is None or broker_name == '':
            return None
        
        # Vérifier le cache
        if broker_name in self._brokers_cache:
            return self._brokers_cache[broker_name]
        
        # Charger depuis le fichier
        broker_file = os.path.join(self.brokers_dir, f"{broker_name.lower()}.json")
        
        if not os.path.exists(broker_file):
            print(f"[WARNING] Fichier broker non trouvé: {broker_file}")
            return None
        
        try:
            with open(broker_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self._brokers_cache[broker_name] = data
            return data
        except Exception as e:
            print(f"[ERROR] Erreur lors du chargement du broker {broker_name}: {str(e)}")
            return None
    
    def get_symbol_metadata(self, broker_name: str, symbol: str) -> Optional[Dict]:
        """
        Récupère les métadonnées d'un symbole spécifique pour un broker.
        
        Args:
            broker_name: Nom du broker
            symbol: Symbole à rechercher (ex: "BTCEUR", "EURUSD")
        
        Returns:
            Dict avec les métadonnées du symbole, ou None si non trouvé
        """
        broker_data = self.get_broker_data(broker_name)
        if broker_data is None:
            return None
        
        symbols = broker_data.get('symbols', {})
        symbol_upper = symbol.upper()
        
        # Chercher le symbole exact
        if symbol_upper in symbols:
            return symbols[symbol_upper]
        
        # Chercher avec variations (sans espaces, etc.)
        for key, value in symbols.items():
            if key.replace(' ', '').upper() == symbol_upper.replace(' ', '').upper():
                return value
        
        return None
    
    def get_pip_value(self, broker_name: str, symbol: str, currency: str = 'USD') -> Optional[float]:
        """
        Récupère la valeur d'un pip pour un symbole donné.
        
        Args:
            broker_name: Nom du broker
            symbol: Symbole
            currency: Devise souhaitée ('USD', 'EUR', ou 'account_currency')
        
        Returns:
            Valeur d'un pip par lot, ou None si non trouvé
        """
        metadata = self.get_symbol_metadata(broker_name, symbol)
        if metadata is None:
            return None
        
        if currency.upper() == 'USD':
            return metadata.get('pip_value_usd')
        elif currency.upper() == 'EUR':
            return metadata.get('pip_value_eur')
        else:
            # Devise du compte
            return metadata.get('pip_value_account_currency')
    
    def get_pip_size(self, broker_name: str, symbol: str) -> Optional[float]:
        """Récupère la taille d'un pip pour un symbole."""
        metadata = self.get_symbol_metadata(broker_name, symbol)
        if metadata is None:
            return None
        return metadata.get('pip_size')
    
    def get_contract_size(self, broker_name: str, symbol: str) -> Optional[float]:
        """Récupère la taille du contrat pour un symbole."""
        metadata = self.get_symbol_metadata(broker_name, symbol)
        if metadata is None:
            return None
        return metadata.get('contract_size')
    
    def get_point(self, broker_name: str, symbol: str) -> Optional[float]:
        """Récupère la valeur d'un point pour un symbole."""
        metadata = self.get_symbol_metadata(broker_name, symbol)
        if metadata is None:
            return None
        return metadata.get('point')
    
    def list_available_brokers(self) -> list:
        """
        Liste tous les brokers disponibles (fichiers JSON dans le dossier brokers).
        
        Returns:
            Liste des noms de brokers disponibles
        """
        if not os.path.exists(self.brokers_dir):
            return []
        
        brokers = []
        for filename in os.listdir(self.brokers_dir):
            if filename.endswith('.json'):
                broker_name = filename[:-5]  # Enlever .json
                brokers.append(broker_name)
        
        return sorted(brokers)

# Instance globale pour faciliter l'utilisation
_broker_manager_instance = None

def get_broker_manager() -> BrokerManager:
    """Retourne l'instance globale du BrokerManager."""
    global _broker_manager_instance
    if _broker_manager_instance is None:
        _broker_manager_instance = BrokerManager()
    return _broker_manager_instance


