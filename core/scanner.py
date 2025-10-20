"""
WiFi network scanner and analyzer.
"""

import subprocess
import re
import time
import threading
import os
import glob
from typing import List, Dict, Optional
from dataclasses import dataclass, field
# Asumo que la importación de ui.colors es correcta
from ui.colors import Colors, print_info, print_success, print_warning 


@dataclass
class WiFiNetwork:
    """Represents a detected WiFi network."""
    bssid: str
    ssid: str = "Hidden"
    channel: int = 0
    signal: int = -100
    encryption: str = "Unknown"
    cipher: str = ""
    authentication: str = ""
    clients: int = 0
    wps: bool = False
    wps_locked: bool = False
    clients_list: List[str] = field(default_factory=list) # Esta lista contendrá los MACs ORDENADOS por tráfico
    beacons: int = 0
    data_packets: int = 0
    
    def get_security_type(self) -> str:
        """Get simplified security type."""
        enc = self.encryption.upper()
        if 'WPA3' in enc:
            return 'WPA3'
        elif 'WPA2' in enc:
            return 'WPA2'
        elif 'WPA' in enc:
            return 'WPA'
        elif 'WEP' in enc:
            return 'WEP'
        elif 'OPN' in enc or 'OPEN' in enc:
            return 'OPEN'
        return 'Unknown'
    
    def __str__(self) -> str:
        """String representation for display."""
        signal_bars = self._signal_to_bars()
        ssid_display = self.ssid if self.ssid else "<Hidden>"
        
        return (f"BSSID: {self.bssid} | SSID: {ssid_display:20} | "
                f"CH: {self.channel:2} | Signal: {signal_bars} {self.signal}dBm | "
                f"Enc: {self.get_security_type():5} | Clients: {self.clients}")
    
    def _signal_to_bars(self) -> str:
        """Convert signal strength to visual bars."""
        if self.signal >= -50:
            return "▂▄▆█"
        elif self.signal >= -60:
            return "▂▄▆ "
        elif self.signal >= -70:
            return "▂▄  "
        else:
            return "▂   "


class NetworkScanner:
    """Scans for WiFi networks in monitor mode."""
    
    def __init__(self, interface: str):
        self.interface = interface
        self.networks: Dict[str, WiFiNetwork] = {}
        self.scanning = False
        self.scan_thread = None
        self.capture_file = "/tmp/wifibreaker_scan"
    
    def _parse_airodump_csv(self, csv_file: str) -> None:
        """Parse airodump-ng CSV output, now including client sorting by packets."""
        try:
            with open(csv_file, 'r', errors='ignore') as f:
                content = f.read()
            
            # Normalizar saltos de línea y dividir en secciones
            content_normalized = content.replace('\r\n', '\n')
            parts = content_normalized.split('\n\n')
            
            # Lógica para manejar el split robusto
            if len(parts) < 2:
                if 'Station MAC, First time seen' in content_normalized:
                    parts = content_normalized.split('Station MAC, First time seen')
                    ap_section = parts[0]
                    station_section = 'Station MAC, First time seen' + parts[1]
                else:
                    return
            else:
                ap_section = parts[0]
                station_section = parts[1] if len(parts) > 1 else ""

            # Parse Access Points
            # 💡 CORRECCIÓN: Cambiar de [2:] a [1:] para leer la primera línea de datos.
            for line in ap_section.split('\n')[1:]:  
                if not line.strip() or line.strip().startswith('BSSID'):
                    continue
                
                parts = [p.strip() for p in line.split(',')]
                if len(parts) < 14:
                    continue
                
                try:
                    bssid = parts[0]
                    if not bssid or ':' not in bssid:
                        continue
                    
                    # Parse network details
                    channel = int(parts[3]) if parts[3].strip().isdigit() else 0
                    # parts[8] es el campo Power que se traduce a Signal (dBm)
                    signal = int(parts[8]) if parts[8].strip().lstrip('-').isdigit() else -100 
                    encryption = parts[5]
                    cipher = parts[6]
                    authentication = parts[7]
                    beacons = int(parts[9]) if parts[9].strip().isdigit() else 0
                    data = int(parts[10]) if parts[10].strip().isdigit() else 0
                    ssid = parts[13] if len(parts) > 13 else ""
                    
                    # Create or update network
                    if bssid not in self.networks:
                        self.networks[bssid] = WiFiNetwork(
                            bssid=bssid,
                            ssid=ssid,
                            channel=channel,
                            signal=signal,
                            encryption=encryption,
                            cipher=cipher,
                            authentication=authentication,
                            beacons=beacons,
                            data_packets=data
                        )
                    else:
                        # Update existing
                        net = self.networks[bssid]
                        net.signal = signal
                        net.beacons = beacons
                        net.data_packets = data
                        if ssid and not net.ssid:
                            net.ssid = ssid
                
                except (ValueError, IndexError, Exception):
                    continue
            
            # Parse Stations (clients)
            # USAMOS ESTA ESTRUCTURA PARA ALMACENAR EL TRAFICO (PAQUETES) Y LUEGO ORDENAR
            # {BSSID: [(client_mac, packets)]}
            client_data_map: Dict[str, List[tuple[str, int]]] = {} 
            
            # 💡 CORRECCIÓN: Cambiar de [2:] a [1:] para leer la primera línea de datos.
            for line in station_section.split('\n')[1:]:
                if not line.strip() or line.strip().startswith('Station MAC'):
                    continue
                
                parts = [p.strip() for p in line.split(',')]
                # Necesitamos al menos 6 campos. El índice 3 es el conteo de paquetes del cliente.
                if len(parts) < 6: 
                    continue
                
                try:
                    station_mac = parts[0]
                    connected_bssid = parts[5]
                    # Indice 3: # Packets del cliente
                    packets = int(parts[3]) if parts[3].strip().lstrip('-').isdigit() else 0 
                    
                    if connected_bssid and ':' in connected_bssid:
                        if connected_bssid not in client_data_map:
                            client_data_map[connected_bssid] = []
                        
                        # Almacenar el par (MAC, Paquetes)
                        # Verificamos si el MAC ya existe para evitar duplicados si airodump repite líneas
                        macs_in_list = [mac for mac, p in client_data_map[connected_bssid]]
                        if station_mac not in macs_in_list:
                            client_data_map[connected_bssid].append((station_mac, packets))
                
                except (ValueError, IndexError, Exception):
                    continue
            
            # Update network clients and SORT THEM by packets
            for bssid, client_list in client_data_map.items():
                if bssid in self.networks:
                    
                    # LÓGICA CLAVE: Ordenar por conteo de paquetes (índice 1 de la tupla) DESCENDENTE
                    client_list.sort(key=lambda x: x[1], reverse=True)
                    
                    # Asignar la lista de solo MACs (ya ordenados) a la red
                    self.networks[bssid].clients_list = [mac for mac, packets in client_list]
                    self.networks[bssid].clients = len(self.networks[bssid].clients_list)
        
        except FileNotFoundError:
             # Se ignora la excepción si el archivo aún no existe al inicio del escaneo
             pass
        except Exception as e:
            print_warning(f"Error general al intentar parsear: {e}")
    
    def _scan_worker(self, duration: int, channels: Optional[List[int]] = None):
        """Worker thread for scanning."""
        # Se elimina la definición estática de csv_file aquí
        
        # Build airodump command
        # 💡 CORRECCIÓN: Se añadió 'sudo' y se eliminan las redirecciones a DEVNULL
        cmd = ['sudo', 'airodump-ng', self.interface, '-w', self.capture_file, '--output-format', 'csv']
        
        if channels:
            cmd.extend(['--channel', ','.join(map(str, channels))])
        
        try:
            print_info(f"DEBUG: Ejecutando airodump-ng: {' '.join(cmd)}") 
            
            # Start airodump
            process = subprocess.Popen(
                cmd,
                # Permitiendo que airodump use stdout/stderr.
            )
            
            # Scan for specified duration
            start_time = time.time()
            time.sleep(5) 
            
            while self.scanning and (time.time() - start_time < duration):
                time.sleep(1)
                
                # --- CORRECCIÓN: Encontrar el archivo CSV más reciente ---
                list_of_files = glob.glob(f"{self.capture_file}-*.csv")
                
                if list_of_files:
                    # Ordena por el timestamp de modificación y toma el más reciente
                    latest_file = max(list_of_files, key=os.path.getctime)
                    self._parse_airodump_csv(latest_file)
                # -----------------------------------------------------------
            
            # Kill airodump
            print_info("Señalando a airodump-ng para que termine...")
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                print_warning("airodump-ng no terminó, enviando señal de KILL.")
                process.kill()
            
            # Final parse
            time.sleep(1)
            # Lectura final
            list_of_files = glob.glob(f"{self.capture_file}-*.csv")
            if list_of_files:
                latest_file = max(list_of_files, key=os.path.getctime)
                self._parse_airodump_csv(latest_file)
            
        except FileNotFoundError:
            print_warning("Error: 'airodump-ng' no se encontró. Asegúrate de que la suite aircrack-ng esté instalada.")
        except PermissionError:
            print_warning("Error: Permiso denegado. Asegúrate de ejecutar el programa con permisos de root (sudo).")
        except Exception as e:
            print_warning(f"Error durante el escaneo: {e}")
        finally:
            self.scanning = False
    
    def start_scan(self, duration: int = 30, channels: Optional[List[int]] = None) -> None:
        """Start scanning for networks."""
        if self.scanning:
            print_warning("Escaneo ya en progreso")
            return
        
        print_info(f"Iniciando escaneo por {duration} segundos...")
        if channels:
            print_info(f"Canales: {', '.join(map(str, channels))}")
        else:
            print_info("Escaneando todos los canales (1-14)")
        
        self.networks.clear()
        self.scanning = True
        
        self.scan_thread = threading.Thread(
            target=self._scan_worker,
            args=(duration, channels)
        )
        self.scan_thread.daemon = True
        self.scan_thread.start()
    
    def stop_scan(self) -> None:
        """Stop the current scan."""
        if not self.scanning:
            return
        
        print_info("Deteniendo escaneo...")
        self.scanning = False
        
        if self.scan_thread:
            self.scan_thread.join(timeout=10)
    
    def is_scanning(self) -> bool:
        """Check if currently scanning."""
        return self.scanning
    
    def get_networks(self, sort_by: str = 'signal') -> List[WiFiNetwork]:
        """Get list of detected networks, sorted."""
        networks = list(self.networks.values())
        
        if sort_by == 'signal':
            networks.sort(key=lambda x: x.signal, reverse=True)
        elif sort_by == 'channel':
            networks.sort(key=lambda x: x.channel)
        elif sort_by == 'clients':
            networks.sort(key=lambda x: x.clients, reverse=True)
        elif sort_by == 'ssid':
            networks.sort(key=lambda x: x.ssid.lower())
        
        return networks
    
    def get_network_by_bssid(self, bssid: str) -> Optional[WiFiNetwork]:
        """Get a specific network by BSSID."""
        return self.networks.get(bssid)
    
    def display_networks(self, top_n: int = None) -> None:
        """Display detected networks in a formatted table."""
        networks = self.get_networks(sort_by='signal')
        
        if not networks:
            print_warning("No se detectaron redes")
            return
        
        if top_n:
            networks = networks[:top_n]
        
        print(f"\n{Colors.HEADER}╔═══════════════════════════════════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║                           Redes WiFi Detectadas ({len(networks)})                                     ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╚═══════════════════════════════════════════════════════════════════════════════════════╝{Colors.ENDC}\n")
        
        # Header
        print(f"{Colors.BOLD}{'#':<3} {'BSSID':<17} {'SSID':<25} {'CH':<3} {'Signal':<8} {'Enc':<6} {'Clients'}{Colors.ENDC}")
        print("─" * 95)
        
        # Networks
        for idx, net in enumerate(networks, 1):
            signal_bars = net._signal_to_bars()
            ssid_display = net.ssid[:24] if net.ssid else f"{Colors.WARNING}<Hidden>{Colors.ENDC}"
            
            # Color code by security
            enc_color = Colors.SUCCESS if net.get_security_type() in ['WPA2', 'WPA3'] else Colors.WARNING
            if net.get_security_type() == 'OPEN':
                enc_color = Colors.FAIL
            
            # Color code by signal
            sig_color = Colors.SUCCESS if net.signal >= -60 else Colors.WARNING if net.signal >= -70 else Colors.FAIL
            
            print(f"{idx:<3} {net.bssid:<17} {ssid_display:<25} {net.channel:<3} "
                  f"{sig_color}{signal_bars} {net.signal:>3}dBm{Colors.ENDC} "
                  f"{enc_color}{net.get_security_type():<6}{Colors.ENDC} "
                  f"{net.clients}")
        
        print()
    
    def cleanup(self) -> None:
        """Clean up temporary files."""
        import glob
        for f in glob.glob(f"{self.capture_file}*"):
            try:
                import os
                os.remove(f)
            except:
                pass
