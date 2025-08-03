"""Archivo principal de SiKIdle.

Inicializa la aplicación Kivy e integra todas las pantallas
del juego para crear la experiencia completa de idle clicker.
"""

import os
import sys
import logging
from typing import Optional

# Configurar logging antes de importar Kivy
logging.basicConfig(
	level=logging.INFO,
	format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
	handlers=[
		logging.StreamHandler(sys.stdout),
		logging.FileHandler('sikidle.log', encoding='utf-8')
	]
)

# Configurar Kivy para móvil antes de importar
os.environ['KIVY_WINDOW'] = 'sdl2'
os.environ['KIVY_GL_BACKEND'] = 'gl'

# Importar Kivy después de configuración
from kivy.app import App  # type: ignore
from kivy.uix.screenmanager import ScreenManager  # type: ignore
from kivy.clock import Clock  # type: ignore
from kivy.logger import Logger  # type: ignore

# Importar componentes del juego
from utils.mobile_config import setup_mobile_environment
from utils.save import get_save_manager
from core.game import get_game_state
from ui.loading_screen import LoadingScreen
from ui.start_screen import StartScreen
from ui.main_screen import MainScreen
from ui.settings_screen import SettingsScreen
from ui.stats_screen import StatsScreen
from ui.upgrades_screen import UpgradesScreen


class SiKIdleApp(App):
	"""Aplicación principal de SiKIdle."""
	
	def __init__(self, **kwargs):
		"""Inicializa la aplicación."""
		super().__init__(**kwargs)
		
		self.title = 'SiKIdle - Idle Clicker'
		self.icon = 'assets/icon.png'  # TODO: Crear icono
		
		# Referencias a componentes principales
		self.save_manager: Optional[object] = None
		self.game_state: Optional[object] = None
		self.screen_manager: Optional[ScreenManager] = None
	
	def build(self):
		"""Construye la aplicación principal.
		
		Returns:
			ScreenManager: Gestor de pantallas principal
		"""
		try:
			# Configurar entorno móvil
			setup_mobile_environment()
			
			# Inicializar componentes principales
			self.save_manager = get_save_manager()
			self.game_state = get_game_state()
			
			# Crear gestor de pantallas
			self.screen_manager = ScreenManager()
			
			# Crear y agregar todas las pantallas
			self.create_screens()
			
			# Configurar pantalla inicial
			self.screen_manager.current = 'loading'
			
			# Iniciar sistemas de guardado
			self.save_manager.start_auto_save()
			
			logging.info("SiKIdle iniciado correctamente")
			return self.screen_manager
			
		except Exception as e:
			logging.error(f"Error inicializando aplicación: {e}")
			raise
	
	def create_screens(self):
		"""Crea y registra todas las pantallas del juego."""
		try:
			# Pantalla de carga
			loading_screen = LoadingScreen(name='loading')
			self.screen_manager.add_widget(loading_screen)
			
			# Pantalla de inicio
			start_screen = StartScreen(name='start')
			self.screen_manager.add_widget(start_screen)
			
			# Pantalla principal del juego
			main_screen = MainScreen(name='main')
			self.screen_manager.add_widget(main_screen)
			
			# Pantalla de configuración
			settings_screen = SettingsScreen(name='settings')
			self.screen_manager.add_widget(settings_screen)
			
			# Pantalla de estadísticas
			stats_screen = StatsScreen(name='stats')
			self.screen_manager.add_widget(stats_screen)
			
			# Pantalla de mejoras
			upgrades_screen = UpgradesScreen(name='upgrades')
			self.screen_manager.add_widget(upgrades_screen)
			
			logging.info("Todas las pantallas creadas correctamente")
			
		except Exception as e:
			logging.error(f"Error creando pantallas: {e}")
			raise
	
	def on_start(self):
		"""Método llamado cuando la aplicación inicia."""
		try:
			# Cargar datos guardados
			if self.save_manager:
				self.save_manager.load_game_state()
			
			logging.info("Aplicación iniciada - datos cargados")
			
		except Exception as e:
			logging.error(f"Error en inicio de aplicación: {e}")
	
	def on_pause(self):
		"""Método llamado cuando la aplicación se pausa (Android).
		
		Returns:
			True para permitir pausar la aplicación
		"""
		try:
			# Guardar estado antes de pausar
			if self.save_manager:
				self.save_manager.force_save()
			
			logging.info("Aplicación pausada - estado guardado")
			return True
			
		except Exception as e:
			logging.error(f"Error pausando aplicación: {e}")
			return True
	
	def on_resume(self):
		"""Método llamado cuando la aplicación se reanuda (Android)."""
		try:
			# Recargar estado al reanudar
			if self.save_manager:
				self.save_manager.load_game_state()
			
			logging.info("Aplicación reanudada - estado recargado")
			
		except Exception as e:
			logging.error(f"Error reanudando aplicación: {e}")
	
	def on_stop(self):
		"""Método llamado cuando la aplicación se cierra."""
		try:
			# Detener guardado automático
			if self.save_manager:
				self.save_manager.stop_auto_save()
				self.save_manager.force_save()
			
			logging.info("Aplicación cerrada - estado final guardado")
			
		except Exception as e:
			logging.error(f"Error cerrando aplicación: {e}")


def main():
	"""Función principal para ejecutar el juego."""
	try:
		# Configurar logging específico para esta sesión
		logger = logging.getLogger(__name__)
		logger.info("Iniciando SiKIdle...")
		
		# Crear y ejecutar aplicación
		app = SiKIdleApp()
		app.run()
		
	except KeyboardInterrupt:
		logging.info("Aplicación cerrada por usuario")
	except Exception as e:
		logging.error(f"Error fatal en aplicación: {e}")
		raise
	finally:
		logging.info("SiKIdle finalizado")


if __name__ == '__main__':
	main()
