"""
Sistema de Integración de Equipamiento para SiKIdle

Este módulo conecta el sistema de loot e inventario con el GameState principal,
aplicando las bonificaciones de los objetos equipados al gameplay real.
"""

import logging
import sys
from pathlib import Path

# Agregar src al path para importaciones
src_path = Path(__file__).parent.parent
sys.path.insert(0, str(src_path))

from core.inventory import Inventory
from core.loot import LootType

logger = logging.getLogger(__name__)


class EquipmentIntegration:
	"""
	Integra las bonificaciones del inventario con el GameState

	Aplica automáticamente los efectos de objetos equipados a las
	mecánicas principales del juego (clics, edificios, experiencia, etc.)
	"""

	def __init__(self, game_state, inventory: Inventory):
		"""
		Inicializa la integración

		Args:
		    game_state: Instancia del GameState principal
		    inventory: Sistema de inventario con objetos equipados
		"""
		self.game_state = game_state
		self.inventory = inventory
		self.cached_bonuses: dict[str, float] = {}
		self.last_equipment_hash = ""
		self.original_values: dict[str, float] = {}

		logger.info("Sistema de integración de equipamiento inicializado")

	def update_equipment_bonuses(self) -> None:
		"""
		Actualiza las bonificaciones basadas en el equipamiento actual

		Recalcula solo si el equipamiento ha cambiado para optimizar rendimiento
		"""
		# Generar hash del equipamiento actual para detectar cambios
		equipped_items = self.inventory.equipment.get_equipped_items()
		current_hash = self._generate_equipment_hash(equipped_items)

		if current_hash != self.last_equipment_hash:
			logger.debug("Equipamiento cambió, recalculando bonificaciones")
			self._recalculate_bonuses()
			self.last_equipment_hash = current_hash

	def _generate_equipment_hash(self, equipped_items) -> str:
		"""Genera un hash del equipamiento actual para detectar cambios"""
		if not equipped_items:
			return "empty"

		item_ids = sorted([item.id for item in equipped_items])
		return "|".join(item_ids)

	def _recalculate_bonuses(self) -> None:
		"""Recalcula todas las bonificaciones del equipamiento"""
		total_stats = self.inventory.equipment.get_total_stats()

		# Resetear bonificaciones cached
		self.cached_bonuses = {
			"click_multiplier": 1.0,
			"crit_chance": 0.0,
			"crit_multiplier": 1.0,
			"building_income": 1.0,
			"global_income": 1.0,
			"experience_bonus": 1.0,
			"gem_active": False,
			"gem_multiplier": 1.0,
			"gem_duration": 0.0,
			"gem_cooldown": 0.0,
		}

		# Aplicar bonificaciones de objetos equipados
		for stat_name, value in total_stats.items():
			if stat_name in self.cached_bonuses:
				self.cached_bonuses[stat_name] = value
			elif stat_name == "temporary_multiplier":
				self.cached_bonuses["gem_multiplier"] = value
				self.cached_bonuses["gem_active"] = True
			elif stat_name == "duration":
				self.cached_bonuses["gem_duration"] = value
			elif stat_name == "cooldown":
				self.cached_bonuses["gem_cooldown"] = value

		logger.info("Bonificaciones de equipamiento recalculadas: %s", self.cached_bonuses)

	def get_click_multiplier(self) -> float:
		"""
		Obtiene el multiplicador total de clic incluyendo equipamiento

		Returns:
		    Multiplicador que debe aplicarse a los clics
		"""
		self.update_equipment_bonuses()

		base_multiplier = self.cached_bonuses.get("click_multiplier", 1.0)
		global_multiplier = self.cached_bonuses.get("global_income", 1.0)

		return base_multiplier * global_multiplier

	def get_building_multiplier(self) -> float:
		"""
		Obtiene el multiplicador para ingresos de edificios

		Returns:
		    Multiplicador que debe aplicarse a la producción de edificios
		"""
		self.update_equipment_bonuses()

		building_multiplier = self.cached_bonuses.get("building_income", 1.0)
		global_multiplier = self.cached_bonuses.get("global_income", 1.0)

		return building_multiplier * global_multiplier

	def get_critical_chance(self) -> float:
		"""
		Obtiene la probabilidad crítica adicional del equipamiento

		Returns:
		    Probabilidad crítica adicional (0.0 a 1.0)
		"""
		self.update_equipment_bonuses()
		return self.cached_bonuses.get("crit_chance", 0.0)

	def get_critical_multiplier(self) -> float:
		"""
		Obtiene el multiplicador de daño crítico del equipamiento

		Returns:
		    Multiplicador de daño crítico
		"""
		self.update_equipment_bonuses()
		return self.cached_bonuses.get("crit_multiplier", 1.0)

	def get_experience_multiplier(self) -> float:
		"""
		Obtiene el multiplicador de experiencia del equipamiento

		Returns:
		    Multiplicador de experiencia ganada
		"""
		self.update_equipment_bonuses()
		return self.cached_bonuses.get("experience_bonus", 1.0)

	def is_gem_active(self) -> bool:
		"""
		Verifica si hay una gema equipada que otorga efectos temporales

		Returns:
		    True si hay una gema activa equipada
		"""
		self.update_equipment_bonuses()
		return self.cached_bonuses.get("gem_active", False)

	def get_gem_multiplier(self) -> float:
		"""
		Obtiene el multiplicador temporal de la gema equipada

		Returns:
		    Multiplicador temporal (solo si hay gema equipada)
		"""
		if not self.is_gem_active():
			return 1.0

		return self.cached_bonuses.get("gem_multiplier", 1.0)

	def get_equipment_summary(self) -> dict[str, any]:
		"""
		Obtiene un resumen completo de las bonificaciones activas

		Returns:
		    Diccionario con todas las bonificaciones activas
		"""
		self.update_equipment_bonuses()

		equipped_items = self.inventory.equipment.get_equipped_items()

		summary = {
			"equipped_items": len(equipped_items),
			"items": [item.get_display_name() for item in equipped_items],
			"bonuses": self.cached_bonuses.copy(),
			"effective_multipliers": {
				"click": self.get_click_multiplier(),
				"building": self.get_building_multiplier(),
				"experience": self.get_experience_multiplier(),
				"critical_chance": self.get_critical_chance(),
				"critical_damage": self.get_critical_multiplier(),
			},
		}

		if self.is_gem_active():
			summary["gem_effects"] = {
				"active": True,
				"multiplier": self.get_gem_multiplier(),
				"duration": self.cached_bonuses.get("gem_duration", 0),
				"cooldown": self.cached_bonuses.get("gem_cooldown", 0),
			}

		return summary

	def apply_to_game_state(self) -> None:
		"""
		Aplica las bonificaciones del equipamiento al GameState principal

		Modifica los multiplicadores del juego para incluir efectos del equipamiento
		"""
		# Modificar multiplicadores de talentos para incluir equipamiento
		equipment_click_bonus = self.get_click_multiplier()
		equipment_building_bonus = self.get_building_multiplier()
		equipment_exp_bonus = self.get_experience_multiplier()
		equipment_crit_chance = self.get_critical_chance()
		equipment_crit_damage = self.get_critical_multiplier()

		# Guardar valores originales si no se han guardado ya
		if not self.original_values:
			self.original_values = {
				"click_income": self.game_state.talent_multipliers["click_income"],
				"building_income": self.game_state.talent_multipliers["building_income"],
				"experience_gain": self.game_state.talent_multipliers["experience_gain"],
				"critical_chance": self.game_state.talent_multipliers["critical_chance"],
				"critical_damage": self.game_state.talent_multipliers["critical_damage"],
			}

		# Aplicar bonificaciones del equipamiento multiplicativamente
		self.game_state.talent_multipliers["click_income"] = (
			self.original_values["click_income"] * equipment_click_bonus
		)
		self.game_state.talent_multipliers["building_income"] = (
			self.original_values["building_income"] * equipment_building_bonus
		)
		self.game_state.talent_multipliers["experience_gain"] = (
			self.original_values["experience_gain"] * equipment_exp_bonus
		)

		# Para críticos, sumar probabilidad y multiplicar daño
		self.game_state.talent_multipliers["critical_chance"] = (
			self.original_values["critical_chance"] + equipment_crit_chance
		)
		self.game_state.talent_multipliers["critical_damage"] = (
			self.original_values["critical_damage"] * equipment_crit_damage
		)

		logger.debug(
			"Bonificaciones aplicadas al GameState: click=%.2f, building=%.2f, exp=%.2f",
			equipment_click_bonus,
			equipment_building_bonus,
			equipment_exp_bonus,
		)


# Función de testing
def test_equipment_integration():
	"""Función de prueba para la integración de equipamiento"""

	# Mock simple del GameState para testing
	class MockGameState:
		def __init__(self):
			self.talent_multipliers = {
				"click_income": 1.0,
				"building_income": 1.0,
				"experience_gain": 1.0,
				"critical_chance": 0.0,
				"critical_damage": 1.0,
			}

	print("=== Prueba de Integración de Equipamiento ===\n")

	# Crear componentes necesarios
	from core.inventory import Inventory
	from core.loot import LootGenerator

	inventory = Inventory(max_slots=20)
	generator = LootGenerator()
	game_state = MockGameState()

	# Crear integración
	integration = EquipmentIntegration(game_state, inventory)

	print("1. ESTADO INICIAL:")
	summary = integration.get_equipment_summary()
	print(f"   Objetos equipados: {summary['equipped_items']}")
	print(f"   Multiplicador de clic: {summary['effective_multipliers']['click']:.3f}")

	# Generar y equipar objetos
	print("\n2. EQUIPANDO OBJETOS:")
	for _ in range(10):
		item = generator.generate_random_loot()
		if inventory.add_item(item):
			# Intentar equipar si es equipable
			all_items = inventory.get_all_items()
			for slot_id, stored_item in all_items:
				if stored_item.id == item.id and stored_item.loot_type in [
					LootType.WEAPON,
					LootType.ARTIFACT,
					LootType.GEM,
				]:
					if inventory.equip_item(slot_id):
						print(f"   ✅ Equipado: {item.get_display_name()}")
						break

	print("\n3. ESTADO DESPUÉS DEL EQUIPAMIENTO:")
	summary = integration.get_equipment_summary()
	print(f"   Objetos equipados: {summary['equipped_items']}")
	print(f"   Items: {', '.join(summary['items'])}")

	print("\n4. MULTIPLICADORES EFECTIVOS:")
	for stat_name, value in summary["effective_multipliers"].items():
		if stat_name == "critical_chance":
			print(f"   {stat_name}: +{value * 100:.1f}%")
		else:
			print(f"   {stat_name}: x{value:.3f}")

	print("\n5. APLICANDO AL GAME STATE:")
	print("   Multiplicadores antes:")
	print(f"     click_income: {game_state.talent_multipliers['click_income']:.3f}")
	print(f"     building_income: {game_state.talent_multipliers['building_income']:.3f}")

	integration.apply_to_game_state()

	print("   Multiplicadores después:")
	print(f"     click_income: {game_state.talent_multipliers['click_income']:.3f}")
	print(f"     building_income: {game_state.talent_multipliers['building_income']:.3f}")

	if summary.get("gem_effects", {}).get("active"):
		print("\n6. EFECTOS DE GEMA:")
		gem_effects = summary["gem_effects"]
		print(f"   Multiplicador temporal: x{gem_effects['multiplier']:.3f}")
		print(f"   Duración: {gem_effects['duration']:.1f} segundos")
		print(f"   Recarga: {gem_effects['cooldown'] / 60:.1f} minutos")


if __name__ == "__main__":
	test_equipment_integration()
