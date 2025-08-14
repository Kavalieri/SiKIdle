"""Sistema de efectos visuales dinámicos para SiKIdle.

Proporciona efectos visuales para combate, progreso, logros y eventos especiales.
Inspirado en los mejores idle clickers del mercado.
"""

import logging
import random
from typing import Dict, List, Optional, Tuple

from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.graphics import Color, Ellipse, Line, Rectangle
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.vector import Vector

from core.visual_assets import VisualAssetManager, EffectType

logger = logging.getLogger(__name__)


class VisualEffect(Widget):
	"""Clase base para efectos visuales."""

	def __init__(self, duration: float = 1.0, **kwargs):
		super().__init__(**kwargs)
		self.duration = duration
		self.visual_manager = VisualAssetManager()

	def play(self, callback=None):
		"""Reproduce el efecto visual."""
		raise NotImplementedError

	def stop(self):
		"""Detiene el efecto visual."""
		pass


class DamageNumberEffect(VisualEffect):
	"""Efecto de números de daño flotantes."""

	def __init__(self, damage: int, is_critical: bool = False, **kwargs):
		super().__init__(duration=1.5, **kwargs)
		self.damage = damage
		self.is_critical = is_critical

		# Configurar el label de daño
		self.damage_label = Label(
			text=str(damage),
			font_size="20sp" if not is_critical else "28sp",
			bold=True,
			color=(1, 1, 1, 1) if not is_critical else (1, 1, 0, 1),
			size_hint=(None, None),
			size=(100, 50),
		)

		if is_critical:
			self.damage_label.text = f"CRÍTICO!\n{damage}"
			self.damage_label.color = (1, 0.8, 0, 1)  # Dorado

		self.add_widget(self.damage_label)

	def play(self, start_pos: Tuple[float, float], callback=None):
		"""Reproduce el efecto de número de daño."""
		self.pos = start_pos

		# Animación de movimiento hacia arriba y desvanecimiento
		end_pos = (start_pos[0] + random.randint(-50, 50), start_pos[1] + 100)

		move_anim = Animation(pos=end_pos, duration=self.duration, transition="out_quart")

		fade_anim = Animation(opacity=0, duration=self.duration * 0.7, transition="out_quad")

		# Efecto de escala para críticos
		if self.is_critical:
			scale_anim = Animation(size=(120, 60), duration=0.2, transition="out_back") + Animation(
				size=(100, 50), duration=0.3, transition="in_back"
			)
			scale_anim.start(self.damage_label)

		move_anim.start(self)
		fade_anim.start(self)

		# Remover el efecto después de la animación
		Clock.schedule_once(lambda dt: self._cleanup(callback), self.duration)

	def _cleanup(self, callback):
		"""Limpia el efecto y ejecuta callback."""
		if self.parent:
			self.parent.remove_widget(self)
		if callback:
			callback()


class EnemyEffectRing(VisualEffect):
	"""Efecto de anillo alrededor de enemigos."""

	def __init__(self, effect_type: EffectType, **kwargs):
		super().__init__(duration=2.0, **kwargs)
		self.effect_type = effect_type

		# Crear scatter para rotación
		from kivy.uix.scatter import Scatter

		self.effect_scatter = Scatter(
			size_hint=(None, None),
			size=(150, 150),
			do_rotation=True,
			do_translation=False,
			rotation=0,
		)

		# Crear imagen del efecto
		self.effect_image = Image(
			source=self.visual_manager.get_effect_path(effect_type),
			size_hint=(1, 1),
			allow_stretch=True,
		)

		self.effect_scatter.add_widget(self.effect_image)
		self.add_widget(self.effect_scatter)

	def play(self, enemy_pos: Tuple[float, float], callback=None):
		"""Reproduce el efecto de anillo en el enemigo."""
		# Centrar el efecto en el enemigo
		self.pos = (
			enemy_pos[0] - self.effect_scatter.width / 2,
			enemy_pos[1] - self.effect_scatter.height / 2,
		)

		# Animación de rotación y pulsación
		rotation_anim = Animation(rotation=360, duration=self.duration, transition="linear")
		rotation_anim.repeat = True

		pulse_anim = Animation(size=(160, 160), duration=0.5, transition="in_out_sine") + Animation(
			size=(140, 140), duration=0.5, transition="in_out_sine"
		)
		pulse_anim.repeat = True

		rotation_anim.start(self.effect_scatter)
		pulse_anim.start(self.effect_scatter)

		# Programar limpieza
		Clock.schedule_once(lambda dt: self._cleanup(callback), self.duration)

	def _cleanup(self, callback):
		"""Limpia el efecto."""
		if self.parent:
			self.parent.remove_widget(self)
		if callback:
			callback()


class LevelUpEffect(VisualEffect):
	"""Efecto de subida de nivel."""

	def __init__(self, new_level: int, **kwargs):
		super().__init__(duration=3.0, **kwargs)
		self.new_level = new_level

		# Crear elementos visuales
		self._create_visual_elements()

	def _create_visual_elements(self):
		"""Crea los elementos visuales del efecto."""
		# Fondo semi-transparente
		with self.canvas.before:
			Color(0, 0, 0, 0.7)
			self.bg_rect = Rectangle(pos=self.pos, size=self.size)

		# Label principal
		self.level_label = Label(
			text=f"¡NIVEL {self.new_level}!",
			font_size="36sp",
			bold=True,
			color=(1, 1, 0, 1),
			size_hint=(None, None),
			size=(300, 100),
			halign="center",
			valign="middle",
		)
		self.level_label.text_size = self.level_label.size
		self.add_widget(self.level_label)

		# Partículas de celebración
		self.particles = []
		for i in range(20):
			particle = Widget(size=(10, 10))
			with particle.canvas:
				Color(random.random(), random.random(), 1, 1)
				Ellipse(pos=particle.pos, size=particle.size)
			self.particles.append(particle)
			self.add_widget(particle)

	def play(self, center_pos: Tuple[float, float], callback=None):
		"""Reproduce el efecto de subida de nivel."""
		# Centrar el efecto
		self.level_label.pos = (
			center_pos[0] - self.level_label.width / 2,
			center_pos[1] - self.level_label.height / 2,
		)

		# Animación del texto principal
		text_anim = (
			Animation(font_size="48sp", duration=0.5, transition="out_back")
			+ Animation(font_size="36sp", duration=0.5, transition="in_back")
			+ Animation(opacity=0, duration=1.0, transition="out_quad")
		)
		text_anim.start(self.level_label)

		# Animación de partículas
		for i, particle in enumerate(self.particles):
			# Posición inicial en el centro
			particle.pos = center_pos

			# Dirección aleatoria
			angle = random.uniform(0, 360)
			distance = random.uniform(100, 200)
			end_pos = (
				center_pos[0] + distance * Vector(1, 0).rotate(angle).x,
				center_pos[1] + distance * Vector(1, 0).rotate(angle).y,
			)

			# Animación de explosión
			particle_anim = Animation(pos=end_pos, opacity=0, duration=2.0, transition="out_quad")
			particle_anim.start(particle)

		# Programar limpieza
		Clock.schedule_once(lambda dt: self._cleanup(callback), self.duration)

	def _cleanup(self, callback):
		"""Limpia el efecto."""
		if self.parent:
			self.parent.remove_widget(self)
		if callback:
			callback()


class WorldTransitionEffect(VisualEffect):
	"""Efecto de transición entre mundos."""

	def __init__(self, from_world: str, to_world: str, **kwargs):
		super().__init__(duration=2.0, **kwargs)
		self.from_world = from_world
		self.to_world = to_world

		# Crear elementos de transición
		self._create_transition_elements()

	def _create_transition_elements(self):
		"""Crea los elementos de la transición."""
		# Overlay oscuro
		with self.canvas.before:
			Color(0, 0, 0, 0)
			self.overlay = Rectangle(pos=self.pos, size=self.size)

		# Label de transición
		self.transition_label = Label(
			text=f"Viajando a...\n{self.to_world}",
			font_size="24sp",
			bold=True,
			color=(1, 1, 1, 1),
			size_hint=(None, None),
			size=(300, 100),
			halign="center",
			valign="middle",
		)
		self.transition_label.text_size = self.transition_label.size
		self.add_widget(self.transition_label)

	def play(self, callback=None):
		"""Reproduce el efecto de transición."""
		# Centrar el label
		self.transition_label.center = self.center

		# Animación de fade in/out
		fade_in = Animation(opacity=0.8, duration=0.5, transition="in_quad")

		hold = Animation(opacity=0.8, duration=1.0)

		fade_out = Animation(opacity=0, duration=0.5, transition="out_quad")

		full_anim = fade_in + hold + fade_out
		full_anim.bind(on_complete=lambda *args: self._cleanup(callback))
		full_anim.start(self.overlay)

		# Animación del texto
		text_anim = (
			Animation(opacity=0, duration=0.5)
			+ Animation(opacity=1, duration=0.5)
			+ Animation(opacity=1, duration=1.0)
			+ Animation(opacity=0, duration=0.5)
		)
		text_anim.start(self.transition_label)

	def _cleanup(self, callback):
		"""Limpia el efecto."""
		if self.parent:
			self.parent.remove_widget(self)
		if callback:
			callback()


class VisualEffectsManager:
	"""Gestor central de efectos visuales."""

	def __init__(self, parent_widget: Widget):
		"""Inicializa el gestor de efectos."""
		self.parent_widget = parent_widget
		self.active_effects: List[VisualEffect] = []
		self.visual_manager = VisualAssetManager()

		logger.info("VisualEffectsManager inicializado")

	def show_damage_number(self, damage: int, pos: Tuple[float, float], is_critical: bool = False):
		"""Muestra un número de daño flotante."""
		effect = DamageNumberEffect(damage, is_critical)
		self.parent_widget.add_widget(effect)
		self.active_effects.append(effect)

		effect.play(pos, lambda: self._remove_effect(effect))

	def show_enemy_effect(self, effect_type: EffectType, enemy_pos: Tuple[float, float]):
		"""Muestra un efecto alrededor de un enemigo."""
		effect = EnemyEffectRing(effect_type)
		self.parent_widget.add_widget(effect)
		self.active_effects.append(effect)

		effect.play(enemy_pos, lambda: self._remove_effect(effect))

	def show_level_up(self, new_level: int, center_pos: Tuple[float, float]):
		"""Muestra el efecto de subida de nivel."""
		effect = LevelUpEffect(new_level)
		self.parent_widget.add_widget(effect)
		self.active_effects.append(effect)

		effect.play(center_pos, lambda: self._remove_effect(effect))

	def show_world_transition(self, from_world: str, to_world: str):
		"""Muestra el efecto de transición entre mundos."""
		effect = WorldTransitionEffect(from_world, to_world)
		effect.size = self.parent_widget.size
		effect.pos = self.parent_widget.pos

		self.parent_widget.add_widget(effect)
		self.active_effects.append(effect)

		effect.play(lambda: self._remove_effect(effect))

	def _remove_effect(self, effect: VisualEffect):
		"""Remueve un efecto de la lista activa."""
		if effect in self.active_effects:
			self.active_effects.remove(effect)

	def clear_all_effects(self):
		"""Limpia todos los efectos activos."""
		for effect in self.active_effects[:]:
			effect.stop()
			if effect.parent:
				effect.parent.remove_widget(effect)

		self.active_effects.clear()
		logger.info("Todos los efectos visuales limpiados")
