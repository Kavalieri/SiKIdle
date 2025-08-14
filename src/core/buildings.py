"""Sistema de edificios generadores para SiKIdle.

Gestiona todos los tipos de edificios que generan recursos automáticamente.
"""

import logging
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any

from core.resources import ResourceType, ResourceManager


class BuildingType(Enum):
	"""Tipos de edificios disponibles en el juego."""
	# Edificios básicos de producción
	FARM = "farm"               # Granja - Generador básico
	FACTORY = "factory"         # Fábrica - Producción media
	BANK = "bank"              # Banco - Producción alta
	LABORATORY = "laboratory"   # Laboratorio - Investigación
	PORTAL = "portal"          # Portal - Generación dimensional
	
	# Edificios especializados
	MINE = "mine"              # Mina - Generador de materiales
	SAWMILL = "sawmill"        # Aserradero - Generador de madera
	QUARRY = "quarry"          # Cantera - Generador de piedra
	REACTOR = "reactor"        # Reactor - Generador de energía


@dataclass
class BuildingInfo:
	"""Información sobre un tipo de edificio."""
	name: str
	description: str
	emoji: str
	base_cost: int
	base_production: float
	production_resource: ResourceType
	cost_resource: ResourceType = ResourceType.COINS
	cost_multiplier: float = 1.15
	unlock_level: int = 1
	max_count = None


class Building:
	"""Representa una instancia específica de un edificio."""
	
	def __init__(self, building_type: BuildingType, count: int = 0):
		"""Inicializa un edificio.
		
		Args:
			building_type: Tipo de edificio
			count: Cantidad de edificios de este tipo
		"""
		self.building_type = building_type
		self.count = count
		self.last_production_time = time.time()
		
	def get_current_cost(self, info: BuildingInfo) -> int:
		"""Calcula el costo actual para comprar uno más de este edificio."""
		return int(info.base_cost * (info.cost_multiplier ** self.count))
	
	def get_total_production_per_second(self, info: BuildingInfo) -> float:
		"""Calcula la producción total por segundo de todos los edificios de este tipo."""
		return info.base_production * self.count
	
	def can_afford(self, info: BuildingInfo, resource_manager: ResourceManager) -> bool:
		"""Verifica si se puede permitir comprar otro edificio de este tipo."""
		cost = self.get_current_cost(info)
		return resource_manager.can_afford(info.cost_resource, cost)
	
	def purchase(self, info: BuildingInfo, resource_manager: ResourceManager) -> bool:
		"""Intenta comprar un edificio adicional.
		
		Returns:
			True si la compra fue exitosa
		"""
		if info.max_count and self.count >= info.max_count:
			return False
			
		cost = self.get_current_cost(info)
		if resource_manager.spend_resource(info.cost_resource, cost):
			self.count += 1
			logging.info("Edificio %s comprado. Total: %d", info.name, self.count)
			return True
		return False
	
	def collect_production(self, info: BuildingInfo, resource_manager: ResourceManager, prestige_multiplier: float = 1.0) -> float:
		"""Recolecta la producción acumulada desde la última recolección.
		
		Args:
			info: Información del tipo de edificio
			resource_manager: Gestor de recursos
			prestige_multiplier: Multiplicador de prestigio
		
		Returns:
			Cantidad de recursos producidos
		"""
		if self.count == 0:
			return 0.0
			
		current_time = time.time()
		time_elapsed = current_time - self.last_production_time
		
		# Calcular producción acumulada con multiplicador de prestigio
		base_production = self.get_total_production_per_second(info) * time_elapsed
		production = base_production * prestige_multiplier
		
		if production > 0:
			actually_added = resource_manager.add_resource(info.production_resource, production)
			self.last_production_time = current_time
			return actually_added
		
		return 0.0


class BuildingManager:
	"""Gestiona todos los edificios del juego."""
	
	def __init__(self, resource_manager: ResourceManager):
		"""Inicializa el gestor de edificios.
		
		Args:
			resource_manager: Gestor de recursos del juego
		"""
		self.resource_manager = resource_manager
		self.buildings = {}
		self.prestige_multiplier = 1.0  # Multiplicador de prestigio
		
		# Información de cada tipo de edificio
		self.building_info = {
			BuildingType.FARM: BuildingInfo(
				name="Granja",
				description="Genera monedas automáticamente",
				emoji="🚜",
				base_cost=10,
				base_production=0.5,
				production_resource=ResourceType.COINS,
				unlock_level=1
			),
			BuildingType.FACTORY: BuildingInfo(
				name="Fábrica",
				description="Producción media de monedas",
				emoji="🏭",
				base_cost=100,
				base_production=5.0,
				production_resource=ResourceType.COINS,
				unlock_level=1
			),
			BuildingType.BANK: BuildingInfo(
				name="Banco",
				description="Generación alta de monedas",
				emoji="🏦",
				base_cost=1000,
				base_production=25.0,
				production_resource=ResourceType.COINS,
				unlock_level=1
			),
			BuildingType.MINE: BuildingInfo(
				name="Mina",
				description="Extrae hierro y materiales",
				emoji="⛏️",
				base_cost=10000,
				base_production=125.0,
				production_resource=ResourceType.COINS,
				unlock_level=1
			),
			BuildingType.SAWMILL: BuildingInfo(
				name="Aserradero",
				description="Produce madera constantemente",
				emoji="🪚",
				base_cost=100000,
				base_production=625.0,
				production_resource=ResourceType.COINS,
				unlock_level=1
			),
			BuildingType.QUARRY: BuildingInfo(
				name="Cantera",
				description="Extrae piedra de las montañas",
				emoji="🗻",
				base_cost=1000000,
				base_production=3125.0,
				production_resource=ResourceType.COINS,
				unlock_level=1
			),
			BuildingType.LABORATORY: BuildingInfo(
				name="Laboratorio",
				description="Genera experiencia y conocimiento",
				emoji="🧪",
				base_cost=10000000,
				base_production=15625.0,
				production_resource=ResourceType.COINS,
				unlock_level=1
			),
			BuildingType.REACTOR: BuildingInfo(
				name="Reactor",
				description="Regenera energía constantemente",
				emoji="⚡",
				base_cost=100000000,
				base_production=78125.0,
				production_resource=ResourceType.COINS,
				unlock_level=1
			),
			BuildingType.PORTAL: BuildingInfo(
				name="Portal Dimensional",
				description="Genera cristales interdimensionales",
				emoji="🌀",
				base_cost=1000000000,
				base_production=390625.0,
				production_resource=ResourceType.COINS,
				unlock_level=1
			)
		}
		
		# Inicializar edificios
		for building_type in BuildingType:
			self.buildings[building_type] = Building(building_type, 0)
		
		logging.info("Gestor de edificios inicializado")
	
	def get_building(self, building_type: BuildingType) -> Building:
		"""Obtiene un edificio específico."""
		return self.buildings[building_type]
	
	def get_building_info(self, building_type: BuildingType) -> BuildingInfo:
		"""Obtiene la información de un tipo de edificio."""
		return self.building_info[building_type]
	
	def get_building_cost(self, building_type: BuildingType) -> dict:
		"""Obtiene el costo actual de un edificio.
		
		Returns:
			Dict con el tipo de recurso y cantidad necesaria
		"""
		building = self.buildings[building_type]
		info = self.building_info[building_type]
		current_cost = building.get_current_cost(info)
		return {info.cost_resource: current_cost}
	
	def get_unlocked_buildings(self, player_level: int = 1) -> list[BuildingType]:
		"""Obtiene lista de edificios desbloqueados para el nivel del jugador."""
		return [
			building_type for building_type in BuildingType
			if self.building_info[building_type].unlock_level <= player_level
		]
	
	def purchase_building(self, building_type: BuildingType, game_state = None) -> bool:
		"""Intenta comprar un edificio.
		
		Args:
			building_type: Tipo de edificio a comprar
			game_state: Referencia al estado del juego para hooks
		
		Returns:
			True si la compra fue exitosa
		"""
		building = self.buildings[building_type]
		info = self.building_info[building_type]
		success = building.purchase(info, self.resource_manager)
		
		# Si la compra fue exitosa, llamar hook del game state
		if success and game_state:
			try:
				game_state.on_building_purchased(building_type, building.count)
			except AttributeError:
				# Si no tiene el método, ignorar
				pass
		
		return success
	
	def collect_all_production(self) -> dict:
		"""Recolecta la producción de todos los edificios.
		
		Returns:
			Diccionario con la producción recolectada por tipo de recurso
		"""
		total_collected = {}
		
		for building_type, building in self.buildings.items():
			info = self.building_info[building_type]
			collected = building.collect_production(info, self.resource_manager, self.prestige_multiplier)
			
			if collected > 0:
				resource_type = info.production_resource
				if resource_type not in total_collected:
					total_collected[resource_type] = 0
				total_collected[resource_type] += collected
		
		return total_collected
	
	def set_prestige_multiplier(self, multiplier: float):
		"""Establece el multiplicador de prestigio para la producción de edificios.
		
		Args:
			multiplier: Multiplicador de prestigio a aplicar
		"""
		self.prestige_multiplier = multiplier
		logging.debug(f"Multiplicador de prestigio establecido a {multiplier:.2f}x")
	
	def get_total_production_per_second(self) -> dict:
		"""Obtiene la producción total por segundo de todos los edificios.
		
		Returns:
			Diccionario con producción por segundo por tipo de recurso
		"""
		total_production = {}
		
		for building_type, building in self.buildings.items():
			info = self.building_info[building_type]
			production = building.get_total_production_per_second(info)
			
			if production > 0:
				resource_type = info.production_resource
				if resource_type not in total_production:
					total_production[resource_type] = 0
				total_production[resource_type] += production
		
		return total_production
	
	def get_building_stats(self) -> dict:
		"""Obtiene estadísticas generales de edificios."""
		stats = {
			'total_buildings': sum(building.count for building in self.buildings.values()),
			'types_owned': sum(1 for building in self.buildings.values() if building.count > 0),
			'production_per_second': self.get_total_production_per_second()
		}
		return stats
	
	def get_save_data(self) -> dict:
		"""Obtiene datos para guardar."""
		return {
			'buildings': {
				building_type.value: {
					'count': building.count,
					'last_production_time': building.last_production_time
				}
				for building_type, building in self.buildings.items()
			}
		}
	
	def load_save_data(self, data: dict) -> None:
		"""Carga datos guardados."""
		if 'buildings' in data:
			for building_name, building_data in data['buildings'].items():
				try:
					building_type = BuildingType(building_name)
					building = self.buildings[building_type]
					building.count = building_data.get('count', 0)
					building.last_production_time = building_data.get('last_production_time', time.time())
				except (ValueError, KeyError) as e:
					logging.warning("Error cargando edificio %s: %s", building_name, e)
		
		logging.info("Edificios cargados desde guardado")
