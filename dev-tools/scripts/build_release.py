#!/usr/bin/env python3
"""
Script para generar binarios de release de SiKIdle.

Genera:
- Ejecutable Windows (.exe) con PyInstaller
- APK Android con Buildozer
- Archivos de release listos para distribución
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Rutas del proyecto
PROJECT_ROOT = Path(__file__).parent.parent.parent
SRC_DIR = PROJECT_ROOT / "src"
RELEASES_DIR = PROJECT_ROOT / "releases"
DIST_DIR = RELEASES_DIR / "dist"

def ensure_directories():
	"""Asegura que existan los directorios necesarios."""
	RELEASES_DIR.mkdir(exist_ok=True)
	DIST_DIR.mkdir(exist_ok=True)
	logger.info(f"Directorios de release preparados: {RELEASES_DIR}")

def build_windows_exe():
	"""Construye el ejecutable Windows con PyInstaller."""
	logger.info("🔨 Construyendo ejecutable Windows...")
	
	try:
		# Comando PyInstaller
		cmd = [
			sys.executable, "-m", "PyInstaller",
			"--onefile",
			"--windowed",
			"--name", "SiKIdle-v0.1.0-windows",
			"--distpath", str(DIST_DIR),
			"--workpath", str(RELEASES_DIR / "build"),
			"--specpath", str(RELEASES_DIR),
			"--add-data", f"{SRC_DIR};src",
			"--hidden-import", "kivy",
			"--hidden-import", "kivy.deps.glew",
			"--hidden-import", "kivy.deps.sdl2",
			"--hidden-import", "kivy.deps.angle",
			str(SRC_DIR / "main.py")
		]
		
		result = subprocess.run(cmd, cwd=PROJECT_ROOT, capture_output=True, text=True)
		
		if result.returncode == 0:
			logger.info("✅ Ejecutable Windows creado exitosamente")
			exe_path = DIST_DIR / "SiKIdle-v0.1.0-windows.exe"
			if exe_path.exists():
				size_mb = exe_path.stat().st_size / (1024 * 1024)
				logger.info(f"📦 Tamaño del ejecutable: {size_mb:.1f} MB")
			return True
		else:
			logger.error(f"❌ Error construyendo ejecutable: {result.stderr}")
			return False
			
	except Exception as e:
		logger.error(f"❌ Excepción construyendo ejecutable: {e}")
		return False

def build_android_apk():
	"""Construye el APK Android con Buildozer."""
	logger.info("🔨 Construyendo APK Android...")
	
	try:
		# Verificar que buildozer.spec existe
		buildozer_spec = PROJECT_ROOT / "buildozer.spec"
		if not buildozer_spec.exists():
			logger.error("❌ buildozer.spec no encontrado")
			return False
		
		# Comando Buildozer
		cmd = ["buildozer", "android", "debug"]
		
		result = subprocess.run(cmd, cwd=PROJECT_ROOT, capture_output=True, text=True)
		
		if result.returncode == 0:
			logger.info("✅ APK Android creado exitosamente")
			
			# Mover APK a directorio de distribución
			bin_dir = PROJECT_ROOT / "bin"
			if bin_dir.exists():
				for apk_file in bin_dir.glob("*.apk"):
					new_name = f"SiKIdle-v0.1.0-android-debug.apk"
					dest_path = DIST_DIR / new_name
					shutil.copy2(apk_file, dest_path)
					size_mb = dest_path.stat().st_size / (1024 * 1024)
					logger.info(f"📦 APK copiado: {new_name} ({size_mb:.1f} MB)")
			return True
		else:
			logger.warning(f"⚠️ Buildozer terminó con código {result.returncode}")
			logger.info("ℹ️ Esto es normal si no tienes Android SDK configurado")
			return False
			
	except FileNotFoundError:
		logger.warning("⚠️ Buildozer no encontrado - saltando build Android")
		logger.info("ℹ️ Instala buildozer para generar APKs: pip install buildozer")
		return False
	except Exception as e:
		logger.error(f"❌ Excepción construyendo APK: {e}")
		return False

def create_release_info():
	"""Crea archivo de información de release."""
	logger.info("📝 Creando información de release...")
	
	info_content = """# SiKIdle Pre-Alpha v0.1.0 - Release Package

## 📦 Contenido del Release

### Windows
- `SiKIdle-v0.1.0-windows.exe` - Ejecutable standalone para Windows
  - No requiere instalación
  - Guarda datos en: `%APPDATA%\\SiKIdle\\`
  - Requisitos: Windows 10+ (64-bit)

### Android
- `SiKIdle-v0.1.0-android-debug.apk` - APK para Android
  - Instalar con "Fuentes desconocidas" habilitado
  - Guarda datos en almacenamiento interno de la app
  - Requisitos: Android 5.0+ (API 21+)

## 🚀 Instalación

### Windows
1. Descargar `SiKIdle-v0.1.0-windows.exe`
2. Ejecutar directamente (no requiere instalación)
3. El juego creará automáticamente los directorios de guardado

### Android
1. Habilitar "Fuentes desconocidas" en Configuración > Seguridad
2. Descargar `SiKIdle-v0.1.0-android-debug.apk`
3. Tocar el archivo APK para instalar
4. Abrir SiKIdle desde el menú de aplicaciones

## 🎮 Primeros Pasos

1. **Tutorial automático** - El juego te guiará en los primeros pasos
2. **Haz clic** en el botón principal para generar monedas
3. **Compra edificios** para generar monedas automáticamente
4. **Desbloquea pestañas** según progreses
5. **Prestigio** cuando tengas suficientes monedas para cristales

## 🐛 Reportar Issues

Si encuentras problemas:
1. Crear issue en: https://github.com/Kavalieri/SiKIdle/issues
2. Incluir: OS, versión, pasos para reproducir
3. Adjuntar logs si es posible

## 📊 Métricas Esperadas

- **Startup:** <3 segundos
- **Performance:** 60fps estables
- **Memory:** <100MB RAM
- **Storage:** ~50MB datos de usuario

---

*© Clan SiK - 2025 | Pre-Alpha v0.1.0*
"""
	
	info_path = DIST_DIR / "README.txt"
	with open(info_path, 'w', encoding='utf-8') as f:
		f.write(info_content)
	
	logger.info(f"✅ Información de release creada: {info_path}")

def main():
	"""Función principal del script de build."""
	logger.info("🚀 Iniciando build de release SiKIdle v0.1.0...")
	
	# Preparar directorios
	ensure_directories()
	
	# Builds
	windows_success = build_windows_exe()
	android_success = build_android_apk()
	
	# Información de release
	create_release_info()
	
	# Resumen
	logger.info("\n" + "="*50)
	logger.info("📋 RESUMEN DEL BUILD")
	logger.info("="*50)
	logger.info(f"✅ Windows EXE: {'Exitoso' if windows_success else 'Falló'}")
	logger.info(f"{'✅' if android_success else '⚠️'} Android APK: {'Exitoso' if android_success else 'Saltado/Falló'}")
	logger.info(f"📁 Archivos en: {DIST_DIR}")
	
	if windows_success or android_success:
		logger.info("\n🎉 Build completado! Archivos listos para distribución.")
		
		# Listar archivos generados
		logger.info("\n📦 Archivos generados:")
		for file in DIST_DIR.iterdir():
			if file.is_file():
				size_mb = file.stat().st_size / (1024 * 1024)
				logger.info(f"  - {file.name} ({size_mb:.1f} MB)")
	else:
		logger.warning("\n⚠️ No se generaron binarios. Verifica las dependencias.")
	
	return windows_success or android_success

if __name__ == "__main__":
	success = main()
	sys.exit(0 if success else 1)