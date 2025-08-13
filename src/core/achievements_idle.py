"""
Sistema de Achievements para Idle Clicker - SiKIdle.

Sistema de logros específicamente diseñado para idle clickers con:
- Logros de progresión basados en hitos del juego
- Recompensas permanentes que persisten
- Categorías: Idle, Combat, Prestigio, Especiales
- Integración con GameState
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Callable, Any


class IdleAchievementCategory(Enum):
	"""Categorías de logros para idle clicker."""

	IDLE = "idle"
	COMBAT = "combat"
	PRESTIGE = "prestige"
	SPECIAL = "special"


@dataclass
class IdleAchievementReward:
	"""Recompensa de un logro de idle clicker."""

	coins_multiplier: float = 0.0  # Multiplicador permanente de monedas
	click_multiplier: float = 0.0  # Multiplicador permanente de clic
	building_multiplier: float = 0.0  # Multiplicador permanente de edificios
	prestige_bonus: float = 0.0  # Bonus permanente de prestigio
	coins_reward: int = 0  # Monedas inmediatas
	gems_reward: int = 0  # Gemas premium inmediatas


@dataclass
class IdleAchievement:
	"""Logro específico para idle clicker."""

	id: str
	name: str
	description: str
	category: IdleAchievementCategory
	target_value: int
	reward: IdleAchievementReward
	current_progress: int = 0
	completed: bool = False
	completion_date: Optional[datetime] = None

	def update_progress(self, new_value: int) -> bool:
		"""Actualiza el progreso del logro con un valor absoluto."""
		if self.completed:
			return False

		self.current_progress = new_value

		if self.current_progress >= self.target_value:
			self.completed = True
			self.completion_date = datetime.now()
			return True

		return False

	def get_progress_percentage(self) -> float:
		"""Obtiene el porcentaje de progreso."""
		if self.target_value <= 0:
			return 0.0
		return min(100.0, (self.current_progress / self.target_value) * 100.0)

	def get_symbol(self) -> str:
		"""Obtiene el emoji del logro según su categoría."""
		symbols = {
			IdleAchievementCategory.IDLE: "💰",
			IdleAchievementCategory.COMBAT: "⚔️",
			IdleAchievementCategory.PRESTIGE: "💎",
			IdleAchievementCategory.SPECIAL: "⭐",
		}
		return symbols.get(self.category, "🏆")


class IdleAchievementManager:
	"""Gestor de logros para idle clicker."""

	def __init__(self, database):
		"""Inicializa el gestor de logros."""
		self.database = database
		self.achievements: Dict[str, IdleAchievement] = {}
		self.completion_callbacks: List[Callable[[IdleAchievement], None]] = []

		self._create_tables()
		self._create_idle_achievements()
		self.load_data()

		logging.info(
			f"IdleAchievementManager initialized with {len(self.achievements)} achievements"
		)

	def _create_tables(self):
		"""Crea las tablas de achievements en la base de datos."""
		try:
			self.database.execute("""
				CREATE TABLE IF NOT EXISTS idle_achievements (
					id TEXT PRIMARY KEY,
					current_progress INTEGER DEFAULT 0,
					completed BOOLEAN DEFAULT FALSE,
					completion_date TIMESTAMP,
					created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
				)
			""")
			logging.debug("Tabla de idle achievements creada/verificada")
		except Exception as e:
			logging.error(f"Error creando tabla de achievements: {e}")

	def _create_idle_achievements(self):
		"""Crea los logros específicos para idle clicker."""
		achievements_data = [
			# IDLE CATEGORY - Logros de progresión básica
			{
				"id": "first_click",
				"name": "Primer Clic",
				"description": "Haz tu primer clic para ganar monedas",
				"category": IdleAchievementCategory.IDLE,
				"target_value": 1,
				"reward": IdleAchievementReward(
					click_multiplier=0.1, coins_reward=10, gems_reward=5
				),
			},
			{
				"id": "clicks_100",
				"name": "Clicker Novato",
				"description": "Haz 100 clics",
				"category": IdleAchievementCategory.IDLE,
				"target_value": 100,
				"reward": IdleAchievementReward(
					click_multiplier=0.2, coins_reward=100, gems_reward=10
				),
			},
			{
				"id": "clicks_1000",
				"name": "Clicker Experto",
				"description": "Haz 1,000 clics",
				"category": IdleAchievementCategory.IDLE,
				"target_value": 1000,
				"reward": IdleAchievementReward(
					click_multiplier=0.5, coins_reward=1000, gems_reward=25
				),
			},
			{
				"id": "first_building",
				"name": "Primer Generador",
				"description": "Compra tu primer edificio generador",
				"category": IdleAchievementCategory.IDLE,
				"target_value": 1,
				"reward": IdleAchievementReward(
					building_multiplier=0.1, coins_reward=50, gems_reward=8
				),
			},
			{
				"id": "buildings_10",
				"name": "Pequeño Empresario",
				"description": "Posee 10 edificios en total",
				"category": IdleAchievementCategory.IDLE,
				"target_value": 10,
				"reward": IdleAchievementReward(
					building_multiplier=0.2, coins_reward=500, gems_reward=15
				),
			},
			{
				"id": "buildings_50",
				"name": "Magnate Industrial",
				"description": "Posee 50 edificios en total",
				"category": IdleAchievementCategory.IDLE,
				"target_value": 50,
				"reward": IdleAchievementReward(
					building_multiplier=0.5, coins_reward=5000, gems_reward=40
				),
			},
			{
				"id": "coins_1k",
				"name": "Primeros Ahorros",
				"description": "Acumula 1,000 monedas",
				"category": IdleAchievementCategory.IDLE,
				"target_value": 1000,
				"reward": IdleAchievementReward(
					coins_multiplier=0.1, coins_reward=200, gems_reward=12
				),
			},
			{
				"id": "coins_100k",
				"name": "Rico",
				"description": "Acumula 100,000 monedas",
				"category": IdleAchievementCategory.IDLE,
				"target_value": 100000,
				"reward": IdleAchievementReward(
					coins_multiplier=0.3, coins_reward=10000, gems_reward=30
				),
			},
			{
				"id": "coins_1m",
				"name": "Millonario",
				"description": "Acumula 1,000,000 monedas",
				"category": IdleAchievementCategory.IDLE,
				"target_value": 1000000,
				"reward": IdleAchievementReward(
					coins_multiplier=0.5, coins_reward=100000, gems_reward=50
				),
			},
			# PRESTIGE CATEGORY - Logros de prestigio
			{
				"id": "first_prestige",
				"name": "Nuevo Comienzo",
				"description": "Realiza tu primer prestigio",
				"category": IdleAchievementCategory.PRESTIGE,
				"target_value": 1,
				"reward": IdleAchievementReward(
					prestige_bonus=0.1, coins_reward=1000, gems_reward=20
				),
			},
			{
				"id": "prestige_5",
				"name": "Veterano del Prestigio",
				"description": "Realiza 5 prestigios",
				"category": IdleAchievementCategory.PRESTIGE,
				"target_value": 5,
				"reward": IdleAchievementReward(
					prestige_bonus=0.2, coins_multiplier=0.2, gems_reward=35
				),
			},
			{
				"id": "crystals_10",
				"name": "Coleccionista de Cristales",
				"description": "Acumula 10 cristales de prestigio",
				"category": IdleAchievementCategory.PRESTIGE,
				"target_value": 10,
				"reward": IdleAchievementReward(
					prestige_bonus=0.3, building_multiplier=0.3, gems_reward=60
				),
			},
			# SPECIAL CATEGORY - Logros especiales
			{
				"id": "idle_master",
				"name": "Maestro del Idle",
				"description": "Completa 10 logros diferentes",
				"category": IdleAchievementCategory.SPECIAL,
				"target_value": 10,
				"reward": IdleAchievementReward(
					coins_multiplier=1.0,
					click_multiplier=1.0,
					building_multiplier=1.0,
					coins_reward=50000,
					gems_reward=100,
				),
			},
		]

		for data in achievements_data:
			achievement = IdleAchievement(**data)
			self.achievements[achievement.id] = achievement

		logging.info(f"Created {len(achievements_data)} idle achievements")

	def check_achievements(self, game_state):
		"""Verifica y actualiza el progreso de todos los logros."""
		newly_completed = []

		try:
			# Logros de clics
			total_clicks = getattr(game_state, "total_clicks", 0)
			if self._update_achievement_progress("first_click", total_clicks):
				newly_completed.append(self.achievements["first_click"])
			if self._update_achievement_progress("clicks_100", total_clicks):
				newly_completed.append(self.achievements["clicks_100"])
			if self._update_achievement_progress("clicks_1000", total_clicks):
				newly_completed.append(self.achievements["clicks_1000"])

			# Logros de edificios
			if hasattr(game_state, "building_manager"):
				total_buildings = sum(
					building.count for building in game_state.building_manager.buildings.values()
				)
				if self._update_achievement_progress("first_building", total_buildings):
					newly_completed.append(self.achievements["first_building"])
				if self._update_achievement_progress("buildings_10", total_buildings):
					newly_completed.append(self.achievements["buildings_10"])
				if self._update_achievement_progress("buildings_50", total_buildings):
					newly_completed.append(self.achievements["buildings_50"])

			# Logros de monedas
			current_coins = getattr(game_state, "coins", 0)
			if self._update_achievement_progress("coins_1k", current_coins):
				newly_completed.append(self.achievements["coins_1k"])
			if self._update_achievement_progress("coins_100k", current_coins):
				newly_completed.append(self.achievements["coins_100k"])
			if self._update_achievement_progress("coins_1m", current_coins):
				newly_completed.append(self.achievements["coins_1m"])

			# Logros de prestigio
			if hasattr(game_state, "prestige_manager"):
				prestige_count = game_state.prestige_manager.prestige_count
				prestige_crystals = game_state.prestige_manager.prestige_crystals

				if self._update_achievement_progress("first_prestige", prestige_count):
					newly_completed.append(self.achievements["first_prestige"])
				if self._update_achievement_progress("prestige_5", prestige_count):
					newly_completed.append(self.achievements["prestige_5"])
				if self._update_achievement_progress("crystals_10", prestige_crystals):
					newly_completed.append(self.achievements["crystals_10"])

			# Logro especial - Maestro del Idle
			completed_count = len(self.get_completed_achievements())
			if self._update_achievement_progress("idle_master", completed_count):
				newly_completed.append(self.achievements["idle_master"])

			# Procesar logros recién completados
			for achievement in newly_completed:
				self._on_achievement_completed(achievement, game_state)

		except Exception as e:
			logging.error(f"Error checking achievements: {e}")

		return newly_completed

	def _update_achievement_progress(self, achievement_id: str, new_value: int) -> bool:
		"""Actualiza el progreso de un logro específico."""
		if achievement_id not in self.achievements:
			return False

		achievement = self.achievements[achievement_id]
		was_completed = achievement.update_progress(new_value)

		if was_completed:
			self.save_achievement_data(achievement)
			logging.info(f"Achievement completed: {achievement.name}")

		return was_completed

	def _on_achievement_completed(self, achievement: IdleAchievement, game_state):
		"""Procesa un logro recién completado."""
		try:
			# Aplicar recompensas inmediatas
			if achievement.reward.coins_reward > 0:
				game_state.coins += achievement.reward.coins_reward

				# ⭐ SINCRONIZAR CON RESOURCE MANAGER
				if hasattr(game_state, "resource_manager"):
					from core.resources import ResourceType

					game_state.resource_manager.add_resource(
						ResourceType.COINS, achievement.reward.coins_reward
					)

				logging.info(f"Achievement reward: +{achievement.reward.coins_reward} coins")

			if achievement.reward.gems_reward > 0:
				if hasattr(game_state, "premium_shop_manager"):
					game_state.premium_shop_manager.gems += achievement.reward.gems_reward
					logging.info(f"Achievement reward: +{achievement.reward.gems_reward} gems")

			# Las recompensas de multiplicadores se aplicarán automáticamente
			# a través de get_achievement_multipliers()

			# Notificar callbacks
			for callback in self.completion_callbacks:
				try:
					callback(achievement)
				except Exception as e:
					logging.error(f"Error in achievement callback: {e}")

		except Exception as e:
			logging.error(f"Error processing achievement completion: {e}")

	def get_achievement_multipliers(self) -> Dict[str, float]:
		"""Obtiene todos los multiplicadores de logros completados."""
		multipliers = {
			"coins_multiplier": 1.0,
			"click_multiplier": 1.0,
			"building_multiplier": 1.0,
			"prestige_bonus": 0.0,
		}

		for achievement in self.achievements.values():
			if achievement.completed:
				multipliers["coins_multiplier"] += achievement.reward.coins_multiplier
				multipliers["click_multiplier"] += achievement.reward.click_multiplier
				multipliers["building_multiplier"] += achievement.reward.building_multiplier
				multipliers["prestige_bonus"] += achievement.reward.prestige_bonus

		return multipliers

	def get_all_achievements(self) -> List[IdleAchievement]:
		"""Obtiene todos los logros."""
		return list(self.achievements.values())

	def get_achievements_by_category(
		self, category: IdleAchievementCategory
	) -> List[IdleAchievement]:
		"""Obtiene logros por categoría."""
		return [
			achievement
			for achievement in self.achievements.values()
			if achievement.category == category
		]

	def get_completed_achievements(self) -> List[IdleAchievement]:
		"""Obtiene logros completados."""
		return [achievement for achievement in self.achievements.values() if achievement.completed]

	def get_completion_stats(self) -> Dict[str, Any]:
		"""Obtiene estadísticas de completado."""
		total = len(self.achievements)
		completed = len(self.get_completed_achievements())

		return {
			"total_achievements": total,
			"completed_achievements": completed,
			"completion_percentage": (completed / total * 100) if total > 0 else 0,
			"remaining_achievements": total - completed,
		}

	def add_completion_callback(self, callback: Callable[[IdleAchievement], None]):
		"""Añade un callback para cuando se completa un logro."""
		self.completion_callbacks.append(callback)

	def save_achievement_data(self, achievement: IdleAchievement):
		"""Guarda los datos de un logro específico."""
		try:
			self.database.execute(
				"""
				INSERT OR REPLACE INTO idle_achievements 
				(id, current_progress, completed, completion_date)
				VALUES (?, ?, ?, ?)
			""",
				(
					achievement.id,
					achievement.current_progress,
					achievement.completed,
					achievement.completion_date,
				),
			)
			logging.debug(f"Achievement data saved: {achievement.id}")
		except Exception as e:
			logging.error(f"Error saving achievement data: {e}")

	def load_data(self):
		"""Carga los datos de logros desde la base de datos."""
		try:
			results = self.database.execute("""
				SELECT id, current_progress, completed, completion_date
				FROM idle_achievements
			""")

			for row in results:
				achievement_id, progress, completed, completion_date = row
				if achievement_id in self.achievements:
					achievement = self.achievements[achievement_id]
					achievement.current_progress = progress
					achievement.completed = bool(completed)
					achievement.completion_date = completion_date

			completed_count = len(self.get_completed_achievements())
			logging.info(f"Loaded achievement data: {completed_count} completed")

		except Exception as e:
			logging.error(f"Error loading achievement data: {e}")

	def save_all_data(self):
		"""Guarda todos los datos de logros."""
		for achievement in self.achievements.values():
			self.save_achievement_data(achievement)
