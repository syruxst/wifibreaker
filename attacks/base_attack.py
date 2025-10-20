"""
Base class for all attack modules.
"""

from abc import ABC, abstractmethod
from core.scanner import WiFiNetwork


class BaseAttack(ABC):
    """Abstract base class for attacks."""
    
    def __init__(self, interface: str, target: WiFiNetwork):
        self.interface = interface
        self.target = target
        self.success = False
        self.result = None
    
    @abstractmethod
    def execute(self) -> bool:
        """Execute the attack. Must be implemented by subclasses."""
        pass
    
    @abstractmethod
    def cleanup(self):
        """Cleanup resources after attack."""
        pass