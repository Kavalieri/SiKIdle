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
				# Actualizar datos básicos del jugador
				player_data = {
					'coins': game_state.get('coins', 0),
					'total_clicks': game_state.get('total_clicks', 0),
					'multiplier': game_state.get('multiplier', 1.0),
					'total_playtime': game_state.get('total_playtime', 0)
				}
				self.db.update_player_data(**player_data)

				# Guardar datos de prestigio
				if any(key in game_state for key in ['prestige_crystals', 'total_prestiges', 'lifetime_coins', 'prestige_multiplier']):
					prestige_data = {
						'prestige_crystals': game_state.get('prestige_crystals', 0),
						'total_prestiges': game_state.get('total_prestiges', 0),
						'lifetime_coins': game_state.get('lifetime_coins', 0.0),
						'prestige_multiplier': game_state.get('prestige_multiplier', 1.0)
					}
					self._save_json_data('prestige', prestige_data)

				# Guardar datos de talentos y experiencia
				if any(key in game_state for key in ['player_level', 'player_experience', 'talent_points', 'talents']):
					talent_data = {
						'player_level': game_state.get('player_level', 1),
						'player_experience': game_state.get('player_experience', 0),
						'talent_points': game_state.get('talent_points', 0),
						'total_talent_points_earned': game_state.get('total_talent_points_earned', 0),
						'talents': game_state.get('talents', {})
					}
					self._save_json_data('talents', talent_data)

				# Guardar datos de sistemas complejos como JSON
				for system_key in ['resources', 'buildings', 'upgrades', 'combat_stats', 'dungeon_progress', 'inventory']:
					if system_key in game_state:
						self._save_json_data(system_key, game_state[system_key])

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

			# Cargar datos de prestigio
			prestige_data = self._load_json_data('prestige', {})
			game_state.update(prestige_data)

			# Cargar datos de talentos
			talent_data = self._load_json_data('talents', {})
			game_state.update(talent_data)

			# Cargar datos de sistemas complejos
			for system_key in ['resources', 'buildings', 'upgrades', 'combat_stats', 'dungeon_progress', 'inventory']:
				system_data = self._load_json_data(system_key, {})
				if system_data:
					game_state[system_key] = system_data

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

	def _save_json_data(self, key: str, data: dict) -> bool:
		"""Guarda datos complejos como JSON en la base de datos.
		
		Args:
			key: Clave para identificar los datos
			data: Datos a guardar
			
		Returns:
			True si se guardó correctamente
		"""
		try:
			import json
			json_data = json.dumps(data)
			self.db.set_setting(f"json_{key}", json_data)
			return True
		except Exception as e:
			logging.error(f"Error guardando datos JSON {key}: {e}")
			return False

	def _load_json_data(self, key: str, default: dict) -> dict:
		"""Carga datos complejos desde JSON en la base de datos.
		
		Args:
			key: Clave de los datos
			default: Valor por defecto si no existen
			
		Returns:
			Datos cargados o valor por defecto
		"""
		try:
			import json
			json_data = self.db.get_setting(f"json_{key}", "")
			if json_data:
				return json.loads(json_data)
			return default
		except Exception as e:
			logging.error(f"Error cargando datos JSON {key}: {e}")
			return default

	def create_backup(self) -> bool:
		"""Crea una copia de seguridad del estado actual.
		
		Returns:
			True si se creó la copia correctamente
		"""
		try:
			import time
			timestamp = int(time.time())
			backup_key = f"backup_{timestamp}"
			
			# Obtener estado actual completo
			current_state = self.load_game_state()
			
			# Guardar como backup
			self._save_json_data(backup_key, current_state)
			
			logging.info(f"Backup creado: {backup_key}")
			return True
		except Exception as e:
			logging.error(f"Error creando backup: {e}")
			return False


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
