"""Lógica principal del juego SiKIdle.

Contiene la clase GameState que gestiona todo el estado del juego,
incluyendo múltiples recursos, clics, multiplicadores y bonificaciones.
"""

import logging
import time
from typing import Any

from utils.save import get_save_manager
from core.resources import ResourceManager, ResourceType


class GameState:
	"""Gestiona el estado principal del juego idle clicker."""

	def __init__(self):
		"""Inicializa el estado del juego."""
		self.save_manager = get_save_manager()

		# Sistema de recursos múltiples
		self.resource_manager = ResourceManager()

		# Estado principal del juego (mantenido para compatibilidad)
		self.coins = 0
		self.total_clicks = 0
		self.multiplier = 1.0
		self.total_playtime = 0

		# Bonificaciones temporales
		self.bonus_multiplier = 1.0
		self.bonus_end_time = 0.0

		# Estadísticas de sesión
		self.session_start_time = time.time()
		self.session_clicks = 0
		self.session_coins = 0

		# Estado de la aplicación
		self.game_running = False

		# Cargar estado guardado
		self.load_game()

		logging.info(f"Juego inicializado: {self.coins} monedas, {self.total_clicks} clics totales")

	def start_game(self) -> None:
		"""Inicia el juego y comienza el guardado automático."""
		self.game_running = True
		self.session_start_time = time.time()
		self.session_clicks = 0
		self.session_coins = 0

		# Iniciar guardado automático
		self.save_manager.start_auto_save()

		# Incrementar estadística de sesiones
		self.save_manager.increment_stat('sessions_played', 1)

		logging.info("Juego iniciado")

	def stop_game(self) -> None:
		"""Detiene el juego y guarda el progreso."""
		if not self.game_running:
			return

		self.game_running = False

		# Actualizar tiempo total de juego
		session_time = int(time.time() - self.session_start_time)
		self.total_playtime += session_time

		# Detener guardado automático y guardar una vez más
		self.save_manager.stop_auto_save()
		self.save_game()

		logging.info(f"Juego detenido. Sesión: {session_time}s, Clics: {self.session_clicks}, Monedas: {self.session_coins}")

	def click(self) -> int:
		"""Procesa un clic del jugador.
		
		Returns:
			Cantidad de monedas ganadas por este clic
		"""
		if not self.game_running:
			return 0

		# Calcular monedas ganadas
		base_coins = 1
		current_multiplier = self.get_current_multiplier()
		coins_earned = int(base_coins * current_multiplier)

		# Actualizar estado tradicional (compatibilidad)
		self.coins += coins_earned
		
		# Actualizar sistema de recursos múltiples
		self.resource_manager.add_resource(ResourceType.COINS, coins_earned)
		
		# Posibilidad de ganar experiencia por clic
		if self.total_clicks % 10 == 0:  # Cada 10 clics
			exp_earned = 1
			self.resource_manager.add_resource(ResourceType.EXPERIENCE, exp_earned)
		
		self.total_clicks += 1
		self.session_clicks += 1
		self.session_coins += coins_earned

		# Incrementar estadísticas
		self.save_manager.increment_stat('clicks_today', 1)
		self.save_manager.increment_stat('coins_earned_today', coins_earned)

		return coins_earned

	def get_current_multiplier(self) -> float:
		"""Obtiene el multiplicador actual considerando bonificaciones.
		
		Returns:
			Multiplicador total actual
		"""
		total_multiplier = self.multiplier

		# Aplicar bonificación temporal si está activa
		if time.time() < self.bonus_end_time:
			total_multiplier *= self.bonus_multiplier

		return total_multiplier

	def apply_ad_bonus(self, multiplier: float = 2.0, duration: int = 30) -> bool:
		"""Aplica bonificación por ver anuncio (simulado).
		
		Args:
			multiplier: Multiplicador de la bonificación
			duration: Duración en segundos
			
		Returns:
			True si se aplicó la bonificación
		"""
		# TODO: AdMob integration here
		# Por ahora simular que siempre funciona

		self.bonus_multiplier = multiplier
		self.bonus_end_time = time.time() + duration

		logging.info(f"Bonificación aplicada: x{multiplier} durante {duration}s")
		return True

	def get_bonus_time_remaining(self) -> float:
		"""Obtiene el tiempo restante de bonificación.
		
		Returns:
			Segundos restantes de bonificación (0 si no hay)
		"""
		remaining = self.bonus_end_time - time.time()
		return max(0, remaining)

	def is_bonus_active(self) -> bool:
		"""Verifica si hay una bonificación activa.
		
		Returns:
			True si hay bonificación activa
		"""
		return self.get_bonus_time_remaining() > 0

	def can_afford(self, cost: int) -> bool:
		"""Verifica si el jugador puede permitirse un costo.
		
		Args:
			cost: Costo a verificar
			
		Returns:
			True si tiene suficientes monedas
		"""
		return self.coins >= cost

	def spend_coins(self, amount: int) -> bool:
		"""Gasta monedas si es posible.
		
		Args:
			amount: Cantidad a gastar
			
		Returns:
			True si se pudieron gastar las monedas
		"""
		if not self.can_afford(amount):
			return False

		self.coins -= amount
		return True

	def get_game_stats(self) -> dict[str, Any]:
		"""Obtiene estadísticas completas del juego.
		
		Returns:
			Diccionario con todas las estadísticas
		"""
		current_session_time = 0
		if self.game_running:
			current_session_time = int(time.time() - self.session_start_time)

		return {
			'coins': self.coins,
			'total_clicks': self.total_clicks,
			'multiplier': self.multiplier,
			'current_multiplier': self.get_current_multiplier(),
			'total_playtime': self.total_playtime + current_session_time,
			'session_clicks': self.session_clicks,
			'session_coins': self.session_coins,
			'session_time': current_session_time,
			'bonus_active': self.is_bonus_active(),
			'bonus_time_remaining': self.get_bonus_time_remaining(),
			'clicks_today': self.save_manager.db.get_stat('clicks_today'),
			'coins_earned_today': self.save_manager.db.get_stat('coins_earned_today'),
			'sessions_played': self.save_manager.db.get_stat('sessions_played')
		}

	def save_game(self) -> bool:
		"""Guarda el estado actual del juego.
		
		Returns:
			True si el guardado fue exitoso
		"""
		# Calcular tiempo total incluyendo sesión actual
		current_session_time = 0
		if self.game_running:
			current_session_time = int(time.time() - self.session_start_time)

		game_state = {
			'coins': self.coins,
			'total_clicks': self.total_clicks,
			'multiplier': self.multiplier,
			'total_playtime': self.total_playtime + current_session_time,
			'resources': self.resource_manager.get_save_data()
		}

		return self.save_manager.save_game_state(game_state)

	def load_game(self) -> None:
		"""Carga el estado del juego desde el sistema de guardado."""
		saved_state = self.save_manager.load_game_state()

		self.coins = saved_state.get('coins', 0)
		self.total_clicks = saved_state.get('total_clicks', 0)
		self.multiplier = saved_state.get('multiplier', 1.0)
		self.total_playtime = saved_state.get('total_playtime', 0)
		
		# Cargar recursos si existen
		if 'resources' in saved_state:
			self.resource_manager.load_save_data(saved_state['resources'])
		
		# Sincronizar coins con el sistema de recursos
		self.resource_manager.set_resource(ResourceType.COINS, self.coins)

		logging.info(f"Estado cargado: {self.coins} monedas, {self.total_clicks} clics")

	def reset_game(self) -> None:
		"""Reinicia el juego (para testing o reset completo)."""
		logging.warning("Reiniciando progreso del juego")

		self.coins = 0
		self.total_clicks = 0
		self.multiplier = 1.0
		self.total_playtime = 0
		self.bonus_multiplier = 1.0
		self.bonus_end_time = 0.0
		self.session_clicks = 0
		self.session_coins = 0

		# Guardar estado reseteado
		self.save_game()


# Instancia global del estado del juego
_game_state: GameState | None = None

def get_game_state() -> GameState:
	"""Obtiene la instancia global del estado del juego.
	
	Returns:
		GameState: Instancia del estado del juego
	"""
	global _game_state
	if _game_state is None:
		_game_state = GameState()
	return _game_state
