"""
Gestor de Equipamiento para SiKIdle
Maneja el inventario, equipamiento activo y aplicación de bonificaciones
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import logging

from .equipment import Equipment, EquipmentType, EquipmentStats, EquipmentGenerator

logger = logging.getLogger(__name__)


@dataclass
class PlayerStats:
	"""Estadísticas totales del jugador incluyendo equipamiento."""

	base_attack: float = 10.0
	base_defense: float = 5.0
	base_health: float = 100.0

	# Bonificaciones del equipamiento
	equipment_attack: float = 0.0
	equipment_defense: float = 0.0
	equipment_health: float = 0.0
	equipment_critical_chance: float = 0.0
	equipment_critical_damage: float = 0.0
	equipment_production_bonus: float = 0.0

	def get_total_attack(self) -> float:
		"""Obtiene el ataque total."""
		return self.base_attack + self.equipment_attack

	def get_total_defense(self) -> float:
		"""Obtiene la defensa total."""
		return self.base_defense + self.equipment_defense

	def get_total_health(self) -> float:
		"""Obtiene la vida total."""
		return self.base_health + self.equipment_health

	def get_total_critical_chance(self) -> float:
		"""Obtiene la probabilidad de crítico total."""
		return min(0.95, self.equipment_critical_chance)  # Cap del 95%

	def get_total_critical_damage(self) -> float:
		"""Obtiene el daño crítico total."""
		return 1.5 + self.equipment_critical_damage  # Base 150%

	def get_total_production_bonus(self) -> float:
		"""Obtiene el bonus de producción total."""
		return self.equipment_production_bonus


class EquipmentManager:
	"""Gestor principal del sistema de equipamiento."""

	def __init__(self):
		self.equipped_items: Dict[EquipmentType, Optional[Equipment]] = {
			EquipmentType.WEAPON: None,
			EquipmentType.ARMOR: None,
			EquipmentType.JEWELRY: None,
		}
		self.inventory: List[Equipment] = []
		self.player_stats = PlayerStats()
		self.generator = EquipmentGenerator()

		# Límites de inventario
		self.max_inventory_size = 50

		# CRITICO: Referencia al PlayerStatsManager del combat system
		self.combat_stats_manager = None

	def set_player_stats_manager(self, stats_manager):
		"""
		CRITICO: Conecta el EquipmentManager con el PlayerStatsManager del combat system.
		Esto permite que los stats del equipo afecten realmente el combate.
		"""
		self.combat_stats_manager = stats_manager
		# Actualizar stats inmediatamente si ya tenemos equipment equipado
		self._update_combat_stats()
		logger.info("EquipmentManager conectado con PlayerStatsManager - Equipment effects activados para combate")

	def equip_item(self, item: Equipment) -> Optional[Equipment]:
		"""
		Equipa un ítem del inventario.

		Args:
			item: El equipamiento a equipar

		Returns:
			El ítem previamente equipado si existía, None si no
		"""
		if item not in self.inventory:
			logger.warning(f"Attempting to equip item {item.name} not in inventory")
			return None

		equipment_type = item.equipment_type
		previously_equipped = self.equipped_items[equipment_type]

		# Equipar el nuevo ítem
		self.equipped_items[equipment_type] = item

		# Quitar del inventario
		self.inventory.remove(item)

		# Si había algo equipado antes, moverlo al inventario
		if previously_equipped is not None:
			if len(self.inventory) < self.max_inventory_size:
				self.inventory.append(previously_equipped)
			else:
				logger.warning(f"Inventory full! Discarding {previously_equipped.name}")

		# Recalcular estadísticas
		self._recalculate_stats()

		logger.info(f"Equipped {item.get_display_name()}")
		if previously_equipped:
			logger.info(f"Unequipped {previously_equipped.get_display_name()}")

		return previously_equipped

	def unequip_item(self, equipment_type: EquipmentType) -> bool:
		"""
		Desequipa un ítem y lo mueve al inventario.

		Args:
			equipment_type: Tipo de equipamiento a desequipar

		Returns:
			True si se desequipó exitosamente, False si no había nada equipado
		"""
		equipped_item = self.equipped_items.get(equipment_type)

		if equipped_item is None:
			return False

		if len(self.inventory) >= self.max_inventory_size:
			logger.warning("Cannot unequip item: inventory is full")
			return False

		# Mover al inventario
		self.inventory.append(equipped_item)
		self.equipped_items[equipment_type] = None

		# Recalcular estadísticas
		self._recalculate_stats()

		logger.info(f"Unequipped {equipped_item.get_display_name()}")
		return True

	def add_to_inventory(self, item: Equipment) -> bool:
		"""
		Añade un ítem al inventario.

		Args:
			item: El equipamiento a añadir

		Returns:
			True si se añadió exitosamente, False si el inventario está lleno
		"""
		if len(self.inventory) >= self.max_inventory_size:
			logger.warning(f"Inventory full! Cannot add {item.name}")
			return False

		self.inventory.append(item)
		logger.info(f"Added {item.get_display_name()} to inventory")
		return True

	def remove_from_inventory(self, item: Equipment) -> bool:
		"""
		Elimina un ítem del inventario.

		Args:
			item: El equipamiento a eliminar

		Returns:
			True si se eliminó exitosamente, False si no estaba en el inventario
		"""
		if item in self.inventory:
			self.inventory.remove(item)
			logger.info(f"Removed {item.get_display_name()} from inventory")
			return True
		return False

	def auto_equip_if_better(self, item: Equipment) -> bool:
		"""
		Equipa automáticamente un ítem si es mejor que el actual.

		Args:
			item: El equipamiento a evaluar

		Returns:
			True si se equipó automáticamente, False si no
		"""
		current_item = self.equipped_items.get(item.equipment_type)

		if item.is_better_than(current_item):
			# Si hay espacio en inventario o nada equipado
			if current_item is None or len(self.inventory) < self.max_inventory_size:
				self.equip_item(item)
				logger.info(f"Auto-equipped {item.get_display_name()} (better than current)")
				return True

		return False

	def suggest_upgrades(self) -> List[Tuple[Equipment, str]]:
		"""
		Sugiere upgrades disponibles en el inventario.

		Returns:
			Lista de tuplas (equipamiento, razón) con posibles mejoras
		"""
		suggestions = []

		for item in self.inventory:
			current_item = self.equipped_items.get(item.equipment_type)

			if item.is_better_than(current_item):
				if current_item is None:
					reason = "No tienes nada equipado en este slot"
				else:
					power_diff = item.stats.get_total_power() - current_item.stats.get_total_power()
					reason = f"+{power_diff:.0f} poder total vs equipamiento actual"

				suggestions.append((item, reason))

		# Ordenar por mejora de poder descendente
		suggestions.sort(key=lambda x: x[0].stats.get_total_power(), reverse=True)

		return suggestions

	def get_inventory_value(self) -> float:
		"""Obtiene el valor total del inventario en poder."""
		return sum(item.stats.get_total_power() for item in self.inventory)

	def get_equipped_value(self) -> float:
		"""Obtiene el valor total del equipamiento actual en poder."""
		total = 0
		for item in self.equipped_items.values():
			if item is not None:
				total += item.stats.get_total_power()
		return total

	def _recalculate_stats(self):
		"""Recalcula las estadísticas del jugador basándose en el equipamiento."""
		# Resetear bonificaciones del equipamiento
		self.player_stats.equipment_attack = 0.0
		self.player_stats.equipment_defense = 0.0
		self.player_stats.equipment_health = 0.0
		self.player_stats.equipment_critical_chance = 0.0
		self.player_stats.equipment_critical_damage = 0.0
		self.player_stats.equipment_production_bonus = 0.0

		# Sumar bonificaciones de todos los ítems equipados
		for item in self.equipped_items.values():
			if item is not None:
				self.player_stats.equipment_attack += item.stats.attack
				self.player_stats.equipment_defense += item.stats.defense
				self.player_stats.equipment_health += item.stats.health
				self.player_stats.equipment_critical_chance += item.stats.critical_chance
				self.player_stats.equipment_critical_damage += item.stats.critical_damage
				self.player_stats.equipment_production_bonus += item.stats.production_bonus

		logger.debug(
			f"Stats recalculated - Attack: {self.player_stats.get_total_attack():.1f}, "
			f"Defense: {self.player_stats.get_total_defense():.1f}, "
			f"Health: {self.player_stats.get_total_health():.1f}"
		)

		# CRITICO: Actualizar el PlayerStatsManager del combat system
		self._update_combat_stats()

	def _update_combat_stats(self):
		"""
		CRITICO: Actualiza el PlayerStatsManager del combat system con los stats del equipment.
		Esto es lo que hace que el equipment realmente afecte el combate.
		"""
		if self.combat_stats_manager is None:
			return

		# Crear el diccionario de bonificaciones para el combat system
		equipment_bonuses = {
			'damage_mult': 1.0 + (self.player_stats.equipment_attack / 100.0),  # Ataque como multiplicador
			'click_mult': 1.0 + (self.player_stats.equipment_attack / 200.0),  # Click damage basado en ataque
			'critical_chance': self.player_stats.equipment_critical_chance,
			'critical_damage': self.player_stats.equipment_critical_damage,
			'defense': self.player_stats.equipment_defense,
			'health': self.player_stats.equipment_health,
			'production_bonus': self.player_stats.equipment_production_bonus
		}

		# Llamar al método del PlayerStatsManager para aplicar las bonificaciones
		self.combat_stats_manager.update_equipment_bonuses(equipment_bonuses)

		logger.info(f"EQUIPMENT EFFECTS: Combat stats updated with bonuses: {equipment_bonuses}")

	def get_equipment_summary(self) -> Dict:
		"""Obtiene un resumen del estado del equipamiento."""
		equipped_count = sum(1 for item in self.equipped_items.values() if item is not None)

		return {
			"equipped_items": equipped_count,
			"total_slots": len(self.equipped_items),
			"inventory_items": len(self.inventory),
			"max_inventory": self.max_inventory_size,
			"total_attack": self.player_stats.get_total_attack(),
			"total_defense": self.player_stats.get_total_defense(),
			"total_health": self.player_stats.get_total_health(),
			"critical_chance": self.player_stats.get_total_critical_chance() * 100,
			"critical_damage": self.player_stats.get_total_critical_damage() * 100,
			"production_bonus": self.player_stats.get_total_production_bonus() * 100,
			"equipped_value": self.get_equipped_value(),
			"inventory_value": self.get_inventory_value(),
		}

	def generate_loot(self, dungeon_level: int, is_boss: bool = False) -> List[Equipment]:
		"""
		Genera loot para el jugador.

		Args:
			dungeon_level: Nivel de la mazmorra/área
			is_boss: Si es loot de boss (mejor calidad)

		Returns:
			Lista de equipamiento generado
		"""
		if is_boss:
			return self.generator.generate_boss_loot(dungeon_level)
		else:
			# Loot normal - 30% de probabilidad
			if (
				self.generator._determine_rarity(1) != self.generator.base_drop_rates
			):  # Simulación rápida
				item = self.generator.generate_equipment(dungeon_level)
				return [item]
			return []

	def sort_inventory(self, sort_by: str = "power"):
		"""
		Ordena el inventario según el criterio especificado.

		Args:
			sort_by: Criterio de ordenación ("power", "rarity", "level", "type")
		"""
		if sort_by == "power":
			self.inventory.sort(key=lambda x: x.stats.get_total_power(), reverse=True)
		elif sort_by == "rarity":
			rarity_order = {"legendary": 4, "epic": 3, "rare": 2, "common": 1}
			self.inventory.sort(key=lambda x: rarity_order.get(x.rarity.value, 0), reverse=True)
		elif sort_by == "level":
			self.inventory.sort(key=lambda x: x.level, reverse=True)
		elif sort_by == "type":
			type_order = {"weapon": 1, "armor": 2, "jewelry": 3}
			self.inventory.sort(key=lambda x: type_order.get(x.equipment_type.value, 0))

		logger.debug(f"Inventory sorted by {sort_by}")

	def get_stat_breakdown(self) -> Dict:
		"""Obtiene un desglose detallado de las estadísticas por ítem."""
		breakdown = {
			"base_stats": {
				"attack": self.player_stats.base_attack,
				"defense": self.player_stats.base_defense,
				"health": self.player_stats.base_health,
			},
			"equipment_contributions": {},
		}

		for eq_type, item in self.equipped_items.items():
			if item is not None:
				breakdown["equipment_contributions"][eq_type.value] = {
					"name": item.name,
					"attack": item.stats.attack,
					"defense": item.stats.defense,
					"health": item.stats.health,
					"critical_chance": item.stats.critical_chance * 100,
					"critical_damage": item.stats.critical_damage * 100,
					"production_bonus": item.stats.production_bonus * 100,
				}

		return breakdown
