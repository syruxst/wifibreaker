"""
Intelligent attack method selector.
"""

from core.scanner import WiFiNetwork
from typing import Dict


class AttackSelector:
    """Selects optimal attack method for a target."""
    
    def select_best_attack(self, network: WiFiNetwork) -> Dict:
        """Determine best attack method."""
        
        security = network.get_security_type()
        
        if security == 'OPEN':
            return {
                'method': 'none',
                'priority': 1,
                'description': 'Red abierta'
            }
        
        if network.wps and not network.wps_locked:
            return {
                'method': 'wps_pixie',
                'priority': 2,
                'description': 'WPS Pixie Dust'
            }
        
        if security == 'WEP':
            return {
                'method': 'wep',
                'priority': 3,
                'description': 'Ataque WEP'
            }
        
        if network.clients > 0:
            return {
                'method': 'wpa_handshake',
                'priority': 4,
                'description': 'WPA Handshake'
            }
        
        return {
            'method': 'pmkid',
            'priority': 5,
            'description': 'PMKID Attack'
        }
