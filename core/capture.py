# ============================================================================
# core/capture.py
# ============================================================================
"""
Packet capture utilities.
"""

import subprocess
from typing import Optional


class PacketCapture:
    """Handles packet capture operations."""
    
    def __init__(self, interface: str):
        self.interface = interface
    
    def start_capture(self, output_file: str, channel: int = None, bssid: str = None):
        """Start packet capture with airodump-ng."""
        cmd = ['airodump-ng', '-w', output_file]
        
        if channel:
            cmd.extend(['-c', str(channel)])
        if bssid:
            cmd.extend(['--bssid', bssid])
        
        cmd.append(self.interface)
        
        return subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)