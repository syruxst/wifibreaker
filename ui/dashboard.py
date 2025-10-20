"""Real-time dashboard for monitoring attacks."""

import time
from ui.colors import Colors


class Dashboard:
    """Real-time attack monitoring dashboard."""
    
    def __init__(self):
        self.start_time = None
        self.stats = {
            'packets': 0,
            'handshakes': 0,
            'deauths_sent': 0
        }
    
    def start(self):
        """Start dashboard."""
        self.start_time = time.time()
    
    def update_stat(self, key: str, value: int):
        """Update a statistic."""
        if key in self.stats:
            self.stats[key] = value
    
    def display(self):
        """Display current stats."""
        if not self.start_time:
            return
        
        elapsed = int(time.time() - self.start_time)
        
        print(f"\r{Colors.OKCYAN}Tiempo: {elapsed}s | "
              f"Paquetes: {self.stats['packets']} | "
              f"Deauths: {self.stats['deauths_sent']}{Colors.ENDC}", 
              end='', flush=True)