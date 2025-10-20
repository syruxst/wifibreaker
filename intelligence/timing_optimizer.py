"""
Attack timing optimization.
"""


class TimingOptimizer:
    """Optimizes attack timing and delays."""
    
    def __init__(self):
        self.default_deauth_delay = 2
        self.default_retry_delay = 5
    
    def calculate_deauth_timing(self, clients: int) -> int:
        """Calculate optimal deauth timing."""
        if clients == 0:
            return 10
        elif clients <= 3:
            return 5
        else:
            return 2
    
    def calculate_retry_timing(self, attempt: int) -> int:
        """Calculate retry delay with exponential backoff."""
        return min(self.default_retry_delay * (2 ** attempt), 60)