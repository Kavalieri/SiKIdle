"""
Sistema de mejoras tradicionales para SiKIdle.

Este módulo implementa mejoras permanentes que el jugador puede comprar
para incrementar la eficiencia del juego de forma permanente.
Inspirado en Cookie Clicker y Adventure Capitalist.
"""

import logging
from enum import Enum
from dataclasses import dataclass
from typing import Any
from core.resources import ResourceType, ResourceManager


class UpgradeCategory(Enum):
	"""Categorías de mejoras disponibles."""
	ECONOMIC = "economic"        # Mejoras económicas: +% ingresos
	EFFICIENCY = "efficiency"    # Mejoras de eficiencia: -% costos, +% velocidad
	CRITICAL = "critical"        # Mejoras de críticos: +% probabilidad, +% multiplicador
	MULTIPLIER = "multiplier"    # Multiplicadores globales exponenciales


class UpgradeType(Enum):
	"""Tipos específicos de mejoras."""
	# Económicas
	CLICK_INCOME = "click_income"              # +% ingresos por clic
	BUILDING_INCOME = "building_income"        # +% ingresos de edificios
	GLOBAL_INCOME = "global_income"           # +% ingresos globales
	
	# Eficiencia
	BUILDING_COST_REDUCTION = "building_cost_reduction"  # -% costo edificios
	PRODUCTION_SPEED = "production_speed"                # +% velocidad producción
	RESOURCE_EFFICIENCY = "resource_efficiency"          # Mejor uso de recursos
	
	# Críticos
	CRITICAL_CHANCE = "critical_chance"        # +% probabilidad crítico
	CRITICAL_MULTIPLIER = "critical_multiplier"  # +% multiplicador crítico
	GOLDEN_CLICK_CHANCE = "golden_click_chance"  # Posibilidad de clics dorados
	
	# Multiplicadores
	EXPONENTIAL_MULTIPLIER = "exponential_multiplier"  # Multiplicadores exponenciales
	PRESTIGE_BONUS = "prestige_bonus"                   # Bonus relacionados a prestigio


@dataclass
class UpgradeInfo:
	"""Información sobre una mejora específica."""
	name: str
	description: str
	category: UpgradeCategory
	upgrade_type: UpgradeType
	base_cost: int
	cost_resource: ResourceType
	effect_value: float              # Valor del efecto (ej: 0.25 = +25%)
	max_level: int                   # Nivel máximo (0 = ilimitado)
	cost_scaling: float = 1.5        # Factor de escalado de costo
	prerequisite_level: int = 1      # Nivel de jugador requerido
	prerequisite_upgrades: list[UpgradeType] | None = None  # Mejoras prerequisito
	emoji: str = "⚡"


class Upgrade:
	"""Representa una mejora comprada por el jugador."""
	
	def __init__(self, upgrade_type: UpgradeType, level: int = 0):
		"""Inicializa una mejora.
		
		Args:
			upgrade_type: Tipo de mejora
			level: Nivel actual de la mejora
		"""
		self.upgrade_type = upgrade_type
		self.level = level
		self.last_purchase_time = 0.0
	
	def get_current_cost(self, info: UpgradeInfo) -> int | float:
		"""Calcula el costo actual de la siguiente mejora.
		
		Args:
			info: Información de la mejora
			
		Returns:
			Costo actual para subir al siguiente nivel
		"""
		if info.max_level > 0 and self.level >= info.max_level:
			return float('inf')  # No se puede mejorar más
		
		return int(info.base_cost * (info.cost_scaling ** self.level))
	
	def get_total_effect(self, info: UpgradeInfo) -> float:
		"""Calcula el efecto total acumulado de esta mejora.
		
		Args:
			info: Información de la mejora
			
		Returns:
			Valor total del efecto
		"""
		return info.effect_value * self.level
	
	def can_upgrade(self, info: UpgradeInfo, resource_manager: ResourceManager) -> bool:
		"""Verifica si se puede mejorar esta upgrade.
		
		Args:
			info: Información de la mejora
			resource_manager: Gestor de recursos
			
		Returns:
			True si se puede mejorar
		"""
		if info.max_level > 0 and self.level >= info.max_level:
			return False
		
		cost = self.get_current_cost(info)
		return resource_manager.get_resource(info.cost_resource) >= cost
	
	def upgrade(self, info: UpgradeInfo, resource_manager: ResourceManager) -> bool:
		"""Intenta mejorar esta upgrade.
		
		Args:
			info: Información de la mejora
			resource_manager: Gestor de recursos
			
		Returns:
			True si la mejora fue exitosa
		"""
		if not self.can_upgrade(info, resource_manager):
			return False
		
		cost = self.get_current_cost(info)
		if resource_manager.spend_resource(info.cost_resource, cost):
			self.level += 1
			logging.info("Mejora %s subida a nivel %d", info.name, self.level)
			return True
		
		return False


class UpgradeManager:
	"""Gestor principal del sistema de mejoras."""
	
	def __init__(self, resource_manager: ResourceManager):
		"""Inicializa el gestor de mejoras.
		
		Args:
			resource_manager: Gestor de recursos del juego
		"""
		self.resource_manager = resource_manager
		self.upgrades: dict[UpgradeType, Upgrade] = {}
		self.upgrade_info: dict[UpgradeType, UpgradeInfo] = {}
		
		self._initialize_upgrade_info()
		self._initialize_upgrades()
		
		logging.info("Gestor de mejoras inicializado")
	
	def _initialize_upgrade_info(self):
		"""Inicializa la información de todas las mejoras disponibles."""
		self.upgrade_info = {
			# Mejoras Económicas
			UpgradeType.CLICK_INCOME: UpgradeInfo(
				name="Dedos Dorados",
				description="Incrementa las monedas ganadas por clic en 25%",
				category=UpgradeCategory.ECONOMIC,
				upgrade_type=UpgradeType.CLICK_INCOME,
				base_cost=100,
				cost_resource=ResourceType.COINS,
				effect_value=0.25,
				max_level=20,
				emoji="👆"
			),
			UpgradeType.BUILDING_INCOME: UpgradeInfo(
				name="Gestión Eficiente",
				description="Incrementa los ingresos de todos los edificios en 15%",
				category=UpgradeCategory.ECONOMIC,
				upgrade_type=UpgradeType.BUILDING_INCOME,
				base_cost=500,
				cost_resource=ResourceType.COINS,
				effect_value=0.15,
				max_level=25,
				emoji="🏗️"
			),
			UpgradeType.GLOBAL_INCOME: UpgradeInfo(
				name="Imperio Económico",
				description="Incrementa todos los ingresos en 10%",
				category=UpgradeCategory.ECONOMIC,
				upgrade_type=UpgradeType.GLOBAL_INCOME,
				base_cost=2000,
				cost_resource=ResourceType.COINS,
				effect_value=0.10,
				max_level=15,
				emoji="💰"
			),
			
			# Mejoras de Eficiencia
			UpgradeType.BUILDING_COST_REDUCTION: UpgradeInfo(
				name="Construcción Inteligente",
				description="Reduce el costo de todos los edificios en 5%",
				category=UpgradeCategory.EFFICIENCY,
				upgrade_type=UpgradeType.BUILDING_COST_REDUCTION,
				base_cost=1000,
				cost_resource=ResourceType.COINS,
				effect_value=0.05,
				max_level=10,
				emoji="🔧"
			),
			UpgradeType.PRODUCTION_SPEED: UpgradeInfo(
				name="Máquinas Mejoradas",
				description="Incrementa la velocidad de producción en 20%",
				category=UpgradeCategory.EFFICIENCY,
				upgrade_type=UpgradeType.PRODUCTION_SPEED,
				base_cost=1500,
				cost_resource=ResourceType.COINS,
				effect_value=0.20,
				max_level=12,
				emoji="⚡"
			),
			UpgradeType.RESOURCE_EFFICIENCY: UpgradeInfo(
				name="Optimización de Recursos",
				description="Mejora la eficiencia de uso de recursos en 15%",
				category=UpgradeCategory.EFFICIENCY,
				upgrade_type=UpgradeType.RESOURCE_EFFICIENCY,
				base_cost=3000,
				cost_resource=ResourceType.COINS,
				effect_value=0.15,
				max_level=8,
				emoji="🔄"
			),
			
			# Mejoras de Críticos
			UpgradeType.CRITICAL_CHANCE: UpgradeInfo(
				name="Suerte del Principiante",
				description="Incrementa la probabilidad de crítico en 2%",
				category=UpgradeCategory.CRITICAL,
				upgrade_type=UpgradeType.CRITICAL_CHANCE,
				base_cost=800,
				cost_resource=ResourceType.COINS,
				effect_value=0.02,
				max_level=25,
				emoji="🍀"
			),
			UpgradeType.CRITICAL_MULTIPLIER: UpgradeInfo(
				name="Golpe Perfecto",
				description="Incrementa el multiplicador de crítico en 0.5x",
				category=UpgradeCategory.CRITICAL,
				upgrade_type=UpgradeType.CRITICAL_MULTIPLIER,
				base_cost=1200,
				cost_resource=ResourceType.COINS,
				effect_value=0.5,
				max_level=20,
				emoji="💥"
			),
			
			# Multiplicadores Globales
			UpgradeType.EXPONENTIAL_MULTIPLIER: UpgradeInfo(
				name="Singularidad Económica",
				description="Multiplica todos los ingresos por 2x",
				category=UpgradeCategory.MULTIPLIER,
				upgrade_type=UpgradeType.EXPONENTIAL_MULTIPLIER,
				base_cost=50000,
				cost_resource=ResourceType.COINS,
				effect_value=2.0,
				max_level=5,
				cost_scaling=10.0,
				emoji="🌟"
			),
		}
	
	def _initialize_upgrades(self):
		"""Inicializa todas las mejoras con nivel 0."""
		for upgrade_type in UpgradeType:
			self.upgrades[upgrade_type] = Upgrade(upgrade_type, 0)
	
	def get_upgrade(self, upgrade_type: UpgradeType) -> Upgrade:
		"""Obtiene una mejora específica.
		
		Args:
			upgrade_type: Tipo de mejora
			
		Returns:
			Instancia de la mejora
		"""
		return self.upgrades[upgrade_type]
	
	def get_upgrade_info(self, upgrade_type: UpgradeType) -> UpgradeInfo:
		"""Obtiene la información de una mejora.
		
		Args:
			upgrade_type: Tipo de mejora
			
		Returns:
			Información de la mejora
		"""
		return self.upgrade_info[upgrade_type]
	
	def get_upgrades_by_category(self, category: UpgradeCategory) -> list[UpgradeType]:
		"""Obtiene todas las mejoras de una categoría específica.
		
		Args:
			category: Categoría de mejoras
			
		Returns:
			Lista de tipos de mejora en esa categoría
		"""
		return [
			upgrade_type for upgrade_type, info in self.upgrade_info.items()
			if info.category == category
		]
	
	def get_available_upgrades(self, player_level: int = 1) -> list[UpgradeType]:
		"""Obtiene lista de mejoras disponibles para el nivel del jugador.
		
		Args:
			player_level: Nivel actual del jugador
			
		Returns:
			Lista de mejoras disponibles
		"""
		available = []
		for upgrade_type, info in self.upgrade_info.items():
			if info.prerequisite_level <= player_level:
				# Verificar prerequisitos de mejoras
				if info.prerequisite_upgrades:
					prerequisites_met = all(
						self.upgrades[prereq].level > 0 
						for prereq in info.prerequisite_upgrades
					)
					if prerequisites_met:
						available.append(upgrade_type)
				else:
					available.append(upgrade_type)
		
		return available
	
	def purchase_upgrade(self, upgrade_type: UpgradeType, game_state = None) -> bool:
		"""Intenta comprar una mejora.
		
		Args:
			upgrade_type: Tipo de mejora a comprar
			game_state: Referencia al estado del juego para hooks
			
		Returns:
			True si la compra fue exitosa
		"""
		upgrade = self.upgrades[upgrade_type]
		info = self.upgrade_info[upgrade_type]
		success = upgrade.upgrade(info, self.resource_manager)
		
		# Si la compra fue exitosa, llamar hook del game state
		if success and game_state:
			try:
				game_state.on_upgrade_purchased(upgrade_type)
			except AttributeError:
				# Si no tiene el método, ignorar
				pass
		
		return success
	
	def get_total_effect(self, upgrade_type: UpgradeType) -> float:
		"""Obtiene el efecto total de una mejora.
		
		Args:
			upgrade_type: Tipo de mejora
			
		Returns:
			Valor total del efecto
		"""
		upgrade = self.upgrades[upgrade_type]
		info = self.upgrade_info[upgrade_type]
		return upgrade.get_total_effect(info)
	
	def get_click_multiplier(self) -> float:
		"""Calcula el multiplicador total para clics.
		
		Returns:
			Multiplicador de ingresos por clic
		"""
		click_bonus = 1.0 + self.get_total_effect(UpgradeType.CLICK_INCOME)
		global_bonus = 1.0 + self.get_total_effect(UpgradeType.GLOBAL_INCOME)
		critical_chance = self.get_total_effect(UpgradeType.CRITICAL_CHANCE)
		critical_multiplier = 2.0 + self.get_total_effect(UpgradeType.CRITICAL_MULTIPLIER)
		
		# Aplicar multiplicadores exponenciales
		exp_multiplier = self.get_total_effect(UpgradeType.EXPONENTIAL_MULTIPLIER)
		if exp_multiplier > 0:
			global_bonus *= exp_multiplier
		
		# Calcular promedio con críticos
		avg_critical = 1.0 + (critical_chance * (critical_multiplier - 1.0))
		
		return click_bonus * global_bonus * avg_critical
	
	def get_building_multiplier(self) -> float:
		"""Calcula el multiplicador total para edificios.
		
		Returns:
			Multiplicador de ingresos de edificios
		"""
		building_bonus = 1.0 + self.get_total_effect(UpgradeType.BUILDING_INCOME)
		global_bonus = 1.0 + self.get_total_effect(UpgradeType.GLOBAL_INCOME)
		speed_bonus = 1.0 + self.get_total_effect(UpgradeType.PRODUCTION_SPEED)
		
		# Aplicar multiplicadores exponenciales
		exp_multiplier = self.get_total_effect(UpgradeType.EXPONENTIAL_MULTIPLIER)
		if exp_multiplier > 0:
			global_bonus *= exp_multiplier
		
		return building_bonus * global_bonus * speed_bonus
	
	def get_building_cost_multiplier(self) -> float:
		"""Calcula el multiplicador de costo para edificios.
		
		Returns:
			Multiplicador de reducción de costos (< 1.0 es mejor)
		"""
		cost_reduction = self.get_total_effect(UpgradeType.BUILDING_COST_REDUCTION)
		return max(0.1, 1.0 - cost_reduction)  # Mínimo 10% del costo original
	
	def get_upgrade_stats(self) -> dict[str, Any]:
		"""Obtiene estadísticas generales de mejoras.
		
		Returns:
			Diccionario con estadísticas
		"""
		total_upgrades = sum(upgrade.level for upgrade in self.upgrades.values())
		total_spent = 0
		
		for upgrade_type, upgrade in self.upgrades.items():
			info = self.upgrade_info[upgrade_type]
			for level in range(upgrade.level):
				total_spent += int(info.base_cost * (info.cost_scaling ** level))
		
		return {
			'total_upgrades': total_upgrades,
			'total_spent': total_spent,
			'click_multiplier': self.get_click_multiplier(),
			'building_multiplier': self.get_building_multiplier(),
			'cost_reduction': 1.0 - self.get_building_cost_multiplier()
		}
	
	def get_save_data(self) -> dict[str, Any]:
		"""Obtiene datos para guardar.
		
		Returns:
			Diccionario con datos de guardado
		"""
		return {
			'upgrades': {
				upgrade_type.value: {
					'level': upgrade.level,
					'last_purchase_time': upgrade.last_purchase_time
				}
				for upgrade_type, upgrade in self.upgrades.items()
			}
		}
	
	def load_save_data(self, data: dict[str, Any]) -> None:
		"""Carga datos desde guardado.
		
		Args:
			data: Datos de guardado
		"""
		if 'upgrades' in data:
			for upgrade_type_str, upgrade_data in data['upgrades'].items():
				try:
					upgrade_type = UpgradeType(upgrade_type_str)
					if upgrade_type in self.upgrades:
						self.upgrades[upgrade_type].level = upgrade_data.get('level', 0)
						self.upgrades[upgrade_type].last_purchase_time = upgrade_data.get('last_purchase_time', 0.0)
				except ValueError:
					logging.warning("Tipo de mejora desconocido: %s", upgrade_type_str)
		
		logging.info("Datos de mejoras cargados")
