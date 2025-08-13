"""
SiKIdle - Videojuego idle clicker dungeon crawler
Archivo principal del juego.

Inicializa la aplicación Kivy y configura todos los sistemas del juego.
"""

import sys
import os
import logging
from pathlib import Path

# Configurar logging antes de cualquier import
logging.basicConfig(
	level=logging.INFO,
	format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
	handlers=[
		logging.FileHandler('sikilde.log'),
		logging.StreamHandler(sys.stdout)
	]
)

# Añadir el directorio src al path para imports absolutos
src_path = Path(__file__).parent
if str(src_path) not in sys.path:
	sys.path.insert(0, str(src_path))

# Imports de Kivy
from kivy.app import App
from kivy.config import Config
from kivy.clock import Clock
from kivy.uix.widget import Widget
from kivy.uix.screenmanager import Screen


def configure_kivy():
	"""Configura los parámetros de Kivy para móvil vertical."""
	# Resolución móvil vertical optimizada
	Config.set('graphics', 'width', '360')
	Config.set('graphics', 'height', '800')
	Config.set('graphics', 'minimum_width', '320')
	Config.set('graphics', 'minimum_height', '640')
	Config.set('graphics', 'resizable', False)  # Fijo para simulación móvil
	Config.set('graphics', 'position', 'custom')
	Config.set('graphics', 'left', '100')
	Config.set('graphics', 'top', '100')
	# Optimización táctil
	Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
	Config.set('graphics', 'multisamples', '0')  # Mejor performance móvil


# Aplicar configuración de Kivy
configure_kivy()

# Imports del juego
from ui.navigation.navigation_manager import MainLayout, NavigationManager
from ui.screens.home_screen import HomeScreen
from ui.achievements_screen_simple import AchievementsScreen as AchievementScreen
from ui.screens.settings_screen import SettingsScreen
from ui.screens.combat_screen import CombatScreen
from ui.buildings_screen import BuildingsScreen
from ui.upgrades_screen import UpgradesScreen

from typing import Optional
from traceback import format_exc


class LoadingScreen(Widget):
	"""Pantalla de carga inicial."""
	pass





class GameApp(App):
	"""Aplicación principal del juego SiKIdle."""
	
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.title = "SiKIdle - Dungeon Crawler Idle Game"
		
		# UI
		self.main_layout: Optional[MainLayout] = None
		self.navigation_manager: Optional[NavigationManager] = None
		
		# Estado de la aplicación
		self.is_initialized = False
		self.initialization_error = None
		
		logging.info("GameApp initialized")
	
	def build(self):
		"""Construye la aplicación principal."""
		try:
			# Crear layout principal
			self.main_layout = MainLayout()
			self.navigation_manager = self.main_layout.get_navigation_manager()
			
			# Registrar pantallas
			self._register_screens()
			
			# Configurar navegación inicial
			self._setup_initial_navigation()
			
			# Programar inicialización diferida
			Clock.schedule_once(self._post_init_setup, 0.1)
			
			self.is_initialized = True
			logging.info("GameApp build completed successfully")
			
			return self.main_layout
			
		except Exception as e:
			logging.error(f"Error building app: {e}")
			logging.error(format_exc())
			self.initialization_error = str(e)
			return self._create_error_widget()
	
	def _register_screens(self):
		"""Registra todas las pantallas en el navigation manager."""
		try:
			# Pantalla principal
			self.navigation_manager.register_screen('home', HomeScreen)
			
			# Pantalla de logros para idle clicker
			from ui.screens.achievements_screen_idle import AchievementsScreenIdle
			self.navigation_manager.register_screen('achievements', AchievementsScreenIdle)
			
			# Pantalla de configuración
			self.navigation_manager.register_screen('settings', SettingsScreen)
			
			# Pantallas de gameplay
			self.navigation_manager.register_screen('combat', CombatScreen)
			
			# Pantallas de progresión
			from core.game import get_game_state
			self.navigation_manager.register_screen('upgrades', lambda name: UpgradesScreen(name=name))
			
			# Pantalla de prestigio
			from ui.screens.prestige_screen_simple import PrestigeScreen
			self.navigation_manager.register_screen('prestige', PrestigeScreen)
			
			# Pantalla de tienda premium
			from ui.screens.premium_shop_screen import PremiumShopScreen
			self.navigation_manager.register_screen('shop', PremiumShopScreen)
			
			# Pantalla de carga
			self.navigation_manager.register_screen('loading', LoadingScreen)
			
			logging.info("All screens registered")
			
		except Exception as e:
			logging.error(f"Error registering screens: {e}")
			raise
	
	def _setup_initial_navigation(self):
		"""Configura la navegación inicial."""
		try:
			# Navegar a la pantalla principal
			success = self.navigation_manager.navigate_to('home')
			
			if not success:
				logging.warning("Failed to navigate to home, creating home screen manually")
				home_screen = HomeScreen(name='home')
				self.navigation_manager.add_widget(home_screen)
				self.navigation_manager.current = 'home'
			
			logging.info("Initial navigation setup completed")
			
		except Exception as e:
			logging.error(f"Error setting up initial navigation: {e}")
			raise
	
	def _post_init_setup(self, dt):
		"""Configuración posterior a la inicialización."""
		try:
			logging.info("Post-initialization setup completed")
			
		except Exception as e:
			logging.error(f"Error in post-init setup: {e}")
	
	def _create_error_widget(self) -> Widget:
		"""Crea un widget de error para mostrar cuando falla la inicialización."""
		from kivy.uix.label import Label
		from kivy.uix.boxlayout import BoxLayout
		
		container = BoxLayout(orientation='vertical', padding=20, spacing=20)
		
		error_title = Label(
			text="Error de Inicialización",
			font_size='24sp',
			bold=True,
			size_hint_y=None,
			height=60
		)
		
		error_message = Label(
			text=f"No se pudo inicializar el juego.\n\nError: {self.initialization_error or 'Error desconocido'}",
			font_size='14sp',
			halign='center',
			valign='middle'
		)
		error_message.bind(texture_size=error_message.setter('text_size'))
		
		container.add_widget(error_title)
		container.add_widget(error_message)
		
		return container
	
	def navigate_to(self, screen_name: str, **kwargs):
		"""Shortcut para navegación desde otras partes del código."""
		if self.navigation_manager:
			return self.navigation_manager.navigate_to(screen_name, **kwargs)
		return False
	
	def on_start(self):
		"""Callback ejecutado cuando la app inicia."""
		logging.info("GameApp started")
		
		# Programar verificación de inicialización
		Clock.schedule_once(self._check_initialization, 1.0)
	
	def _check_initialization(self, dt):
		"""Verifica que la inicialización fue exitosa."""
		if not self.is_initialized:
			logging.error("App failed to initialize properly")
		else:
			logging.info("App initialization verified successfully")
	
	def on_stop(self):
		"""Callback ejecutado cuando la app se cierra."""
		try:
			logging.info("GameApp stopping...")
			logging.info("GameApp stopped successfully")
			
		except Exception as e:
			logging.error(f"Error during app shutdown: {e}")
	
	def on_pause(self):
		"""Callback para cuando la app se pausa (móvil)."""
		try:
			logging.info("Game paused")
			return True
			
		except Exception as e:
			logging.error(f"Error during pause: {e}")
			return True
	
	def on_resume(self):
		"""Callback para cuando la app se reanuda (móvil)."""
		try:
			logging.info("Game resumed")
			
		except Exception as e:
			logging.error(f"Error during resume: {e}")


def main():
	"""Función principal de entrada."""
	try:
		logging.info("Starting SiKIdle...")
		
		# Crear y ejecutar la aplicación
		app = GameApp()
		app.run()
		
		logging.info("SiKIdle shutdown complete")
		
	except KeyboardInterrupt:
		logging.info("Game interrupted by user")
	except Exception as e:
		logging.error(f"Fatal error: {e}")
		logging.error(format_exc())
		sys.exit(1)


if __name__ == '__main__':
	main()
