"""Monitor mode management."""

import subprocess
import time
import re
from typing import Optional
from ui.colors import print_error, print_info, print_success, print_warning


class MonitorMode:
    """Manages monitor mode activation/deactivation."""
    
    def __init__(self, interface: str):
        self.interface = interface
        self.monitor_interface = None
        self.conflicting_processes = []
    
    def _execute_command(self, cmd: list, silent: bool = False) -> tuple:
        """Execute system command."""
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if not silent and result.returncode != 0 and result.stderr:
                print_error(f"Error: {result.stderr[:100]}")
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            print_error(f"Timeout: {' '.join(cmd)}")
            return -1, "", "Timeout"
        except Exception as e:
            print_error(f"Excepción: {e}")
            return -1, "", str(e)
    
    def _check_conflicting_processes(self) -> list:
        """Check for conflicting processes."""
        conflicting = ['NetworkManager', 'wpa_supplicant', 'dhclient']
        running = []
        
        for process in conflicting:
            code, _, _ = self._execute_command(['pgrep', '-x', process], silent=True)
            if code == 0:
                running.append(process)
        
        return running
    
    def _kill_conflicting_processes(self) -> bool:
        """Kill conflicting processes."""
        self.conflicting_processes = self._check_conflicting_processes()
        
        if not self.conflicting_processes:
            return True
        
        print_warning(f"Deteniendo: {', '.join(self.conflicting_processes)}")
        
        for process in self.conflicting_processes:
            if process == 'NetworkManager':
                self._execute_command(['systemctl', 'stop', 'NetworkManager'])
            else:
                self._execute_command(['killall', process])
        
        time.sleep(2)
        return True
    
    def _start_monitor_airmon(self) -> Optional[str]:
        """Start monitor mode using airmon-ng."""
        print_info(f"Activando modo monitor en {self.interface}...")
        
        self._execute_command(['airmon-ng', 'check', 'kill'])
        time.sleep(1)
        
        code, output, _ = self._execute_command(['airmon-ng', 'start', self.interface])
        
        if code != 0:
            print_error("Fallo al iniciar modo monitor")
            return None
        
        monitor_iface = None
        for line in output.split('\n'):
            if 'monitor mode' in line.lower() and 'enabled' in line.lower():
                match = re.search(r'on (\w+)', line)
                if match:
                    monitor_iface = match.group(1)
                    break
        
        if not monitor_iface:
            possible = [f"{self.interface}mon", "mon0", "wlan0mon"]
            for name in possible:
                code, _, _ = self._execute_command(['ip', 'link', 'show', name], silent=True)
                if code == 0:
                    monitor_iface = name
                    break
        
        if monitor_iface:
            print_success(f"Modo monitor activado: {monitor_iface}")
            self._execute_command(['ip', 'link', 'set', monitor_iface, 'up'])
        
        return monitor_iface
    
    def enable(self) -> bool:
        """Enable monitor mode."""
        self._kill_conflicting_processes()
        
        monitor_iface = self._start_monitor_airmon()
        
        if monitor_iface:
            self.monitor_interface = monitor_iface
            time.sleep(1)
            code, output, _ = self._execute_command(['iwconfig', monitor_iface])
            if code == 0 and 'Mode:Monitor' in output:
                print_success("✓ Modo monitor verificado")
                return True
        
        print_error("No se pudo activar modo monitor")
        return False
    
    def disable(self) -> bool:
        """Disable monitor mode."""
        if not self.monitor_interface:
            return True
        
        print_info(f"Desactivando modo monitor...")
        
        self._execute_command(['airmon-ng', 'stop', self.monitor_interface])
        
        if 'NetworkManager' in self.conflicting_processes:
            print_info("Reiniciando NetworkManager...")
            self._execute_command(['systemctl', 'start', 'NetworkManager'])
            time.sleep(2)
        
        print_success("Modo monitor desactivado")
        self.monitor_interface = None
        return True
    
    def get_monitor_interface(self) -> Optional[str]:
        """Get monitor interface name."""
        return self.monitor_interface
    
    def set_channel(self, channel: int) -> bool:
        """Set wireless channel."""
        if not self.monitor_interface:
            print_error("Modo monitor no activado")
            return False
        
        if channel < 1 or channel > 14:
            print_error(f"Canal inválido: {channel}")
            return False
        
        code, _, _ = self._execute_command(['iwconfig', self.monitor_interface, 'channel', str(channel)])
        
        if code == 0:
            return True
        else:
            print_error(f"Error configurando canal {channel}")
            return False