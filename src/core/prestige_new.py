"""
Sistema de Prestigio para SiKIdle.

Permite a los jugadores reiniciar su progreso a cambio de bonificaciones permanentes
a través de Cristales de Prestigio.
"""

import logging
import math
import time
from enum import Enum
from typing import Optional

from core.resources import ResourceType, ResourceManager


class PrestigeType(Enum):
	"""Tipos de prestigio disponibles."""
	SOFT = "soft"           # Prestigio suave - 1M requisito
	HARD = "hard"           # Prestigio duro - 1B requisito  
	DIMENSION = "dimension" # Prestigio dimensional - 1T requisito


class PrestigeReward:
	"""Representa una recompensa de prestigio."""
	
	def __init__(self, crystals: int, multiplier_bonus: float):
		"""Inicializa una recompensa de prestigio.
		
		Args:
			crystals: Cristales de prestigio ganados
			multiplier_bonus: Bonificación de multiplicador obtenida
		"""
		self.crystals = crystals
		self.multiplier_bonus = multiplier_bonus


class PrestigeManager:
	"""Gestiona el sistema de prestigio del juego."""
	
	def __init__(self, resource_manager: ResourceManager, database):
		"""Inicializa el gestor de prestigio.
		
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
	
	def calculate_prestige_reward(self, prestige_type: PrestigeType, total_coins: float) -> PrestigeReward:
		"""Calcula la recompensa de un prestigio.
		
		Args:
			prestige_type: Tipo de prestigio
			total_coins: Total de monedas para el cálculo
			
		Returns:
			Recompensa calculada del prestigio
		"""
		base_crystals = self.calculate_crystals_gained(total_coins)
		
		# Bonus por tipo de prestigio
		type_multipliers = {
			PrestigeType.SOFT: 1.0,      # Base
			PrestigeType.HARD: 2.0,      # Doble cristales
			PrestigeType.DIMENSION: 5.0  # 5x cristales
		}
		
		multiplier = type_multipliers.get(prestige_type, 1.0)
		final_crystals = int(base_crystals * multiplier)
		
		# Calcular nuevo multiplicador total
		new_total_crystals = self.prestige_crystals + final_crystals
		new_multiplier = self.calculate_multiplier_from_crystals(new_total_crystals)
		
		return PrestigeReward(final_crystals, new_multiplier)
	
	def perform_prestige(self, prestige_type: PrestigeType, game_state) -> bool:
		"""Realiza un prestigio completo.
		
		Args:
			prestige_type: Tipo de prestigio a realizar
			game_state: Referencia al estado del juego
			
		Returns:
			True si el prestigio fue exitoso
		"""
		try:
			current_coins = self.resource_manager.get_resource(ResourceType.COINS)
			
			# Verificar si se puede realizar
			if not self.can_prestige(prestige_type, current_coins):
				logging.warning(f"No se puede realizar prestigio {prestige_type}: insuficientes monedas")
				return False
			
			# Actualizar lifetime coins
			self.lifetime_coins += current_coins
			
			# Calcular recompensa
			reward = self.calculate_prestige_reward(prestige_type, self.lifetime_coins)
			
			# Otorgar cristales
			self.prestige_crystals += reward.crystals
			
			# Actualizar contadores
			self.total_prestiges += 1
			if prestige_type == PrestigeType.SOFT:
				self.soft_prestiges += 1
			elif prestige_type == PrestigeType.HARD:
				self.hard_prestiges += 1
			elif prestige_type == PrestigeType.DIMENSION:
				self.dimension_prestiges += 1
			
			# Recalcular multiplicadores
			self._update_multipliers()
			
			# Resetear progreso del juego
			self._reset_game_progress(game_state)
			
			# Guardar estado
			self.save_prestige_data()
			
			logging.info(f"Prestigio {prestige_type.value} realizado: +{reward.crystals} cristales, nuevo multiplicador: {reward.multiplier_bonus:.1f}x")
			return True
		
		except Exception as e:
			logging.error(f"Error realizando prestigio: {e}")
			return False
	
	def _reset_game_progress(self, game_state):
		"""Resetea el progreso del juego manteniendo prestigio y logros.
		
		Args:
			game_state: Estado del juego a resetear
		"""
		try:
			# Resetear recursos (excepto cristales de prestigio)
			game_state.coins = 0
			self.resource_manager.resources[ResourceType.COINS] = 0
			self.resource_manager.resources[ResourceType.EXPERIENCE] = 0
			# Mantener cristales de prestigio
			
			# Resetear edificios
			if hasattr(game_state, 'building_manager'):
				for building_type, building in game_state.building_manager.buildings.items():
					building.count = 0
					building.last_production_time = time.time()
			
			# Resetear mejoras
			if hasattr(game_state, 'upgrade_manager'):
				for upgrade_type, upgrade in game_state.upgrade_manager.upgrades.items():
					upgrade.level = 0
			
			# NO resetear logros - se mantienen
			
			logging.info("Progreso del juego reseteado por prestigio")
		
		except Exception as e:
			logging.error(f"Error reseteando progreso: {e}")
	
	def _update_multipliers(self):
		"""Actualiza todos los multiplicadores basados en cristales actuales."""
		base_multiplier = self.calculate_multiplier_from_crystals(self.prestige_crystals)
		
		# Multiplicadores principales
		self.income_multiplier = base_multiplier
		self.building_income_multiplier = base_multiplier
		
		# Reducción de costos: 1% por cada 5 cristales
		self.cost_reduction = min(0.5, (self.prestige_crystals // 5) * 0.01)
		
		# Bonificación de experiencia: 10% por cada 10 cristales
		self.experience_bonus = 1.0 + ((self.prestige_crystals // 10) * 0.10)
		
		logging.debug(f"Multiplicadores actualizados: Income {self.income_multiplier:.1f}x, Cost reduction {self.cost_reduction:.0%}")
	
	def get_prestige_multiplier(self) -> float:
		"""Obtiene el multiplicador de prestigio para ingresos.
		
		Returns:
			Multiplicador actual de ingresos
		"""
		return self.income_multiplier
	
	def get_building_multiplier(self) -> float:
		"""Obtiene el multiplicador de prestigio para edificios.
		
		Returns:
			Multiplicador actual de edificios
		"""
		return self.building_income_multiplier
	
	def get_cost_reduction(self) -> float:
		"""Obtiene la reducción de costos por prestigio.
		
		Returns:
			Porcentaje de reducción de costos (0.0 - 1.0)
		"""
		return self.cost_reduction
	
	def get_experience_bonus(self) -> float:
		"""Obtiene la bonificación de experiencia por prestigio.
		
		Returns:
			Multiplicador de experiencia
		"""
		return self.experience_bonus
	
	def save_prestige_data(self):
		"""Guarda el estado de prestigio en la base de datos."""
		try:
			# Guardar estadísticas
			self.database.execute('''
				UPDATE prestige_stats SET
					total_prestiges = ?,
					soft_prestiges = ?,
					hard_prestiges = ?,
					dimension_prestiges = ?,
					prestige_crystals = ?,
					lifetime_coins = ?
				WHERE id = 1
			''', (
				self.total_prestiges,
				self.soft_prestiges,
				self.hard_prestiges,
				self.dimension_prestiges,
				self.prestige_crystals,
				self.lifetime_coins
			))
			
			# Guardar bonificaciones
			self.database.execute('''
				UPDATE prestige_bonuses SET
					income_multiplier = ?,
					building_income_multiplier = ?,
					cost_reduction = ?,
					experience_bonus = ?
				WHERE id = 1
			''', (
				self.income_multiplier,
				self.building_income_multiplier,
				self.cost_reduction,
				self.experience_bonus
			))
			
			logging.debug("Datos de prestigio guardados")
		
		except Exception as e:
			logging.error(f"Error guardando datos de prestigio: {e}")
	
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
			
			# Cargar bonificaciones
			bonus_result = self.database.execute('''
				SELECT income_multiplier, building_income_multiplier, 
				       cost_reduction, experience_bonus
				FROM prestige_bonuses WHERE id = 1
			''').fetchone()
			
			if bonus_result:
				(self.income_multiplier, self.building_income_multiplier,
				 self.cost_reduction, self.experience_bonus) = bonus_result
			else:
				# Recalcular si no hay datos guardados
				self._update_multipliers()
			
			logging.info(f"Prestigio cargado: {self.prestige_crystals} cristales, {self.total_prestiges} prestiges")
		
		except Exception as e:
			logging.error(f"Error cargando datos de prestigio: {e}")
			# Valores por defecto en caso de error
			self._update_multipliers()
	
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
