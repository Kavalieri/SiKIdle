"""
Sistema de combate central para SiKIdle.
Gestiona el combate automático entre jugador y enemigos con estadísticas RPG.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, TYPE_CHECKING
import time
import random

if TYPE_CHECKING:
	from core.player_stats import PlayerStatsManager


class DamageType(Enum):
	"""Tipos de daño en el combate."""

	PHYSICAL = "physical"
	MAGICAL = "magical"
	TRUE = "true"  # Daño que ignora defensa


@dataclass
class CombatStats:
	"""Estadísticas base de combate para jugador y enemigos."""

	max_hp: int
	current_hp: int
	attack: int
	defense: int
	speed: float  # Ataques por segundo
	critical_chance: float = 0.05  # 5% base
	critical_multiplier: float = 2.0  # x2 daño en crítico

	def __post_init__(self):
		"""Valida que la salud actual no exceda la máxima."""
		if self.current_hp > self.max_hp:
			self.current_hp = self.max_hp

	def is_alive(self) -> bool:
		"""Verifica si la entidad está viva."""
		return self.current_hp > 0

	def take_damage(self, damage: int) -> int:
		"""Aplica daño y retorna el daño real recibido."""
		actual_damage = max(1, damage - self.defense)  # Mínimo 1 de daño
		self.current_hp = max(0, self.current_hp - actual_damage)
		return actual_damage

	def heal(self, amount: int) -> int:
		"""Cura y retorna la cantidad curada real."""
		old_hp = self.current_hp
		self.current_hp = min(self.max_hp, self.current_hp + amount)
		return self.current_hp - old_hp

	def get_hp_percentage(self) -> float:
		"""Retorna el porcentaje de salud actual."""
		return self.current_hp / self.max_hp if self.max_hp > 0 else 0.0


@dataclass
class Player:
	"""Jugador con sistema avanzado de estadísticas y progresión."""
	
	# Referencia al sistema de estadísticas completo
	stats_manager: Optional['PlayerStatsManager'] = None
	
	# Stats base para casos donde no hay PlayerStatsManager (retrocompatibilidad)
	base_stats: CombatStats = field(
		default_factory=lambda: CombatStats(
			max_hp=100,
			current_hp=100,
			attack=10,
			defense=2,
			speed=1.0,
			critical_chance=0.05,
			critical_multiplier=2.0,
		)
	)
	
	# Bonificaciones de equipamiento (aplicadas desde EquipmentIntegration)
	equipment_bonuses: dict = field(default_factory=dict)
	
	def initialize_stats_manager(self):
		"""Inicializa el gestor de estadísticas si no existe."""
		if self.stats_manager is None:
			from core.player_stats import PlayerStatsManager
			self.stats_manager = PlayerStatsManager()
			# Actualizar bonificaciones de equipamiento
			self.stats_manager.update_equipment_bonuses(self.equipment_bonuses)
	
	def get_level(self) -> int:
		"""Obtiene el nivel actual del jugador."""
		if self.stats_manager:
			return self.stats_manager.level_system.level
		return 1  # Valor por defecto
	
	def get_experience_for_next_level(self) -> int:
		"""Calcula la experiencia necesaria para el siguiente nivel."""
		if self.stats_manager:
			return self.stats_manager.level_system.get_experience_for_next_level()
		return 100 + (self.get_level() - 1) * 50  # Fórmula legacy
	
	def can_level_up(self) -> bool:
		"""Verifica si puede subir de nivel."""
		if self.stats_manager:
			return self.stats_manager.level_system.can_level_up()
		return False
	
	def get_effective_stats(self, biome_bonuses: Optional[dict] = None) -> CombatStats:
		"""Calcula las estadísticas finales con bonificaciones de equipamiento y bioma."""
		if self.stats_manager:
			# Usar el sistema avanzado de estadísticas con bonificaciones de bioma
			return self.stats_manager.get_effective_combat_stats(self.base_stats.current_hp, biome_bonuses)
		
		# Sistema legacy para retrocompatibilidad
		damage_mult = self.equipment_bonuses.get("damage_multiplier", 1.0)
		click_mult = self.equipment_bonuses.get("click_multiplier", 1.0)
		
		# Aplicar bonificaciones de bioma al sistema legacy
		biome_damage_mult = 1.0
		biome_defense_mult = 1.0
		biome_speed_mult = 1.0
		
		if biome_bonuses:
			biome_damage_mult = biome_bonuses.get("damage", 1.0)
			biome_defense_mult = biome_bonuses.get("defense", 1.0)
			biome_speed_mult = biome_bonuses.get("attack_speed", 1.0)
		
		effective_attack = int(self.base_stats.attack * damage_mult * click_mult * biome_damage_mult)
		effective_defense = int(self.base_stats.defense * biome_defense_mult)
		effective_speed = self.base_stats.speed * click_mult * biome_speed_mult
		
		return CombatStats(
			max_hp=self.base_stats.max_hp,
			current_hp=self.base_stats.current_hp,
			attack=effective_attack,
			defense=effective_defense,
			speed=effective_speed,
			critical_chance=min(0.95, self.base_stats.critical_chance),
			critical_multiplier=self.base_stats.critical_multiplier,
		)
	
	def add_experience(self, amount: int) -> int:
		"""Añade experiencia y retorna niveles ganados."""
		if self.stats_manager:
			levels_gained = self.stats_manager.add_experience(amount)
			return len(levels_gained)
		
		# Sistema legacy - no implementado
		return 0
	
	def update_equipment_bonuses(self, bonuses: dict):
		"""Actualiza las bonificaciones de equipamiento."""
		self.equipment_bonuses = bonuses.copy()
		if self.stats_manager:
			self.stats_manager.update_equipment_bonuses(bonuses)
	
	def get_player_info(self) -> dict:
		"""Retorna información completa del jugador."""
		if self.stats_manager:
			return self.stats_manager.get_player_info()
		
		# Información básica sin sistema avanzado
		return {
			'level': self.get_level(),
			'experience': {'current': 0, 'to_next_level': 0, 'total': 0, 'progress': 0.0},
			'attributes': {'strength': 10, 'agility': 10, 'intelligence': 10, 'vitality': 10, 'available_points': 0},
			'combat_stats': {
				'max_hp': self.base_stats.max_hp,
				'attack': self.base_stats.attack,
				'defense': self.base_stats.defense,
				'speed': self.base_stats.speed,
				'critical_chance': self.base_stats.critical_chance,
				'critical_multiplier': self.base_stats.critical_multiplier
			},
			'statistics': {
				'enemies_defeated': 0,
				'damage_dealt': 0,
				'critical_hits': 0,
				'items_found': 0,
				'current_streak': 0,
				'longest_streak': 0
			}
		}


@dataclass
class Enemy:
	"""Enemigo con estadísticas y propiedades."""

	name: str
	level: int
	stats: CombatStats
	experience_reward: int
	gold_reward: int
	enemy_type: str = "generic"
	special_abilities: list = field(default_factory=list)

	def calculate_damage_to_player(self, player_stats: CombatStats) -> tuple[int, bool]:
		"""Calcula el daño que este enemigo hace al jugador."""
		base_damage = self.stats.attack

		# Probabilidad de crítico
		is_critical = random.random() < self.stats.critical_chance
		if is_critical:
			base_damage = int(base_damage * self.stats.critical_multiplier)

		# Aplicar defensa del jugador
		final_damage = max(1, base_damage - player_stats.defense)

		return final_damage, is_critical


class CombatState(Enum):
	"""Estados posibles del combate."""

	FIGHTING = "fighting"
	PLAYER_VICTORY = "player_victory"
	PLAYER_DEFEATED = "player_defeated"
	NO_COMBAT = "no_combat"


@dataclass
class CombatResult:
	"""Resultado de un combate completado."""

	state: CombatState
	experience_gained: int = 0
	gold_gained: int = 0
	enemy_defeated: Optional[str] = None
	damage_dealt: int = 0
	damage_received: int = 0
	time_elapsed: float = 0.0


class CombatManager:
	"""Gestiona el combate automático entre jugador y enemigos."""

	def __init__(self, player: "Player"):
		"""
		Inicializa el gestor de combate.
		
		Args:
			player: Instancia del jugador
		"""
		self.player = player
		self.current_enemy: Optional[Enemy] = None
		self.combat_state = CombatState.NO_COMBAT
		self.combat_start_time = 0.0
		self.last_player_attack = 0.0
		self.last_enemy_attack = 0.0
		
		# Bonificaciones de bioma aplicadas
		self.biome_bonuses: Optional[dict] = None

		# Estadísticas del combate actual
		self.total_damage_dealt = 0
		self.total_damage_received = 0

		# Regeneración automática del jugador
		self.last_regen_time = 0.0
		self.regen_rate = 0.02  # 2% de salud máxima por segundo
		
		# Callback para registrar eventos de combate
		self.on_enemy_defeated_callback = None

	def set_enemy_defeat_callback(self, callback):
		"""Establece callback para cuando se derrota un enemigo."""
		self.on_enemy_defeated_callback = callback

	def start_combat(self, enemy: Enemy) -> None:
		"""Inicia un combate contra un enemigo."""
		self.current_enemy = enemy
		self.combat_state = CombatState.FIGHTING
		self.combat_start_time = time.time()
		self.last_player_attack = time.time()
		self.last_enemy_attack = time.time()
		self.total_damage_dealt = 0
		self.total_damage_received = 0

		print(f"¡Combate iniciado contra {enemy.name} (Nivel {enemy.level})!")
	
	def set_biome_bonuses(self, bonuses: Optional[dict]) -> None:
		"""Configura las bonificaciones de bioma para el combate."""
		self.biome_bonuses = bonuses

	def update_combat(self, delta_time: float) -> Optional[CombatResult]:
		"""Actualiza el combate automático. Retorna resultado si el combate termina."""
		if self.combat_state != CombatState.FIGHTING or not self.current_enemy:
			return None

		current_time = time.time()

		# Regeneración automática del jugador fuera de combate
		self._update_player_regeneration(current_time)

		# Verificar si es momento de que el jugador ataque
		player_stats = self.player.get_effective_stats(self.biome_bonuses)
		player_attack_interval = 1.0 / player_stats.speed

		if current_time - self.last_player_attack >= player_attack_interval:
			self._player_attack()
			self.last_player_attack = current_time

		# Verificar si es momento de que el enemigo ataque
		enemy_attack_interval = 1.0 / self.current_enemy.stats.speed

		if current_time - self.last_enemy_attack >= enemy_attack_interval:
			self._enemy_attack()
			self.last_enemy_attack = current_time

		# Verificar condiciones de fin de combate
		return self._check_combat_end()

	def _player_attack(self) -> None:
		"""Ejecuta un ataque del jugador al enemigo."""
		if not self.current_enemy or not self.current_enemy.stats.is_alive():
			return

		player_stats = self.player.get_effective_stats(self.biome_bonuses)
		base_damage = player_stats.attack

		# Calcular crítico
		is_critical = random.random() < player_stats.critical_chance
		if is_critical:
			base_damage = int(base_damage * player_stats.critical_multiplier)

		# Aplicar daño al enemigo
		damage_dealt = self.current_enemy.stats.take_damage(base_damage)

		# Registrar estadísticas en PlayerStatsManager si está disponible
		if self.player.stats_manager:
			self.player.stats_manager.statistics.add_damage_dealt(damage_dealt)
			if is_critical:
				print(f"¡CRÍTICO! Haces {damage_dealt} de daño")
		
		self.total_damage_dealt += damage_dealt
		self.total_damage_dealt += damage_dealt

		crit_text = " ¡CRÍTICO!" if is_critical else ""
		print(f"Jugador ataca por {damage_dealt} de daño{crit_text}")

	def _enemy_attack(self) -> None:
		"""Ejecuta un ataque del enemigo al jugador."""
		if not self.current_enemy or not self.current_enemy.stats.is_alive():
			return

		player_stats = self.player.get_effective_stats(self.biome_bonuses)
		damage_dealt, is_critical = self.current_enemy.calculate_damage_to_player(player_stats)

		# Aplicar daño al jugador
		actual_damage = self.player.base_stats.take_damage(damage_dealt)
		self.total_damage_received += actual_damage

		crit_text = " ¡CRÍTICO!" if is_critical else ""
		print(f"{self.current_enemy.name} ataca por {actual_damage} de daño{crit_text}")

	def _update_player_regeneration(self, current_time: float) -> None:
		"""Actualiza la regeneración pasiva del jugador."""
		if current_time - self.last_regen_time >= 1.0:  # Cada segundo
			player_stats = self.player.base_stats
			if player_stats.current_hp < player_stats.max_hp:
				regen_amount = max(1, int(player_stats.max_hp * self.regen_rate))
				healed = player_stats.heal(regen_amount)
				if healed > 0:
					print(f"Jugador regenera {healed} HP")

			self.last_regen_time = current_time

	def _check_combat_end(self) -> Optional[CombatResult]:
		"""Verifica si el combate ha terminado y retorna el resultado."""
		current_time = time.time()
		time_elapsed = current_time - self.combat_start_time

		if not self.current_enemy:
			return None

		# Victoria del jugador
		if not self.current_enemy.stats.is_alive():
			exp_gained = self.current_enemy.experience_reward
			gold_gained = self.current_enemy.gold_reward

			# Registrar enemigo derrotado en estadísticas
			if self.player.stats_manager:
				was_critical = random.random() < 0.1  # 10% chance para registro de crítico
				self.player.stats_manager.statistics.add_enemy_defeated(was_critical)

			# Añadir experiencia al jugador
			levels_gained = self.player.add_experience(exp_gained)
			if levels_gained > 0:
				level = self.player.get_level()
				print(f"¡Nivel subido! Ahora eres nivel {level}")
			
			# Llamar callback para registrar derrota de enemigo
			if self.on_enemy_defeated_callback:
				try:
					# Determinar si era un boss (enemigos de nivel muy alto o con nombre especial)
					is_boss = (self.current_enemy.level > 50 or 
							 any(boss_keyword in self.current_enemy.name.lower() 
								 for boss_keyword in ['boss', 'chief', 'lord', 'king', 'dragon', 'lich']))
					
					self.on_enemy_defeated_callback(
						enemy_type=self.current_enemy.name,
						enemy_level=self.current_enemy.level,
						is_boss=is_boss
					)
				except Exception as e:
					print(f"Error en callback de derrota de enemigo: {e}")

			result = CombatResult(
				state=CombatState.PLAYER_VICTORY,
				experience_gained=exp_gained,
				gold_gained=gold_gained,
				enemy_defeated=self.current_enemy.name,
				damage_dealt=self.total_damage_dealt,
				damage_received=self.total_damage_received,
				time_elapsed=time_elapsed,
			)

			print(f"¡Victoria! Ganaste {exp_gained} XP y {gold_gained} oro")
			self._end_combat()
			return result

		# Derrota del jugador
		if not self.player.base_stats.is_alive():
			# Resetear racha de combate
			if self.player.stats_manager:
				self.player.stats_manager.statistics.reset_combat_streak()
			
			result = CombatResult(
				state=CombatState.PLAYER_DEFEATED,
				damage_dealt=self.total_damage_dealt,
				damage_received=self.total_damage_received,
				time_elapsed=time_elapsed,
			)

			print("¡Has sido derrotado!")
			self._handle_player_defeat()
			return result

		return None

	def _end_combat(self) -> None:
		"""Finaliza el combate actual."""
		self.current_enemy = None
		self.combat_state = CombatState.NO_COMBAT
		self.total_damage_dealt = 0
		self.total_damage_received = 0

	def _handle_player_defeat(self) -> None:
		"""Maneja la derrota del jugador."""
		# En idle games, normalmente no hay penalización severa por muerte
		# Restaurar algo de salud para permitir continuar
		self.player.base_stats.current_hp = max(1, self.player.base_stats.max_hp // 4)
		self.combat_state = CombatState.NO_COMBAT
		self.current_enemy = None

		print("Te has recuperado con 25% de salud...")

	def get_combat_info(self) -> dict:
		"""Retorna información del estado actual del combate."""
		player_stats = self.player.get_effective_stats(self.biome_bonuses)

		info = {
			"player": {
				"level": self.player.level,
				"hp": self.player.base_stats.current_hp,
				"max_hp": self.player.base_stats.max_hp,
				"hp_percentage": self.player.base_stats.get_hp_percentage(),
				"attack": player_stats.attack,
				"defense": player_stats.defense,
				"speed": player_stats.speed,
				"experience": self.player.experience,
				"exp_to_next": self.player.get_experience_for_next_level(),
			},
			"combat_state": self.combat_state.value,
			"damage_dealt": self.total_damage_dealt,
			"damage_received": self.total_damage_received,
		}

		if self.current_enemy:
			info["enemy"] = {
				"name": self.current_enemy.name,
				"level": self.current_enemy.level,
				"hp": self.current_enemy.stats.current_hp,
				"max_hp": self.current_enemy.stats.max_hp,
				"hp_percentage": self.current_enemy.stats.get_hp_percentage(),
				"attack": self.current_enemy.stats.attack,
				"defense": self.current_enemy.stats.defense,
				"type": self.current_enemy.enemy_type,
			}

		return info

	def force_stop_combat(self) -> None:
		"""Fuerza el fin del combate (para huir o cambiar de área)."""
		if self.combat_state == CombatState.FIGHTING:
			print("Combate interrumpido.")
			self._end_combat()
