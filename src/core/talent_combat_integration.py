"""
Integración del Sistema de Talentos con Sistemas de Combate
Aplica automáticamente los efectos de talentos a los sistemas del juego
"""

import logging
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
	from core.talents import TalentManager
	from core.combat import CombatManager
	from core.loot import LootGenerator
	from core.player_stats import PlayerLevel

logger = logging.getLogger(__name__)


class TalentCombatIntegration:
	"""Integra los efectos de talentos con los sistemas de combate"""

	def __init__(
		self,
		talent_manager: "TalentManager",
		combat_manager: Optional["CombatManager"] = None,
		loot_generator: Optional["LootGenerator"] = None,
		player_level: Optional["PlayerLevel"] = None,
	):
		self.talent_manager = talent_manager
		self.combat_manager = combat_manager
		self.loot_generator = loot_generator
		self.player_level = player_level

		# Estados especiales de combate (para talentos avanzados)
		self.berserker_stacks = 0
		self.max_berserker_stacks = 50
		self.combo_chain = 0
		self.last_critical_time = 0

		# Configurar callbacks
		self._setup_talent_callbacks()

		logger.info("Integración talentos-combate inicializada")

	def _setup_talent_callbacks(self):
		"""Configura callbacks para cuando se actualizan talentos"""
		if self.talent_manager:
			self.talent_manager.set_talent_updated_callback(self._on_talent_updated)

	def _on_talent_updated(self, talent_id: str, new_level: int, talent_info):
		"""Callback ejecutado cuando se mejora un talento"""
		logger.info("Talento %s mejorado a nivel %d, recalculando efectos", 
					talent_info.name, new_level)
		self._apply_all_talent_effects()

	def _apply_all_talent_effects(self):
		"""Aplica todos los efectos de talentos activos a los sistemas"""
		if not self.talent_manager:
			return

		# Obtener multiplicadores actuales
		multipliers = self.talent_manager.calculate_total_multipliers()

		# Aplicar efectos a CombatManager si está disponible
		if self.combat_manager:
			self._apply_combat_effects(multipliers)

		# Aplicar efectos a LootGenerator si está disponible
		if self.loot_generator:
			self._apply_loot_effects(multipliers)

		# Aplicar efectos a PlayerLevel si está disponible
		if self.player_level:
			self._apply_player_effects(multipliers)

	def _apply_combat_effects(self, multipliers: dict):
		"""Aplica efectos de talentos al sistema de combate"""
		if not self.combat_manager or not self.combat_manager.player:
			return

		player = self.combat_manager.player
		base_stats = player.base_stats

		# Aplicar multiplicadores de daño físico (Guerrero)
		if multipliers["physical_damage"] > 1.0:
			bonus = multipliers["physical_damage"] - 1.0
			player.stats.attack = base_stats.attack * (1.0 + bonus)
			logger.debug("Daño físico aumentado: +%.1f%% por talentos", bonus * 100)

		# Aplicar bonificación de probabilidad crítica (Guerrero)
		if multipliers["critical_chance"] > 0:
			# El CombatManager debería usar esto en sus cálculos
			setattr(player, '_talent_critical_bonus', multipliers["critical_chance"])
			logger.debug("Probabilidad crítica aumentada: +%.1f%% por talentos", 
						multipliers["critical_chance"] * 100)

		# Aplicar velocidad de ataque (Guerrero)
		if multipliers["attack_speed"] > 1.0:
			bonus = multipliers["attack_speed"] - 1.0
			current_speed = getattr(player.stats, 'speed', 1.0)
			player.stats.speed = current_speed * (1.0 + bonus)
			logger.debug("Velocidad de ataque aumentada: +%.1f%% por talentos", bonus * 100)

		# Aplicar reducción de daño (Tanque)
		if multipliers["damage_reduction"] > 0:
			setattr(player, '_talent_damage_reduction', multipliers["damage_reduction"])
			logger.debug("Reducción de daño: +%.1f%% por talentos", 
						multipliers["damage_reduction"] * 100)

		# Aplicar bonificación de salud máxima (Tanque)
		if multipliers["max_health_bonus"] > 0:
			bonus_health = multipliers["max_health_bonus"]
			player.stats.hp = base_stats.hp + bonus_health
			logger.debug("Salud máxima aumentada: +%.0f por talentos", bonus_health)

		# Aplicar regeneración de salud (Tanque)
		if multipliers["health_regeneration"] > 0:
			setattr(player, '_talent_health_regen', multipliers["health_regeneration"])
			logger.debug("Regeneración de salud: +%.1f%% por talentos", 
						multipliers["health_regeneration"] * 100)

	def _apply_loot_effects(self, multipliers: dict):
		"""Aplica efectos de talentos al sistema de loot"""
		if not self.loot_generator:
			return

		# Aplicar bonificación de loot raro (Explorador)
		if multipliers["loot_rarity_chance"] > 1.0:
			bonus = multipliers["loot_rarity_chance"] - 1.0
			setattr(self.loot_generator, '_talent_rarity_bonus', bonus)
			logger.debug("Probabilidad de loot raro aumentada: +%.1f%% por talentos", 
						bonus * 100)

		# Aplicar velocidad de exploración (Explorador)
		if multipliers["exploration_speed"] > 1.0:
			bonus = multipliers["exploration_speed"] - 1.0
			setattr(self.loot_generator, '_talent_exploration_bonus', bonus)
			logger.debug("Velocidad de exploración aumentada: +%.1f%% por talentos", 
						bonus * 100)

		# Aplicar probabilidad de efectos elementales (Mago)
		if multipliers["elemental_chance"] > 0:
			setattr(self.loot_generator, '_talent_elemental_bonus', 
					multipliers["elemental_chance"])
			logger.debug("Probabilidad de efectos elementales: +%.1f%% por talentos", 
						multipliers["elemental_chance"] * 100)

	def _apply_player_effects(self, multipliers: dict):
		"""Aplica efectos de talentos al sistema de experiencia"""
		if not self.player_level:
			return

		# Aplicar bonificación de experiencia (Mago)
		if multipliers["experience_gain"] > 1.0:
			bonus = multipliers["experience_gain"] - 1.0
			setattr(self.player_level, '_talent_exp_bonus', bonus)
			logger.debug("Ganancia de experiencia aumentada: +%.1f%% por talentos", 
						bonus * 100)

	def apply_berserker_effect(self, enemies_defeated: int = 1):
		"""Aplica el efecto Berserker cuando se derrotan enemigos"""
		from core.talents import TalentType

		berserker_level = self.talent_manager.get_talent_level(TalentType.WARRIOR_BERSERKER)
		if berserker_level <= 0:
			return 1.0

		# Aumentar stacks de berserker
		self.berserker_stacks = min(
			self.berserker_stacks + enemies_defeated,
			self.max_berserker_stacks
		)

		# Calcular multiplicador (+2% por stack por nivel)
		stack_bonus = berserker_level * 0.02 * self.berserker_stacks
		multiplier = 1.0 + stack_bonus

		logger.debug("Berserker activo: %d stacks, +%.1f%% daño", 
					self.berserker_stacks, stack_bonus * 100)

		return multiplier

	def apply_critical_combo_effect(self, is_critical: bool) -> float:
		"""Aplica el efecto de combo crítico"""
		from core.talents import TalentType

		combo_level = self.talent_manager.get_talent_level(TalentType.WARRIOR_WEAPON_MASTER)
		if combo_level <= 0:
			return 1.0

		if is_critical:
			self.combo_chain += 1
			# +5% daño adicional por crítico en cadena, por nivel
			chain_bonus = combo_level * 0.05 * min(self.combo_chain, 10)  # Max 10 chain
			multiplier = 1.0 + chain_bonus

			logger.debug("Combo crítico: %d cadena, +%.1f%% daño", 
						self.combo_chain, chain_bonus * 100)
			return multiplier
		else:
			# Romper la cadena si no es crítico
			self.combo_chain = 0
			return 1.0

	def apply_spell_echo_effect(self) -> bool:
		"""Verifica si se activa el efecto de eco de hechizo"""
		from core.talents import TalentType

		echo_level = self.talent_manager.get_talent_level(TalentType.MAGE_SPELL_ECHO)
		if echo_level <= 0:
			return False

		# 15% probabilidad base por nivel
		echo_chance = echo_level * 0.15
		import random
		
		if random.random() < echo_chance:
			logger.debug("Eco de hechizo activado (%.1f%% probabilidad)", echo_chance * 100)
			return True

		return False

	def apply_legendary_seeker_effect(self) -> bool:
		"""Verifica si se fuerza la aparición de loot legendario"""
		from core.talents import TalentType

		seeker_level = self.talent_manager.get_talent_level(TalentType.EXPLORER_LEGENDARY_SEEKER)
		if seeker_level <= 0:
			return False

		# 0.5% probabilidad base por nivel
		legendary_chance = seeker_level * 0.005
		import random

		if random.random() < legendary_chance:
			logger.debug("Buscador de leyendas activado (%.2f%% probabilidad)", 
						legendary_chance * 100)
			return True

		return False

	def apply_last_stand_effect(self, current_hp: float, max_hp: float) -> float:
		"""Aplica el efecto de última resistencia"""
		from core.talents import TalentType

		last_stand_level = self.talent_manager.get_talent_level(TalentType.TANK_LAST_STAND)
		if last_stand_level <= 0:
			return 1.0

		# Activar cuando la salud está por debajo del 25%
		hp_percentage = current_hp / max_hp if max_hp > 0 else 1.0

		if hp_percentage < 0.25:
			# +100% daño por nivel cuando salud < 25%
			last_stand_bonus = last_stand_level * 1.0
			multiplier = 1.0 + last_stand_bonus

			logger.debug("Última resistencia activada: +%.0f%% daño (%.1f%% HP)", 
						last_stand_bonus * 100, hp_percentage * 100)
			return multiplier

		return 1.0

	def apply_mana_shield_effect(self, incoming_damage: float, current_mana: float) -> tuple[float, float]:
		"""Aplica el efecto de escudo de maná"""
		from core.talents import TalentType

		shield_level = self.talent_manager.get_talent_level(TalentType.MAGE_MANA_SHIELD)
		if shield_level <= 0 or current_mana <= 0:
			return incoming_damage, current_mana

		# 15% absorción por nivel
		absorption_rate = shield_level * 0.15
		absorbed_damage = incoming_damage * absorption_rate

		# Convertir daño absorbido en costo de maná (2:1 ratio)
		mana_cost = absorbed_damage * 2.0

		if current_mana >= mana_cost:
			# Suficiente maná, absorber el daño
			remaining_damage = incoming_damage - absorbed_damage
			remaining_mana = current_mana - mana_cost

			logger.debug("Escudo de maná: absorbió %.1f daño, costó %.1f maná", 
						absorbed_damage, mana_cost)

			return remaining_damage, remaining_mana
		else:
			# Maná insuficiente, absorber solo lo que se pueda
			possible_absorption = current_mana / 2.0
			remaining_damage = incoming_damage - possible_absorption
			remaining_mana = 0.0

			logger.debug("Escudo de maná parcial: absorbió %.1f daño, agotó maná", 
						possible_absorption)

			return remaining_damage, remaining_mana

	def decay_berserker_stacks(self, decay_rate: float = 1.0):
		"""Decrementa los stacks de berserker con el tiempo"""
		if self.berserker_stacks > 0:
			self.berserker_stacks = max(0, self.berserker_stacks - decay_rate)

	def reset_combat_states(self):
		"""Resetea estados de combate (al cambiar de área, etc.)"""
		self.berserker_stacks = 0
		self.combo_chain = 0
		self.last_critical_time = 0
		logger.debug("Estados de combate reseteados")

	def get_talent_combat_stats(self) -> dict:
		"""Obtiene estadísticas del estado actual de talentos en combate"""
		multipliers = self.talent_manager.calculate_total_multipliers() if self.talent_manager else {}

		return {
			"multipliers": multipliers,
			"berserker_stacks": self.berserker_stacks,
			"combo_chain": self.combo_chain,
			"active_effects": {
				"berserker": self.berserker_stacks > 0,
				"combo": self.combo_chain > 0,
			}
		}
