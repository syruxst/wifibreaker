"""
Intelligent target scoring system.
Evaluates WiFi networks and prioritizes attack targets.
"""

from typing import Dict
from core.scanner import WiFiNetwork


class TargetScorer:
    """Scores and prioritizes WiFi targets for attacking."""
    
    def __init__(self):
        self.weights = {
            'signal': 0.35,      
            'clients': 0.25,     
            'security': 0.20,    
            'wps': 0.15,         
            'activity': 0.05     
        }
    
    def _score_signal(self, network: WiFiNetwork) -> int:
        """Score based on signal strength (0-100)."""
        signal = network.signal
        
        if signal >= -30:
            return 100
        elif signal >= -50:
            return 90
        elif signal >= -60:
            return 75
        elif signal >= -70:
            return 50
        elif signal >= -80:
            return 25
        else:
            return 10
    
    def _score_clients(self, network: WiFiNetwork) -> int:
        """Score based on number of connected clients (0-100)."""
        clients = network.clients
        
        if clients == 0:
            return 20  
        elif 1 <= clients <= 3:
            return 100  
        elif 4 <= clients <= 10:
            return 80  
        else:
            return 60  
    
    def _score_security(self, network: WiFiNetwork) -> int:
        """Score based on security type (0-100)."""
        security = network.get_security_type()
        
        security_scores = {
            'OPEN': 100,    
            'WEP': 95,      
            'WPA': 70,      
            'WPA2': 60,    
            'WPA3': 30,     
            'Unknown': 40
        }
        
        return security_scores.get(security, 40)
    
    def _score_wps(self, network: WiFiNetwork) -> int:
        """Score based on WPS availability (0-100)."""
        if network.wps and not network.wps_locked:
            return 100  
        elif network.wps and network.wps_locked:
            return 30   
        else:
            return 0    
    
    def _score_activity(self, network: WiFiNetwork) -> int:
        """Score based on network activity (0-100)."""
        beacons = network.beacons
        data = network.data_packets
        
        total_packets = beacons + data
        
        if total_packets > 1000:
            return 100
        elif total_packets > 500:
            return 80
        elif total_packets > 100:
            return 60
        else:
            return 40
    
    def calculate_score(self, network: WiFiNetwork) -> int:
        """Calculate overall attack priority score (0-100)."""
        signal_score = self._score_signal(network)
        clients_score = self._score_clients(network)
        security_score = self._score_security(network)
        wps_score = self._score_wps(network)
        activity_score = self._score_activity(network)
        
        total_score = (
            signal_score * self.weights['signal'] +
            clients_score * self.weights['clients'] +
            security_score * self.weights['security'] +
            wps_score * self.weights['wps'] +
            activity_score * self.weights['activity']
        )
        
        return int(total_score)
    
    def get_score_breakdown(self, network: WiFiNetwork) -> Dict[str, int]:
        """Get detailed scoring breakdown."""
        return {
            'signal': int(self._score_signal(network) * self.weights['signal']),
            'clients': int(self._score_clients(network) * self.weights['clients']),
            'security': int(self._score_security(network) * self.weights['security']),
            'wps': int(self._score_wps(network) * self.weights['wps']),
            'activity': int(self._score_activity(network) * self.weights['activity'])
        }
    
    def get_attack_recommendation(self, network: WiFiNetwork) -> Dict:
        """Get recommended attack strategy for a network."""
        score = self.calculate_score(network)
        security = network.get_security_type()
        
        recommendation = {
            'score': score,
            'difficulty': 'Unknown',
            'method': 'Unknown',
            'estimated_time': 'Unknown',
            'success_probability': 0
        }
        
        if score >= 80:
            recommendation['difficulty'] = 'Fácil'
            recommendation['success_probability'] = 90
        elif score >= 60:
            recommendation['difficulty'] = 'Medio'
            recommendation['success_probability'] = 65
        else:
            recommendation['difficulty'] = 'Difícil'
            recommendation['success_probability'] = 35
        
        if security == 'OPEN':
            recommendation['method'] = 'Sin contraseña'
            recommendation['estimated_time'] = 'Instantáneo'
            recommendation['success_probability'] = 100
        
        elif security == 'WEP':
            recommendation['method'] = 'Ataque WEP (ARP Replay)'
            recommendation['estimated_time'] = '5-15 minutos'
            recommendation['success_probability'] = 95
        
        elif network.wps and not network.wps_locked:
            recommendation['method'] = 'WPS Pixie Dust'
            recommendation['estimated_time'] = '30-120 segundos'
            recommendation['success_probability'] = 85
        
        elif security in ['WPA', 'WPA2']:
            if network.clients > 0:
                recommendation['method'] = 'Handshake + Diccionario'
                recommendation['estimated_time'] = '1-10 minutos (captura) + variable (crack)'
                recommendation['success_probability'] = 60
            else:
                recommendation['method'] = 'PMKID Attack'
                recommendation['estimated_time'] = 'Variable'
                recommendation['success_probability'] = 40
        
        elif security == 'WPA3':
            recommendation['method'] = 'Ataque Dragonblood (si vulnerable)'
            recommendation['estimated_time'] = 'Varias horas'
            recommendation['success_probability'] = 20
        
        return recommendation