"""
Sistema de Inventario para SiKIdle

Este módulo gestiona la colección, organización y equipamiento de objetos de loot.
Proporciona una interfaz para que los jugadores administren su inventario de items.
"""

import logging
from typing import Optional
from dataclasses import dataclass

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.loot import LootItem, LootType

logger = logging.getLogger(__name__)


@dataclass
class InventorySlot:
	"""
	Representa un slot del inventario con un objeto y metadatos

	Attributes:
	    item: El objeto almacenado en este slot
	    slot_id: Identificador único del slot
	    equipped: Si el objeto está equipado actualmente
	    locked: Si el slot está bloqueado (expandible en futuro)
	"""

	item: Optional[LootItem]
	slot_id: int
	equipped: bool = False
	locked: bool = False

	def is_empty(self) -> bool:
		"""Retorna True si el slot está vacío"""
		return self.item is None

	def can_equip(self) -> bool:
		"""Retorna True si el objeto puede ser equipado"""
		return self.item is not None and not self.equipped


@dataclass
class Equipment:
	"""
	Gestiona los objetos equipados del jugador

	Los objetos equipados otorgan bonificaciones activas.
	Solo un objeto por tipo puede estar equipado simultáneamente.
	"""

	weapon: Optional[LootItem] = None
	artifact: Optional[LootItem] = None
	gem: Optional[LootItem] = None

	def equip_item(self, item: LootItem) -> bool:
		"""
		Equipa un objeto según su tipo

		Args:
		    item: El objeto a equipar

		Returns:
		    True si se equipó exitosamente, False si ya hay otro equipado
		"""
		if item.loot_type == LootType.WEAPON:
			if self.weapon is None:
				self.weapon = item
				item.equipped = True
				logger.info("Arma equipada: %s", item.get_display_name())
				return True
		elif item.loot_type == LootType.ARTIFACT:
			if self.artifact is None:
				self.artifact = item
				item.equipped = True
				logger.info("Artefacto equipado: %s", item.get_display_name())
				return True
		elif item.loot_type == LootType.GEM:
			if self.gem is None:
				self.gem = item
				item.equipped = True
				logger.info("Gema equipada: %s", item.get_display_name())
				return True

		logger.warning("No se pudo equipar %s: slot ocupado", item.get_display_name())
		return False

	def unequip_item(self, loot_type: LootType) -> Optional[LootItem]:
		"""
		Desequipa un objeto por tipo

		Args:
		    loot_type: Tipo de objeto a desequipar

		Returns:
		    El objeto desequipado o None si no había nada equipado
		"""
		item = None

		if loot_type == LootType.WEAPON and self.weapon:
			item = self.weapon
			self.weapon = None
		elif loot_type == LootType.ARTIFACT and self.artifact:
			item = self.artifact
			self.artifact = None
		elif loot_type == LootType.GEM and self.gem:
			item = self.gem
			self.gem = None

		if item:
			item.equipped = False
			logger.info("Objeto desequipado: %s", item.get_display_name())

		return item

	def get_equipped_items(self) -> list[LootItem]:
		"""Retorna una lista de todos los objetos equipados"""
		equipped = []
		if self.weapon:
			equipped.append(self.weapon)
		if self.artifact:
			equipped.append(self.artifact)
		if self.gem:
			equipped.append(self.gem)
		return equipped

	def get_total_stats(self) -> dict[str, float]:
		"""
		Calcula las estadísticas totales de todos los objetos equipados

		Returns:
		    Diccionario con las estadísticas acumuladas
		"""
		total_stats: dict[str, float] = {}

		for item in self.get_equipped_items():
			for stat_name, value in item.stats.items():
				if stat_name in total_stats:
					# Para multiplicadores, usar multiplicación compuesta
					if stat_name.endswith("_multiplier"):
						total_stats[stat_name] *= value
					else:
						total_stats[stat_name] += value
				else:
					total_stats[stat_name] = value

		return total_stats


class Inventory:
	"""
	Sistema de inventario principal

	Gestiona la colección de objetos, filtrado, búsqueda y organización.
	"""

	def __init__(self, max_slots: int = 50):
		"""
		Inicializa el inventario

		Args:
		    max_slots: Número máximo de slots disponibles
		"""
		self.max_slots = max_slots
		self.slots: list[InventorySlot] = []
		self.equipment = Equipment()

		# Inicializar slots vacíos
		for i in range(max_slots):
			self.slots.append(InventorySlot(item=None, slot_id=i))

		logger.info("Inventario inicializado con %d slots", max_slots)

	def add_item(self, item: LootItem) -> bool:
		"""
		Añade un objeto al inventario

		Args:
		    item: El objeto a añadir

		Returns:
		    True si se añadió exitosamente, False si no hay espacio
		"""
		# Buscar primer slot vacío
		for slot in self.slots:
			if slot.is_empty():
				slot.item = item
				logger.info(
					"Objeto añadido al inventario: %s (slot %d)",
					item.get_display_name(),
					slot.slot_id,
				)
				return True

		logger.warning("Inventario lleno, no se pudo añadir: %s", item.get_display_name())
		return False

	def equip_item(self, slot_id: int) -> bool:
		"""
		Equipa un objeto desde el inventario

		Args:
		    slot_id: ID del slot del objeto a equipar

		Returns:
		    True si se equipó exitosamente
		"""
		if 0 <= slot_id < len(self.slots):
			slot = self.slots[slot_id]
			if not slot.is_empty() and slot.item:
				# Solo armas, artefactos y gemas pueden equiparse
				if slot.item.loot_type in [LootType.WEAPON, LootType.ARTIFACT, LootType.GEM]:
					return self.equipment.equip_item(slot.item)

		return False

	def get_all_items(self) -> list[tuple[int, LootItem]]:
		"""
		Obtiene todos los objetos del inventario

		Returns:
		    Lista de tuplas (slot_id, item) de todos los objetos
		"""
		items = []
		for slot in self.slots:
			if not slot.is_empty() and slot.item:
				items.append((slot.slot_id, slot.item))
		return items

	@property
	def items(self) -> list[LootItem]:
		"""
		Propiedad que devuelve todos los objetos del inventario sin slot_id

		Returns:
		    Lista de todos los objetos en el inventario
		"""
		items = []
		for slot in self.slots:
			if not slot.is_empty() and slot.item:
				items.append(slot.item)
		return items

	def get_used_slots_count(self) -> int:
		"""Retorna el número de slots ocupados"""
		return sum(1 for slot in self.slots if not slot.is_empty())

	def get_inventory_summary(self) -> dict[str, int]:
		"""
		Obtiene un resumen del inventario

		Returns:
		    Diccionario con conteos por tipo y rareza
		"""
		summary = {
			"total_items": self.get_used_slots_count(),
			"equipped_items": len(self.equipment.get_equipped_items()),
		}

		# Conteo por tipo
		type_counts = {loot_type: 0 for loot_type in LootType}
		for slot in self.slots:
			if not slot.is_empty() and slot.item:
				type_counts[slot.item.loot_type] += 1

		for loot_type, count in type_counts.items():
			summary[f"{loot_type.value}_count"] = count

		return summary


# Función de testing
def test_inventory_system():
	"""Función de prueba para el sistema de inventario"""
	from core.loot import LootGenerator

	print("=== Prueba del Sistema de Inventario ===\n")

	# Crear inventario y generador
	inventory = Inventory(max_slots=20)
	generator = LootGenerator()

	# Generar y añadir objetos
	print("1. GENERANDO Y AÑADIENDO OBJETOS:")
	for _ in range(15):
		item = generator.generate_random_loot()
		success = inventory.add_item(item)
		print(
			f"   {item.get_display_name()} - {'✅ Añadido' if success else '❌ Inventario lleno'}"
		)

	print("\n2. RESUMEN DEL INVENTARIO:")
	summary = inventory.get_inventory_summary()
	print(f"   Total objetos: {summary['total_items']}")
	print(f"   Armas: {summary['weapon_count']}")
	print(f"   Artefactos: {summary['artifact_count']}")
	print(f"   Gemas: {summary['gem_count']}")
	print(f"   Materiales: {summary['material_count']}")

	print("\n3. EQUIPANDO OBJETOS:")
	# Intentar equipar algunos objetos
	all_items = inventory.get_all_items()
	equipped_count = 0

	for slot_id, item in all_items:
		if item.loot_type in [LootType.WEAPON, LootType.ARTIFACT, LootType.GEM]:
			if inventory.equip_item(slot_id):
				print(f"   ✅ Equipado: {item.get_display_name()}")
				equipped_count += 1
				if equipped_count >= 3:  # Máximo uno por tipo
					break

	print("\n4. OBJETOS EQUIPADOS:")
	equipped = inventory.equipment.get_equipped_items()
	for item in equipped:
		print(f"   {item.get_display_name()} - {item.get_stat_summary()}")

	print("\n5. ESTADÍSTICAS TOTALES:")
	total_stats = inventory.equipment.get_total_stats()
	for stat_name, value in total_stats.items():
		if stat_name.endswith("_multiplier"):
			print(f"   {stat_name}: x{value:.3f}")
		else:
			print(f"   {stat_name}: {value:.2f}")


if __name__ == "__main__":
	test_inventory_system()
