"""
Sistema de enemigos para SiKIdle.
Define los diferentes tipos de enemigos, sus estadísticas y comportamientos.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional
import random

from core.combat import CombatStats, Enemy


class EnemyType(Enum):
	"""Tipos de enemigos disponibles en el juego."""

	# Bosque Encantado (Nivel 1-10)
	GOBLIN = "goblin"
	WOLF = "wolf"
	WILD_BOAR = "wild_boar"
	FOREST_SPRITE = "forest_sprite"

	# Cuevas Profundas (Nivel 11-25)
	CAVE_BAT = "cave_bat"
	GIANT_SPIDER = "giant_spider"
	CAVE_TROLL = "cave_troll"
	CRYSTAL_GOLEM = "crystal_golem"

	# Ruinas Antiguas (Nivel 26-50)
	SKELETON_WARRIOR = "skeleton_warrior"
	ANCIENT_SPIRIT = "ancient_spirit"
	STONE_GUARDIAN = "stone_guardian"
	LICH = "lich"

	# Fortaleza Orc (Nivel 51-75)
	ORC_GRUNT = "orc_grunt"
	ORC_SHAMAN = "orc_shaman"
	ORC_WARLORD = "orc_warlord"
	ORC_CHIEFTAIN = "orc_chieftain"

	# Dimensión Sombría (Nivel 76+)
	SHADOW_DEMON = "shadow_demon"
	VOID_WALKER = "void_walker"
	ANCIENT_DRAGON = "ancient_dragon"
	DIMENSIONAL_LORD = "dimensional_lord"


@dataclass
class EnemyData:
	"""Datos base de un tipo de enemigo."""

	name: str
	enemy_type: EnemyType
	base_level: int
	min_level: int
	max_level: int

	# Stats base (escalados por nivel)
	base_hp: int
	base_attack: int
	base_defense: int
	base_speed: float

	# Propiedades especiales
	critical_chance: float = 0.05
	critical_multiplier: float = 1.8

	# Recompensas base (escaladas por nivel)
	base_experience: int = 10
	base_gold: int = 5

	# Propiedades de loot
	loot_chance: float = 0.15  # 15% base de drop
	rare_loot_chance: float = 0.03  # 3% de loot raro

	# Descripción y características
	description: str = ""
	biome: str = "generic"
	special_abilities: List[str] = field(default_factory=list)


class EnemyFactory:
	"""Fábrica para crear enemigos con estadísticas escaladas."""

	# Base de datos de enemigos
	ENEMY_DATABASE: Dict[EnemyType, EnemyData] = {
		# Bosque Encantado
		EnemyType.GOBLIN: EnemyData(
			name="Goblin Salvaje",
			enemy_type=EnemyType.GOBLIN,
			base_level=1,
			min_level=1,
			max_level=8,
			base_hp=25,
			base_attack=8,
			base_defense=1,
			base_speed=1.2,
			base_experience=12,
			base_gold=8,
			loot_chance=0.20,
			description="Un goblin ágil que ataca rápidamente",
			biome="forest",
			special_abilities=["quick_strike"],
		),
		EnemyType.WOLF: EnemyData(
			name="Lobo del Bosque",
			enemy_type=EnemyType.WOLF,
			base_level=3,
			min_level=2,
			max_level=10,
			base_hp=40,
			base_attack=12,
			base_defense=2,
			base_speed=1.0,
			critical_chance=0.10,
			base_experience=18,
			base_gold=12,
			description="Un lobo feroz con instintos de caza",
			biome="forest",
			special_abilities=["pack_hunter"],
		),
		EnemyType.WILD_BOAR: EnemyData(
			name="Jabalí Furioso",
			enemy_type=EnemyType.WILD_BOAR,
			base_level=5,
			min_level=4,
			max_level=12,
			base_hp=60,
			base_attack=15,
			base_defense=4,
			base_speed=0.8,
			base_experience=25,
			base_gold=15,
			description="Un jabalí resistente con carga devastadora",
			biome="forest",
			special_abilities=["charge_attack"],
		),
		EnemyType.FOREST_SPRITE: EnemyData(
			name="Sprite del Bosque",
			enemy_type=EnemyType.FOREST_SPRITE,
			base_level=8,
			min_level=7,
			max_level=15,
			base_hp=35,
			base_attack=20,
			base_defense=1,
			base_speed=1.5,
			critical_chance=0.15,
			base_experience=35,
			base_gold=25,
			loot_chance=0.30,
			rare_loot_chance=0.08,
			description="Un sprite mágico evasivo con ataques rápidos",
			biome="forest",
			special_abilities=["evasion", "magic_burst"],
		),
		# Cuevas Profundas
		EnemyType.CAVE_BAT: EnemyData(
			name="Murciélago de Cueva",
			enemy_type=EnemyType.CAVE_BAT,
			base_level=12,
			min_level=11,
			max_level=18,
			base_hp=30,
			base_attack=18,
			base_defense=1,
			base_speed=1.8,
			base_experience=20,
			base_gold=15,
			description="Un murciélago veloz que ataca en enjambre",
			biome="caves",
			special_abilities=["swarm_attack"],
		),
		EnemyType.GIANT_SPIDER: EnemyData(
			name="Araña Gigante",
			enemy_type=EnemyType.GIANT_SPIDER,
			base_level=15,
			min_level=13,
			max_level=22,
			base_hp=80,
			base_attack=25,
			base_defense=3,
			base_speed=1.1,
			base_experience=45,
			base_gold=30,
			loot_chance=0.25,
			description="Una araña venenosa con ataques mortales",
			biome="caves",
			special_abilities=["poison_bite", "web_trap"],
		),
		EnemyType.CAVE_TROLL: EnemyData(
			name="Troll de Cueva",
			enemy_type=EnemyType.CAVE_TROLL,
			base_level=20,
			min_level=18,
			max_level=25,
			base_hp=150,
			base_attack=35,
			base_defense=8,
			base_speed=0.7,
			critical_multiplier=2.5,
			base_experience=80,
			base_gold=50,
			description="Un troll masivo con fuerza demoledora",
			biome="caves",
			special_abilities=["heavy_slam", "regeneration"],
		),
		EnemyType.CRYSTAL_GOLEM: EnemyData(
			name="Gólem de Cristal",
			enemy_type=EnemyType.CRYSTAL_GOLEM,
			base_level=25,
			min_level=22,
			max_level=30,
			base_hp=200,
			base_attack=30,
			base_defense=15,
			base_speed=0.6,
			base_experience=120,
			base_gold=80,
			loot_chance=0.40,
			rare_loot_chance=0.15,
			description="Un gólem resistente hecho de cristales mágicos",
			biome="caves",
			special_abilities=["crystal_armor", "reflect_damage"],
		),
		# Ruinas Antiguas
		EnemyType.SKELETON_WARRIOR: EnemyData(
			name="Guerrero Esqueleto",
			enemy_type=EnemyType.SKELETON_WARRIOR,
			base_level=28,
			min_level=26,
			max_level=35,
			base_hp=120,
			base_attack=40,
			base_defense=12,
			base_speed=1.0,
			critical_chance=0.08,
			base_experience=100,
			base_gold=60,
			description="Un guerrero no-muerto con habilidades de combate",
			biome="ruins",
			special_abilities=["undead_resilience", "bone_armor"],
		),
		EnemyType.ANCIENT_SPIRIT: EnemyData(
			name="Espíritu Ancestral",
			enemy_type=EnemyType.ANCIENT_SPIRIT,
			base_level=35,
			min_level=32,
			max_level=42,
			base_hp=100,
			base_attack=50,
			base_defense=5,
			base_speed=1.3,
			critical_chance=0.12,
			base_experience=150,
			base_gold=90,
			loot_chance=0.35,
			description="Un espíritu etéreo con ataques mágicos",
			biome="ruins",
			special_abilities=["phase_shift", "drain_life"],
		),
		EnemyType.STONE_GUARDIAN: EnemyData(
			name="Guardián de Piedra",
			enemy_type=EnemyType.STONE_GUARDIAN,
			base_level=40,
			min_level=38,
			max_level=45,
			base_hp=300,
			base_attack=45,
			base_defense=25,
			base_speed=0.5,
			base_experience=200,
			base_gold=120,
			description="Un guardián ancestral de piedra viviente",
			biome="ruins",
			special_abilities=["stone_skin", "earthquake"],
		),
		EnemyType.LICH: EnemyData(
			name="Lich Ancestral",
			enemy_type=EnemyType.LICH,
			base_level=50,
			min_level=45,
			max_level=55,
			base_hp=250,
			base_attack=65,
			base_defense=15,
			base_speed=1.1,
			critical_chance=0.15,
			critical_multiplier=3.0,
			base_experience=300,
			base_gold=200,
			loot_chance=0.50,
			rare_loot_chance=0.25,
			description="Un mago no-muerto de poder inmensurable",
			biome="ruins",
			special_abilities=["dark_magic", "soul_drain", "death_ray"],
		),
		# Fortaleza Orc
		EnemyType.ORC_GRUNT: EnemyData(
			name="Orco Soldado",
			enemy_type=EnemyType.ORC_GRUNT,
			base_level=52,
			min_level=51,
			max_level=60,
			base_hp=180,
			base_attack=55,
			base_defense=18,
			base_speed=0.9,
			base_experience=180,
			base_gold=100,
			description="Un orco soldado entrenado para la guerra",
			biome="fortress",
			special_abilities=["war_cry", "berserker_rage"],
		),
		EnemyType.ORC_SHAMAN: EnemyData(
			name="Chamán Orco",
			enemy_type=EnemyType.ORC_SHAMAN,
			base_level=58,
			min_level=55,
			max_level=65,
			base_hp=160,
			base_attack=60,
			base_defense=12,
			base_speed=1.2,
			critical_chance=0.10,
			base_experience=220,
			base_gold=130,
			loot_chance=0.40,
			description="Un chamán orco con poderes elementales",
			biome="fortress",
			special_abilities=["elemental_bolt", "healing_totem"],
		),
		EnemyType.ORC_WARLORD: EnemyData(
			name="Señor de la Guerra Orco",
			enemy_type=EnemyType.ORC_WARLORD,
			base_level=65,
			min_level=62,
			max_level=72,
			base_hp=350,
			base_attack=70,
			base_defense=25,
			base_speed=0.8,
			critical_chance=0.12,
			critical_multiplier=2.8,
			base_experience=350,
			base_gold=200,
			description="Un poderoso líder orco con armadura pesada",
			biome="fortress",
			special_abilities=["command_troops", "devastating_blow"],
		),
		EnemyType.ORC_CHIEFTAIN: EnemyData(
			name="Jefe Supremo Orco",
			enemy_type=EnemyType.ORC_CHIEFTAIN,
			base_level=75,
			min_level=70,
			max_level=80,
			base_hp=500,
			base_attack=85,
			base_defense=30,
			base_speed=1.0,
			critical_chance=0.15,
			critical_multiplier=3.5,
			base_experience=500,
			base_gold=350,
			loot_chance=0.60,
			rare_loot_chance=0.30,
			description="El líder supremo de todos los orcos",
			biome="fortress",
			special_abilities=["tribal_fury", "legendary_weapon", "intimidate"],
		),
		# Dimensión Sombría
		EnemyType.SHADOW_DEMON: EnemyData(
			name="Demonio Sombra",
			enemy_type=EnemyType.SHADOW_DEMON,
			base_level=78,
			min_level=76,
			max_level=85,
			base_hp=300,
			base_attack=90,
			base_defense=20,
			base_speed=1.4,
			critical_chance=0.18,
			base_experience=400,
			base_gold=250,
			description="Un demonio de las sombras con velocidad letal",
			biome="shadow_dimension",
			special_abilities=["shadow_strike", "darkness_veil"],
		),
		EnemyType.VOID_WALKER: EnemyData(
			name="Caminante del Vacío",
			enemy_type=EnemyType.VOID_WALKER,
			base_level=85,
			min_level=82,
			max_level=92,
			base_hp=400,
			base_attack=95,
			base_defense=25,
			base_speed=1.1,
			critical_chance=0.15,
			critical_multiplier=4.0,
			base_experience=600,
			base_gold=400,
			loot_chance=0.50,
			description="Una entidad interdimensional de poder cósmico",
			biome="shadow_dimension",
			special_abilities=["void_blast", "dimensional_shift"],
		),
		EnemyType.ANCIENT_DRAGON: EnemyData(
			name="Dragón Ancestral",
			enemy_type=EnemyType.ANCIENT_DRAGON,
			base_level=95,
			min_level=90,
			max_level=105,
			base_hp=800,
			base_attack=120,
			base_defense=40,
			base_speed=0.9,
			critical_chance=0.20,
			critical_multiplier=5.0,
			base_experience=1000,
			base_gold=600,
			loot_chance=0.70,
			rare_loot_chance=0.40,
			description="Un dragón milenario de poder inimaginable",
			biome="shadow_dimension",
			special_abilities=["dragon_breath", "ancient_magic", "fly_attack"],
		),
		EnemyType.DIMENSIONAL_LORD: EnemyData(
			name="Señor Dimensional",
			enemy_type=EnemyType.DIMENSIONAL_LORD,
			base_level=100,
			min_level=95,
			max_level=120,
			base_hp=1200,
			base_attack=150,
			base_defense=50,
			base_speed=1.0,
			critical_chance=0.25,
			critical_multiplier=6.0,
			base_experience=1500,
			base_gold=1000,
			loot_chance=0.80,
			rare_loot_chance=0.50,
			description="El maestro absoluto de la dimensión sombría",
			biome="shadow_dimension",
			special_abilities=["reality_warp", "dimensional_prison", "cosmic_fury"],
		),
	}

	@classmethod
	def create_enemy(cls, enemy_type: EnemyType, level: Optional[int] = None) -> Enemy:
		"""Crea un enemigo del tipo especificado con nivel escalado."""
		if enemy_type not in cls.ENEMY_DATABASE:
			raise ValueError(f"Tipo de enemigo desconocido: {enemy_type}")

		enemy_data = cls.ENEMY_DATABASE[enemy_type]

		# Determinar nivel del enemigo
		if level is None:
			enemy_level = random.randint(enemy_data.min_level, enemy_data.max_level)
		else:
			enemy_level = max(enemy_data.min_level, min(enemy_data.max_level, level))

		# Calcular scaling factor basado en nivel
		level_scale = enemy_level / enemy_data.base_level

		# Escalar estadísticas
		scaled_hp = int(enemy_data.base_hp * level_scale)
		scaled_attack = int(enemy_data.base_attack * level_scale)
		scaled_defense = int(enemy_data.base_defense * level_scale)
		scaled_speed = enemy_data.base_speed * (
			1 + (level_scale - 1) * 0.1
		)  # Scaling más suave para velocidad

		# Escalar recompensas
		scaled_exp = int(enemy_data.base_experience * level_scale * 1.2)  # 20% bonus en exp scaling
		scaled_gold = int(enemy_data.base_gold * level_scale)

		# Crear estadísticas de combate
		combat_stats = CombatStats(
			max_hp=scaled_hp,
			current_hp=scaled_hp,
			attack=scaled_attack,
			defense=scaled_defense,
			speed=scaled_speed,
			critical_chance=enemy_data.critical_chance,
			critical_multiplier=enemy_data.critical_multiplier,
		)

		# Crear enemigo
		enemy = Enemy(
			name=f"{enemy_data.name} (Nv.{enemy_level})",
			level=enemy_level,
			stats=combat_stats,
			experience_reward=scaled_exp,
			gold_reward=scaled_gold,
			enemy_type=enemy_data.enemy_type.value,
			special_abilities=enemy_data.special_abilities.copy(),
		)

		return enemy

	@classmethod
	def get_enemies_for_biome(
		cls, biome: str, count: int = 1, level_range: Optional[tuple] = None
	) -> List[Enemy]:
		"""Obtiene enemigos aleatorios de un bioma específico."""
		biome_enemies = [
			enemy_type for enemy_type, data in cls.ENEMY_DATABASE.items() if data.biome == biome
		]

		if not biome_enemies:
			# Fallback a enemigos genéricos
			biome_enemies = [EnemyType.GOBLIN, EnemyType.WOLF]

		enemies = []
		for _ in range(count):
			enemy_type = random.choice(biome_enemies)

			if level_range:
				min_level, max_level = level_range
				enemy_level = random.randint(min_level, max_level)
				enemy = cls.create_enemy(enemy_type, enemy_level)
			else:
				enemy = cls.create_enemy(enemy_type)

			enemies.append(enemy)

		return enemies

	@classmethod
	def get_boss_enemy(cls, biome: str, level: int) -> Enemy:
		"""Crea un enemigo boss especial para un bioma."""
		boss_types = {
			"forest": EnemyType.FOREST_SPRITE,
			"caves": EnemyType.CRYSTAL_GOLEM,
			"ruins": EnemyType.LICH,
			"fortress": EnemyType.ORC_CHIEFTAIN,
			"shadow_dimension": EnemyType.DIMENSIONAL_LORD,
		}

		boss_type = boss_types.get(biome, EnemyType.GOBLIN)
		boss = cls.create_enemy(boss_type, level)

		# Potenciar al boss
		boss.name = f"BOSS: {boss.name}"
		boss.stats.max_hp = int(boss.stats.max_hp * 2.5)
		boss.stats.current_hp = boss.stats.max_hp
		boss.stats.attack = int(boss.stats.attack * 1.5)
		boss.stats.defense = int(boss.stats.defense * 1.8)
		boss.experience_reward = int(boss.experience_reward * 3)
		boss.gold_reward = int(boss.gold_reward * 2.5)

		return boss

	@classmethod
	def get_enemy_info(cls, enemy_type: EnemyType) -> EnemyData:
		"""Obtiene la información base de un tipo de enemigo."""
		return cls.ENEMY_DATABASE.get(enemy_type)
