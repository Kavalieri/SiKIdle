"""
Sistema de Equipamiento para SiKIdle
Maneja armas, armaduras y joyas con generación procedural y stats escalables
"""

from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Optional, Any
import random
import logging

logger = logging.getLogger(__name__)


class EquipmentType(Enum):
	"""Tipos de equipamiento disponibles."""

	WEAPON = "weapon"
	ARMOR = "armor"
	JEWELRY = "jewelry"


class Rarity(Enum):
	"""Niveles de rareza del equipamiento."""

	COMMON = "common"
	RARE = "rare"
	EPIC = "epic"
	LEGENDARY = "legendary"


@dataclass
class EquipmentStats:
	"""Estadísticas base del equipamiento."""

	attack: float = 0.0
	defense: float = 0.0
	health: float = 0.0
	critical_chance: float = 0.0
	critical_damage: float = 0.0
	production_bonus: float = 0.0  # Bonus para producción idle

	def get_total_power(self) -> float:
		"""Calcula el poder total del equipamiento."""
		return (
			self.attack * 2
			+ self.defense
			+ self.health * 0.5
			+ self.critical_chance * 50
			+ self.critical_damage * 10
			+ self.production_bonus * 30
		)


@dataclass
class EquipmentEffect:
	"""Efecto especial del equipamiento."""

	name: str
	description: str
	value: float
	effect_type: str  # "percentage", "flat", "special"


class Equipment:
	"""Clase base para todo el equipamiento."""

	def __init__(
		self, equipment_type: EquipmentType, level: int = 1, rarity: Rarity = Rarity.COMMON
	):
		self.equipment_type = equipment_type
		self.level = level
		self.rarity = rarity
		self.stats = EquipmentStats()
		self.effects: List[EquipmentEffect] = []
		self.name = ""
		self.description = ""
		self.item_id = self._generate_id()

		# Generar equipamiento
		self._generate_base_stats()
		self._generate_name()
		self._generate_effects()

	def _generate_id(self) -> str:
		"""Genera un ID único para el ítem."""
		import time

		return f"{self.equipment_type.value}_{int(time.time() * 1000)}{random.randint(100, 999)}"

	def _generate_base_stats(self):
		"""Genera las estadísticas base según tipo y rareza."""
		base_multiplier = self._get_rarity_multiplier()
		level_multiplier = 1 + (self.level - 1) * 0.15  # +15% por nivel

		if self.equipment_type == EquipmentType.WEAPON:
			self.stats.attack = (10 + random.uniform(5, 15)) * base_multiplier * level_multiplier
			self.stats.critical_chance = random.uniform(0.05, 0.15) * base_multiplier
			self.stats.critical_damage = random.uniform(0.2, 0.5) * base_multiplier

		elif self.equipment_type == EquipmentType.ARMOR:
			self.stats.defense = (8 + random.uniform(4, 12)) * base_multiplier * level_multiplier
			self.stats.health = (50 + random.uniform(20, 80)) * base_multiplier * level_multiplier

		elif self.equipment_type == EquipmentType.JEWELRY:
			# Joyas dan efectos más variados
			stat_choice = random.choice(["attack", "defense", "critical", "production"])
			if stat_choice == "attack":
				self.stats.attack = (5 + random.uniform(2, 8)) * base_multiplier * level_multiplier
			elif stat_choice == "defense":
				self.stats.defense = (4 + random.uniform(2, 6)) * base_multiplier * level_multiplier
			elif stat_choice == "critical":
				self.stats.critical_chance = random.uniform(0.03, 0.10) * base_multiplier
				self.stats.critical_damage = random.uniform(0.1, 0.3) * base_multiplier
			else:  # production
				self.stats.production_bonus = random.uniform(0.05, 0.20) * base_multiplier

	def _get_rarity_multiplier(self) -> float:
		"""Obtiene el multiplicador según la rareza."""
		multipliers = {
			Rarity.COMMON: 1.0,
			Rarity.RARE: 1.5,
			Rarity.EPIC: 2.2,
			Rarity.LEGENDARY: 3.5,
		}
		return multipliers[self.rarity]

	def _generate_name(self):
		"""Genera un nombre procedural para el equipamiento."""
		prefixes = {
			Rarity.COMMON: ["Simple", "Básico", "Común"],
			Rarity.RARE: ["Refinado", "Superior", "Mejorado"],
			Rarity.EPIC: ["Épico", "Poderoso", "Magistral"],
			Rarity.LEGENDARY: ["Legendario", "Divino", "Ancestral"],
		}

		suffixes = {
			EquipmentType.WEAPON: ["Espada", "Hacha", "Bastón", "Daga"],
			EquipmentType.ARMOR: ["Armadura", "Cota", "Túnica", "Casco"],
			EquipmentType.JEWELRY: ["Anillo", "Amuleto", "Collar", "Brazalete"],
		}

		materials = [
			"de Hierro",
			"de Acero",
			"de Mithril",
			"de Adamantium",
			"Encantado",
			"del Poder",
			"de la Velocidad",
			"de la Sabiduría",
		]

		prefix = random.choice(prefixes[self.rarity])
		suffix = random.choice(suffixes[self.equipment_type])
		material = random.choice(materials) if self.rarity != Rarity.COMMON else ""

		self.name = f"{prefix} {suffix} {material}".strip()

	def _generate_effects(self):
		"""Genera efectos especiales según la rareza."""
		if self.rarity == Rarity.COMMON:
			return  # Común no tiene efectos especiales

		effect_count = {
			Rarity.RARE: 1,
			Rarity.EPIC: random.randint(1, 2),
			Rarity.LEGENDARY: random.randint(2, 3),
		}

		possible_effects = [
			EquipmentEffect("Regeneración", "+{value}% regeneración de vida", 0.02, "percentage"),
			EquipmentEffect("Velocidad", "+{value}% velocidad de ataque", 0.15, "percentage"),
			EquipmentEffect("Fortuna", "+{value}% probabilidad de loot raro", 0.10, "percentage"),
			EquipmentEffect("Eficiencia", "+{value}% producción idle", 0.05, "percentage"),
			EquipmentEffect("Resistencia", "+{value} resistencia elemental", 10, "flat"),
		]

		num_effects = effect_count.get(self.rarity, 0)
		selected_effects = random.sample(possible_effects, min(num_effects, len(possible_effects)))

		for effect in selected_effects:
			# Escalar el valor del efecto con rareza y nivel
			rarity_mult = self._get_rarity_multiplier()
			level_mult = 1 + (self.level - 1) * 0.1
			scaled_value = effect.value * rarity_mult * level_mult

			new_effect = EquipmentEffect(
				effect.name,
				effect.description.format(value=f"{scaled_value:.1f}"),
				scaled_value,
				effect.effect_type,
			)
			self.effects.append(new_effect)

	def get_display_name(self) -> str:
		"""Obtiene el nombre para mostrar con color según rareza."""
		color_codes = {
			Rarity.COMMON: "⚪",
			Rarity.RARE: "🔵",
			Rarity.EPIC: "🟣",
			Rarity.LEGENDARY: "🟡",
		}
		return f"{color_codes[self.rarity]} {self.name}"

	def get_tooltip_text(self) -> str:
		"""Genera el texto del tooltip con todas las estadísticas."""
		lines = [self.get_display_name()]
		lines.append(f"Nivel: {self.level}")

		# Estadísticas principales
		if self.stats.attack > 0:
			lines.append(f"⚔️ Ataque: +{self.stats.attack:.1f}")
		if self.stats.defense > 0:
			lines.append(f"🛡️ Defensa: +{self.stats.defense:.1f}")
		if self.stats.health > 0:
			lines.append(f"❤️ Vida: +{self.stats.health:.0f}")
		if self.stats.critical_chance > 0:
			lines.append(f"🍀 Crítico: +{self.stats.critical_chance * 100:.1f}%")
		if self.stats.critical_damage > 0:
			lines.append(f"💥 Daño Crítico: +{self.stats.critical_damage * 100:.1f}%")
		if self.stats.production_bonus > 0:
			lines.append(f"📈 Producción: +{self.stats.production_bonus * 100:.1f}%")

		# Efectos especiales
		if self.effects:
			lines.append("")
			lines.append("Efectos especiales:")
			for effect in self.effects:
				lines.append(f"✨ {effect.description}")

		# Poder total
		lines.append("")
		lines.append(f"Poder Total: {self.stats.get_total_power():.0f}")

		return "\n".join(lines)

	def is_better_than(self, other: Optional["Equipment"]) -> bool:
		"""Compara si este equipamiento es mejor que otro."""
		if other is None:
			return True

		# Comparar poder total con ligero bias hacia mayor rareza
		rarity_weights = {
			Rarity.COMMON: 1.0,
			Rarity.RARE: 1.1,
			Rarity.EPIC: 1.2,
			Rarity.LEGENDARY: 1.3,
		}

		self_power = self.stats.get_total_power() * rarity_weights[self.rarity]
		other_power = other.stats.get_total_power() * rarity_weights[other.rarity]

		return self_power > other_power


class EquipmentGenerator:
	"""Generador de equipamiento procedural."""

	def __init__(self):
		self.base_drop_rates = {
			Rarity.COMMON: 0.70,
			Rarity.RARE: 0.25,
			Rarity.EPIC: 0.04,
			Rarity.LEGENDARY: 0.01,
		}

	def generate_equipment(
		self,
		dungeon_level: int,
		equipment_type: Optional[EquipmentType] = None,
		force_rarity: Optional[Rarity] = None,
	) -> Equipment:
		"""Genera un equipamiento aleatorio según el nivel de mazmorra."""

		# Determinar tipo si no se especifica
		if equipment_type is None:
			equipment_type = random.choice(list(EquipmentType))

		# Determinar rareza
		if force_rarity is None:
			rarity = self._determine_rarity(dungeon_level)
		else:
			rarity = force_rarity

		# Determinar nivel del ítem (cerca del nivel de mazmorra)
		item_level = max(1, dungeon_level + random.randint(-2, 2))

		equipment = Equipment(equipment_type, item_level, rarity)

		logger.debug(
			f"Generated {equipment.get_display_name()} (Level {item_level}) "
			f"for dungeon level {dungeon_level}"
		)

		return equipment

	def _determine_rarity(self, dungeon_level: int) -> Rarity:
		"""Determina la rareza basada en el nivel de mazmorra."""
		# Mejorar probabilidades con niveles altos
		level_bonus = min(dungeon_level * 0.002, 0.15)  # Hasta +15% para rareza alta

		adjusted_rates = {
			Rarity.COMMON: max(0.20, self.base_drop_rates[Rarity.COMMON] - level_bonus),
			Rarity.RARE: self.base_drop_rates[Rarity.RARE] + level_bonus * 0.6,
			Rarity.EPIC: self.base_drop_rates[Rarity.EPIC] + level_bonus * 0.3,
			Rarity.LEGENDARY: self.base_drop_rates[Rarity.LEGENDARY] + level_bonus * 0.1,
		}

		# Normalizar probabilidades
		total = sum(adjusted_rates.values())
		for rarity in adjusted_rates:
			adjusted_rates[rarity] /= total

		# Selección aleatoria ponderada
		rand = random.random()
		cumulative = 0

		for rarity, rate in adjusted_rates.items():
			cumulative += rate
			if rand <= cumulative:
				return rarity

		return Rarity.COMMON  # Fallback

	def generate_boss_loot(self, dungeon_level: int) -> List[Equipment]:
		"""Genera loot garantizado de boss con mejor calidad."""
		loot = []

		# Boss siempre dropea al menos 1 ítem raro o mejor
		min_rarity = Rarity.RARE if dungeon_level < 20 else Rarity.EPIC
		main_item = self.generate_equipment(
			dungeon_level + 2,  # Boss loot es 2 niveles superior
			force_rarity=min_rarity,
		)
		loot.append(main_item)

		# Probabilidad de loot adicional
		if random.random() < 0.4:  # 40% chance
			extra_item = self.generate_equipment(dungeon_level)
			loot.append(extra_item)

		# Bosses de nivel alto pueden dropear legendarios
		if dungeon_level >= 30 and random.random() < 0.05:  # 5% a partir del nivel 30
			legendary_item = self.generate_equipment(dungeon_level, force_rarity=Rarity.LEGENDARY)
			loot.append(legendary_item)

		return loot
