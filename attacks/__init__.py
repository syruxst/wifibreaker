# ============================================================================
# attacks/__init__.py (ACTUALIZAR ESTE)
# ============================================================================
"""Attack modules for WifiBreaker Pro."""

from .base_attack import BaseAttack
from .wpa_attack import WPAAttack
from .wps_attack import WPSAttack
from .wep_attack import WEPAttack
from .pmkid_attack import PMKIDAttack

__all__ = ['BaseAttack', 'WPAAttack', 'WPSAttack', 'WEPAttack', 'PMKIDAttack']