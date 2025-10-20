#!/usr/bin/env python3
"""
WifiBreaker Pro - Automated WiFi Auditing Suite
Author: Security Research Team
Version: 1.0.0

Main entry point for the application.
"""

import sys
import os
import signal
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from core.validator import SystemValidator
from core.adapter import AdapterManager
from core.monitor import MonitorMode
from ui.menu import MainMenu
from ui.colors import Colors, print_banner
from utils.logger import Logger
from utils.cleanup import SystemCleanup


class WifiBreaker:
    """Main application class."""
    
    def __init__(self):
        self.logger = Logger()
        self.validator = SystemValidator()
        self.adapter_manager = None
        self.monitor_mode = None
        self.cleanup = SystemCleanup()
        
        # Setup signal handlers for cleanup
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, sig, frame):
        """Handle interrupt signals gracefully."""
        print(f"\n\n{Colors.WARNING}[!] Interrumpido por el usuario{Colors.ENDC}")
        self.cleanup_and_exit()
    
    def check_root(self):
        """Verify the script is running with root privileges."""
        if os.geteuid() != 0:
            print(f"{Colors.FAIL}[✗] Este script requiere privilegios de root{Colors.ENDC}")
            print(f"{Colors.INFO}[i] Ejecuta: sudo python3 {sys.argv[0]}{Colors.ENDC}")
            sys.exit(1)
        print(f"{Colors.SUCCESS}[✓] Ejecutando con privilegios root{Colors.ENDC}")
    
    def validate_system(self):
        """Validate system requirements."""
        print(f"\n{Colors.HEADER}[*] Validando dependencias del sistema...{Colors.ENDC}")
        
        if not self.validator.check_all():
            print(f"{Colors.FAIL}[✗] Faltan dependencias críticas{Colors.ENDC}")
            print(f"{Colors.INFO}[i] Ejecuta './setup.sh' para instalar dependencias{Colors.ENDC}")
            sys.exit(1)
        
        print(f"{Colors.SUCCESS}[✓] Todas las dependencias están instaladas{Colors.ENDC}")
    
    def initialize_adapter(self):
        """Initialize WiFi adapter management."""
        print(f"\n{Colors.HEADER}[*] Detectando adaptadores WiFi...{Colors.ENDC}")
        
        self.adapter_manager = AdapterManager()
        adapters = self.adapter_manager.detect_adapters()
        
        if not adapters:
            print(f"{Colors.FAIL}[✗] No se detectaron adaptadores WiFi{Colors.ENDC}")
            sys.exit(1)
        
        # Use first adapter by default (can be changed in menu)
        adapter = adapters[0]
        print(f"{Colors.SUCCESS}[✓] Adaptador detectado: {adapter['interface']}{Colors.ENDC}")
        print(f"{Colors.INFO}    Driver: {adapter['driver']}{Colors.ENDC}")
        print(f"{Colors.INFO}    Modo Monitor: {'Soportado' if adapter['monitor_support'] else 'No soportado'}{Colors.ENDC}")
        
        if not adapter['monitor_support']:
            print_warning("⚠ El adaptador puede no soportar modo monitor correctamente")
            print_info("Algunas funciones pueden no estar disponibles")
            
            confirm = input(f"\n{Colors.BOLD}¿Intentar continuar de todos modos? (s/N): {Colors.ENDC}").strip().lower()
            if confirm != 's':
                print_info("Revisa tus adaptadores de red e intenta de nuevo")
                print_info("Conecta un adaptador compatible y vuelve a ejecutar")
                sys.exit(0)
            else:
                print_warning("Continuando con adaptador sin soporte verificado...")
        
        return adapter
    
    def enable_monitor_mode(self, adapter):
        """Enable monitor mode on the adapter."""
        print(f"\n{Colors.HEADER}[*] Configurando modo monitor...{Colors.ENDC}")
        
        self.monitor_mode = MonitorMode(adapter['interface'])
        
        if not self.monitor_mode.enable():
            print(f"{Colors.FAIL}[✗] Error al activar modo monitor{Colors.ENDC}")
            sys.exit(1)
        
        mon_interface = self.monitor_mode.get_monitor_interface()
        print(f"{Colors.SUCCESS}[✓] Modo monitor activado: {mon_interface}{Colors.ENDC}")
        
        return mon_interface
    
    def run_main_menu(self, mon_interface):
        """Run the main interactive menu."""
        menu = MainMenu(mon_interface)
        menu.run()
    
    def cleanup_and_exit(self, exit_code=0):
        """Clean up and exit the application."""
        print(f"\n{Colors.HEADER}[*] Restaurando sistema...{Colors.ENDC}")
        
        if self.monitor_mode:
            self.monitor_mode.disable()
        
        self.cleanup.restore_network_manager()
        self.cleanup.kill_conflicting_processes()
        
        print(f"{Colors.SUCCESS}[✓] Sistema restaurado correctamente{Colors.ENDC}")
        print(f"\n{Colors.HEADER}¡Gracias por usar WifiBreaker Pro!{Colors.ENDC}\n")
        sys.exit(exit_code)
    
    def run(self):
        """Main execution flow."""
        try:
            # Print banner
            print_banner()
            
            # 1. Check root privileges
            self.check_root()
            
            # 2. Validate system dependencies
            self.validate_system()
            
            # 3. Initialize adapter
            adapter = self.initialize_adapter()
            
            # 4. Enable monitor mode
            mon_interface = self.enable_monitor_mode(adapter)
            
            # 5. Run main menu
            self.run_main_menu(mon_interface)
            
        except KeyboardInterrupt:
            self._signal_handler(None, None)
        except Exception as e:
            self.logger.error(f"Error crítico: {e}")
            print(f"\n{Colors.FAIL}[✗] Error crítico: {e}{Colors.ENDC}")
            self.cleanup_and_exit(1)
        else:
            self.cleanup_and_exit(0)


def main():
    """Entry point."""
    app = WifiBreaker()
    app.run()


if __name__ == "__main__":
    main()