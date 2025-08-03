# SiKIdle

Un videojuego tipo *idle clicker 2D* desarrollado en **Python 3.11+** utilizando **Kivy**, **orientado principalmente a dispositivos móviles Android** con soporte para Windows. Optimizado para **pantallas verticales**.

## 🎮 Descripción

SiKIdle es un juego idle clicker diseñado especialmente para móviles que permite a los jugadores progresar automáticamente mientras realizan toques estratégicos para mejorar su progreso. El juego está optimizado para pantallas táctiles verticales y funciona nativamente en Android.

## 📱 Plataformas Objetivo

### Primaria
- **Android** (API 21+) - Plataforma principal
- Orientación: **Portrait (vertical)**
- Pantallas táctiles optimizadas

### Secundaria  
- **Windows** - Para desarrollo y testing
- Simula resoluciones móviles (360x640)

## 🛠️ Tecnologías

- **Python 3.11+**
- **Kivy 2.3.0+** (sin archivos .kv) - Framework UI multiplataforma
- **Buildozer** - Compilación para Android
- **SQLite** - Persistencia de datos local
- **Ruff** - Linting y formateo
- **MyPy** - Verificación de tipos

## 📱 Configuración Móvil

### Resoluciones Objetivo
- **Android**: Adaptativo (fullscreen portrait)
- **Windows**: 360x640px (simulación móvil)

### Optimizaciones Móviles
- Interfaz táctil optimizada
- Botones de tamaño adecuado (mínimo 44dp)
- Layout vertical (portrait)
- Fuentes escalables (sp)
- Padding adaptativo para diferentes densidades

## 📂 Estructura del Proyecto

```
SiKIdle/
├── src/
│   ├── main.py          # Punto de entrada
│   ├── core/            # Lógica principal del juego
│   ├── ui/              # Widgets y estructura visual
│   ├── utils/           # Utilidades, paths, helpers, db
│   └── assets/          # Imágenes, sonidos, fuentes
├── docs/
│   ├── resumen/
│   └── checklist/
├── tmp/                 # Archivos temporales
├── ARCHIVO/             # Elementos deprecated/backups
└── .github/
```

## 🚀 Instalación y Ejecución

### Requisitos Previos

- Python 3.11 o superior
- pip (gestor de paquetes de Python)
- Para Android: Android SDK, NDK (opcional, buildozer lo gestiona)

### Instalación para Desarrollo

1. Clona el repositorio:
```bash
git clone https://github.com/Kavalieri/SiKIdle.git
cd SiKIdle
```

2. Instala las dependencias:
```bash
pip install -r requirements.txt
```

### Ejecución

#### Modo Desktop (simulación móvil)
```bash
python src/main.py
```

#### Compilación para Android
```bash
# Instalar buildozer si no está instalado
pip install buildozer

# Compilar APK debug
buildozer android debug

# La APK se generará en bin/
```

### Desarrollo Rápido
```bash
# Usar el script helper
python dev-tools/scripts/mobile_dev.py test    # Ejecutar en modo móvil
python dev-tools/scripts/mobile_dev.py build   # Compilar para Android
```

## 🎯 Estado del Desarrollo

**Fase actual: Esqueleto Base** ✅

El proyecto actualmente cuenta con:
- Estructura de directorios establecida
- Ventana básica de Kivy funcional
- Sistema de rutas multiplataforma
- Configuración de herramientas de desarrollo

## ✅ Estado de Implementación

### Completado ✅
- ✅ Estructura de directorios establecida
- ✅ Ventana básica de Kivy funcional **optimizada para móviles**
- ✅ **Configuración portrait (vertical) para Android**
- ✅ **Resolución adaptativa móvil (360x640 en desktop)**
- ✅ **Interfaz táctil con botones optimizados**
- ✅ Sistema de rutas multiplataforma básico
- ✅ **Configuración buildozer para Android**
- ✅ Configuración de herramientas de desarrollo (ruff, mypy)
- ✅ Entorno virtual configurado
- ✅ Dependencias instaladas correctamente
- ✅ El juego se ejecuta sin errores

### Próximos Pasos ⏳
- ⏳ Generar iconos e imágenes de splash para Android
- ⏳ Implementar sistema completo de base de datos SQLite
- ⏳ Desarrollar lógica básica de clicker táctil
- ⏳ Crear sistema de recursos y mejoras
- ⏳ Implementar guardado automático
- ⏳ Optimizar rendimiento para dispositivos móviles
- ⏳ Testing en dispositivos Android reales

### Configuración Móvil Específica ✅
- ✅ **Orientación portrait forzada**
- ✅ **Ventana FIJA no redimensionable (360x640 en desktop)**
- ✅ **Posición consistente para desarrollo**
- ✅ **Fuentes escalables (sp units)**
- ✅ **Padding optimizado para touch**
- ✅ **Buildozer configurado para Android API 21-34**
- ✅ **Simulación móvil perfecta en desktop**

## 🤝 Contribución

Consulta `CONTRIBUTING.md` para más información sobre cómo contribuir al proyecto.

## 📄 Licencia

Este proyecto está bajo la Licencia MIT.

---

© Clan SiK - 2025
