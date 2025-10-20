"""
System cleanup and restoration utilities.
"""

import subprocess
from ui.colors import print_info, print_success, print_warning


class SystemCleanup:
    """Handles system cleanup and restoration."""
    
    def __init__(self):
        self.processes_to_kill = [
            'airodump-ng',
            'aireplay-ng',
            'aircrack-ng',
            'reaver',
            'bully',
            'wash'
        ]
    
    def _execute_command(self, cmd: list, silent: bool = True) -> bool:
        """Execute a system command."""
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                timeout=10
            )
            return result.returncode == 0
        except:
            return False
    
    def kill_conflicting_processes(self):
        """Kill all processes that might interfere."""
        print_info("Limpiando procesos...")
        
        for process in self.processes_to_kill:
            self._execute_command(['killall', process])
        
        print_success("Procesos limpiados")
    
    def restore_network_manager(self):
        """Restore NetworkManager service."""
        print_info("Restaurando NetworkManager...")
        
        if self._execute_command(['systemctl', 'start', 'NetworkManager']):
            print_success("NetworkManager restaurado")
        else:
            print_warning("No se pudo restaurar NetworkManager")
    
    def cleanup_temp_files(self):
        """Remove temporary files created during attacks."""
        import glob
        import os
        
        patterns = [
            '/tmp/wifibreaker*',
            '/tmp/reaver*'
        ]
        
        for pattern in patterns:
            for file in glob.glob(pattern):
                try:
                    os.remove(file)
                except:
                    pass