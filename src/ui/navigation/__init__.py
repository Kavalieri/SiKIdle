"""
NavigationManager - Sistema de navegación central para SiKIdle.

Gestor principal de navegación con stack navigation, transiciones fluidas
y gestión de estado entre pantallas.
"""

from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition, FadeTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.properties import StringProperty, ObjectProperty, BooleanProperty

from typing import Dict, List, Optional, Callable, Any
from enum import Enum
import logging


class NavigationTransition(Enum):
	"""Tipos de transiciones disponibles."""
	SLIDE_LEFT = "slide_left"
	SLIDE_RIGHT = "slide_right"
	SLIDE_UP = "slide_up"
	SLIDE_DOWN = "slide_down"
	FADE = "fade"
	NONE = "none"


class ScreenType(Enum):
	"""Tipos de pantallas del juego."""
	HOME = "home"
	COMBAT = "combat"
	TALENTS = "talents"
	ACHIEVEMENTS = "achievements"
	DUNGEONS = "dungeons"
	SETTINGS = "settings"
	LOADING = "loading"


class NavigationButton(Button):
	"""Botón de navegación personalizado para el TabNavigator."""
	
	screen_type = ObjectProperty(None)
	is_active = BooleanProperty(False)
	
	def __init__(self, screen_type: ScreenType, **kwargs):
		super().__init__(**kwargs)
		self.screen_type = screen_type
		self.text = self._get_button_text()
		self.size_hint_x = None
		self.width = 80
		self.height = 60
		
		self._setup_styling()
		self.bind(is_active=self._on_active_changed)
	
	def _get_button_text(self) -> str:
		"""Obtiene el texto e icono del botón."""
		button_configs = {
			ScreenType.HOME: "🏠\nHome",
			ScreenType.COMBAT: "⚔️\nCombat",
			ScreenType.TALENTS: "🌟\nTalents",
			ScreenType.ACHIEVEMENTS: "🏆\nLogros",
			ScreenType.SETTINGS: "⚙️\nConfig"
		}
		return button_configs.get(self.screen_type, "📱\nApp")
	
	def _setup_styling(self):
		"""Configura el estilo del botón."""
		self.font_size = '10sp'
		self.halign = 'center'
		self.valign = 'center'
		self._update_colors()
	
	def _on_active_changed(self, instance, is_active):
		"""Actualiza el estilo cuando cambia el estado activo."""
		self._update_colors()
		
		# Animación de activación
		if is_active:
			anim = Animation(
				size=(self.width * 1.1, self.height * 1.1),
				duration=0.1,
				t='out_expo'
			) + Animation(
				size=(self.width, self.height),
				duration=0.1,
				t='in_expo'
			)
			anim.start(self)
	
	def _update_colors(self):
		"""Actualiza los colores según el estado."""
		if self.is_active:
			self.background_color = (0.20, 0.60, 0.86, 1)  # Azul activo
		else:
			self.background_color = (0.47, 0.55, 0.55, 1)  # Gris inactivo


class TabNavigator(BoxLayout):
	"""Navegador de pestañas inferior para navegación principal."""
	
	def __init__(self, navigation_manager, **kwargs):
		super().__init__(**kwargs)
		self.navigation_manager = navigation_manager
		self.orientation = 'horizontal'
		self.size_hint_y = None
		self.height = 70
		self.spacing = 2
		self.padding = [4, 8, 4, 8]
		
		# Diccionario de botones
		self.nav_buttons: Dict[ScreenType, NavigationButton] = {}
		
		self._build_navigation_bar()
		self._setup_styling()
	
	def _build_navigation_bar(self):
		"""Construye la barra de navegación."""
		# Pantallas principales del tab navigator
		main_screens = [
			ScreenType.HOME,
			ScreenType.COMBAT,
			ScreenType.TALENTS,
			ScreenType.ACHIEVEMENTS,
			ScreenType.SETTINGS
		]
		
		for screen_type in main_screens:
			btn = NavigationButton(screen_type)
			btn.bind(on_press=lambda x, st=screen_type: self._on_tab_pressed(st))
			
			self.nav_buttons[screen_type] = btn
			self.add_widget(btn)
		
		# Activar primera pestaña por defecto
		self._set_active_tab(ScreenType.HOME)
	
	def _setup_styling(self):
		"""Configura el estilo de la barra de navegación."""
		from kivy.graphics import Color, Rectangle
		
		with self.canvas.before:
			Color(0.17, 0.24, 0.31, 1)  # Color de fondo dark blue
			self.bg_rect = Rectangle(pos=self.pos, size=self.size)
		
		self.bind(pos=self._update_bg, size=self._update_bg)
	
	def _update_bg(self, *args):
		"""Actualiza el fondo cuando cambia el tamaño."""
		if hasattr(self, 'bg_rect'):
			self.bg_rect.pos = self.pos
			self.bg_rect.size = self.size
	
	def _on_tab_pressed(self, screen_type: ScreenType):
		"""Maneja el press de una pestaña."""
		self._set_active_tab(screen_type)
		self.navigation_manager.navigate_to(screen_type.value)
	
	def _set_active_tab(self, active_screen: ScreenType):
		"""Activa una pestaña específica."""
		for screen_type, button in self.nav_buttons.items():
			button.is_active = (screen_type == active_screen)
	
	def update_active_tab(self, screen_name: str):
		"""Actualiza la pestaña activa desde el navigation manager."""
		try:
			screen_type = ScreenType(screen_name)
			self._set_active_tab(screen_type)
		except ValueError:
			# Screen no está en el tab navigator (ej: loading, dungeons)
			pass


class HeaderBar(BoxLayout):
	"""Barra de header superior con título y acciones contextuales."""
	
	title_text = StringProperty("SiKIdle")
	
	def __init__(self, navigation_manager, **kwargs):
		super().__init__(**kwargs)
		self.navigation_manager = navigation_manager
		self.orientation = 'horizontal'
		self.size_hint_y = None
		self.height = 56
		self.padding = [16, 8, 16, 8]
		self.spacing = 8
		
		self._build_header()
		self._setup_styling()
	
	def _build_header(self):
		"""Construye el header."""
		# Botón de menú (futuro)
		self.menu_button = Button(
			text="☰",
			size_hint_x=None,
			width=40,
			font_size='20sp'
		)
		
		# Título principal
		self.title_label = Label(
			text=self.title_text,
			font_size='20sp',
			bold=True,
			halign='left'
		)
		self.title_label.bind(texture_size=self.title_label.setter('text_size'))
		
		# Indicadores de estado (recursos, salud, etc.)
		self.status_layout = BoxLayout(
			orientation='horizontal',
			size_hint_x=None,
			width=120,
			spacing=4
		)
		
		# Placeholder para indicadores
		self.coins_label = Label(
			text="💰 1,234",
			font_size='12sp',
			size_hint_x=None,
			width=60
		)
		
		self.level_label = Label(
			text="⭐ Lv.5",
			font_size='12sp',
			size_hint_x=None,
			width=60
		)
		
		self.status_layout.add_widget(self.coins_label)
		self.status_layout.add_widget(self.level_label)
		
		# Ensamblar header
		self.add_widget(self.menu_button)
		self.add_widget(self.title_label)
		self.add_widget(self.status_layout)
	
	def _setup_styling(self):
		"""Configura el estilo del header."""
		from kivy.graphics import Color, Rectangle
		
		with self.canvas.before:
			Color(0.20, 0.60, 0.86, 1)  # Azul principal
			self.bg_rect = Rectangle(pos=self.pos, size=self.size)
		
		self.bind(pos=self._update_bg, size=self._update_bg)
	
	def _update_bg(self, *args):
		"""Actualiza el fondo del header."""
		if hasattr(self, 'bg_rect'):
			self.bg_rect.pos = self.pos
			self.bg_rect.size = self.size
	
	def update_title(self, title: str):
		"""Actualiza el título del header."""
		self.title_text = title
		self.title_label.text = title
	
	def update_status(self, coins: int = None, level: int = None):
		"""Actualiza los indicadores de estado."""
		if coins is not None:
			self.coins_label.text = f"💰 {coins:,}"
		
		if level is not None:
			self.level_label.text = f"⭐ Lv.{level}"


class NavigationManager(ScreenManager):
	"""Gestor principal de navegación del juego."""
	
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		
		# Configurar transiciones
		self.transition = SlideTransition(direction='left', duration=0.3)
		
		# Historia de navegación para back navigation
		self.navigation_history: List[str] = []
		self.max_history = 10
		
		# Callbacks para cambios de pantalla
		self.screen_change_callbacks: List[Callable[[str], None]] = []
		
		# Registro de pantallas
		self.registered_screens: Dict[str, type] = {}
		
		# Estado actual
		self.current_screen_name = ""
		
		logging.info("NavigationManager initialized")
	
	def register_screen(self, screen_name: str, screen_class: type):
		"""Registra una clase de pantalla para lazy loading."""
		self.registered_screens[screen_name] = screen_class
		logging.debug(f"Registered screen: {screen_name}")
	
	def navigate_to(self, screen_name: str, transition: NavigationTransition = None, **kwargs):
		"""Navega a una pantalla específica."""
		try:
			# Configurar transición si se especifica
			if transition:
				self._set_transition(transition)
			
			# Verificar si la pantalla existe
			if not self.has_screen(screen_name) and screen_name in self.registered_screens:
				self._create_screen(screen_name)
			
			if not self.has_screen(screen_name):
				logging.error(f"Screen '{screen_name}' not found")
				return False
			
			# Añadir a historia si no es la misma pantalla
			if self.current_screen_name != screen_name:
				self._add_to_history(self.current_screen_name)
			
			# Navegar
			self.current = screen_name
			self.current_screen_name = screen_name
			
			# Notificar callbacks
			self._notify_screen_change(screen_name)
			
			logging.info(f"Navigated to: {screen_name}")
			return True
			
		except Exception as e:
			logging.error(f"Navigation error: {e}")
			return False
	
	def navigate_back(self) -> bool:
		"""Navega a la pantalla anterior en la historia."""
		if not self.navigation_history:
			return False
		
		previous_screen = self.navigation_history.pop()
		
		# Configurar transición de vuelta
		self._set_transition(NavigationTransition.SLIDE_RIGHT)
		
		# Navegar sin añadir a historia
		if self.has_screen(previous_screen):
			self.current = previous_screen
			self.current_screen_name = previous_screen
			self._notify_screen_change(previous_screen)
			return True
		
		return False
	
	def _create_screen(self, screen_name: str):
		"""Crea una pantalla usando lazy loading."""
		if screen_name not in self.registered_screens:
			return
		
		try:
			screen_class = self.registered_screens[screen_name]
			screen_instance = screen_class(name=screen_name)
			self.add_widget(screen_instance)
			logging.debug(f"Created screen: {screen_name}")
		except Exception as e:
			logging.error(f"Error creating screen {screen_name}: {e}")
	
	def _set_transition(self, transition: NavigationTransition):
		"""Configura el tipo de transición."""
		if transition == NavigationTransition.SLIDE_LEFT:
			self.transition = SlideTransition(direction='left', duration=0.3)
		elif transition == NavigationTransition.SLIDE_RIGHT:
			self.transition = SlideTransition(direction='right', duration=0.3)
		elif transition == NavigationTransition.SLIDE_UP:
			self.transition = SlideTransition(direction='up', duration=0.3)
		elif transition == NavigationTransition.SLIDE_DOWN:
			self.transition = SlideTransition(direction='down', duration=0.3)
		elif transition == NavigationTransition.FADE:
			self.transition = FadeTransition(duration=0.3)
		elif transition == NavigationTransition.NONE:
			self.transition.duration = 0
	
	def _add_to_history(self, screen_name: str):
		"""Añade una pantalla a la historia de navegación."""
		if screen_name and screen_name != "":
			self.navigation_history.append(screen_name)
			
			# Limitar tamaño de historia
			if len(self.navigation_history) > self.max_history:
				self.navigation_history.pop(0)
	
	def _notify_screen_change(self, screen_name: str):
		"""Notifica a los callbacks del cambio de pantalla."""
		for callback in self.screen_change_callbacks:
			try:
				callback(screen_name)
			except Exception as e:
				logging.error(f"Error in screen change callback: {e}")
	
	def add_screen_change_callback(self, callback: Callable[[str], None]):
		"""Añade un callback para cambios de pantalla."""
		self.screen_change_callbacks.append(callback)
	
	def get_current_screen_name(self) -> str:
		"""Obtiene el nombre de la pantalla actual."""
		return self.current_screen_name
	
	def clear_history(self):
		"""Limpia la historia de navegación."""
		self.navigation_history.clear()
	
	def show_loading(self, message: str = "Cargando..."):
		"""Muestra pantalla de loading."""
		self.navigate_to("loading", NavigationTransition.FADE)
	
	def hide_loading(self, return_to: str = None):
		"""Oculta pantalla de loading."""
		if return_to:
			self.navigate_to(return_to, NavigationTransition.FADE)
		else:
			self.navigate_back()


class MainLayout(BoxLayout):
	"""Layout principal que contiene header, content y navigation."""
	
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.orientation = 'vertical'
		
		# Crear navigation manager
		self.navigation_manager = NavigationManager()
		
		# Crear header
		self.header = HeaderBar(self.navigation_manager)
		
		# Crear tab navigator
		self.tab_navigator = TabNavigator(self.navigation_manager)
		
		# Configurar callbacks
		self.navigation_manager.add_screen_change_callback(self._on_screen_changed)
		
		# Ensamblar layout
		self.add_widget(self.header)
		self.add_widget(self.navigation_manager)
		self.add_widget(self.tab_navigator)
		
		logging.info("MainLayout initialized")
	
	def _on_screen_changed(self, screen_name: str):
		"""Callback ejecutado cuando cambia la pantalla."""
		# Actualizar tab navigator
		self.tab_navigator.update_active_tab(screen_name)
		
		# Actualizar título del header
		screen_titles = {
			"home": "🏠 SiKIdle - Dashboard",
			"combat": "⚔️ Sistema de Combate", 
			"talents": "🌟 Árbol de Talentos",
			"achievements": "🏆 Sistema de Logros",
			"dungeons": "🗺️ Mazmorras",
			"settings": "⚙️ Configuración"
		}
		
		title = screen_titles.get(screen_name, "SiKIdle")
		self.header.update_title(title)
	
	def register_screen(self, screen_name: str, screen_class: type):
		"""Registra una pantalla en el navigation manager."""
		self.navigation_manager.register_screen(screen_name, screen_class)
	
	def navigate_to(self, screen_name: str, **kwargs):
		"""Shortcut para navegar a una pantalla."""
		return self.navigation_manager.navigate_to(screen_name, **kwargs)
	
	def get_navigation_manager(self) -> NavigationManager:
		"""Obtiene el navigation manager."""
		return self.navigation_manager
