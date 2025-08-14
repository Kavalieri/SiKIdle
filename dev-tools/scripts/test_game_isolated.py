#!/usr/bin/env python3
"""
Script para probar SiKIdle en entorno aislado con logging detallado.
Detecta problemas en tiempo real y genera reportes de errores.
"""

import sys
import os
import logging
import subprocess
import traceback
from pathlib import Path
from datetime import datetime

# Configurar paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
SRC_PATH = PROJECT_ROOT / "src"
LOGS_PATH = PROJECT_ROOT / "tmp"

# Crear directorio de logs si no existe
LOGS_PATH.mkdir(exist_ok=True)

def setup_logging():
	"""Configurar logging detallado para capturar todos los errores."""
	timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
	log_file = LOGS_PATH / f"game_test_{timestamp}.log"
	
	logging.basicConfig(
		level=logging.DEBUG,
		format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
		handlers=[
			logging.FileHandler(log_file, encoding='utf-8'),
			logging.StreamHandler(sys.stdout)
		]
	)
	
	return log_file

def check_venv():
	"""Verificar si estamos en un entorno virtual."""
	in_venv = hasattr(sys, 'real_prefix') or (
		hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
	)
	
	logging.info(f"Python executable: {sys.executable}")
	logging.info(f"En entorno virtual: {in_venv}")
	logging.info(f"Python version: {sys.version}")
	
	return in_venv

def check_dependencies():
	"""Verificar dependencias críticas."""
	critical_deps = ['kivy', 'sqlite3']
	missing_deps = []
	
	for dep in critical_deps:
		try:
			__import__(dep)
			logging.info(f"✅ {dep} disponible")
		except ImportError as e:
			logging.error(f"❌ {dep} no disponible: {e}")
			missing_deps.append(dep)
	
	return missing_deps

def test_imports():
	"""Probar importaciones del proyecto."""
	sys.path.insert(0, str(SRC_PATH))
	
	test_modules = [
		'core.game',
		'core.prestige_simple',
		'core.achievements_idle',
		'core.premium_shop',
		'core.engagement_system',
		'utils.db_fixed',
		'utils.performance',
		'ui.main_screen'
	]
	
	failed_imports = []
	
	for module in test_modules:
		try:
			__import__(module)
			logging.info(f"✅ Import {module} exitoso")
		except Exception as e:
			logging.error(f"❌ Import {module} falló: {e}")
			logging.error(traceback.format_exc())
			failed_imports.append((module, str(e)))
	
	return failed_imports

def test_game_initialization():
	"""Probar inicialización básica del juego."""
	try:
		from core.game import GameState
		
		logging.info("Inicializando GameState...")
		game = GameState()
		
		# Verificar atributos críticos
		critical_attrs = ['coins', 'buildings', 'prestige_manager', 'achievement_manager']
		for attr in critical_attrs:
			if hasattr(game, attr):
				logging.info(f"✅ {attr} presente")
			else:
				logging.error(f"❌ {attr} faltante")
		
		# Probar operaciones básicas
		logging.info("Probando click...")
		initial_coins = game.coins
		game.click()
		after_click = game.coins
		logging.info(f"Coins antes: {initial_coins}, después: {after_click}")
		
		if after_click > initial_coins:
			logging.info("✅ Click funciona correctamente")
		else:
			logging.error("❌ Click no genera coins")
		
		return True
		
	except Exception as e:
		logging.error(f"❌ Error en inicialización del juego: {e}")
		logging.error(traceback.format_exc())
		return False

def test_ui_basic():
	"""Probar inicialización básica de UI."""
	try:
		# Configurar Kivy para testing
		os.environ['KIVY_NO_CONSOLELOG'] = '1'
		
		from kivy.app import App
		from ui.main_screen import MainScreen
		
		logging.info("Probando inicialización de UI...")
		
		# Crear instancia básica sin ejecutar
		screen = MainScreen()
		logging.info("✅ MainScreen se puede instanciar")
		
		return True
		
	except Exception as e:
		logging.error(f"❌ Error en UI: {e}")
		logging.error(traceback.format_exc())
		return False

def run_isolated_test():
	"""Ejecutar test completo en entorno aislado."""
	log_file = setup_logging()
	logging.info("=== INICIO TEST AISLADO SIKIDLE ===")
	
	# Verificar entorno
	logging.info("1. Verificando entorno...")
	in_venv = check_venv()
	
	# Verificar dependencias
	logging.info("2. Verificando dependencias...")
	missing_deps = check_dependencies()
	
	if missing_deps:
		logging.error(f"Dependencias faltantes: {missing_deps}")
		return False
	
	# Probar imports
	logging.info("3. Probando imports...")
	failed_imports = test_imports()
	
	if failed_imports:
		logging.error("Imports fallidos:")
		for module, error in failed_imports:
			logging.error(f"  - {module}: {error}")
	
	# Probar inicialización del juego
	logging.info("4. Probando inicialización del juego...")
	game_ok = test_game_initialization()
	
	# Probar UI básica
	logging.info("5. Probando UI básica...")
	ui_ok = test_ui_basic()
	
	# Resumen
	logging.info("=== RESUMEN TEST ===")
	logging.info(f"Entorno virtual: {in_venv}")
	logging.info(f"Dependencias: {'✅' if not missing_deps else '❌'}")
	logging.info(f"Imports: {'✅' if not failed_imports else '❌'}")
	logging.info(f"GameState: {'✅' if game_ok else '❌'}")
	logging.info(f"UI básica: {'✅' if ui_ok else '❌'}")
	
	success = not missing_deps and not failed_imports and game_ok and ui_ok
	logging.info(f"RESULTADO GENERAL: {'✅ ÉXITO' if success else '❌ FALLOS DETECTADOS'}")
	logging.info(f"Log guardado en: {log_file}")
	
	return success

if __name__ == "__main__":
	success = run_isolated_test()
	sys.exit(0 if success else 1)