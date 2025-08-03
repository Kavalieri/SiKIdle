"""
Sistema de logros para SiKIdle.

Este módulo maneja todos los logros del juego, incluyendo:
- Definición de tipos de logros
- Gestión de progreso y desbloqueo
- Recompensas por logros completados
- Persistencia de datos de logros
"""

import logging
import time
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Callable, Any

from utils.database import Database
from core.resources import ResourceType, ResourceManager


class AchievementType(Enum):
	"""Tipos de logros disponibles en el juego."""
	
	# Logros de Clics
	CLICK_NOVICE = "click_novice"              # Primer clic
	CLICK_APPRENTICE = "click_apprentice"      # 100 clics
	CLICK_EXPERT = "click_expert"              # 1,000 clics
	CLICK_MASTER = "click_master"              # 10,000 clics
	CLICK_LEGEND = "click_legend"              # 100,000 clics
	
	# Logros de Monedas
	MONEY_FIRST = "money_first"                # 10 monedas
	MONEY_RICH = "money_rich"                  # 1,000 monedas
	MONEY_MILLIONAIRE = "money_millionaire"    # 1,000,000 monedas
	MONEY_BILLIONAIRE = "money_billionaire"    # 1,000,000,000 monedas
	
	# Logros de Edificios
	BUILDING_FIRST = "building_first"          # 1 edificio
	BUILDING_EMPIRE = "building_empire"        # 10 edificios
	BUILDING_CORPORATION = "building_corporation"  # 50 edificios
	BUILDING_MEGACORP = "building_megacorp"    # 100 edificios
	
	# Logros de Mejoras
	UPGRADE_FIRST = "upgrade_first"            # 1 mejora
	UPGRADE_OPTIMIZER = "upgrade_optimizer"    # 5 mejoras
	UPGRADE_PERFECTIONIST = "upgrade_perfectionist"  # 15 mejoras
	
	# Logros de Tiempo
	TIME_SESSION_1H = "time_session_1h"        # 1 hora jugando
	TIME_SESSION_6H = "time_session_6h"        # 6 horas jugando
	TIME_DAILY_1 = "time_daily_1"              # 1 día jugando
	TIME_DAILY_7 = "time_daily_7"              # 7 días jugando
	
	# Logros Ocultos
	HIDDEN_SPEED_1000 = "hidden_speed_1000"    # 1000 clics/min
	HIDDEN_IDLE_12H = "hidden_idle_12h"        # 12h sin clickear
	HIDDEN_PERFECTIONIST = "hidden_perfectionist"  # Todas mejoras al máximo


class AchievementCategory(Enum):
	"""Categorías de logros para organización en UI."""
	PROGRESSION = "progression"  # Logros de progreso básico
	TIME = "time"               # Logros relacionados con tiempo
	EFFICIENCY = "efficiency"   # Logros de optimización
	HIDDEN = "hidden"          # Logros ocultos/especiales


class RewardType(Enum):
	"""Tipos de recompensas por logros."""
	COINS = "coins"                    # Monedas directas
	MULTIPLIER_TEMPORARY = "mult_temp" # Multiplicador temporal
	MULTIPLIER_PERMANENT = "mult_perm" # Multiplicador permanente
	UNLOCK_CONTENT = "unlock"          # Desbloquea contenido


@dataclass
class AchievementReward:
	"""Recompensa otorgada al completar un logro."""
	reward_type: RewardType
	value: float                       # Cantidad o multiplicador
	duration: float = 0               # Duración en segundos (para temporales)
	resource_type: ResourceType = ResourceType.COINS  # Tipo de recurso


@dataclass
class AchievementInfo:
	"""Información completa sobre un logro."""
	achievement_type: AchievementType
	name: str
	description: str
	category: AchievementCategory
	target_value: float               # Valor objetivo para completar
	reward: AchievementReward
	emoji: str = "🏆"
	hidden: bool = False             # Si es un logro oculto
	prerequisite: Optional[AchievementType] = None  # Logro prerequisito


class Achievement:
	"""Representa el estado de un logro específico del jugador."""
	
	def __init__(self, achievement_type: AchievementType):
		"""Inicializa un logro.
		
		Args:
			achievement_type: Tipo de logro
		"""
		self.achievement_type = achievement_type
		self.unlocked = False
		self.progress = 0.0
		self.unlock_time = 0.0
	
	def update_progress(self, current_value: float) -> bool:
		"""Actualiza el progreso del logro.
		
		Args:
			current_value: Valor actual de la estadística
			
		Returns:
			True si el logro se desbloqueó con esta actualización
		"""
		if self.unlocked:
			return False
		
		self.progress = current_value
		return False  # Se evaluará en el manager
	
	def unlock(self) -> None:
		"""Marca el logro como desbloqueado."""
		if not self.unlocked:
			self.unlocked = True
			self.unlock_time = time.time()
			logging.info(f"🏆 Logro desbloqueado: {self.achievement_type.value}")
	
	def get_progress_percentage(self, target_value: float) -> float:
		"""Obtiene el porcentaje de progreso del logro.
		
		Args:
			target_value: Valor objetivo del logro
			
		Returns:
			Porcentaje de progreso (0.0 a 1.0)
		"""
		if self.unlocked or target_value <= 0:
			return 1.0
		
		return min(self.progress / target_value, 1.0)


class AchievementManager:
	"""Gestor principal del sistema de logros."""
	
	def __init__(self, database: Database, resource_manager: ResourceManager):
		"""Inicializa el gestor de logros.
		
		Args:
			database: Instancia de la base de datos
			resource_manager: Gestor de recursos para recompensas
		"""
		self.database = database
		self.resource_manager = resource_manager
		self.achievements: dict[AchievementType, Achievement] = {}
		self.achievement_info: dict[AchievementType, AchievementInfo] = {}
		
		self._initialize_achievement_info()
		self._initialize_achievements()
		self._create_tables()
		self._load_achievements()
		
		logging.info("Gestor de logros inicializado")
	
	def _create_tables(self):
		"""Crea las tablas necesarias en la base de datos."""
		self.database.execute('''
			CREATE TABLE IF NOT EXISTS achievements (
				achievement_id TEXT PRIMARY KEY,
				unlocked INTEGER DEFAULT 0,
				progress REAL DEFAULT 0.0,
				unlock_time REAL DEFAULT 0.0
			)
		''')
	
	def _initialize_achievement_info(self):
		"""Inicializa la información de todos los logros disponibles."""
		self.achievement_info = {
			# Logros de Clics
			AchievementType.CLICK_NOVICE: AchievementInfo(
				achievement_type=AchievementType.CLICK_NOVICE,
				name="Primer Clic",
				description="Haz tu primer clic",
				category=AchievementCategory.PROGRESSION,
				target_value=1,
				reward=AchievementReward(RewardType.COINS, 10),
				emoji="🖱️"
			),
			AchievementType.CLICK_APPRENTICE: AchievementInfo(
				achievement_type=AchievementType.CLICK_APPRENTICE,
				name="Haciendo Click",
				description="Haz 100 clics",
				category=AchievementCategory.PROGRESSION,
				target_value=100,
				reward=AchievementReward(RewardType.COINS, 100),
				emoji="🖱️"
			),
			AchievementType.CLICK_EXPERT: AchievementInfo(
				achievement_type=AchievementType.CLICK_EXPERT,
				name="Adicto al Click",
				description="Haz 1,000 clics",
				category=AchievementCategory.PROGRESSION,
				target_value=1000,
				reward=AchievementReward(RewardType.COINS, 1000),
				emoji="🖱️"
			),
			AchievementType.CLICK_MASTER: AchievementInfo(
				achievement_type=AchievementType.CLICK_MASTER,
				name="Maestro del Click",
				description="Haz 10,000 clics",
				category=AchievementCategory.PROGRESSION,
				target_value=10000,
				reward=AchievementReward(RewardType.COINS, 10000),
				emoji="🖱️"
			),
			AchievementType.CLICK_LEGEND: AchievementInfo(
				achievement_type=AchievementType.CLICK_LEGEND,
				name="Leyenda del Click",
				description="Haz 100,000 clics",
				category=AchievementCategory.PROGRESSION,
				target_value=100000,
				reward=AchievementReward(RewardType.COINS, 100000),
				emoji="🖱️"
			),
			
			# Logros de Monedas
			AchievementType.MONEY_FIRST: AchievementInfo(
				achievement_type=AchievementType.MONEY_FIRST,
				name="Primeras Monedas",
				description="Acumula 10 monedas",
				category=AchievementCategory.PROGRESSION,
				target_value=10,
				reward=AchievementReward(RewardType.COINS, 50),
				emoji="💰"
			),
			AchievementType.MONEY_RICH: AchievementInfo(
				achievement_type=AchievementType.MONEY_RICH,
				name="Rico",
				description="Acumula 1,000 monedas",
				category=AchievementCategory.PROGRESSION,
				target_value=1000,
				reward=AchievementReward(RewardType.COINS, 500),
				emoji="💰"
			),
			AchievementType.MONEY_MILLIONAIRE: AchievementInfo(
				achievement_type=AchievementType.MONEY_MILLIONAIRE,
				name="Millonario",
				description="Acumula 1,000,000 monedas",
				category=AchievementCategory.PROGRESSION,
				target_value=1000000,
				reward=AchievementReward(RewardType.COINS, 50000),
				emoji="💰"
			),
			AchievementType.MONEY_BILLIONAIRE: AchievementInfo(
				achievement_type=AchievementType.MONEY_BILLIONAIRE,
				name="Billonario",
				description="Acumula 1,000,000,000 monedas",
				category=AchievementCategory.PROGRESSION,
				target_value=1000000000,
				reward=AchievementReward(RewardType.COINS, 10000000),
				emoji="💰"
			),
			
			# Logros de Edificios
			AchievementType.BUILDING_FIRST: AchievementInfo(
				achievement_type=AchievementType.BUILDING_FIRST,
				name="Primera Granja",
				description="Compra tu primer edificio",
				category=AchievementCategory.PROGRESSION,
				target_value=1,
				reward=AchievementReward(RewardType.COINS, 25),
				emoji="🏗️"
			),
			AchievementType.BUILDING_EMPIRE: AchievementInfo(
				achievement_type=AchievementType.BUILDING_EMPIRE,
				name="Pequeño Imperio",
				description="Posee 10 edificios",
				category=AchievementCategory.PROGRESSION,
				target_value=10,
				reward=AchievementReward(RewardType.COINS, 1000),
				emoji="🏗️"
			),
			AchievementType.BUILDING_CORPORATION: AchievementInfo(
				achievement_type=AchievementType.BUILDING_CORPORATION,
				name="Gran Imperio",
				description="Posee 50 edificios",
				category=AchievementCategory.PROGRESSION,
				target_value=50,
				reward=AchievementReward(RewardType.COINS, 25000),
				emoji="🏗️"
			),
			AchievementType.BUILDING_MEGACORP: AchievementInfo(
				achievement_type=AchievementType.BUILDING_MEGACORP,
				name="Megacorporación",
				description="Posee 100 edificios",
				category=AchievementCategory.PROGRESSION,
				target_value=100,
				reward=AchievementReward(RewardType.COINS, 100000),
				emoji="🏗️"
			),
			
			# Logros de Mejoras
			AchievementType.UPGRADE_FIRST: AchievementInfo(
				achievement_type=AchievementType.UPGRADE_FIRST,
				name="Primera Mejora",
				description="Compra tu primera mejora",
				category=AchievementCategory.PROGRESSION,
				target_value=1,
				reward=AchievementReward(RewardType.COINS, 50),
				emoji="⚡"
			),
			AchievementType.UPGRADE_OPTIMIZER: AchievementInfo(
				achievement_type=AchievementType.UPGRADE_OPTIMIZER,
				name="Mejorador",
				description="Compra 5 mejoras",
				category=AchievementCategory.PROGRESSION,
				target_value=5,
				reward=AchievementReward(RewardType.COINS, 500),
				emoji="⚡"
			),
			AchievementType.UPGRADE_PERFECTIONIST: AchievementInfo(
				achievement_type=AchievementType.UPGRADE_PERFECTIONIST,
				name="Optimizador",
				description="Compra 15 mejoras",
				category=AchievementCategory.PROGRESSION,
				target_value=15,
				reward=AchievementReward(RewardType.COINS, 5000),
				emoji="⚡"
			),
		}
	
	def _initialize_achievements(self):
		"""Inicializa todos los logros con progreso 0."""
		for achievement_type in AchievementType:
			self.achievements[achievement_type] = Achievement(achievement_type)
	
	def _load_achievements(self):
		"""Carga el progreso de logros desde la base de datos."""
		try:
			results = self.database.fetch_all(
				"SELECT achievement_id, unlocked, progress, unlock_time FROM achievements"
			)
			
			for row in results:
				achievement_id, unlocked, progress, unlock_time = row
				try:
					achievement_type = AchievementType(achievement_id)
					achievement = self.achievements[achievement_type]
					achievement.unlocked = bool(unlocked)
					achievement.progress = progress
					achievement.unlock_time = unlock_time
				except ValueError:
					logging.warning(f"Logro desconocido en base de datos: {achievement_id}")
			
			unlocked_count = sum(1 for a in self.achievements.values() if a.unlocked)
			logging.info(f"Logros cargados: {unlocked_count}/{len(self.achievements)} desbloqueados")
		
		except Exception as e:
			logging.error(f"Error cargando logros: {e}")
	
	def save_achievements(self):
		"""Guarda el progreso de logros en la base de datos."""
		try:
			for achievement_type, achievement in self.achievements.items():
				self.database.execute('''
					INSERT OR REPLACE INTO achievements 
					(achievement_id, unlocked, progress, unlock_time)
					VALUES (?, ?, ?, ?)
				''', (
					achievement_type.value,
					int(achievement.unlocked),
					achievement.progress,
					achievement.unlock_time
				))
			
			logging.debug("Logros guardados correctamente")
		
		except Exception as e:
			logging.error(f"Error guardando logros: {e}")
	
	def get_achievement(self, achievement_type: AchievementType) -> Achievement:
		"""Obtiene un logro específico.
		
		Args:
			achievement_type: Tipo de logro
			
		Returns:
			Instancia del logro
		"""
		return self.achievements[achievement_type]
	
	def get_achievement_info(self, achievement_type: AchievementType) -> AchievementInfo:
		"""Obtiene la información de un logro.
		
		Args:
			achievement_type: Tipo de logro
			
		Returns:
			Información del logro
		"""
		return self.achievement_info[achievement_type]
	
	def check_achievement_progress(self, achievement_type: AchievementType, current_value: float) -> bool:
		"""Verifica y actualiza el progreso de un logro específico.
		
		Args:
			achievement_type: Tipo de logro a verificar
			current_value: Valor actual de la estadística
			
		Returns:
			True si el logro se desbloqueó
		"""
		achievement = self.achievements[achievement_type]
		if achievement.unlocked:
			return False
		
		info = self.achievement_info[achievement_type]
		achievement.update_progress(current_value)
		
		if current_value >= info.target_value:
			achievement.unlock()
			self._give_reward(info.reward)
			self.save_achievements()
			return True
		
		return False
	
	def check_click_achievements(self, total_clicks: int) -> list[AchievementType]:
		"""Verifica logros relacionados con clics.
		
		Args:
			total_clicks: Número total de clics
			
		Returns:
			Lista de logros desbloqueados
		"""
		unlocked = []
		click_achievements = [
			AchievementType.CLICK_NOVICE,
			AchievementType.CLICK_APPRENTICE,
			AchievementType.CLICK_EXPERT,
			AchievementType.CLICK_MASTER,
			AchievementType.CLICK_LEGEND
		]
		
		for achievement_type in click_achievements:
			if self.check_achievement_progress(achievement_type, total_clicks):
				unlocked.append(achievement_type)
		
		return unlocked
	
	def check_money_achievements(self, total_money: float) -> list[AchievementType]:
		"""Verifica logros relacionados con monedas.
		
		Args:
			total_money: Total de monedas acumuladas
			
		Returns:
			Lista de logros desbloqueados
		"""
		unlocked = []
		money_achievements = [
			AchievementType.MONEY_FIRST,
			AchievementType.MONEY_RICH,
			AchievementType.MONEY_MILLIONAIRE,
			AchievementType.MONEY_BILLIONAIRE
		]
		
		for achievement_type in money_achievements:
			if self.check_achievement_progress(achievement_type, total_money):
				unlocked.append(achievement_type)
		
		return unlocked
	
	def check_building_achievements(self, total_buildings: int) -> list[AchievementType]:
		"""Verifica logros relacionados con edificios.
		
		Args:
			total_buildings: Número total de edificios
			
		Returns:
			Lista de logros desbloqueados
		"""
		unlocked = []
		building_achievements = [
			AchievementType.BUILDING_FIRST,
			AchievementType.BUILDING_EMPIRE,
			AchievementType.BUILDING_CORPORATION,
			AchievementType.BUILDING_MEGACORP
		]
		
		for achievement_type in building_achievements:
			if self.check_achievement_progress(achievement_type, total_buildings):
				unlocked.append(achievement_type)
		
		return unlocked
	
	def check_upgrade_achievements(self, total_upgrades: int) -> list[AchievementType]:
		"""Verifica logros relacionados con mejoras.
		
		Args:
			total_upgrades: Número total de mejoras compradas
			
		Returns:
			Lista de logros desbloqueados
		"""
		unlocked = []
		upgrade_achievements = [
			AchievementType.UPGRADE_FIRST,
			AchievementType.UPGRADE_OPTIMIZER,
			AchievementType.UPGRADE_PERFECTIONIST
		]
		
		for achievement_type in upgrade_achievements:
			if self.check_achievement_progress(achievement_type, total_upgrades):
				unlocked.append(achievement_type)
		
		return unlocked
	
	def _give_reward(self, reward: AchievementReward):
		"""Otorga la recompensa por un logro completado.
		
		Args:
			reward: Recompensa a otorgar
		"""
		if reward.reward_type == RewardType.COINS:
			self.resource_manager.add_resource(reward.resource_type, reward.value)
			logging.info(f"💰 Recompensa otorgada: {reward.value} {reward.resource_type.value}")
		
		# TODO: Implementar otros tipos de recompensas (multiplicadores, etc.)
	
	def get_unlocked_count(self) -> int:
		"""Obtiene el número de logros desbloqueados.
		
		Returns:
			Número de logros completados
		"""
		return sum(1 for achievement in self.achievements.values() if achievement.unlocked)
	
	def get_total_count(self) -> int:
		"""Obtiene el número total de logros.
		
		Returns:
			Número total de logros disponibles
		"""
		return len(self.achievements)
	
	def get_achievements_by_category(self, category: AchievementCategory) -> list[AchievementType]:
		"""Obtiene logros por categoría.
		
		Args:
			category: Categoría de logros
			
		Returns:
			Lista de tipos de logros en la categoría
		"""
		return [
			achievement_type for achievement_type, info in self.achievement_info.items()
			if info.category == category
		]
