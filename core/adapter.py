"""
WiFi adapter detection and management.
"""

import subprocess
import re
from typing import List, Dict, Optional
from ui.colors import Colors, print_error, print_info


class AdapterManager:
    """Manages WiFi adapter detection and configuration."""
    
    def __init__(self):
        self.adapters = []
        self.selected_adapter = None
    
    def _execute_command(self, cmd: List[str]) -> tuple:
        """Execute a system command and return output."""
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return -1, "", "Command timeout"
        except Exception as e:
            return -1, "", str(e)
    
    def _get_wireless_interfaces(self) -> List[str]:
        """Get list of wireless interfaces."""
        interfaces = []
        
        # Method 1: Using iwconfig
        code, output, _ = self._execute_command(['iwconfig'])
        if code == 0:
            for line in output.split('\n'):
                if 'IEEE 802.11' in line or 'ESSID' in line:
                    interface = line.split()[0]
                    if interface and interface not in interfaces:
                        interfaces.append(interface)
        
        # Method 2: Using iw dev (fallback)
        if not interfaces:
            code, output, _ = self._execute_command(['iw', 'dev'])
            if code == 0:
                for line in output.split('\n'):
                    if 'Interface' in line:
                        parts = line.split()
                        if len(parts) >= 2:
                            interface = parts[1]
                            if interface not in interfaces:
                                interfaces.append(interface)
        
        return interfaces
    
    def _get_adapter_info(self, interface: str) -> Dict:
        """Get detailed information about an adapter."""
        info = {
            'interface': interface,
            'driver': 'Unknown',
            'chipset': 'Unknown',
            'monitor_support': False,
            'injection_support': False,
            'mac_address': 'Unknown'
        }
        
        # Get driver info
        try:
            with open(f'/sys/class/net/{interface}/device/uevent', 'r') as f:
                content = f.read()
                driver_match = re.search(r'DRIVER=(.+)', content)
                if driver_match:
                    info['driver'] = driver_match.group(1)
        except:
            pass
        
        # Get MAC address
        code, output, _ = self._execute_command(['cat', f'/sys/class/net/{interface}/address'])
        if code == 0:
            info['mac_address'] = output.strip()
        
        # Check monitor mode support using iw
        code, output, _ = self._execute_command(['iw', 'list'])
        if code == 0:
            # Check supported modes
            if 'monitor' in output.lower() or 'Monitor' in output:
                info['monitor_support'] = True
            # Also check by trying to list interface capabilities
            code2, output2, _ = self._execute_command(['iw', interface, 'info'])
            if code2 == 0 and 'type managed' in output2.lower():
                # Even managed interfaces can usually be put in monitor mode
                info['monitor_support'] = True
        
        # Check injection support (heuristic based on driver)
        injection_drivers = ['rtl', 'ath', 'rt2', 'rt3', 'rt5', 'iwl', 'mt7']
        if any(driver in info['driver'].lower() for driver in injection_drivers):
            info['injection_support'] = True
        
        # Get chipset info
        code, output, _ = self._execute_command(['lsusb'])
        if code == 0:
            # Try to match chipset from USB info
            for line in output.split('\n'):
                if 'wireless' in line.lower() or '802.11' in line.lower():
                    parts = line.split(': ')
                    if len(parts) > 1:
                        info['chipset'] = parts[1][:50]
                        break
        
        return info
    
    def detect_adapters(self) -> List[Dict]:
        """Detect all available wireless adapters."""
        print_info("Buscando adaptadores wireless...")
        
        interfaces = self._get_wireless_interfaces()
        
        if not interfaces:
            print_error("No se encontraron adaptadores wireless")
            return []
        
        self.adapters = []
        for iface in interfaces:
            adapter_info = self._get_adapter_info(iface)
            self.adapters.append(adapter_info)
        
        return self.adapters
    
    def list_adapters(self) -> None:
        """Display all detected adapters."""
        if not self.adapters:
            print_error("No hay adaptadores detectados. Ejecuta detect_adapters() primero.")
            return
        
        print(f"\n{Colors.HEADER}╔═══════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║        Adaptadores WiFi Detectados                       ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╚═══════════════════════════════════════════════════════════╝{Colors.ENDC}\n")
        
        for idx, adapter in enumerate(self.adapters, 1):
            print(f"{Colors.BOLD}[{idx}] {adapter['interface']}{Colors.ENDC}")
            print(f"    {Colors.INFO}├─ Driver:{Colors.ENDC} {adapter['driver']}")
            print(f"    {Colors.INFO}├─ MAC:{Colors.ENDC} {adapter['mac_address']}")
            print(f"    {Colors.INFO}├─ Chipset:{Colors.ENDC} {adapter['chipset']}")
            
            monitor_status = f"{Colors.SUCCESS}✓ Soportado{Colors.ENDC}" if adapter['monitor_support'] else f"{Colors.FAIL}✗ No soportado{Colors.ENDC}"
            print(f"    {Colors.INFO}├─ Modo Monitor:{Colors.ENDC} {monitor_status}")
            
            injection_status = f"{Colors.SUCCESS}✓ Probable{Colors.ENDC}" if adapter['injection_support'] else f"{Colors.WARNING}? Desconocido{Colors.ENDC}"
            print(f"    {Colors.INFO}└─ Inyección:{Colors.ENDC} {injection_status}")
            print()
    
    def select_adapter(self, index: int = 0) -> Optional[Dict]:
        """Select an adapter by index."""
        if not self.adapters:
            print_error("No hay adaptadores disponibles")
            return None
        
        if index < 0 or index >= len(self.adapters):
            print_error(f"Índice inválido: {index}")
            return None
        
        self.selected_adapter = self.adapters[index]
        return self.selected_adapter
    
    def get_selected_adapter(self) -> Optional[Dict]:
        """Get the currently selected adapter."""
        return self.selected_adapter
    
    def check_adapter_status(self, interface: str) -> Dict:
        """Check current status of an adapter."""
        status = {
            'up': False,
            'mode': 'Unknown',
            'channel': None,
            'power': None
        }
        
        # Check if interface is up
        code, output, _ = self._execute_command(['ip', 'link', 'show', interface])
        if code == 0 and 'UP' in output:
            status['up'] = True
        
        # Get current mode and channel
        code, output, _ = self._execute_command(['iwconfig', interface])
        if code == 0:
            mode_match = re.search(r'Mode:(\w+)', output)
            if mode_match:
                status['mode'] = mode_match.group(1)
            
            channel_match = re.search(r'Channel[=:](\d+)', output)
            if channel_match:
                status['channel'] = int(channel_match.group(1))
            
            power_match = re.search(r'Tx-Power[=:](\d+)', output)
            if power_match:
                status['power'] = int(power_match.group(1))
        
        return status