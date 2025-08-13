"""
Sistema de estadísticas y progresión del jugador para SiKIdle.
Maneja atributos, niveles, puntos de habilidad y integración con equipamiento.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Optional
import math

from core.combat import CombatStats


class AttributeType(Enum):
	"""Tipos de atributos principales del jugador."""
	STRENGTH = "strength"		# Aumenta daño físico y HP
	AGILITY = "agility"			# Aumenta velocidad de ataque y críticos
	INTELLIGENCE = "intelligence"	# Aumenta regeneración y resistencias
	VITALITY = "vitality"		# Aumenta HP y defensa


@dataclass
class PlayerAttributes:
	"""Atributos base del jugador."""
	strength: int = 10
	agility: int = 10
	intelligence: int = 10
	vitality: int = 10
	
	# Puntos disponibles para distribuir
	available_points: int = 0
	
	def get_total_points(self) -> int:
		"""Calcula el total de puntos invertidos en atributos."""
		return self.strength + self.agility + self.intelligence + self.vitality
	
	def add_attribute_point(self, attribute: AttributeType, points: int = 1) -> bool:
		"""Añade puntos a un atributo si hay puntos disponibles."""
		if self.available_points < points:
			return False
		
		if attribute == AttributeType.STRENGTH:
			self.strength += points
		elif attribute == AttributeType.AGILITY:
			self.agility += points
		elif attribute == AttributeType.INTELLIGENCE:
			self.intelligence += points
		elif attribute == AttributeType.VITALITY:
			self.vitality += points
		else:
			return False
		
		self.available_points -= points
		return True
	
	def get_attribute_value(self, attribute: AttributeType) -> int:
		"""Obtiene el valor de un atributo específico."""
		if attribute == AttributeType.STRENGTH:
			return self.strength
		elif attribute == AttributeType.AGILITY:
			return self.agility
		elif attribute == AttributeType.INTELLIGENCE:
			return self.intelligence
		elif attribute == AttributeType.VITALITY:
			return self.vitality
		return 0


@dataclass
class PlayerLevel:
	"""Sistema de experiencia y niveles del jugador."""
	level: int = 1
	current_experience: int = 0
	total_experience: int = 0
	
	# Constantes de balancing
	BASE_EXP_REQUIREMENT: int = 100
	EXP_SCALING_FACTOR: float = 1.5
	
	def get_experience_for_level(self, target_level: int) -> int:
		"""Calcula la experiencia requerida para un nivel específico."""
		if target_level <= 1:
			return 0
		
		# Fórmula exponencial: base * (scaling ^ (level - 1))
		return int(self.BASE_EXP_REQUIREMENT * (self.EXP_SCALING_FACTOR ** (target_level - 1)))
	
	def get_experience_for_next_level(self) -> int:
		"""Calcula la experiencia necesaria para el siguiente nivel."""
		return self.get_experience_for_level(self.level + 1)
	
	def get_experience_to_next_level(self) -> int:
		"""Calcula cuánta experiencia falta para el siguiente nivel."""
		return self.get_experience_for_next_level() - self.current_experience
	
	def can_level_up(self) -> bool:
		"""Verifica si el jugador puede subir de nivel."""
		return self.current_experience >= self.get_experience_for_next_level()
	
	def add_experience(self, amount: int) -> list[int]:
		"""Añade experiencia y retorna lista de niveles ganados."""
		self.current_experience += amount
		self.total_experience += amount
		
		levels_gained = []
		while self.can_level_up():
			exp_required = self.get_experience_for_next_level()
			self.current_experience -= exp_required
			self.level += 1
			levels_gained.append(self.level)
		
		return levels_gained
	
	def get_level_progress(self) -> float:
		"""Retorna el progreso hacia el siguiente nivel (0.0 - 1.0)."""
		if self.level == 1:
			total_needed = self.get_experience_for_next_level()
			return self.current_experience / total_needed if total_needed > 0 else 0.0
		
		prev_level_exp = self.get_experience_for_level(self.level)
		next_level_exp = self.get_experience_for_next_level()
		current_in_level = self.current_experience
		
		if next_level_exp <= prev_level_exp:
			return 1.0
		
		return current_in_level / (next_level_exp - prev_level_exp)


@dataclass
class PlayerStatistics:
	"""Estadísticas detalladas del progreso del jugador."""
	# Estadísticas de combate
	total_enemies_defeated: int = 0
	total_damage_dealt: int = 0
	total_damage_received: int = 0
	total_critical_hits: int = 0
	longest_combat_streak: int = 0
	current_combat_streak: int = 0
	
	# Estadísticas de exploración
	dungeons_explored: int = 0
	bosses_defeated: int = 0
	areas_unlocked: int = 0
	
	# Estadísticas de loot
	items_found: int = 0
	rare_items_found: int = 0
	epic_items_found: int = 0
	legendary_items_found: int = 0
	
	# Estadísticas de tiempo
	total_playtime_seconds: int = 0
	sessions_played: int = 0
	
	def add_enemy_defeated(self, was_critical: bool = False):
		"""Registra un enemigo derrotado."""
		self.total_enemies_defeated += 1
		self.current_combat_streak += 1
		self.longest_combat_streak = max(self.longest_combat_streak, self.current_combat_streak)
		
		if was_critical:
			self.total_critical_hits += 1
	
	def reset_combat_streak(self):
		"""Resetea la racha de combate actual."""
		self.current_combat_streak = 0
	
	def add_damage_dealt(self, damage: int):
		"""Registra daño infligido."""
		self.total_damage_dealt += damage
	
	def add_damage_received(self, damage: int):
		"""Registra daño recibido."""
		self.total_damage_received += damage
	
	def add_item_found(self, rarity: str):
		"""Registra un ítem encontrado según su rareza."""
		self.items_found += 1
		
		if rarity.lower() == "rare":
			self.rare_items_found += 1
		elif rarity.lower() == "epic":
			self.epic_items_found += 1
		elif rarity.lower() == "legendary":
			self.legendary_items_found += 1
	
	def get_average_damage_per_enemy(self) -> float:
		"""Calcula el daño promedio por enemigo."""
		if self.total_enemies_defeated == 0:
			return 0.0
		return self.total_damage_dealt / self.total_enemies_defeated
	
	def get_critical_hit_rate(self) -> float:
		"""Calcula el porcentaje de críticos."""
		if self.total_enemies_defeated == 0:
			return 0.0
		return (self.total_critical_hits / self.total_enemies_defeated) * 100


class PlayerStatsManager:
	"""Gestor principal de las estadísticas del jugador."""
	
	def __init__(self):
		self.attributes = PlayerAttributes()
		self.level_system = PlayerLevel()
		self.statistics = PlayerStatistics()
		
		# Cache para estadísticas calculadas
		self._cached_combat_stats: Optional[CombatStats] = None
		self._cache_dirty = True
		
		# Bonificaciones de equipamiento (aplicadas externamente)
		self.equipment_bonuses: Dict[str, float] = {}
	
	def calculate_base_combat_stats(self) -> CombatStats:
		"""Calcula las estadísticas de combate base del jugador sin equipamiento."""
		# Estadísticas base por nivel
		base_hp = 100 + (self.level_system.level - 1) * 20
		base_attack = 10 + (self.level_system.level - 1) * 3
		base_defense = 2 + (self.level_system.level - 1) * 1
		base_speed = 1.0 + (self.level_system.level - 1) * 0.05
		
		# Bonificaciones por atributos
		str_bonus = self.attributes.strength - 10  # Cada punto sobre 10
		agi_bonus = self.attributes.agility - 10
		int_bonus = self.attributes.intelligence - 10
		vit_bonus = self.attributes.vitality - 10
		
		# Aplicar bonificaciones de atributos
		# Strength: +5% HP, +10% damage por punto
		hp_multiplier = 1.0 + (str_bonus * 0.05)
		attack_multiplier = 1.0 + (str_bonus * 0.10)
		
		# Agility: +5% speed, +1% crit chance por punto
		speed_multiplier = 1.0 + (agi_bonus * 0.05)
		crit_chance_bonus = agi_bonus * 0.01
		
		# Intelligence: +2% crit multiplier por punto
		crit_multiplier_bonus = int_bonus * 0.02
		
		# Vitality: +8% HP, +5% defense por punto
		hp_vit_multiplier = 1.0 + (vit_bonus * 0.08)
		defense_multiplier = 1.0 + (vit_bonus * 0.05)
		
		# Calcular estadísticas finales
		final_hp = int(base_hp * hp_multiplier * hp_vit_multiplier)
		final_attack = int(base_attack * attack_multiplier)
		final_defense = int(base_defense * defense_multiplier)
		final_speed = base_speed * speed_multiplier
		final_crit_chance = max(0.0, min(0.95, 0.05 + crit_chance_bonus))  # 5% base, max 95%
		final_crit_multiplier = 2.0 + crit_multiplier_bonus
		
		return CombatStats(
			max_hp=final_hp,
			current_hp=final_hp,  # Se gestionará externamente
			attack=final_attack,
			defense=final_defense,
			speed=final_speed,
			critical_chance=final_crit_chance,
			critical_multiplier=final_crit_multiplier
		)
	
	def get_effective_combat_stats(self, current_hp: Optional[int] = None, biome_bonuses: Optional[dict] = None) -> CombatStats:
		"""Obtiene las estadísticas de combate finales con equipamiento y bonificaciones de bioma."""
		if self._cache_dirty or self._cached_combat_stats is None:
			self._cached_combat_stats = self.calculate_base_combat_stats()
			self._cache_dirty = False
		
		# Aplicar bonificaciones de bioma si están disponibles
		attack_multiplier = 1.0
		defense_multiplier = 1.0
		speed_multiplier = 1.0
		
		if biome_bonuses:
			attack_multiplier = biome_bonuses.get("damage", 1.0)
			defense_multiplier = biome_bonuses.get("defense", 1.0)
			speed_multiplier = biome_bonuses.get("attack_speed", 1.0)
		
		# Copiar stats base y aplicar bonificaciones de bioma
		stats = CombatStats(
			max_hp=self._cached_combat_stats.max_hp,
			current_hp=current_hp if current_hp is not None else self._cached_combat_stats.max_hp,
			attack=int(self._cached_combat_stats.attack * attack_multiplier),
			defense=int(self._cached_combat_stats.defense * defense_multiplier),
			speed=self._cached_combat_stats.speed * speed_multiplier,
			critical_chance=self._cached_combat_stats.critical_chance,
			critical_multiplier=self._cached_combat_stats.critical_multiplier
		)
		
		# Aplicar bonificaciones de equipamiento
		damage_mult = self.equipment_bonuses.get('damage_multiplier', 1.0)
		click_mult = self.equipment_bonuses.get('click_multiplier', 1.0)
		
		stats.attack = int(stats.attack * damage_mult * click_mult)
		stats.speed = stats.speed * click_mult
		
		return stats
	
	def add_experience(self, amount: int) -> list[int]:
		"""Añade experiencia y maneja subidas de nivel."""
		levels_gained = self.level_system.add_experience(amount)
		
		# Por cada nivel ganado, dar puntos de atributo
		for level in levels_gained:
			points_per_level = 5  # 5 puntos de atributo por nivel
			self.attributes.available_points += points_per_level
			self._cache_dirty = True
			print(f"¡Nivel {level} alcanzado! +{points_per_level} puntos de atributo disponibles")
		
		return levels_gained
	
	def allocate_attribute_points(self, allocations: Dict[AttributeType, int]) -> bool:
		"""Asigna múltiples puntos de atributo de una vez."""
		total_points_needed = sum(allocations.values())
		
		if total_points_needed > self.attributes.available_points:
			return False
		
		# Aplicar todas las asignaciones
		for attribute, points in allocations.items():
			if points > 0:
				self.attributes.add_attribute_point(attribute, points)
		
		self._cache_dirty = True
		return True
	
	def get_attribute_recommendations(self) -> Dict[AttributeType, str]:
		"""Proporciona recomendaciones sobre qué atributos mejorar."""
		recommendations = {}
		
		current_level = self.level_system.level
		
		# Recomendaciones basadas en nivel
		if current_level < 10:
			recommendations[AttributeType.STRENGTH] = "Aumenta daño y HP para sobrevivir"
			recommendations[AttributeType.VITALITY] = "Esencial para resistir ataques tempranos"
		elif current_level < 25:
			recommendations[AttributeType.AGILITY] = "Mejora velocidad de ataque y críticos"
			recommendations[AttributeType.STRENGTH] = "Continúa aumentando el daño"
		else:
			recommendations[AttributeType.INTELLIGENCE] = "Mejora regeneración y resistencias"
			recommendations[AttributeType.AGILITY] = "Maximiza críticos para late game"
		
		return recommendations
	
	def reset_attributes(self, cost_multiplier: float = 1.0) -> bool:
		"""Resetea todos los atributos y devuelve los puntos."""
		# En un juego real, esto costaría recursos
		total_invested = self.attributes.get_total_points() - 40  # 40 puntos base (10 cada atributo)
		
		if total_invested <= 0:
			return False
		
		# Resetear a valores base
		self.attributes.strength = 10
		self.attributes.agility = 10
		self.attributes.intelligence = 10
		self.attributes.vitality = 10
		self.attributes.available_points += total_invested
		
		self._cache_dirty = True
		return True
	
	def get_player_info(self) -> Dict:
		"""Retorna información completa del jugador."""
		stats = self.get_effective_combat_stats()
		
		return {
			'level': self.level_system.level,
			'experience': {
				'current': self.level_system.current_experience,
				'to_next_level': self.level_system.get_experience_to_next_level(),
				'total': self.level_system.total_experience,
				'progress': self.level_system.get_level_progress()
			},
			'attributes': {
				'strength': self.attributes.strength,
				'agility': self.attributes.agility,
				'intelligence': self.attributes.intelligence,
				'vitality': self.attributes.vitality,
				'available_points': self.attributes.available_points
			},
			'combat_stats': {
				'max_hp': stats.max_hp,
				'attack': stats.attack,
				'defense': stats.defense,
				'speed': stats.speed,
				'critical_chance': stats.critical_chance,
				'critical_multiplier': stats.critical_multiplier
			},
			'statistics': {
				'enemies_defeated': self.statistics.total_enemies_defeated,
				'damage_dealt': self.statistics.total_damage_dealt,
				'critical_hits': self.statistics.total_critical_hits,
				'items_found': self.statistics.items_found,
				'current_streak': self.statistics.current_combat_streak,
				'longest_streak': self.statistics.longest_combat_streak
			}
		}
	
	def update_equipment_bonuses(self, bonuses: Dict[str, float]):
		"""Actualiza las bonificaciones de equipamiento."""
		self.equipment_bonuses = bonuses.copy()
		# No marcamos cache como dirty porque las bonificaciones se aplican en get_effective_combat_stats
	
	def invalidate_cache(self):
		"""Invalida el cache de estadísticas calculadas."""
		self._cache_dirty = True
