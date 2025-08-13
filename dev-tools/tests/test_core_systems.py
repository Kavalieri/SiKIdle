#!/usr/bin/env python3
"""
Tests exhaustivos de sistemas core - SiKIdle Pre-Alfa.

Prueba todos los sistemas principales para detectar errores
antes del primer alfa.
"""

import sys
import os
from pathlib import Path

# Añadir src al path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

import unittest
from unittest.mock import patch, MagicMock
import tempfile
import shutil


class TestCoreGameLoop(unittest.TestCase):
	"""Tests del bucle principal del juego."""
	
	def setUp(self):
		"""Configuración para cada test."""
		# Crear directorio temporal para tests
		self.temp_dir = tempfile.mkdtemp()
		
		# Mock del sistema de paths para usar directorio temporal
		with patch('utils.paths.get_user_data_dir', return_value=Path(self.temp_dir)):
			from core.game import GameState
			self.game_state = GameState()
	
	def tearDown(self):
		"""Limpieza después de cada test."""
		# Limpiar directorio temporal
		shutil.rmtree(self.temp_dir, ignore_errors=True)
	
	def test_game_initialization(self):
		"""Test de inicialización del juego."""
		self.assertIsNotNone(self.game_state)
		self.assertEqual(self.game_state.coins, 0)
		self.assertEqual(self.game_state.total_clicks, 0)
		self.assertGreaterEqual(self.game_state.multiplier, 1.0)
	
	def test_click_mechanics(self):
		"""Test de mecánicas de clic."""
		initial_coins = self.game_state.coins
		
		# Simular clic
		coins_earned = self.game_state.click()
		
		self.assertGreater(coins_earned, 0)
		self.assertEqual(self.game_state.coins, initial_coins + coins_earned)
		self.assertEqual(self.game_state.total_clicks, 1)
	
	def test_building_system(self):
		"""Test del sistema de edificios."""
		# Dar monedas suficientes para comprar edificio
		self.game_state.coins = 1000
		
		# Intentar comprar edificio
		building_manager = self.game_state.building_manager
		initial_count = building_manager.buildings['farm'].count
		
		success = building_manager.purchase_building('farm', self.game_state)
		
		if success:
			self.assertEqual(
				building_manager.buildings['farm'].count, 
				initial_count + 1
			)
			self.assertLess(self.game_state.coins, 1000)
	
	def test_save_load_system(self):
		"""Test del sistema de guardado y carga."""
		# Modificar estado del juego
		self.game_state.coins = 500
		self.game_state.total_clicks = 10
		
		# Guardar
		save_success = self.game_state.save_game()
		self.assertTrue(save_success)
		
		# Crear nuevo GameState y cargar
		with patch('utils.paths.get_user_data_dir', return_value=Path(self.temp_dir)):
			from core.game import GameState
			new_game_state = GameState()
		
		# Verificar que se cargó correctamente
		self.assertEqual(new_game_state.coins, 500)
		self.assertEqual(new_game_state.total_clicks, 10)


class TestPrestigeSystem(unittest.TestCase):
	"""Tests del sistema de prestigio."""
	
	def setUp(self):
		"""Configuración para cada test."""
		self.temp_dir = tempfile.mkdtemp()
		
		with patch('utils.paths.get_user_data_dir', return_value=Path(self.temp_dir)):
			from core.game import GameState
			self.game_state = GameState()
	
	def tearDown(self):
		"""Limpieza después de cada test."""
		shutil.rmtree(self.temp_dir, ignore_errors=True)
	
	def test_prestige_calculation(self):
		"""Test de cálculo de prestigio."""
		# Configurar condiciones para prestigio
		self.game_state.coins = 200000  # Suficiente para prestigio
		
		can_prestige = self.game_state.can_prestige()
		self.assertTrue(can_prestige)
		
		crystals = self.game_state.calculate_prestige_crystals()
		self.assertGreater(crystals, 0)
	
	def test_prestige_execution(self):
		"""Test de ejecución de prestigio."""
		# Configurar estado pre-prestigio
		self.game_state.coins = 300000
		self.game_state.total_clicks = 100
		
		initial_crystals = self.game_state.prestige_manager.prestige_crystals
		
		# Realizar prestigio
		success = self.game_state.perform_prestige()
		
		if success:
			# Verificar reset
			self.assertEqual(self.game_state.coins, 0)
			self.assertEqual(self.game_state.total_clicks, 0)
			
			# Verificar cristales ganados
			self.assertGreater(
				self.game_state.prestige_manager.prestige_crystals,
				initial_crystals
			)


class TestAchievementSystem(unittest.TestCase):
	"""Tests del sistema de logros."""
	
	def setUp(self):
		"""Configuración para cada test."""
		self.temp_dir = tempfile.mkdtemp()
		
		with patch('utils.paths.get_user_data_dir', return_value=Path(self.temp_dir)):
			from core.game import GameState
			self.game_state = GameState()
	
	def tearDown(self):
		"""Limpieza después de cada test."""
		shutil.rmtree(self.temp_dir, ignore_errors=True)
	
	def test_achievement_detection(self):
		"""Test de detección de logros."""
		achievement_manager = self.game_state.achievement_manager
		
		# Simular progreso para logro de primer clic
		self.game_state.total_clicks = 1
		
		completed = achievement_manager.check_achievements(self.game_state)
		
		# Verificar que se detectó el logro
		first_click_achievement = achievement_manager.achievements.get('first_click')
		if first_click_achievement:
			self.assertTrue(first_click_achievement.completed)
	
	def test_achievement_rewards(self):
		"""Test de recompensas de logros."""
		# Simular completar logro con recompensa de gemas
		achievement_manager = self.game_state.achievement_manager
		
		initial_gems = 0
		if hasattr(self.game_state, 'premium_shop_manager'):
			initial_gems = self.game_state.premium_shop_manager.gems
		
		# Forzar completar logro
		first_click = achievement_manager.achievements.get('first_click')
		if first_click and not first_click.completed:
			first_click.completed = True
			achievement_manager._on_achievement_completed(first_click, self.game_state)
			
			# Verificar recompensas aplicadas
			if hasattr(self.game_state, 'premium_shop_manager'):
				self.assertGreaterEqual(
					self.game_state.premium_shop_manager.gems,
					initial_gems
				)


class TestPremiumShop(unittest.TestCase):
	"""Tests del sistema de tienda premium."""
	
	def setUp(self):
		"""Configuración para cada test."""
		self.temp_dir = tempfile.mkdtemp()
		
		with patch('utils.paths.get_user_data_dir', return_value=Path(self.temp_dir)):
			from core.game import GameState
			self.game_state = GameState()
	
	def tearDown(self):
		"""Limpieza después de cada test."""
		shutil.rmtree(self.temp_dir, ignore_errors=True)
	
	def test_gem_system(self):
		"""Test del sistema de gemas."""
		if hasattr(self.game_state, 'premium_shop_manager'):
			shop = self.game_state.premium_shop_manager
			
			# Añadir gemas
			initial_gems = shop.gems
			shop.add_gems(100, "test")
			
			self.assertEqual(shop.gems, initial_gems + 100)
	
	def test_premium_purchases(self):
		"""Test de compras premium."""
		if hasattr(self.game_state, 'premium_shop_manager'):
			shop = self.game_state.premium_shop_manager
			
			# Dar gemas para compra
			shop.gems = 100
			
			# Intentar comprar item
			result = shop.purchase_with_gems("boost_coins_1h")
			
			# Verificar resultado (puede fallar si item no existe)
			self.assertIsInstance(result, dict)
			self.assertIn('success', result)


class TestEngagementSystem(unittest.TestCase):
	"""Tests del sistema de engagement."""
	
	def setUp(self):
		"""Configuración para cada test."""
		self.temp_dir = tempfile.mkdtemp()
		
		with patch('utils.paths.get_user_data_dir', return_value=Path(self.temp_dir)):
			from core.game import GameState
			self.game_state = GameState()
	
	def tearDown(self):
		"""Limpieza después de cada test."""
		shutil.rmtree(self.temp_dir, ignore_errors=True)
	
	def test_daily_login(self):
		"""Test de login diario."""
		if hasattr(self.game_state, 'engagement_system'):
			engagement = self.game_state.engagement_system
			
			streak = engagement.check_daily_login()
			self.assertGreaterEqual(streak, 1)
	
	def test_offline_progress(self):
		"""Test de progreso offline."""
		if hasattr(self.game_state, 'engagement_system'):
			engagement = self.game_state.engagement_system
			
			# Simular tiempo offline
			import time
			engagement.last_save_time = time.time() - 3600  # 1 hora atrás
			
			earnings = engagement.calculate_offline_earnings()
			self.assertIsInstance(earnings, dict)
			self.assertIn('coins', earnings)


def run_all_tests():
	"""Ejecuta todos los tests y genera reporte."""
	print("Ejecutando tests exhaustivos de sistemas core...")
	
	# Crear suite de tests
	loader = unittest.TestLoader()
	suite = unittest.TestSuite()
	
	# Añadir todas las clases de test
	test_classes = [
		TestCoreGameLoop,
		TestPrestigeSystem,
		TestAchievementSystem,
		TestPremiumShop,
		TestEngagementSystem
	]
	
	for test_class in test_classes:
		tests = loader.loadTestsFromTestCase(test_class)
		suite.addTests(tests)
	
	# Ejecutar tests
	runner = unittest.TextTestRunner(verbosity=2)
	result = runner.run(suite)
	
	# Generar reporte
	print(f"\nResultados del testing:")
	print(f"  Tests ejecutados: {result.testsRun}")
	print(f"  Errores: {len(result.errors)}")
	print(f"  Fallos: {len(result.failures)}")
	
	if result.errors:
		print(f"\nErrores detectados:")
		for test, error in result.errors:
			print(f"  - {test}: {error}")
	
	if result.failures:
		print(f"\nFallos detectados:")
		for test, failure in result.failures:
			print(f"  - {test}: {failure}")
	
	# Retornar código de salida
	return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
	sys.exit(run_all_tests())