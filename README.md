# 🔓 WifiBreaker Pro

**Automated WiFi Auditing Suite** - Herramienta profesional para auditorías de seguridad WiFi con motor de generación de wordlists inteligente **Cerbero**

> ⚠️ **DISCLAIMER**: Esta herramienta es solo para uso educativo y auditorías autorizadas. El uso no autorizado es ilegal y puede resultar en consecuencias legales graves.

---

## 🎯 Características

### ✨ Innovaciones Principales

- **🤖 Selección Inteligente de Targets**: Sistema de scoring automático que evalúa y prioriza redes objetivo
- **🔥 Motor Cerbero**: Generador avanzado de wordlists personalizadas basado en información del objetivo
- **📊 Dashboard en Tiempo Real**: Visualización moderna de escaneos y ataques
- **⚡ Ataques Automatizados**: Flujo simplificado desde escaneo hasta crack
- **🎯 Múltiples Vectores de Ataque**: WPA/WPA2, WPS (Pixie Dust), WEP
- **📈 Progreso en Tiempo Real**: Monitoreo visual de cada fase del ataque
- **💾 Gestión de Resultados**: Guardado automático de contraseñas crackeadas
- **🌐 Conexión Automática**: Conecta directamente a redes crackeadas

### 🔧 Funcionalidades

#### 1. **Escaneo de Redes**
- Escaneo rápido (15s), estándar (30s) y profundo (60s)
- Detección de canales, clientes, encriptación
- Identificación de WPS habilitado
- Análisis de actividad y beacons

#### 2. **Sistema de Scoring Inteligente**
- Evaluación automática basada en:
  - Potencia de señal (40 puntos)
  - Número de clientes (30 puntos)
  - Tipo de seguridad (20 puntos)
  - WPS habilitado (10 puntos)
- Recomendaciones automáticas de targets
- Estimación de probabilidad de éxito

#### 3. **Motor Cerbero - Generador de Wordlists Personalizadas**

Cerbero implementa **6 motores especializados** de generación de contraseñas:

- **Motor 1**: Combinaciones simples (estilo RockYou)
  - `juan`, `Juan`, `JUAN`, `juan123`
  
- **Motor 2**: Patrones complejos (estilo WiFi)
  - `Casa-Wifi`, `MiRed_2024`, `Home.Network`
  
- **Motor 3**: Leetspeak moderno
  - `2024D4n13l%`, `P3dr0@2024!`
  
- **Motor 4**: Patrones centrados en hijos
  - `2014Jiub$`, `JoaquinI2015!`
  
- **Motor 5**: Permutación de iniciales
  - `Djsm1611`, `Cdck1277kd`
  
- **Motor 6**: Mangler de frases
  - `MiCasaSegura2024!#`, `R3d$S3gur4@`

**Datos que utiliza Cerbero:**
- Nombres, apellidos, sobrenombres
- Fechas de nacimiento
- Nombres de pareja e hijos
- Mascotas
- SSID de la red objetivo (crítico)
- Palabras clave relacionadas
- Frases comunes del objetivo
- Números importantes

#### 4. **Ataques Implementados**

- **WPA/WPA2**: 
  - Captura automática de handshake (4-way)
  - Múltiples estrategias de deauth
  - Crack con diccionario
  - Soporte para handshakes manuales
  
- **WPS**: 
  - Pixie Dust attack
  - Bully brute force
  - Reaver attack
  
- **WEP**: (En desarrollo)

#### 5. **Gestión Avanzada de Wordlists**

- 🎯 Generador Cerbero (personalizado)
- 🔢 Generador numérico (PINs)
- 📥 Descarga de rockyou.txt
- ✏️ Creación manual
- 🔍 Visualización de contenido
- 🗑️ Eliminación
- 🔗 Combinación de múltiples wordlists

#### 6. **Configuración Avanzada**

- Gestión de adaptadores WiFi
- Ajuste de potencia de transmisión
- Configuración de canales
- Timeouts personalizables
- Reinicio de modo monitor
- Visualización de logs

---

## 📋 Requisitos

### Sistema Operativo
- **Linux** (Ubuntu 20.04+, Debian 11+, Kali Linux 2023+, Parrot OS, Arch Linux)
- Adaptador WiFi con soporte de modo monitor
- Acceso root (sudo)

### Adaptadores WiFi Recomendados
- **Alfa AWUS036NHA** (Atheros AR9271)
- **TP-Link TL-WN722N v1** (Atheros AR9271)
- **Alfa AWUS036ACH** (Realtek RTL8812AU)
- **Panda PAU09** (Ralink RT5572)

### Dependencias del Sistema

```bash
# Herramientas principales (requeridas)
aircrack-ng       # Suite de auditoría WiFi
reaver            # Ataque WPS
bully             # Ataque WPS alternativo
wireless-tools    # iwconfig, iwlist
net-tools         # ifconfig, route
iw                # Gestión de interfaces WiFi
macchanger        # Cambio de MAC
wpa_supplicant    # Conexión a redes
dhclient/dhcpcd   # Cliente DHCP

# Opcionales (recomendadas)
hashcat           # Cracking GPU
hcxtools          # Conversión de handshakes
```

### Dependencias de Python

```bash
python3.8+
scapy             # Manipulación de paquetes
rich              # UI mejorada (opcional)
psutil            # Información del sistema
requests          # Descarga de wordlists
```

---

## 🚀 Instalación

### Método 1: Instalación Automática (Recomendado)

```bash
# 1. Clonar repositorio desde GitHub
git clone https://github.com/syruxst/wifibreaker.git

# 2. Entrar al directorio
cd wifibreaker

# 3. Dar permisos de ejecución al instalador
chmod +x setup.sh

# 4. Ejecutar el instalador automático
sudo ./setup.sh

# 5. Verificar instalación
python3 check_dependencies.py

# 6. ¡Listo! Ejecutar WifiBreaker Pro
sudo python3 main.py
```

El script `setup.sh` instalará automáticamente:
- ✅ Todas las dependencias del sistema (aircrack-ng, reaver, bully, etc.)
- ✅ Dependencias Python (scapy, rich, psutil, requests)
- ✅ Creará la estructura de directorios necesaria
- ✅ Descargará wordlist básica (top1000.txt)

### Método 2: Instalación Manual

```bash
# 1. Clonar repositorio
git clone https://github.com/syruxst/wifibreaker.git
cd wifibreaker

# 2. Instalar dependencias del sistema
sudo apt update
sudo apt install -y \
    aircrack-ng \
    reaver \
    bully \
    wireless-tools \
    net-tools \
    iw \
    macchanger \
    python3 \
    python3-pip \
    python3-scapy \
    wpa-supplicant \
    dhcpcd5

# 3. Instalar dependencias de Python
pip3 install -r requirements.txt

# O manualmente:
pip3 install scapy psutil requests

# 4. Crear estructura de directorios
mkdir -p data/{wordlists,captures,results,logs}

# 5. Verificar instalación
python3 check_dependencies.py
```

### Verificación de Adaptador

```bash
# Listar interfaces WiFi
iwconfig

# Verificar modo monitor
sudo airmon-ng check kill
sudo airmon-ng start wlan0

# Debería aparecer wlan0mon o similar
iwconfig
```

---

## 💻 Uso

### Inicio Rápido

```bash
# Ejecutar con privilegios root
sudo python3 main.py
```

### Flujo de Trabajo Típico

```
1. [1] 🔍 Escanear Redes WiFi
   └─ Escaneo estándar (30s)

2. [4] 🤖 Selección Automática (Modo Inteligente)
   └─ El sistema elige el mejor target

3. [8] ⚙️ Configuración Avanzada
   └─ [2] 📝 Gestionar Wordlists
       └─ [1] 🎯 Generar Wordlist Personalizada (Cerbero)
           └─ Ingresar datos del objetivo:
               • Nombres: Juan Carlos
               • Apellidos: Rodriguez
               • Fecha nacimiento: 15081990
               • SSID: Casa-Rodriguez
               • Frases: mi casa segura
               └─ Genera: target_casa_rodriguez.txt (5,842 contraseñas)

4. [5] ⚡ Iniciar Ataque al Target
   └─ [1] Ataque WPA/WPA2
       └─ Captura handshake automáticamente
       └─ Crack con wordlist generada

5. [7] 🌐 Conectar a Red Crackeada
   └─ Conexión automática con contraseña recuperada
```

---

## 🎮 Menú Principal

```
╔══════════════════════════════════════════════════════╗
║     🔓 WifiBreaker Pro - Menú Principal             ║
╚══════════════════════════════════════════════════════╝

[1] 🔍 Escanear Redes WiFi
[2] 🎯 Ver Redes Detectadas
[3] ⭐ Seleccionar Target (Manual)
[4] 🤖 Selección Automática (Modo Inteligente)
[5] ⚡ Iniciar Ataque al Target
[6] 📊 Ver Detalles del Target
[7] 🌐 Conectar a Red Crackeada
[8] ⚙️  Configuración Avanzada
[0] ❌ Salir
```

---

## 🔥 Uso de Cerbero

### Ejemplo Completo

```bash
sudo python3 main.py

# Navegar a:
[8] → [2] → [1]

# Ingresar información:
═══ Información del Objetivo ═══

Nombres: Daniel María
Apellidos: Ugalde Pérez
Fecha de nacimiento: 16/11/1981
Sobrenombre: Dany
Nombre de pareja: Sandra
Nombres de hijos: Joaquín Ignacio
Nombre de mascota: Mia
SSID: kasa Baez                    ← CRÍTICO
Palabras clave: operamaq mkd
Frases a destrozar:
> mi casa segura
> kasa Baez
> (Enter vacío para terminar)
Números importantes: 38 1611

Configuración:
Longitud mínima: 8
Longitud máxima: 16
Nombre archivo: target_kasabaez

¿Generar wordlist? (S/n): s
```

### Resultado

```
🔥 Iniciando Cerbero Engine...
════════════════════════════════════════════════════════════

  [*] Palabras base encontradas: 15
      Texto: 12 | Números: 3

  [Motor 1] Combinaciones simples...
      Generadas: 1,247

  [Motor 2] Patrones complejos...
      Nuevas: 856

  [Motor 3] Leetspeak moderno...
      Nuevas: 423

  [Motor 4] Patrones de hijos...
      Nuevas: 189

  [Motor 5] Permutación de iniciales...
      Nuevas: 2,341

  [Motor 6] Mangler de frases...
      Nuevas: 1,786

  [*] Total generadas: 6,842
  [*] Después de filtrar (8-16 chars): 5,247

╔══════════════════════════════════════════════╗
║          ✓ Wordlist Generada                ║
╚══════════════════════════════════════════════╝

Archivo: data/wordlists/target_kasabaez.txt
Contraseñas: 5,247
Tamaño: 0.07 MB

Muestra (primeras 10):
  1. DanyMia38
  2. KasaBaez
  3. kasabaez
  4. k4s4b43z
  5. Sandra1611
  6. Joaquin38
  7. 2024D4ny!
  8. ugalde_mia
  9. DanielSandra
  10. MiCasaSegura2024!

¡Lista para usar en ataques!
```

---

## 📊 Ejemplos de Contraseñas Generadas

### Con SSID "MiFibra-Router"
```
MiFibra
mifibra
M1F1br4
MiFibra2024
mifibra_router
MiFibra@2024!
m1f1br4r0ut3r
```

### Con nombres "Carlos" + fecha "1990"
```
Carlos
carlos
C4rl0s
Carlos1990
carlos_1990
1990Carlos!
C4rl0s@90
```

### Patrón moderno
```
2024Juan!
2024J04n#
2025Pedro$
P3dr0@2024
```

---

## 🛠️ Configuración Avanzada

### Cambiar Potencia de Transmisión

```bash
# Desde el menú:
[8] → [5]

# O manualmente:
sudo iwconfig wlan0mon txpower 30
```

### Gestionar Adaptadores

```bash
# Desde el menú:
[8] → [1]

# Ver adaptadores disponibles
# Cambiar adaptador activo
# Probar inyección de paquetes
```

### Ver Logs

```bash
# Desde el menú:
[8] → [9]

# O manualmente:
tail -f data/logs/wifibreaker_YYYYMMDD.log
```

---

## 📁 Estructura del Proyecto

```
wifibreaker/
├── main.py                    # Punto de entrada
├── setup.sh                   # Instalador automático
├── requirements.txt           # Dependencias Python
├── check_dependencies.py      # Verificador de dependencias
│
├── core/                      # Núcleo de la aplicación
│   ├── scanner.py            # Escaneo de redes
│   ├── monitor.py            # Modo monitor
│   └── adapter.py            # Gestión de adaptadores
│
├── attacks/                   # Módulos de ataque
│   ├── wpa_attack.py         # Ataque WPA/WPA2
│   └── wps_attack.py         # Ataque WPS
│
├── cracking/                  # Motores de cracking
│   └── wordlist_generator.py # 🔥 Motor Cerbero
│
├── intelligence/              # Sistemas inteligentes
│   └── target_scoring.py     # Scoring de targets
│
├── ui/                        # Interfaz de usuario
│   ├── menu.py               # Menú principal
│   └── colors.py             # Colores y formato
│
└── data/                      # Datos de la aplicación
    ├── wordlists/            # Diccionarios
    ├── captures/             # Handshakes capturados
    ├── results/              # Contraseñas crackeadas
    └── logs/                 # Logs de la aplicación
```

---

## 🔒 Seguridad y Ética

### ⚠️ Uso Legal

**WifiBreaker Pro es una herramienta de auditoría de seguridad.**

✅ **Uso Permitido:**
- Auditorías de seguridad en tus propias redes
- Pruebas de penetración autorizadas por escrito
- Entornos educativos controlados
- Investigación de seguridad legítima

❌ **Uso Prohibido:**
- Acceso no autorizado a redes WiFi
- Interceptación de tráfico ajeno
- Robo de información
- Cualquier actividad ilegal

### 📜 Responsabilidad

El uso de esta herramienta es **responsabilidad exclusiva del usuario**. Los desarrolladores no se hacen responsables de:
- Uso indebido o ilegal
- Daños causados por mal uso
- Violaciones de leyes locales

**Conoce las leyes de tu país antes de usar esta herramienta.**

---

## 🐛 Solución de Problemas

### Error: "No wireless interfaces found"

```bash
# Verificar drivers
lsusb
dmesg | grep -i wifi

# Reinstalar drivers (ejemplo para Alfa)
sudo apt install realtek-rtl88xxau-dkms
```

### Error: "Failed to enable monitor mode"

```bash
# Matar procesos conflictivos
sudo airmon-ng check kill

# Reiniciar NetworkManager después
sudo systemctl start NetworkManager
```

### Error: "Permission denied"

```bash
# Ejecutar siempre con sudo
sudo python3 main.py
```

### Handshake no se captura

```bash
# Aumentar tiempo de captura
# Acercarse al router
# Esperar a que haya clientes conectados
# Probar diferentes estrategias de deauth
```

### Cerbero no genera contraseñas

```bash
# Verificar que ingresaste:
# - Al menos nombres o apellidos
# - SSID de la red (crítico)
# - Longitud mínima <= máxima
```

---

## 🤝 Contribuir

Las contribuciones son bienvenidas!

```bash
# 1. Fork el repositorio
# 2. Crea una rama para tu feature
git checkout -b feature/nueva-funcionalidad

# 3. Commit tus cambios
git commit -am 'Agrega nueva funcionalidad'

# 4. Push a la rama
git push origin feature/nueva-funcionalidad

# 5. Crea un Pull Request
```

---

## 📝 Changelog

### v2.0.0 (2025-01-20)
- ✨ **Nuevo**: Motor Cerbero integrado
- ✨ 6 motores de generación de wordlists
- ✨ Generador numérico de PINs
- ✨ Combinación de wordlists
- 🔧 Mejoras en captura de handshakes
- 🔧 Soporte para handshakes manuales
- 🐛 Correcciones en detección de handshakes

### v1.5.0 (2025-01-15)
- ✨ Conexión automática a redes crackeadas
- ✨ Sistema de scoring mejorado
- 🔧 Mejor gestión de wordlists
- 📊 Logs más detallados

### v1.0.0 (2025-01-10)
- 🎉 Lanzamiento inicial
- ⚡ Ataques WPA/WPA2 y WPS
- 🤖 Selección inteligente de targets
- 📈 Dashboard en tiempo real

---

## 📞 Soporte

### Reportar Bugs
- GitHub Issues: https://github.com/syruxst/wifibreaker/issues

### Documentación
- Wiki: https://github.com/syruxst/wifibreaker/wiki
- FAQ: https://github.com/syruxst/wifibreaker/wiki/FAQ

### Comunidad
- Telegram: [Próximamente]
- Discord: [Próximamente]

---

## 📄 Licencia

Este proyecto está licenciado bajo la licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

---

## 🙏 Créditos

### Herramientas Utilizadas
- **aircrack-ng** - Suite de auditoría WiFi
- **reaver/bully** - Ataques WPS
- **scapy** - Manipulación de paquetes Python

### Inspiración
- Wifite2
- Fluxion
- WiFi-Pumpkin

### Autor
**Daniel Ugalde - syruxst** - [GitHub](https://github.com/syruxst)

---

## ⭐ Agradecimientos

Si esta herramienta te fue útil, considera dar una ⭐ en GitHub!

```bash
# Sígueme en GitHub
https://github.com/syruxst
```

---

**Happy Hacking! 🔓🔥**

*Recuerda: Usa tus poderes solo para el bien.*