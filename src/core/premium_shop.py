"""
Sistema de Tienda Premium para SiKIdle - Monetización No Intrusiva.

Sistema dual de monedas/gemas con:
- Paquetes de gemas (0.99€ - 19.99€)
- Bonus temporales (pay-to-accelerate)
- Aceleradores de progreso
- Cosméticos premium
- NO pay-to-win, solo conveniencia
"""

import logging
import time
from typing import Dict, List, Any, Optional
from enum import Enum
from dataclasses import dataclass


class PremiumItemType(Enum):
	"""Tipos de items premium."""

	GEM_PACK = "gem_pack"
	TEMPORARY_BOOST = "temporary_boost"
	PROGRESS_ACCELERATOR = "progress_accelerator"
	COSMETIC = "cosmetic"
	CONVENIENCE = "convenience"


class BoostType(Enum):
	"""Tipos de boosts temporales."""

	COIN_MULTIPLIER = "coin_multiplier"
	CLICK_MULTIPLIER = "click_multiplier"
	BUILDING_SPEED = "building_speed"
	XP_MULTIPLIER = "xp_multiplier"
	OFFLINE_EARNINGS = "offline_earnings"


@dataclass
class PremiumItem:
	"""Item de la tienda premium."""

	id: str
	name: str
	description: str
	item_type: PremiumItemType
	gem_cost: int
	real_money_cost: Optional[float] = None  # En euros
	duration_minutes: Optional[int] = None
	multiplier: Optional[float] = None
	boost_type: Optional[BoostType] = None
	icon: str = "💎"


class PremiumShopManager:
	"""Gestor de la tienda premium."""

	def __init__(self, game_state):
		self.game_state = game_state

		# Moneda premium
		self.gems = 0

		# Boosts activos
		self.active_boosts: Dict[BoostType, Dict] = {}

		# Items comprados
		self.owned_cosmetics: set = set()
		self.owned_convenience: set = set()

		# Configurar catálogo
		self.catalog = self._create_premium_catalog()

		# Base de datos
		self._create_tables()
		self.load_data()

		logging.info("PremiumShopManager initialized")

	def _create_tables(self):
		"""Crea tablas de la tienda premium."""
		try:
			db = self.game_state.save_manager.db

			db.execute("""
				CREATE TABLE IF NOT EXISTS premium_data (
					id INTEGER PRIMARY KEY,
					gems INTEGER DEFAULT 0,
					owned_cosmetics TEXT DEFAULT '',
					owned_convenience TEXT DEFAULT '',
					created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
				)
			""")

			db.execute("""
				CREATE TABLE IF NOT EXISTS active_boosts (
					boost_type TEXT PRIMARY KEY,
					multiplier REAL,
					end_time REAL,
					created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
				)
			""")

			# Insertar fila inicial
			db.execute("INSERT OR IGNORE INTO premium_data (id) VALUES (1)")

			logging.debug("Premium shop tables created")

		except Exception as e:
			logging.error(f"Error creating premium tables: {e}")

	def _create_premium_catalog(self) -> List[PremiumItem]:
		"""Crea el catálogo de items premium."""
		return [
			# PAQUETES DE GEMAS
			PremiumItem(
				id="gems_starter",
				name="Paquete Inicial",
				description="Perfecto para empezar tu aventura premium",
				item_type=PremiumItemType.GEM_PACK,
				gem_cost=100,
				real_money_cost=0.99,
				icon="💎",
			),
			PremiumItem(
				id="gems_popular",
				name="Paquete Popular",
				description="¡El más elegido! Mejor valor por tu dinero",
				item_type=PremiumItemType.GEM_PACK,
				gem_cost=600,
				real_money_cost=4.99,
				icon="💎",
			),
			PremiumItem(
				id="gems_value",
				name="Paquete Valor",
				description="Máximo ahorro para jugadores serios",
				item_type=PremiumItemType.GEM_PACK,
				gem_cost=1300,
				real_money_cost=9.99,
				icon="💎",
			),
			PremiumItem(
				id="gems_ultimate",
				name="Paquete Definitivo",
				description="Para los verdaderos maestros del idle",
				item_type=PremiumItemType.GEM_PACK,
				gem_cost=2800,
				real_money_cost=19.99,
				icon="💎",
			),
			# BOOSTS TEMPORALES
			PremiumItem(
				id="boost_coins_1h",
				name="Lluvia de Monedas",
				description="Duplica tus ganancias de monedas por 1 hora",
				item_type=PremiumItemType.TEMPORARY_BOOST,
				gem_cost=50,
				duration_minutes=60,
				multiplier=2.0,
				boost_type=BoostType.COIN_MULTIPLIER,
				icon="💰",
			),
			PremiumItem(
				id="boost_click_30m",
				name="Dedos de Oro",
				description="Triplica el poder de tus clics por 30 minutos",
				item_type=PremiumItemType.TEMPORARY_BOOST,
				gem_cost=30,
				duration_minutes=30,
				multiplier=3.0,
				boost_type=BoostType.CLICK_MULTIPLIER,
				icon="👆",
			),
			PremiumItem(
				id="boost_building_2h",
				name="Turbo Edificios",
				description="Acelera la producción de edificios por 2 horas",
				item_type=PremiumItemType.TEMPORARY_BOOST,
				gem_cost=80,
				duration_minutes=120,
				multiplier=2.5,
				boost_type=BoostType.BUILDING_SPEED,
				icon="🏭",
			),
			PremiumItem(
				id="boost_xp_1h",
				name="Sabiduría Ancestral",
				description="Duplica la experiencia ganada por 1 hora",
				item_type=PremiumItemType.TEMPORARY_BOOST,
				gem_cost=40,
				duration_minutes=60,
				multiplier=2.0,
				boost_type=BoostType.XP_MULTIPLIER,
				icon="⭐",
			),
			# ACELERADORES DE PROGRESO
			PremiumItem(
				id="offline_8h",
				name="Ingresos Offline 8h",
				description="Recibe 8 horas de ingresos offline instantáneamente",
				item_type=PremiumItemType.PROGRESS_ACCELERATOR,
				gem_cost=100,
				icon="⏰",
			),
			PremiumItem(
				id="complete_building",
				name="Construcción Instantánea",
				description="Completa instantáneamente la compra de 10 edificios",
				item_type=PremiumItemType.PROGRESS_ACCELERATOR,
				gem_cost=150,
				icon="🚀",
			),
			PremiumItem(
				id="prestige_boost",
				name="Impulso de Prestigio",
				description="Gana 25% más cristales en tu próximo prestigio",
				item_type=PremiumItemType.PROGRESS_ACCELERATOR,
				gem_cost=200,
				icon="💎",
			),
			# CONVENIENCIA
			PremiumItem(
				id="auto_clicker",
				name="Auto-Clicker Premium",
				description="Clics automáticos cada 2 segundos (permanente)",
				item_type=PremiumItemType.CONVENIENCE,
				gem_cost=500,
				icon="🤖",
			),
			PremiumItem(
				id="offline_calculator",
				name="Calculadora Offline",
				description="Muestra exactamente cuánto ganarás offline",
				item_type=PremiumItemType.CONVENIENCE,
				gem_cost=200,
				icon="📊",
			),
			# COSMÉTICOS
			PremiumItem(
				id="golden_theme",
				name="Tema Dorado",
				description="Transforma tu interfaz con elegantes tonos dorados",
				item_type=PremiumItemType.COSMETIC,
				gem_cost=300,
				icon="✨",
			),
			PremiumItem(
				id="rainbow_clicks",
				name="Clics Arcoíris",
				description="Efectos de colores espectaculares al hacer clic",
				item_type=PremiumItemType.COSMETIC,
				gem_cost=150,
				icon="🌈",
			),
		]

	def get_catalog_by_type(self, item_type: PremiumItemType) -> List[PremiumItem]:
		"""Obtiene items del catálogo por tipo."""
		return [item for item in self.catalog if item.item_type == item_type]

	def can_afford_gems(self, cost: int) -> bool:
		"""Verifica si se pueden permitir las gemas."""
		return self.gems >= cost

	def purchase_with_gems(self, item_id: str) -> Dict[str, Any]:
		"""Compra un item con gemas."""
		item = next((i for i in self.catalog if i.id == item_id), None)
		if not item:
			return {"success": False, "reason": "Item no encontrado"}

		if not self.can_afford_gems(item.gem_cost):
			return {"success": False, "reason": "Gemas insuficientes"}

		# Procesar compra según tipo
		result = self._process_purchase(item)
		if result["success"]:
			self.gems -= item.gem_cost
			self.save_data()
			logging.info(f"Premium purchase: {item.name} for {item.gem_cost} gems")

		return result

	def purchase_gem_pack(self, pack_id: str) -> Dict[str, Any]:
		"""Simula compra de paquete de gemas (integración con tienda real)."""
		item = next((i for i in self.catalog if i.id == pack_id), None)
		if not item or item.item_type != PremiumItemType.GEM_PACK:
			return {"success": False, "reason": "Paquete no válido"}

		# En producción, aquí iría la integración con Google Play/App Store
		# Por ahora, simulamos la compra exitosa
		self.gems += item.gem_cost
		self.save_data()

		logging.info(f"Gem pack purchased: {item.name} (+{item.gem_cost} gems)")
		return {
			"success": True,
			"gems_added": item.gem_cost,
			"total_gems": self.gems,
			"cost": item.real_money_cost,
		}

	def _process_purchase(self, item: PremiumItem) -> Dict[str, Any]:
		"""Procesa la compra de un item."""
		if item.item_type == PremiumItemType.TEMPORARY_BOOST:
			return self._activate_boost(item)
		elif item.item_type == PremiumItemType.PROGRESS_ACCELERATOR:
			return self._apply_accelerator(item)
		elif item.item_type == PremiumItemType.COSMETIC:
			return self._unlock_cosmetic(item)
		elif item.item_type == PremiumItemType.CONVENIENCE:
			return self._unlock_convenience(item)

		return {"success": False, "reason": "Tipo de item no soportado"}

	def _activate_boost(self, item: PremiumItem) -> Dict[str, Any]:
		"""Activa un boost temporal."""
		if item.boost_type in self.active_boosts:
			# Extender duración si ya está activo
			current_end = self.active_boosts[item.boost_type]["end_time"]
			new_end = max(current_end, time.time()) + (item.duration_minutes * 60)
			self.active_boosts[item.boost_type]["end_time"] = new_end
		else:
			# Activar nuevo boost
			self.active_boosts[item.boost_type] = {
				"multiplier": item.multiplier,
				"end_time": time.time() + (item.duration_minutes * 60),
			}

		self._save_active_boosts()
		return {
			"success": True,
			"boost_type": item.boost_type.value,
			"multiplier": item.multiplier,
			"duration": item.duration_minutes,
		}

	def _apply_accelerator(self, item: PremiumItem) -> Dict[str, Any]:
		"""Aplica un acelerador de progreso."""
		if item.id == "offline_8h":
			# Simular 8 horas de ingresos offline
			offline_earnings = self._calculate_offline_earnings(8 * 3600)  # 8 horas en segundos
			self.game_state.coins += offline_earnings
			return {"success": True, "coins_added": offline_earnings}

		elif item.id == "complete_building":
			# Comprar 10 edificios del más barato disponible
			buildings_bought = self._auto_buy_buildings(10)
			return {"success": True, "buildings_bought": buildings_bought}

		elif item.id == "prestige_boost":
			# Añadir boost temporal al próximo prestigio
			# Esto se implementaría en el PrestigeManager
			return {"success": True, "prestige_boost": 1.25}

		return {"success": False, "reason": "Acelerador no implementado"}

	def _unlock_cosmetic(self, item: PremiumItem) -> Dict[str, Any]:
		"""Desbloquea un cosmético."""
		if item.id in self.owned_cosmetics:
			return {"success": False, "reason": "Ya poseído"}

		self.owned_cosmetics.add(item.id)
		return {"success": True, "cosmetic_unlocked": item.id}

	def _unlock_convenience(self, item: PremiumItem) -> Dict[str, Any]:
		"""Desbloquea una función de conveniencia."""
		if item.id in self.owned_convenience:
			return {"success": False, "reason": "Ya poseído"}

		self.owned_convenience.add(item.id)
		return {"success": True, "convenience_unlocked": item.id}

	def get_active_multipliers(self) -> Dict[str, float]:
		"""Obtiene multiplicadores activos de boosts premium."""
		multipliers = {
			"coin_multiplier": 1.0,
			"click_multiplier": 1.0,
			"building_multiplier": 1.0,
			"xp_multiplier": 1.0,
		}

		current_time = time.time()
		expired_boosts = []

		for boost_type, boost_data in self.active_boosts.items():
			if current_time > boost_data["end_time"]:
				expired_boosts.append(boost_type)
				continue

			# Aplicar multiplicador
			if boost_type == BoostType.COIN_MULTIPLIER:
				multipliers["coin_multiplier"] *= boost_data["multiplier"]
			elif boost_type == BoostType.CLICK_MULTIPLIER:
				multipliers["click_multiplier"] *= boost_data["multiplier"]
			elif boost_type == BoostType.BUILDING_SPEED:
				multipliers["building_multiplier"] *= boost_data["multiplier"]
			elif boost_type == BoostType.XP_MULTIPLIER:
				multipliers["xp_multiplier"] *= boost_data["multiplier"]

		# Limpiar boosts expirados
		for boost_type in expired_boosts:
			del self.active_boosts[boost_type]
			logging.info(f"Premium boost expired: {boost_type.value}")

		return multipliers

	def _calculate_offline_earnings(self, seconds: int) -> int:
		"""Calcula ganancias offline."""
		if not hasattr(self.game_state, "building_manager"):
			return 0

		# Calcular producción por segundo total
		total_production = 0
		for building in self.game_state.building_manager.buildings.values():
			if building.count > 0:
				info = self.game_state.building_manager.get_building_info(building.building_type)
				production = building.get_total_production_per_second(info)
				total_production += production

		# Aplicar multiplicadores
		multipliers = self.game_state.prestige_manager.get_multipliers()
		total_production *= multipliers["building_multiplier"]

		return int(total_production * seconds)

	def _auto_buy_buildings(self, count: int) -> int:
		"""Compra automáticamente edificios."""
		if not hasattr(self.game_state, "building_manager"):
			return 0

		buildings_bought = 0
		building_manager = self.game_state.building_manager

		for _ in range(count):
			# Encontrar el edificio más barato que se pueda permitir
			cheapest_cost = float("inf")
			cheapest_type = None

			for building_type, building in building_manager.buildings.items():
				info = building_manager.get_building_info(building_type)
				cost = building.get_current_cost(info)

				if cost < cheapest_cost and self.game_state.coins >= cost:
					cheapest_cost = cost
					cheapest_type = building_type

			# Comprar si se encontró uno
			if cheapest_type and building_manager.purchase_building(cheapest_type, self.game_state):
				buildings_bought += 1
			else:
				break  # No se puede comprar más

		return buildings_bought

	def add_gems(self, amount: int, source: str = "unknown"):
		"""Añade gemas desde fuentes externas (logros, eventos, etc.)."""
		if amount > 0:
			self.gems += amount
			self.save_data()
			logging.info(f"Gems added: +{amount} from {source} (total: {self.gems})")

	def get_shop_stats(self) -> Dict[str, Any]:
		"""Obtiene estadísticas de la tienda."""
		active_boost_count = len(
			[b for b in self.active_boosts.values() if time.time() < b["end_time"]]
		)

		return {
			"gems": self.gems,
			"active_boosts": active_boost_count,
			"owned_cosmetics": len(self.owned_cosmetics),
			"owned_convenience": len(self.owned_convenience),
			"catalog_items": len(self.catalog),
			"active_multipliers": self.get_active_multipliers(),
		}

	def save_data(self):
		"""Guarda datos de la tienda premium."""
		try:
			db = self.game_state.save_manager.db

			# Guardar datos principales
			cosmetics_str = ",".join(self.owned_cosmetics)
			convenience_str = ",".join(self.owned_convenience)

			db.execute(
				"""
				UPDATE premium_data 
				SET gems = ?, owned_cosmetics = ?, owned_convenience = ?
				WHERE id = 1
			""",
				(self.gems, cosmetics_str, convenience_str),
			)

			self._save_active_boosts()
			logging.debug("Premium shop data saved")

		except Exception as e:
			logging.error(f"Error saving premium data: {e}")

	def _save_active_boosts(self):
		"""Guarda boosts activos."""
		try:
			db = self.game_state.save_manager.db

			# Limpiar boosts expirados
			db.execute("DELETE FROM active_boosts WHERE end_time < ?", (time.time(),))

			# Guardar boosts activos
			for boost_type, boost_data in self.active_boosts.items():
				db.execute(
					"""
					INSERT OR REPLACE INTO active_boosts 
					(boost_type, multiplier, end_time)
					VALUES (?, ?, ?)
				""",
					(boost_type.value, boost_data["multiplier"], boost_data["end_time"]),
				)

		except Exception as e:
			logging.error(f"Error saving active boosts: {e}")

	def load_data(self):
		"""Carga datos de la tienda premium."""
		try:
			db = self.game_state.save_manager.db

			# Cargar datos principales
			result = db.execute("""
				SELECT gems, owned_cosmetics, owned_convenience
				FROM premium_data WHERE id = 1
			""")

			if result:
				row = result[0] if result else None
				if row:
					self.gems, cosmetics_str, convenience_str = row

					if cosmetics_str:
						self.owned_cosmetics = set(cosmetics_str.split(","))
					if convenience_str:
						self.owned_convenience = set(convenience_str.split(","))

			# Cargar boosts activos
			boost_results = db.execute(
				"""
				SELECT boost_type, multiplier, end_time
				FROM active_boosts WHERE end_time > ?
			""",
				(time.time(),),
			)

			for boost_type_str, multiplier, end_time in boost_results:
				boost_type = BoostType(boost_type_str)
				self.active_boosts[boost_type] = {"multiplier": multiplier, "end_time": end_time}

			logging.info(
				f"Premium shop loaded: {self.gems} gems, {len(self.active_boosts)} active boosts"
			)

		except Exception as e:
			logging.error(f"Error loading premium data: {e}")
