"""Pantalla de carga para SiKIdle.

Muestra el logo y progreso de carga inicial del juego.
Incluye tiempo mínimo para mostrar branding.
"""

from kivy.uix.boxlayout import BoxLayout  # type: ignore
from kivy.uix.label import Label  # type: ignore
from kivy.uix.progressbar import ProgressBar  # type: ignore
from kivy.clock import Clock  # type: ignore
from kivy.animation import Animation  # type: ignore
import logging
import time
from typing import Any

from ui.screen_manager import SiKIdleScreen


class LoadingScreen(SiKIdleScreen):
	"""Pantalla de carga inicial del juego."""
	
	def __init__(self, **kwargs: Any):
		"""Inicializa la pantalla de carga."""
		super().__init__(**kwargs)
		
		self.loading_start_time = 0.0
		self.min_loading_time = 2.5  # Mínimo 2.5 segundos para mostrar branding
		self.progress_bar = None
		self.status_label = None
		
		self.build_ui()
		
	def build_ui(self):
		"""Construye la interfaz de la pantalla de carga."""
		# Layout principal
		main_layout = BoxLayout(
			orientation='vertical',
			padding=[40, 80, 40, 80],
			spacing=40
		)
		
		# Espacio superior
		main_layout.add_widget(Label(size_hint=(1, 0.3)))
		
		# Logo del juego
		logo_label = Label(
			text='SiKIdle',
			font_size='64sp',
			size_hint=(1, 0.2),
			bold=True,
			color=[0.2, 0.8, 1, 1]  # Azul claro
		)
		main_layout.add_widget(logo_label)
		
		# Subtítulo
		subtitle_label = Label(
			text='Idle Clicker Game',
			font_size='20sp',
			size_hint=(1, 0.1),
			color=[0.7, 0.7, 0.7, 1]  # Gris
		)
		main_layout.add_widget(subtitle_label)
		
		# Espacio medio
		main_layout.add_widget(Label(size_hint=(1, 0.2)))
		
		# Barra de progreso
		self.progress_bar = ProgressBar(
			max=100,
			value=0,
			size_hint=(1, None),
			height='10dp'
		)
		main_layout.add_widget(self.progress_bar)
		
		# Estado de carga
		self.status_label = Label(
			text='Inicializando...',
			font_size='16sp',
			size_hint=(1, 0.1),
			color=[0.9, 0.9, 0.9, 1]
		)
		main_layout.add_widget(self.status_label)
		
		# Espacio inferior
		main_layout.add_widget(Label(size_hint=(1, 0.3)))
		
		self.add_widget(main_layout)
		
		logging.info("Pantalla de carga construida")
	
	def start_loading(self):
		"""Inicia el proceso de carga."""
		self.loading_start_time = time.time()
		
		# Resetear progreso
		if self.progress_bar:
			self.progress_bar.value = 0
		if self.status_label:
			self.status_label.text = 'Inicializando...'
		
		# Iniciar simulación de carga
		Clock.schedule_interval(self.update_progress, 0.1)
		
		logging.info("Proceso de carga iniciado")
	
	def update_progress(self, dt: float) -> bool:
		"""Actualiza el progreso de carga.
		
		Args:
			dt: Delta time desde la última actualización
			
		Returns:
			False para cancelar el schedule si terminó
		"""
		if not self.progress_bar or not self.status_label:
			return False
			
		# Simular progreso de carga
		current_progress = self.progress_bar.value
		
		if current_progress < 30:
			self.status_label.text = 'Cargando base de datos...'
			self.progress_bar.value += 3
		elif current_progress < 60:
			self.status_label.text = 'Inicializando sistema de guardado...'
			self.progress_bar.value += 2
		elif current_progress < 85:
			self.status_label.text = 'Preparando interfaz...'
			self.progress_bar.value += 1.5
		elif current_progress < 100:
			self.status_label.text = 'Finalizando...'
			self.progress_bar.value += 2
		
		# Verificar si el progreso y tiempo mínimo están completos
		if (self.progress_bar.value >= 100 and 
			time.time() - self.loading_start_time >= self.min_loading_time):
			
			self.status_label.text = '¡Listo!'
			
			# Animar desvanecimiento y cambiar pantalla
			Clock.schedule_once(self.finish_loading, 0.5)
			return False  # Cancelar este schedule
			
		return True  # Continuar actualizando
	
	def finish_loading(self, dt: float):
		"""Termina la carga y navega a la pantalla de inicio.
		
		Args:
			dt: Delta time (no usado)
		"""
		logging.info("Carga completada, navegando a pantalla de inicio")
		
		# Navegar a la pantalla de inicio
		if self.manager_ref:
			self.manager_ref.show_start()
	
	def on_enter(self, *args):
		"""Método llamado cuando se entra a la pantalla."""
		super().on_enter(*args)
		
		# Iniciar carga automáticamente al entrar
		Clock.schedule_once(lambda dt: self.start_loading(), 0.1)
	
	def on_leave(self, *args):
		"""Método llamado cuando se sale de la pantalla."""
		super().on_leave(*args)
		
		# Limpiar cualquier schedule activo
		Clock.unschedule(self.update_progress)
