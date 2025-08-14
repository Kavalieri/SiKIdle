"""Sistema de recursos múltiples para SiKIdle.

Gestiona diferentes tipos de monedas y materiales del juego.
"""

import logging
from dataclasses import dataclass
from enum import Enum


class ResourceType(Enum):
	"""Tipos de recursos disponibles en el juego."""

	# Monedas principales
	COINS = "coins"  # Oro - Moneda básica
	PLATINUM = "platinum"  # Platino - Moneda de prestigio
	DIAMONDS = "diamonds"  # Diamantes - Moneda premium

	# Recursos especiales
	ENERGY = "energy"  # Energía - Para habilidades
	EXPERIENCE = "experience"  # Experiencia - Para niveles

	# Materiales de crafteo
	IRON = "iron"  # Hierro - Material básico
	WOOD = "wood"  # Madera - Material básico
	STONE = "stone"  # Piedra - Material básico
	CRYSTALS = "crystals"  # Cristales - Material avanzado

	# Recursos de exploración de mazmorras
	ALIMENTOS = "Alimentos"  # De Praderas Verdes
	MADERA_MAGICA = "Madera Mágica"  # De Bosque Ancestral
	HIERRO = "Hierro"  # De Minas de Hierro Profundo
	ESENCIA_ARCANA = "Esencia Arcana"  # De Ruinas Arcanas
	ORO_DRAGON = "Oro del Dragón"  # De Fortaleza del Dragón


@dataclass
class ResourceInfo:
	"""Información sobre un tipo de recurso."""

	name: str
	symbol: str
	description: str
	color: str = "#FFFFFF"
	unlock_level: int = 1
	max_value = None
	precision: int = 0  # Decimales a mostrar


class ResourceManager:
	"""Gestiona todos los recursos del juego."""

	def __init__(self):
		"""Inicializa el gestor de recursos."""
		# Almacenamiento de recursos
		self._resources = {}

		# Información de cada tipo de recurso
		self._resource_info = {
			ResourceType.COINS: ResourceInfo(
				name="Oro", symbol="🪙", description="Moneda básica del juego", color="#FFD700"
			),
			ResourceType.PLATINUM: ResourceInfo(
				name="Platino",
				symbol="💎",
				description="Moneda obtenida por prestigio",
				color="#E5E4E2",
				unlock_level=25,
			),
			ResourceType.DIAMONDS: ResourceInfo(
				name="Diamantes",
				symbol="💠",
				description="Moneda premium especial",
				color="#B9F2FF",
				unlock_level=50,
			),
			ResourceType.ENERGY: ResourceInfo(
				name="Energía",
				symbol="⚡",
				description="Poder para habilidades especiales",
				color="#FFFF00",
				unlock_level=10,
			),
			ResourceType.EXPERIENCE: ResourceInfo(
				name="Experiencia",
				symbol="✨",
				description="Progreso hacia el siguiente nivel",
				color="#9370DB",
				unlock_level=5,
			),
			ResourceType.IRON: ResourceInfo(
				name="Hierro",
				symbol="🔩",
				description="Material básico para construcción",
				color="#808080",
				unlock_level=15,
			),
			ResourceType.WOOD: ResourceInfo(
				name="Madera",
				symbol="🪵",
				description="Recurso natural renovable",
				color="#8B4513",
				unlock_level=12,
			),
			ResourceType.STONE: ResourceInfo(
				name="Piedra",
				symbol="🪨",
				description="Material resistente para edificios",
				color="#696969",
				unlock_level=18,
			),
			ResourceType.CRYSTALS: ResourceInfo(
				name="Cristales",
				symbol="🔮",
				description="Energía cristalizada muy valiosa",
				color="#FF69B4",
				unlock_level=30,
			),
			# Recursos de exploración de mazmorras
			ResourceType.ALIMENTOS: ResourceInfo(
				name="Alimentos",
				symbol="🥖",
				description="Recursos nutritivos de las praderas",
				color="#90EE90",
				unlock_level=1,
			),
			ResourceType.MADERA_MAGICA: ResourceInfo(
				name="Madera Mágica",
				symbol="🌳",
				description="Madera imbuida de energía ancestral",
				color="#228B22",
				unlock_level=1,
			),
			ResourceType.HIERRO: ResourceInfo(
				name="Hierro",
				symbol="⛏️",
				description="Metal resistente de las minas profundas",
				color="#A0A0A0",
				unlock_level=1,
			),
			ResourceType.ESENCIA_ARCANA: ResourceInfo(
				name="Esencia Arcana",
				symbol="🔮",
				description="Poder mágico de las ruinas antiguas",
				color="#8A2BE2",
				unlock_level=1,
			),
			ResourceType.ORO_DRAGON: ResourceInfo(
				name="Oro del Dragón",
				symbol="🐉",
				description="Tesoro legendario custodiado por dragones",
				color="#FFD700",
				unlock_level=1,
			),
		}

		# Configurar recursos iniciales
		for resource_type in ResourceType:
			self._resources[resource_type] = 0.0

		# Configuración específica por recurso
		self._resources[ResourceType.COINS] = 0.0
		self._resources[ResourceType.ENERGY] = 100.0  # Energía completa al inicio

		logging.info("Gestor de recursos inicializado")

	def get_resource(self, resource_type: ResourceType) -> float:
		"""Obtiene la cantidad de un recurso específico."""
		return self._resources.get(resource_type, 0.0)

	def set_resource(self, resource_type: ResourceType, amount: float) -> None:
		"""Establece la cantidad de un recurso específico."""
		# Aplicar límite máximo si existe
		resource_info = self._resource_info[resource_type]
		if resource_info.max_value is not None:
			amount = min(amount, resource_info.max_value)

		# No permitir valores negativos
		amount = max(0.0, amount)

		self._resources[resource_type] = amount

	def add_resource(self, resource_type: ResourceType, amount: float) -> float:
		"""Añade cantidad a un recurso específico.

		Returns:
			Cantidad realmente añadida (después de aplicar límites)
		"""
		if amount <= 0:
			return 0.0

		current = self.get_resource(resource_type)
		resource_info = self._resource_info[resource_type]

		# Calcular nueva cantidad con límites
		new_amount = current + amount
		if resource_info.max_value is not None:
			new_amount = min(new_amount, resource_info.max_value)

		actually_added = new_amount - current
		self.set_resource(resource_type, new_amount)

		return actually_added

	def spend_resource(self, resource_type: ResourceType, amount: float) -> bool:
		"""Intenta gastar una cantidad de un recurso.

		Returns:
			True si se pudo gastar, False si no hay suficiente
		"""
		if amount <= 0:
			return True

		current = self.get_resource(resource_type)
		if current >= amount:
			self.set_resource(resource_type, current - amount)
			return True
		return False

	def can_afford(self, resource_type: ResourceType, amount: float) -> bool:
		"""Verifica si se puede gastar una cantidad de un recurso."""
		return self.get_resource(resource_type) >= amount

	def get_resource_info(self, resource_type: ResourceType) -> ResourceInfo:
		"""Obtiene la información de un tipo de recurso."""
		return self._resource_info[resource_type]

	def get_all_resources(self):
		"""Obtiene todos los recursos como diccionario."""
		return self._resources.copy()

	def format_resource(self, resource_type: ResourceType, amount=None) -> str:
		"""Formatea un recurso para mostrar en UI.

		Args:
			resource_type: Tipo de recurso
			amount: Cantidad específica (usa cantidad actual si None)
		"""
		if amount is None:
			amount = self.get_resource(resource_type)

		resource_info = self._resource_info[resource_type]

		# Formatear número según precisión
		if resource_info.precision == 0:
			formatted_amount = f"{int(amount):,}"
		else:
			formatted_amount = f"{amount:,.{resource_info.precision}f}"

		return f"{resource_info.symbol} {formatted_amount}"

	def is_resource_unlocked(self, resource_type: ResourceType, player_level: int = 1) -> bool:
		"""Verifica si un recurso está desbloqueado para el nivel del jugador."""
		resource_info = self._resource_info[resource_type]
		return player_level >= resource_info.unlock_level

	def get_unlocked_resources(self, player_level: int = 1) -> list[ResourceType]:
		"""Obtiene lista de recursos desbloqueados para el nivel del jugador."""
		return [
			resource_type
			for resource_type in ResourceType
			if self.is_resource_unlocked(resource_type, player_level)
		]

	def convert_resource(
		self, from_type: ResourceType, to_type: ResourceType, amount: float, rate: float
	) -> bool:
		"""Convierte un recurso a otro usando una tasa de cambio.

		Args:
			from_type: Recurso de origen
			to_type: Recurso de destino
			amount: Cantidad a convertir
			rate: Tasa de conversión (cuánto del destino por unidad del origen)

		Returns:
			True si la conversión fue exitosa
		"""
		if not self.can_afford(from_type, amount):
			return False

		# Calcular cantidad a recibir
		converted_amount = amount * rate

		# Realizar la conversión
		if self.spend_resource(from_type, amount):
			actually_added = self.add_resource(to_type, converted_amount)
			logging.info(
				f"Convertido {amount} {from_type.value} → {actually_added} {to_type.value}"
			)
			return True

		return False

	def get_save_data(self):
		"""Obtiene datos para guardar."""
		return {
			"resources": {
				resource_type.value: amount for resource_type, amount in self._resources.items()
			}
		}

	def load_save_data(self, data) -> None:
		"""Carga datos guardados."""
		if "resources" in data:
			for resource_name, amount in data["resources"].items():
				try:
					resource_type = ResourceType(resource_name)
					self.set_resource(resource_type, float(amount))
				except (ValueError, TypeError):
					logging.warning("Recurso desconocido en guardado: %s", resource_name)

		logging.info("Recursos cargados desde guardado")
