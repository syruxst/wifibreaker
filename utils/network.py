"""Network utilities for connection management."""

import subprocess
from typing import Optional
from ui.colors import print_info, print_success, print_error


class NetworkManager:
    """Manages network connections."""
    
    def __init__(self):
        self.current_connection = None
    
    def connect_to_network(self, ssid: str, password: str, interface: str = "wlan0") -> bool:
        """Connect to a WiFi network."""
        print_info(f"Conectando a {ssid}...")
        
        config_file = "/tmp/wpa_temp.conf"
        
        try:
            with open(config_file, 'w') as f:
                f.write("network={\n")
                f.write(f'    ssid="{ssid}"\n')
                f.write(f'    psk="{password}"\n')
                f.write("}\n")
            
            cmd = ['wpa_supplicant', '-B', '-i', interface, '-c', config_file]
            result = subprocess.run(cmd, capture_output=True, timeout=10)
            
            if result.returncode == 0:
                subprocess.run(['dhclient', interface], timeout=10)
                print_success(f"Conectado a {ssid}")
                self.current_connection = ssid
                return True
            else:
                print_error("Fallo al conectar")
                return False
        
        except Exception as e:
            print_error(f"Error: {e}")
            return False
        finally:
            try:
                import os
                os.remove(config_file)
            except:
                pass
    
    def disconnect(self, interface: str = "wlan0"):
        """Disconnect from network."""
        if not self.current_connection:
            return
        
        subprocess.run(['killall', 'wpa_supplicant'], capture_output=True)
        self.current_connection = None
        print_success("Desconectado")