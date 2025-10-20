"""Logging system."""

import os
import time
from datetime import datetime


class Logger:
    """Simple logging system."""
    
    def __init__(self, log_dir: str = "data/logs"):
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
        
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        self.log_file = os.path.join(log_dir, f"wifibreaker_{timestamp}.log")
    
    def _write(self, level: str, message: str):
        """Write log entry."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}\n"
        
        try:
            with open(self.log_file, 'a') as f:
                f.write(log_entry)
        except:
            pass
    
    def info(self, message: str):
        self._write("INFO", message)
    
    def warning(self, message: str):
        self._write("WARNING", message)
    
    def error(self, message: str):
        self._write("ERROR", message)
    
    def success(self, message: str):
        self._write("SUCCESS", message)