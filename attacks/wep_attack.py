# ============================================================================
# attacks/wep_attack.py
# ============================================================================
"""
WEP attack implementation (placeholder for future).
"""

from attacks.base_attack import BaseAttack
from ui.colors import print_warning


class WEPAttack(BaseAttack):
    """WEP attack implementation."""
    
    def execute(self) -> bool:
        print_warning("Ataque WEP aún no implementado")
        print_warning("Será implementado en versión futura")
        return False
    
    def cleanup(self):
        pass