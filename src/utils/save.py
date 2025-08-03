"""Sistema de guardado automático para SiKIdle.

Gestiona el guardado periódico del progreso del jugador
y proporciona métodos para guardar/cargar el estado del juego.
"""

import logging
import threading
from typing import Any

from utils.db import get_database


class SaveManager:
	"""Gestiona el guardado automático y manual del progreso del juego."""

	def __init__(self):
		"""Inicializa el gestor de guardado."""
		self.db = get_database()
		self.save_interval = 30  # Guardar cada 30 segundos
		self.auto_save_enabled = True
		self._save_thread: threading.Thread | None = None
		self._stop_event = threading.Event()

	def start_auto_save(self) -> None:
		"""Inicia el guardado automático en un hilo separado."""
		if self._save_thread and self._save_thread.is_alive():
			logging.warning("El guardado automático ya está en ejecución")
			return

		self._stop_event.clear()
		self._save_thread = threading.Thread(target=self._auto_save_loop, daemon=True)
		self._save_thread.start()
		logging.info("Guardado automático iniciado")

	def stop_auto_save(self) -> None:
		"""Detiene el guardado automático."""
		if self._save_thread and self._save_thread.is_alive():
			self._stop_event.set()
			self._save_thread.join(timeout=5)
			logging.info("Guardado automático detenido")

	def _auto_save_loop(self) -> None:
		"""Bucle principal del guardado automático."""
		while not self._stop_event.is_set():
			if self.auto_save_enabled:
				try:
					self.save_game_state()
					logging.debug("Guardado automático completado")
				except Exception as e:
					logging.error(f"Error en guardado automático: {e}")

			# Esperar el intervalo o hasta que se solicite parar
			self._stop_event.wait(self.save_interval)

	def save_game_state(self, game_state: dict[str, Any] | None = None) -> bool:
		"""Guarda el estado actual del juego.
		
		Args:
			game_state: Estado del juego a guardar. Si es None, no actualiza nada.
			
		Returns:
			True si el guardado fue exitoso, False en caso contrario
		"""
		try:
			if game_state:
				# Actualizar datos del jugador
				player_data = {
					'coins': game_state.get('coins', 0),
					'total_clicks': game_state.get('total_clicks', 0),
					'multiplier': game_state.get('multiplier', 1.0),
					'total_playtime': game_state.get('total_playtime', 0)
				}
				self.db.update_player_data(**player_data)

				# Actualizar estadísticas si están disponibles
				stats = game_state.get('stats', {})
				for key, value in stats.items():
					self.db.increment_stat(key, value - self.db.get_stat(key))

			return True

		except Exception as e:
			logging.error(f"Error guardando el estado del juego: {e}")
			return False

	def load_game_state(self) -> dict[str, Any]:
		"""Carga el estado del juego desde la base de datos.
		
		Returns:
			Diccionario con el estado del juego
		"""
		try:
			# Cargar datos del jugador
			player_data = self.db.get_player_data()

			if not player_data:
				# Crear estado por defecto si no existe
				default_state = {
					'coins': 0,
					'total_clicks': 0,
					'multiplier': 1.0,
					'total_playtime': 0,
					'stats': {},
					'settings': {}
				}
				return default_state

			# Cargar estadísticas básicas
			stats = {
				'clicks_today': self.db.get_stat('clicks_today'),
				'coins_earned_today': self.db.get_stat('coins_earned_today'),
				'sessions_played': self.db.get_stat('sessions_played'),
				'upgrades_bought': self.db.get_stat('upgrades_bought')
			}

			# Cargar configuraciones básicas
			settings = {
				'sound_enabled': self.db.get_setting('sound_enabled', 'true'),
				'vibration_enabled': self.db.get_setting('vibration_enabled', 'true'),
				'language': self.db.get_setting('language', 'es')
			}

			game_state = {
				'coins': int(player_data['coins']),
				'total_clicks': int(player_data['total_clicks']),
				'multiplier': float(player_data['multiplier']),
				'total_playtime': int(player_data['total_playtime']),
				'last_saved': player_data['last_saved'],
				'stats': stats,
				'settings': settings
			}

			logging.info(f"Estado del juego cargado: {player_data['coins']} monedas, {player_data['total_clicks']} clics")
			return game_state

		except Exception as e:
			logging.error(f"Error cargando el estado del juego: {e}")
			# Devolver estado por defecto en caso de error
			return {
				'coins': 0,
				'total_clicks': 0,
				'multiplier': 1.0,
				'total_playtime': 0,
				'stats': {},
				'settings': {}
			}

	def save_setting(self, key: str, value: str) -> None:
		"""Guarda una configuración específica.
		
		Args:
			key: Clave de la configuración
			value: Valor a guardar
		"""
		try:
			self.db.set_setting(key, value)
			logging.debug(f"Configuración guardada: {key} = {value}")
		except Exception as e:
			logging.error(f"Error guardando configuración {key}: {e}")

	def get_setting(self, key: str, default: str = "") -> str:
		"""Obtiene una configuración específica.
		
		Args:
			key: Clave de la configuración
			default: Valor por defecto
			
		Returns:
			Valor de la configuración
		"""
		try:
			return self.db.get_setting(key, default)
		except Exception as e:
			logging.error(f"Error obteniendo configuración {key}: {e}")
			return default

	def increment_stat(self, stat_key: str, amount: int = 1) -> None:
		"""Incrementa una estadística específica.
		
		Args:
			stat_key: Clave de la estadística
			amount: Cantidad a incrementar
		"""
		try:
			self.db.increment_stat(stat_key, amount)
		except Exception as e:
			logging.error(f"Error incrementando estadística {stat_key}: {e}")

	def get_stat(self, stat_key: str, default: int = 0) -> int:
		"""Obtiene una estadística específica.
		
		Args:
			stat_key: Clave de la estadística
			default: Valor por defecto si no existe
			
		Returns:
			Valor de la estadística
		"""
		try:
			return self.db.get_stat(stat_key) or default
		except Exception as e:
			logging.error(f"Error obteniendo estadística {stat_key}: {e}")
			return default

	def get_upgrade_level(self, upgrade_id: str) -> int:
		"""Obtiene el nivel actual de una mejora.
		
		Args:
			upgrade_id: ID de la mejora
			
		Returns:
			Nivel actual de la mejora
		"""
		try:
			return self.db.get_upgrade_level(upgrade_id)
		except Exception as e:
			logging.error(f"Error obteniendo nivel de mejora {upgrade_id}: {e}")
			return 0

	def set_upgrade_level(self, upgrade_id: str, level: int) -> bool:
		"""Establece el nivel de una mejora.
		
		Args:
			upgrade_id: ID de la mejora
			level: Nuevo nivel
			
		Returns:
			True si se actualizó correctamente
		"""
		try:
			self.db.set_upgrade_level(upgrade_id, level)
			return True
		except Exception as e:
			logging.error(f"Error estableciendo nivel de mejora {upgrade_id}: {e}")
			return False

	def get_all_upgrades(self) -> dict:
		"""Obtiene todos los niveles de mejoras.
		
		Returns:
			Diccionario con upgrade_id: level
		"""
		try:
			return self.db.get_all_upgrades()
		except Exception as e:
			logging.error(f"Error obteniendo todas las mejoras: {e}")
			return {}

	def force_save(self) -> bool:
		"""Fuerza un guardado inmediato del estado actual.
		
		Returns:
			True si el guardado fue exitoso
		"""
		logging.info("Guardado forzado ejecutado")
		return self.save_game_state()


# Instancia global del gestor de guardado
_save_manager: SaveManager | None = None

def get_save_manager() -> SaveManager:
	"""Obtiene la instancia global del gestor de guardado.
	
	Returns:
		SaveManager: Instancia del gestor de guardado
	"""
	global _save_manager
	if _save_manager is None:
		_save_manager = SaveManager()
	return _save_manager
