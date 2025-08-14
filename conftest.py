"""
Configuración de pytest para SiKIdle.

Configura el path y fixtures comunes para todos los tests.
"""

import sys
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

# Configurar path para imports
src_path = Path(__file__).parent / "src"
if str(src_path) not in sys.path:
	sys.path.insert(0, str(src_path))


@pytest.fixture
def isolated_db():
	"""
	Crea una base de datos completamente aislada para cada test.
	Patchea automáticamente utils.db.get_user_data_dir() para usar directorio temporal.
	"""
	with tempfile.TemporaryDirectory() as temp_dir:
		temp_path = Path(temp_dir)

		# Patchear TODAS las posibles referencias a get_user_data_dir
		patcher = patch("utils.db.get_user_data_dir", return_value=temp_path)
		patcher.start()

		yield temp_path

		patcher.stop()


@pytest.fixture
def clean_game_state(isolated_db):
	"""
	Crea un GameState completamente limpio y aislado.
	Garantiza que no hay interference entre tests.
	"""
	# Limpiar cualquier estado global antes de crear GameState
	import gc

	gc.collect()

	# Crear GameState con base de datos aislada
	from core.game import GameState

	game_state = GameState()

	yield game_state

	# Limpiar después del test
	if hasattr(game_state, "stop_game"):
		try:
			game_state.stop_game()
		except:
			pass

	# Forzar limpieza de memoria
	del game_state
	gc.collect()


@pytest.fixture
def temp_db():
	"""Crea una base de datos temporal para tests."""
	with tempfile.TemporaryDirectory() as temp_dir:
		yield Path(temp_dir)


@pytest.fixture
def mock_game_state():
	"""Crea un estado de juego mockeado básico."""
	mock_state = Mock()
	mock_state.coins = 0
	mock_state.total_clicks = 0
	mock_state.multiplier = 1.0
	mock_state.game_running = False
	return mock_state
