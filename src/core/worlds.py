"""Sistema de mundos para SiKIdle.

Reemplaza el sistema de mazmorras con un sistema de mundos coherente
donde el jugador progresa a través de diferentes ambientes temáticos,
enfrentando enemigos y jefes en una progresión clara por fases.

Inspirado en AFK Arena y Tap Titans 2.
"""

import logging
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, List, Optional, Dict, Tuple
import random

from core.resources import ResourceType, ResourceManager
from core.enemies import EnemyType
from core.visual_assets import VisualAssetManager

logger = logging.getLogger(__name__)


class WorldType(Enum):
	"""Tipos de mundos disponibles en el juego."""

	ENCHANTED_FOREST = "enchanted_forest"  # Mundo 1: Bosque Encantado (1-50)
	BURNING_DESERT = "burning_desert"  # Mundo 2: Desierto Ardiente (51-100)
	FROZEN_MOUNTAINS = "frozen_mountains"  # Mundo 3: Montañas Heladas (101-150)
	DEEP_DUNGEONS = "deep_dungeons"  # Mundo 4: Mazmorras Profundas (151-200)
	TROPICAL_COAST = "tropical_coast"  # Mundo 5: Costa Tropical (201-250)
	ABANDONED_CITY = "abandoned_city"  # Mundo 6: Ciudad Abandonada (251-300)
	INDUSTRIAL_COMPLEX = "industrial_complex"  # Mundo 7: Complejo Industrial (301-350)
	SPACE_STATION = "space_station"  # Mundo 8: Estación Espacial (351-400)
	NETHER_REALM = "nether_realm"  # Mundo 9: Reino Infernal (401-450)


@dataclass
class WorldInfo:
	"""Información sobre un mundo específico."""

	name: str
	description: str
	emoji: str
	level_range: Tuple[int, int]  # (nivel_inicio, nivel_fin)
	unlock_cost: int  # Costo para desbloquear
	unlock_resource: ResourceType  # Recurso necesario para desbloquear
	unlock_level: int  # Nivel del jugador requerido

	# Enemigos por fases
	basic_enemies: List[EnemyType]  # Enemigos básicos (fases 1-20)
	intermediate_enemies: List[EnemyType]  # Enemigos intermedios (fases 21-35)
	advanced_enemies: List[EnemyType]  # Enemigos avanzados (fases 36-45)
	elite_enemies: List[EnemyType]  # Enemigos elite (fases 46-49)
	boss_enemy: EnemyType  # Jefe final (fase 50)

	# Mecánicas especiales del mundo
	special_mechanic: str  # Descripción de la mecánica especial
	mechanic_description: str  # Explicación detallada

	# Bonificaciones y recompensas
	base_gold_multiplier: float = 1.0  # Multiplicador de oro base
	base_exp_multiplier: float = 1.0  # Multiplicador de experiencia base
	completion_reward_gems: int = 50  # Gemas por completar el mundo
	first_clear_bonus: int = 100  # Bonus extra por primera vez


@dataclass
class WorldProgress:
	"""Progreso del jugador en un mundo específico."""

	world_type: WorldType
	unlocked: bool = False
	current_level: int = 1  # Nivel actual dentro del mundo (1-50)
	completed: bool = False  # Si el mundo está completado
	boss_defeated: bool = False  # Si el jefe final fue derrotado
	first_clear_claimed: bool = False  # Si se reclamó el bonus de primera vez
	times_completed: int = 0  # Veces que se completó (para farming)
	best_time: float = 0.0  # Mejor tiempo de completion
	total_enemies_defeated: int = 0  # Total de enemigos derrotados

	# Estadísticas por repetición
	completion_times: List[float] = None  # Tiempos de cada completion

	def __post_init__(self):
		if self.completion_times is None:
			self.completion_times = []


class World:
	"""Representa un mundo específico con su progresión."""

	def __init__(self, world_type: WorldType, world_info: WorldInfo):
		"""Inicializa un mundo.

		Args:
		    world_type: Tipo de mundo
		    world_info: Información del mundo
		"""
		self.world_type = world_type
		self.info = world_info
		self.progress = WorldProgress(world_type)

	def get_current_enemy_type(self) -> EnemyType:
		"""Obtiene el tipo de enemigo para el nivel actual."""
		level = self.progress.current_level

		# Determinar fase basada en el nivel
		if level <= 20:
			# Fases básicas (1-20)
			return random.choice(self.info.basic_enemies)
		elif level <= 35:
			# Fases intermedias (21-35)
			return random.choice(self.info.intermediate_enemies)
		elif level <= 45:
			# Fases avanzadas (36-45)
			return random.choice(self.info.advanced_enemies)
		elif level <= 49:
			# Fases elite (46-49)
			return random.choice(self.info.elite_enemies)
		else:
			# Jefe final (50)
			return self.info.boss_enemy

	def is_boss_level(self) -> bool:
		"""Verifica si el nivel actual es un jefe."""
		return self.progress.current_level == 50 or self.progress.current_level % 10 == 0

	def is_mini_boss_level(self) -> bool:
		"""Verifica si el nivel actual es un mini-jefe."""
		return self.progress.current_level % 5 == 0 and not self.is_boss_level()

	def get_level_difficulty_multiplier(self) -> float:
		"""Obtiene el multiplicador de dificultad para el nivel actual."""
		base_multiplier = 1.0 + (self.progress.current_level - 1) * 0.15

		# Bonus por repeticiones del mundo
		repetition_bonus = self.progress.times_completed * 0.25

		return base_multiplier + repetition_bonus

	def get_level_rewards_multiplier(self) -> float:
		"""Obtiene el multiplicador de recompensas para el nivel actual."""
		base_multiplier = self.info.base_gold_multiplier

		# Bonus por nivel
		level_bonus = (self.progress.current_level - 1) * 0.05

		# Bonus por repeticiones
		repetition_bonus = self.progress.times_completed * 0.5

		return base_multiplier + level_bonus + repetition_bonus

	def advance_level(self) -> Dict[str, Any]:
		"""Avanza al siguiente nivel del mundo.

		Returns:
		    Información sobre el avance y recompensas
		"""
		if self.progress.completed:
			return {"success": False, "message": "Mundo ya completado"}

		self.progress.current_level += 1
		self.progress.total_enemies_defeated += 1

		result = {
			"success": True,
			"new_level": self.progress.current_level,
			"is_boss": self.is_boss_level(),
			"is_mini_boss": self.is_mini_boss_level(),
			"rewards_multiplier": self.get_level_rewards_multiplier(),
		}

		# Verificar si se completó el mundo
		if self.progress.current_level > 50:
			self.progress.completed = True
			self.progress.boss_defeated = True
			self.progress.times_completed += 1
			self.progress.current_level = 1  # Reset para farming

			result.update(
				{
					"world_completed": True,
					"completion_reward": self.info.completion_reward_gems,
					"first_clear_bonus": self.info.first_clear_bonus
					if not self.progress.first_clear_claimed
					else 0,
				}
			)

			if not self.progress.first_clear_claimed:
				self.progress.first_clear_claimed = True

		return result

	def reset_for_farming(self) -> None:
		"""Resetea el mundo para farming (rejugarlo)."""
		if not self.progress.completed:
			return

		self.progress.current_level = 1
		self.progress.boss_defeated = False
		# Mantener completed=True para indicar que ya se completó antes

	def get_unlock_requirements(self) -> Dict[str, Any]:
		"""Obtiene los requisitos para desbloquear este mundo."""
		return {
			"cost": self.info.unlock_cost,
			"resource": self.info.unlock_resource,
			"player_level": self.info.unlock_level,
			"description": f"Desbloquear {self.info.name}",
		}


class WorldManager:
	"""Gestiona todos los mundos del juego."""

	def __init__(self, resource_manager: ResourceManager):
		"""Inicializa el gestor de mundos.

		Args:
		    resource_manager: Gestor de recursos del juego
		"""
		self.resource_manager = resource_manager
		self.worlds: Dict[WorldType, World] = {}
		self.active_world: Optional[WorldType] = None

		# Inicializar gestor de assets visuales
		self.visual_manager = VisualAssetManager()

		# Inicializar información de mundos
		self._initialize_world_info()

		# Crear instancias de mundos
		for world_type, world_info in self.world_info.items():
			self.worlds[world_type] = World(world_type, world_info)

		# Desbloquear el primer mundo
		self.worlds[WorldType.ENCHANTED_FOREST].progress.unlocked = True
		self.active_world = WorldType.ENCHANTED_FOREST

		# Precargar assets del mundo inicial
		if self.active_world:
			self.visual_manager.preload_world_assets(self.active_world.value)

		logger.info("WorldManager inicializado con %d mundos", len(self.worlds))

	def _initialize_world_info(self) -> None:
		"""Inicializa la información de todos los mundos."""
		self.world_info = {
			WorldType.ENCHANTED_FOREST: WorldInfo(
				name="Bosque Encantado",
				description="Un bosque mágico lleno de criaturas místicas y secretos antiguos",
				emoji="🌲",
				level_range=(1, 50),
				unlock_cost=0,  # Gratis - mundo inicial
				unlock_resource=ResourceType.COINS,
				unlock_level=1,
				basic_enemies=[EnemyType.GOBLIN, EnemyType.WOLF, EnemyType.WILD_BOAR],
				intermediate_enemies=[
					EnemyType.CAVE_BAT,
					EnemyType.GIANT_SPIDER,
					EnemyType.FOREST_SPRITE,
				],
				advanced_enemies=[
					EnemyType.CAVE_TROLL,
					EnemyType.CRYSTAL_GOLEM,
					EnemyType.SKELETON_WARRIOR,
				],
				elite_enemies=[EnemyType.ANCIENT_SPIRIT, EnemyType.STONE_GUARDIAN, EnemyType.LICH],
				boss_enemy=EnemyType.ORC_CHIEFTAIN,  # Usar un jefe disponible
				special_mechanic="Veneno y Regeneración",
				mechanic_description="Los enemigos pueden envenenar (niveles 15-25) y algunos se regeneran (niveles 30-40)",
				base_gold_multiplier=1.0,
				base_exp_multiplier=1.0,
				completion_reward_gems=50,
				first_clear_bonus=100,
			)
		}

		# Agregar más mundos cuando estén listos los enemigos correspondientes
		logger.info(
			"Información de mundos inicializada: %d mundos disponibles", len(self.world_info)
		)

	def get_active_world(self) -> Optional[World]:
		"""Obtiene el mundo actualmente activo."""
		if self.active_world:
			return self.worlds[self.active_world]
		return None

	def set_active_world(self, world_type: WorldType) -> bool:
		"""Establece el mundo activo.

		Args:
		    world_type: Tipo de mundo a activar

		Returns:
		    True si se activó correctamente
		"""
		world = self.worlds.get(world_type)
		if not world or not world.progress.unlocked:
			logger.warning(f"Intento de activar mundo bloqueado: {world_type}")
			return False

		self.active_world = world_type
		logger.info(f"Mundo activo cambiado a: {world.info.name}")
		return True

	def unlock_world(self, world_type: WorldType, player_level: int) -> Dict[str, Any]:
		"""Intenta desbloquear un mundo.

		Args:
		    world_type: Tipo de mundo a desbloquear
		    player_level: Nivel actual del jugador

		Returns:
		    Resultado del intento de desbloqueo
		"""
		world = self.worlds.get(world_type)
		if not world:
			return {"success": False, "message": "Mundo no encontrado"}

		if world.progress.unlocked:
			return {"success": False, "message": "Mundo ya desbloqueado"}

		# Verificar requisitos
		requirements = world.get_unlock_requirements()

		# Verificar nivel del jugador
		if player_level < requirements["player_level"]:
			return {
				"success": False,
				"message": f"Nivel {requirements['player_level']} requerido",
				"current_level": player_level,
			}

		# Verificar recursos
		if not self.resource_manager.can_afford(requirements["resource"], requirements["cost"]):
			return {
				"success": False,
				"message": f"Necesitas {requirements['cost']} {requirements['resource'].value}",
				"cost": requirements["cost"],
				"resource": requirements["resource"],
			}

		# Desbloquear mundo
		if self.resource_manager.spend_resource(requirements["resource"], requirements["cost"]):
			world.progress.unlocked = True
			logger.info(f"Mundo desbloqueado: {world.info.name}")
			return {
				"success": True,
				"message": f"¡{world.info.name} desbloqueado!",
				"world_name": world.info.name,
			}

		return {"success": False, "message": "Error procesando desbloqueo"}

	def advance_active_world(self) -> Dict[str, Any]:
		"""Avanza el nivel en el mundo activo.

		Returns:
		    Resultado del avance
		"""
		active_world = self.get_active_world()
		if not active_world:
			return {"success": False, "message": "No hay mundo activo"}

		return active_world.advance_level()

	def get_current_enemy(self) -> Optional[EnemyType]:
		"""Obtiene el enemigo actual del mundo activo."""
		active_world = self.get_active_world()
		if not active_world:
			return None

		return active_world.get_current_enemy_type()

	def get_world_progress_info(self, world_type: WorldType) -> Dict[str, Any]:
		"""Obtiene información detallada del progreso de un mundo."""
		world = self.worlds.get(world_type)
		if not world:
			return {}

		return {
			"world_name": world.info.name,
			"emoji": world.info.emoji,
			"unlocked": world.progress.unlocked,
			"current_level": world.progress.current_level,
			"level_range": world.info.level_range,
			"completed": world.progress.completed,
			"boss_defeated": world.progress.boss_defeated,
			"times_completed": world.progress.times_completed,
			"total_enemies_defeated": world.progress.total_enemies_defeated,
			"is_boss_level": world.is_boss_level(),
			"is_mini_boss_level": world.is_mini_boss_level(),
			"difficulty_multiplier": world.get_level_difficulty_multiplier(),
			"rewards_multiplier": world.get_level_rewards_multiplier(),
			"special_mechanic": world.info.special_mechanic,
			"unlock_requirements": world.get_unlock_requirements()
			if not world.progress.unlocked
			else None,
		}

	def get_all_worlds_info(self) -> List[Dict[str, Any]]:
		"""Obtiene información de todos los mundos."""
		return [self.get_world_progress_info(world_type) for world_type in WorldType]

	def reset_world_for_farming(self, world_type: WorldType) -> bool:
		"""Resetea un mundo completado para farming.

		Args:
		    world_type: Tipo de mundo a resetear

		Returns:
		    True si se reseteó correctamente
		"""
		world = self.worlds.get(world_type)
		if not world or not world.progress.completed:
			return False

		world.reset_for_farming()
		logger.info(f"Mundo reseteado para farming: {world.info.name}")
		return True

	def get_next_world_to_unlock(self) -> Optional[WorldType]:
		"""Obtiene el siguiente mundo que se puede desbloquear."""
		for world_type in WorldType:
			world = self.worlds[world_type]
			if not world.progress.unlocked:
				return world_type
		return None

	def save_progress(self) -> Dict[str, Any]:
		"""Guarda el progreso de todos los mundos.

		Returns:
		    Datos de progreso para guardar
		"""
		progress_data = {
			"active_world": self.active_world.value if self.active_world else None,
			"worlds": {},
		}

		for world_type, world in self.worlds.items():
			progress_data["worlds"][world_type.value] = {
				"unlocked": world.progress.unlocked,
				"current_level": world.progress.current_level,
				"completed": world.progress.completed,
				"boss_defeated": world.progress.boss_defeated,
				"first_clear_claimed": world.progress.first_clear_claimed,
				"times_completed": world.progress.times_completed,
				"best_time": world.progress.best_time,
				"total_enemies_defeated": world.progress.total_enemies_defeated,
				"completion_times": world.progress.completion_times,
			}

		return progress_data

	def load_progress(self, progress_data: Dict[str, Any]) -> None:
		"""Carga el progreso de todos los mundos.

		Args:
		    progress_data: Datos de progreso guardados
		"""
		try:
			# Cargar mundo activo
			if progress_data.get("active_world"):
				self.active_world = WorldType(progress_data["active_world"])

			# Cargar progreso de mundos
			worlds_data = progress_data.get("worlds", {})
			for world_type_str, world_data in worlds_data.items():
				try:
					world_type = WorldType(world_type_str)
					world = self.worlds[world_type]

					# Cargar datos de progreso
					world.progress.unlocked = world_data.get("unlocked", False)
					world.progress.current_level = world_data.get("current_level", 1)
					world.progress.completed = world_data.get("completed", False)
					world.progress.boss_defeated = world_data.get("boss_defeated", False)
					world.progress.first_clear_claimed = world_data.get(
						"first_clear_claimed", False
					)
					world.progress.times_completed = world_data.get("times_completed", 0)
					world.progress.best_time = world_data.get("best_time", 0.0)
					world.progress.total_enemies_defeated = world_data.get(
						"total_enemies_defeated", 0
					)
					world.progress.completion_times = world_data.get("completion_times", [])

				except (ValueError, KeyError) as e:
					logger.warning(f"Error cargando progreso del mundo {world_type_str}: {e}")

			logger.info("Progreso de mundos cargado correctamente")

		except Exception as e:
			logger.error(f"Error cargando progreso de mundos: {e}")
			# En caso de error, mantener estado por defecto

	# Métodos visuales
	def get_world_background_path(self, world_type: WorldType) -> str:
		"""Obtiene la ruta del fondo para un mundo específico."""
		theme = self.visual_manager.get_world_theme(world_type.value)
		if theme:
			return self.visual_manager.get_background_path(theme.background)
		return self.visual_manager.get_background_path(BackgroundType.MAIN)


def get_world_theme_colors(self, world_type: WorldType) -> Dict[str, str]:
	"""Obtiene los colores del tema para un mundo específico."""
	return self.visual_manager.get_ui_theme_colors(world_type.value)


def get_enemy_visual_effects(self, world_type: WorldType, enemy_tier: str) -> List:
	"""Obtiene los efectos visuales para un enemigo en un mundo específico."""
	return self.visual_manager.get_enemy_effects(world_type.value, enemy_tier)


def preload_world_visuals(self, world_type: WorldType) -> bool:
	"""Precarga todos los assets visuales para un mundo."""
	return self.visual_manager.preload_world_assets(world_type.value)


def set_active_world_with_transition(self, world_type: WorldType, effects_manager=None) -> bool:
	"""Cambia el mundo activo con efectos de transición visual."""
	if world_type not in self.worlds:
		logger.warning(f"Mundo no encontrado: {world_type}")
		return False

	if not self.worlds[world_type].progress.unlocked:
		logger.warning(f"Mundo no desbloqueado: {world_type}")
		return False

	old_world = self.active_world

	# Precargar assets del nuevo mundo
	if not self.preload_world_visuals(world_type):
		logger.warning(f"Error precargando assets para: {world_type}")

	# Cambiar mundo activo
	self.active_world = world_type

	# Mostrar efecto de transición si se proporciona el manager
	if effects_manager and old_world:
		old_theme = self.visual_manager.get_world_theme(old_world.value)
		new_theme = self.visual_manager.get_world_theme(world_type.value)

		if old_theme and new_theme:
			effects_manager.show_world_transition(old_theme.name, new_theme.name)

	logger.info(f"Mundo activo cambiado a: {world_type.value}")
	return True


def cleanup_visual_assets(self):
	"""Limpia assets visuales no utilizados."""
	self.visual_manager.cleanup_unused_assets()
