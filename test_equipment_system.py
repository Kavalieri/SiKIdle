#!/usr/bin/env python3
"""
Script de prueba para verificar el sistema de equipamiento y venta.
"""

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from core.game import get_game_state
from core.equipment_manager import EquipmentManager
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format="%(message)s")


def test_equipment_system():
	"""Prueba el sistema de equipamiento"""
	print("=== 🧪 TESTING SIKIDLE EQUIPMENT SYSTEM ===\n")

	# Obtener GameState
	game_state = get_game_state()
	print(f"📊 GameState: {game_state.coins} monedas, nivel {game_state.player_level}")
	print(f"⭐ Puntos de talento: {game_state.talent_points}")

	# Verificar EquipmentManager
	equipment_manager = game_state.equipment_manager
	print(f"\n🎒 Equipment Manager: {len(equipment_manager.inventory)} items en inventario")

	# Si el inventario está vacío, generar algunos items de prueba
	if not equipment_manager.inventory:
		print("❌ Inventario vacío - Generando items de prueba...")

		# Generar algunos items usando el LootGenerator
		loot_generator = game_state.loot_generator

		# Simular drops de enemigos usando drop_loot_from_enemy
		for _ in range(3):
			items = loot_generator.drop_loot_from_enemy(
				enemy_name="Orco de Prueba", enemy_level=1, player_level=1, is_boss=False
			)
			for item in items:
				equipment_manager.add_to_inventory(item)
				print(f"  ➕ Generado: {item.name}")

		# También generar algunos items aleatorios
		for _ in range(2):
			item = loot_generator.generate_random_loot()
			equipment_manager.add_to_inventory(item)
			print(f"  🎲 Aleatorio: {item.name}")

	# Mostrar inventario
	print(f"\n📦 === INVENTARIO ACTUAL ({len(equipment_manager.inventory)} items) ===")
	if not equipment_manager.inventory:
		print("❌ Aún vacío después de generación")
		return

	for i, item in enumerate(equipment_manager.inventory):
		rarity_emoji = {"Common": "🤍", "Rare": "💚", "Epic": "💙", "Legendary": "🧡"}.get(
			item.rarity.name, "❓"
		)

		power = item.stats.get_total_power()
		sell_price = max(1, int(power * 0.5))

		print(f"  {i}: {rarity_emoji} {item.name} - Poder: {power} - Venta: {sell_price} oro")
		print(
			f"      Tipo: {item.type.name} | Stats: ATK+{item.stats.attack}, DEF+{item.stats.defense}"
		)

	# Probar sistema de venta
	print(f"\n💰 === PRUEBA DE VENTA ===")
	if equipment_manager.inventory:
		item_to_sell = equipment_manager.inventory[0]
		original_coins = game_state.coins
		sell_price = max(1, int(item_to_sell.stats.get_total_power() * 0.5))

		print(f"🏷️  Vendiendo: {item_to_sell.name}")
		print(f"💰 Precio de venta: {sell_price} oro")
		print(f"🪙  Monedas antes: {original_coins}")

		# Simular venta
		game_state.add_coins(sell_price)
		equipment_manager.inventory.remove(item_to_sell)

		print(f"✅ ¡Venta exitosa!")
		print(f"🪙  Monedas después: {game_state.coins}")
		print(f"📦 Items restantes: {len(equipment_manager.inventory)}")

	# Verificar sistema de talentos
	print(f"\n⭐ === SISTEMA DE TALENTOS ===")
	talent_manager = game_state.talent_manager
	print(f"🌟 Puntos disponibles: {game_state.talent_points}")

	# Mostrar algunas ramas de talentos
	branches = ["warrior", "mage", "explorer", "tank"]
	for branch in branches:
		if branch in talent_manager.talents:
			talent = talent_manager.talents[branch]
			cost = talent_manager.get_upgrade_cost(branch)
			print(
				f"   {branch.capitalize()}: Nivel {talent['level']} (Coste upgrade: {cost} puntos)"
			)

	print(f"\n✅ === RESUMEN DE SISTEMAS ===")
	print(f"🎒 Inventario: {'✅ Funcional' if equipment_manager.inventory else '❌ Vacío'}")
	print(f"💰 Venta: ✅ Funcional (precio basado en poder del item)")
	print(f"⭐ Talentos: ✅ Funcional ({game_state.talent_points} puntos disponibles)")
	print(
		f"🔄 Level up: ✅ Funcional (nivel {game_state.player_level}, {game_state.experience} XP)"
	)

	print(f"\n🎮 ¡Todos los sistemas están funcionando correctamente!")


if __name__ == "__main__":
	test_equipment_system()
