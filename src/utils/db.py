"""Sistema de base de datos para SiKIdle.

Gestiona la conexión SQLite y las operaciones básicas de base de datos.
Utiliza rutas del sistema de usuario para persistencia cross-platform.
"""

import sqlite3
import logging
from pathlib import Path
from typing import Any, Optional
from contextlib import contextmanager

from utils.paths import get_user_data_dir


class DatabaseManager:
	"""Gestiona la conexión y operaciones de la base de datos SQLite."""
	
	def __init__(self):
		"""Inicializa el gestor de base de datos."""
		self.db_path = self._get_database_path()
		self._ensure_database_exists()
		
	def _get_database_path(self) -> Path:
		"""Obtiene la ruta completa del archivo de base de datos.
		
		Returns:
			Path: Ruta al archivo sikidle.db
		"""
		savegames_dir = get_user_data_dir() / 'savegames'
		savegames_dir.mkdir(parents=True, exist_ok=True)
		return savegames_dir / 'sikidle.db'
	
	def _ensure_database_exists(self) -> None:
		"""Asegura que la base de datos existe y tiene las tablas necesarias."""
		try:
			with self.get_connection() as conn:
				self._create_tables(conn)
			logging.info(f"Base de datos inicializada en: {self.db_path}")
		except Exception as e:
			logging.error(f"Error inicializando base de datos: {e}")
			raise
	
	def _create_tables(self, conn: sqlite3.Connection) -> None:
		"""Crea todas las tablas necesarias si no existen.
		
		Args:
			conn: Conexión a la base de datos
		"""
		cursor = conn.cursor()
		
		# Tabla del jugador (monedas, progreso general)
		cursor.execute("""
			CREATE TABLE IF NOT EXISTS player (
				id INTEGER PRIMARY KEY CHECK (id = 1),
				coins INTEGER DEFAULT 0,
				total_clicks INTEGER DEFAULT 0,
				multiplier REAL DEFAULT 1.0,
				last_saved TEXT DEFAULT CURRENT_TIMESTAMP,
				total_playtime INTEGER DEFAULT 0
			)
		""")
		
		# Tabla de mejoras disponibles y sus niveles
		cursor.execute("""
			CREATE TABLE IF NOT EXISTS upgrades (
				id INTEGER PRIMARY KEY AUTOINCREMENT,
				name TEXT UNIQUE NOT NULL,
				level INTEGER DEFAULT 0,
				base_cost INTEGER NOT NULL,
				current_cost INTEGER,
				unlocked BOOLEAN DEFAULT 0,
				description TEXT
			)
		""")
		
		# Tabla de configuración del usuario
		cursor.execute("""
			CREATE TABLE IF NOT EXISTS settings (
				key TEXT PRIMARY KEY,
				value TEXT NOT NULL
			)
		""")
		
		# Tabla de estadísticas del juego
		cursor.execute("""
			CREATE TABLE IF NOT EXISTS stats (
				key TEXT PRIMARY KEY,
				value INTEGER DEFAULT 0
			)
		""")
		
		conn.commit()
		
		# Insertar jugador por defecto si no existe
		cursor.execute("SELECT COUNT(*) FROM player")
		if cursor.fetchone()[0] == 0:
			cursor.execute("INSERT INTO player (id) VALUES (1)")
			conn.commit()
	
	@contextmanager
	def get_connection(self):
		"""Context manager para obtener conexión a la base de datos.
		
		Yields:
			sqlite3.Connection: Conexión a la base de datos
		"""
		conn = None
		try:
			conn = sqlite3.connect(self.db_path)
			conn.row_factory = sqlite3.Row  # Permite acceso por nombre de columna
			yield conn
		except Exception as e:
			if conn:
				conn.rollback()
			logging.error(f"Error en operación de base de datos: {e}")
			raise
		finally:
			if conn:
				conn.close()
	
	def execute_query(self, query: str, params: tuple[Any, ...] = ()) -> list[sqlite3.Row]:
		"""Ejecuta una consulta SELECT y devuelve los resultados.
		
		Args:
			query: Consulta SQL a ejecutar
			params: Parámetros para la consulta
			
		Returns:
			Lista de filas del resultado
		"""
		with self.get_connection() as conn:
			cursor = conn.cursor()
			cursor.execute(query, params)
			return cursor.fetchall()
	
	def execute_update(self, query: str, params: tuple[Any, ...] = ()) -> int:
		"""Ejecuta una consulta INSERT/UPDATE/DELETE.
		
		Args:
			query: Consulta SQL a ejecutar
			params: Parámetros para la consulta
			
		Returns:
			Número de filas afectadas
		"""
		with self.get_connection() as conn:
			cursor = conn.cursor()
			cursor.execute(query, params)
			conn.commit()
			return cursor.rowcount
	
	def get_player_data(self) -> Optional[sqlite3.Row]:
		"""Obtiene los datos del jugador.
		
		Returns:
			Datos del jugador o None si no existe
		"""
		result = self.execute_query("SELECT * FROM player WHERE id = 1")
		return result[0] if result else None
	
	def update_player_data(self, **kwargs: Any) -> None:
		"""Actualiza los datos del jugador.
		
		Args:
			**kwargs: Campos a actualizar (coins, total_clicks, multiplier, etc.)
		"""
		if not kwargs:
			return
			
		fields: list[str] = []
		values: list[Any] = []
		
		for key, value in kwargs.items():
			fields.append(f"{key} = ?")
			values.append(value)
		
		# Añadir timestamp de último guardado
		fields.append("last_saved = CURRENT_TIMESTAMP")
		
		query = f"UPDATE player SET {', '.join(fields)} WHERE id = 1"
		self.execute_update(query, tuple(values))
	
	def get_setting(self, key: str, default: str = "") -> str:
		"""Obtiene un valor de configuración.
		
		Args:
			key: Clave de la configuración
			default: Valor por defecto si no existe
			
		Returns:
			Valor de la configuración
		"""
		result = self.execute_query("SELECT value FROM settings WHERE key = ?", (key,))
		return result[0]['value'] if result else default
	
	def set_setting(self, key: str, value: str) -> None:
		"""Establece un valor de configuración.
		
		Args:
			key: Clave de la configuración
			value: Valor a establecer
		"""
		self.execute_update(
			"INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
			(key, value)
		)
	
	def get_stat(self, key: str) -> int:
		"""Obtiene una estadística del juego.
		
		Args:
			key: Clave de la estadística
			
		Returns:
			Valor de la estadística (0 si no existe)
		"""
		result = self.execute_query("SELECT value FROM stats WHERE key = ?", (key,))
		return result[0]['value'] if result else 0
	
	def increment_stat(self, key: str, amount: int = 1) -> None:
		"""Incrementa una estadística del juego.
		
		Args:
			key: Clave de la estadística
			amount: Cantidad a incrementar
		"""
		self.execute_update(
			"INSERT OR REPLACE INTO stats (key, value) VALUES (?, COALESCE((SELECT value FROM stats WHERE key = ?), 0) + ?)",
			(key, key, amount)
		)
	
	def get_upgrade_level(self, upgrade_id: str) -> int:
		"""Obtiene el nivel actual de una mejora.
		
		Args:
			upgrade_id: ID de la mejora
			
		Returns:
			Nivel de la mejora (0 si no existe)
		"""
		result = self.execute_query("SELECT level FROM upgrades WHERE upgrade_id = ?", (upgrade_id,))
		return result[0]['level'] if result else 0
	
	def set_upgrade_level(self, upgrade_id: str, level: int) -> None:
		"""Establece el nivel de una mejora.
		
		Args:
			upgrade_id: ID de la mejora
			level: Nuevo nivel
		"""
		self.execute_update(
			"INSERT OR REPLACE INTO upgrades (upgrade_id, level) VALUES (?, ?)",
			(upgrade_id, level)
		)
	
	def get_all_upgrades(self) -> dict:
		"""Obtiene todos los niveles de mejoras.
		
		Returns:
			Diccionario con upgrade_id: level
		"""
		result = self.execute_query("SELECT upgrade_id, level FROM upgrades")
		return {row['upgrade_id']: row['level'] for row in result}


# Instancia global del gestor de base de datos
_db_manager: Optional[DatabaseManager] = None

def get_database() -> DatabaseManager:
	"""Obtiene la instancia global del gestor de base de datos.
	
	Returns:
		DatabaseManager: Instancia del gestor de base de datos
	"""
	global _db_manager
	if _db_manager is None:
		_db_manager = DatabaseManager()
	return _db_manager
