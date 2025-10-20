# 🔓 WifiBreaker Pro

**Automated WiFi Auditing Suite** - Herramienta profesional para auditorías de seguridad WiFi

> ⚠️ **DISCLAIMER**: Esta herramienta es solo para uso educativo y auditorías autorizadas. El uso no autorizado es ilegal.

---

## 🎯 Características

### ✨ Innovaciones Principales

- **🤖 Selección Inteligente de Targets**: Sistema de scoring automático que evalúa y prioriza redes objetivo
- **📊 Dashboard en Tiempo Real**: Visualización moderna de escaneos y ataques
- **⚡ Ataques Automatizados**: Flujo simplificado desde escaneo hasta crack
- **🎯 Múltiples Vectores de Ataque**: WPA/WPA2, WPS (Pixie Dust), WEP
- **📈 Progreso en Tiempo Real**: Monitoreo visual de cada fase del ataque
- **💾 Gestión de Resultados**: Guardado automático de contraseñas crackeadas

### 🔧 Funcionalidades

1. **Escaneo de Redes**
   - Escaneo rápido, estándar y profundo
   - Detección de canales, clientes, encriptación
   - Identificación de WPS habilitado

2. **Sistema de Scoring**
   - Evaluación basada en: señal, clientes, seguridad, WPS, actividad
   - Recomendaciones automáticas de targets
   - Estimación de probabilidad de éxito

3. **Ataques Implementados**
   - **WPA/WPA2**: Captura de handshake + ataque de diccionario
   - **WPS**: Pixie Dust, Bully, Reaver brute force
   - **WEP**: (Próximamente)

4. **Gestión de Wordlists**
   - Soporte para múltiples diccionarios
   - Integración con rockyou.txt
   - Top 1000 passwords incluido

---

## 📋 Requisitos

### Sistema Operativo
- Linux (Ubuntu, Debian, Kali, Parrot, Arch)
- Adaptador WiFi con soporte de modo monitor

### Dependencias del Sistema
```bash
# Herramientas principales
aircrack-ng
reaver
bully
wireless-tools
net-tools
iw
macchanger

# Opcionales (recomendadas)
hashcat
hcxtools
```

### Dependencias de Python
```bash
python3.8+
scapy
rich
psutil
requests
```

---

## 🚀 Instalación

### Instal# wifibreaker
