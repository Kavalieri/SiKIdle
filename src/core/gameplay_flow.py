"""
Sistema de Flujo de Gameplay para SiKIdle - Idle Clicker Tradicional.

Gestiona el bucle de gameplay tradicional:
1. Inicio: Clic manual para primeras monedas
2. Primer edificio: Comprar generador básico
3. Automatización: Ingresos pasivos crecientes
4. Mejoras: Multiplicadores para acelerar progreso
5. Estancamiento: Progreso lento que motiva prestigio
"""

import logging
from enum import Enum
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass


class GameplayPhase(Enum):
	"""Fases del bucle de gameplay tradicional."""
	TUTORIAL_CLICKS = "tutorial_clicks"          # 0-10 monedas: Aprender a hacer clic
	FIRST_BUILDING = "first_building"            # 10-100 monedas: Comprar primer edificio
	EARLY_AUTOMATION = "early_automation"       # 100-1K monedas: Primeros ingresos pasivos
	BUILDING_EXPANSION = "building_expansion"   # 1K-10K monedas: Múltiples edificios
	UPGRADE_PHASE = "upgrade_phase"             # 10K-100K monedas: Multiplicadores
	PRE_PRESTIGE = "pre_prestige"               # 100K+ monedas: Preparar prestigio
	POST_PRESTIGE = "post_prestige"             # Después del prestigio: Ciclo acelerado


@dataclass
class GameplayHint:
	"""Pista o sugerencia para el jugador."""
	title: str
	message: str
	priority: int  # 1=crítico, 2=importante, 3=sugerencia
	action_button: Optional[str] = None
	callback: Optional[Callable] = None


class GameplayFlowManager:
	"""Gestor del flujo de gameplay tradicional."""
	
	def __init__(self, game_state):
		"""Inicializa el gestor de flujo de gameplay."""
		self.game_state = game_state
		self.current_phase = GameplayPhase.TUTORIAL_CLICKS
		self.hints_shown = set()
		self.phase_callbacks: Dict[GameplayPhase, List[Callable]] = {}
		
		# Configuración de fases
		self.phase_thresholds = {
			GameplayPhase.TUTORIAL_CLICKS: 0,
			GameplayPhase.FIRST_BUILDING: 10,
			GameplayPhase.EARLY_AUTOMATION: 100,
			GameplayPhase.BUILDING_EXPANSION: 1000,
			GameplayPhase.UPGRADE_PHASE: 10000,
			GameplayPhase.PRE_PRESTIGE: 100000,
			GameplayPhase.POST_PRESTIGE: 0  # Se activa tras prestigio
		}
		
		logging.info("GameplayFlowManager initialized")
	
	def update_phase(self) -> bool:
		"""Actualiza la fase actual según el progreso. Returns True si cambió."""
		old_phase = self.current_phase
		coins = self.game_state.coins
		
		# Verificar si ha hecho prestigio
		if hasattr(self.game_state, 'prestige_manager'):
			if self.game_state.prestige_manager.prestige_count > 0:
				if self.current_phase != GameplayPhase.POST_PRESTIGE:
					self.current_phase = GameplayPhase.POST_PRESTIGE
			else:
				# Determinar fase según monedas
				for phase in reversed(list(GameplayPhase)):
					if phase == GameplayPhase.POST_PRESTIGE:
						continue
					if coins >= self.phase_thresholds[phase]:
						self.current_phase = phase
						break
		
		# Notificar cambio de fase
		if old_phase != self.current_phase:
			logging.info(f"Gameplay phase changed: {old_phase.value} → {self.current_phase.value}")
			self._on_phase_changed(old_phase, self.current_phase)
			return True
		
		return False
	
	def get_current_hints(self) -> List[GameplayHint]:
		"""Obtiene las pistas actuales según la fase."""
		hints = []
		
		if self.current_phase == GameplayPhase.TUTORIAL_CLICKS:
			hints.extend(self._get_tutorial_hints())
		elif self.current_phase == GameplayPhase.FIRST_BUILDING:
			hints.extend(self._get_first_building_hints())
		elif self.current_phase == GameplayPhase.EARLY_AUTOMATION:
			hints.extend(self._get_early_automation_hints())
		elif self.current_phase == GameplayPhase.BUILDING_EXPANSION:
			hints.extend(self._get_building_expansion_hints())
		elif self.current_phase == GameplayPhase.UPGRADE_PHASE:
			hints.extend(self._get_upgrade_phase_hints())
		elif self.current_phase == GameplayPhase.PRE_PRESTIGE:
			hints.extend(self._get_pre_prestige_hints())
		elif self.current_phase == GameplayPhase.POST_PRESTIGE:
			hints.extend(self._get_post_prestige_hints())
		
		# Añadir hints de combat si está disponible
		if hasattr(self.game_state, 'combat_idle_integration'):
			combat_hints = self.game_state.combat_idle_integration.get_integration_hints()
			for combat_hint in combat_hints:
				hints.append(GameplayHint(
					title=combat_hint['title'],
					message=combat_hint['message'],
					priority=combat_hint['priority']
				))
		
		# Filtrar hints ya mostradas
		return [hint for hint in hints if hint.title not in self.hints_shown]
	
	def _get_tutorial_hints(self) -> List[GameplayHint]:
		"""Pistas para la fase tutorial."""
		return [
			GameplayHint(
				title="¡Bienvenido a SiKIdle!",
				message="Haz clic en el botón grande para ganar tus primeras monedas. ¡Cada clic cuenta!",
				priority=1
			),
			GameplayHint(
				title="Objetivo: 10 monedas",
				message="Necesitas 10 monedas para comprar tu primer generador automático.",
				priority=2
			)
		]
	
	def _get_first_building_hints(self) -> List[GameplayHint]:
		"""Pistas para comprar el primer edificio."""
		return [
			GameplayHint(
				title="¡Compra tu primera Granja!",
				message="Con 10 monedas puedes comprar una Granja que genera monedas automáticamente. ¡Es el inicio de tu imperio!",
				priority=1
			),
			GameplayHint(
				title="Ingresos Pasivos",
				message="Los edificios generan monedas incluso cuando no haces clic. ¡La automatización ha comenzado!",
				priority=2
			)
		]
	
	def _get_early_automation_hints(self) -> List[GameplayHint]:
		"""Pistas para la automatización temprana."""
		return [
			GameplayHint(
				title="¡Más edificios, más ingresos!",
				message="Compra más Granjas o desbloquea la Fábrica (100 monedas) para acelerar tu progreso.",
				priority=1
			),
			GameplayHint(
				title="Combina Clic + Automatización",
				message="Sigue haciendo clic mientras tus edificios trabajan. ¡Duplica tus ganancias!",
				priority=2
			)
		]
	
	def _get_building_expansion_hints(self) -> List[GameplayHint]:
		"""Pistas para la expansión de edificios."""
		return [
			GameplayHint(
				title="Diversifica tu Imperio",
				message="Desbloquea nuevos tipos de edificios: Banco (1K), Mina (10K). Cada uno es más eficiente.",
				priority=1
			),
			GameplayHint(
				title="Pestaña Upgrades Desbloqueada",
				message="¡Con 10 edificios has desbloqueado las Mejoras! Visita la pestaña para multiplicadores.",
				priority=1
			)
		]
	
	def _get_upgrade_phase_hints(self) -> List[GameplayHint]:
		"""Pistas para la fase de mejoras."""
		return [
			GameplayHint(
				title="¡Hora de las Mejoras!",
				message="Invierte en mejoras para multiplicar tus ganancias. Empieza con 'Poder de Clic' y 'Eficiencia'.",
				priority=1
			),
			GameplayHint(
				title="Estrategia de Multiplicadores",
				message="Las mejoras se acumulan. Una mejora de +50% se suma a otras para crear efectos poderosos.",
				priority=2
			)
		]
	
	def _get_pre_prestige_hints(self) -> List[GameplayHint]:
		"""Pistas antes del prestigio."""
		return [
			GameplayHint(
				title="¡Prestigio Disponible!",
				message="Con 100K monedas puedes hacer prestigio. Reseteas tu progreso pero ganas cristales permanentes.",
				priority=1
			),
			GameplayHint(
				title="¿Cuándo hacer Prestigio?",
				message="Haz prestigio cuando el progreso se vuelva lento. Los cristales te darán multiplicadores permanentes.",
				priority=2
			),
			GameplayHint(
				title="Sección de Prestigio",
				message="Revisa la sección de prestigio en la pantalla principal para ver cuántos cristales ganarías.",
				priority=2
			)
		]
	
	def _get_post_prestige_hints(self) -> List[GameplayHint]:
		"""Pistas después del prestigio."""
		return [
			GameplayHint(
				title="¡Prestigio Completado!",
				message="Ahora tienes multiplicadores permanentes. Tu progreso será mucho más rápido.",
				priority=1
			),
			GameplayHint(
				title="Pestaña Logros Desbloqueada",
				message="¡Los logros están disponibles! Completa objetivos para más multiplicadores permanentes.",
				priority=1
			),
			GameplayHint(
				title="Ciclo Acelerado",
				message="Repite el ciclo: edificios → mejoras → prestigio. Cada vez será más rápido y poderoso.",
				priority=2
			)
		]
	
	def mark_hint_shown(self, hint_title: str):
		"""Marca una pista como mostrada."""
		self.hints_shown.add(hint_title)
	
	def _on_phase_changed(self, old_phase: GameplayPhase, new_phase: GameplayPhase):
		"""Callback cuando cambia la fase."""
		# Ejecutar callbacks registrados
		if new_phase in self.phase_callbacks:
			for callback in self.phase_callbacks[new_phase]:
				try:
					callback(old_phase, new_phase)
				except Exception as e:
					logging.error(f"Error in phase callback: {e}")
	
	def register_phase_callback(self, phase: GameplayPhase, callback: Callable):
		"""Registra un callback para cuando se alcance una fase."""
		if phase not in self.phase_callbacks:
			self.phase_callbacks[phase] = []
		self.phase_callbacks[phase].append(callback)
	
	def get_progress_to_next_phase(self) -> Dict:
		"""Obtiene el progreso hacia la siguiente fase."""
		current_coins = self.game_state.coins
		
		# Encontrar siguiente fase
		next_phase = None
		next_threshold = float('inf')
		
		for phase, threshold in self.phase_thresholds.items():
			if threshold > current_coins and threshold < next_threshold:
				next_phase = phase
				next_threshold = threshold
		
		if next_phase is None:
			return {
				'next_phase': None,
				'progress_percentage': 100.0,
				'coins_needed': 0,
				'current_coins': current_coins
			}
		
		# Calcular progreso
		current_threshold = self.phase_thresholds.get(self.current_phase, 0)
		progress = (current_coins - current_threshold) / (next_threshold - current_threshold)
		progress_percentage = min(100.0, max(0.0, progress * 100))
		
		return {
			'next_phase': next_phase,
			'progress_percentage': progress_percentage,
			'coins_needed': max(0, next_threshold - current_coins),
			'current_coins': current_coins,
			'next_threshold': next_threshold
		}
	
	def is_stagnation_phase(self) -> bool:
		"""Verifica si el jugador está en una fase de estancamiento."""
		# Estancamiento ocurre en PRE_PRESTIGE cuando el progreso es lento
		if self.current_phase != GameplayPhase.PRE_PRESTIGE:
			return False
		
		# Verificar si tiene suficientes monedas para prestigio pero progreso lento
		if hasattr(self.game_state, 'prestige_manager'):
			total_coins = self.game_state.lifetime_coins + self.game_state.coins
			can_prestige = self.game_state.prestige_manager.can_prestige(total_coins)
			
			# Si puede hacer prestigio y tiene muchas monedas, es estancamiento
			return can_prestige and self.game_state.coins > 150000
		
		return False
	
	def get_stagnation_solution(self) -> Optional[GameplayHint]:
		"""Obtiene sugerencia para resolver el estancamiento."""
		if not self.is_stagnation_phase():
			return None
		
		return GameplayHint(
			title="¡Momento del Prestigio!",
			message="Tu progreso se ha ralentizado. Es el momento perfecto para hacer prestigio y obtener multiplicadores permanentes.",
			priority=1,
			action_button="Ir a Prestigio"
		)
	
	def get_phase_name(self) -> str:
		"""Obtiene el nombre amigable de la fase actual."""
		phase_names = {
			GameplayPhase.TUTORIAL_CLICKS: "Tutorial - Primeros Clics",
			GameplayPhase.FIRST_BUILDING: "Primer Generador",
			GameplayPhase.EARLY_AUTOMATION: "Automatización Temprana",
			GameplayPhase.BUILDING_EXPANSION: "Expansión de Imperio",
			GameplayPhase.UPGRADE_PHASE: "Era de las Mejoras",
			GameplayPhase.PRE_PRESTIGE: "Preparando Prestigio",
			GameplayPhase.POST_PRESTIGE: "Maestro del Prestigio"
		}
		return phase_names.get(self.current_phase, "Fase Desconocida")
	
	def get_stats(self) -> Dict:
		"""Obtiene estadísticas del flujo de gameplay."""
		return {
			'current_phase': self.current_phase.value,
			'phase_name': self.get_phase_name(),
			'hints_shown_count': len(self.hints_shown),
			'is_stagnation': self.is_stagnation_phase(),
			'progress_to_next': self.get_progress_to_next_phase()
		}