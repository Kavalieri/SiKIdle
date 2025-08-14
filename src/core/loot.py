"""
Sistema de Loot Aleatorio para SiKIdle

Este módulo implementa un sistema completo de loot con objetos aleatorios,
diferentes rarezas y efectos que enriquecen la experiencia de juego.
"""

import logging
import random
from dataclasses import dataclass
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class LootRarity(Enum):
	"""Niveles de rareza para objetos de loot"""

	COMMON = "common"
	RARE = "rare"
	EPIC = "epic"
	LEGENDARY = "legendary"


class LootType(Enum):
	"""Tipos de objetos de loot"""

	WEAPON = "weapon"
	ARTIFACT = "artifact"
	GEM = "gem"
	MATERIAL = "material"


@dataclass
class LootItem:
	"""
	Clase base para todos los objetos de loot

	Attributes:
	    id: Identificador único del objeto
	    name: Nombre descriptivo del objeto
	    loot_type: Tipo de objeto (arma, artefacto, etc.)
	    rarity: Nivel de rareza del objeto
	    stats: Diccionario con estadísticas del objeto
	    description: Descripción detallada del objeto
	    equipped: Si el objeto está equipado actualmente
	"""

	id: str
	name: str
	loot_type: LootType
	rarity: LootRarity
	stats: dict[str, float]
	description: str
	equipped: bool = False

	def get_display_name(self) -> str:
		"""Retorna el nombre con indicador de rareza"""
		rarity_colors = {
			LootRarity.COMMON: "🤍",
			LootRarity.RARE: "💚",
			LootRarity.EPIC: "💙",
			LootRarity.LEGENDARY: "🟣",
		}
		return f"{rarity_colors[self.rarity]} {self.name}"

	def get_stat_summary(self) -> str:
		"""Retorna un resumen de las estadísticas principales"""
		if not self.stats:
			return "Sin estadísticas"

		summary_parts: list[str] = []
		for stat_name, value in self.stats.items():
			if stat_name.endswith("_multiplier"):
				summary_parts.append(
					f"+{(value - 1) * 100:.1f}% {stat_name.replace('_multiplier', '').title()}"
				)
			elif stat_name.endswith("_chance"):
				summary_parts.append(
					f"+{value * 100:.1f}% {stat_name.replace('_chance', '').title()}"
				)
			elif stat_name.endswith("_bonus"):
				summary_parts.append(
					f"+{value * 100:.1f}% {stat_name.replace('_bonus', '').title()}"
				)
			elif stat_name.endswith("_income"):
				summary_parts.append(
					f"+{(value - 1) * 100:.1f}% {stat_name.replace('_income', '').title()}"
				)
			elif stat_name == "quantity":
				summary_parts.append(f"Cantidad: {int(value)}")
			else:
				summary_parts.append(f"{stat_name.title()}: {value:.1f}")

		return " | ".join(summary_parts)


class WeaponItem(LootItem):
	"""Armas que mejoran las capacidades de clic del jugador"""

	def __init__(self, name: str, rarity: LootRarity, stats: dict[str, float]):
		description = self._generate_description(stats)
		super().__init__(
			id=f"weapon_{random.randint(100000, 999999)}",
			name=name,
			loot_type=LootType.WEAPON,
			rarity=rarity,
			stats=stats,
			description=description,
		)

	def _generate_description(self, stats: dict[str, float]) -> str:
		"""Genera una descripción basada en las estadísticas"""
		desc_parts = ["Un arma que potencia tus habilidades de combate."]

		if "click_multiplier" in stats:
			bonus = (stats["click_multiplier"] - 1) * 100
			desc_parts.append(f"Incrementa el daño por clic en {bonus:.1f}%.")

		if "crit_chance" in stats:
			chance = stats["crit_chance"] * 100
			desc_parts.append(f"Aumenta la probabilidad crítica en {chance:.1f}%.")

		if "crit_multiplier" in stats:
			bonus = (stats["crit_multiplier"] - 1) * 100
			desc_parts.append(f"Potencia el daño crítico en {bonus:.1f}%.")

		return " ".join(desc_parts)


class ArtifactItem(LootItem):
	"""Artefactos que otorgan bonificaciones pasivas permanentes"""

	def __init__(self, name: str, rarity: LootRarity, stats: dict[str, float]):
		description = self._generate_description(stats)
		super().__init__(
			id=f"artifact_{random.randint(100000, 999999)}",
			name=name,
			loot_type=LootType.ARTIFACT,
			rarity=rarity,
			stats=stats,
			description=description,
		)

	def _generate_description(self, stats: dict[str, float]) -> str:
		"""Genera una descripción basada en las estadísticas"""
		desc_parts = ["Un artefacto místico con poder permanente."]

		if "building_income" in stats:
			bonus = (stats["building_income"] - 1) * 100
			desc_parts.append(f"Aumenta los ingresos de edificios en {bonus:.1f}%.")

		if "global_income" in stats:
			bonus = (stats["global_income"] - 1) * 100
			desc_parts.append(f"Incrementa todos los ingresos en {bonus:.1f}%.")

		if "experience_bonus" in stats:
			bonus = (stats["experience_bonus"] - 1) * 100
			desc_parts.append(f"Otorga {bonus:.1f}% más experiencia.")

		return " ".join(desc_parts)


class GemItem(LootItem):
	"""Gemas consumibles que otorgan efectos temporales potentes"""

	def __init__(self, name: str, rarity: LootRarity, stats: dict[str, float]):
		description = self._generate_description(stats)
		super().__init__(
			id=f"gem_{random.randint(100000, 999999)}",
			name=name,
			loot_type=LootType.GEM,
			rarity=rarity,
			stats=stats,
			description=description,
		)

	def _generate_description(self, stats: dict[str, float]) -> str:
		"""Genera una descripción basada en las estadísticas"""
		desc_parts = ["Una gema mágica de uso único."]

		if "temporary_multiplier" in stats:
			multiplier = stats["temporary_multiplier"]
			desc_parts.append(f"Otorga un multiplicador x{multiplier:.1f} temporal.")

		if "duration" in stats:
			duration = int(stats["duration"])
			desc_parts.append(f"Duración: {duration} segundos.")

		if "cooldown" in stats:
			cooldown = int(stats["cooldown"] / 60)
			desc_parts.append(f"Recarga: {cooldown} minutos.")

		return " ".join(desc_parts)


class MaterialItem(LootItem):
	"""Materiales para crafteo futuro"""

	def __init__(self, name: str, rarity: LootRarity, quantity: int = 1):
		super().__init__(
			id=f"material_{name.lower().replace(' ', '_')}",
			name=name,
			loot_type=LootType.MATERIAL,
			rarity=rarity,
			stats={"quantity": quantity},
			description=f"Material para crafteo. Cantidad: {quantity}",
		)


class LootGenerator:
	"""
	Generador principal de loot aleatorio

	Maneja la creación de objetos con probabilidades configurables
	y estadísticas aleatorias dentro de rangos por rareza.
	"""

	# Probabilidades de rareza (suma debe ser 100)
	RARITY_WEIGHTS = {
		LootRarity.COMMON: 70,
		LootRarity.RARE: 20,
		LootRarity.EPIC: 8,
		LootRarity.LEGENDARY: 2,
	}

	# Multiplicadores de stats por rareza
	RARITY_MULTIPLIERS = {
		LootRarity.COMMON: {"min": 1.05, "max": 1.20},
		LootRarity.RARE: {"min": 1.20, "max": 1.50},
		LootRarity.EPIC: {"min": 1.50, "max": 2.00},
		LootRarity.LEGENDARY: {"min": 2.00, "max": 3.00},
	}

	# Nombres temáticos por tipo y rareza
	WEAPON_NAMES = {
		LootRarity.COMMON: ["Pico Oxidado", "Martillo Viejo", "Cuchillo Mellado", "Palo de Madera"],
		LootRarity.RARE: [
			"Espada Afilada",
			"Hacha de Guerra",
			"Martillo de Acero",
			"Lanza Forjada",
		],
		LootRarity.EPIC: ["Lanza del Dragón", "Martillo Divino", "Espada Flamígera", "Arco Élfico"],
		LootRarity.LEGENDARY: ["Excalibur", "Mjölnir", "Durandal", "Gungnir"],
	}

	ARTIFACT_NAMES = {
		LootRarity.COMMON: [
			"Amuleto Simple",
			"Anillo de Cobre",
			"Talismán Básico",
			"Brazalete Tosco",
		],
		LootRarity.RARE: [
			"Talismán Mágico",
			"Collar de Plata",
			"Anillo Encantado",
			"Diadema Noble",
		],
		LootRarity.EPIC: ["Orbe del Poder", "Corona de Oro", "Cetro Real", "Medallón Arcano"],
		LootRarity.LEGENDARY: [
			"Anillo del Infinito",
			"Corazón del Dragón",
			"Ojo de Sauron",
			"Grial Sagrado",
		],
	}

	GEM_NAMES = {
		LootRarity.COMMON: ["Cuarzo", "Topacio", "Ágata", "Jaspe"],
		LootRarity.RARE: ["Amatista", "Esmeralda", "Turquesa", "Granate"],
		LootRarity.EPIC: ["Rubí", "Zafiro", "Diamante", "Ópalo Negro"],
		LootRarity.LEGENDARY: [
			"Diamante Negro",
			"Cristal Cósmico",
			"Gema del Tiempo",
			"Piedra del Infinito",
		],
	}

	MATERIAL_NAMES = {
		LootRarity.COMMON: ["Hierro", "Madera", "Piedra", "Cuero"],
		LootRarity.RARE: ["Plata", "Cristal", "Esencia", "Seda"],
		LootRarity.EPIC: ["Oro", "Mithril", "Esencia Arcana", "Escama de Dragón"],
		LootRarity.LEGENDARY: [
			"Adamantium",
			"Esencia Divina",
			"Polvo de Estrella",
			"Fragmento Cósmico",
		],
	}

	def __init__(self):
		"""Inicializa el generador de loot"""
		logger.info("Generador de loot inicializado")

	def generate_random_rarity(self) -> LootRarity:
		"""Genera una rareza aleatoria basada en las probabilidades configuradas"""
		rand = random.randint(1, 100)
		cumulative = 0

		for rarity, weight in self.RARITY_WEIGHTS.items():
			cumulative += weight
			if rand <= cumulative:
				return rarity

		return LootRarity.COMMON

	def generate_stat_value(self, rarity: LootRarity, base_value: float = 1.0) -> float:
		"""Genera un valor de estadística aleatorio dentro del rango de la rareza"""
		multiplier_range = self.RARITY_MULTIPLIERS[rarity]
		multiplier = random.uniform(multiplier_range["min"], multiplier_range["max"])
		return base_value * multiplier

	def generate_weapon(self, rarity: LootRarity | None = None) -> WeaponItem:
		"""Genera un arma aleatoria"""
		if rarity is None:
			rarity = self.generate_random_rarity()

		# Seleccionar nombre aleatorio
		name = random.choice(self.WEAPON_NAMES[rarity])

		# Generar estadísticas aleatorias
		stats: dict[str, float] = {}

		# Todas las armas tienen multiplicador de clic
		stats["click_multiplier"] = self.generate_stat_value(rarity, 1.0)

		# Probabilidad de tener estadísticas adicionales
		if random.random() < 0.7:  # 70% chance
			stats["crit_chance"] = self.generate_stat_value(rarity, 0.01)  # Base 1%

		if random.random() < 0.5:  # 50% chance
			stats["crit_multiplier"] = self.generate_stat_value(rarity, 1.0)

		weapon = WeaponItem(name, rarity, stats)
		logger.debug("Arma generada: %s", weapon.get_display_name())
		return weapon

	def generate_artifact(self, rarity: LootRarity | None = None) -> ArtifactItem:
		"""Genera un artefacto aleatorio"""
		if rarity is None:
			rarity = self.generate_random_rarity()

		# Seleccionar nombre aleatorio
		name = random.choice(self.ARTIFACT_NAMES[rarity])

		# Generar estadísticas aleatorias
		stats: dict[str, float] = {}

		# Probabilidad de diferentes tipos de bonificaciones
		stat_chances = [
			("building_income", 0.6, 1.0),
			("global_income", 0.4, 1.0),
			("experience_bonus", 0.3, 1.0),
		]

		for stat_name, chance, base_value in stat_chances:
			if random.random() < chance:
				stats[stat_name] = self.generate_stat_value(rarity, base_value)

		# Garantizar al menos una estadística
		if not stats:
			stats["building_income"] = self.generate_stat_value(rarity, 1.0)

		artifact = ArtifactItem(name, rarity, stats)
		logger.debug("Artefacto generado: %s", artifact.get_display_name())
		return artifact

	def generate_gem(self, rarity: LootRarity | None = None) -> GemItem:
		"""Genera una gema aleatoria"""
		if rarity is None:
			rarity = self.generate_random_rarity()

		# Seleccionar nombre aleatorio
		name = random.choice(self.GEM_NAMES[rarity])

		# Generar estadísticas basadas en rareza
		base_multipliers = {
			LootRarity.COMMON: 1.5,
			LootRarity.RARE: 2.0,
			LootRarity.EPIC: 3.0,
			LootRarity.LEGENDARY: 5.0,
		}

		base_durations = {
			LootRarity.COMMON: 30,  # 30 segundos
			LootRarity.RARE: 60,  # 1 minuto
			LootRarity.EPIC: 120,  # 2 minutos
			LootRarity.LEGENDARY: 300,  # 5 minutos
		}

		base_cooldowns = {
			LootRarity.COMMON: 300,  # 5 minutos
			LootRarity.RARE: 600,  # 10 minutos
			LootRarity.EPIC: 900,  # 15 minutos
			LootRarity.LEGENDARY: 1800,  # 30 minutos
		}

		stats: dict[str, float] = {
			"temporary_multiplier": base_multipliers[rarity] * random.uniform(0.8, 1.2),
			"duration": base_durations[rarity] * random.uniform(0.8, 1.2),
			"cooldown": base_cooldowns[rarity] * random.uniform(0.8, 1.2),
		}

		gem = GemItem(name, rarity, stats)
		logger.debug("Gema generada: %s", gem.get_display_name())
		return gem

	def generate_material(self, rarity: LootRarity | None = None) -> MaterialItem:
		"""Genera un material aleatorio"""
		if rarity is None:
			rarity = self.generate_random_rarity()

		# Seleccionar nombre aleatorio
		name = random.choice(self.MATERIAL_NAMES[rarity])

		# Cantidad basada en rareza (más raro = menos cantidad pero más valioso)
		base_quantities = {
			LootRarity.COMMON: 5,
			LootRarity.RARE: 3,
			LootRarity.EPIC: 2,
			LootRarity.LEGENDARY: 1,
		}

		quantity = random.randint(1, base_quantities[rarity])

		material = MaterialItem(name, rarity, quantity)
		logger.debug("Material generado: %s", material.get_display_name())
		return material

	def drop_loot_from_enemy(
		self,
		enemy_type: str,
		enemy_level: int,
		player_level: int,
		is_boss: bool = False,
		biome_bonus: float = 1.0,
	) -> list[LootItem]:
		"""
		Genera loot específico basado en el enemigo derrotado

		Args:
		    enemy_type: Tipo/nombre del enemigo derrotado
		    enemy_level: Nivel del enemigo
		    player_level: Nivel del jugador
		    is_boss: Si el enemigo era un boss
		    biome_bonus: Multiplicador de loot por bioma activo

		Returns:
		    Lista de objetos generados (puede estar vacía)
		"""
		logger.info(
			"=== LOOT GENERATION === Enemigo: %s (lvl %d), Jugador: lvl %d, Boss: %s",
			enemy_type,
			enemy_level,
			player_level,
			is_boss,
		)

		dropped_items: list[LootItem] = []

		# Probabilidad base de drop
		base_drop_chance = 0.3  # 30% base
		if is_boss:
			base_drop_chance = 1.0  # Bosses siempre dropean algo

		# Ajustar probabilidad por diferencia de nivel
		level_diff = enemy_level - player_level
		level_modifier = 1.0 + (level_diff * 0.1)  # +10% por cada nivel de diferencia
		level_modifier = max(0.1, min(3.0, level_modifier))  # Entre 10% y 300%

		# Aplicar bonificación de bioma
		final_drop_chance = base_drop_chance * level_modifier * biome_bonus
		final_drop_chance = min(1.0, final_drop_chance)  # Máximo 100%

		logger.info(
			"Drop chance: %.2f (base: %.2f, level_mod: %.2f, biome: %.2f)",
			final_drop_chance,
			base_drop_chance,
			level_modifier,
			biome_bonus,
		)

		# Determinar cantidad de ítems
		num_drops = 1
		if is_boss:
			num_drops = random.randint(2, 4)  # Bosses dropean 2-4 ítems
		elif random.random() < 0.2:  # 20% chance de drop múltiple
			num_drops = 2

		# Generar ítems
		for _ in range(num_drops):
			if random.random() < final_drop_chance:
				# Ajustar tabla de rareza para enemigos de alto nivel y bosses
				modified_weights = self.RARITY_WEIGHTS.copy()

				if is_boss or enemy_level > player_level + 10:
					# Bosses y enemigos muy superiores tienen mejor loot
					modified_weights[LootRarity.COMMON] = max(
						10, modified_weights[LootRarity.COMMON] - 20
					)
					modified_weights[LootRarity.RARE] += 15
					modified_weights[LootRarity.EPIC] += 10
					modified_weights[LootRarity.LEGENDARY] += 5

				# Seleccionar rareza con pesos modificados
				rarities = list(modified_weights.keys())
				weights = list(modified_weights.values())
				selected_rarity = random.choices(rarities, weights=weights)[0]

				# Seleccionar tipo basado en enemigo
				loot_type = self._get_enemy_preferred_loot_type(enemy_type)

				# Generar ítem según el tipo
				if loot_type == LootType.WEAPON:
					item = self.generate_weapon(selected_rarity)
				elif loot_type == LootType.ARTIFACT:
					item = self.generate_artifact(selected_rarity)
				elif loot_type == LootType.GEM:
					item = self.generate_gem(selected_rarity)
				else:  # MATERIAL
					item = self.generate_material(selected_rarity)

				# Escalar estadísticas por nivel del enemigo
				item = self._scale_item_by_level(item, enemy_level)
				dropped_items.append(item)

		if dropped_items:
			logger.info(
				"Loot dropeado por %s (nivel %d): %d ítems",
				enemy_type,
				enemy_level,
				len(dropped_items),
			)

		return dropped_items

	def _get_enemy_preferred_loot_type(self, enemy_type: str) -> LootType:
		"""
		Determina el tipo de loot preferido basado en el tipo de enemigo

		Args:
		    enemy_type: Nombre/tipo del enemigo

		Returns:
		    Tipo de loot con mayor probabilidad para este enemigo
		"""
		enemy_lower = enemy_type.lower()

		# Mapeo de enemigos a tipos de loot preferidos
		if any(keyword in enemy_lower for keyword in ["goblin", "bandit", "thief"]):
			# Enemigos ágiles prefieren armas
			return random.choice([LootType.WEAPON, LootType.GEM])
		elif any(keyword in enemy_lower for keyword in ["orc", "warrior", "knight"]):
			# Guerreros prefieren armas y artefactos
			return random.choice([LootType.WEAPON, LootType.ARTIFACT])
		elif any(keyword in enemy_lower for keyword in ["skeleton", "undead", "lich"]):
			# No-muertos prefieren artefactos mágicos
			return random.choice([LootType.ARTIFACT, LootType.GEM])
		elif any(keyword in enemy_lower for keyword in ["dragon", "boss", "lord", "king"]):
			# Bosses pueden dropear cualquier cosa
			return random.choice(list(LootType))
		elif any(keyword in enemy_lower for keyword in ["spider", "rat", "bat"]):
			# Criaturas menores prefieren materiales
			return random.choice([LootType.MATERIAL, LootType.GEM])
		else:
			# Default: distribución balanceada
			return random.choice(list(LootType))

	def _scale_item_by_level(self, item: LootItem, enemy_level: int) -> LootItem:
		"""
		Escala las estadísticas de un ítem según el nivel del enemigo

		Args:
		    item: Ítem a escalar
		    enemy_level: Nivel del enemigo que dropea el ítem

		Returns:
		    Ítem con estadísticas escaladas
		"""
		level_multiplier = 1.0 + (enemy_level * 0.05)  # +5% por nivel

		scaled_stats: dict[str, float] = {}
		for stat_name, base_value in item.stats.items():
			if stat_name.endswith("_multiplier") or stat_name.endswith("_income"):
				# Para multiplicadores, el escalado es más conservador
				bonus = (base_value - 1.0) * level_multiplier * 0.5  # 50% del escalado normal
				scaled_stats[stat_name] = 1.0 + bonus
			elif stat_name.endswith("_chance") or stat_name.endswith("_bonus"):
				# Para probabilidades y bonuses, escalado directo pero limitado
				scaled_stats[stat_name] = min(1.0, base_value * level_multiplier * 0.7)
			elif stat_name in ["quantity"]:
				# Para cantidad, escalado entero
				scaled_stats[stat_name] = max(1, int(base_value * level_multiplier))
			else:
				# Para stats planos como multiplicadores temporales, duración, etc.
				scaled_stats[stat_name] = base_value * level_multiplier

		# Crear una copia del ítem con las nuevas estadísticas
		scaled_item = LootItem(
			id=item.id,
			name=item.name,
			loot_type=item.loot_type,
			rarity=item.rarity,
			stats=scaled_stats,
			description=item.description,
			equipped=item.equipped,
		)

		return scaled_item

	def generate_random_loot(self) -> LootItem:
		"""Genera un objeto de loot completamente aleatorio"""
		# Probabilidades de tipo de objeto
		type_weights = {
			LootType.WEAPON: 25,
			LootType.ARTIFACT: 25,
			LootType.GEM: 30,
			LootType.MATERIAL: 20,
		}

		# Seleccionar tipo aleatorio
		rand = random.randint(1, 100)
		cumulative = 0
		selected_type = LootType.WEAPON

		for loot_type, weight in type_weights.items():
			cumulative += weight
			if rand <= cumulative:
				selected_type = loot_type
				break

		# Generar objeto del tipo seleccionado
		if selected_type == LootType.WEAPON:
			item = self.generate_weapon()
		elif selected_type == LootType.ARTIFACT:
			item = self.generate_artifact()
		elif selected_type == LootType.GEM:
			item = self.generate_gem()
		else:  # MATERIAL
			item = self.generate_material()

		logger.info("Loot generado: %s (%s)", item.get_display_name(), item.loot_type.value)
		return item


# Test function para verificar funcionamiento
def test_loot_system():
	"""Función de prueba para el sistema de loot"""
	generator = LootGenerator()

	print("=== Prueba Completa del Sistema de Loot ===\n")

	# Probar todos los tipos específicos
	print("1. ARMAS:")
	for _ in range(3):
		weapon = generator.generate_weapon()
		print(f"   {weapon.get_display_name()} - {weapon.get_stat_summary()}")

	print("\n2. ARTEFACTOS:")
	for _ in range(3):
		artifact = generator.generate_artifact()
		print(f"   {artifact.get_display_name()} - {artifact.get_stat_summary()}")

	print("\n3. GEMAS:")
	for _ in range(3):
		gem = generator.generate_gem()
		print(f"   {gem.get_display_name()} - {gem.get_stat_summary()}")

	print("\n4. MATERIALES:")
	for _ in range(3):
		material = generator.generate_material()
		print(f"   {material.get_display_name()} - {material.get_stat_summary()}")

	print("\n5. LOOT ALEATORIO COMPLETO:")
	for _ in range(8):
		item = generator.generate_random_loot()
		print(f"   {item.get_display_name()} ({item.loot_type.value}) - {item.get_stat_summary()}")

	# Estadísticas de rareza
	print("\n6. ESTADÍSTICAS DE RAREZA (100 objetos):")
	rarity_counts = dict.fromkeys(LootRarity, 0)

	for _ in range(100):
		item = generator.generate_random_loot()
		rarity_counts[item.rarity] += 1

	for rarity, count in rarity_counts.items():
		print(
			f"   {rarity.value.title()}: {count}% (esperado: {generator.RARITY_WEIGHTS[rarity]}%)"
		)


if __name__ == "__main__":
	test_loot_system()
