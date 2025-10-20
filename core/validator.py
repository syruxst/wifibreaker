"""System requirements validator."""

import subprocess
import shutil
from typing import Dict, List
from ui.colors import Colors


class SystemValidator:
    """Validates system requirements."""
    
    REQUIRED_TOOLS = {
        'aircrack-ng': 'Aircrack suite',
        'airmon-ng': 'Monitor mode',
        'airodump-ng': 'Packet capture',
        'aireplay-ng': 'Packet injection',
        'iwconfig': 'Wireless tools',
        'ifconfig': 'Network config',
    }
    
    OPTIONAL_TOOLS = {
        'reaver': 'WPS attacks',
        'bully': 'WPS alternative',
        'macchanger': 'MAC spoofing',
    }
    
    def __init__(self):
        self.missing_required = []
        self.missing_optional = []
    
    def _check_command(self, command: str) -> bool:
        """Check if command exists."""
        return shutil.which(command) is not None
    
    def check_required_tools(self) -> bool:
        """Check required tools."""
        all_present = True
        
        for tool, desc in self.REQUIRED_TOOLS.items():
            if self._check_command(tool):
                print(f"{Colors.SUCCESS}  ✓ {tool:<15} ({desc}){Colors.ENDC}")
            else:
                print(f"{Colors.FAIL}  ✗ {tool:<15} ({desc}) - FALTANTE{Colors.ENDC}")
                self.missing_required.append(tool)
                all_present = False
        
        return all_present
    
    def check_optional_tools(self):
        """Check optional tools."""
        print(f"\n{Colors.INFO}Herramientas opcionales:{Colors.ENDC}")
        
        for tool, desc in self.OPTIONAL_TOOLS.items():
            if self._check_command(tool):
                print(f"{Colors.SUCCESS}  ✓ {tool:<15} ({desc}){Colors.ENDC}")
            else:
                print(f"{Colors.WARNING}  - {tool:<15} ({desc}) - No instalado{Colors.ENDC}")
                self.missing_optional.append(tool)
    
    def check_python_version(self) -> bool:
        """Check Python version."""
        import sys
        version = sys.version_info
        
        if version.major >= 3 and version.minor >= 8:
            print(f"{Colors.SUCCESS}  ✓ Python {version.major}.{version.minor}.{version.micro}{Colors.ENDC}")
            return True
        else:
            print(f"{Colors.FAIL}  ✗ Python {version.major}.{version.minor} (requiere 3.8+){Colors.ENDC}")
            return False
    
    def check_wireless_extensions(self) -> bool:
        """Check wireless extensions."""
        try:
            result = subprocess.run(['iwconfig'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print(f"{Colors.SUCCESS}  ✓ Extensiones wireless OK{Colors.ENDC}")
                return True
        except:
            pass
        
        print(f"{Colors.FAIL}  ✗ Extensiones wireless no disponibles{Colors.ENDC}")
        return False
    
    def check_all(self) -> bool:
        """Run all checks."""
        print(f"\n{Colors.HEADER}Validando sistema:{Colors.ENDC}\n")
        
        python_ok = self.check_python_version()
        print(f"\n{Colors.INFO}Herramientas requeridas:{Colors.ENDC}")
        tools_ok = self.check_required_tools()
        self.check_optional_tools()
        print(f"\n{Colors.INFO}Sistema:{Colors.ENDC}")
        wireless_ok = self.check_wireless_extensions()
        
        if not (python_ok and tools_ok and wireless_ok):
            print(f"\n{Colors.FAIL}═══════════════════════════════════════{Colors.ENDC}")
            print(f"{Colors.FAIL}  Faltan dependencias críticas{Colors.ENDC}")
            print(f"{Colors.FAIL}═══════════════════════════════════════{Colors.ENDC}")
            
            if self.missing_required:
                print(f"\n{Colors.WARNING}Ejecuta: ./setup.sh{Colors.ENDC}")
            
            return False
        
        print(f"\n{Colors.SUCCESS}═══════════════════════════════════════{Colors.ENDC}")
        print(f"{Colors.SUCCESS}  Sistema OK{Colors.ENDC}")
        print(f"{Colors.SUCCESS}═══════════════════════════════════════{Colors.ENDC}")
        
        return True