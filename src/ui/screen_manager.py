"""Gestor de pantallas para SiKIdle.

Maneja la navegación entre las diferentes pantallas del juego
usando Kivy ScreenManager para transiciones suaves.
"""

from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition  # type: ignore
from kivy.clock import Clock  # type: ignore
import logging


class SiKIdleScreenManager(ScreenManager):
	"""Gestor principal de pantallas para SiKIdle."""
	
	def __init__(self, **kwargs):
		"""Inicializa el gestor de pantallas."""
		super().__init__(**kwargs)
		
		# Configurar transición por defecto
		self.transition = SlideTransition()
		self.transition.duration = 0.3  # Transición de 300ms
		
		# Referencias a pantallas para fácil acceso
		self.loading_screen = None
		self.start_screen = None
		self.main_screen = None
		self.settings_screen = None
		self.stats_screen = None
		self.upgrades_screen = None
		
		logging.info("Gestor de pantallas inicializado")
	
	def add_screens(self):
		"""Añade todas las pantallas al gestor."""
		from ui.loading_screen import LoadingScreen
		from ui.start_screen import StartScreen
		from ui.main_screen import MainScreen
		from ui.settings_screen import SettingsScreen
		from ui.stats_screen import StatsScreen
		from ui.upgrades_screen import UpgradesScreen
		
		# Crear e inicializar pantallas
		self.loading_screen = LoadingScreen(name='loading')
		self.start_screen = StartScreen(name='start')
		self.main_screen = MainScreen(name='main')
		self.settings_screen = SettingsScreen(name='settings')
		self.stats_screen = StatsScreen(name='stats')
		self.upgrades_screen = UpgradesScreen(name='upgrades')
		
		# Añadir pantallas al gestor
		self.add_widget(self.loading_screen)
		self.add_widget(self.start_screen)
		self.add_widget(self.main_screen)
		self.add_widget(self.settings_screen)
		self.add_widget(self.stats_screen)
		self.add_widget(self.upgrades_screen)
		
		logging.info("Todas las pantallas añadidas al gestor")
	
	def show_loading(self):
		"""Muestra la pantalla de carga."""
		self.current = 'loading'
		if self.loading_screen:
			self.loading_screen.start_loading()
	
	def show_start(self):
		"""Muestra la pantalla de inicio."""
		self.current = 'start'
		if self.start_screen:
			self.start_screen.on_enter()
	
	def show_main_game(self):
		"""Muestra la pantalla principal del juego."""
		self.current = 'main'
		if self.main_screen:
			self.main_screen.on_enter()
	
	def show_settings(self):
		"""Muestra la pantalla de configuración."""
		self.current = 'settings'
		if self.settings_screen:
			self.settings_screen.on_enter()
	
	def show_stats(self):
		"""Muestra la pantalla de estadísticas."""
		self.current = 'stats'
		if self.stats_screen:
			self.stats_screen.on_enter()
	
	def show_upgrades(self):
		"""Muestra la pantalla de mejoras."""
		self.current = 'upgrades'
		if self.upgrades_screen:
			self.upgrades_screen.on_enter()
	
	def go_back(self):
		"""Navega hacia atrás según la pantalla actual."""
		current = self.current
		
		if current == 'main':
			self.show_start()
		elif current in ['settings', 'stats']:
			self.show_start()
		elif current == 'upgrades':
			self.show_main_game()
		else:
			# Por defecto ir a inicio
			self.show_start()
		
		logging.debug(f"Navegación hacia atrás desde {current}")


class SiKIdleScreen(Screen):
	"""Clase base para todas las pantallas de SiKIdle."""
	
	def __init__(self, **kwargs):
		"""Inicializa la pantalla base."""
		super().__init__(**kwargs)
		self.manager_ref = None
	
	def set_manager_reference(self, manager: SiKIdleScreenManager):
		"""Establece referencia al gestor de pantallas.
		
		Args:
			manager: Referencia al gestor principal
		"""
		self.manager_ref = manager
	
	def on_enter(self, *args):
		"""Método llamado cuando se entra a la pantalla."""
		logging.debug(f"Entrando a pantalla: {self.name}")
	
	def on_leave(self, *args):
		"""Método llamado cuando se sale de la pantalla."""
		logging.debug(f"Saliendo de pantalla: {self.name}")
	
	def navigate_to(self, screen_name: str):
		"""Navega a una pantalla específica.
		
		Args:
			screen_name: Nombre de la pantalla destino
		"""
		if self.manager_ref:
			if screen_name == 'start':
				self.manager_ref.show_start()
			elif screen_name == 'main':
				self.manager_ref.show_main_game()
			elif screen_name == 'settings':
				self.manager_ref.show_settings()
			elif screen_name == 'stats':
				self.manager_ref.show_stats()
			elif screen_name == 'upgrades':
				self.manager_ref.show_upgrades()
		else:
			logging.warning(f"No se puede navegar a {screen_name}: sin referencia al manager")
	
	def go_back(self):
		"""Navega hacia atrás."""
		if self.manager_ref:
			self.manager_ref.go_back()
	
	def schedule_update(self, callback, interval: float = 1.0):
		"""Programa una actualización periódica.
		
		Args:
			callback: Función a llamar periódicamente
			interval: Intervalo en segundos
		"""
		Clock.schedule_interval(callback, interval)
	
	def unschedule_update(self, callback):
		"""Cancela una actualización programada.
		
		Args:
			callback: Función a cancelar
		"""
		Clock.unschedule(callback)
