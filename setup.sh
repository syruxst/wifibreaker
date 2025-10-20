#!/bin/bash
# ============================================================================
# setup.sh - Script de Instalación Automática
# ============================================================================

set -e

BLUE='\033[0;34m'
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}"
cat << "EOF"
╦ ╦┬┌─┐┬╔╗ ┬─┐┌─┐┌─┐┬┌─┌─┐┬─┐
║║║│├┤ │╠╩╗├┬┘├┤ ├─┤├┴┐├┤ ├┬┘
╚╩╝┴└  ┴╚═╝┴└─└─┘┴ ┴┴ ┴└─┘┴└─
    Setup & Installation
EOF
echo -e "${NC}"

if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}[✗] Ejecuta como root: sudo ./setup.sh${NC}"
    exit 1
fi

echo -e "${GREEN}[✓] Ejecutando como root${NC}"

if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
else
    echo -e "${RED}[✗] No se detectó el sistema operativo${NC}"
    exit 1
fi

echo -e "${BLUE}[*] Sistema: $OS${NC}"

install_debian() {
    echo -e "${BLUE}[*] Instalando dependencias para Debian/Ubuntu...${NC}"
    apt-get update
    apt-get install -y \
        python3 \
        python3-pip \
        python3-dev \
        aircrack-ng \
        reaver \
        wireless-tools \
        net-tools \
        iw \
        build-essential \
        libssl-dev
    echo -e "${GREEN}[✓] Dependencias instaladas${NC}"
}

install_arch() {
    echo -e "${BLUE}[*] Instalando para Arch Linux...${NC}"
    pacman -Sy --noconfirm \
        python \
        python-pip \
        aircrack-ng \
        reaver \
        wireless_tools \
        net-tools \
        iw
    echo -e "${GREEN}[✓] Dependencias instaladas${NC}"
}

case "$OS" in
    ubuntu|debian|kali|parrot)
        install_debian
        ;;
    arch|manjaro)
        install_arch
        ;;
    *)
        echo -e "${YELLOW}[!] Sistema no reconocido${NC}"
        echo -e "${YELLOW}[!] Instala manualmente: aircrack-ng, reaver${NC}"
        ;;
esac

echo -e "${BLUE}[*] Instalando dependencias Python...${NC}"
sudo apt install python3-scapy python3-rich python3-psutil python3-requests -y
echo -e "${GREEN}[✓] Python OK${NC}"

echo -e "${BLUE}[*] Creando directorios...${NC}"
mkdir -p data/wordlists data/captures data/results data/logs

echo -e "${BLUE}[*] Descargando wordlist...${NC}"
if [ ! -f "data/wordlists/top1000.txt" ]; then
    curl -s "https://raw.githubusercontent.com/danielmiessler/SecLists/master/Passwords/Common-Credentials/10-million-password-list-top-1000.txt" \
        -o data/wordlists/top1000.txt 2>/dev/null || \
        echo -e "${YELLOW}[!] No se descargó top1000.txt${NC}"
fi

chmod +x main.py

echo -e "${GREEN}"
cat << "EOF"

╔═══════════════════════════════════════╗
║   ✓ Instalación Completada           ║
╚═══════════════════════════════════════╝

Ejecutar: sudo python3 main.py

EOF
echo -e "${NC}"