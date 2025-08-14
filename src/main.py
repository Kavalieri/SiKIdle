"""
SiKIdle - Videojuego idle clicker dungeon crawler
Archivo principal del juego.

Inicializa la aplicación Kivy y configura todos los sistemas del juego.
"""

import logging
import sys
from pathlib import Path
from traceback import format_exc

from kivy.app import App
from kivy.clock import Clock
from kivy.config import Config
from kivy.uix.widget import Widget

# Configurar path para imports absolutos
src_path = Path(__file__).parent
if str(src_path) not in sys.path:
	sys.path.insert(0, str(src_path))

# Imports del juego (después de configurar path)
from ui.navigation.navigation_manager import MainLayout, NavigationManager
from ui.screens.home_screen import HomeScreen
from ui.screens.settings_screen import SettingsScreen
from ui.screens.combat_screen import CombatScreen
from ui.screens.equipment_screen import EquipmentScreen
from ui.screens.exploration_screen import ExplorationScreen
from ui.upgrades_screen import UpgradesScreen

# Imports de la nueva interfaz premium
from ui.integrated_ui_system import IntegratedUIManager, get_ui_manager
from ui.screens.enhanced_combat_screen import EnhancedCombatScreen
from ui.world_selection_screen import WorldSelectionScreen


def setup_logging():
	"""Configura el logging usando el directorio de usuario."""
	from utils.paths import ensure_directories, get_user_data_dir

	ensure_directories()
	log_file = get_user_data_dir() / "logs" / "sikilde.log"

	# Limpiar handlers existentes para evitar bucles
	root_logger = logging.getLogger()
	for handler in root_logger.handlers[:]:
		root_logger.removeHandler(handler)

	# Configurar logging con handlers específicos
	logging.basicConfig(
		level=logging.INFO,
		format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
		handlers=[
			logging.FileHandler(log_file, encoding="utf-8"),
			logging.StreamHandler(sys.stdout),
		],
		force=True,
	)

	# Configurar el logger de Kivy para evitar bucles
	kivy_logger = logging.getLogger("kivy")
	kivy_logger.propagate = False

	# Crear un handler específico para Kivy que no cause bucles
	kivy_handler = logging.FileHandler(log_file, encoding="utf-8")
	kivy_handler.setFormatter(logging.Formatter("%(asctime)s - KIVY - %(levelname)s - %(message)s"))
	kivy_logger.addHandler(kivy_handler)

	logging.info(f"Log configurado en: {log_file}")


def configure_kivy():
	"""Configura los parámetros de Kivy para móvil vertical."""
	# Resolución móvil vertical optimizada
	Config.set("graphics", "width", "360")
	Config.set("graphics", "height", "800")
	Config.set("graphics", "minimum_width", "320")
	Config.set("graphics", "minimum_height", "640")
	Config.set("graphics", "resizable", False)  # Fijo para simulación móvil
	Config.set("graphics", "position", "custom")
	Config.set("graphics", "left", "100")
	Config.set("graphics", "top", "100")
	# Optimización táctil
	Config.set("input", "mouse", "mouse,multitouch_on_demand")
	Config.set("graphics", "multisamples", "0")  # Mejor performance móvil


# Configurar logging y Kivy al inicio
setup_logging()
configure_kivy()


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
		"""Construye la aplicación principal con la nueva interfaz premium."""
		try:
			# Usar el nuevo sistema de UI integrado
			ui_manager = get_ui_manager()
			self.main_layout = ui_manager.initialize(self)

			# Mantener referencia al navigation manager para compatibilidad
			self.navigation_manager = ui_manager

			# Registrar pantallas adicionales si es necesario
			self._register_additional_screens()

			# Programar inicialización diferida
			Clock.schedule_once(self._post_init_setup, 0.1)

			self.is_initialized = True
			logging.info("GameApp build completed successfully with PREMIUM UI")

			return self.main_layout

		except Exception as e:
			logging.error(f"Error building app with premium UI: {e}")
			logging.error(format_exc())
			self.initialization_error = str(e)
			# Fallback a la interfaz antigua si falla la premium
			return self._build_fallback_ui()

	def _register_additional_screens(self):
		"""Registra pantallas adicionales si es necesario."""
		# El nuevo sistema UI ya incluye las pantallas principales
		# Aquí podemos agregar pantallas específicas si es necesario
		pass

	def _build_fallback_ui(self):
		"""Construye la interfaz antigua como fallback."""
		try:
			# Crear layout principal antiguo
			self.main_layout = MainLayout()
			self.navigation_manager = self.main_layout.get_navigation_manager()

			# Registrar pantallas
			self._register_screens()

			# Configurar navegación inicial
			self._setup_initial_navigation()

			logging.info("Fallback UI loaded successfully")
			return self.main_layout

		except Exception as e:
			logging.error(f"Error building fallback UI: {e}")
			return self._create_error_widget()

	def _register_screens(self):
		"""Registra todas las pantallas en el navigation manager."""
		try:
			# Pantalla principal
			self.navigation_manager.register_screen("home", HomeScreen)

			# Pantalla de logros para idle clicker
			from ui.screens.achievements_screen_idle import AchievementsScreenIdle

			self.navigation_manager.register_screen("achievements", AchievementsScreenIdle)

			# Pantalla de configuración
			self.navigation_manager.register_screen("settings", SettingsScreen)

			# Pantallas de gameplay
			self.navigation_manager.register_screen("combat", CombatScreen)

			# Pantalla de exploración de mazmorras
			self.navigation_manager.register_screen("exploration", ExplorationScreen)

			# Pantalla de equipamiento
			def create_equipment_screen(name):
				from core.game import get_game_state

				game_state = get_game_state()
				return EquipmentScreen(game_state.equipment_manager, name=name)

			self.navigation_manager.register_screen("equipment", create_equipment_screen)

			# Pantallas de progresión
			from core.game import get_game_state

			self.navigation_manager.register_screen(
				"upgrades", lambda name: UpgradesScreen(name=name)
			)

			# Pantalla de prestigio
			from ui.screens.prestige_screen_simple import PrestigeScreen

			self.navigation_manager.register_screen("prestige", PrestigeScreen)

			# Pantalla de tienda premium
			from ui.screens.premium_shop_screen import PremiumShopScreen

			self.navigation_manager.register_screen("shop", PremiumShopScreen)

			# Pantalla de carga
			self.navigation_manager.register_screen("loading", LoadingScreen)

			logging.info("All screens registered")

		except Exception as e:
			logging.error(f"Error registering screens: {e}")
			raise

	def _setup_initial_navigation(self):
		"""Configura la navegación inicial."""
		try:
			# Navegar a Combat como pantalla principal
			success = self.navigation_manager.navigate_to("combat")

			if not success:
				logging.warning("Failed to navigate to combat, creating combat screen manually")
				combat_screen = CombatScreen(name="combat")
				self.navigation_manager.add_widget(combat_screen)
				self.navigation_manager.current = "combat"

			logging.info("Initial navigation setup completed")

		except Exception as e:
			logging.error(f"Error setting up initial navigation: {e}")
			raise

	def _post_init_setup(self, dt):
		"""Configuración posterior a la inicialización."""
		try:
			# CRITICO: Activar debug mode por defecto si está configurado
			self._setup_debug_mode()

			logging.info("Post-initialization setup completed")

		except Exception as e:
			logging.error(f"Error in post-init setup: {e}")

	def _setup_debug_mode(self):
		"""Configura el modo debug basándose en la configuración guardada."""
		try:
			from ui.screens.settings_screen import SettingsScreen

			# Crear instancia temporal para acceder a la configuración por defecto
			temp_settings = SettingsScreen()
			current_settings = temp_settings.current_settings

			# Verificar si debug mode está activado en configuración
			debug_enabled = current_settings.get("debug", {}).get("mode_enabled", False)

			if debug_enabled:
				# Activar debug mode en TabNavigator (NO en NavigationManager)
				tab_navigator = self.main_layout.get_tab_navigator()
				if hasattr(tab_navigator, "enable_debug_mode"):
					tab_navigator.enable_debug_mode()
					logging.info(
						"DEBUG MODE: Activado automáticamente al inicio - Todos los menús desbloqueados para desarrollo"
					)
				else:
					logging.warning("TabNavigator no tiene enable_debug_mode")
			else:
				logging.info("DEBUG MODE: Desactivado por configuración")

		except Exception as e:
			logging.error(f"Error setting up debug mode: {e}")

	def _create_error_widget(self) -> Widget:
		"""Crea un widget de error para mostrar cuando falla la inicialización."""
		from kivy.uix.label import Label
		from kivy.uix.boxlayout import BoxLayout

		container = BoxLayout(orientation="vertical", padding=20, spacing=20)

		error_title = Label(
			text="Error de Inicialización", font_size="24sp", bold=True, size_hint_y=None, height=60
		)

		error_message = Label(
			text=f"No se pudo inicializar el juego.\n\nError: {self.initialization_error or 'Error desconocido'}",
			font_size="14sp",
			halign="center",
			valign="middle",
		)
		error_message.bind(texture_size=error_message.setter("text_size"))

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


if __name__ == "__main__":
	main()
