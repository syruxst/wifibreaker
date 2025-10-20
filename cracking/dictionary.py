# ============================================================================
# cracking/dictionary.py
# ============================================================================
"""
Dictionary-based password cracking.
"""

import subprocess
import re
from typing import Optional
from ui.colors import print_info, print_success, print_error


class DictionaryCracker:
    """Simple dictionary attack using aircrack-ng."""
    
    def __init__(self, capture_file: str, bssid: str):
        self.capture_file = capture_file
        self.bssid = bssid
        self.password = None
    
    def crack(self, wordlist: str) -> Optional[str]:
        """Crack password using wordlist."""
        print_info(f"Usando wordlist: {wordlist}")
        
        cmd = [
            'aircrack-ng',
            '-w', wordlist,
            '-b', self.bssid,
            self.capture_file
        ]
        
        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )
            
            for line in process.stdout:
                if 'KEY FOUND!' in line:
                    match = re.search(r'\[ (.+) \]', line)
                    if match:
                        self.password = match.group(1)
                        print_success(f"Password: {self.password}")
                        return self.password
            
            process.wait()
            return None
        
        except Exception as e:
            print_error(f"Error: {e}")
            return None