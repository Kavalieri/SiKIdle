"""
Sistema de Balanceo para crear estancamiento natural en SiKIdle.

Gestiona la curva de dificultad para crear el "wall" que motiva prestigio:
- Costos exponenciales que se vuelven prohibitivos
- Ingresos que se ralentizan progresivamente
- Detección automática de estancamiento
"""

import logging
import math
from typing import Dict, Any


class BalanceManager:
	"""Gestor de balanceo para crear estancamiento natural."""
	
	def __init__(self, game_state):
		self.game_state = game_state
		
		# Configuración de balanceo
		self.base_cost_multiplier = 1.15  # Crecimiento de costos
		self.stagnation_threshold = 0.1   # 10% de progreso por minuto = estancamiento
		self.last_coins_check = 0
		self.last_check_time = 0
		
		logging.info("BalanceManager initialized")
	
	def calculate_building_cost_multiplier(self, building_count: int) -> float:
		"""Calcula multiplicador de costo según cantidad de edificios."""
		# Costo crece exponencialmente: 1.15^count
		return math.pow(self.base_cost_multiplier, building_count)
	
	def calculate_progress_rate(self) -> float:
		"""Calcula la tasa de progreso actual (monedas/minuto)."""
		import time
		current_time = time.time()
		current_coins = self.game_state.coins
		
		if self.last_check_time == 0:
			self.last_check_time = current_time
			self.last_coins_check = current_coins
			return 1.0  # Valor inicial
		
		time_diff = current_time - self.last_check_time
		if time_diff < 60:  # Esperar al menos 1 minuto
			return 1.0
		
		coins_diff = current_coins - self.last_coins_check
		progress_rate = coins_diff / (time_diff / 60)  # monedas por minuto
		
		# Actualizar para próxima verificación
		self.last_check_time = current_time
		self.last_coins_check = current_coins
		
		return max(0.1, progress_rate)
	
	def is_stagnation_detected(self) -> bool:
		"""Detecta si el jugador está en estancamiento."""
		# Verificar si puede hacer prestigio
		if hasattr(self.game_state, 'prestige_manager'):
			total_coins = self.game_state.lifetime_coins + self.game_state.coins
			can_prestige = self.game_state.prestige_manager.can_prestige(total_coins)
			
			if can_prestige:
				# Verificar tasa de progreso
				progress_rate = self.calculate_progress_rate()
				expected_rate = self.game_state.coins * 0.01  # 1% de monedas actuales por minuto
				
				return progress_rate < expected_rate * self.stagnation_threshold
		
		return False
	
	def get_next_meaningful_purchase(self) -> Dict[str, Any]:
		"""Obtiene la próxima compra significativa recomendada."""
		if not hasattr(self.game_state, 'building_manager'):
			return {'type': 'none', 'cost': 0, 'benefit': 'N/A'}
		
		building_manager = self.game_state.building_manager
		current_coins = self.game_state.coins
		
		best_purchase = None
		best_efficiency = 0
		
		# Evaluar edificios
		for building_type, building in building_manager.buildings.items():
			info = building_manager.get_building_info(building_type)
			cost = building.get_current_cost(info)
			
			if cost <= current_coins * 10:  # Solo considerar si es alcanzable
				production_increase = info.base_production_per_second
				efficiency = production_increase / cost
				
				if efficiency > best_efficiency:
					best_efficiency = efficiency
					best_purchase = {
						'type': 'building',
						'building_type': building_type,
						'cost': cost,
						'benefit': f"+{production_increase:.1f}/s",
						'efficiency': efficiency
					}
		
		# Evaluar upgrades si están disponibles
		if hasattr(self.game_state, 'upgrade_manager'):
			upgrade_manager = self.game_state.upgrade_manager
			for upgrade_type, upgrade in upgrade_manager.upgrades.items():
				if upgrade.level < upgrade.max_level:
					cost = upgrade.get_current_cost()
					if cost <= current_coins * 5:  # Upgrades más accesibles
						multiplier_increase = upgrade.get_multiplier_increase()
						efficiency = multiplier_increase / cost * 1000  # Escalar para comparar
						
						if efficiency > best_efficiency:
							best_efficiency = efficiency
							best_purchase = {
								'type': 'upgrade',
								'upgrade_type': upgrade_type,
								'cost': cost,
								'benefit': f"+{multiplier_increase:.1%} multiplicador",
								'efficiency': efficiency
							}
		
		return best_purchase or {'type': 'none', 'cost': 0, 'benefit': 'Considera hacer prestigio'}
	
	def get_stagnation_advice(self) -> str:
		"""Obtiene consejo específico para superar el estancamiento."""
		if not self.is_stagnation_detected():
			return "Tu progreso es bueno. ¡Sigue así!"
		
		next_purchase = self.get_next_meaningful_purchase()
		
		if next_purchase['type'] == 'none':
			return "Tu progreso se ha ralentizado. ¡Es momento de hacer prestigio para obtener multiplicadores permanentes!"
		
		if next_purchase['type'] == 'building':
			return f"Considera comprar más {next_purchase['building_type']} ({next_purchase['cost']:,} monedas) para {next_purchase['benefit']}"
		
		if next_purchase['type'] == 'upgrade':
			return f"Invierte en la mejora {next_purchase['upgrade_type']} ({next_purchase['cost']:,} monedas) para {next_purchase['benefit']}"
		
		return "Continúa acumulando monedas o considera hacer prestigio."
	
	def get_balance_stats(self) -> Dict[str, Any]:
		"""Obtiene estadísticas de balanceo."""
		return {
			'progress_rate': self.calculate_progress_rate(),
			'is_stagnation': self.is_stagnation_detected(),
			'next_purchase': self.get_next_meaningful_purchase(),
			'stagnation_advice': self.get_stagnation_advice(),
			'base_cost_multiplier': self.base_cost_multiplier
		}