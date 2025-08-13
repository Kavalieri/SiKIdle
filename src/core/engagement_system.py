"""
Sistema de Engagement y Retención para SiKIdle.

Sistemas para mantener a los jugadores comprometidos:
- Daily rewards
- Eventos temporales
- Progreso offline
- Metas diarias
- Sistema de rachas
"""

import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum


class RewardType(Enum):
	"""Tipos de recompensas diarias."""

	COINS = "coins"
	GEMS = "gems"
	MULTIPLIER = "multiplier"
	BOOST = "boost"


@dataclass
class DailyReward:
	"""Recompensa diaria."""

	day: int
	reward_type: RewardType
	amount: int
	duration_minutes: Optional[int] = None
	multiplier: Optional[float] = None


@dataclass
class DailyGoal:
	"""Meta diaria."""

	id: str
	name: str
	description: str
	target_value: int
	current_progress: int = 0
	completed: bool = False
	reward_coins: int = 0
	reward_gems: int = 0


class EngagementSystem:
	"""Sistema principal de engagement."""

	def __init__(self, game_state):
		self.game_state = game_state

		# Daily rewards
		self.current_streak = 0
		self.last_login_date = None
		self.daily_rewards_claimed = set()

		# Daily goals
		self.daily_goals = {}
		self.goals_reset_date = None

		# Offline progress
		self.last_save_time = time.time()
		self.max_offline_hours = 8
		self.offline_efficiency = 0.5  # 50% de producción offline

		# Eventos
		self.active_events = {}

		self._create_tables()
		self._setup_daily_rewards()
		self._setup_daily_goals()
		self.load_data()

		logging.info("EngagementSystem initialized")

	def _create_tables(self):
		"""Crea tablas de engagement."""
		try:
			db = self.game_state.save_manager.db

			db.execute("""
				CREATE TABLE IF NOT EXISTS engagement_data (
					id INTEGER PRIMARY KEY,
					current_streak INTEGER DEFAULT 0,
					last_login_date TEXT,
					daily_rewards_claimed TEXT DEFAULT '',
					goals_reset_date TEXT,
					last_save_time REAL,
					created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
				)
			""")

			db.execute("""
				CREATE TABLE IF NOT EXISTS daily_goals (
					id TEXT PRIMARY KEY,
					current_progress INTEGER DEFAULT 0,
					completed BOOLEAN DEFAULT FALSE,
					completion_date TEXT,
					created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
				)
			""")

			# Insertar fila inicial
			db.execute("INSERT OR IGNORE INTO engagement_data (id) VALUES (1)")

		except Exception as e:
			logging.error(f"Error creating engagement tables: {e}")

	def _setup_daily_rewards(self):
		"""Configura recompensas diarias progresivas."""
		self.daily_reward_cycle = [
			DailyReward(1, RewardType.COINS, 100),
			DailyReward(2, RewardType.GEMS, 5),
			DailyReward(3, RewardType.COINS, 250),
			DailyReward(4, RewardType.MULTIPLIER, 2, duration_minutes=60),
			DailyReward(5, RewardType.COINS, 500),
			DailyReward(6, RewardType.GEMS, 10),
			DailyReward(7, RewardType.BOOST, 3, duration_minutes=120),  # Mega reward
		]

	def _setup_daily_goals(self):
		"""Configura metas diarias."""
		daily_goals_templates = [
			{
				"id": "daily_clicks",
				"name": "Clicker Activo",
				"description": "Haz 50 clics",
				"target_value": 50,
				"reward_coins": 200,
				"reward_gems": 2,
			},
			{
				"id": "daily_buildings",
				"name": "Expansión",
				"description": "Compra 5 edificios",
				"target_value": 5,
				"reward_coins": 500,
				"reward_gems": 3,
			},
			{
				"id": "daily_earnings",
				"name": "Acumulador",
				"description": "Gana 10,000 monedas",
				"target_value": 10000,
				"reward_coins": 1000,
				"reward_gems": 5,
			},
		]

		for template in daily_goals_templates:
			goal = DailyGoal(**template)
			self.daily_goals[goal.id] = goal

	def check_daily_login(self):
		"""Verifica login diario y actualiza racha."""
		today = datetime.now().date()

		if self.last_login_date:
			last_date = datetime.fromisoformat(self.last_login_date).date()
			days_diff = (today - last_date).days

			if days_diff == 1:
				# Login consecutivo
				self.current_streak += 1
			elif days_diff > 1:
				# Racha rota
				self.current_streak = 1
			# Si days_diff == 0, ya logueado hoy
		else:
			# Primer login
			self.current_streak = 1

		self.last_login_date = today.isoformat()
		self.save_data()

		logging.info(f"Daily login: streak {self.current_streak}")
		return self.current_streak

	def can_claim_daily_reward(self, day: int) -> bool:
		"""Verifica si se puede reclamar recompensa diaria."""
		today = datetime.now().date().isoformat()
		reward_key = f"{today}_{day}"

		return day <= self.current_streak and reward_key not in self.daily_rewards_claimed

	def claim_daily_reward(self, day: int) -> Optional[DailyReward]:
		"""Reclama recompensa diaria."""
		if not self.can_claim_daily_reward(day):
			return None

		# Encontrar recompensa (ciclo de 7 días)
		reward_index = (day - 1) % len(self.daily_reward_cycle)
		reward = self.daily_reward_cycle[reward_index]

		# Aplicar recompensa
		if reward.reward_type == RewardType.COINS:
			self.game_state.coins += reward.amount
		elif reward.reward_type == RewardType.GEMS:
			if hasattr(self.game_state, "premium_shop_manager"):
				self.game_state.premium_shop_manager.add_gems(reward.amount, "daily_reward")
		elif reward.reward_type == RewardType.MULTIPLIER:
			# Activar boost temporal
			self._activate_daily_boost("coin_multiplier", reward.amount, reward.duration_minutes)
		elif reward.reward_type == RewardType.BOOST:
			# Mega boost
			self._activate_daily_boost("mega_boost", reward.amount, reward.duration_minutes)

		# Marcar como reclamada
		today = datetime.now().date().isoformat()
		reward_key = f"{today}_{day}"
		self.daily_rewards_claimed.add(reward_key)

		self.save_data()
		logging.info(f"Daily reward claimed: day {day}, {reward.reward_type.value}")

		return reward

	def _activate_daily_boost(self, boost_type: str, multiplier: float, duration_minutes: int):
		"""Activa boost temporal desde daily reward."""
		if hasattr(self.game_state, "premium_shop_manager"):
			from core.premium_shop import BoostType

			if boost_type == "coin_multiplier":
				boost_enum = BoostType.COIN_MULTIPLIER
			else:
				boost_enum = BoostType.COIN_MULTIPLIER  # Default

			# Simular activación de boost
			end_time = time.time() + (duration_minutes * 60)
			self.game_state.premium_shop_manager.active_boosts[boost_enum] = {
				"multiplier": multiplier,
				"end_time": end_time,
			}
			self.game_state.premium_shop_manager._save_active_boosts()

	def update_daily_goals(self):
		"""Actualiza progreso de metas diarias."""
		today = datetime.now().date()

		# Reset diario si es necesario
		if (
			not self.goals_reset_date
			or datetime.fromisoformat(self.goals_reset_date).date() < today
		):
			self._reset_daily_goals()
			self.goals_reset_date = today.isoformat()

		# Actualizar progreso
		if "daily_clicks" in self.daily_goals:
			total_clicks = getattr(self.game_state, "total_clicks", 0)
			self.daily_goals["daily_clicks"].current_progress = min(
				total_clicks, self.daily_goals["daily_clicks"].target_value
			)

		if "daily_buildings" in self.daily_goals and hasattr(self.game_state, "building_manager"):
			buildings_today = sum(
				building.count for building in self.game_state.building_manager.buildings.values()
			)
			self.daily_goals["daily_buildings"].current_progress = min(
				buildings_today, self.daily_goals["daily_buildings"].target_value
			)

		if "daily_earnings" in self.daily_goals:
			current_coins = getattr(self.game_state, "coins", 0)
			self.daily_goals["daily_earnings"].current_progress = min(
				current_coins, self.daily_goals["daily_earnings"].target_value
			)

		# Verificar completados
		newly_completed = []
		for goal in self.daily_goals.values():
			if not goal.completed and goal.current_progress >= goal.target_value:
				goal.completed = True
				newly_completed.append(goal)
				self._reward_daily_goal(goal)

		if newly_completed:
			self.save_data()

		return newly_completed

	def _reset_daily_goals(self):
		"""Resetea metas diarias."""
		for goal in self.daily_goals.values():
			goal.current_progress = 0
			goal.completed = False

		logging.info("Daily goals reset")

	def _reward_daily_goal(self, goal: DailyGoal):
		"""Otorga recompensa por meta diaria completada."""
		if goal.reward_coins > 0:
			self.game_state.coins += goal.reward_coins

		if goal.reward_gems > 0 and hasattr(self.game_state, "premium_shop_manager"):
			self.game_state.premium_shop_manager.add_gems(goal.reward_gems, f"daily_goal_{goal.id}")

		logging.info(f"Daily goal completed: {goal.name}")

	def calculate_offline_earnings(self) -> Dict[str, Any]:
		"""Calcula ganancias offline."""
		current_time = time.time()
		offline_seconds = min(current_time - self.last_save_time, self.max_offline_hours * 3600)

		if offline_seconds < 60:  # Menos de 1 minuto
			return {"coins": 0, "time_away": 0}

		# Calcular producción offline
		offline_coins = 0
		if hasattr(self.game_state, "building_manager"):
			total_production = 0
			for building in self.game_state.building_manager.buildings.values():
				if building.count > 0:
					info = self.game_state.building_manager.get_building_info(
						building.building_type
					)
					production = building.get_total_production_per_second(info)
					total_production += production

			# Aplicar eficiencia offline y multiplicadores
			multipliers = self.game_state.prestige_manager.get_multipliers()
			offline_coins = int(
				total_production
				* offline_seconds
				* self.offline_efficiency
				* multipliers["building_multiplier"]
			)

		self.last_save_time = current_time

		return {
			"coins": offline_coins,
			"time_away": offline_seconds,
			"hours_away": offline_seconds / 3600,
			"efficiency": self.offline_efficiency,
		}

	def apply_offline_earnings(self) -> Dict[str, Any]:
		"""Aplica ganancias offline al juego."""
		earnings = self.calculate_offline_earnings()

		if earnings["coins"] > 0:
			self.game_state.coins += earnings["coins"]
			self.save_data()
			logging.info(f"Offline earnings applied: {earnings['coins']} coins")

		return earnings

	def get_engagement_stats(self) -> Dict[str, Any]:
		"""Obtiene estadísticas de engagement."""
		completed_goals = len([g for g in self.daily_goals.values() if g.completed])
		total_goals = len(self.daily_goals)

		return {
			"current_streak": self.current_streak,
			"daily_goals_completed": completed_goals,
			"daily_goals_total": total_goals,
			"daily_goals_progress": (completed_goals / total_goals * 100) if total_goals > 0 else 0,
			"max_offline_hours": self.max_offline_hours,
			"offline_efficiency": self.offline_efficiency * 100,
		}

	def save_data(self):
		"""Guarda datos de engagement."""
		try:
			db = self.game_state.save_manager.db

			# Datos principales
			rewards_claimed_str = ",".join(self.daily_rewards_claimed)

			db.execute(
				"""
				UPDATE engagement_data 
				SET current_streak = ?, last_login_date = ?, daily_rewards_claimed = ?,
					goals_reset_date = ?, last_save_time = ?
				WHERE id = 1
			""",
				(
					self.current_streak,
					self.last_login_date,
					rewards_claimed_str,
					self.goals_reset_date,
					self.last_save_time,
				),
			)

			# Metas diarias
			for goal in self.daily_goals.values():
				db.execute(
					"""
					INSERT OR REPLACE INTO daily_goals 
					(id, current_progress, completed, completion_date)
					VALUES (?, ?, ?, ?)
				""",
					(
						goal.id,
						goal.current_progress,
						goal.completed,
						datetime.now().isoformat() if goal.completed else None,
					),
				)

			logging.debug("Engagement data saved")

		except Exception as e:
			logging.error(f"Error saving engagement data: {e}")

	def load_data(self):
		"""Carga datos de engagement."""
		try:
			db = self.game_state.save_manager.db

			# Datos principales
			result = db.execute("""
				SELECT current_streak, last_login_date, daily_rewards_claimed,
					   goals_reset_date, last_save_time
				FROM engagement_data WHERE id = 1
			""")

			if result:
				row = result[0] if result else None
				if row:
					(
						self.current_streak,
						self.last_login_date,
						rewards_claimed_str,
						self.goals_reset_date,
						self.last_save_time,
					) = row

					if rewards_claimed_str:
						self.daily_rewards_claimed = set(rewards_claimed_str.split(","))

					if not self.last_save_time:
						self.last_save_time = time.time()

			# Metas diarias
			goal_results = db.execute("""
				SELECT id, current_progress, completed
				FROM daily_goals
			""")

			for goal_id, progress, completed in goal_results:
				if goal_id in self.daily_goals:
					self.daily_goals[goal_id].current_progress = progress
					self.daily_goals[goal_id].completed = bool(completed)

			logging.info(f"Engagement data loaded: streak {self.current_streak}")

		except Exception as e:
			logging.error(f"Error loading engagement data: {e}")
