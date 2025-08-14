"""
Sistema de Feedback Visual para SiKIdle.

Mejoras visuales para una experiencia más satisfactoria:
- Notación científica para números grandes
- Animaciones de feedback
- Efectos visuales para acciones
"""

import math
from kivy.animation import Animation
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle
from kivy.clock import Clock


class NumberFormatter:
	"""Formateador de números grandes."""
	
	@staticmethod
	def format_number(number: float) -> str:
		"""Formatea números grandes con notación amigable."""
		if number < 1000:
			return str(int(number))
		elif number < 1000000:
			return f"{number/1000:.1f}K"
		elif number < 1000000000:
			return f"{number/1000000:.1f}M"
		elif number < 1000000000000:
			return f"{number/1000000000:.1f}B"
		else:
			return f"{number/1000000000000:.1f}T"
	
	@staticmethod
	def format_currency(amount: float) -> str:
		"""Formatea monedas con símbolo."""
		return f"💰 {NumberFormatter.format_number(amount)}"
	
	@staticmethod
	def format_per_second(rate: float) -> str:
		"""Formatea producción por segundo."""
		return f"{NumberFormatter.format_number(rate)}/s"


class VisualEffects:
	"""Efectos visuales para feedback."""
	
	@staticmethod
	def create_floating_text(parent, text: str, start_pos: tuple, color=(1, 1, 0, 1)):
		"""Crea texto flotante que desaparece."""
		label = Label(
			text=text,
			font_size='16sp',
			color=color,
			pos=start_pos,
			size_hint=(None, None),
			size=(100, 30)
		)
		
		parent.add_widget(label)
		
		# Animación flotante
		anim = Animation(
			y=start_pos[1] + 50,
			opacity=0,
			duration=1.5,
			t='out_expo'
		)
		
		anim.bind(on_complete=lambda *args: parent.remove_widget(label))
		anim.start(label)
		
		return label
	
	@staticmethod
	def pulse_widget(widget, scale=1.1, duration=0.2):
		"""Efecto de pulso en un widget."""
		original_size = widget.size
		
		# Animación de escala
		pulse_out = Animation(
			size=(original_size[0] * scale, original_size[1] * scale),
			duration=duration,
			t='out_expo'
		)
		pulse_in = Animation(
			size=original_size,
			duration=duration,
			t='in_expo'
		)
		
		sequence = pulse_out + pulse_in
		sequence.start(widget)
	
	@staticmethod
	def flash_widget(widget, color=(1, 1, 1, 0.5), duration=0.3):
		"""Efecto de flash en un widget."""
		with widget.canvas.after:
			Color(*color)
			flash_rect = Rectangle(pos=widget.pos, size=widget.size)
		
		# Animación de desvanecimiento
		def update_flash(dt, progress):
			alpha = color[3] * (1 - progress)
			flash_rect.rgba = (*color[:3], alpha)
		
		def remove_flash(*args):
			widget.canvas.after.remove(flash_rect)
		
		Clock.schedule_interval(lambda dt: update_flash(dt, min(1.0, Clock.get_time() % duration / duration)), 1/60)
		Clock.schedule_once(remove_flash, duration)


class ProgressIndicators:
	"""Indicadores de progreso visual."""
	
	@staticmethod
	def create_progress_bar(current: float, target: float, width: int = 200):
		"""Crea una barra de progreso simple."""
		from kivy.uix.progressbar import ProgressBar
		
		progress_bar = ProgressBar(
			max=target,
			value=current,
			size_hint=(None, None),
			size=(width, 20)
		)
		
		return progress_bar
	
	@staticmethod
	def animate_progress_bar(progress_bar, target_value: float, duration: float = 1.0):
		"""Anima una barra de progreso hacia un valor."""
		anim = Animation(
			value=target_value,
			duration=duration,
			t='out_expo'
		)
		anim.start(progress_bar)


class SatisfactionFeedback:
	"""Sistema de feedback de satisfacción."""
	
	def __init__(self, game_state):
		self.game_state = game_state
		self.last_click_time = 0
		self.click_combo = 0
	
	def on_click_feedback(self, widget, coins_earned: int):
		"""Feedback visual para clics."""
		# Texto flotante con monedas ganadas
		VisualEffects.create_floating_text(
			widget.parent,
			f"+{NumberFormatter.format_number(coins_earned)}",
			widget.pos,
			(1, 1, 0, 1)
		)
		
		# Efecto de pulso en el botón
		VisualEffects.pulse_widget(widget, 1.05, 0.1)
		
		# Combo de clics rápidos
		import time
		current_time = time.time()
		if current_time - self.last_click_time < 0.5:
			self.click_combo += 1
			if self.click_combo >= 5:
				self._trigger_combo_effect(widget)
				self.click_combo = 0
		else:
			self.click_combo = 0
		
		self.last_click_time = current_time
	
	def on_building_purchase(self, widget, building_name: str):
		"""Feedback visual para compra de edificios."""
		# Flash verde para compra exitosa
		VisualEffects.flash_widget(widget, (0, 1, 0, 0.3), 0.5)
		
		# Texto de confirmación
		VisualEffects.create_floating_text(
			widget.parent,
			f"¡{building_name} comprado!",
			(widget.x, widget.y + widget.height),
			(0, 1, 0, 1)
		)
	
	def on_achievement_unlock(self, widget, achievement_name: str):
		"""Feedback visual para logros desbloqueados."""
		# Efecto dorado
		VisualEffects.flash_widget(widget, (1, 0.8, 0, 0.7), 1.0)
		
		# Texto especial
		VisualEffects.create_floating_text(
			widget.parent,
			f"🏆 {achievement_name}",
			widget.pos,
			(1, 0.8, 0, 1)
		)
	
	def _trigger_combo_effect(self, widget):
		"""Efecto especial para combo de clics."""
		# Efecto de arcoíris
		colors = [
			(1, 0, 0, 0.5),  # Rojo
			(1, 0.5, 0, 0.5),  # Naranja
			(1, 1, 0, 0.5),  # Amarillo
			(0, 1, 0, 0.5),  # Verde
			(0, 0, 1, 0.5),  # Azul
		]
		
		for i, color in enumerate(colors):
			Clock.schedule_once(
				lambda dt, c=color: VisualEffects.flash_widget(widget, c, 0.2),
				i * 0.1
			)
		
		# Texto de combo
		VisualEffects.create_floating_text(
			widget.parent,
			"🌟 COMBO! 🌟",
			(widget.x, widget.y + widget.height + 20),
			(1, 0, 1, 1)
		)


# Instancias globales
number_formatter = NumberFormatter()
visual_effects = VisualEffects()
progress_indicators = ProgressIndicators()