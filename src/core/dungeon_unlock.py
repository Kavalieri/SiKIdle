"""
Sistema de Desbloqueo Avanzado de Mazmorras para SiKIdle.

Este módulo gestiona las condiciones complejas de desbloqueo de mazmorras,
incluyendo requisitos de nivel, derrota de bosses, recursos especiales,
y logros completados.

Autor: GitHub Copilot
Fecha: 04 de agosto de 2025
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Callable, Any, Union
import time

from core.resources import ResourceType, ResourceManager
from core.dungeons import DungeonType, DungeonManager


class UnlockConditionType(Enum):
	"""Tipos de condiciones de desbloqueo disponibles."""
	PLAYER_LEVEL = "player_level"				# Nivel mínimo del jugador
	BOSS_DEFEATED = "boss_defeated"			# Boss específico derrotado
	RESOURCE_REQUIREMENT = "resource_requirement"	# Recursos específicos
	ACHIEVEMENT_COMPLETED = "achievement_completed"	# Logro completado
	DUNGEON_EXPLORED = "dungeon_explored"		# Mazmorra explorada al X%
	TIME_PLAYED = "time_played"				# Tiempo total de juego
	ENEMIES_DEFEATED = "enemies_defeated"		# Número de enemigos derrotados
	SPECIAL_KEY = "special_key"				# Llave especial obtenida


@dataclass
class UnlockCondition:
	"""
	Representa una condición individual para desbloquear una mazmorra.
	
	Attributes:
		condition_type: Tipo de condición
		required_value: Valor requerido para cumplir la condición
		target: Objetivo específico (boss, logro, etc.)
		description: Descripción legible de la condición
		validator: Función opcional para validación personalizada
	"""
	condition_type: UnlockConditionType
	required_value: Any
	target: Optional[str] = None
	description: str = ""
	validator: Optional[Callable[..., bool]] = None
	
	def __post_init__(self):
		"""Genera descripción automática si no se proporciona."""
		if not self.description:
			self.description = self._generate_description()
	
	def _generate_description(self) -> str:
		"""Genera una descripción legible de la condición."""
		if self.condition_type == UnlockConditionType.PLAYER_LEVEL:
			return f"Alcanzar nivel {self.required_value}"
		elif self.condition_type == UnlockConditionType.BOSS_DEFEATED:
			return f"Derrotar al boss {self.target}"
		elif self.condition_type == UnlockConditionType.RESOURCE_REQUIREMENT:
			return f"Obtener {self.required_value} {self.target}"
		elif self.condition_type == UnlockConditionType.ACHIEVEMENT_COMPLETED:
			return f"Completar logro: {self.target}"
		elif self.condition_type == UnlockConditionType.DUNGEON_EXPLORED:
			return f"Explorar {self.target} al {self.required_value}%"
		elif self.condition_type == UnlockConditionType.TIME_PLAYED:
			hours = self.required_value / 3600
			return f"Jugar durante {hours:.1f} horas"
		elif self.condition_type == UnlockConditionType.ENEMIES_DEFEATED:
			return f"Derrotar {self.required_value} enemigos"
		elif self.condition_type == UnlockConditionType.SPECIAL_KEY:
			return f"Obtener {self.target}"
		else:
			return "Condición desconocida"


@dataclass
class UnlockRequirement:
	"""
	Conjunto de condiciones requeridas para desbloquear una mazmorra.
	
	Attributes:
		dungeon_type: Tipo de mazmorra a desbloquear
		conditions: Lista de condiciones que deben cumplirse
		require_all: Si True, todas las condiciones deben cumplirse
		unlock_message: Mensaje mostrado al desbloquear
		warning_message: Mensaje de advertencia si es muy difícil
	"""
	dungeon_type: DungeonType
	conditions: List[UnlockCondition]
	require_all: bool = True  # AND vs OR logic
	unlock_message: str = ""
	warning_message: str = ""
	
	def __post_init__(self):
		"""Genera mensajes automáticos si no se proporcionan."""
		if not self.unlock_message:
			self.unlock_message = f"¡{self.dungeon_type.value.replace('_', ' ').title()} desbloqueada!"
		
		if not self.warning_message:
			self.warning_message = f"⚠️ {self.dungeon_type.value.replace('_', ' ').title()} es un área peligrosa"


class DungeonUnlockManager:
	"""
	Gestor principal del sistema de desbloqueo de mazmorras.
	
	Maneja todas las condiciones de desbloqueo, validación de requisitos,
	y proporciona información sobre progreso hacia desbloqueos.
	"""
	
	def __init__(self, dungeon_manager: DungeonManager, resource_manager: ResourceManager):
		"""
		Inicializa el gestor de desbloqueos.
		
		Args:
			dungeon_manager: Gestor de mazmorras
			resource_manager: Gestor de recursos
		"""
		self.dungeon_manager = dungeon_manager
		self.resource_manager = resource_manager
		
		# Registro de desbloqueos especiales
		self.special_keys: Dict[str, bool] = {}
		self.boss_defeats: Dict[str, bool] = {}
		self.exploration_records: Dict[DungeonType, float] = {}
		
		# Configuración de requisitos por mazmorra
		self.unlock_requirements: Dict[DungeonType, UnlockRequirement] = {}
		self._initialize_unlock_requirements()
		
		# Estadísticas para validación
		self.total_enemies_defeated = 0
		self.total_playtime = 0.0
		self.session_start_time = time.time()
	
	def _initialize_unlock_requirements(self) -> None:
		"""
		Inicializa todos los requisitos de desbloqueo para cada mazmorra.
		
		Define condiciones progresivamente más complejas para crear
		una progresión estructurada y desafiante.
		"""
		
		# Bosque Encantado - Mazmorra inicial (desbloqueada por defecto)
		self.unlock_requirements[DungeonType.ENCHANTED_FOREST] = UnlockRequirement(
			dungeon_type=DungeonType.ENCHANTED_FOREST,
			conditions=[],  # Sin condiciones - siempre disponible
			unlock_message="🌲 ¡Bienvenido al Bosque Encantado!",
			warning_message="🌿 Área segura para principiantes"
		)
		
		# Cuevas Profundas - Requisitos básicos
		self.unlock_requirements[DungeonType.DEEP_CAVES] = UnlockRequirement(
			dungeon_type=DungeonType.DEEP_CAVES,
			conditions=[
				UnlockCondition(
					condition_type=UnlockConditionType.PLAYER_LEVEL,
					required_value=10,
					description="Alcanzar nivel 10"
				),
				UnlockCondition(
					condition_type=UnlockConditionType.DUNGEON_EXPLORED,
					required_value=50.0,
					target="Bosque Encantado",
					description="Explorar el Bosque Encantado al 50%"
				),
				UnlockCondition(
					condition_type=UnlockConditionType.RESOURCE_REQUIREMENT,
					required_value=1000,
					target="coins",
					description="Acumular 1,000 monedas"
				)
			],
			unlock_message="🕳️ ¡Las Cuevas Profundas te esperan!",
			warning_message="⚠️ Ambiente hostil - enemigos más resistentes"
		)
		
		# Ruinas Antiguas - Requisitos intermedios
		self.unlock_requirements[DungeonType.ANCIENT_RUINS] = UnlockRequirement(
			dungeon_type=DungeonType.ANCIENT_RUINS,
			conditions=[
				UnlockCondition(
					condition_type=UnlockConditionType.PLAYER_LEVEL,
					required_value=25,
					description="Alcanzar nivel 25"
				),
				UnlockCondition(
					condition_type=UnlockConditionType.BOSS_DEFEATED,
					required_value=True,
					target="Cave Troll",
					description="Derrotar al Cave Troll de las Cuevas"
				),
				UnlockCondition(
					condition_type=UnlockConditionType.ENEMIES_DEFEATED,
					required_value=500,
					description="Derrotar 500 enemigos en total"
				),
				UnlockCondition(
					condition_type=UnlockConditionType.SPECIAL_KEY,
					required_value=True,
					target="Llave Antigua",
					description="Obtener la Llave Antigua"
				)
			],
			unlock_message="🏛️ ¡Los secretos de las Ruinas Antiguas se revelan!",
			warning_message="⚠️ Magia arcana peligrosa - nivel recomendado 25+"
		)
		
		# Fortaleza Orc - Requisitos avanzados
		self.unlock_requirements[DungeonType.ORC_FORTRESS] = UnlockRequirement(
			dungeon_type=DungeonType.ORC_FORTRESS,
			conditions=[
				UnlockCondition(
					condition_type=UnlockConditionType.PLAYER_LEVEL,
					required_value=50,
					description="Alcanzar nivel 50"
				),
				UnlockCondition(
					condition_type=UnlockConditionType.BOSS_DEFEATED,
					required_value=True,
					target="Ancient Spirit",
					description="Derrotar al Ancient Spirit de las Ruinas"
				),
				UnlockCondition(
					condition_type=UnlockConditionType.TIME_PLAYED,
					required_value=7200,  # 2 horas
					description="Jugar durante 2 horas"
				),
				UnlockCondition(
					condition_type=UnlockConditionType.ACHIEVEMENT_COMPLETED,
					required_value=True,
					target="explorer_veteran",
					description="Completar logro 'Explorador Veterano'"
				)
			],
			unlock_message="🏰 ¡La Fortaleza Orc está bajo asedio!",
			warning_message="💀 PELIGRO EXTREMO - Solo para guerreros experimentados"
		)
		
		# Dimensión Sombría - Requisitos épicos
		self.unlock_requirements[DungeonType.SHADOW_DIMENSION] = UnlockRequirement(
			dungeon_type=DungeonType.SHADOW_DIMENSION,
			conditions=[
				UnlockCondition(
					condition_type=UnlockConditionType.PLAYER_LEVEL,
					required_value=75,
					description="Alcanzar nivel 75"
				),
				UnlockCondition(
					condition_type=UnlockConditionType.BOSS_DEFEATED,
					required_value=True,
					target="Orc Chieftain",
					description="Derrotar al Orc Chieftain"
				),
				UnlockCondition(
					condition_type=UnlockConditionType.DUNGEON_EXPLORED,
					required_value=100.0,
					target="Fortaleza Orc",
					description="Completar totalmente la Fortaleza Orc"
				),
				UnlockCondition(
					condition_type=UnlockConditionType.SPECIAL_KEY,
					required_value=True,
					target="Fragmento Dimensional",
					description="Obtener un Fragmento Dimensional"
				),
				UnlockCondition(
					condition_type=UnlockConditionType.ENEMIES_DEFEATED,
					required_value=2000,
					description="Derrotar 2,000 enemigos en total"
				)
			],
			require_all=True,
			unlock_message="🌌 ¡Las barreras dimensionales se han roto!",
			warning_message="💀💀 ÁREA LETAL - Solo para los más poderosos"
		)
	
	def check_unlock_conditions(self, dungeon_type: DungeonType, player_level: int, 
								player_stats: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
		"""
		Verifica si una mazmorra puede ser desbloqueada.
		
		Args:
			dungeon_type: Tipo de mazmorra a verificar
			player_level: Nivel actual del jugador
			player_stats: Estadísticas adicionales del jugador
			
		Returns:
			Diccionario con información de desbloqueo
		"""
		if dungeon_type not in self.unlock_requirements:
			return {
				"can_unlock": False,
				"error": "Mazmorra no configurada",
				"conditions_met": [],
				"conditions_failed": [],
				"progress": 0.0
			}
		
		requirement = self.unlock_requirements[dungeon_type]
		conditions_met: List[UnlockCondition] = []
		conditions_failed: List[UnlockCondition] = []
		
		# Verificar cada condición
		for condition in requirement.conditions:
			is_met = self._check_single_condition(condition, player_level, player_stats)
			
			if is_met:
				conditions_met.append(condition)
			else:
				conditions_failed.append(condition)
		
		# Determinar si puede desbloquearse
		if requirement.require_all:
			can_unlock = len(conditions_failed) == 0
		else:
			can_unlock = len(conditions_met) > 0
		
		# Calcular progreso
		total_conditions = len(requirement.conditions)
		if total_conditions == 0:
			progress = 1.0
		else:
			progress = len(conditions_met) / total_conditions
		
		return {
			"can_unlock": can_unlock,
			"conditions_met": conditions_met,
			"conditions_failed": conditions_failed,
			"progress": progress,
			"unlock_message": requirement.unlock_message if can_unlock else "",
			"warning_message": requirement.warning_message,
			"require_all": requirement.require_all
		}
	
	def _check_single_condition(self, condition: UnlockCondition, player_level: int,
							   player_stats: Optional[Dict[str, Any]] = None) -> bool:
		"""
		Verifica una condición individual de desbloqueo.
		
		Args:
			condition: Condición a verificar
			player_level: Nivel del jugador
			player_stats: Estadísticas del jugador
			
		Returns:
			True si la condición se cumple
		"""
		try:
			# Verificar validador personalizado primero
			if condition.validator:
				return condition.validator(condition, player_level, player_stats)
			
			# Verificaciones estándar
			if condition.condition_type == UnlockConditionType.PLAYER_LEVEL:
				return player_level >= condition.required_value
			
			elif condition.condition_type == UnlockConditionType.BOSS_DEFEATED:
				if condition.target:
					return self.boss_defeats.get(condition.target, False)
				return False
			
			elif condition.condition_type == UnlockConditionType.RESOURCE_REQUIREMENT:
				if condition.target == "coins":
					return self.resource_manager.get_resource(ResourceType.COINS) >= condition.required_value
				# Agregar otros tipos de recursos según sea necesario
				return False
			
			elif condition.condition_type == UnlockConditionType.DUNGEON_EXPLORED:
				if condition.target:
					dungeon_type = self._get_dungeon_type_by_name(condition.target)
					if dungeon_type:
						exploration = self.exploration_records.get(dungeon_type, 0.0)
						return exploration >= condition.required_value
				return False
			
			elif condition.condition_type == UnlockConditionType.TIME_PLAYED:
				current_playtime = self.total_playtime + (time.time() - self.session_start_time)
				return current_playtime >= condition.required_value
			
			elif condition.condition_type == UnlockConditionType.ENEMIES_DEFEATED:
				return self.total_enemies_defeated >= condition.required_value
			
			elif condition.condition_type == UnlockConditionType.SPECIAL_KEY:
				if condition.target:
					return self.special_keys.get(condition.target, False)
				return False
			
			return False
			
		except Exception as e:
			print(f"Error verificando condición {condition.condition_type}: {e}")
			return False
	
	def _get_dungeon_type_by_name(self, name: str) -> Optional[DungeonType]:
		"""Convierte nombre de mazmorra a DungeonType."""
		name_mapping = {
			"Bosque Encantado": DungeonType.ENCHANTED_FOREST,
			"Cuevas Profundas": DungeonType.DEEP_CAVES,
			"Ruinas Antiguas": DungeonType.ANCIENT_RUINS,
			"Fortaleza Orc": DungeonType.ORC_FORTRESS,
			"Dimensión Sombría": DungeonType.SHADOW_DIMENSION
		}
		return name_mapping.get(name)
	
	def register_boss_defeat(self, boss_name: str) -> None:
		"""
		Registra la derrota de un boss para desbloqueos futuros.
		
		Args:
			boss_name: Nombre del boss derrotado
		"""
		self.boss_defeats[boss_name] = True
		print(f"🏆 Boss derrotado registrado: {boss_name}")
	
	def register_special_key(self, key_name: str) -> None:
		"""
		Registra la obtención de una llave especial.
		
		Args:
			key_name: Nombre de la llave obtenida
		"""
		self.special_keys[key_name] = True
		print(f"🗝️ Llave especial obtenida: {key_name}")
	
	def update_exploration_progress(self, dungeon_type: DungeonType, progress: float) -> None:
		"""
		Actualiza el progreso de exploración de una mazmorra.
		
		Args:
			dungeon_type: Tipo de mazmorra
			progress: Progreso de exploración (0.0-100.0)
		"""
		self.exploration_records[dungeon_type] = progress
	
	def add_enemies_defeated(self, count: int) -> None:
		"""
		Añade enemigos derrotados al contador total.
		
		Args:
			count: Número de enemigos derrotados
		"""
		self.total_enemies_defeated += count
	
	def update_playtime(self, additional_time: float) -> None:
		"""
		Actualiza el tiempo total de juego.
		
		Args:
			additional_time: Tiempo adicional en segundos
		"""
		self.total_playtime += additional_time
	
	def get_all_unlock_status(self, player_level: int, 
							 player_stats: Optional[Dict[str, Any]] = None) -> Dict[DungeonType, Dict[str, Any]]:
		"""
		Obtiene el estado de desbloqueo de todas las mazmorras.
		
		Args:
			player_level: Nivel del jugador
			player_stats: Estadísticas del jugador
			
		Returns:
			Diccionario con estado de cada mazmorra
		"""
		status = {}
		
		for dungeon_type in DungeonType:
			status[dungeon_type] = self.check_unlock_conditions(
				dungeon_type, player_level, player_stats
			)
		
		return status
	
	def get_next_unlockable_dungeon(self, player_level: int,
								   player_stats: Optional[Dict[str, Any]] = None) -> Optional[DungeonType]:
		"""
		Obtiene la siguiente mazmorra que puede ser desbloqueada.
		
		Args:
			player_level: Nivel del jugador
			player_stats: Estadísticas del jugador
			
		Returns:
			Siguiente mazmorra desbloqueable o None
		"""
		all_status = self.get_all_unlock_status(player_level, player_stats)
		
		best_candidate = None
		best_progress = 0.0
		
		for dungeon_type, status in all_status.items():
			# Skip si ya está desbloqueada
			if self.dungeon_manager.get_dungeon(dungeon_type).unlocked:
				continue
			
			# Si puede desbloquearse, es la mejor opción
			if status["can_unlock"]:
				return dungeon_type
			
			# Sino, buscar la que tiene más progreso
			if status["progress"] > best_progress:
				best_progress = status["progress"]
				best_candidate = dungeon_type
		
		return best_candidate
	
	def get_unlock_hints(self, dungeon_type: DungeonType, player_level: int,
						player_stats: Optional[Dict[str, Any]] = None) -> List[str]:
		"""
		Obtiene pistas sobre cómo desbloquear una mazmorra.
		
		Args:
			dungeon_type: Tipo de mazmorra
			player_level: Nivel del jugador
			player_stats: Estadísticas del jugador
			
		Returns:
			Lista de pistas para el jugador
		"""
		status = self.check_unlock_conditions(dungeon_type, player_level, player_stats)
		hints = []
		
		if status["can_unlock"]:
			hints.append("✅ ¡Todas las condiciones cumplidas! Puedes desbloquear esta área.")
			return hints
		
		for condition in status["conditions_failed"]:
			hint = f"❌ {condition.description}"
			
			# Añadir información específica de progreso
			if condition.condition_type == UnlockConditionType.PLAYER_LEVEL:
				needed = condition.required_value - player_level
				hint += f" (faltan {needed} niveles)"
			
			elif condition.condition_type == UnlockConditionType.RESOURCE_REQUIREMENT:
				if condition.target == "coins":
					current = self.resource_manager.get_resource(ResourceType.COINS)
					needed = condition.required_value - current
					hint += f" (faltan {needed} monedas)"
			
			elif condition.condition_type == UnlockConditionType.ENEMIES_DEFEATED:
				needed = condition.required_value - self.total_enemies_defeated
				hint += f" (faltan {needed} enemigos)"
			
			hints.append(hint)
		
		return hints
	
	def attempt_unlock(self, dungeon_type: DungeonType, player_level: int,
					  player_stats: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
		"""
		Intenta desbloquear una mazmorra específica.
		
		Args:
			dungeon_type: Tipo de mazmorra a desbloquear
			player_level: Nivel del jugador
			player_stats: Estadísticas del jugador
			
		Returns:
			Resultado del intento de desbloqueo
		"""
		status = self.check_unlock_conditions(dungeon_type, player_level, player_stats)
		
		if not status["can_unlock"]:
			return {
				"success": False,
				"message": "No cumples todos los requisitos",
				"hints": self.get_unlock_hints(dungeon_type, player_level, player_stats)
			}
		
		# Intentar desbloquear en el DungeonManager
		dungeon = self.dungeon_manager.get_dungeon(dungeon_type)
		dungeon_info = self.dungeon_manager.get_dungeon_info(dungeon_type)
		
		success = dungeon.unlock(dungeon_info, self.resource_manager)
		
		if success:
			return {
				"success": True,
				"message": status["unlock_message"],
				"warning": status["warning_message"],
				"dungeon_type": dungeon_type
			}
		else:
			return {
				"success": False,
				"message": "Error interno al desbloquear",
				"hints": ["Contacta al soporte si este error persiste"]
			}
	
	def get_unlock_summary(self) -> Dict[str, Any]:
		"""
		Obtiene un resumen completo del estado de desbloqueos.
		
		Returns:
			Resumen con estadísticas y estado actual
		"""
		return {
			"total_enemies_defeated": self.total_enemies_defeated,
			"total_playtime": self.total_playtime + (time.time() - self.session_start_time),
			"special_keys_obtained": list(self.special_keys.keys()),
			"bosses_defeated": list(self.boss_defeats.keys()),
			"exploration_records": {dt.value: progress for dt, progress in self.exploration_records.items()},
			"dungeons_unlocked": len([d for d in self.dungeon_manager.dungeons.values() if d.unlocked]),
			"total_dungeons": len(DungeonType)
		}
