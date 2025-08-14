"""
Sistema de Prestigio Dimensional para SiKIdle.

Sistema de ascensión dimensional donde los exploradores pueden reiniciar su progreso
para acceder a dimensiones superiores, ganando fragmentos de esencia y bonificaciones permanentes.
"""

import logging
import math
import time
from enum import Enum
from typing import Optional, Dict, List

from core.resources import ResourceType, ResourceManager


class AscensionType(Enum):
	"""Tipos de ascensión dimensional disponibles."""
	MINOR = "minor"           # Ascensión Menor - nivel 50+, requiere derrotar boss dimensión actual
	MAJOR = "major"           # Ascensión Mayor - nivel 100+, requiere boss + completar mazmorra secreta  
	DIMENSION = "dimension"   # Ascensión Dimensional - nivel 200+, requiere boss final + acceso nueva dimensión


class DimensionalReward:
	"""Representa una recompensa de ascensión dimensional."""
	
	def __init__(self, essence_fragments: int, stat_bonus: float, special_unlock: Optional[str] = None):
		"""Inicializa una recompensa de ascensión.
		
		Args:
			essence_fragments: Fragmentos de esencia dimensional ganados
			stat_bonus: Bonificación porcentual de estadísticas (+25%, +50%, etc.)
			special_unlock: Desbloqueo especial (nueva mazmorra, dimensión, etc.)
		"""
		self.essence_fragments = essence_fragments
		self.stat_bonus = stat_bonus
		self.special_unlock = special_unlock


class DimensionalPrestigeManager:
	"""Gestiona el sistema de prestigio dimensional del juego."""
	
	def __init__(self, resource_manager: ResourceManager, database):
		"""Inicializa el gestor de prestigio dimensional.
		
		Args:
			resource_manager: Gestor de recursos del juego
			database: Conexión a la base de datos
		"""
		self.resource_manager = resource_manager
		self.database = database
		
		# Estado del prestigio
		self.total_prestiges = 0
		self.soft_prestiges = 0
		self.hard_prestiges = 0
		self.dimension_prestiges = 0
		
		# Cristales y bonificaciones
		self.prestige_crystals = 0
		self.lifetime_coins = 0.0
		
		# Multiplicadores actuales
		self.income_multiplier = 1.0
		self.building_income_multiplier = 1.0
		self.cost_reduction = 0.0
		self.experience_bonus = 1.0
		
		# Inicializar tablas de base de datos
		self._create_tables()
		
		# Cargar estado guardado
		self.load_prestige_data()
		
		logging.info("Sistema de prestigio inicializado")
	
	def _create_tables(self):
		"""Crea las tablas de prestigio en la base de datos."""
		try:
			# Tabla de estadísticas de prestigio
			self.database.execute('''
				CREATE TABLE IF NOT EXISTS prestige_stats (
					id INTEGER PRIMARY KEY,
					total_prestiges INTEGER DEFAULT 0,
					soft_prestiges INTEGER DEFAULT 0,
					hard_prestiges INTEGER DEFAULT 0,
					dimension_prestiges INTEGER DEFAULT 0,
					prestige_crystals INTEGER DEFAULT 0,
					lifetime_coins REAL DEFAULT 0.0,
					created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
				)
			''')
			
			# Tabla de bonificaciones activas
			self.database.execute('''
				CREATE TABLE IF NOT EXISTS prestige_bonuses (
					id INTEGER PRIMARY KEY,
					income_multiplier REAL DEFAULT 1.0,
					building_income_multiplier REAL DEFAULT 1.0,
					cost_reduction REAL DEFAULT 0.0,
					experience_bonus REAL DEFAULT 1.0,
					last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
				)
			''')
			
			# Insertar fila inicial si no existe
			self.database.execute('''
				INSERT OR IGNORE INTO prestige_stats (id) VALUES (1)
			''')
			
			self.database.execute('''
				INSERT OR IGNORE INTO prestige_bonuses (id) VALUES (1)
			''')
			
			logging.debug("Tablas de prestigio creadas/verificadas")
		
		except Exception as e:
			logging.error(f"Error creando tablas de prestigio: {e}")
	
	def calculate_crystals_gained(self, total_coins: float) -> int:
		"""Calcula los cristales que se ganarían con un prestigio.
		
		Args:
			total_coins: Total de monedas acumuladas en la vida
			
		Returns:
			Número de cristales que se ganarían
		"""
		if total_coins < 1_000_000:
			return 0
		
		# Fórmula: sqrt(total_coins / 1_000_000)
		crystals = math.sqrt(total_coins / 1_000_000)
		return max(1, int(crystals))
	
	def calculate_multiplier_from_crystals(self, crystals: int) -> float:
		"""Calcula el multiplicador basado en cristales de prestigio.
		
		Args:
			crystals: Número de cristales de prestigio
			
		Returns:
			Multiplicador de ingresos
		"""
		# Cada cristal otorga +10% de bonificación
		return 1.0 + (crystals * 0.10)
	
	def can_prestige(self, prestige_type: PrestigeType, current_coins: float) -> bool:
		"""Verifica si se puede realizar un prestigio.
		
		Args:
			prestige_type: Tipo de prestigio a verificar
			current_coins: Monedas actuales del jugador
			
		Returns:
			True si se puede realizar el prestigio
		"""
		requirements = {
			PrestigeType.SOFT: 1_000_000,      # 1 millón
			PrestigeType.HARD: 1_000_000_000,  # 1 billón
			PrestigeType.DIMENSION: 1_000_000_000_000  # 1 trillón
		}
		
		required_coins = requirements.get(prestige_type, float('inf'))
		return current_coins >= required_coins
	
	def get_prestige_stats(self) -> dict:
		"""Obtiene estadísticas completas de prestigio.
		
		Returns:
			Diccionario con todas las estadísticas
		"""
		return {
			'total_prestiges': self.total_prestiges,
			'soft_prestiges': self.soft_prestiges,
			'hard_prestiges': self.hard_prestiges,
			'dimension_prestiges': self.dimension_prestiges,
			'prestige_crystals': self.prestige_crystals,
			'lifetime_coins': self.lifetime_coins,
			'income_multiplier': self.income_multiplier,
			'building_income_multiplier': self.building_income_multiplier,
			'cost_reduction': self.cost_reduction,
			'experience_bonus': self.experience_bonus
		}
	
	def load_prestige_data(self):
		"""Carga el estado de prestigio desde la base de datos."""
		try:
			# Cargar estadísticas
			stats_result = self.database.execute('''
				SELECT total_prestiges, soft_prestiges, hard_prestiges, 
				       dimension_prestiges, prestige_crystals, lifetime_coins
				FROM prestige_stats WHERE id = 1
			''').fetchone()
			
			if stats_result:
				(self.total_prestiges, self.soft_prestiges, self.hard_prestiges,
				 self.dimension_prestiges, self.prestige_crystals, self.lifetime_coins) = stats_result
			
			logging.info(f"Prestigio cargado: {self.prestige_crystals} cristales, {self.total_prestiges} prestiges")
		
		except Exception as e:
			logging.error(f"Error cargando datos de prestigio: {e}")
