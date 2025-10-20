# ============================================================================
# cracking/smart_crack.py
# ============================================================================
"""
Intelligent cascading crack strategy.
"""

import os
from typing import Optional, List
from .dictionary import DictionaryCracker
from ui.colors import print_info, print_progress


class SmartCracker:
    """Intelligent multi-method cracking."""
    
    def __init__(self, capture_file: str, bssid: str, ssid: str):
        self.capture_file = capture_file
        self.bssid = bssid
        self.ssid = ssid
        self.cracker = DictionaryCracker(capture_file, bssid)
    
    def crack_cascade(self) -> Optional[str]:
        """Try multiple cracking methods in order."""
        
        wordlists = self._get_wordlist_cascade()
        
        for wordlist_name, wordlist_path in wordlists:
            if not os.path.exists(wordlist_path):
                continue
            
            print_progress(f"Probando con {wordlist_name}...")
            password = self.cracker.crack(wordlist_path)
            
            if password:
                return password
        
        return None
    
    def _get_wordlist_cascade(self) -> List[tuple]:
        """Get ordered list of wordlists to try."""
        return [
            ("Top 1000", "data/wordlists/top1000.txt"),
            ("Common patterns", "data/wordlists/common_patterns.txt"),
            ("Rockyou", "/usr/share/wordlists/rockyou.txt"),
        ]