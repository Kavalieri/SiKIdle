# 📦 SiKIdle - Releases & Packaging

Este directorio contiene toda la infraestructura necesaria para generar releases de SiKIdle en múltiples plataformas.

## 🏗️ Estructura

```
releases/
├── README.md                    # Este archivo
├── packaging/                   # Scripts de empaquetado
│   ├── android/                # Empaquetado para Android
│   │   ├── buildozer.spec      # Configuración de Buildozer
│   │   ├── Dockerfile          # Entorno Docker para build
│   │   └── build_android.bat   # Script de build automatizado
│   └── windows/                # Empaquetado para Windows
│       ├── sikidle.spec        # Configuración de PyInstaller
│       ├── build_windows.bat   # Script de build automatizado
│       └── venv/               # Entorno virtual (generado)
└── dist/                       # Archivos generados (ignorado por git)
```

## 🚀 Cómo generar releases

### Android APK
```bash
cd releases/packaging/android
./build_android.bat
```

### Windows EXE
```bash
cd releases/packaging/windows
./build_windows.bat
```

## 📋 Requisitos

- **Para Android:** Docker Desktop
- **Para Windows:** Python 3.11+, entorno virtual

## 🎯 Stack Tecnológico

- **Python:** 3.11.13
- **Kivy:** 2.3.1
- **Android:** Buildozer + Docker + JDK 17
- **Windows:** PyInstaller 6.3.0 + UPX

## 📝 Notas

- Los archivos generados se almacenan en `dist/` (ignorado por git)
- Cada release incluye tanto APK como EXE
- Los builds son reproducibles y automatizados
