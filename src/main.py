"""Archivo principal de SiKIdle.

Inicializa la aplicación Kivy e integra todas las pantallas
del juego para crear la experiencia completa de idle clicker.
"""

import logging
import os
import sys

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

from core.game import get_game_state
from ui.loading_screen import LoadingScreen
from ui.main_screen import MainScreen
from ui.settings_screen import SettingsScreen
from ui.start_screen import StartScreen
from ui.stats_screen import StatsScreen
from ui.upgrades_screen import UpgradesScreen
from ui.screen_manager import SiKIdleScreenManager

# Importar componentes del juego
from utils.mobile_config import setup_mobile_environment
from utils.save import get_save_manager
from typing import Any, Optional


class SiKIdleApp(App):
	"""Aplicación principal de SiKIdle."""

	def __init__(self, **kwargs: Any) -> None:
		"""Inicializa la aplicación."""
		super().__init__(**kwargs)

		self.title = 'SiKIdle - Idle Clicker'
		self.icon = 'assets/icon.png'  # TODO: Crear icono

		# Referencias a componentes principales
		self.save_manager: Optional[object] = None
		self.game_state: Optional[object] = None
		self.screen_manager: Optional[SiKIdleScreenManager] = None

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

			# Crear contenedor principal con menú lateral
			from ui.screen_manager import SiKIdleMainContainer
			self.main_container = SiKIdleMainContainer()
			self.screen_manager = self.main_container.get_screen_manager()

			# Crear y agregar todas las pantallas
			self.create_screens()

			# Configurar pantalla inicial
			self.screen_manager.current = 'loading'
			self.screen_manager.show_loading()

			# Iniciar sistemas de guardado
			self.save_manager.start_auto_save()

			logging.info("SiKIdle iniciado correctamente")
			return self.main_container

		except Exception as e:
			logging.error(f"Error inicializando aplicación: {e}")
			raise

	def create_screens(self):
		"""Crea y registra todas las pantallas del juego."""
		try:
			# Usar el método add_screens del screen manager
			self.screen_manager.add_screens()

			# Configurar referencias del manager en todas las pantallas
			for screen in self.screen_manager.screens:
				if hasattr(screen, 'set_manager_reference'):
					screen.set_manager_reference(self.screen_manager)

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
