#!/usr/bin/env python3
"""Script de desarrollo para SiKIdle móvil.

Este script facilita las tareas comunes de desarrollo para la versión móvil
del juego, incluyendo testing, compilación para Android, etc.
"""

import os
import subprocess
import sys
from pathlib import Path


def run_command(cmd: str, description: str) -> bool:
	"""Ejecuta un comando y muestra el resultado."""
	print(f"\n🔄 {description}...")
	print(f"Ejecutando: {cmd}")
	
	result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
	
	if result.returncode == 0:
		print(f"✅ {description} completado exitosamente")
		if result.stdout:
			print(result.stdout)
		return True
	else:
		print(f"❌ Error en {description}")
		if result.stderr:
			print(f"Error: {result.stderr}")
		return False


def test_mobile_simulation():
	"""Ejecuta el juego en modo simulación móvil."""
	print("🎮 Iniciando SiKIdle en modo simulación móvil...")
	os.chdir(Path(__file__).parent.parent.parent)
	
	# Ejecutar el juego
	cmd = "python src/main.py"
	return run_command(cmd, "Ejecución en modo móvil")


def build_android_debug():
	"""Compila una APK de debug para Android."""
	print("📱 Iniciando compilación para Android (debug)...")
	os.chdir(Path(__file__).parent.parent.parent)
	
	# Verificar que buildozer esté instalado
	if not run_command("buildozer --version", "Verificación de buildozer"):
		print("❌ Buildozer no está instalado. Instálalo con: pip install buildozer")
		return False
	
	# Compilar APK debug
	return run_command("buildozer android debug", "Compilación Android debug")


def clean_build():
	"""Limpia los archivos de compilación."""
	print("🧹 Limpiando archivos de compilación...")
	os.chdir(Path(__file__).parent.parent.parent)
	
	commands = [
		"buildozer android clean",
		"rm -rf .buildozer",
		"rm -rf bin"
	]
	
	success = True
	for cmd in commands:
		if not run_command(cmd, f"Limpieza: {cmd}"):
			success = False
	
	return success


def setup_android_dev():
	"""Configura el entorno de desarrollo para Android."""
	print("⚙️ Configurando entorno de desarrollo Android...")
	
	# Verificar dependencias
	dependencies = [
		("python", "Python"),
		("pip", "pip"),
		("git", "Git")
	]
	
	for cmd, name in dependencies:
		if not run_command(f"{cmd} --version", f"Verificación de {name}"):
			print(f"❌ {name} no está disponible")
			return False
	
	# Instalar dependencias Python
	cmd = "pip install buildozer cython"
	return run_command(cmd, "Instalación de dependencias Android")


def main():
	"""Función principal del script."""
	if len(sys.argv) < 2:
		print("""
🎮 SiKIdle - Script de Desarrollo Móvil

Uso: python mobile_dev.py [comando]

Comandos disponibles:
test          - Ejecutar en modo simulación móvil
build         - Compilar APK debug para Android  
clean         - Limpiar archivos de compilación
setup         - Configurar entorno de desarrollo Android

Ejemplos:
python mobile_dev.py test
python mobile_dev.py build
		""")
		return
	
	command = sys.argv[1].lower()
	
	if command == "test":
		test_mobile_simulation()
	elif command == "build":
		build_android_debug()
	elif command == "clean":
		clean_build()
	elif command == "setup":
		setup_android_dev()
	else:
		print(f"❌ Comando desconocido: {command}")
		main()


if __name__ == "__main__":
	main()
