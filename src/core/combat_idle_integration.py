"""
Sistema de Integración Combat-Idle para SiKIdle.

Combat actúa como boost complementario para el idle clicker:
- Bonificaciones temporales para idle
- Recursos compartidos (monedas)
- Desbloqueo gradual basado en progreso idle
- Combat complementa, no reemplaza idle
"""

import logging
import time
from typing import Dict, Any, Optional
from enum import Enum


class CombatBoostType(Enum):
	"""Tipos de boost que combat puede dar al idle."""
	COIN_MULTIPLIER = "coin_multiplier"
	CLICK_MULTIPLIER = "click_multiplier"
	BUILDING_SPEED = "building_speed"
	OFFLINE_EARNINGS = "offline_earnings"


class CombatIdleIntegration:
	"""Gestor de integración entre combat e idle."""
	
	def __init__(self, game_state):
		self.game_state = game_state
		
		# Boosts activos
		self.active_boosts: Dict[CombatBoostType, Dict] = {}
		
		# Configuración de boosts
		self.boost_config = {
			CombatBoostType.COIN_MULTIPLIER: {
				'base_multiplier': 1.5,
				'duration': 300,  # 5 minutos
				'cooldown': 600   # 10 minutos
			},
			CombatBoostType.CLICK_MULTIPLIER: {
				'base_multiplier': 2.0,
				'duration': 180,  # 3 minutos
				'cooldown': 360   # 6 minutos
			},
			CombatBoostType.BUILDING_SPEED: {
				'base_multiplier': 1.3,
				'duration': 600,  # 10 minutos
				'cooldown': 900   # 15 minutos
			},
			CombatBoostType.OFFLINE_EARNINGS: {
				'base_multiplier': 2.0,
				'duration': 480,  # 8 minutos
				'cooldown': 1200  # 20 minutos
			}
		}
		
		# Estado de cooldowns
		self.last_boost_times: Dict[CombatBoostType, float] = {}
		
		logging.info("CombatIdleIntegration initialized")
	
	def can_activate_boost(self, boost_type: CombatBoostType) -> bool:
		"""Verifica si se puede activar un boost."""
		if boost_type in self.active_boosts:
			return False  # Ya está activo
		
		current_time = time.time()
		last_use = self.last_boost_times.get(boost_type, 0)
		cooldown = self.boost_config[boost_type]['cooldown']
		
		return current_time - last_use >= cooldown
	
	def activate_combat_boost(self, boost_type: CombatBoostType, combat_performance: float = 1.0) -> bool:
		"""Activa un boost basado en performance de combat."""
		if not self.can_activate_boost(boost_type):
			return False
		
		config = self.boost_config[boost_type]
		current_time = time.time()
		
		# Calcular multiplicador basado en performance
		performance_bonus = min(2.0, 1.0 + (combat_performance - 1.0) * 0.5)
		final_multiplier = config['base_multiplier'] * performance_bonus
		
		# Activar boost
		self.active_boosts[boost_type] = {
			'multiplier': final_multiplier,
			'start_time': current_time,
			'end_time': current_time + config['duration'],
			'combat_performance': combat_performance
		}
		
		self.last_boost_times[boost_type] = current_time
		
		logging.info(f"Combat boost activated: {boost_type.value} x{final_multiplier:.2f} for {config['duration']}s")
		return True
	
	def get_active_multipliers(self) -> Dict[str, float]:
		"""Obtiene multiplicadores activos de combat."""
		multipliers = {
			'coin_multiplier': 1.0,
			'click_multiplier': 1.0,
			'building_multiplier': 1.0
		}
		
		current_time = time.time()
		expired_boosts = []
		
		for boost_type, boost_data in self.active_boosts.items():
			if current_time > boost_data['end_time']:
				expired_boosts.append(boost_type)
				continue
			
			# Aplicar multiplicador según tipo
			if boost_type == CombatBoostType.COIN_MULTIPLIER:
				multipliers['coin_multiplier'] *= boost_data['multiplier']
			elif boost_type == CombatBoostType.CLICK_MULTIPLIER:
				multipliers['click_multiplier'] *= boost_data['multiplier']
			elif boost_type == CombatBoostType.BUILDING_SPEED:
				multipliers['building_multiplier'] *= boost_data['multiplier']
		
		# Limpiar boosts expirados
		for boost_type in expired_boosts:
			del self.active_boosts[boost_type]
			logging.info(f"Combat boost expired: {boost_type.value}")
		
		return multipliers
	
	def get_combat_unlock_level(self) -> int:
		"""Obtiene el nivel de desbloqueo de combat basado en progreso idle."""
		# Combat se desbloquea gradualmente según progreso idle
		coins = self.game_state.coins
		
		if coins < 1000:
			return 1  # Combat básico
		elif coins < 10000:
			return 2  # Combat intermedio
		elif coins < 100000:
			return 3  # Combat avanzado
		else:
			return 4  # Combat maestro
	
	def get_combat_rewards_multiplier(self) -> float:
		"""Obtiene multiplicador de recompensas de combat basado en idle."""
		# Más progreso idle = mejores recompensas de combat
		total_buildings = 0
		if hasattr(self.game_state, 'building_manager'):
			total_buildings = sum(
				building.count for building in self.game_state.building_manager.buildings.values()
			)
		
		# Base 1.0x, +10% por cada 10 edificios
		return 1.0 + (total_buildings // 10) * 0.1
	
	def process_combat_victory(self, enemy_level: int, damage_dealt: float, time_taken: float) -> Dict[str, Any]:
		"""Procesa una victoria de combat y otorga recompensas."""
		# Calcular performance de combat
		performance = self._calculate_combat_performance(enemy_level, damage_dealt, time_taken)
		
		# Calcular recompensas base
		base_coins = enemy_level * 10
		multiplier = self.get_combat_rewards_multiplier()
		final_coins = int(base_coins * multiplier * performance)
		
		# Otorgar monedas
		self.game_state.coins += final_coins
		
		# Posibilidad de activar boost automático
		boost_chance = min(0.3, performance * 0.2)  # Máximo 30% chance
		activated_boost = None
		
		if self._should_activate_auto_boost(boost_chance):
			# Seleccionar boost disponible
			available_boosts = [
				boost for boost in CombatBoostType 
				if self.can_activate_boost(boost)
			]
			
			if available_boosts:
				import random
				boost_type = random.choice(available_boosts)
				if self.activate_combat_boost(boost_type, performance):
					activated_boost = boost_type
		
		result = {
			'coins_earned': final_coins,
			'performance': performance,
			'multiplier_applied': multiplier,
			'boost_activated': activated_boost,
			'combat_level': self.get_combat_unlock_level()
		}
		
		logging.info(f"Combat victory: +{final_coins} coins, performance: {performance:.2f}")
		return result
	
	def _calculate_combat_performance(self, enemy_level: int, damage_dealt: float, time_taken: float) -> float:
		"""Calcula performance de combat (1.0 = normal, >1.0 = excelente)."""
		# Performance basada en eficiencia
		expected_damage = enemy_level * 100  # Daño esperado
		expected_time = enemy_level * 5      # Tiempo esperado
		
		damage_efficiency = min(2.0, damage_dealt / expected_damage)
		time_efficiency = min(2.0, expected_time / max(1.0, time_taken))
		
		return (damage_efficiency + time_efficiency) / 2
	
	def _should_activate_auto_boost(self, chance: float) -> bool:
		"""Determina si se debe activar un boost automático."""
		import random
		return random.random() < chance
	
	def get_boost_status(self) -> Dict[str, Any]:
		"""Obtiene estado de todos los boosts."""
		current_time = time.time()
		status = {}
		
		for boost_type in CombatBoostType:
			boost_info = {
				'available': self.can_activate_boost(boost_type),
				'active': boost_type in self.active_boosts,
				'cooldown_remaining': 0,
				'duration_remaining': 0
			}
			
			# Calcular cooldown restante
			if not boost_info['available'] and boost_type not in self.active_boosts:
				last_use = self.last_boost_times.get(boost_type, 0)
				cooldown = self.boost_config[boost_type]['cooldown']
				boost_info['cooldown_remaining'] = max(0, cooldown - (current_time - last_use))
			
			# Calcular duración restante si está activo
			if boost_info['active']:
				boost_data = self.active_boosts[boost_type]
				boost_info['duration_remaining'] = max(0, boost_data['end_time'] - current_time)
				boost_info['multiplier'] = boost_data['multiplier']
			
			status[boost_type.value] = boost_info
		
		return status
	
	def get_integration_hints(self) -> list:
		"""Obtiene hints sobre integración combat-idle."""
		hints = []
		
		# Hint sobre boosts disponibles
		available_boosts = [
			boost for boost in CombatBoostType 
			if self.can_activate_boost(boost)
		]
		
		if available_boosts and self.game_state.coins > 1000:
			hints.append({
				'title': '⚔️ Combat Boost Disponible',
				'message': f'Participa en combat para activar multiplicadores temporales para tu idle clicker.',
				'priority': 2
			})
		
		# Hint sobre nivel de combat
		combat_level = self.get_combat_unlock_level()
		if combat_level > 1:
			hints.append({
				'title': f'⚔️ Combat Nivel {combat_level}',
				'message': f'Tu progreso idle ha desbloqueado combat de nivel {combat_level}. ¡Mejores recompensas te esperan!',
				'priority': 3
			})
		
		return hints
	
	def get_stats(self) -> Dict[str, Any]:
		"""Obtiene estadísticas de integración."""
		return {
			'combat_level': self.get_combat_unlock_level(),
			'rewards_multiplier': self.get_combat_rewards_multiplier(),
			'active_boosts': len(self.active_boosts),
			'boost_status': self.get_boost_status(),
			'active_multipliers': self.get_active_multipliers()
		}