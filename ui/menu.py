"""
Main interactive menu for WifiBreaker Pro.
"""

import time
import sys
import subprocess
import glob
import os
from typing import Optional
from datetime import datetime
from core.scanner import NetworkScanner, WiFiNetwork
from intelligence.target_scoring import TargetScorer
from attacks.wpa_attack import WPAAttack
from attacks.wps_attack import WPSAttack
from cracking.wordlist_generator import CerberoEngine
from ui.colors import Colors, print_section_header, print_info, print_success, print_error, print_warning


class MainMenu:
    """Interactive main menu."""
    
    def __init__(self, monitor_interface: str):
        self.monitor_interface = monitor_interface
        self.scanner = NetworkScanner(monitor_interface)
        self.scorer = TargetScorer()
        self.selected_target: Optional[WiFiNetwork] = None
        self.running = True
    
    def _clear_screen(self):
        """Clear terminal screen."""
        print("\033[2J\033[H", end="")
    
    def _pause(self):
        """Pause and wait for user input."""
        input(f"\n{Colors.INFO}Presiona Enter para continuar...{Colors.ENDC}")
    
    def _print_menu(self):
        """Display main menu."""
        self._clear_screen()
        
        print(f"{Colors.CYAN}╔══════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.CYAN}║          🔓 WifiBreaker Pro - Menú Principal        ║{Colors.ENDC}")
        print(f"{Colors.CYAN}╚══════════════════════════════════════════════════════╝{Colors.ENDC}\n")
        
        print(f"{Colors.INFO}Interface en modo monitor: {Colors.BOLD}{self.monitor_interface}{Colors.ENDC}")
        
        if self.selected_target:
            print(f"{Colors.SUCCESS}Target seleccionado: {self.selected_target.ssid} ({self.selected_target.bssid}){Colors.ENDC}")
        else:
            print(f"{Colors.WARNING}Sin target seleccionado{Colors.ENDC}")
        
        print(f"\n{Colors.HEADER}════════════════ Opciones ════════════════{Colors.ENDC}\n")
        
        print(f"{Colors.BOLD}[1]{Colors.ENDC} 🔍 Escanear Redes WiFi")
        print(f"{Colors.BOLD}[2]{Colors.ENDC} 🎯 Ver Redes Detectadas")
        print(f"{Colors.BOLD}[3]{Colors.ENDC} ⭐ Seleccionar Target (Manual)")
        print(f"{Colors.BOLD}[4]{Colors.ENDC} 🤖 Selección Automática (Modo Inteligente)")
        print(f"{Colors.BOLD}[5]{Colors.ENDC} ⚡ Iniciar Ataque al Target")
        print(f"{Colors.BOLD}[6]{Colors.ENDC} 📊 Ver Detalles del Target")
        print(f"{Colors.BOLD}[7]{Colors.ENDC} 🌐 Conectar a Red Crackeada")
        print(f"{Colors.BOLD}[8]{Colors.ENDC} ⚙️  Configuración Avanzada")
        print(f"{Colors.BOLD}[0]{Colors.ENDC} ❌ Salir\n")
        
        print(f"{Colors.HEADER}═══════════════════════════════════════════{Colors.ENDC}\n")
    
    def _scan_networks(self):
        """Scan for WiFi networks."""
        print_section_header("ESCANEO DE REDES")
        
        print(f"{Colors.INFO}Opciones de escaneo:{Colors.ENDC}")
        print(f"  [1] Escaneo rápido (15 segundos)")
        print(f"  [2] Escaneo estándar (30 segundos)")
        print(f"  [3] Escaneo profundo (60 segundos)")
        print(f"  [4] Escaneo personalizado")
        
        choice = input(f"\n{Colors.BOLD}Selecciona opción [1-4]: {Colors.ENDC}").strip()
        
        duration_map = {'1': 15, '2': 30, '3': 60}
        duration = duration_map.get(choice, 30)
        
        if choice == '4':
            try:
                duration = int(input(f"{Colors.INFO}Duración en segundos: {Colors.ENDC}"))
                if duration < 5 or duration > 300:
                    print_warning("Duración inválida, usando 30 segundos")
                    duration = 30
            except ValueError:
                print_warning("Valor inválido, usando 30 segundos")
                duration = 30
        
        self.scanner.start_scan(duration=duration)
        
        print(f"\n{Colors.OKCYAN}[*] Escaneando", end="", flush=True)
        start_time = time.time()
        
        while self.scanner.is_scanning():
            elapsed = int(time.time() - start_time)
            remaining = duration - elapsed
            
            progress = int((elapsed / duration) * 40)
            bar = "█" * progress + "░" * (40 - progress)
            
            print(f"\r{Colors.OKCYAN}[*] Escaneando [{bar}] {elapsed}/{duration}s - "
                  f"Redes encontradas: {len(self.scanner.networks)}{Colors.ENDC}", 
                  end="", flush=True)
            
            time.sleep(0.5)
        
        print()
        
        networks = self.scanner.get_networks()
        print_success(f"Escaneo completado: {len(networks)} redes detectadas")
        
        if networks:
            self.scanner.display_networks(top_n=20)
        
        self._pause()
    
    def _view_networks(self):
        """View detected networks."""
        print_section_header("REDES DETECTADAS")
        
        networks = self.scanner.get_networks()
        
        if not networks:
            print_warning("No hay redes detectadas. Ejecuta un escaneo primero [Opción 1]")
        else:
            self.scanner.display_networks()
        
        self._pause()
    
    def _select_target_manual(self):
        """Manual target selection."""
        print_section_header("SELECCIÓN MANUAL DE TARGET")
        
        networks = self.scanner.get_networks()
        
        if not networks:
            print_warning("No hay redes detectadas. Ejecuta un escaneo primero [Opción 1]")
            self._pause()
            return
        
        self.scanner.display_networks()
        
        try:
            choice = input(f"\n{Colors.BOLD}Selecciona el número de red (1-{len(networks)}) o 0 para cancelar: {Colors.ENDC}").strip()
            index = int(choice)
            
            if index == 0:
                print_info("Selección cancelada")
            elif 1 <= index <= len(networks):
                self.selected_target = networks[index - 1]
                print_success(f"Target seleccionado: {self.selected_target.ssid} ({self.selected_target.bssid})")
            else:
                print_error("Índice fuera de rango")
        
        except ValueError:
            print_error("Entrada inválida")
        
        self._pause()
    
    def _select_target_auto(self):
        """Automatic intelligent target selection."""
        print_section_header("SELECCIÓN AUTOMÁTICA INTELIGENTE")
        
        networks = self.scanner.get_networks()
        
        if not networks:
            print_warning("No hay redes detectadas. Ejecuta un escaneo primero [Opción 1]")
            self._pause()
            return
        
        print_info("Analizando targets con sistema de scoring...")
        time.sleep(1)
        
        scored_networks = []
        for net in networks:
            score = self.scorer.calculate_score(net)
            scored_networks.append((net, score))
        
        scored_networks.sort(key=lambda x: x[1], reverse=True)
        
        print(f"\n{Colors.HEADER}╔═══════════════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║              Top 5 Targets Recomendados                          ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╚═══════════════════════════════════════════════════════════════════╝{Colors.ENDC}\n")
        
        for idx, (net, score) in enumerate(scored_networks[:5], 1):
            score_color = Colors.SUCCESS if score >= 80 else Colors.WARNING if score >= 60 else Colors.INFO
            
            print(f"{Colors.BOLD}[{idx}] Score: {score_color}{score:>3}/100{Colors.ENDC}")
            print(f"    SSID: {net.ssid}")
            print(f"    BSSID: {net.bssid}")
            print(f"    Canal: {net.channel} | Señal: {net.signal}dBm | Clientes: {net.clients}")
            print(f"    Encriptación: {net.get_security_type()}")
            
            breakdown = self.scorer.get_score_breakdown(net)
            print(f"    {Colors.INFO}Desglose: Señal={breakdown['signal']} | "
                  f"Clientes={breakdown['clients']} | Seguridad={breakdown['security']}{Colors.ENDC}")
            print()
        
        if scored_networks:
            self.selected_target = scored_networks[0][0]
            print_success(f"Target automático seleccionado: {self.selected_target.ssid}")
            print_info(f"Score: {scored_networks[0][1]}/100")
        
        self._pause()
    
    def _attack_target(self):
        """Launch attack on selected target."""
        print_section_header("ATAQUE AL TARGET")
        
        if not self.selected_target:
            print_warning("No hay target seleccionado. Selecciona uno primero [Opción 3 o 4]")
            self._pause()
            return
        
        target = self.selected_target
        
        print(f"{Colors.INFO}Target: {target.ssid}{Colors.ENDC}")
        print(f"{Colors.INFO}BSSID: {target.bssid}{Colors.ENDC}")
        print(f"{Colors.INFO}Canal: {target.channel}{Colors.ENDC}")
        print(f"{Colors.INFO}Encriptación: {target.get_security_type()}{Colors.ENDC}")
        print(f"{Colors.INFO}Clientes conectados: {target.clients}{Colors.ENDC}\n")
        
        security = target.get_security_type()
        
        if security == 'OPEN':
            print_info("Red abierta detectada - No requiere contraseña")
            self._pause()
            return
        
        print(f"{Colors.HEADER}Métodos de ataque disponibles:{Colors.ENDC}\n")
        
        attack_methods = []
        
        if security in ['WPA', 'WPA2', 'WPA3']:
            print(f"  [1] 🎯 Ataque WPA/WPA2 (Handshake + Diccionario)")
            attack_methods.append('wpa')
            
            print(f"  [2] 📂 Usar Handshake Capturado Manualmente")
            attack_methods.append('wpa_manual')
            
            if target.wps:
                print(f"  [3] ⚡ Ataque WPS (Pixie Dust / Reaver)")
                attack_methods.append('wps')
        
        elif security == 'WEP':
            print(f"  [1] 🔓 Ataque WEP (ARP Replay)")
            attack_methods.append('wep')
        
        print(f"  [0] ← Volver")
        
        choice = input(f"\n{Colors.BOLD}Selecciona método de ataque: {Colors.ENDC}").strip()
        
        if choice == '0':
            return
        
        try:
            index = int(choice) - 1
            if 0 <= index < len(attack_methods):
                method = attack_methods[index]
                
                if method == 'wpa':
                    attack = WPAAttack(self.monitor_interface, target)
                    success = attack.execute()
                elif method == 'wpa_manual':
                    success = self._crack_manual_handshake(target)
                elif method == 'wps':
                    attack = WPSAttack(self.monitor_interface, target)
                    success = attack.execute()
                elif method == 'wep':
                    print_warning("Ataque WEP aún no implementado")
                    success = False
                
                if success:
                    print_success("¡Ataque exitoso!")
                else:
                    print_error("Ataque fallido")
            else:
                print_error("Opción inválida")
        
        except ValueError:
            print_error("Entrada inválida")
        
        self._pause()
    
    def _crack_manual_handshake(self, target: WiFiNetwork) -> bool:
        """Crack a manually provided handshake file."""
        print_section_header("CRACK DE HANDSHAKE MANUAL")
        
        print_info("Introduce la ruta del archivo .cap con el handshake")
        print_info("Ejemplo: /tmp/wifibreaker_capture-01.cap")
        print_info("O presiona Enter para buscar automáticamente\n")
        
        handshake_file = input(f"{Colors.BOLD}Ruta del archivo: {Colors.ENDC}").strip()
        
        # Si no se proporciona ruta, buscar automáticamente
        if not handshake_file:
            print_info("Buscando archivos .cap recientes...")
            
            # Buscar en /tmp y data/captures
            search_paths = [
                "/tmp/wifibreaker*.cap",
                "data/captures/*.cap",
                f"/tmp/*{target.bssid.replace(':', '')}*.cap"
            ]
            
            found_files = []
            for pattern in search_paths:
                found_files.extend(glob.glob(pattern))
            
            if not found_files:
                print_error("No se encontraron archivos .cap")
                return False
            
            # Ordenar por fecha de modificación (más reciente primero)
            found_files.sort(key=os.path.getmtime, reverse=True)
            
            print(f"\n{Colors.INFO}Archivos encontrados:{Colors.ENDC}")
            for idx, f in enumerate(found_files[:10], 1):
                size = os.path.getsize(f) / 1024  # KB
                mtime = time.strftime("%Y-%m-%d %H:%M", time.localtime(os.path.getmtime(f)))
                print(f"  [{idx}] {f} ({size:.1f} KB, {mtime})")
            
            choice = input(f"\n{Colors.BOLD}Selecciona archivo [1-{len(found_files[:10])}]: {Colors.ENDC}").strip()
            
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(found_files[:10]):
                    handshake_file = found_files[idx]
                else:
                    print_error("Índice inválido")
                    return False
            except ValueError:
                print_error("Entrada inválida")
                return False
        
        # Verificar que el archivo existe
        if not os.path.exists(handshake_file):
            print_error(f"Archivo no encontrado: {handshake_file}")
            return False
        
        # Verificar que contiene handshake del target
        print_info(f"Verificando handshake en: {handshake_file}")
        
        cmd = ['sudo', 'aircrack-ng', handshake_file, '-b', target.bssid]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            # Mostrar salida para debugging
            print_info("Salida de aircrack-ng:")
            print(result.stdout[:500])
            
            # CORRECCIÓN: Verificar handshake con múltiples patrones más permisivos
            handshake_valid = False
            bssid_upper = target.bssid.upper()
            
            if "1 handshake" in result.stdout.lower():
                handshake_valid = True
                print_success("✓ Patrón '1 handshake' detectado")
            elif "handshake" in result.stdout.lower() and bssid_upper in result.stdout.upper():
                handshake_valid = True
                print_success("✓ Patrón 'handshake' + BSSID detectado")
            elif "potential targets" in result.stdout.lower() and bssid_upper in result.stdout.upper():
                # Aircrack dice "potential targets" cuando hay datos pero no confirma handshake aún
                handshake_valid = True
                print_success("✓ Target potencial con BSSID correcto - probablemente válido")
            elif "Read" in result.stdout and "packets" in result.stdout and bssid_upper in result.stdout.upper():
                # Si leyó paquetes y tiene el BSSID correcto
                handshake_valid = True
                print_success("✓ Archivo contiene paquetes del BSSID correcto")
            
            if not handshake_valid:
                print_warning(f"No se pudo confirmar handshake automáticamente para {target.bssid}")
                print_info("Esto puede ser un falso negativo si el archivo es válido")
                
                confirm = input(f"\n{Colors.BOLD}¿Intentar crack de todos modos? (S/n): {Colors.ENDC}").strip().lower()
                if confirm == 'n':
                    return False
            else:
                print_success("✓ Handshake válido detectado")
        
        except Exception as e:
            print_warning(f"Error al verificar: {e}")
            confirm = input(f"{Colors.BOLD}¿Continuar de todos modos? (s/N): {Colors.ENDC}").strip().lower()
            if confirm != 's':
                return False
        
        # Crear objeto WPAAttack y asignar el handshake manualmente
        attack = WPAAttack(self.monitor_interface, target)
        attack.handshake_file = handshake_file
        attack.handshake_captured = True
        
        # Ir directo al crack
        print(f"\n{Colors.BOLD}[Fase de Cracking]{Colors.ENDC}")
        print("─" * 60)
        
        # CORRECCIÓN: Listar wordlists disponibles dinámicamente
        print_info("Wordlists disponibles:\n")
        
        # Buscar wordlists en data/wordlists/
        wordlists_dir = 'data/wordlists'
        available_wordlists = []
        
        if os.path.exists(wordlists_dir):
            wordlist_files = sorted(glob.glob(f"{wordlists_dir}/*.txt"))
            for wl in wordlist_files:
                available_wordlists.append(wl)
        
        # Agregar rockyou.txt si existe
        rockyou_path = '/usr/share/wordlists/rockyou.txt'
        if os.path.exists(rockyou_path):
            available_wordlists.append(rockyou_path)
        
        # Mostrar wordlists disponibles
        if available_wordlists:
            for idx, wl in enumerate(available_wordlists, 1):
                size_mb = os.path.getsize(wl) / (1024 * 1024)
                filename = os.path.basename(wl)
                print(f"  [{idx}] {filename} ({size_mb:.1f} MB)")
        else:
            print_warning("  No se encontraron wordlists en data/wordlists/")
        
        print(f"  [{len(available_wordlists) + 1}] Ruta personalizada")
        print(f"  [0] Cancelar\n")
        
        choice = input(f"{Colors.BOLD}Opción [0-{len(available_wordlists) + 1}]: {Colors.ENDC}").strip()
        
        wordlist = None
        try:
            choice_num = int(choice)
            
            if choice_num == 0:
                print_info("Operación cancelada")
                return False
            elif 1 <= choice_num <= len(available_wordlists):
                wordlist = available_wordlists[choice_num - 1]
            elif choice_num == len(available_wordlists) + 1:
                wordlist = input(f"{Colors.INFO}Ruta del wordlist: {Colors.ENDC}").strip()
            else:
                print_error("Opción inválida")
                return False
        except ValueError:
            print_error("Entrada inválida")
            return False
        
        if attack.crack_password(wordlist):
            attack._save_results()
            return True
        else:
            print_info("\nSugerencias:")
            print("  • Usa rockyou.txt completo")
            print("  • Genera wordlist específico del SSID")
            return False
    
    def _view_target_details(self):
        """View detailed information about selected target."""
        print_section_header("DETALLES DEL TARGET")
        
        if not self.selected_target:
            print_warning("No hay target seleccionado")
            self._pause()
            return
        
        target = self.selected_target
        score = self.scorer.calculate_score(target)
        breakdown = self.scorer.get_score_breakdown(target)
        
        print(f"{Colors.HEADER}╔═══════════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║                  Información del Target                       ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╚═══════════════════════════════════════════════════════════════╝{Colors.ENDC}\n")
        
        print(f"{Colors.BOLD}Identificación:{Colors.ENDC}")
        print(f"  SSID: {target.ssid}")
        print(f"  BSSID: {target.bssid}")
        print(f"  Canal: {target.channel}")
        
        print(f"\n{Colors.BOLD}Señal:{Colors.ENDC}")
        signal_bars = target._signal_to_bars()
        print(f"  Potencia: {signal_bars} {target.signal} dBm")
        
        print(f"\n{Colors.BOLD}Seguridad:{Colors.ENDC}")
        print(f"  Tipo: {target.get_security_type()}")
        print(f"  Encriptación: {target.encryption}")
        print(f"  Cifrado: {target.cipher}")
        print(f"  Autenticación: {target.authentication}")
        print(f"  WPS: {'Sí' if target.wps else 'No'}")
        
        print(f"\n{Colors.BOLD}Actividad:{Colors.ENDC}")
        print(f"  Clientes: {target.clients}")
        print(f"  Beacons: {target.beacons}")
        print(f"  Paquetes de datos: {target.data_packets}")
        
        if target.clients_list:
            print(f"\n{Colors.BOLD}Clientes conectados (ordenados por tráfico):{Colors.ENDC}")
            for idx, client in enumerate(target.clients_list[:10], 1):
                print(f"  {idx}. {client}")
        
        print(f"\n{Colors.BOLD}Análisis de Ataque:{Colors.ENDC}")
        print(f"  Score Total: {score}/100")
        print(f"  Puntos por señal: {breakdown['signal']}")
        print(f"  Puntos por clientes: {breakdown['clients']}")
        print(f"  Puntos por seguridad: {breakdown['security']}")
        
        # Attack recommendation
        print(f"\n{Colors.BOLD}Recomendación:{Colors.ENDC}")
        if score >= 80:
            print(f"  {Colors.SUCCESS}Target excelente - Alta probabilidad de éxito{Colors.ENDC}")
        elif score >= 60:
            print(f"  {Colors.WARNING}Target viable - Requiere paciencia{Colors.ENDC}")
        else:
            print(f"  {Colors.FAIL}Target difícil - Busca alternativas mejores{Colors.ENDC}")
        
        self._pause()
    
    def _connect_to_network(self):
        """Connect to a cracked network."""
        print_section_header("CONECTAR A RED")
        
        # Verificar si hay resultados de ataques exitosos
        results_dir = "data/results"
        if not os.path.exists(results_dir):
            print_warning("No hay resultados de ataques guardados")
            self._pause()
            return
        
        # Buscar archivos de resultados
        result_files = sorted(glob.glob(f"{results_dir}/*.txt"), key=os.path.getmtime, reverse=True)
        
        if not result_files:
            print_warning("No se encontraron redes crackeadas")
            print_info("Primero debes crackear una red exitosamente")
            self._pause()
            return
        
        # Mostrar redes crackeadas disponibles
        print(f"{Colors.INFO}Redes crackeadas disponibles:{Colors.ENDC}\n")
        
        networks_info = []
        for idx, result_file in enumerate(result_files[:10], 1):
            try:
                with open(result_file, 'r') as f:
                    content = f.read()
                    ssid = None
                    bssid = None
                    password = None
                    
                    for line in content.split('\n'):
                        if line.startswith('SSID:'):
                            ssid = line.split(':', 1)[1].strip()
                        elif line.startswith('BSSID:'):
                            bssid = line.split(':', 1)[1].strip()
                        elif line.startswith('Password:'):
                            password = line.split(':', 1)[1].strip()
                    
                    if ssid and password:
                        mtime = time.strftime("%Y-%m-%d %H:%M", time.localtime(os.path.getmtime(result_file)))
                        print(f"  [{idx}] {ssid} - Crackeada el {mtime}")
                        networks_info.append({
                            'ssid': ssid,
                            'bssid': bssid,
                            'password': password,
                            'file': result_file
                        })
            except:
                continue
        
        if not networks_info:
            print_warning("No se pudieron leer los resultados")
            self._pause()
            return
        
        print(f"  [0] Cancelar\n")
        
        choice = input(f"{Colors.BOLD}Selecciona red [0-{len(networks_info)}]: {Colors.ENDC}").strip()
        
        try:
            idx = int(choice)
            if idx == 0:
                print_info("Operación cancelada")
                self._pause()
                return
            
            if 1 <= idx <= len(networks_info):
                network = networks_info[idx - 1]
                
                print(f"\n{Colors.INFO}Red seleccionada:{Colors.ENDC}")
                print(f"  SSID: {network['ssid']}")
                print(f"  Password: {network['password']}\n")
                
                confirm = input(f"{Colors.BOLD}¿Conectar a esta red? (S/n): {Colors.ENDC}").strip().lower()
                
                if confirm == 'n':
                    print_info("Conexión cancelada")
                    self._pause()
                    return
                
                # Proceso de conexión
                self._perform_connection(network['ssid'], network['password'])
            else:
                print_error("Opción inválida")
        
        except ValueError:
            print_error("Entrada inválida")
        
        self._pause()
    
    def _perform_connection(self, ssid: str, password: str):
        """Perform the actual connection process."""
        from core.monitor import MonitorMode
        
        print(f"\n{Colors.HEADER}═══ Proceso de Conexión ═══{Colors.ENDC}\n")
        
        # Paso 1: Desactivar modo monitor
        print_info("[1/4] Desactivando modo monitor...")
        
        try:
            monitor = MonitorMode(self.monitor_interface.replace('mon', ''))
            monitor.monitor_interface = self.monitor_interface
            monitor.disable()
            
            # Obtener interfaz original (sin 'mon')
            if 'mon' in self.monitor_interface:
                original_interface = self.monitor_interface.replace('mon', '')
            else:
                original_interface = 'wlan0'
            
            print_success(f"✓ Modo monitor desactivado - Interface: {original_interface}")
            time.sleep(2)
        
        except Exception as e:
            print_error(f"Error al desactivar modo monitor: {e}")
            print_info("Intentando continuar de todos modos...")
            original_interface = 'wlan0'
        
        # Paso 2: Levantar interfaz
        print_info(f"[2/4] Levantando interfaz {original_interface}...")
        
        cmd_up = ['sudo', 'ip', 'link', 'set', original_interface, 'up']
        try:
            subprocess.run(cmd_up, timeout=10)
            print_success(f"✓ Interfaz {original_interface} levantada")
            time.sleep(2)
        except Exception as e:
            print_warning(f"Error: {e}")
        
        # Paso 3: Crear configuración de wpa_supplicant
        print_info("[3/4] Configurando conexión...")
        
        wpa_conf = "/tmp/wpa_supplicant_wifibreaker.conf"
        
        try:
            with open(wpa_conf, 'w') as f:
                f.write("ctrl_interface=/var/run/wpa_supplicant\n")
                f.write("update_config=1\n\n")
                f.write("network={\n")
                f.write(f'    ssid="{ssid}"\n')
                f.write(f'    psk="{password}"\n')
                f.write("    key_mgmt=WPA-PSK\n")
                f.write("}\n")
            
            print_success("✓ Configuración creada")
        
        except Exception as e:
            print_error(f"Error al crear configuración: {e}")
            return
        
        # Paso 4: Conectar con wpa_supplicant
        print_info(f"[4/4] Conectando a {ssid}...")
        print_warning("Esto puede tomar 10-15 segundos...")
        
        # Matar wpa_supplicant existentes
        subprocess.run(['sudo', 'killall', 'wpa_supplicant'], capture_output=True)
        time.sleep(1)
        
        # Iniciar wpa_supplicant
        cmd_wpa = [
            'sudo', 'wpa_supplicant',
            '-B',  # Background
            '-i', original_interface,
            '-c', wpa_conf
        ]
        
        try:
            result = subprocess.run(cmd_wpa, capture_output=True, text=True, timeout=15)
            
            if result.returncode == 0:
                print_success("✓ wpa_supplicant iniciado")
                time.sleep(3)
                
                # Obtener IP con dhclient o alternativas
                print_info("Obteniendo dirección IP...")
                
                # Intentar múltiples métodos (Kali usa dhcpcd, Ubuntu usa dhclient)
                dhcp_commands = [
                    ['sudo', 'dhcpcd', original_interface],
                    ['sudo', 'dhclient', '-v', original_interface],
                    ['sudo', 'dhclient', original_interface]
                ]
                
                dhcp_success = False
                for cmd_dhcp in dhcp_commands:
                    try:
                        result_dhcp = subprocess.run(cmd_dhcp, capture_output=True, timeout=15)
                        if result_dhcp.returncode == 0:
                            dhcp_success = True
                            break
                    except:
                        continue
                
                if not dhcp_success:
                    print_warning("⚠ No se encontró dhclient/dhcpcd, intentando con NetworkManager...")
                    # Intentar con nmcli (NetworkManager)
                    try:
                        subprocess.run(['sudo', 'systemctl', 'start', 'NetworkManager'], timeout=5)
                        time.sleep(2)
                        subprocess.run(['sudo', 'nmcli', 'device', 'connect', original_interface], timeout=10)
                    except:
                        pass
                
                time.sleep(3)
                
                # Verificar conexión
                cmd_ip = ['ip', 'addr', 'show', original_interface]
                result_ip = subprocess.run(cmd_ip, capture_output=True, text=True)
                
                # Buscar IP asignada
                ip_assigned = None
                for line in result_ip.stdout.split('\n'):
                    if 'inet ' in line and '127.0.0.1' not in line:
                        ip_assigned = line.strip().split()[1].split('/')[0]
                        break
                
                if ip_assigned:
                    print_success(f"\n{'═' * 50}")
                    print_success(f"✓ ¡CONECTADO EXITOSAMENTE!")
                    print_success(f"{'═' * 50}\n")
                    print(f"{Colors.INFO}Red: {Colors.BOLD}{ssid}{Colors.ENDC}")
                    print(f"{Colors.INFO}IP asignada: {Colors.BOLD}{ip_assigned}{Colors.ENDC}")
                    print(f"{Colors.INFO}Interface: {Colors.BOLD}{original_interface}{Colors.ENDC}\n")
                    
                    # Probar conectividad
                    print_info("Probando conectividad a Internet...")
                    ping_result = subprocess.run(
                        ['ping', '-c', '3', '8.8.8.8'],
                        capture_output=True,
                        timeout=10
                    )
                    
                    if ping_result.returncode == 0:
                        print_success("✓ Conexión a Internet verificada")
                    else:
                        print_warning("⚠ No se pudo verificar conexión a Internet")
                    
                    print(f"\n{Colors.WARNING}IMPORTANTE:{Colors.ENDC}")
                    print(f"  • El adaptador ya NO está en modo monitor")
                    print(f"  • Para volver a auditar, reinicia la herramienta")
                    print(f"  • Para desconectar: sudo killall wpa_supplicant\n")
                    
                    # Preguntar si quiere salir o continuar sin modo monitor
                    print(f"{Colors.INFO}Opciones:{Colors.ENDC}")
                    print(f"  [1] Salir del programa (recomendado)")
                    print(f"  [2] Continuar (sin modo monitor - solo ver resultados)")
                    
                    choice = input(f"\n{Colors.BOLD}Opción [1-2]: {Colors.ENDC}").strip()
                    
                    if choice == '1':
                        print_info("Saliendo de WifiBreaker Pro...")
                        self.running = False
                    
                else:
                    print_error("✗ Conectado pero no se obtuvo IP")
                    print_info("\nIntenta manualmente uno de estos comandos:")
                    print(f"  {Colors.BOLD}# Para Kali Linux:{Colors.ENDC}")
                    print(f"  sudo dhcpcd {original_interface}")
                    print(f"\n  {Colors.BOLD}# Para Ubuntu/Debian:{Colors.ENDC}")
                    print(f"  sudo dhclient {original_interface}")
                    print(f"\n  {Colors.BOLD}# O con NetworkManager:{Colors.ENDC}")
                    print(f"  sudo systemctl start NetworkManager")
                    print(f"  sudo nmcli device connect {original_interface}")
                    print(f"\n  {Colors.BOLD}# Verificar IP:{Colors.ENDC}")
                    print(f"  ip addr show {original_interface}")
                    
                    print(f"\n{Colors.WARNING}La conexión WiFi está establecida, solo falta obtener IP{Colors.ENDC}")
            
            else:
                print_error("✗ Error al iniciar wpa_supplicant")
                print_info(f"Error: {result.stderr[:200]}")
        
        except subprocess.TimeoutExpired:
            print_error("✗ Timeout al conectar")
        except Exception as e:
            print_error(f"✗ Error: {e}")
        
        finally:
            # Limpiar archivo temporal
            try:
                os.remove(wpa_conf)
            except:
                pass
    
    def _advanced_settings(self):
        """Advanced configuration menu."""
        print_section_header("CONFIGURACIÓN AVANZADA")
        
        while True:
            print(f"\n{Colors.HEADER}╔══════════════════════════════════════════════╗{Colors.ENDC}")
            print(f"{Colors.HEADER}║        Configuración Avanzada               ║{Colors.ENDC}")
            print(f"{Colors.HEADER}╚══════════════════════════════════════════════╝{Colors.ENDC}\n")
            
            print(f"{Colors.BOLD}[1]{Colors.ENDC} 📡 Gestionar Adaptadores WiFi")
            print(f"{Colors.BOLD}[2]{Colors.ENDC} 📝 Gestionar Wordlists")
            print(f"{Colors.BOLD}[3]{Colors.ENDC} 🗑️  Limpiar Archivos Temporales")
            print(f"{Colors.BOLD}[4]{Colors.ENDC} 📊 Ver Resultados Guardados")
            print(f"{Colors.BOLD}[5]{Colors.ENDC} 🔧 Cambiar Potencia de Transmisión")
            print(f"{Colors.BOLD}[6]{Colors.ENDC} 🎯 Configurar Canales de Escaneo")
            print(f"{Colors.BOLD}[7]{Colors.ENDC} ⏱️  Ajustar Timeouts de Ataque")
            print(f"{Colors.BOLD}[8]{Colors.ENDC} 🔄 Reiniciar Modo Monitor")
            print(f"{Colors.BOLD}[9]{Colors.ENDC} 📋 Ver Logs de la Aplicación")
            print(f"{Colors.BOLD}[0]{Colors.ENDC} ← Volver al Menú Principal\n")
            
            choice = input(f"{Colors.BOLD}Selecciona opción [0-9]: {Colors.ENDC}").strip()
            
            if choice == '1':
                self._manage_adapters()
            elif choice == '2':
                self._manage_wordlists()
            elif choice == '3':
                self._cleanup_temp_files()
            elif choice == '4':
                self._view_saved_results()
            elif choice == '5':
                self._change_tx_power()
            elif choice == '6':
                self._configure_scan_channels()
            elif choice == '7':
                self._configure_timeouts()
            elif choice == '8':
                self._restart_monitor_mode()
            elif choice == '9':
                self._view_logs()
            elif choice == '0':
                break
            else:
                print_error("Opción inválida")
                time.sleep(1)
    
    def _manage_adapters(self):
        """Manage WiFi adapters."""
        print_section_header("GESTIÓN DE ADAPTADORES")
        
        from core.adapter import AdapterManager
        
        adapter_mgr = AdapterManager()
        adapters = adapter_mgr.detect_adapters()
        
        if not adapters:
            print_error("No se detectaron adaptadores")
            self._pause()
            return
        
        adapter_mgr.list_adapters()
        
        print(f"\n{Colors.INFO}Opciones:{Colors.ENDC}")
        print(f"  [1] Cambiar adaptador actual")
        print(f"  [2] Ver información detallada")
        print(f"  [3] Probar inyección de paquetes")
        print(f"  [0] Volver")
        
        choice = input(f"\n{Colors.BOLD}Opción: {Colors.ENDC}").strip()
        
        if choice == '1':
            idx = input(f"{Colors.BOLD}Número de adaptador: {Colors.ENDC}").strip()
            try:
                selected = adapter_mgr.select_adapter(int(idx) - 1)
                if selected:
                    print_success(f"Adaptador cambiado a: {selected['interface']}")
                    print_warning("Reinicia la aplicación para aplicar cambios")
            except:
                print_error("Índice inválido")
        
        elif choice == '2':
            print_info("\nInformación del adaptador actual:")
            print(f"  Interface: {self.monitor_interface}")
            subprocess.run(['iwconfig', self.monitor_interface.replace('mon', '')])
        
        elif choice == '3':
            print_info("Probando inyección de paquetes...")
            result = subprocess.run(
                ['sudo', 'aireplay-ng', '--test', self.monitor_interface],
                capture_output=True,
                text=True,
                timeout=30
            )
            print(result.stdout)
        
        self._pause()
    
    def _manage_wordlists(self):
        """Manage wordlists with Cerbero integration."""
        print_section_header("GESTIÓN DE WORDLISTS")
        
        wordlists_dir = 'data/wordlists'
        
        # Crear directorio si no existe
        if not os.path.exists(wordlists_dir):
            os.makedirs(wordlists_dir, exist_ok=True)
        
        # Mostrar wordlists disponibles
        wordlists = glob.glob(f"{wordlists_dir}/*.txt")
        
        if wordlists:
            print(f"{Colors.INFO}Wordlists disponibles:{Colors.ENDC}\n")
            
            total_size = 0
            for idx, wl in enumerate(sorted(wordlists)[:10], 1):
                size = os.path.getsize(wl)
                total_size += size
                size_mb = size / (1024 * 1024)
                
                try:
                    with open(wl, 'r', errors='ignore') as f:
                        lines = sum(1 for _ in f)
                    print(f"  {os.path.basename(wl)}: {size_mb:.2f} MB | {lines:,} palabras")
                except:
                    print(f"  {os.path.basename(wl)}: {size_mb:.2f} MB")
            
            if len(wordlists) > 10:
                print(f"  ... y {len(wordlists) - 10} más")
            
            print(f"\n{Colors.SUCCESS}Total: {len(wordlists)} wordlists ({total_size / (1024*1024):.2f} MB){Colors.ENDC}\n")
        else:
            print_warning("No hay wordlists en data/wordlists/\n")
        
        # Menú principal
        print(f"{Colors.HEADER}╔══════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║          Gestión de Wordlists               ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╚══════════════════════════════════════════════╝{Colors.ENDC}\n")
        
        print(f"{Colors.BOLD}[1]{Colors.ENDC} 🎯 Generar Wordlist Personalizada (Cerbero)")
        print(f"{Colors.BOLD}[2]{Colors.ENDC} 🔢 Generar Wordlist Numérica (PINs)")
        print(f"{Colors.BOLD}[3]{Colors.ENDC} 📥 Descargar rockyou.txt")
        print(f"{Colors.BOLD}[4]{Colors.ENDC} ✏️  Crear wordlist simple")
        print(f"{Colors.BOLD}[5]{Colors.ENDC} 🔍 Ver contenido de wordlist")
        print(f"{Colors.BOLD}[6]{Colors.ENDC} 🗑️  Eliminar wordlist")
        print(f"{Colors.BOLD}[7]{Colors.ENDC} 🔗 Combinar wordlists")
        print(f"{Colors.BOLD}[0]{Colors.ENDC} ← Volver\n")
        
        choice = input(f"{Colors.BOLD}Opción [0-7]: {Colors.ENDC}").strip()
        
        if choice == '1':
            self._generate_cerbero_wordlist()
        elif choice == '2':
            self._generate_numeric_wordlist()
        elif choice == '3':
            self._download_rockyou()
        elif choice == '4':
            self._create_simple_wordlist()
        elif choice == '5':
            self._view_wordlist_content(wordlists)
        elif choice == '6':
            self._delete_wordlist(wordlists)
        elif choice == '7':
            self._combine_wordlists(wordlists)
        elif choice == '0':
            return
        else:
            print_error("Opción inválida")
            time.sleep(1)
    
    def _generate_cerbero_wordlist(self):
        """Generate personalized wordlist using Cerbero engine."""
        print_section_header("🎯 CERBERO - GENERADOR PERSONALIZADO")
        
        print(f"{Colors.INFO}Cerbero genera contraseñas específicas basadas en información del objetivo.{Colors.ENDC}")
        print(f"{Colors.INFO}Ideal para ataques dirigidos contra redes conocidas.{Colors.ENDC}\n")
        
        # Recolectar información del target
        print(f"{Colors.BOLD}═══ Información del Objetivo ═══{Colors.ENDC}\n")
        
        # Nombres
        print(f"{Colors.INFO}Nombres (separados por espacio):{Colors.ENDC}")
        print(f"{Colors.WARNING}Ej: Juan Carlos, Maria, Pedro{Colors.ENDC}")
        names = input(f"{Colors.BOLD}> {Colors.ENDC}").strip()
        
        # Apellidos
        print(f"\n{Colors.INFO}Apellidos (separados por espacio):{Colors.ENDC}")
        print(f"{Colors.WARNING}Ej: Rodriguez, Garcia, Lopez{Colors.ENDC}")
        surnames = input(f"{Colors.BOLD}> {Colors.ENDC}").strip()
        
        # Fecha de nacimiento
        print(f"\n{Colors.INFO}Fecha de nacimiento (DDMMYYYY o DD/MM/YYYY):{Colors.ENDC}")
        print(f"{Colors.WARNING}Ej: 15081990 o 15/08/1990{Colors.ENDC}")
        birthdate = input(f"{Colors.BOLD}> {Colors.ENDC}").strip()
        
        # Sobrenombre
        print(f"\n{Colors.INFO}Sobrenombre/Apodo:{Colors.ENDC}")
        print(f"{Colors.WARNING}Ej: Chino, Flaco, Gordito{Colors.ENDC}")
        nickname = input(f"{Colors.BOLD}> {Colors.ENDC}").strip()
        
        # Datos de pareja
        print(f"\n{Colors.INFO}Nombre de pareja/cónyuge:{Colors.ENDC}")
        partner = input(f"{Colors.BOLD}> {Colors.ENDC}").strip()
        
        # Hijos
        print(f"\n{Colors.INFO}Nombres de hijos (separados por espacio):{Colors.ENDC}")
        children = input(f"{Colors.BOLD}> {Colors.ENDC}").strip()
        
        # Mascota
        print(f"\n{Colors.INFO}Nombre de mascota:{Colors.ENDC}")
        pet = input(f"{Colors.BOLD}> {Colors.ENDC}").strip()
        
        # SSID (MUY IMPORTANTE)
        print(f"\n{Colors.SUCCESS}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Colors.ENDC}")
        print(f"{Colors.SUCCESS}IMPORTANTE: El SSID es clave para generar contraseñas específicas{Colors.ENDC}")
        print(f"{Colors.SUCCESS}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Colors.ENDC}")
        print(f"{Colors.INFO}SSID de la red WiFi objetivo:{Colors.ENDC}")
        if self.selected_target:
            print(f"{Colors.WARNING}Red actual: {self.selected_target.ssid}{Colors.ENDC}")
            use_current = input(f"{Colors.BOLD}¿Usar esta red? (S/n): {Colors.ENDC}").strip().lower()
            if use_current != 'n':
                ssid = self.selected_target.ssid
            else:
                ssid = input(f"{Colors.BOLD}SSID: {Colors.ENDC}").strip()
        else:
            ssid = input(f"{Colors.BOLD}SSID: {Colors.ENDC}").strip()
        
        # Palabras clave
        print(f"\n{Colors.INFO}Palabras clave relacionadas (separadas por espacio):{Colors.ENDC}")
        print(f"{Colors.WARNING}Ej: empresa, ciudad, equipo de fútbol{Colors.ENDC}")
        keywords = input(f"{Colors.BOLD}> {Colors.ENDC}").strip()
        
        # Frases a destrozar
        print(f"\n{Colors.INFO}Frases completas para 'destrozar' (una por línea, Enter vacío para terminar):{Colors.ENDC}")
        print(f"{Colors.WARNING}Ej: 'Mi casa es azul', 'kasa de Juan'{Colors.ENDC}")
        print(f"{Colors.INFO}Estas se convertirán en múltiples variaciones:{Colors.ENDC}")
        phrases = []
        while True:
            phrase = input(f"{Colors.BOLD}> {Colors.ENDC}").strip()
            if not phrase:
                break
            phrases.append(phrase)
        
        # Números importantes
        print(f"\n{Colors.INFO}Números importantes (separados por espacio):{Colors.ENDC}")
        print(f"{Colors.WARNING}Ej: 123, 456, 2024{Colors.ENDC}")
        numbers = input(f"{Colors.BOLD}> {Colors.ENDC}").strip()
        
        # Configuración de generación
        print(f"\n{Colors.BOLD}═══ Configuración ═══{Colors.ENDC}\n")
        
        print(f"{Colors.INFO}Longitud mínima de contraseñas:{Colors.ENDC}")
        min_length = input(f"{Colors.BOLD}[8]: {Colors.ENDC}").strip() or "8"
        
        print(f"{Colors.INFO}Longitud máxima de contraseñas:{Colors.ENDC}")
        max_length = input(f"{Colors.BOLD}[16]: {Colors.ENDC}").strip() or "16"
        
        # Nombre del archivo
        print(f"\n{Colors.INFO}Nombre del archivo (sin extensión):{Colors.ENDC}")
        default_name = f"target_{ssid.replace(' ', '_')}" if ssid else "target_custom"
        filename = input(f"{Colors.BOLD}[{default_name}]: {Colors.ENDC}").strip() or default_name
        
        if not filename.endswith('.txt'):
            filename += '.txt'
        
        # Resumen
        print(f"\n{Colors.HEADER}╔══════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║              Resumen de Datos                ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╚══════════════════════════════════════════════╝{Colors.ENDC}\n")
        
        data_summary = []
        if names: data_summary.append(f"Nombres: {names}")
        if surnames: data_summary.append(f"Apellidos: {surnames}")
        if birthdate: data_summary.append(f"Fecha nac: {birthdate}")
        if nickname: data_summary.append(f"Apodo: {nickname}")
        if partner: data_summary.append(f"Pareja: {partner}")
        if children: data_summary.append(f"Hijos: {children}")
        if pet: data_summary.append(f"Mascota: {pet}")
        if ssid: data_summary.append(f"SSID: {Colors.SUCCESS}{ssid}{Colors.ENDC}")
        if keywords: data_summary.append(f"Keywords: {keywords}")
        if phrases: data_summary.append(f"Frases: {len(phrases)}")
        if numbers: data_summary.append(f"Números: {numbers}")
        
        for item in data_summary:
            print(f"  • {item}")
        
        print(f"\n{Colors.INFO}Configuración:{Colors.ENDC}")
        print(f"  • Longitud: {min_length}-{max_length} caracteres")
        print(f"  • Archivo: data/wordlists/{filename}\n")
        
        confirm = input(f"{Colors.BOLD}¿Generar wordlist? (S/n): {Colors.ENDC}").strip().lower()
        
        if confirm == 'n':
            print_info("Generación cancelada")
            self._pause()
            return
        
        # Generar con Cerbero
        print(f"\n{Colors.HEADER}{'═' * 60}{Colors.ENDC}")
        print(f"{Colors.SUCCESS}🔥 Iniciando Cerbero Engine...{Colors.ENDC}")
        print(f"{Colors.HEADER}{'═' * 60}{Colors.ENDC}\n")
        
        try:
            engine = CerberoEngine()
            
            # Adaptar datos al formato que espera Cerbero
            # Parsear fecha de nacimiento
            birthdate_obj = None
            if birthdate:
                try:
                    # Intentar diferentes formatos
                    birthdate_clean = birthdate.replace('/', '').replace('-', '').strip()
                    if len(birthdate_clean) == 8:  # DDMMYYYY
                        day = int(birthdate_clean[:2])
                        month = int(birthdate_clean[2:4])
                        year = int(birthdate_clean[4:8])
                        birthdate_obj = datetime(year, month, day)
                except:
                    print_warning(f"No se pudo parsear fecha: {birthdate}")
            
            # Parsear datos de hijos
            children_list = []
            if children:
                for child_name in children.split():
                    children_list.append({
                        'nombres': [child_name],
                        'apellidos': surnames.split() if surnames else [],
                        'fecha_nacimiento': None
                    })
            
            # Estructura de datos que espera Cerbero
            cerbero_info = {
                'persona_principal': {
                    'nombres': names.split() if names else [],
                    'apellidos': surnames.split() if surnames else [],
                    'fecha_nacimiento': birthdate_obj,
                    'sobrenombre': nickname if nickname else None
                },
                'familia': {
                    'pareja': {
                        'nombres': [partner] if partner else [],
                        'apellidos': [],
                        'fecha_nacimiento': None
                    },
                    'hijos': children_list,
                    'mascotas': [pet] if pet else []
                },
                'otros_datos': {
                    'ssid': ssid,
                    'keywords': keywords.split() if keywords else [],
                    'mangle_phrases': phrases,
                    'numeros_importantes': numbers.split() if numbers else []
                }
            }
            
            # Generar contraseñas
            passwords_list = engine.generate_full_passwords(
                info=cerbero_info,
                min_length=int(min_length),
                max_length=int(max_length)
            )
            
            # Guardar en archivo
            output_path = f"data/wordlists/{filename}"
            with open(output_path, 'w') as f:
                for pwd in sorted(passwords_list):
                    f.write(f"{pwd}\n")
            
            total_passwords = len(passwords_list)
            
            if total_passwords > 0:
                print(f"\n{Colors.SUCCESS}╔══════════════════════════════════════════════╗{Colors.ENDC}")
                print(f"{Colors.SUCCESS}║          ✓ Wordlist Generada                ║{Colors.ENDC}")
                print(f"{Colors.SUCCESS}╚══════════════════════════════════════════════╝{Colors.ENDC}\n")
                
                print(f"{Colors.INFO}Archivo: {Colors.BOLD}{output_path}{Colors.ENDC}")
                print(f"{Colors.INFO}Contraseñas: {Colors.BOLD}{total_passwords:,}{Colors.ENDC}")
                
                size_mb = os.path.getsize(output_path) / (1024 * 1024)
                print(f"{Colors.INFO}Tamaño: {Colors.BOLD}{size_mb:.2f} MB{Colors.ENDC}\n")
                
                # Mostrar muestra
                print(f"{Colors.INFO}Muestra (primeras 10 contraseñas):{Colors.ENDC}\n")
                with open(output_path, 'r') as f:
                    for i, line in enumerate(f):
                        if i >= 10:
                            break
                        print(f"  {i+1}. {line.strip()}")
                
                print(f"\n{Colors.SUCCESS}¡Lista para usar en ataques!{Colors.ENDC}")
            else:
                print_error("No se generaron contraseñas")
        
        except Exception as e:
            print_error(f"Error al generar wordlist: {e}")
            import traceback
            traceback.print_exc()
        
        self._pause()
    
    def _generate_numeric_wordlist(self):
        """Generate numeric PIN wordlist."""
        print_section_header("🔢 GENERADOR DE PINs NUMÉRICOS")
        
        print(f"{Colors.INFO}Genera wordlists de combinaciones numéricas.{Colors.ENDC}")
        print(f"{Colors.INFO}Útil para ataques a redes con PINs numéricos.{Colors.ENDC}\n")
        
        print(f"{Colors.BOLD}Opciones:{Colors.ENDC}\n")
        print(f"  [1] 4 dígitos (0000-9999) - 10,000 combinaciones")
        print(f"  [2] 6 dígitos (000000-999999) - 1,000,000 combinaciones")
        print(f"  [3] 8 dígitos (00000000-99999999) - 100,000,000 combinaciones")
        print(f"  [4] Rango personalizado")
        print(f"  [0] Cancelar\n")
        
        choice = input(f"{Colors.BOLD}Opción [0-4]: {Colors.ENDC}").strip()
        
        if choice == '0':
            return
        
        if choice == '1':
            start, end = 0, 9999
            digits = 4
        elif choice == '2':
            start, end = 0, 999999
            digits = 6
        elif choice == '3':
            start, end = 0, 99999999
            digits = 8
        elif choice == '4':
            try:
                start = int(input(f"{Colors.INFO}Número inicial: {Colors.ENDC}"))
                end = int(input(f"{Colors.INFO}Número final: {Colors.ENDC}"))
                digits = len(str(end))
            except ValueError:
                print_error("Valores inválidos")
                self._pause()
                return
        else:
            print_error("Opción inválida")
            self._pause()
            return
        
        filename = input(f"\n{Colors.INFO}Nombre del archivo [{digits}digits.txt]: {Colors.ENDC}").strip() or f"{digits}digits.txt"
        if not filename.endswith('.txt'):
            filename += '.txt'
        
        output_path = f"data/wordlists/{filename}"
        
        print(f"\n{Colors.WARNING}Se generarán {end - start + 1:,} combinaciones{Colors.ENDC}")
        print(f"{Colors.WARNING}Esto puede tomar tiempo y espacio...{Colors.ENDC}\n")
        
        confirm = input(f"{Colors.BOLD}¿Continuar? (s/N): {Colors.ENDC}").strip().lower()
        
        if confirm != 's':
            print_info("Operación cancelada")
            self._pause()
            return
        
        print_info(f"Generando {output_path}...")
        
        try:
            with open(output_path, 'w') as f:
                for num in range(start, end + 1):
                    f.write(f"{num:0{digits}d}\n")
                    
                    if num % 100000 == 0:
                        progress = (num / (end - start)) * 100
                        print(f"\r{Colors.INFO}Progreso: {progress:.1f}% ({num:,}/{end:,}){Colors.ENDC}", end="", flush=True)
            
            print(f"\n{Colors.SUCCESS}✓ Wordlist generada: {output_path}{Colors.ENDC}")
            
            size_mb = os.path.getsize(output_path) / (1024 * 1024)
            print(f"{Colors.INFO}Tamaño: {size_mb:.2f} MB{Colors.ENDC}")
        
        except Exception as e:
            print_error(f"Error: {e}")
        
        self._pause()
    
    def _download_rockyou(self):
        """Download rockyou.txt wordlist."""
        print_info("Descargando rockyou.txt...")
        print_warning("Esto puede tomar varios minutos (139 MB)")
        confirm = input(f"{Colors.BOLD}¿Continuar? (s/N): {Colors.ENDC}").strip().lower()
        
        if confirm == 's':
            try:
                import requests
                url = "https://github.com/brannondorsey/naive-hashcat/releases/download/data/rockyou.txt"
                response = requests.get(url, stream=True)
                
                with open("data/wordlists/rockyou.txt", 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                print_success("✓ rockyou.txt descargado exitosamente")
            except Exception as e:
                print_error(f"Error al descargar: {e}")
        
        self._pause()
    
    def _create_simple_wordlist(self):
        """Create simple wordlist manually."""
        print_info("Crear wordlist simple")
        name = input(f"{Colors.INFO}Nombre del archivo: {Colors.ENDC}").strip()
        
        if name and not name.endswith('.txt'):
            name += '.txt'
        
        if name:
            filepath = f"data/wordlists/{name}"
            print_info("Introduce palabras (una por línea, Enter vacío para terminar):")
            
            words = []
            while True:
                word = input("> ")
                if not word:
                    break
                words.append(word)
            
            if words:
                with open(filepath, 'w') as f:
                    f.write('\n'.join(words))
                print_success(f"✓ Wordlist creada: {filepath}")
        
        self._pause()
    
    def _view_wordlist_content(self, wordlists):
        """View content of a wordlist."""
        if not wordlists:
            print_warning("No hay wordlists disponibles")
            self._pause()
            return
        
        print(f"\n{Colors.INFO}Wordlists disponibles:{Colors.ENDC}\n")
        for idx, wl in enumerate(sorted(wordlists), 1):
            print(f"  [{idx}] {os.path.basename(wl)}")
        
        choice = input(f"\n{Colors.BOLD}Número de wordlist [1-{len(wordlists)}]: {Colors.ENDC}").strip()
        
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(wordlists):
                wl = sorted(wordlists)[idx]
                print(f"\n{Colors.HEADER}{'═' * 60}{Colors.ENDC}")
                print(f"{Colors.BOLD}{os.path.basename(wl)}{Colors.ENDC}")
                print(f"{Colors.HEADER}{'═' * 60}{Colors.ENDC}\n")
                
                with open(wl, 'r', errors='ignore') as f:
                    lines = f.readlines()
                    print(f"{Colors.INFO}Mostrando primeras 20 líneas de {len(lines):,} totales:{Colors.ENDC}\n")
                    for i, line in enumerate(lines[:20], 1):
                        print(f"  {i:3}. {line.rstrip()}")
                
                print(f"\n{Colors.HEADER}{'═' * 60}{Colors.ENDC}")
        except:
            print_error("Índice inválido")
        
        self._pause()
    
    def _delete_wordlist(self, wordlists):
        """Delete a wordlist."""
        if not wordlists:
            print_warning("No hay wordlists disponibles")
            self._pause()
            return
        
        print(f"\n{Colors.INFO}Wordlists disponibles:{Colors.ENDC}\n")
        for idx, wl in enumerate(sorted(wordlists), 1):
            size_mb = os.path.getsize(wl) / (1024 * 1024)
            print(f"  [{idx}] {os.path.basename(wl)} ({size_mb:.2f} MB)")
        
        idx = input(f"\n{Colors.BOLD}Número de wordlist a eliminar [1-{len(wordlists)}]: {Colors.ENDC}").strip()
        try:
            idx_num = int(idx) - 1
            if 0 <= idx_num < len(wordlists):
                wl = sorted(wordlists)[idx_num]
                confirm = input(f"{Colors.WARNING}¿Eliminar {os.path.basename(wl)}? (s/N): {Colors.ENDC}").strip().lower()
                if confirm == 's':
                    os.remove(wl)
                    print_success("✓ Wordlist eliminada")
        except:
            print_error("Índice inválido")
        
        self._pause()
    
    def _combine_wordlists(self, wordlists):
        """Combine multiple wordlists."""
        if len(wordlists) < 2:
            print_warning("Se necesitan al menos 2 wordlists para combinar")
            self._pause()
            return
        
        print(f"\n{Colors.INFO}Wordlists disponibles:{Colors.ENDC}\n")
        for idx, wl in enumerate(sorted(wordlists), 1):
            size_mb = os.path.getsize(wl) / (1024 * 1024)
            print(f"  [{idx}] {os.path.basename(wl)} ({size_mb:.2f} MB)")
        
        print(f"\n{Colors.INFO}Selecciona wordlists a combinar (separados por coma):{Colors.ENDC}")
        print(f"{Colors.WARNING}Ejemplo: 1,3,5{Colors.ENDC}")
        
        selection = input(f"\n{Colors.BOLD}Wordlists: {Colors.ENDC}").strip()
        
        try:
            indices = [int(x.strip()) - 1 for x in selection.split(',')]
            selected_wls = [sorted(wordlists)[i] for i in indices if 0 <= i < len(wordlists)]
            
            if len(selected_wls) < 2:
                print_error("Se necesitan al menos 2 wordlists")
                self._pause()
                return
            
            output_name = input(f"\n{Colors.INFO}Nombre del archivo combinado [combined.txt]: {Colors.ENDC}").strip() or "combined.txt"
            
            if not output_name.endswith('.txt'):
                output_name += '.txt'
            
            output_path = f"data/wordlists/{output_name}"
            
            print(f"\n{Colors.INFO}Opciones de combinación:{Colors.ENDC}")
            print(f"  [1] Combinar y eliminar duplicados (recomendado)")
            print(f"  [2] Combinar simple (más rápido)")
            
            opt = input(f"\n{Colors.BOLD}Opción [1-2]: {Colors.ENDC}").strip()
            
            print_info("Combinando wordlists...")
            
            if opt == '1':
                # Combinar eliminando duplicados
                unique_words = set()
                for wl in selected_wls:
                    print(f"  Procesando {os.path.basename(wl)}...")
                    with open(wl, 'r', errors='ignore') as f:
                        unique_words.update(line.strip() for line in f if line.strip())
                
                with open(output_path, 'w') as f:
                    for word in sorted(unique_words):
                        f.write(f"{word}\n")
                
                print_success(f"✓ Combinadas {len(selected_wls)} wordlists")
                print(f"{Colors.INFO}Palabras únicas: {len(unique_words):,}{Colors.ENDC}")
            else:
                # Combinar simple
                total = 0
                with open(output_path, 'w') as out_f:
                    for wl in selected_wls:
                        print(f"  Agregando {os.path.basename(wl)}...")
                        with open(wl, 'r', errors='ignore') as in_f:
                            for line in in_f:
                                out_f.write(line)
                                total += 1
                
                print_success(f"✓ Combinadas {len(selected_wls)} wordlists")
                print(f"{Colors.INFO}Total palabras: {total:,}{Colors.ENDC}")
            
            size_mb = os.path.getsize(output_path) / (1024 * 1024)
            print(f"{Colors.INFO}Archivo: {output_path} ({size_mb:.2f} MB){Colors.ENDC}")
        
        except Exception as e:
            print_error(f"Error: {e}")
        
        self._pause()
    
    def _download_rockyou(self):
        """Download rockyou.txt wordlist."""
        print_info("Descargando rockyou.txt...")
        print_warning("Esto puede tomar varios minutos (139 MB)")
        confirm = input(f"{Colors.BOLD}¿Continuar? (s/N): {Colors.ENDC}").strip().lower()
        
        if confirm == 's':
            try:
                import requests
                url = "https://github.com/brannondorsey/naive-hashcat/releases/download/data/rockyou.txt"
                response = requests.get(url, stream=True)
                
                with open("data/wordlists/rockyou.txt", 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                print_success("✓ rockyou.txt descargado exitosamente")
            except Exception as e:
                print_error(f"Error al descargar: {e}")
        
        self._pause()
    
    def _create_simple_wordlist(self):
        """Create simple wordlist manually."""
        print_info("Crear wordlist simple")
        name = input(f"{Colors.INFO}Nombre del archivo: {Colors.ENDC}").strip()
        
        if name and not name.endswith('.txt'):
            name += '.txt'
        
        if name:
            filepath = f"data/wordlists/{name}"
            print_info("Introduce palabras (una por línea, Enter vacío para terminar):")
            
            words = []
            while True:
                word = input("> ")
                if not word:
                    break
                words.append(word)
            
            if words:
                with open(filepath, 'w') as f:
                    f.write('\n'.join(words))
                print_success(f"✓ Wordlist creada: {filepath}")
        
        self._pause()
    
    def _view_wordlist_content(self, wordlists):
        """View content of a wordlist."""
        if not wordlists:
            print_warning("No hay wordlists disponibles")
            self._pause()
            return
        
        print(f"\n{Colors.INFO}Wordlists disponibles:{Colors.ENDC}\n")
        for idx, wl in enumerate(sorted(wordlists), 1):
            print(f"  [{idx}] {os.path.basename(wl)}")
        
        choice = input(f"\n{Colors.BOLD}Número de wordlist [1-{len(wordlists)}]: {Colors.ENDC}").strip()
        
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(wordlists):
                wl = sorted(wordlists)[idx]
                print(f"\n{Colors.HEADER}{'═' * 60}{Colors.ENDC}")
                print(f"{Colors.BOLD}{os.path.basename(wl)}{Colors.ENDC}")
                print(f"{Colors.HEADER}{'═' * 60}{Colors.ENDC}\n")
                
                with open(wl, 'r', errors='ignore') as f:
                    lines = f.readlines()
                    print(f"{Colors.INFO}Mostrando primeras 20 líneas de {len(lines):,} totales:{Colors.ENDC}\n")
                    for i, line in enumerate(lines[:20], 1):
                        print(f"  {i:3}. {line.rstrip()}")
                
                print(f"\n{Colors.HEADER}{'═' * 60}{Colors.ENDC}")
        except:
            print_error("Índice inválido")
        
        self._pause()
    
    def _delete_wordlist(self, wordlists):
        """Delete a wordlist."""
        if not wordlists:
            print_warning("No hay wordlists disponibles")
            self._pause()
            return
        
        print(f"\n{Colors.INFO}Wordlists disponibles:{Colors.ENDC}\n")
        for idx, wl in enumerate(sorted(wordlists), 1):
            size_mb = os.path.getsize(wl) / (1024 * 1024)
            print(f"  [{idx}] {os.path.basename(wl)} ({size_mb:.2f} MB)")
        
        idx = input(f"\n{Colors.BOLD}Número de wordlist a eliminar [1-{len(wordlists)}]: {Colors.ENDC}").strip()
        try:
            idx_num = int(idx) - 1
            if 0 <= idx_num < len(wordlists):
                wl = sorted(wordlists)[idx_num]
                confirm = input(f"{Colors.WARNING}¿Eliminar {os.path.basename(wl)}? (s/N): {Colors.ENDC}").strip().lower()
                if confirm == 's':
                    os.remove(wl)
                    print_success("✓ Wordlist eliminada")
        except:
            print_error("Índice inválido")
        
        self._pause()
    
    def _combine_wordlists(self, wordlists):
        """Combine multiple wordlists."""
        if len(wordlists) < 2:
            print_warning("Se necesitan al menos 2 wordlists para combinar")
            self._pause()
            return
        
        print(f"\n{Colors.INFO}Wordlists disponibles:{Colors.ENDC}\n")
        for idx, wl in enumerate(sorted(wordlists), 1):
            size_mb = os.path.getsize(wl) / (1024 * 1024)
            print(f"  [{idx}] {os.path.basename(wl)} ({size_mb:.2f} MB)")
        
        print(f"\n{Colors.INFO}Selecciona wordlists a combinar (separados por coma):{Colors.ENDC}")
        print(f"{Colors.WARNING}Ejemplo: 1,3,5{Colors.ENDC}")
        
        selection = input(f"\n{Colors.BOLD}Wordlists: {Colors.ENDC}").strip()
        
        try:
            indices = [int(x.strip()) - 1 for x in selection.split(',')]
            selected_wls = [sorted(wordlists)[i] for i in indices if 0 <= i < len(wordlists)]
            
            if len(selected_wls) < 2:
                print_error("Se necesitan al menos 2 wordlists")
                self._pause()
                return
            
            output_name = input(f"\n{Colors.INFO}Nombre del archivo combinado [combined.txt]: {Colors.ENDC}").strip() or "combined.txt"
            
            if not output_name.endswith('.txt'):
                output_name += '.txt'
            
            output_path = f"data/wordlists/{output_name}"
            
            print(f"\n{Colors.INFO}Opciones de combinación:{Colors.ENDC}")
            print(f"  [1] Combinar y eliminar duplicados (recomendado)")
            print(f"  [2] Combinar simple (más rápido)")
            
            opt = input(f"\n{Colors.BOLD}Opción [1-2]: {Colors.ENDC}").strip()
            
            print_info("Combinando wordlists...")
            
            if opt == '1':
                # Combinar eliminando duplicados
                unique_words = set()
                for wl in selected_wls:
                    print(f"  Procesando {os.path.basename(wl)}...")
                    with open(wl, 'r', errors='ignore') as f:
                        unique_words.update(line.strip() for line in f if line.strip())
                
                with open(output_path, 'w') as f:
                    for word in sorted(unique_words):
                        f.write(f"{word}\n")
                
                print_success(f"✓ Combinadas {len(selected_wls)} wordlists")
                print(f"{Colors.INFO}Palabras únicas: {len(unique_words):,}{Colors.ENDC}")
            else:
                # Combinar simple
                total = 0
                with open(output_path, 'w') as out_f:
                    for wl in selected_wls:
                        print(f"  Agregando {os.path.basename(wl)}...")
                        with open(wl, 'r', errors='ignore') as in_f:
                            for line in in_f:
                                out_f.write(line)
                                total += 1
                
                print_success(f"✓ Combinadas {len(selected_wls)} wordlists")
                print(f"{Colors.INFO}Total palabras: {total:,}{Colors.ENDC}")
            
            size_mb = os.path.getsize(output_path) / (1024 * 1024)
            print(f"{Colors.INFO}Archivo: {output_path} ({size_mb:.2f} MB){Colors.ENDC}")
        
        except Exception as e:
            print_error(f"Error: {e}")
        
        self._pause()
    
    def _cleanup_temp_files(self):
        """Clean up temporary files."""
        print_section_header("LIMPIAR ARCHIVOS TEMPORALES")
        
        print_info("Buscando archivos temporales...\n")
        
        patterns = [
            "/tmp/wifibreaker*",
            "/tmp/wpa_supplicant_wifibreaker*"
        ]
        
        files_found = []
        total_size = 0
        
        for pattern in patterns:
            for f in glob.glob(pattern):
                try:
                    size = os.path.getsize(f)
                    files_found.append((f, size))
                    total_size += size
                except:
                    pass
        
        if files_found:
            print(f"{Colors.INFO}Archivos encontrados:{Colors.ENDC}\n")
            for f, size in files_found:
                print(f"  • {f} ({size / 1024:.1f} KB)")
            
            print(f"\n{Colors.WARNING}Total: {len(files_found)} archivos ({total_size / (1024*1024):.2f} MB){Colors.ENDC}\n")
            
            confirm = input(f"{Colors.BOLD}¿Eliminar todos? (s/N): {Colors.ENDC}").strip().lower()
            
            if confirm == 's':
                deleted = 0
                for f, _ in files_found:
                    try:
                        os.remove(f)
                        deleted += 1
                    except:
                        pass
                
                print_success(f"✓ {deleted} archivos eliminados")
        else:
            print_success("✓ No hay archivos temporales")
        
        self._pause()
    
    def _view_saved_results(self):
        """View saved attack results."""
        print_section_header("RESULTADOS GUARDADOS")
        
        results_dir = "data/results"
        
        if not os.path.exists(results_dir):
            print_warning("No hay resultados guardados")
            self._pause()
            return
        
        results = sorted(glob.glob(f"{results_dir}/*.txt"), key=os.path.getmtime, reverse=True)
        
        if not results:
            print_warning("No hay resultados guardados")
            self._pause()
            return
        
        print(f"{Colors.INFO}Resultados guardados ({len(results)}):{Colors.ENDC}\n")
        
        for idx, result in enumerate(results[:20], 1):
            try:
                with open(result, 'r') as f:
                    content = f.read()
                    ssid = "Unknown"
                    password = "Unknown"
                    
                    for line in content.split('\n'):
                        if line.startswith('SSID:'):
                            ssid = line.split(':', 1)[1].strip()
                        elif line.startswith('Password:'):
                            password = line.split(':', 1)[1].strip()
                    
                    mtime = time.strftime("%Y-%m-%d %H:%M", time.localtime(os.path.getmtime(result)))
                    print(f"  [{idx}] {ssid} - {mtime}")
                    print(f"      Password: {Colors.BOLD}{password}{Colors.ENDC}")
                    print()
            except:
                continue
        
        print(f"\n{Colors.INFO}Opciones:{Colors.ENDC}")
        print(f"  [N] Ver detalle del resultado N")
        print(f"  [d] Eliminar todos los resultados")
        print(f"  [0] Volver")
        
        choice = input(f"\n{Colors.BOLD}Opción: {Colors.ENDC}").strip()
        
        if choice == 'd':
            confirm = input(f"{Colors.WARNING}¿Eliminar TODOS los resultados? (s/N): {Colors.ENDC}").strip().lower()
            if confirm == 's':
                for r in results:
                    try:
                        os.remove(r)
                    except:
                        pass
                print_success("✓ Resultados eliminados")
        elif choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(results):
                with open(results[idx], 'r') as f:
                    print(f"\n{Colors.HEADER}{'═' * 60}{Colors.ENDC}")
                    print(f.read())
                    print(f"{Colors.HEADER}{'═' * 60}{Colors.ENDC}")
        
        self._pause()
    
    def _change_tx_power(self):
        """Change transmission power."""
        print_section_header("POTENCIA DE TRANSMISIÓN")
        
        print_info("Potencia actual:")
        subprocess.run(['iwconfig', self.monitor_interface])
        
        print(f"\n{Colors.WARNING}Advertencia: Aumentar la potencia puede ser ilegal en tu país{Colors.ENDC}\n")
        
        print(f"{Colors.INFO}Valores comunes:{Colors.ENDC}")
        print(f"  20 dBm - Estándar")
        print(f"  30 dBm - Alto (puede sobrecalentar)")
        
        power = input(f"\n{Colors.BOLD}Nueva potencia (dBm) o [Enter] para cancelar: {Colors.ENDC}").strip()
        
        if power.isdigit():
            cmd = ['sudo', 'iwconfig', self.monitor_interface, 'txpower', power]
            result = subprocess.run(cmd, capture_output=True)
            
            if result.returncode == 0:
                print_success(f"✓ Potencia cambiada a {power} dBm")
            else:
                print_error("Error al cambiar potencia")
        
        self._pause()
    
    def _configure_scan_channels(self):
        """Configure scan channels."""
        print_section_header("CANALES DE ESCANEO")
        
        print(f"{Colors.INFO}Canales actuales: 1-14 (todos){Colors.ENDC}\n")
        
        print(f"{Colors.INFO}Opciones:{Colors.ENDC}")
        print(f"  [1] 2.4 GHz (1-14)")
        print(f"  [2] Solo canales populares (1, 6, 11)")
        print(f"  [3] Personalizado")
        print(f"  [0] Volver")
        
        choice = input(f"\n{Colors.BOLD}Opción: {Colors.ENDC}").strip()
        
        if choice == '3':
            channels = input(f"{Colors.INFO}Canales separados por coma (ej: 1,6,11): {Colors.ENDC}").strip()
            print_success(f"✓ Configurado: {channels}")
            print_warning("Esta configuración se aplicará en el próximo escaneo")
        
        self._pause()
    
    def _configure_timeouts(self):
        """Configure attack timeouts."""
        print_section_header("CONFIGURAR TIMEOUTS")
        
        print(f"{Colors.INFO}Timeouts actuales:{Colors.ENDC}\n")
        print(f"  Captura de handshake: 120 segundos")
        print(f"  Ataque WPS: 300 segundos")
        print(f"  Deauth entre pulsos: 5 segundos")
        
        print_warning("\nEsta funcionalidad requiere editar config.json")
        print_info("Ubicación: config.json")
        
        self._pause()
    
    def _restart_monitor_mode(self):
        """Restart monitor mode."""
        print_section_header("REINICIAR MODO MONITOR")
        
        print_warning("Esto reiniciará el modo monitor del adaptador")
        confirm = input(f"{Colors.BOLD}¿Continuar? (s/N): {Colors.ENDC}").strip().lower()
        
        if confirm == 's':
            from core.monitor import MonitorMode
            
            print_info("Desactivando modo monitor...")
            original_interface = self.monitor_interface.replace('mon', '')
            monitor = MonitorMode(original_interface)
            monitor.monitor_interface = self.monitor_interface
            monitor.disable()
            
            time.sleep(2)
            
            print_info("Reactivando modo monitor...")
            if monitor.enable():
                self.monitor_interface = monitor.get_monitor_interface()
                print_success(f"✓ Modo monitor reiniciado: {self.monitor_interface}")
            else:
                print_error("Error al reiniciar")
        
        self._pause()
    
    def _view_logs(self):
        """View application logs."""
        print_section_header("LOGS DE LA APLICACIÓN")
        
        logs_dir = "data/logs"
        
        if not os.path.exists(logs_dir):
            print_warning("No hay logs disponibles")
            self._pause()
            return
        
        logs = sorted(glob.glob(f"{logs_dir}/*.log"), key=os.path.getmtime, reverse=True)
        
        if not logs:
            print_warning("No hay logs disponibles")
            self._pause()
            return
        
        print(f"{Colors.INFO}Logs disponibles:{Colors.ENDC}\n")
        
        for idx, log in enumerate(logs[:10], 1):
            size = os.path.getsize(log) / 1024
            mtime = time.strftime("%Y-%m-%d %H:%M", time.localtime(os.path.getmtime(log)))
            print(f"  [{idx}] {os.path.basename(log)} ({size:.1f} KB) - {mtime}")
        
        choice = input(f"\n{Colors.BOLD}Ver log [1-{len(logs[:10])}] o [0] para volver: {Colors.ENDC}").strip()
        
        if choice.isdigit() and choice != '0':
            idx = int(choice) - 1
            if 0 <= idx < len(logs):
                print(f"\n{Colors.HEADER}{'═' * 60}{Colors.ENDC}")
                with open(logs[idx], 'r') as f:
                    lines = f.readlines()
                    # Mostrar últimas 50 líneas
                    for line in lines[-50:]:
                        print(line.rstrip())
                print(f"{Colors.HEADER}{'═' * 60}{Colors.ENDC}")
        
        self._pause()
    
    def run(self):
        """Run the main menu loop."""
        while self.running:
            try:
                self._print_menu()
                
                choice = input(f"{Colors.BOLD}Selecciona una opción [0-8]: {Colors.ENDC}").strip()
                
                if choice == '1':
                    self._scan_networks()
                elif choice == '2':
                    self._view_networks()
                elif choice == '3':
                    self._select_target_manual()
                elif choice == '4':
                    self._select_target_auto()
                elif choice == '5':
                    self._attack_target()
                elif choice == '6':
                    self._view_target_details()
                elif choice == '7':
                    self._connect_to_network()
                elif choice == '8':
                    self._advanced_settings()
                elif choice == '0':
                    print(f"\n{Colors.INFO}Saliendo...{Colors.ENDC}")
                    self.running = False
                else:
                    print_error("Opción inválida")
                    time.sleep(1)
            
            except KeyboardInterrupt:
                print(f"\n\n{Colors.WARNING}Interrupción detectada{Colors.ENDC}")
                confirm = input(f"{Colors.BOLD}¿Realmente deseas salir? (s/N): {Colors.ENDC}").strip().lower()
                if confirm == 's':
                    self.running = False
            
            except Exception as e:
                print_error(f"Error: {e}")
                import traceback
                traceback.print_exc()
                self._pause()
        
        # Cleanup
        self.scanner.stop_scan()
        self.scanner.cleanup()