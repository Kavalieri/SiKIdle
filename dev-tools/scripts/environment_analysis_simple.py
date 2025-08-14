#!/usr/bin/env python3
"""
Script de Análisis del Entorno - SiKIdle Pre-Alfa Testing (Versión Simple).
"""

import sys
import os
import subprocess
import importlib
from pathlib import Path


def main():
	"""Análisis simple del entorno."""
	print("Iniciando analisis del entorno...")
	
	project_root = Path(__file__).parent.parent.parent
	src_path = project_root / "src"
	issues = []
	
	# 1. Verificar Python
	print("  Verificando Python...")
	version = sys.version_info
	if version < (3, 11):
		issues.append(f"CRITICO: Python {version.major}.{version.minor} < 3.11")
	else:
		print(f"    OK: Python {version.major}.{version.minor}.{version.micro}")
	
	# 2. Verificar Kivy
	print("  Verificando Kivy...")
	try:
		import kivy
		print(f"    OK: Kivy {kivy.__version__}")
	except ImportError:
		issues.append("CRITICO: Kivy no instalado")
	
	# 3. Verificar estructura
	print("  Verificando estructura...")
	critical_files = [
		"src/main.py",
		"src/core/game.py",
		"src/utils/save.py"
	]
	
	for file_path in critical_files:
		full_path = project_root / file_path
		if not full_path.exists():
			issues.append(f"CRITICO: Falta {file_path}")
		else:
			print(f"    OK: {file_path}")
	
	# 4. Verificar importaciones principales
	print("  Verificando importaciones...")
	if src_path.exists():
		sys.path.insert(0, str(src_path))
		
		modules = [
			"core.game",
			"core.achievements_idle", 
			"core.prestige_simple",
			"utils.save"
		]
		
		for module in modules:
			try:
				importlib.import_module(module)
				print(f"    OK: {module}")
			except ImportError as e:
				issues.append(f"ERROR: No se puede importar {module}: {e}")
	
	# 5. Probar ejecución básica
	print("  Probando inicialización básica...")
	try:
		from core.game import get_game_state
		game_state = get_game_state()
		print("    OK: GameState se inicializa")
	except Exception as e:
		issues.append(f"ERROR: GameState falla: {e}")
	
	# Resumen
	print(f"\nAnalisis completado:")
	if issues:
		print(f"  {len(issues)} problemas encontrados:")
		for issue in issues:
			print(f"    - {issue}")
		return 1
	else:
		print("  Sin problemas criticos detectados")
		return 0


if __name__ == "__main__":
	sys.exit(main())