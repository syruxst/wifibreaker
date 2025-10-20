"""File management utilities."""

import os
import glob
from typing import List


class FileManager:
    """Manages capture files and results."""
    
    def __init__(self):
        self.captures_dir = "data/captures"
        self.results_dir = "data/results"
        self.logs_dir = "data/logs"
    
    def ensure_directories(self):
        """Ensure all data directories exist."""
        for directory in [self.captures_dir, self.results_dir, self.logs_dir]:
            os.makedirs(directory, exist_ok=True)
    
    def list_captures(self) -> List[str]:
        """List all capture files."""
        pattern = os.path.join(self.captures_dir, "*.cap")
        return glob.glob(pattern)
    
    def list_results(self) -> List[str]:
        """List all result files."""
        pattern = os.path.join(self.results_dir, "*.txt")
        return glob.glob(pattern)
    
    def cleanup_old_captures(self, days: int = 7):
        """Remove old captures."""
        import time
        now = time.time()
        cutoff = now - (days * 86400)
        
        for capture in self.list_captures():
            if os.path.getmtime(capture) < cutoff:
                try:
                    os.remove(capture)
                except:
                    pass