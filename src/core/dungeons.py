"""Sistema de mazmorras y exploración para SiKIdle.

Gestiona todas las mazmorras temáticas que reemplazan a los edificios industriales.
"""

import logging
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, List, Optional, Dict, Tuple
import random

from core.resources import ResourceType, ResourceManager
from core.enemies import EnemyType
from core.biomes import BiomeType, BiomeManager


class DungeonType(Enum):
	"""Tipos de mazmorras disponibles en el juego."""
	# Mazmorras por orden de desbloqueado
	ENCHANTED_FOREST = "enchanted_forest"        # Bosque Encantado (1-10)
	DEEP_CAVES = "deep_caves"                   # Cuevas Profundas (11-25)
	ANCIENT_RUINS = "ancient_ruins"             # Ruinas Antiguas (26-50)
	ORC_FORTRESS = "orc_fortress"               # Fortaleza Orc (51-75)
	SHADOW_DIMENSION = "shadow_dimension"        # Dimensión Sombría (76+)


@dataclass
class DungeonInfo:
	"""Información sobre un tipo de mazmorra."""
	name: str
	description: str
	emoji: str
	biome: BiomeType
	unlock_cost: int                    # Costo para desbloquear
	base_enemy_level: int              # Nivel base de enemigos
	max_enemy_level: int               # Nivel máximo de enemigos
	enemy_types: List[EnemyType]       # Tipos de enemigos disponibles
	unlock_level: int                  # Nivel del jugador requerido
	unlock_resource: ResourceType = ResourceType.COINS
	boss_enemy: Optional[EnemyType] = None  # Enemigo boss opcional
	
	# Bonificaciones especiales del bioma
	damage_bonus: float = 0.0          # Bonificación de daño
	defense_bonus: float = 0.0         # Bonificación de defensa
	speed_bonus: float = 0.0           # Bonificación de velocidad
	exp_bonus: float = 0.0             # Bonificación de experiencia
	loot_bonus: float = 0.0            # Bonificación de loot raro


class Dungeon:
	"""Representa una instancia específica de una mazmorra."""
	
	def __init__(self, dungeon_type: DungeonType, unlocked: bool = False):
		"""Inicializa una mazmorra.
		
		Args:
			dungeon_type: Tipo de mazmorra
			unlocked: Si la mazmorra está desbloqueada
		"""
		self.dungeon_type = dungeon_type
		self.unlocked = unlocked
		self.last_exploration_time = time.time()
		self.total_enemies_defeated = 0
		self.boss_defeated = False
		self.exploration_progress = 0.0  # 0.0 - 1.0 (100% completa)
	
	def can_unlock(self, info: 'DungeonInfo', resource_manager: ResourceManager, player_level: int) -> bool:
		"""Verifica si la mazmorra puede ser desbloqueada.
		
		Args:
			info: Información de la mazmorra
			resource_manager: Gestor de recursos
			player_level: Nivel actual del jugador
			
		Returns:
			True si puede ser desbloqueada
		"""
		if self.unlocked:
			return False
		
		# Verificar nivel del jugador
		if player_level < info.unlock_level:
			return False
		
		# Verificar recursos suficientes
		if not resource_manager.can_afford(info.unlock_resource, info.unlock_cost):
			return False
		
		return True
	
	def unlock(self, info: 'DungeonInfo', resource_manager: ResourceManager) -> bool:
		"""Desbloquea la mazmorra gastando recursos.
		
		Args:
			info: Información de la mazmorra
			resource_manager: Gestor de recursos
			
		Returns:
			True si se desbloqueó exitosamente
		"""
		if self.unlocked:
			return False
		
		if resource_manager.spend_resource(info.unlock_resource, info.unlock_cost):
			self.unlocked = True
			logging.info(f"Mazmorra {info.name} desbloqueada por {info.unlock_cost} {info.unlock_resource.value}")
			return True
		
		return False
	
	def get_current_enemy_level(self, info: 'DungeonInfo') -> int:
		"""Calcula el nivel actual de enemigos según el progreso.
		
		Args:
			info: Información de la mazmorra
			
		Returns:
			Nivel de enemigo apropiado
		"""
		# El nivel aumenta con el progreso de exploración
		level_range = info.max_enemy_level - info.base_enemy_level
		progress_bonus = int(level_range * self.exploration_progress)
		
		return info.base_enemy_level + progress_bonus
	
	def get_random_enemy_type(self, info: 'DungeonInfo', force_boss: bool = False) -> EnemyType:
		"""Selecciona un tipo de enemigo aleatorio para esta mazmorra.
		
		Args:
			info: Información de la mazmorra
			force_boss: Si forzar un enemigo boss
			
		Returns:
			Tipo de enemigo seleccionado
		"""
		if force_boss and info.boss_enemy:
			return info.boss_enemy
		
		# 5% de probabilidad de boss si está disponible y mazmorra > 50% completa
		if (info.boss_enemy and 
			self.exploration_progress > 0.5 and 
			random.random() < 0.05):
			return info.boss_enemy
		
		# Seleccionar enemigo regular aleatorio
		return random.choice(info.enemy_types)
	
	def advance_exploration(self, enemies_defeated: int = 1) -> float:
		"""Avanza el progreso de exploración.
		
		Args:
			enemies_defeated: Número de enemigos derrotados
			
		Returns:
			Nuevo progreso de exploración (0.0 - 1.0)
		"""
		self.total_enemies_defeated += enemies_defeated
		
		# Cada enemigo aporta 0.1% de progreso, slowing down over time
		progress_per_enemy = 0.001 * (1.0 - self.exploration_progress * 0.5)
		self.exploration_progress = min(1.0, self.exploration_progress + progress_per_enemy)
		
		return self.exploration_progress
	
	def get_biome_bonuses(self, info: 'DungeonInfo') -> Dict[str, float]:
		"""Obtiene las bonificaciones activas del bioma.
		
		Args:
			info: Información de la mazmorra
			
		Returns:
			Diccionario con bonificaciones aplicables
		"""
		return {
			'damage_multiplier': 1.0 + info.damage_bonus,
			'defense_multiplier': 1.0 + info.defense_bonus,
			'speed_multiplier': 1.0 + info.speed_bonus,
			'exp_multiplier': 1.0 + info.exp_bonus,
			'loot_multiplier': 1.0 + info.loot_bonus
		}


class DungeonManager:
	"""Gestiona todas las mazmorras del juego."""
	
	def __init__(self, resource_manager: ResourceManager):
		"""Inicializa el gestor de mazmorras.
		
		Args:
			resource_manager: Gestor de recursos del juego
		"""
		self.resource_manager = resource_manager
		self.biome_manager = BiomeManager()
		self.dungeons: Dict[DungeonType, Dungeon] = {}
		self.active_dungeon: Optional[DungeonType] = None
		
		# Información de cada tipo de mazmorra
		self.dungeon_info = {
			DungeonType.ENCHANTED_FOREST: DungeonInfo(
				name="Bosque Encantado",
				description="Un bosque mágico lleno de criaturas místicas",
				emoji="🌲",
				biome=BiomeType.ENCHANTED_FOREST,
				unlock_cost=0,  # Gratis - mazmorra inicial
				base_enemy_level=1,
				max_enemy_level=10,
				enemy_types=[EnemyType.GOBLIN, EnemyType.WOLF, EnemyType.WILD_BOAR, EnemyType.FOREST_SPRITE],
				unlock_level=1,
				speed_bonus=0.15,  # +15% velocidad de ataque
				loot_bonus=0.10    # +10% loot de materiales naturales
			),
			
			DungeonType.DEEP_CAVES: DungeonInfo(
				name="Cuevas Profundas",
				description="Cavernas oscuras con criaturas subterráneas",
				emoji="🕳️",
				biome=BiomeType.DEEP_CAVES,
				unlock_cost=500,
				base_enemy_level=11,
				max_enemy_level=25,
				enemy_types=[EnemyType.CAVE_BAT, EnemyType.GIANT_SPIDER, EnemyType.CAVE_TROLL, EnemyType.CRYSTAL_GOLEM],
				unlock_level=10,
				defense_bonus=0.20,  # +20% defensa
				loot_bonus=0.15      # +15% probabilidad de gemas
			),
			
			DungeonType.ANCIENT_RUINS: DungeonInfo(
				name="Ruinas Antiguas",
				description="Restos de una civilización perdida",
				emoji="🏛️",
				biome=BiomeType.ANCIENT_RUINS,
				unlock_cost=2500,
				base_enemy_level=26,
				max_enemy_level=50,
				enemy_types=[EnemyType.SKELETON_WARRIOR, EnemyType.ANCIENT_SPIRIT, EnemyType.STONE_GUARDIAN, EnemyType.LICH],
				unlock_level=25,
				boss_enemy=EnemyType.LICH,
				exp_bonus=0.25,      # +25% experiencia
				loot_bonus=0.20      # +20% artefactos únicos
			),
			
			DungeonType.ORC_FORTRESS: DungeonInfo(
				name="Fortaleza Orc",
				description="Bastión militar de los clanes orcos",
				emoji="🏰",
				biome=BiomeType.ORC_FORTRESS,
				unlock_cost=10000,
				base_enemy_level=51,
				max_enemy_level=75,
				enemy_types=[EnemyType.ORC_GRUNT, EnemyType.ORC_SHAMAN, EnemyType.ORC_WARLORD, EnemyType.ORC_CHIEFTAIN],
				unlock_level=50,
				boss_enemy=EnemyType.ORC_CHIEFTAIN,
				damage_bonus=0.30,   # +30% daño
				loot_bonus=0.25      # +25% armas de guerra
			),
			
			DungeonType.SHADOW_DIMENSION: DungeonInfo(
				name="Dimensión Sombría",
				description="Plano de existencia corrompido por la oscuridad",
				emoji="🌌",
				biome=BiomeType.SHADOW_DIMENSION,
				unlock_cost=50000,
				base_enemy_level=76,
				max_enemy_level=100,
				enemy_types=[EnemyType.SHADOW_DEMON, EnemyType.VOID_WALKER, EnemyType.ANCIENT_DRAGON, EnemyType.DIMENSIONAL_LORD],
				unlock_level=75,
				boss_enemy=EnemyType.DIMENSIONAL_LORD,
				damage_bonus=0.10,   # Bonificaciones variables
				defense_bonus=0.10,
				speed_bonus=0.10,
				exp_bonus=0.10,
				loot_bonus=0.30      # +30% loot legendario
			)
		}
		
		# Inicializar todas las mazmorras
		for dungeon_type in DungeonType:
			unlocked = (dungeon_type == DungeonType.ENCHANTED_FOREST)  # Solo primera desbloqueada
			self.dungeons[dungeon_type] = Dungeon(dungeon_type, unlocked)
		
		# Activar la primera mazmorra por defecto
		self.active_dungeon = DungeonType.ENCHANTED_FOREST
	
	def get_dungeon_info(self, dungeon_type: DungeonType) -> DungeonInfo:
		"""Obtiene información sobre un tipo de mazmorra.
		
		Args:
			dungeon_type: Tipo de mazmorra
			
		Returns:
			Información de la mazmorra
		"""
		return self.dungeon_info[dungeon_type]
	
	def get_dungeon(self, dungeon_type: DungeonType) -> Dungeon:
		"""Obtiene una instancia de mazmorra.
		
		Args:
			dungeon_type: Tipo de mazmorra
			
		Returns:
			Instancia de la mazmorra
		"""
		return self.dungeons[dungeon_type]
	
	def get_unlocked_dungeons(self) -> List[DungeonType]:
		"""Obtiene lista de mazmorras desbloqueadas.
		
		Returns:
			Lista de tipos de mazmorra desbloqueadas
		"""
		return [dt for dt, dungeon in self.dungeons.items() if dungeon.unlocked]
	
	def get_next_dungeon_to_unlock(self, player_level: int) -> Optional[DungeonType]:
		"""Obtiene la siguiente mazmorra que puede ser desbloqueada.
		
		Args:
			player_level: Nivel del jugador
			
		Returns:
			Tipo de mazmorra o None si no hay disponibles
		"""
		for dungeon_type in DungeonType:
			dungeon = self.dungeons[dungeon_type]
			info = self.dungeon_info[dungeon_type]
			
			if not dungeon.unlocked and player_level >= info.unlock_level:
				return dungeon_type
		
		return None
	
	def can_unlock_dungeon(self, dungeon_type: DungeonType, player_level: int) -> bool:
		"""Verifica si una mazmorra puede ser desbloqueada.
		
		Args:
			dungeon_type: Tipo de mazmorra
			player_level: Nivel del jugador
			
		Returns:
			True si puede ser desbloqueada
		"""
		dungeon = self.dungeons[dungeon_type]
		info = self.dungeon_info[dungeon_type]
		
		return dungeon.can_unlock(info, self.resource_manager, player_level)
	
	def unlock_dungeon(self, dungeon_type: DungeonType) -> bool:
		"""Desbloquea una mazmorra.
		
		Args:
			dungeon_type: Tipo de mazmorra a desbloquear
			
		Returns:
			True si se desbloqueó exitosamente
		"""
		dungeon = self.dungeons[dungeon_type]
		info = self.dungeon_info[dungeon_type]
		
		if dungeon.unlock(info, self.resource_manager):
			logging.info(f"Mazmorra {info.name} desbloqueada")
			return True
		
		return False
	
	def set_active_dungeon(self, dungeon_type: DungeonType) -> bool:
		"""Establece la mazmorra activa para exploración.
		
		Args:
			dungeon_type: Tipo de mazmorra a activar
			
		Returns:
			True si se activó correctamente
		"""
		dungeon = self.dungeons[dungeon_type]
		
		if not dungeon.unlocked:
			logging.warning(f"Intento de activar mazmorra bloqueada: {dungeon_type}")
			return False
		
		self.active_dungeon = dungeon_type
		logging.info(f"Mazmorra activa cambiada a: {self.dungeon_info[dungeon_type].name}")
		return True
	
	def get_active_dungeon_info(self) -> Optional[tuple]:
		"""Obtiene información de la mazmorra activa.
		
		Returns:
			Tupla (DungeonType, Dungeon, DungeonInfo) o None
		"""
		if not self.active_dungeon:
			return None
		
		dungeon_type = self.active_dungeon
		dungeon = self.dungeons[dungeon_type]
		info = self.dungeon_info[dungeon_type]
		
		return (dungeon_type, dungeon, info)
	
	def generate_enemy_for_active_dungeon(self, force_boss: bool = False) -> Optional[tuple]:
		"""Genera un enemigo para la mazmorra activa.
		
		Args:
			force_boss: Si forzar generación de boss
			
		Returns:
			Tupla (EnemyType, level) o None si no hay mazmorra activa
		"""
		active_info = self.get_active_dungeon_info()
		if not active_info:
			return None
		
		dungeon_type, dungeon, info = active_info
		
		enemy_type = dungeon.get_random_enemy_type(info, force_boss)
		enemy_level = dungeon.get_current_enemy_level(info)
		
		return (enemy_type, enemy_level)
	
	def on_enemy_defeated(self, enemy_level: int) -> Dict[str, Any]:
		"""Procesa la derrota de un enemigo en la mazmorra activa.
		
		Args:
			enemy_level: Nivel del enemigo derrotado
			
		Returns:
			Diccionario con información del progreso
		"""
		active_info = self.get_active_dungeon_info()
		if not active_info:
			return {}
		
		dungeon_type, dungeon, info = active_info
		
		# Avanzar progreso de exploración
		old_progress = dungeon.exploration_progress
		new_progress = dungeon.advance_exploration(1)
		
		# Obtener bonificaciones del bioma
		bonuses = dungeon.get_biome_bonuses(info)
		
		result = {
			'dungeon_name': info.name,
			'exploration_progress': new_progress,
			'progress_gained': new_progress - old_progress,
			'total_enemies_defeated': dungeon.total_enemies_defeated,
			'biome_bonuses': bonuses,
			'dungeon_completed': new_progress >= 1.0
		}
		
		if new_progress >= 1.0 and not dungeon.boss_defeated:
			dungeon.boss_defeated = True
			result['boss_unlocked'] = True
		
		return result
	
	def get_dungeon_status_summary(self) -> Dict[str, Any]:
		"""Obtiene un resumen del estado de todas las mazmorras.
		
		Returns:
			Diccionario con información de estado
		"""
		summary = {
			'active_dungeon': self.active_dungeon.value if self.active_dungeon else None,
			'unlocked_count': len(self.get_unlocked_dungeons()),
			'total_count': len(DungeonType),
			'dungeons': {}
		}
		
		for dungeon_type, dungeon in self.dungeons.items():
			info = self.dungeon_info[dungeon_type]
			summary['dungeons'][dungeon_type.value] = {
				'name': info.name,
				'unlocked': dungeon.unlocked,
				'exploration_progress': dungeon.exploration_progress,
				'enemies_defeated': dungeon.total_enemies_defeated,
				'boss_defeated': dungeon.boss_defeated,
				'unlock_cost': info.unlock_cost,
				'unlock_level': info.unlock_level
			}
		
		return summary
	
	def get_active_biome_bonuses(self) -> Dict[str, float]:
		"""
		Obtiene las bonificaciones del bioma activo actual.
		
		Returns:
			Diccionario con bonificaciones aplicables al combate
		"""
		if not self.active_dungeon:
			return self.biome_manager.get_combat_bonuses()
		
		# Obtener el bioma de la mazmorra activa
		active_info = self.get_dungeon_info(self.active_dungeon)
		return self.biome_manager.get_combat_bonuses(active_info.biome)
	
	def get_active_biome_visual_theme(self):
		"""
		Obtiene el tema visual del bioma activo.
		
		Returns:
			BiomeVisualData para aplicar tema visual o None
		"""
		if not self.active_dungeon:
			return self.biome_manager.get_visual_theme()
		
		# Obtener el bioma de la mazmorra activa
		active_info = self.get_dungeon_info(self.active_dungeon)
		return self.biome_manager.get_visual_theme(active_info.biome)
	
	def get_active_biome_colors(self) -> Dict[str, Tuple[float, float, float, float]]:
		"""
		Obtiene los colores del bioma activo en formato Kivy.
		
		Returns:
			Diccionario con colores en formato RGBA normalizado
		"""
		if not self.active_dungeon:
			return self.biome_manager.get_kivy_colors()
		
		# Obtener el bioma de la mazmorra activa
		active_info = self.get_dungeon_info(self.active_dungeon)
		return self.biome_manager.get_kivy_colors(active_info.biome)
	
	def update_biome_manager_for_active_dungeon(self) -> None:
		"""
		Actualiza el BiomeManager para reflejar la mazmorra activa.
		
		Esto sincroniza el bioma activo en el BiomeManager con
		el bioma de la mazmorra actualmente seleccionada.
		"""
		if self.active_dungeon:
			active_info = self.get_dungeon_info(self.active_dungeon)
			self.biome_manager.set_current_biome(active_info.biome)
		else:
			# Si no hay mazmorra activa, limpiar bioma activo
			self.biome_manager.set_current_biome(None)
	
	def get_biome_description_for_dungeon(self, dungeon_type: DungeonType) -> str:
		"""
		Obtiene la descripción completa del bioma para una mazmorra específica.
		
		Args:
			dungeon_type: Tipo de mazmorra
			
		Returns:
			Descripción detallada del bioma con bonificaciones
		"""
		dungeon_info = self.get_dungeon_info(dungeon_type)
		return self.biome_manager.get_biome_description_with_bonuses(dungeon_info.biome)
