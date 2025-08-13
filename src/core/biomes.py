"""
Sistema de Biomas y Ambientación para SiKIdle.

Este módulo define los diferentes biomas disponibles en el juego,
sus propiedades visuales, mecánicas especiales y bonificaciones únicas.
Cada bioma proporciona una experiencia de juego diferenciada.

Autor: GitHub Copilot
Fecha: 04 de agosto de 2025
"""

from enum import Enum
from dataclasses import dataclass
from typing import Dict, Tuple, List, Optional
from kivy.utils import get_color_from_hex


class BiomeType(Enum):
	"""
	Enumeración de todos los tipos de biomas disponibles en el juego.
	
	Cada bioma tiene características únicas que afectan:
	- Bonificaciones de combate del jugador
	- Probabilidades de loot específicas
	- Efectos visuales y ambientación
	- Tipos de enemigos predominantes
	"""
	ENCHANTED_FOREST = "enchanted_forest"		# Bosque Encantado
	DEEP_CAVES = "deep_caves"					# Cuevas Profundas
	ANCIENT_RUINS = "ancient_ruins"				# Ruinas Antiguas
	ORC_FORTRESS = "orc_fortress"				# Fortaleza Orc
	SHADOW_DIMENSION = "shadow_dimension"		# Dimensión Sombría


@dataclass
class BiomeVisualData:
	"""
	Datos visuales y de ambientación para un bioma específico.
	
	Attributes:
		primary_color: Color principal del bioma (hex)
		secondary_color: Color secundario para efectos (hex)
		accent_color: Color de acentos y efectos especiales (hex)
		background_gradient: Tupla de colores para gradiente de fondo
		particle_color: Color de las partículas ambientales
		lighting_intensity: Intensidad de la iluminación (0.0-1.0)
		ambient_description: Descripción textual del ambiente
	"""
	primary_color: str
	secondary_color: str
	accent_color: str
	background_gradient: Tuple[str, str]
	particle_color: str
	lighting_intensity: float
	ambient_description: str


@dataclass
class BiomeMechanics:
	"""
	Mecánicas y bonificaciones específicas de un bioma.
	
	Attributes:
		attack_speed_bonus: Multiplicador de velocidad de ataque
		defense_bonus: Multiplicador de defensa del jugador
		experience_bonus: Multiplicador de experiencia ganada
		damage_bonus: Multiplicador de daño del jugador
		loot_rarity_bonus: Bonus a probabilidad de loot raro (%)
		special_loot_types: Tipos de loot únicos del bioma
		environmental_effects: Efectos especiales del ambiente
	"""
	attack_speed_bonus: float		# Multiplicador (1.0 = sin bonus)
	defense_bonus: float			# Multiplicador (1.0 = sin bonus)
	experience_bonus: float			# Multiplicador (1.0 = sin bonus)
	damage_bonus: float				# Multiplicador (1.0 = sin bonus)
	loot_rarity_bonus: float		# Porcentaje adicional (0.15 = +15%)
	special_loot_types: List[str]	# Tipos de loot únicos
	environmental_effects: List[str] # Efectos ambientales activos


@dataclass
class BiomeData:
	"""
	Datos completos de un bioma, incluyendo visuales y mecánicas.
	
	Attributes:
		biome_type: Tipo de bioma
		name: Nombre mostrado al jugador
		description: Descripción detallada del bioma
		visual_data: Información visual y de ambientación
		mechanics: Mecánicas y bonificaciones del bioma
		unlock_level: Nivel requerido para acceder al bioma
		music_theme: Nombre del tema musical del bioma
	"""
	biome_type: BiomeType
	name: str
	description: str
	visual_data: BiomeVisualData
	mechanics: BiomeMechanics
	unlock_level: int
	music_theme: str


class BiomeManager:
	"""
	Gestor principal del sistema de biomas.
	
	Maneja la aplicación de efectos de bioma, cambios visuales
	y la lógica de bonificaciones según el bioma activo.
	"""
	
	def __init__(self):
		"""Inicializa el gestor de biomas con todos los datos predefinidos."""
		self._biome_data: Dict[BiomeType, BiomeData] = {}
		self._current_biome: Optional[BiomeType] = None
		self._initialize_biome_data()
	
	def _initialize_biome_data(self) -> None:
		"""
		Inicializa todos los datos de biomas con sus propiedades específicas.
		
		Define las características visuales, mecánicas y temáticas
		de cada bioma disponible en el juego.
		"""
		# Bosque Encantado - Bioma inicial y equilibrado
		self._biome_data[BiomeType.ENCHANTED_FOREST] = BiomeData(
			biome_type=BiomeType.ENCHANTED_FOREST,
			name="Bosque Encantado",
			description="Un misterioso bosque lleno de criaturas mágicas y vegetación exuberante. "
					   "La magia natural del lugar acelera tus reflejos en combate.",
			visual_data=BiomeVisualData(
				primary_color="#2d5016",		# Verde bosque oscuro
				secondary_color="#4a7c59",		# Verde medio
				accent_color="#7fb069",			# Verde claro
				background_gradient=("#1a3409", "#2d5016"),
				particle_color="#90ee90",		# Partículas verdes brillantes
				lighting_intensity=0.7,
				ambient_description="Rayos de sol filtrados entre hojas, sonidos de criaturas místicas"
			),
			mechanics=BiomeMechanics(
				attack_speed_bonus=1.15,		# +15% velocidad de ataque
				defense_bonus=1.0,				# Sin bonus de defensa
				experience_bonus=1.05,			# +5% experiencia
				damage_bonus=1.0,				# Sin bonus de daño
				loot_rarity_bonus=0.10,			# +10% loot raro
				special_loot_types=["hierbas_medicinales", "madera_encantada", "esencias_naturales"],
				environmental_effects=["regeneracion_natural", "velocidad_mejorada"]
			),
			unlock_level=1,
			music_theme="forest_ambience"
		)
		
		# Cuevas Profundas - Enfoque defensivo
		self._biome_data[BiomeType.DEEP_CAVES] = BiomeData(
			biome_type=BiomeType.DEEP_CAVES,
			name="Cuevas Profundas",
			description="Túneles subterráneos llenos de cristales y formaciones rocosas. "
					   "La dureza del entorno fortalece tu resistencia natural.",
			visual_data=BiomeVisualData(
				primary_color="#2c1810",		# Marrón oscuro
				secondary_color="#4a3728",		# Marrón medio
				accent_color="#8b4513",			# Marrón rojizo
				background_gradient=("#1a0f08", "#2c1810"),
				particle_color="#daa520",		# Partículas doradas (cristales)
				lighting_intensity=0.4,
				ambient_description="Eco de gotas, brillo de cristales, aire húmedo y fresco"
			),
			mechanics=BiomeMechanics(
				attack_speed_bonus=0.95,		# -5% velocidad de ataque
				defense_bonus=1.20,				# +20% defensa
				experience_bonus=1.0,			# Sin bonus de experiencia
				damage_bonus=1.0,				# Sin bonus de daño
				loot_rarity_bonus=0.15,			# +15% loot raro (cristales/gemas)
				special_loot_types=["cristales_energia", "gemas_preciosas", "minerales_raros"],
				environmental_effects=["resistencia_mejorada", "vision_cristalina"]
			),
			unlock_level=11,
			music_theme="cave_echoes"
		)
		
		# Ruinas Antiguas - Enfoque en experiencia
		self._biome_data[BiomeType.ANCIENT_RUINS] = BiomeData(
			biome_type=BiomeType.ANCIENT_RUINS,
			name="Ruinas Antiguas",
			description="Restos de una civilización perdida llenos de conocimiento arcano. "
					   "Los secretos del pasado aceleran tu aprendizaje.",
			visual_data=BiomeVisualData(
				primary_color="#3c3c3c",		# Gris piedra
				secondary_color="#696969",		# Gris medio
				accent_color="#b8860b",			# Dorado antiguo
				background_gradient=("#2f2f2f", "#3c3c3c"),
				particle_color="#ffd700",		# Partículas doradas (magia antigua)
				lighting_intensity=0.5,
				ambient_description="Viento entre ruinas, susurros arcanos, destellos de magia antigua"
			),
			mechanics=BiomeMechanics(
				attack_speed_bonus=1.0,			# Sin bonus de velocidad
				defense_bonus=1.05,				# +5% defensa
				experience_bonus=1.25,			# +25% experiencia
				damage_bonus=1.10,				# +10% daño (conocimiento arcano)
				loot_rarity_bonus=0.20,			# +20% loot raro (artefactos)
				special_loot_types=["pergaminos_antiguos", "artefactos_arcanos", "reliquias_perdidas"],
				environmental_effects=["sabiduria_antigua", "poder_arcano"]
			),
			unlock_level=26,
			music_theme="ancient_mysteries"
		)
		
		# Fortaleza Orc - Enfoque en daño
		self._biome_data[BiomeType.ORC_FORTRESS] = BiomeData(
			biome_type=BiomeType.ORC_FORTRESS,
			name="Fortaleza Orc",
			description="Una fortaleza militar brutal donde solo los más fuertes sobreviven. "
					   "El ambiente de guerra intensifica tu ferocidad en combate.",
			visual_data=BiomeVisualData(
				primary_color="#4a0e0e",		# Rojo sangre oscuro
				secondary_color="#8b0000",		# Rojo sangre
				accent_color="#ff6347",			# Rojo tomate
				background_gradient=("#2f0606", "#4a0e0e"),
				particle_color="#ff4500",		# Partículas naranjas (fuego)
				lighting_intensity=0.6,
				ambient_description="Gritos de guerra, metal chocando, humo de forjas ardientes"
			),
			mechanics=BiomeMechanics(
				attack_speed_bonus=1.10,		# +10% velocidad de ataque
				defense_bonus=0.95,				# -5% defensa
				experience_bonus=1.10,			# +10% experiencia
				damage_bonus=1.30,				# +30% daño
				loot_rarity_bonus=0.12,			# +12% loot raro
				special_loot_types=["armas_guerra", "armaduras_batalla", "trofeos_combate"],
				environmental_effects=["furia_batalla", "espiritu_guerrero"]
			),
			unlock_level=51,
			music_theme="war_drums"
		)
		
		# Dimensión Sombría - Bioma end-game con bonificaciones variables
		self._biome_data[BiomeType.SHADOW_DIMENSION] = BiomeData(
			biome_type=BiomeType.SHADOW_DIMENSION,
			name="Dimensión Sombría",
			description="Un plano de existencia alterado donde las leyes de la realidad se tuercen. "
					   "Aquí todo es posible, pero también extremadamente peligroso.",
			visual_data=BiomeVisualData(
				primary_color="#1a0033",		# Púrpura muy oscuro
				secondary_color="#4b0082",		# Índigo
				accent_color="#9400d3",			# Violeta
				background_gradient=("#0a0015", "#1a0033"),
				particle_color="#dda0dd",		# Partículas púrpura brillante
				lighting_intensity=0.3,
				ambient_description="Susurros dimensionales, energía crepitante, realidad distorsionada"
			),
			mechanics=BiomeMechanics(
				attack_speed_bonus=1.20,		# +20% velocidad de ataque
				defense_bonus=1.15,				# +15% defensa
				experience_bonus=1.50,			# +50% experiencia
				damage_bonus=1.25,				# +25% daño
				loot_rarity_bonus=0.35,			# +35% loot raro
				special_loot_types=["fragmentos_dimension", "energia_sombria", "artefactos_legendarios"],
				environmental_effects=["distorsion_temporal", "poder_dimensional", "caos_benefico"]
			),
			unlock_level=76,
			music_theme="dimensional_chaos"
		)
	
	def get_biome_data(self, biome_type: BiomeType) -> Optional[BiomeData]:
		"""
		Obtiene los datos completos de un bioma específico.
		
		Args:
			biome_type: Tipo de bioma a consultar
			
		Returns:
			BiomeData del bioma solicitado o None si no existe
		"""
		return self._biome_data.get(biome_type)
	
	def get_all_biomes(self) -> Dict[BiomeType, BiomeData]:
		"""
		Obtiene todos los biomas disponibles en el juego.
		
		Returns:
			Diccionario con todos los biomas y sus datos
		"""
		return self._biome_data.copy()
	
	def set_current_biome(self, biome_type: Optional[BiomeType]) -> bool:
		"""
		Establece el bioma activo actual.
		
		Args:
			biome_type: Tipo de bioma a activar o None para limpiar
			
		Returns:
			True si el bioma se activó correctamente, False si no existe
		"""
		if biome_type is None:
			self._current_biome = None
			return True
		
		if biome_type in self._biome_data:
			self._current_biome = biome_type
			return True
		return False
	
	def get_current_biome(self) -> Optional[BiomeType]:
		"""
		Obtiene el bioma actualmente activo.
		
		Returns:
			BiomeType activo o None si no hay bioma activo
		"""
		return self._current_biome
	
	def get_current_biome_data(self) -> Optional[BiomeData]:
		"""
		Obtiene los datos del bioma actualmente activo.
		
		Returns:
			BiomeData del bioma activo o None si no hay bioma activo
		"""
		if self._current_biome:
			return self._biome_data.get(self._current_biome)
		return None
	
	def get_combat_bonuses(self, biome_type: Optional[BiomeType] = None) -> Dict[str, float]:
		"""
		Obtiene las bonificaciones de combate del bioma especificado o activo.
		
		Args:
			biome_type: Bioma específico o None para usar el activo
			
		Returns:
			Diccionario con las bonificaciones aplicables al combate
		"""
		target_biome = biome_type or self._current_biome
		if not target_biome or target_biome not in self._biome_data:
			# Sin bioma activo, devolver bonificaciones neutras
			return {
				"attack_speed": 1.0,
				"defense": 1.0,
				"damage": 1.0,
				"experience": 1.0,
				"loot_rarity": 0.0
			}
		
		mechanics = self._biome_data[target_biome].mechanics
		return {
			"attack_speed": mechanics.attack_speed_bonus,
			"defense": mechanics.defense_bonus,
			"damage": mechanics.damage_bonus,
			"experience": mechanics.experience_bonus,
			"loot_rarity": mechanics.loot_rarity_bonus
		}
	
	def get_visual_theme(self, biome_type: Optional[BiomeType] = None) -> Optional[BiomeVisualData]:
		"""
		Obtiene los datos visuales del bioma especificado o activo.
		
		Args:
			biome_type: Bioma específico o None para usar el activo
			
		Returns:
			BiomeVisualData para aplicar tema visual o None
		"""
		target_biome = biome_type or self._current_biome
		if not target_biome or target_biome not in self._biome_data:
			return None
		
		return self._biome_data[target_biome].visual_data
	
	def get_kivy_colors(self, biome_type: Optional[BiomeType] = None) -> Dict[str, Tuple[float, float, float, float]]:
		"""
		Obtiene los colores del bioma en formato Kivy (RGBA normalizado).
		
		Args:
			biome_type: Bioma específico o None para usar el activo
			
		Returns:
			Diccionario con colores en formato Kivy (RGBA)
		"""
		visual_data = self.get_visual_theme(biome_type)
		if not visual_data:
			# Colores por defecto si no hay bioma activo
			return {
				"primary": (0.3, 0.3, 0.3, 1.0),
				"secondary": (0.5, 0.5, 0.5, 1.0),
				"accent": (0.7, 0.7, 0.7, 1.0),
				"particle": (1.0, 1.0, 1.0, 1.0)
			}
		
		return {
			"primary": get_color_from_hex(visual_data.primary_color),
			"secondary": get_color_from_hex(visual_data.secondary_color),
			"accent": get_color_from_hex(visual_data.accent_color),
			"particle": get_color_from_hex(visual_data.particle_color)
		}
	
	def is_biome_unlocked(self, biome_type: BiomeType, player_level: int) -> bool:
		"""
		Verifica si un bioma está desbloqueado para el nivel del jugador.
		
		Args:
			biome_type: Tipo de bioma a verificar
			player_level: Nivel actual del jugador
			
		Returns:
			True si el bioma está desbloqueado, False en caso contrario
		"""
		biome_data = self.get_biome_data(biome_type)
		if not biome_data:
			return False
		
		return player_level >= biome_data.unlock_level
	
	def get_unlocked_biomes(self, player_level: int) -> List[BiomeType]:
		"""
		Obtiene la lista de biomas desbloqueados para el nivel del jugador.
		
		Args:
			player_level: Nivel actual del jugador
			
		Returns:
			Lista de BiomeType desbloqueados, ordenados por nivel requerido
		"""
		unlocked = []
		for biome_type, biome_data in self._biome_data.items():
			if player_level >= biome_data.unlock_level:
				unlocked.append(biome_type)
		
		# Ordenar por nivel de desbloqueo
		unlocked.sort(key=lambda bt: self._biome_data[bt].unlock_level)
		return unlocked
	
	def get_biome_description_with_bonuses(self, biome_type: BiomeType) -> str:
		"""
		Obtiene una descripción completa del bioma incluyendo sus bonificaciones.
		
		Args:
			biome_type: Tipo de bioma a describir
			
		Returns:
			Descripción detallada con bonificaciones formateadas
		"""
		biome_data = self.get_biome_data(biome_type)
		if not biome_data:
			return "Bioma desconocido"
		
		description = biome_data.description + "\n\n"
		mechanics = biome_data.mechanics
		
		description += "🎯 Bonificaciones activas:\n"
		
		if mechanics.attack_speed_bonus != 1.0:
			bonus_pct = int((mechanics.attack_speed_bonus - 1.0) * 100)
			sign = "+" if bonus_pct > 0 else ""
			description += f"⚡ Velocidad de ataque: {sign}{bonus_pct}%\n"
		
		if mechanics.defense_bonus != 1.0:
			bonus_pct = int((mechanics.defense_bonus - 1.0) * 100)
			sign = "+" if bonus_pct > 0 else ""
			description += f"🛡️ Defensa: {sign}{bonus_pct}%\n"
		
		if mechanics.damage_bonus != 1.0:
			bonus_pct = int((mechanics.damage_bonus - 1.0) * 100)
			sign = "+" if bonus_pct > 0 else ""
			description += f"⚔️ Daño: {sign}{bonus_pct}%\n"
		
		if mechanics.experience_bonus != 1.0:
			bonus_pct = int((mechanics.experience_bonus - 1.0) * 100)
			sign = "+" if bonus_pct > 0 else ""
			description += f"📈 Experiencia: {sign}{bonus_pct}%\n"
		
		if mechanics.loot_rarity_bonus > 0:
			bonus_pct = int(mechanics.loot_rarity_bonus * 100)
			description += f"💎 Loot raro: +{bonus_pct}%\n"
		
		return description
