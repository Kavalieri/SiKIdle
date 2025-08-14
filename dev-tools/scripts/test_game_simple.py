#!/usr/bin/env python3
"""
Script simplificado para probar SiKIdle sin problemas de encoding.
"""

import sys
import os
from pathlib import Path

# Configurar paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
SRC_PATH = PROJECT_ROOT / "src"

def test_basic_imports():
	"""Probar importaciones básicas del proyecto."""
	sys.path.insert(0, str(SRC_PATH))
	
	print("Probando imports básicos...")
	
	try:
		from core.game import GameState
		print("OK - GameState importado")
		
		from core.prestige_simple import PrestigeManager
		print("OK - PrestigeManager importado")
		
		from core.achievements_idle import IdleAchievementManager
		print("OK - IdleAchievementManager importado")
		
		from utils.db_fixed import DatabaseManager
		print("OK - DatabaseManager importado")
		
		return True
		
	except Exception as e:
		print(f"ERROR en imports: {e}")
		return False

def test_game_basic():
	"""Probar funcionalidad básica del juego."""
	try:
		from core.game import GameState
		
		print("Inicializando GameState...")
		game = GameState()
		
		print(f"Coins iniciales: {game.coins}")
		
		# Probar click
		initial_coins = game.coins
		game.click()
		after_click = game.coins
		
		print(f"Coins después de click: {after_click}")
		
		if after_click > initial_coins:
			print("OK - Click funciona")
			return True
		else:
			print("ERROR - Click no genera coins")
			return False
			
	except Exception as e:
		print(f"ERROR en GameState: {e}")
		return False

def main():
	print("=== TEST SIMPLE SIKIDLE ===")
	
	# Test imports
	imports_ok = test_basic_imports()
	
	if not imports_ok:
		print("FALLO: Imports no funcionan")
		return False
	
	# Test game
	game_ok = test_game_basic()
	
	if not game_ok:
		print("FALLO: GameState no funciona")
		return False
	
	print("=== TODOS LOS TESTS PASARON ===")
	return True

if __name__ == "__main__":
	success = main()
	sys.exit(0 if success else 1)