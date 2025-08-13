"""
Sistema de Optimización UX Móvil para SiKIdle.

Optimizaciones específicas para dispositivos móviles:
- Touch targets optimizados
- Feedback háptico
- Animaciones fluidas
- Resoluciones adaptativas
"""

import logging
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.utils import platform
from typing import Dict, Tuple, Optional, Callable
import time


class MobileOptimizer:
	"""Optimizador para experiencia móvil."""
	
	def __init__(self):
		self.platform = platform
		self.is_mobile = platform in ('android', 'ios')
		self.target_fps = 60
		self.min_touch_size = dp(44)  # Mínimo recomendado
		self.touch_spacing = dp(8)
		
		# Configurar resoluciones objetivo
		self.target_resolutions = {
			'android_small': (360, 640),
			'android_medium': (360, 740), 
			'android_large': (414, 896),
			'ios_standard': (375, 667),
			'ios_large': (414, 896),
			'desktop_mobile_sim': (360, 800)
		}
		
		self._setup_mobile_optimizations()
		logging.info(f"MobileOptimizer initialized for {self.platform}")
	
	def _setup_mobile_optimizations(self):
		"""Configura optimizaciones específicas para móvil."""
		if self.is_mobile:
			# Configurar ventana para móvil
			Window.softinput_mode = 'below_target'
			Window.keyboard_anim_args = {'d': 0.2, 't': 'in_out_expo'}
		else:
			# Simular móvil en desktop
			self.set_mobile_resolution('desktop_mobile_sim')
	
	def set_mobile_resolution(self, resolution_key: str):
		"""Establece resolución móvil específica."""
		if resolution_key in self.target_resolutions:
			width, height = self.target_resolutions[resolution_key]
			Window.size = (width, height)
			Window.top = 100
			Window.left = 100
			logging.info(f"Mobile resolution set: {width}x{height}")
	
	def optimize_touch_target(self, widget, min_size: Optional[int] = None):
		"""Optimiza un widget para touch móvil."""
		target_size = min_size or self.min_touch_size
		
		# Asegurar tamaño mínimo
		if hasattr(widget, 'size_hint') and widget.size_hint == (None, None):
			if widget.width < target_size:
				widget.width = target_size
			if widget.height < target_size:
				widget.height = target_size
		
		# Añadir padding si es necesario
		if hasattr(widget, 'padding'):
			widget.padding = max(widget.padding or 0, self.touch_spacing)
	
	def add_haptic_feedback(self, widget, feedback_type: str = 'light'):
		"""Añade feedback háptico a un widget."""
		if not self.is_mobile:
			return
		
		original_on_press = getattr(widget, 'on_press', None)
		
		def enhanced_on_press(*args):
			self.trigger_haptic(feedback_type)
			if original_on_press:
				original_on_press(*args)
		
		widget.bind(on_press=enhanced_on_press)
	
	def trigger_haptic(self, feedback_type: str = 'light'):
		"""Dispara feedback háptico."""
		if not self.is_mobile:
			return
		
		try:
			if platform == 'android':
				from jnius import autoclass
				PythonActivity = autoclass('org.kivy.android.PythonActivity')
				activity = PythonActivity.mActivity
				Context = autoclass('android.content.Context')
				vibrator = activity.getSystemService(Context.VIBRATOR_SERVICE)
				
				if feedback_type == 'light':
					vibrator.vibrate(50)
				elif feedback_type == 'medium':
					vibrator.vibrate(100)
				elif feedback_type == 'heavy':
					vibrator.vibrate(200)
			
		except Exception as e:
			logging.debug(f"Haptic feedback not available: {e}")
	
	def create_smooth_animation(self, widget, **kwargs):
		"""Crea animación optimizada para móvil."""
		# Configuración por defecto para 60fps
		defaults = {
			't': 'out_expo',
			'd': 0.3
		}
		defaults.update(kwargs)
		
		return Animation(**defaults)
	
	def get_optimal_font_size(self, base_size: int) -> int:
		"""Calcula tamaño de fuente óptimo para la resolución."""
		if Window.width <= 360:
			return int(base_size * 0.9)
		elif Window.width >= 414:
			return int(base_size * 1.1)
		return base_size


class AnimationManager:
	"""Gestor de animaciones optimizadas para móvil."""
	
	def __init__(self):
		self.active_animations = {}
		self.animation_queue = []
		self.max_concurrent = 3  # Límite para performance
	
	def animate_button_press(self, button):
		"""Animación de botón presionado."""
		if button in self.active_animations:
			return
		
		# Escala down y up
		anim = Animation(
			size=(button.width * 0.95, button.height * 0.95),
			duration=0.1,
			t='out_expo'
		) + Animation(
			size=(button.width, button.height),
			duration=0.1,
			t='in_expo'
		)
		
		self.active_animations[button] = anim
		anim.bind(on_complete=lambda *args: self._cleanup_animation(button))
		anim.start(button)
	
	def animate_coin_gain(self, widget, amount: int):
		"""Animación de ganancia de monedas."""
		# Crear label flotante
		from kivy.uix.label import Label
		
		coin_label = Label(
			text=f"+{amount}",
			font_size='16sp',
			color=(1, 1, 0, 1),
			pos=widget.pos
		)
		
		widget.parent.add_widget(coin_label)
		
		# Animación flotante
		anim = Animation(
			y=widget.y + 50,
			opacity=0,
			duration=1.0,
			t='out_expo'
		)
		
		anim.bind(on_complete=lambda *args: widget.parent.remove_widget(coin_label))
		anim.start(coin_label)
	
	def animate_achievement_unlock(self, widget):
		"""Animación de logro desbloqueado."""
		# Efecto de brillo
		original_color = widget.background_color
		
		flash_anim = Animation(
			background_color=(1, 1, 1, 1),
			duration=0.2
		) + Animation(
			background_color=original_color,
			duration=0.2
		)
		
		# Escala
		scale_anim = Animation(
			size=(widget.width * 1.1, widget.height * 1.1),
			duration=0.3,
			t='out_back'
		) + Animation(
			size=(widget.width, widget.height),
			duration=0.3,
			t='in_back'
		)
		
		flash_anim.start(widget)
		scale_anim.start(widget)
	
	def _cleanup_animation(self, widget):
		"""Limpia animación completada."""
		if widget in self.active_animations:
			del self.active_animations[widget]


class PerformanceMonitor:
	"""Monitor de performance para móvil."""
	
	def __init__(self):
		self.fps_samples = []
		self.max_samples = 60
		self.last_frame_time = time.time()
		self.performance_mode = 'high'  # high, medium, low
		
		Clock.schedule_interval(self._update_fps, 1/60)
	
	def _update_fps(self, dt):
		"""Actualiza medición de FPS."""
		current_time = time.time()
		frame_time = current_time - self.last_frame_time
		
		if frame_time > 0:
			fps = 1.0 / frame_time
			self.fps_samples.append(fps)
			
			if len(self.fps_samples) > self.max_samples:
				self.fps_samples.pop(0)
		
		self.last_frame_time = current_time
		self._adjust_performance_mode()
	
	def _adjust_performance_mode(self):
		"""Ajusta modo de performance según FPS."""
		if len(self.fps_samples) < 30:
			return
		
		avg_fps = sum(self.fps_samples[-30:]) / 30
		
		if avg_fps < 30:
			self.performance_mode = 'low'
		elif avg_fps < 45:
			self.performance_mode = 'medium'
		else:
			self.performance_mode = 'high'
	
	def get_fps_stats(self) -> Dict:
		"""Obtiene estadísticas de FPS."""
		if not self.fps_samples:
			return {'avg': 0, 'min': 0, 'max': 0, 'mode': self.performance_mode}
		
		return {
			'avg': sum(self.fps_samples) / len(self.fps_samples),
			'min': min(self.fps_samples),
			'max': max(self.fps_samples),
			'mode': self.performance_mode,
			'samples': len(self.fps_samples)
		}
	
	def should_reduce_effects(self) -> bool:
		"""Determina si reducir efectos visuales."""
		return self.performance_mode == 'low'


# Instancia global
mobile_optimizer = MobileOptimizer()
animation_manager = AnimationManager()
performance_monitor = PerformanceMonitor()