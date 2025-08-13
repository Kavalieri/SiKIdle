"""Lógica principal del juego SiKIdle.

Contiene la clase GameState que gestiona todo el estado del juego,
incluyendo múltiples recursos, clics, multiplicadores y bonificaciones.
"""

import logging
import time
from typing import Any, Dict, List

from utils.save import get_save_manager
from core.resources import ResourceManager, ResourceType
from core.buildings import BuildingManager
from core.upgrades import UpgradeManager
from core.achievements import AchievementManager
from core.inventory import Inventory
from core.dungeons import DungeonManager
from core.combat import CombatManager
from core.player_stats import PlayerStatsManager


class GameState:
	"""Gestiona el estado principal del juego idle clicker."""

	def __init__(self):
		"""Inicializa el estado del juego."""
		self.save_manager = get_save_manager()

		# Sistema de recursos múltiples
		self.resource_manager = ResourceManager()

		# Sistema de edificios generadores
		self.building_manager = BuildingManager(self.resource_manager)

		# Sistema de mejoras permanentes
		self.upgrade_manager = UpgradeManager(self.resource_manager)

		# Sistema de logros para idle clicker
		from core.achievements_idle import IdleAchievementManager
		self.achievement_manager = IdleAchievementManager(self.save_manager.db)

		# Sistema de inventario y loot
		self.inventory = Inventory()

		# Nuevos sistemas: Combat y Mazmorras
		self.player_stats = PlayerStatsManager()
		from core.combat import Player

		self.player = Player(stats_manager=self.player_stats)
		self.combat_manager = CombatManager(self.player)
		self.dungeon_manager = DungeonManager(self.resource_manager)

		# Sistema de desbloqueo avanzado de mazmorras
		from core.dungeon_unlock import DungeonUnlockManager

		self.unlock_manager = DungeonUnlockManager(self.dungeon_manager, self.resource_manager)

		# Sistema de loot y generación
		from core.loot import LootGenerator
		from core.loot_combat_integration import LootCombatIntegration

		self.loot_generator = LootGenerator()
		self.loot_combat_integration = LootCombatIntegration(
			combat_manager=self.combat_manager,
			loot_generator=self.loot_generator,
			inventory=self.inventory,
			biome_manager=self.dungeon_manager.biome_manager,
		)

		# Configurar callback para registro de derrotas de enemigos
		self.combat_manager.set_enemy_defeat_callback(self.register_enemy_defeat)

		# Sistema de prestigio integrado
		from core.prestige_simple import PrestigeManager
		self.prestige_manager = PrestigeManager(self.save_manager.db)
		
		# Mantener compatibilidad con variables existentes
		self.prestige_crystals = 0
		self.total_prestiges = 0
		self.lifetime_coins = 0.0
		self.prestige_multiplier = 1.0

		# Sistema de talentos (implementación básica)
		self.talent_points = 0
		self.total_talent_points_earned = 0
		self.player_level = 1
		self.player_experience = 0
		self.talents = {}  # Dict[str, int] - talent_name: level
		self.talent_multipliers = {
			"click_income": 1.0,
			"building_income": 1.0,
			"building_cost_reduction": 0.0,
			"critical_chance": 0.0,
			"critical_damage": 1.0,
			"experience_gain": 1.0,
		}

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

		# Sistema de optimización de performance
		from utils.performance import get_performance_optimizer
		self.performance_optimizer = get_performance_optimizer()
		
		# Sistema de flujo de gameplay tradicional
		from core.gameplay_flow import GameplayFlowManager
		self.gameplay_flow = GameplayFlowManager(self)
		
		# Sistema de balanceo para estancamiento natural
		from core.balance_manager import BalanceManager
		self.balance_manager = BalanceManager(self)
		
		# Sistema de integración Combat-Idle
		from core.combat_idle_integration import CombatIdleIntegration
		self.combat_idle_integration = CombatIdleIntegration(self)
		
		# Sistema de tienda premium
		from core.premium_shop import PremiumShopManager
		self.premium_shop = PremiumShopManager(self)
		
		# Sistema de engagement y retención
		from core.engagement_system import EngagementSystem
		self.engagement_system = EngagementSystem(self)
		
		# Optimización móvil
		from utils.mobile_optimization import mobile_optimizer, animation_manager, performance_monitor
		self.mobile_optimizer = mobile_optimizer
		self.animation_manager = animation_manager
		self.mobile_performance_monitor = performance_monitor
		
		# Cargar estado guardado
		self.load_game()
		
		# Sincronizar datos de prestigio con el manager
		self._sync_prestige_data()

		logging.info("Juego inicializado: %d monedas, %d clics totales", self.coins, self.total_clicks)

	def start_game(self) -> None:
		"""Inicia el juego y comienza el guardado automático."""
		self.game_running = True
		self.session_start_time = time.time()
		self.session_clicks = 0
		self.session_coins = 0

		# Iniciar guardado automático
		self.save_manager.start_auto_save()

		# Iniciar producción automática de edificios
		from kivy.clock import Clock
		Clock.schedule_interval(self._auto_collect_buildings, 1.0)  # Cada segundo
		
		# Iniciar verificación periódica de achievements
		Clock.schedule_interval(self._check_achievements_periodic, 3.0)  # Cada 3 segundos
		
		# Verificar login diario y aplicar ganancias offline
		self.engagement_system.check_daily_login()
		offline_earnings = self.engagement_system.apply_offline_earnings()
		if offline_earnings['coins'] > 0:
			logging.info(f"Offline earnings: {offline_earnings['coins']} coins ({offline_earnings['hours_away']:.1f}h away)")
		
		# Iniciar actualización de metas diarias
		Clock.schedule_interval(self._update_daily_goals, 30.0)  # Cada 30 segundos

		# Incrementar estadística de sesiones
		self.save_manager.increment_stat("sessions_played", 1)

		logging.info("Juego iniciado")
	
	def _auto_collect_buildings(self, dt):
		"""Recolecta automáticamente la producción de edificios (optimizado)."""
		if not self.game_running:
			return False  # Detener el clock
		
		# Usar optimizador de performance
		produced = self.performance_optimizer.optimize_building_production(
			self.building_manager, dt
		)
		
		if produced and produced.get('coins', 0) > 0:
			coins_produced = produced['coins']
			# Sincronizar con el sistema tradicional de monedas
			self.coins += int(coins_produced)
			
			# Solo log si es significativo y no muy frecuente
			if coins_produced > 1.0 and self.performance_optimizer.should_update_ui('low'):
				logging.debug(f"Producción: +{coins_produced:.1f} monedas (Total: {self.coins:,})")
		
		# Registrar frame para monitoreo
		self.performance_optimizer.record_frame()
		
		return True  # Continuar el clock
	
	def _check_achievements_periodic(self, dt):
		"""Verifica achievements periódicamente (optimizado)."""
		if not self.game_running:
			return False  # Detener el clock
		
		try:
			# Usar optimizador para verificación eficiente
			completed_ids = self.performance_optimizer.optimize_achievement_check(
				self.achievement_manager, self
			)
			
			if completed_ids:
				for achievement_id in completed_ids:
					achievement = self.achievement_manager.achievements[achievement_id]
					logging.info(f"🏆 Achievement unlocked: {achievement.name}")
					
					# Aplicar recompensas inmediatas
					if achievement.reward.coins_reward > 0:
						self.coins += achievement.reward.coins_reward
					
					# Guardar achievement
					self.achievement_manager.save_achievement_data(achievement)
					
		except Exception as e:
			logging.debug(f"Periodic achievement check error: {e}")
		
		# Ajustar performance cada 10 verificaciones
		if hasattr(self, '_perf_check_count'):
			self._perf_check_count += 1
		else:
			self._perf_check_count = 1
			
		if self._perf_check_count % 10 == 0:
			self.performance_optimizer.adjust_performance()
			
			# Actualizar flujo de gameplay cada 10 verificaciones
			if hasattr(self, 'gameplay_flow'):
				self.gameplay_flow.update_phase()
		
		return True  # Continuar el clock
	
	def _update_daily_goals(self, dt):
		"""Actualiza progreso de metas diarias."""
		if not self.game_running:
			return False
		
		try:
			newly_completed = self.engagement_system.update_daily_goals()
			for goal in newly_completed:
				logging.info(f"🎯 Daily goal completed: {goal.name}")
		except Exception as e:
			logging.debug(f"Daily goals update error: {e}")
		
		return True

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
		
		# Limpiar optimizador de performance
		if hasattr(self, 'performance_optimizer'):
			self.performance_optimizer.cleanup()

		logging.info(
			"Juego detenido. Sesión: %ds, Clics: %d, Monedas: %d", session_time, self.session_clicks, self.session_coins
		)

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

		# Aplicar multiplicadores de mejoras
		upgrade_multiplier = self.upgrade_manager.get_click_multiplier()

		# Aplicar multiplicador de prestigio desde el manager
		prestige_multiplier = self.prestige_manager.get_multipliers()['click_multiplier']

		# Aplicar multiplicadores de talentos
		talent_click_multiplier = self.talent_multipliers["click_income"]
		
		# Aplicar multiplicadores de achievements
		achievement_multipliers = self.achievement_manager.get_achievement_multipliers()
		achievement_click_multiplier = achievement_multipliers['click_multiplier']
		
		# Aplicar multiplicadores de combat
		combat_multipliers = self.combat_idle_integration.get_active_multipliers()
		combat_click_multiplier = combat_multipliers['click_multiplier']
		
		# Aplicar multiplicadores premium
		premium_multipliers = self.premium_shop.get_active_multipliers()
		premium_click_multiplier = premium_multipliers['click_multiplier']

		total_multiplier = (
			current_multiplier * upgrade_multiplier * prestige_multiplier * 
			talent_click_multiplier * achievement_click_multiplier * 
			combat_click_multiplier * premium_click_multiplier
		)

		coins_earned = int(base_coins * total_multiplier)

		# Actualizar estado tradicional (compatibilidad)
		self.coins += coins_earned

		# Actualizar sistema de recursos múltiples
		self.resource_manager.add_resource(ResourceType.COINS, coins_earned)

		# Actualizar lifetime coins para prestigio
		self.lifetime_coins += coins_earned

		# Ganar experiencia por clic
		exp_earned = 1
		self.add_experience(exp_earned)
		self.resource_manager.add_resource(ResourceType.EXPERIENCE, exp_earned)

		self.total_clicks += 1
		self.session_clicks += 1
		self.session_coins += coins_earned

		# Incrementar estadísticas
		self.save_manager.increment_stat("clicks_today", 1)
		self.save_manager.increment_stat("coins_earned_today", coins_earned)

		# Verificar logros de idle clicker
		try:
			newly_completed = self.achievement_manager.check_achievements(self)
			if newly_completed:
				for achievement in newly_completed:
					logging.info(f"🏆 Achievement unlocked: {achievement.name}")
		except Exception as e:
			logging.debug(f"Achievement check error: {e}")

		return coins_earned

	def update_building_production(self) -> dict:
		"""Actualiza la producción de todos los edificios.

		Returns:
			Diccionario con recursos producidos
		"""
		if not self.game_running:
			return {}

		# Actualizar multiplicadores en el building manager
		prestige_multipliers = self.prestige_manager.get_multipliers()
		achievement_multipliers = self.achievement_manager.get_achievement_multipliers()
		combat_multipliers = self.combat_idle_integration.get_active_multipliers()
		premium_multipliers = self.premium_shop.get_active_multipliers()
		
		# Combinar todos los multiplicadores
		combined_multiplier = (
			prestige_multipliers['building_multiplier'] * 
			achievement_multipliers['building_multiplier'] *
			combat_multipliers['building_multiplier'] *
			premium_multipliers['building_multiplier']
		)
		self.building_manager.set_prestige_multiplier(combined_multiplier)

		# Recolectar producción de edificios
		produced = self.building_manager.collect_all_production()

		# Actualizar lifetime coins si se produjeron monedas
		if ResourceType.COINS in produced:
			self.lifetime_coins += produced[ResourceType.COINS]
			# También actualizar en el prestige manager
			self.prestige_manager.lifetime_coins = self.lifetime_coins

		return produced

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

		logging.info("Bonificación aplicada: x%.1f durante %ds", float(multiplier), int(duration))
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
		self.resource_manager.subtract_resource(ResourceType.COINS, amount)
		return True

	def on_building_purchased(self, building_type, new_count: int) -> None:
		"""Hook llamado cuando se compra un edificio.

		Args:
			building_type: Tipo de edificio comprado
			new_count: Cantidad total del edificio después de la compra
		"""
		# Verificar logros de edificios
		total_buildings = 0
		try:
			total_buildings = sum(building.count for building in self.building_manager.buildings.values())
			if hasattr(self.achievement_manager, 'check_building_achievements'):
				self.achievement_manager.check_building_achievements(total_buildings)
		except Exception as e:
			logging.debug(f"Building achievement check error: {e}")

		logging.debug("Edificio comprado: %s, total buildings: %d", building_type, total_buildings)

	def on_upgrade_purchased(self, upgrade_type) -> None:
		"""Hook llamado cuando se compra una mejora.

		Args:
			upgrade_type: Tipo de mejora comprada
		"""
		# Verificar logros de mejoras
		try:
			total_upgrades = sum(
				1 for upgrade in self.upgrade_manager.upgrades.values() if upgrade.level > 0
			)
			if hasattr(self.achievement_manager, 'check_upgrade_achievements'):
				self.achievement_manager.check_upgrade_achievements(total_upgrades)
		except Exception as e:
			logging.debug(f"Upgrade achievement check error: {e}")

		logging.debug("Mejora comprada: %s, total upgrades: %d", upgrade_type, total_upgrades)

	def get_game_stats(self) -> dict[str, Any]:
		"""Obtiene estadísticas completas del juego.

		Returns:
			Diccionario con todas las estadísticas
		"""
		current_session_time = 0
		if self.game_running:
			current_session_time = int(time.time() - self.session_start_time)

		stats = {
			"coins": self.coins,
			"total_clicks": self.total_clicks,
			"multiplier": self.multiplier,
			"current_multiplier": self.get_current_multiplier(),
			"total_playtime": self.total_playtime + current_session_time,
			"session_clicks": self.session_clicks,
			"session_coins": self.session_coins,
			"session_time": current_session_time,
			"bonus_active": self.is_bonus_active(),
			"bonus_time_remaining": self.get_bonus_time_remaining(),
			"clicks_today": self.save_manager.db.get_stat("clicks_today"),
			"coins_earned_today": self.save_manager.db.get_stat("coins_earned_today"),
			"sessions_played": self.save_manager.db.get_stat("sessions_played"),
		}
		
		# Añadir estadísticas de performance si está disponible
		if hasattr(self, 'performance_optimizer'):
			stats['performance'] = self.performance_optimizer.get_performance_stats()
		
		return stats
	
	def simulate_combat_victory(self, enemy_level: int = None) -> Dict[str, Any]:
		"""Simula una victoria de combat para testing."""
		if not hasattr(self, 'combat_idle_integration'):
			return {'error': 'Combat integration not available'}
		
		# Usar nivel basado en progreso si no se especifica
		if enemy_level is None:
			enemy_level = max(1, self.coins // 10000)  # 1 nivel por cada 10K monedas
		
		# Simular combat con performance aleatoria
		import random
		damage_dealt = enemy_level * random.uniform(80, 120)  # 80-120% del esperado
		time_taken = enemy_level * random.uniform(3, 7)       # 3-7 segundos por nivel
		
		return self.combat_idle_integration.process_combat_victory(
			enemy_level, damage_dealt, time_taken
		)

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
			"coins": self.coins,
			"total_clicks": self.total_clicks,
			"multiplier": self.multiplier,
			"total_playtime": self.total_playtime + current_session_time,
			"resources": self.resource_manager.get_save_data(),
			"buildings": self.building_manager.get_save_data(),
			"upgrades": self.upgrade_manager.get_save_data(),
			# Datos de prestigio (sincronizados con PrestigeManager)
			"prestige_crystals": self.prestige_manager.prestige_crystals,
			"total_prestiges": self.prestige_manager.prestige_count,
			"lifetime_coins": self.prestige_manager.lifetime_coins,
			"prestige_multiplier": self.prestige_manager.income_multiplier,
			# Datos de talentos y experiencia
			"player_level": self.player_level,
			"player_experience": self.player_experience,
			"talent_points": self.talent_points,
			"total_talent_points_earned": self.total_talent_points_earned,
			"talents": self.talents.copy(),
			# Datos de combat y mazmorras
			"combat_stats": self.player_stats.get_save_data() if hasattr(self.player_stats, 'get_save_data') else {},
			"dungeon_progress": self.dungeon_manager.get_save_data() if hasattr(self.dungeon_manager, 'get_save_data') else {},
			"inventory": self.inventory.get_save_data() if hasattr(self.inventory, 'get_save_data') else {},
			# Datos de engagement
			"engagement_data": self.engagement_system.get_engagement_stats() if hasattr(self, 'engagement_system') else {},
		}

		return self.save_manager.save_game_state(game_state)

	def load_game(self) -> None:
		"""Carga el estado del juego desde el sistema de guardado."""
		saved_state = self.save_manager.load_game_state()

		self.coins = saved_state.get("coins", 0)
		self.total_clicks = saved_state.get("total_clicks", 0)
		self.multiplier = saved_state.get("multiplier", 1.0)
		self.total_playtime = saved_state.get("total_playtime", 0)

		# Cargar recursos si existen
		if "resources" in saved_state:
			self.resource_manager.load_save_data(saved_state["resources"])

		# Cargar edificios si existen
		if "buildings" in saved_state:
			self.building_manager.load_save_data(saved_state["buildings"])

		# Cargar mejoras si existen
		if "upgrades" in saved_state:
			self.upgrade_manager.load_save_data(saved_state["upgrades"])

		# Cargar datos de prestigio en variables de compatibilidad
		self.prestige_crystals = saved_state.get("prestige_crystals", 0)
		self.total_prestiges = saved_state.get("total_prestiges", 0)
		self.lifetime_coins = saved_state.get("lifetime_coins", 0.0)
		self.prestige_multiplier = saved_state.get("prestige_multiplier", 1.0)
		
		# Sincronizar con PrestigeManager si hay datos guardados
		if self.prestige_crystals > 0 or self.total_prestiges > 0:
			self.prestige_manager.prestige_crystals = self.prestige_crystals
			self.prestige_manager.prestige_count = self.total_prestiges
			self.prestige_manager.lifetime_coins = self.lifetime_coins
			self.prestige_manager.income_multiplier = self.prestige_multiplier
			self.prestige_manager.click_multiplier = self.prestige_multiplier
			self.prestige_manager.save_data()

		# Cargar datos de talentos y experiencia
		self.player_level = saved_state.get("player_level", 1)
		self.player_experience = saved_state.get("player_experience", 0)
		self.talent_points = saved_state.get("talent_points", 0)
		self.total_talent_points_earned = saved_state.get("total_talent_points_earned", 0)
		self.talents = saved_state.get("talents", {})

		# Recalcular multiplicadores de talentos
		self._update_talent_multipliers()

		# Cargar datos de combat si existen
		if "combat_stats" in saved_state and hasattr(self.player_stats, 'load_save_data'):
			try:
				self.player_stats.load_save_data(saved_state["combat_stats"])
			except Exception as e:
				logging.warning(f"Error cargando stats de combat: {e}")

		# Cargar progreso de mazmorras si existe
		if "dungeon_progress" in saved_state and hasattr(self.dungeon_manager, 'load_save_data'):
			try:
				self.dungeon_manager.load_save_data(saved_state["dungeon_progress"])
			except Exception as e:
				logging.warning(f"Error cargando progreso de mazmorras: {e}")

		# Cargar inventario si existe
		if "inventory" in saved_state and hasattr(self.inventory, 'load_save_data'):
			try:
				self.inventory.load_save_data(saved_state["inventory"])
			except Exception as e:
				logging.warning(f"Error cargando inventario: {e}")

		# Sincronizar coins con el sistema de recursos
		self.resource_manager.set_resource(ResourceType.COINS, self.coins)

		logging.info("Estado cargado: %d monedas, %d clics, nivel %d", self.coins, self.total_clicks, self.player_level)

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

	def _sync_prestige_data(self):
		"""Sincroniza datos de prestigio entre GameState y PrestigeManager."""
		try:
			# Obtener stats del manager
			stats = self.prestige_manager.get_stats()
			
			# Sincronizar variables de compatibilidad
			self.prestige_crystals = stats['prestige_crystals']
			self.total_prestiges = stats['prestige_count']
			self.prestige_multiplier = stats['income_multiplier']
			
			# Sincronizar lifetime_coins si el manager tiene más
			if stats['lifetime_coins'] > self.lifetime_coins:
				self.lifetime_coins = stats['lifetime_coins']
			else:
				self.prestige_manager.lifetime_coins = self.lifetime_coins
			
			logging.debug(f"Datos de prestigio sincronizados: {stats['prestige_crystals']} cristales, {stats['prestige_count']} prestiges")
			
		except Exception as e:
			logging.error(f"Error sincronizando datos de prestigio: {e}")

	def can_prestige(self) -> bool:
		"""Verifica si se puede realizar un prestigio.

		Returns:
			True si se puede realizar prestigio
		"""
		return self.prestige_manager.can_prestige(self.lifetime_coins + self.coins)

	def calculate_prestige_crystals(self) -> int:
		"""Calcula cuántos cristales se ganarían con prestigio.

		Returns:
			Número de cristales que se obtendrían
		"""
		return self.prestige_manager.calculate_crystals_from_coins(self.lifetime_coins + self.coins)

	def perform_prestige(self) -> bool:
		"""Realiza un prestigio usando el PrestigeManager.

		Returns:
			True si el prestigio fue exitoso
		"""
		# Actualizar lifetime_coins con monedas actuales
		total_coins = self.lifetime_coins + self.coins
		
		# Realizar prestigio a través del manager
		result = self.prestige_manager.perform_prestige(total_coins)
		
		if result['success']:
			# Resetear progreso del juego
			self.reset_for_prestige()
			
			# Sincronizar datos
			self._sync_prestige_data()
			
			logging.info(f"Prestigio completado: {result}")
			return True
		
		return False

	def reset_for_prestige(self):
		"""Resetea el progreso del juego para prestigio."""
		# Resetear progreso básico
		self.coins = 0
		self.total_clicks = 0
		self.multiplier = 1.0
		
		# Resetear recursos
		self.resource_manager.resources = {
			resource_type: 0 for resource_type in self.resource_manager.resources
		}
		
		# Resetear edificios
		for building in self.building_manager.buildings.values():
			building.count = 0
		
		# Resetear mejoras
		for upgrade in self.upgrade_manager.upgrades.values():
			upgrade.level = 0
		
		# Resetear bonificaciones temporales
		self.bonus_multiplier = 1.0
		self.bonus_end_time = 0.0
		
		# Resetear estadísticas de sesión
		self.session_clicks = 0
		self.session_coins = 0
		
		# Guardar estado
		self.save_game()
		
		logging.info("Progreso reseteado para prestigio")

	def get_prestige_stats(self) -> dict:
		"""Obtiene estadísticas de prestigio.

		Returns:
			Diccionario con estadísticas de prestigio
		"""
		stats = self.prestige_manager.get_stats()
		preview = self.prestige_manager.get_prestige_preview(self.lifetime_coins + self.coins)
		
		return {
			"prestige_crystals": stats['prestige_crystals'],
			"total_prestiges": stats['prestige_count'],
			"lifetime_coins": stats['lifetime_coins'],
			"prestige_multiplier": stats['income_multiplier'],
			"can_prestige": preview['can_prestige'],
			"crystals_if_prestige": preview['crystals_gained'],
			"preview": preview
		}

	def add_experience(self, amount: int):
		"""Añade experiencia al jugador y verifica level ups.

		Args:
			amount: Cantidad de experiencia a añadir
		"""
		self.player_experience += amount * self.talent_multipliers["experience_gain"]

		# Verificar level up (cada 1000 XP = 1 nivel)
		xp_for_next_level = self.player_level * 1000
		while self.player_experience >= xp_for_next_level:
			self.player_experience -= xp_for_next_level
			self.player_level += 1
			self.talent_points += 1
			self.total_talent_points_earned += 1
			logging.info("¡Level up! Nivel %d alcanzado. +1 punto de talento", self.player_level)
			xp_for_next_level = self.player_level * 1000

	def upgrade_talent(self, talent_name: str) -> bool:
		"""Mejora un talento específico.

		Args:
			talent_name: Nombre del talento a mejorar

		Returns:
			True si fue mejorado exitosamente
		"""
		if self.talent_points <= 0:
			return False

		# Obtener nivel actual del talento
		current_level = self.talents.get(talent_name, 0)

		# Verificar límite máximo (10 niveles por talento)
		if current_level >= 10:
			return False

		# Calcular costo (Fibonacci-like: 1,2,3,5,8,13,21,34,55,89)
		costs = [1, 2, 3, 5, 8, 13, 21, 34, 55, 89]
		cost = costs[current_level] if current_level < len(costs) else 89

		if self.talent_points < cost:
			return False

		# Mejorar talento
		self.talents[talent_name] = current_level + 1
		self.talent_points -= cost

		# Recalcular multiplicadores
		self._update_talent_multipliers()

		logging.info("Talento %s mejorado a nivel %d", talent_name, self.talents[talent_name])
		return True

	def _update_talent_multipliers(self):
		"""Actualiza los multiplicadores basados en talentos."""
		# Resetear multiplicadores a valores base
		self.talent_multipliers = {
			"click_income": 1.0,
			"building_income": 1.0,
			"building_cost_reduction": 0.0,
			"critical_chance": 0.0,
			"critical_damage": 1.0,
			"experience_gain": 1.0,
		}

		# Aplicar efectos de talentos económicos
		efficiency_level = self.talents.get("efficiency_boost", 0)
		self.talent_multipliers["click_income"] += efficiency_level * 0.05  # +5% por nivel

		idle_level = self.talents.get("idle_multiplier", 0)
		self.talent_multipliers["building_income"] += idle_level * 0.10  # +10% por nivel

		discount_level = self.talents.get("building_discount", 0)
		self.talent_multipliers["building_cost_reduction"] += discount_level * 0.03  # -3% por nivel

		# Aplicar efectos de talentos de combate
		crit_chance_level = self.talents.get("critical_chance", 0)
		self.talent_multipliers["critical_chance"] += crit_chance_level * 0.02  # +2% por nivel

		crit_damage_level = self.talents.get("critical_damage", 0)
		self.talent_multipliers["critical_damage"] += crit_damage_level * 0.15  # +15% por nivel

		# Aplicar efectos de talentos de exploración
		wanderlust_level = self.talents.get("wanderlust", 0)
		self.talent_multipliers["experience_gain"] += wanderlust_level * 0.02  # +2% por nivel

	def get_talent_stats(self) -> dict:
		"""Obtiene estadísticas de talentos.

		Returns:
			Diccionario con estadísticas de talentos
		"""
		# Calcular estadísticas en una sola iteración
		total_levels = 0
		total_talents = 0
		for level in self.talents.values():
			total_levels += level
			if level > 0:
				total_talents += 1

		return {
			"player_level": self.player_level,
			"player_experience": self.player_experience,
			"xp_for_next_level": self.player_level * 1000,
			"talent_points": self.talent_points,
			"total_talent_points_earned": self.total_talent_points_earned,
			"talents": self.talents.copy(),
			"talent_multipliers": self.talent_multipliers.copy(),
			"total_talent_levels": total_levels,
			"unlocked_talents": total_talents,
		}

	def sync_biome_bonuses_to_combat(self) -> None:
		"""
		Sincroniza las bonificaciones del bioma activo con el CombatManager.

		Este método debe llamarse cuando cambie la mazmorra activa
		para asegurar que el combate use las bonificaciones correctas.
		"""
		try:
			# Obtener bonificaciones del bioma activo
			biome_bonuses = self.dungeon_manager.get_active_biome_bonuses()

			# Aplicar al CombatManager
			self.combat_manager.set_biome_bonuses(biome_bonuses)

			# Log para debugging
			if biome_bonuses and any(
				v != 1.0 for v in biome_bonuses.values() if isinstance(v, (int, float))
			):
				active_bonuses = [
					f"{k}: {v}"
					for k, v in biome_bonuses.items()
					if isinstance(v, (int, float)) and v != 1.0
				]
				print(f"🌟 Bonificaciones de bioma aplicadas: {', '.join(active_bonuses)}")
			else:
				print("🌟 Sin bonificaciones de bioma activas")

		except Exception as e:
			logging.error("Error sincronizando bonificaciones de bioma: %s", e)

	def update_active_dungeon(self, dungeon_type) -> bool:
		"""
		Actualiza la mazmorra activa y sincroniza bonificaciones de bioma.

		Args:
			dungeon_type: Tipo de mazmorra a activar

		Returns:
			True si el cambio fue exitoso
		"""
		try:
			# Cambiar mazmorra activa
			if self.dungeon_manager.set_active_dungeon(dungeon_type):
				# Sincronizar bonificaciones de bioma automáticamente
				self.sync_biome_bonuses_to_combat()
				return True
			return False
		except Exception as e:
			logging.error("Error actualizando mazmorra activa: %s", e)
			return False

	def register_enemy_defeat(self, enemy_type, enemy_level: int, is_boss: bool = False) -> None:
		"""
		Registra la derrota de un enemigo para el sistema de desbloqueo.

		Args:
			enemy_type: Tipo de enemigo derrotado
			enemy_level: Nivel del enemigo
			is_boss: Si era un boss
		"""
		try:
			# Registrar en el unlock manager
			self.unlock_manager.add_enemies_defeated(1)

			# Si es un boss, registrarlo específicamente
			if is_boss:
				boss_name = enemy_type.value if hasattr(enemy_type, "value") else str(enemy_type)
				self.unlock_manager.register_boss_defeat(boss_name)

			# Actualizar progreso de exploración de mazmorra activa
			if self.dungeon_manager.active_dungeon:
				current_progress = self.dungeon_manager.dungeons[
					self.dungeon_manager.active_dungeon
				].exploration_progress
				self.unlock_manager.update_exploration_progress(
					self.dungeon_manager.active_dungeon,
					current_progress * 100.0,  # Convertir a porcentaje
				)

		except Exception as e:
			logging.error("Error registrando derrota de enemigo: %s", e)

	def check_dungeon_unlocks(self) -> Dict[str, Any]:
		"""
		Verifica qué mazmorras pueden ser desbloqueadas.

		Returns:
			Diccionario con información de desbloqueos disponibles
		"""
		try:
			player_level = self.player_stats.get_level()
			player_stats = {
				"level": player_level,
				"total_experience": self.player_stats.get_total_experience(),
			}

			return self.unlock_manager.get_all_unlock_status(player_level, player_stats)
		except Exception as e:
			logging.error("Error verificando desbloqueos: %s", e)
			return {}

	def attempt_dungeon_unlock(self, dungeon_type) -> Dict[str, Any]:
		"""
		Intenta desbloquear una mazmorra específica.

		Args:
			dungeon_type: Tipo de mazmorra a desbloquear

		Returns:
			Resultado del intento de desbloqueo
		"""
		try:
			player_level = self.player_stats.get_level()
			player_stats = {
				"level": player_level,
				"total_experience": self.player_stats.get_total_experience(),
			}

			result = self.unlock_manager.attempt_unlock(dungeon_type, player_level, player_stats)

			# Si se desbloqueó exitosamente, sincronizar bonificaciones
			if result.get("success"):
				self.sync_biome_bonuses_to_combat()

			return result
		except Exception as e:
			logging.error("Error intentando desbloquear mazmorra: %s", e)
			return {"success": False, "message": "Error interno", "hints": []}

	def get_unlock_hints(self, dungeon_type) -> List[str]:
		"""
		Obtiene pistas para desbloquear una mazmorra.

		Args:
			dungeon_type: Tipo de mazmorra

		Returns:
			Lista de pistas
		"""
		try:
			player_level = self.player_stats.get_level()
			player_stats = {
				"level": player_level,
				"total_experience": self.player_stats.get_total_experience(),
			}

			return self.unlock_manager.get_unlock_hints(dungeon_type, player_level, player_stats)
		except Exception as e:
			logging.error("Error obteniendo pistas: %s", e)
			return ["Error obteniendo información"]

	def get_unlock_summary(self) -> Dict[str, Any]:
		"""
		Obtiene un resumen del progreso de desbloqueos.

		Returns:
			Resumen con estadísticas de progreso
		"""
		try:
			# Actualizar tiempo de juego en unlock manager
			current_time = time.time()
			session_time = current_time - self.session_start_time
			self.unlock_manager.update_playtime(session_time)

			return self.unlock_manager.get_unlock_summary()
		except Exception as e:
			logging.error("Error obteniendo resumen de desbloqueos: %s", e)
			return {}


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
