"""
Sistema de Talentos de Combate para SiKIdle Dungeon Crawler.

Este módulo gestiona el árbol de talentos especializado en combate con 4 ramas:
- 🗡️ Guerrero: Daño físico, críticos y velocidad de ataque
- 🏹 Explorador: Loot finder, velocidad de exploración y resistencias  
- 🔮 Mago: Habilidades mágicas, regeneración de maná y daño elemental
- 🛡️ Tanque: Defensa, salud y absorción de daño

Cada talento tiene niveles escalables con prerequisitos balanceados para combate.
"""

import logging
import time
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Set, Any

from core.resources import ResourceType, ResourceManager


class TalentBranch(Enum):
	"""Ramas del árbol de talentos especializadas en combate."""

	WARRIOR = "warrior"  # 🗡️ Guerrero
	EXPLORER = "explorer"  # 🏹 Explorador
	MAGE = "mage"  # 🔮 Mago
	TANK = "tank"  # 🛡️ Tanque


class TalentTier(Enum):
	"""Niveles de tier de talentos."""

	TIER_1 = 1
	TIER_2 = 2
	TIER_3 = 3


class TalentType(Enum):
	"""Tipos específicos de talentos de combate disponibles."""

	# 🗡️ Rama Guerrero - Tier 1
	WARRIOR_STRENGTH = "warrior_strength"
	WARRIOR_CRITICAL = "warrior_critical"
	WARRIOR_SPEED = "warrior_speed"

	# 🗡️ Rama Guerrero - Tier 2
	WARRIOR_BERSERKER = "warrior_berserker"
	WARRIOR_WEAPON_MASTER = "warrior_weapon_master"

	# 🗡️ Rama Guerrero - Tier 3
	WARRIOR_DEVASTATION = "warrior_devastation"

	# 🏹 Rama Explorador - Tier 1
	EXPLORER_TREASURE = "explorer_treasure"
	EXPLORER_SPEED = "explorer_speed"
	EXPLORER_LUCK = "explorer_luck"

	# 🏹 Rama Explorador - Tier 2
	EXPLORER_TRAP_DETECTION = "explorer_trap_detection"
	EXPLORER_LEGENDARY_SEEKER = "explorer_legendary_seeker"

	# 🏹 Rama Explorador - Tier 3
	EXPLORER_DIMENSIONAL_TRAVEL = "explorer_dimensional_travel"

	# 🔮 Rama Mago - Tier 1
	MAGE_ELEMENTAL = "mage_elemental"
	MAGE_INTELLECT = "mage_intellect"
	MAGE_MANA_EFFICIENCY = "mage_mana_efficiency"

	# 🔮 Rama Mago - Tier 2
	MAGE_MANA_SHIELD = "mage_mana_shield"
	MAGE_SPELL_ECHO = "mage_spell_echo"

	# 🔮 Rama Mago - Tier 3
	MAGE_TRANSCENDENCE = "mage_transcendence"

	# 🛡️ Rama Tanque - Tier 1
	TANK_IRON_SKIN = "tank_iron_skin"
	TANK_HEALTH_BOOST = "tank_health_boost"
	TANK_REGENERATION = "tank_regeneration"

	# 🛡️ Rama Tanque - Tier 2
	TANK_LAST_STAND = "tank_last_stand"
	TANK_GUARDIAN_AURA = "tank_guardian_aura"

	# 🛡️ Rama Tanque - Tier 3
	TANK_IMMORTAL = "tank_immortal"


@dataclass
class TalentInfo:
	"""Información estática de un talento."""

	name: str
	description: str
	branch: TalentBranch
	tier: TalentTier
	emoji: str
	max_level: int
	base_effect: float
	scaling_factor: float
	prerequisites: List[TalentType]
	cost_progression: List[int]  # Costo en puntos por cada nivel


class Talent:
	"""Instancia de un talento del jugador."""

	def __init__(self, talent_type: TalentType, info: TalentInfo):
		"""Inicializa un talento del jugador.

		Args:
			talent_type: Tipo de talento
			info: Información del talento
		"""
		self.talent_type = talent_type
		self.info = info
		self.level = 0
		self.unlocked = False

	def can_upgrade(self, available_points: int, unlocked_talents: Set[TalentType]) -> bool:
		"""Verifica si el talento puede ser mejorado.

		Args:
			available_points: Puntos de talento disponibles
			unlocked_talents: Set de talentos ya desbloqueados

		Returns:
			True si puede ser mejorado
		"""
		# Verificar si ya está al máximo
		if self.level >= self.info.max_level:
			return False

		# Verificar si tiene puntos suficientes
		next_cost = self.get_upgrade_cost()
		if available_points < next_cost:
			return False

		# Verificar prerequisitos
		for prereq in self.info.prerequisites:
			if prereq not in unlocked_talents:
				return False

		return True

	def get_upgrade_cost(self) -> int:
		"""Obtiene el costo para el siguiente nivel.

		Returns:
			Costo en puntos de talento
		"""
		if self.level >= self.info.max_level:
			return 0

		if self.level < len(self.info.cost_progression):
			return self.info.cost_progression[self.level]

		# Fallback para niveles no definidos
		return self.info.cost_progression[-1] * 2

	def get_current_effect(self) -> float:
		"""Calcula el efecto actual del talento.

		Returns:
			Valor del efecto actual
		"""
		if self.level == 0:
			return 0.0

		return self.info.base_effect + (self.level - 1) * self.info.scaling_factor

	def upgrade(self) -> bool:
		"""Mejora el talento un nivel.

		Returns:
			True si fue mejorado exitosamente
		"""
		if self.level < self.info.max_level:
			self.level += 1
			if not self.unlocked:
				self.unlocked = True
			logging.info(f"Talento {self.info.name} mejorado a nivel {self.level}")
			return True
		return False


class TalentManager:
	"""Gestiona el sistema completo de talentos."""

	def __init__(self, resource_manager: ResourceManager):
		"""Inicializa el gestor de talentos.

		Args:
			resource_manager: Gestor de recursos del juego
		"""
		self.resource_manager = resource_manager
		self.talents: Dict[TalentType, Talent] = {}
		self.talent_info: Dict[TalentType, TalentInfo] = {}
		self.talent_points = 0
		self.total_points_earned = 0
		self.total_points_spent = 0

		# Callback para cuando se actualiza un talento
		self.on_talent_updated_callback = None

		# Inicializar información de talentos
		self._initialize_talent_info()

		# Crear instancias de talentos
		self._create_talent_instances()

		logging.info("Sistema de talentos inicializado")

	def _initialize_talent_info(self):
		"""Inicializa la información de todos los talentos de combate."""
		# Costos progresivos para talentos (Fibonacci-like)
		standard_costs = [1, 2, 3, 5, 8, 13, 21, 34, 55, 89]
		advanced_costs = [2, 4, 6, 10, 16, 26, 42, 68, 110, 178]

		self.talent_info = {
			# 🗡️ RAMA GUERRERO - TIER 1
			TalentType.WARRIOR_STRENGTH: TalentInfo(
				name="Fuerza Bruta",
				description="Aumenta el daño físico base",
				branch=TalentBranch.WARRIOR,
				tier=TalentTier.TIER_1,
				emoji="�",
				max_level=10,
				base_effect=0.08,  # +8% daño base
				scaling_factor=0.08,  # +8% por nivel adicional
				prerequisites=[],
				cost_progression=standard_costs,
			),
			TalentType.WARRIOR_CRITICAL: TalentInfo(
				name="Golpe Crítico",
				description="Aumenta la probabilidad de ataques críticos",
				branch=TalentBranch.WARRIOR,
				tier=TalentTier.TIER_1,
				emoji="⚔️",
				max_level=10,
				base_effect=0.03,  # +3% crítico base
				scaling_factor=0.03,  # +3% por nivel adicional
				prerequisites=[],
				cost_progression=standard_costs,
			),
			TalentType.WARRIOR_SPEED: TalentInfo(
				name="Velocidad de Ataque",
				description="Aumenta la velocidad de ataques automáticos",
				branch=TalentBranch.WARRIOR,
				tier=TalentTier.TIER_1,
				emoji="⚡",
				max_level=10,
				base_effect=0.05,  # +5% velocidad base
				scaling_factor=0.05,  # +5% por nivel adicional
				prerequisites=[],
				cost_progression=standard_costs,
			),

			# 🗡️ RAMA GUERRERO - TIER 2
			TalentType.WARRIOR_BERSERKER: TalentInfo(
				name="Furia Berserker",
				description="Daño aumenta con enemigos derrotados recientemente",
				branch=TalentBranch.WARRIOR,
				tier=TalentTier.TIER_2,
				emoji="😡",
				max_level=5,
				base_effect=0.02,  # +2% daño por stack base
				scaling_factor=0.02,  # +2% por nivel adicional
				prerequisites=[TalentType.WARRIOR_STRENGTH, TalentType.WARRIOR_CRITICAL],
				cost_progression=advanced_costs,
			),
			TalentType.WARRIOR_WEAPON_MASTER: TalentInfo(
				name="Maestro de Armas",
				description="Aumenta la efectividad de armas equipadas",
				branch=TalentBranch.WARRIOR,
				tier=TalentTier.TIER_2,
				emoji="🗡️",
				max_level=5,
				base_effect=0.10,  # +10% efectividad base
				scaling_factor=0.10,  # +10% por nivel adicional
				prerequisites=[TalentType.WARRIOR_SPEED],
				cost_progression=advanced_costs,
			),

			# 🗡️ RAMA GUERRERO - TIER 3
			TalentType.WARRIOR_DEVASTATION: TalentInfo(
				name="Devastación",
				description="Ataques tienen probabilidad de hacer daño masivo",
				branch=TalentBranch.WARRIOR,
				tier=TalentTier.TIER_3,
				emoji="�",
				max_level=3,
				base_effect=0.05,  # +5% probabilidad devastación
				scaling_factor=0.05,  # +5% por nivel adicional
				prerequisites=[TalentType.WARRIOR_BERSERKER, TalentType.WARRIOR_WEAPON_MASTER],
				cost_progression=[5, 10, 20],
			),

			# 🏹 RAMA EXPLORADOR - TIER 1
			TalentType.EXPLORER_TREASURE: TalentInfo(
				name="Cazatesoros",
				description="Aumenta la probabilidad de encontrar loot raro",
				branch=TalentBranch.EXPLORER,
				tier=TalentTier.TIER_1,
				emoji="💎",
				max_level=10,
				base_effect=0.05,  # +5% loot raro base
				scaling_factor=0.05,  # +5% por nivel adicional
				prerequisites=[],
				cost_progression=standard_costs,
			),
			TalentType.EXPLORER_SPEED: TalentInfo(
				name="Explorador Rápido",
				description="Aumenta la velocidad de exploración de mazmorras",
				branch=TalentBranch.EXPLORER,
				tier=TalentTier.TIER_1,
				emoji="🏃",
				max_level=10,
				base_effect=0.08,  # +8% velocidad exploración
				scaling_factor=0.08,  # +8% por nivel adicional
				prerequisites=[],
				cost_progression=standard_costs,
			),
			TalentType.EXPLORER_LUCK: TalentInfo(
				name="Suerte del Aventurero",
				description="Mejora la calidad general del loot encontrado",
				branch=TalentBranch.EXPLORER,
				tier=TalentTier.TIER_1,
				emoji="🍀",
				max_level=10,
				base_effect=0.03,  # +3% calidad loot
				scaling_factor=0.03,  # +3% por nivel adicional
				prerequisites=[],
				cost_progression=standard_costs,
			),

			# 🏹 RAMA EXPLORADOR - TIER 2
			TalentType.EXPLORER_TRAP_DETECTION: TalentInfo(
				name="Detección de Trampas",
				description="Evita efectos negativos de enemigos especiales",
				branch=TalentBranch.EXPLORER,
				tier=TalentTier.TIER_2,
				emoji="🕷️",
				max_level=5,
				base_effect=0.20,  # +20% resistencia efectos
				scaling_factor=0.20,  # +20% por nivel adicional
				prerequisites=[TalentType.EXPLORER_SPEED],
				cost_progression=advanced_costs,
			),
			TalentType.EXPLORER_LEGENDARY_SEEKER: TalentInfo(
				name="Buscador de Leyendas",
				description="Probabilidad de forzar aparición de loot legendario",
				branch=TalentBranch.EXPLORER,
				tier=TalentTier.TIER_2,
				emoji="�",
				max_level=5,
				base_effect=0.005,  # +0.5% legendario base
				scaling_factor=0.005,  # +0.5% por nivel adicional
				prerequisites=[TalentType.EXPLORER_TREASURE, TalentType.EXPLORER_LUCK],
				cost_progression=advanced_costs,
			),

			# 🏹 RAMA EXPLORADOR - TIER 3
			TalentType.EXPLORER_DIMENSIONAL_TRAVEL: TalentInfo(
				name="Viaje Dimensional",
				description="Acceso a áreas secretas con loot único",
				branch=TalentBranch.EXPLORER,
				tier=TalentTier.TIER_3,
				emoji="🌀",
				max_level=3,
				base_effect=0.1,  # +10% acceso áreas secretas
				scaling_factor=0.1,  # +10% por nivel adicional
				prerequisites=[TalentType.EXPLORER_TRAP_DETECTION, TalentType.EXPLORER_LEGENDARY_SEEKER],
				cost_progression=[5, 10, 20],
			),

			# 🔮 RAMA MAGO - TIER 1
			TalentType.MAGE_ELEMENTAL: TalentInfo(
				name="Maestría Elemental",
				description="Ataques aplican efectos elementales aleatorios",
				branch=TalentBranch.MAGE,
				tier=TalentTier.TIER_1,
				emoji="�",
				max_level=10,
				base_effect=0.15,  # +15% probabilidad elemental
				scaling_factor=0.15,  # +15% por nivel adicional
				prerequisites=[],
				cost_progression=standard_costs,
			),
			TalentType.MAGE_INTELLECT: TalentInfo(
				name="Intelecto Arcano",
				description="Aumenta la experiencia ganada en combate",
				branch=TalentBranch.MAGE,
				tier=TalentTier.TIER_1,
				emoji="📚",
				max_level=10,
				base_effect=0.05,  # +5% experiencia base
				scaling_factor=0.05,  # +5% por nivel adicional
				prerequisites=[],
				cost_progression=standard_costs,
			),
			TalentType.MAGE_MANA_EFFICIENCY: TalentInfo(
				name="Eficiencia de Maná",
				description="Reduce el costo de habilidades mágicas",
				branch=TalentBranch.MAGE,
				tier=TalentTier.TIER_1,
				emoji="�",
				max_level=10,
				base_effect=0.10,  # -10% costo maná base
				scaling_factor=0.05,  # -5% por nivel adicional
				prerequisites=[],
				cost_progression=standard_costs,
			),

			# 🔮 RAMA MAGO - TIER 2
			TalentType.MAGE_MANA_SHIELD: TalentInfo(
				name="Escudo de Maná",
				description="Absorbe parte del daño recibido usando maná",
				branch=TalentBranch.MAGE,
				tier=TalentTier.TIER_2,
				emoji="🛡️",
				max_level=5,
				base_effect=0.15,  # +15% absorción base
				scaling_factor=0.15,  # +15% por nivel adicional
				prerequisites=[TalentType.MAGE_ELEMENTAL, TalentType.MAGE_MANA_EFFICIENCY],
				cost_progression=advanced_costs,
			),
			TalentType.MAGE_SPELL_ECHO: TalentInfo(
				name="Eco Hechizo",
				description="Probabilidad de repetir el último ataque mágico",
				branch=TalentBranch.MAGE,
				tier=TalentTier.TIER_2,
				emoji="�",
				max_level=5,
				base_effect=0.15,  # +15% probabilidad eco
				scaling_factor=0.15,  # +15% por nivel adicional
				prerequisites=[TalentType.MAGE_INTELLECT],
				cost_progression=advanced_costs,
			),

			# 🔮 RAMA MAGO - TIER 3
			TalentType.MAGE_TRANSCENDENCE: TalentInfo(
				name="Trascendencia",
				description="Efectos mágicos afectan múltiples enemigos",
				branch=TalentBranch.MAGE,
				tier=TalentTier.TIER_3,
				emoji="✨",
				max_level=3,
				base_effect=0.5,  # +50% área de efecto
				scaling_factor=0.5,  # +50% por nivel adicional
				prerequisites=[TalentType.MAGE_MANA_SHIELD, TalentType.MAGE_SPELL_ECHO],
				cost_progression=[5, 10, 20],
			),

			# 🛡️ RAMA TANQUE - TIER 1
			TalentType.TANK_IRON_SKIN: TalentInfo(
				name="Piel de Hierro",
				description="Reduce el daño recibido de todos los ataques",
				branch=TalentBranch.TANK,
				tier=TalentTier.TIER_1,
				emoji="🛡️",
				max_level=10,
				base_effect=0.03,  # +3% reducción daño base
				scaling_factor=0.03,  # +3% por nivel adicional
				prerequisites=[],
				cost_progression=standard_costs,
			),
			TalentType.TANK_HEALTH_BOOST: TalentInfo(
				name="Vitalidad Mejorada",
				description="Aumenta la salud máxima del personaje",
				branch=TalentBranch.TANK,
				tier=TalentTier.TIER_1,
				emoji="❤️",
				max_level=10,
				base_effect=50.0,  # +50 salud base
				scaling_factor=50.0,  # +50 por nivel adicional
				prerequisites=[],
				cost_progression=standard_costs,
			),
			TalentType.TANK_REGENERATION: TalentInfo(
				name="Regeneración",
				description="Regenera salud continuamente durante el combate",
				branch=TalentBranch.TANK,
				tier=TalentTier.TIER_1,
				emoji="💚",
				max_level=10,
				base_effect=0.02,  # +2% regeneración base
				scaling_factor=0.02,  # +2% por nivel adicional
				prerequisites=[],
				cost_progression=standard_costs,
			),

			# 🛡️ RAMA TANQUE - TIER 2
			TalentType.TANK_LAST_STAND: TalentInfo(
				name="Última Resistencia",
				description="Daño aumenta cuando la salud es muy baja",
				branch=TalentBranch.TANK,
				tier=TalentTier.TIER_2,
				emoji="⚰️",
				max_level=5,
				base_effect=1.0,  # +100% daño cuando salud < 25%
				scaling_factor=1.0,  # +100% por nivel adicional
				prerequisites=[TalentType.TANK_IRON_SKIN, TalentType.TANK_HEALTH_BOOST],
				cost_progression=advanced_costs,
			),
			TalentType.TANK_GUARDIAN_AURA: TalentInfo(
				name="Aura de Guardián",
				description="Efectos protectores adicionales en combate",
				branch=TalentBranch.TANK,
				tier=TalentTier.TIER_2,
				emoji="🌟",
				max_level=5,
				base_effect=0.10,  # +10% resistencia total
				scaling_factor=0.10,  # +10% por nivel adicional
				prerequisites=[TalentType.TANK_REGENERATION],
				cost_progression=advanced_costs,
			),

			# 🛡️ RAMA TANQUE - TIER 3
			TalentType.TANK_IMMORTAL: TalentInfo(
				name="Inmortal",
				description="Probabilidad de sobrevivir ataques letales",
				branch=TalentBranch.TANK,
				tier=TalentTier.TIER_3,
				emoji="👑",
				max_level=3,
				base_effect=0.05,  # +5% probabilidad supervivencia
				scaling_factor=0.05,  # +5% por nivel adicional
				prerequisites=[TalentType.TANK_LAST_STAND, TalentType.TANK_GUARDIAN_AURA],
				cost_progression=[5, 10, 20],
			),
		}

	def _create_talent_instances(self):
		"""Crea instancias de todos los talentos."""
		for talent_type, info in self.talent_info.items():
			self.talents[talent_type] = Talent(talent_type, info)

	def add_talent_points(self, points: int):
		"""Añade puntos de talento disponibles.

		Args:
			points: Número de puntos a añadir
		"""
		self.talent_points += points
		self.total_points_earned += points
		logging.info(f"Añadidos {points} puntos de talento. Total disponible: {self.talent_points}")

	def can_upgrade_talent(self, talent_type: TalentType) -> bool:
		"""Verifica si un talento puede ser mejorado.

		Args:
			talent_type: Tipo de talento a verificar

		Returns:
			True si puede ser mejorado
		"""
		if talent_type not in self.talents:
			return False

		talent = self.talents[talent_type]
		unlocked_talents = {t for t, talent_inst in self.talents.items() if talent_inst.unlocked}

		return talent.can_upgrade(self.talent_points, unlocked_talents)

	def upgrade_talent(self, talent_type: TalentType) -> bool:
		"""Mejora un talento específico.

		Args:
			talent_type: Tipo de talento a mejorar

		Returns:
			True si fue mejorado exitosamente
		"""
		if not self.can_upgrade_talent(talent_type):
			return False

		talent = self.talents[talent_type]
		cost = talent.get_upgrade_cost()

		if talent.upgrade():
			self.talent_points -= cost
			self.total_points_spent += cost

			# Verificar logros relacionados con talentos
			self._check_talent_achievements()

			# Ejecutar callback si existe
			if self.on_talent_updated_callback:
				try:
					self.on_talent_updated_callback(talent_type.value, talent.level, talent.info)
				except Exception as e:
					logging.error(f"Error en callback de talento actualizado: {e}")

			logging.info(f"Talento {talent.info.name} mejorado a nivel {talent.level}")
			return True

		return False

	def get_talent_effect(self, talent_type: TalentType) -> float:
		"""Obtiene el efecto actual de un talento.

		Args:
			talent_type: Tipo de talento

		Returns:
			Valor del efecto actual
		"""
		if talent_type not in self.talents:
			return 0.0

		return self.talents[talent_type].get_current_effect()

	def get_branch_talents(self, branch: TalentBranch) -> Dict[str, TalentInfo]:
		"""Obtiene todos los talentos de una rama específica.

		Args:
			branch: Rama a consultar

		Returns:
			Diccionario con los talentos de la rama
		"""
		return {
			talent_id.value: talent_info
			for talent_id, talent_info in self.talent_info.items()
			if talent_info.branch == branch
		}

	def get_talent_level(self, talent_type: TalentType) -> int:
		"""Obtiene el nivel actual de un talento.

		Args:
			talent_type: Tipo de talento

		Returns:
			Nivel actual del talento
		"""
		if talent_type not in self.talents:
			return 0
		return self.talents[talent_type].level

	def get_branch_summary(self, branch: TalentBranch) -> Dict[str, int]:
		"""Obtiene resumen de una rama de talentos.

		Args:
			branch: Rama a resumir

		Returns:
			Diccionario con información de la rama
		"""
		branch_talents = [t for t in self.talents.values() if t.info.branch == branch]

		total_levels = sum(t.level for t in branch_talents)
		unlocked_count = sum(1 for t in branch_talents if t.unlocked)
		points_invested = sum(sum(t.info.cost_progression[: t.level]) for t in branch_talents)

		return {
			"total_talents": len(branch_talents),
			"unlocked_talents": unlocked_count,
			"total_levels": total_levels,
			"points_invested": points_invested,
			"branch_power": total_levels * 10,  # Métrica simple de poder
		}

	def reset_talents(self) -> int:
		"""Reinicia todos los talentos y devuelve puntos.

		Returns:
			Número de puntos devueltos
		"""
		points_returned = self.total_points_spent

		for talent in self.talents.values():
			talent.level = 0
			talent.unlocked = False

		self.talent_points += points_returned
		self.total_points_spent = 0

		logging.info(f"Talentos reiniciados. {points_returned} puntos devueltos")
		return points_returned

	def set_talent_updated_callback(self, callback) -> None:
		"""Establece callback para cuando se actualiza un talento"""
		self.on_talent_updated_callback = callback

	def get_talent_stats(self) -> Dict[str, object]:
		"""Obtiene estadísticas generales de talentos.

		Returns:
			Diccionario con estadísticas
		"""
		unlocked_count = sum(1 for t in self.talents.values() if t.unlocked)
		total_levels = sum(t.level for t in self.talents.values())

		branch_stats = {}
		for branch in TalentBranch:
			branch_stats[branch.value] = self.get_branch_summary(branch)

		return {
			"available_points": self.talent_points,
			"total_points_earned": self.total_points_earned,
			"total_points_spent": self.total_points_spent,
			"unlocked_talents": unlocked_count,
			"total_talent_levels": total_levels,
			"branch_stats": branch_stats,
		}

	def _check_talent_achievements(self):
		"""Verifica logros relacionados con talentos."""
		# Esta función se integrará con el sistema de logros
		# Por ahora es un placeholder para futuras implementaciones
		pass

	def calculate_total_multipliers(self) -> Dict[str, float]:
		"""Calcula todos los multiplicadores activos por talentos de combate.

		Returns:
			Diccionario con multiplicadores por categoría
		"""
		multipliers = {
			"physical_damage": 1.0,
			"critical_chance": 0.0,
			"attack_speed": 1.0,
			"loot_rarity_chance": 1.0,
			"exploration_speed": 1.0,
			"elemental_chance": 0.0,
			"experience_gain": 1.0,
			"damage_reduction": 0.0,
			"max_health_bonus": 0.0,
			"health_regeneration": 0.0,
		}

		# Aplicar efectos de talentos guerrero
		multipliers["physical_damage"] += self.get_talent_effect(TalentType.WARRIOR_STRENGTH)
		multipliers["critical_chance"] += self.get_talent_effect(TalentType.WARRIOR_CRITICAL)
		multipliers["attack_speed"] += self.get_talent_effect(TalentType.WARRIOR_SPEED)

		# Aplicar efectos de talentos explorador
		multipliers["loot_rarity_chance"] += self.get_talent_effect(TalentType.EXPLORER_TREASURE)
		multipliers["exploration_speed"] += self.get_talent_effect(TalentType.EXPLORER_SPEED)

		# Aplicar efectos de talentos mago
		multipliers["elemental_chance"] += self.get_talent_effect(TalentType.MAGE_ELEMENTAL)
		multipliers["experience_gain"] += self.get_talent_effect(TalentType.MAGE_INTELLECT)

		# Aplicar efectos de talentos tanque
		multipliers["damage_reduction"] += self.get_talent_effect(TalentType.TANK_IRON_SKIN)
		multipliers["max_health_bonus"] += self.get_talent_effect(TalentType.TANK_HEALTH_BOOST)
		multipliers["health_regeneration"] += self.get_talent_effect(TalentType.TANK_REGENERATION)

		return multipliers


# Función de utilidad para obtener el gestor de talentos
_talent_manager = None


def get_talent_manager() -> TalentManager:
	"""Obtiene la instancia global del gestor de talentos.

	Returns:
		Instancia del TalentManager
	"""
	global _talent_manager
	if _talent_manager is None:
		from core.game import get_game_state

		game_state = get_game_state()
		_talent_manager = TalentManager(game_state.resource_manager)
	return _talent_manager
