"""Menú lateral deslizable para SiKIdle.

Sistema de navegación expandido con múltiples categorías de contenido.
"""

import logging
from typing import Any, Optional

from kivy.animation import Animation  # type: ignore
from kivy.uix.boxlayout import BoxLayout  # type: ignore
from kivy.uix.button import Button  # type: ignore
from kivy.uix.label import Label  # type: ignore
from kivy.uix.widget import Widget  # type: ignore

from ui.screen_manager import SiKIdleScreenManager


class SideMenuCategory:
	"""Representa una categoría del menú lateral."""
	
	def __init__(self, name: str, icon: str, screen_name: str, description: str = ""):
		"""Inicializa una categoría del menú.
		
		Args:
			name: Nombre de la categoría
			icon: Emoji o símbolo para la categoría
			screen_name: Nombre de la pantalla a navegar
			description: Descripción opcional
		"""
		self.name = name
		self.icon = icon
		self.screen_name = screen_name
		self.description = description


class SideMenu(Widget):
	"""Menú lateral deslizable con categorías expandidas."""
	
	def __init__(self, **kwargs: Any):
		"""Inicializa el menú lateral."""
		super().__init__(**kwargs)
		
		self.manager_ref: Optional[SiKIdleScreenManager] = None
		self.is_open = False
		self.menu_width = 280  # Ancho del menú en píxeles
		
		# Definir categorías del menú
		self.categories = [
			SideMenuCategory("Edificios", "🏭", "buildings", "Generadores automáticos"),
			SideMenuCategory("Mejoras", "⬆️", "upgrades", "Mejoras tradicionales"),
			SideMenuCategory("Talentos", "🌟", "talents", "Árbol de especialización"),
			SideMenuCategory("Inventario", "🎒", "inventory", "Loot y artefactos"),
			SideMenuCategory("Logros", "🏆", "achievements", "Progreso y desafíos"),
			SideMenuCategory("Aventura", "⚔️", "adventure", "Combate y exploración"),
			SideMenuCategory("Prestigio", "💎", "prestige", "Renacimiento y bonificaciones"),
			SideMenuCategory("Estadísticas", "📊", "stats", "Datos de progreso"),
			SideMenuCategory("Configuración", "⚙️", "settings", "Opciones del juego"),
		]
		
		self.build_ui()
	
	def set_manager_reference(self, manager: SiKIdleScreenManager):
		"""Establece la referencia al gestor de pantallas.
		
		Args:
			manager: Gestor de pantallas del juego
		"""
		self.manager_ref = manager
	
	def build_ui(self):
		"""Construye la interfaz del menú lateral."""
		# Overlay semitransparente para cerrar el menú
		self.overlay = Widget(
			size_hint=(1, 1),
			opacity=0
		)
		self.overlay.bind(on_touch_down=self.on_overlay_touch)
		self.add_widget(self.overlay)
		
		# Panel principal del menú
		self.menu_panel = BoxLayout(
			orientation='vertical',
			size_hint=(None, 1),
			width=self.menu_width,
			pos=(-self.menu_width, 0),  # Inicialmente oculto
			padding=[15, 20, 15, 20],
			spacing=10
		)
		
		# Fondo del panel
		with self.menu_panel.canvas.before:
			from kivy.graphics import Color, Rectangle  # type: ignore
			Color(0.1, 0.1, 0.15, 0.95)  # Azul oscuro semitransparente
			self.menu_bg = Rectangle(size=self.menu_panel.size, pos=self.menu_panel.pos)
		
		self.menu_panel.bind(size=self.update_bg, pos=self.update_bg)
		
		# Título del menú
		title_label = Label(
			text='🎮 SiKIdle',
			font_size='24sp',
			size_hint=(1, None),
			height='50dp',
			bold=True,
			color=[1, 1, 1, 1]
		)
		self.menu_panel.add_widget(title_label)
		
		# Línea separadora
		separator = Widget(
			size_hint=(1, None),
			height='2dp'
		)
		with separator.canvas:
			Color(0.3, 0.3, 0.4, 1)
			self.separator_rect = Rectangle(size=separator.size, pos=separator.pos)
		separator.bind(size=self.update_separator, pos=self.update_separator)
		self.menu_panel.add_widget(separator)
		
		# Botones de categorías
		self.create_category_buttons()
		
		# Botón de cerrar en la parte inferior
		close_button = Button(
			text='❌ Cerrar Menú',
			font_size='16sp',
			size_hint=(1, None),
			height='50dp',
			background_color=[0.6, 0.3, 0.3, 1]
		)
		close_button.bind(on_press=self.close_menu)
		self.menu_panel.add_widget(close_button)
		
		self.add_widget(self.menu_panel)
		
		logging.info("Menú lateral construido")
	
	def create_category_buttons(self):
		"""Crea los botones para cada categoría del menú."""
		for category in self.categories:
			# Contenedor del botón con información
			button_container = BoxLayout(
				orientation='horizontal',
				size_hint=(1, None),
				height='60dp',
				spacing=10
			)
			
			# Botón principal de la categoría
			category_button = Button(
				text=f'{category.icon} {category.name}',
				font_size='16sp',
				size_hint=(0.8, 1),
				background_color=[0.2, 0.3, 0.5, 1],
				halign='left',
				text_size=(None, None)
			)
			
			# Configurar alineación del texto
			category_button.bind(size=lambda btn, size: setattr(btn, 'text_size', (size[0] - 20, None)))
			category_button.bind(on_press=lambda x, cat=category: self.on_category_selected(cat))
			
			# Indicador de estado (TODO: implementar lógica de estado)
			status_indicator = Label(
				text='●',
				font_size='20sp',
				size_hint=(0.2, 1),
				color=[0.5, 0.8, 0.3, 1]  # Verde por defecto
			)
			
			button_container.add_widget(category_button)
			button_container.add_widget(status_indicator)
			
			self.menu_panel.add_widget(button_container)
			
			# Descripción pequeña (opcional)
			if category.description:
				desc_label = Label(
					text=category.description,
					font_size='12sp',
					size_hint=(1, None),
					height='25dp',
					color=[0.7, 0.7, 0.7, 1],
					text_size=(self.menu_width - 30, None),
					halign='left'
				)
				self.menu_panel.add_widget(desc_label)
	
	def update_bg(self, instance: Widget, value: Any):
		"""Actualiza el fondo del panel del menú.
		
		Args:
			instance: Widget que cambió
			value: Nuevo valor
		"""
		self.menu_bg.size = instance.size
		self.menu_bg.pos = instance.pos
	
	def update_separator(self, instance: Widget, value: Any):
		"""Actualiza el separador del menú.
		
		Args:
			instance: Widget que cambió
			value: Nuevo valor
		"""
		if hasattr(self, 'separator_rect'):
			self.separator_rect.size = instance.size
			self.separator_rect.pos = instance.pos
	
	def on_overlay_touch(self, instance: Widget, touch: Any) -> bool:
		"""Maneja el toque en el overlay para cerrar el menú.
		
		Args:
			instance: Widget tocado
			touch: Evento de toque
			
		Returns:
			True si se manejó el evento
		"""
		if self.is_open and touch.pos[0] > self.menu_width:
			self.close_menu()
			return True
		return False
	
	def open_menu(self):
		"""Abre el menú lateral con animación."""
		if self.is_open:
			return
		
		self.is_open = True
		
		# Animar overlay
		overlay_anim = Animation(opacity=0.5, duration=0.3)
		overlay_anim.start(self.overlay)
		
		# Animar panel
		panel_anim = Animation(pos=(0, self.menu_panel.pos[1]), duration=0.3, t='out_cubic')
		panel_anim.start(self.menu_panel)
		
		logging.info("Menú lateral abierto")
	
	def close_menu(self, instance: Optional[Button] = None):
		"""Cierra el menú lateral con animación.
		
		Args:
			instance: Botón que activó el cierre (opcional)
		"""
		if not self.is_open:
			return
		
		self.is_open = False
		
		# Animar overlay
		overlay_anim = Animation(opacity=0, duration=0.3)
		overlay_anim.start(self.overlay)
		
		# Animar panel
		panel_anim = Animation(pos=(-self.menu_width, self.menu_panel.pos[1]), duration=0.3, t='in_cubic')
		panel_anim.start(self.menu_panel)
		
		logging.info("Menú lateral cerrado")
	
	def toggle_menu(self):
		"""Alterna el estado del menú (abierto/cerrado)."""
		if self.is_open:
			self.close_menu()
		else:
			self.open_menu()
	
	def on_category_selected(self, category: SideMenuCategory):
		"""Maneja la selección de una categoría del menú.
		
		Args:
			category: Categoría seleccionada
		"""
		logging.info(f"Categoría seleccionada: {category.name} -> {category.screen_name}")
		
		# Cerrar el menú primero
		self.close_menu()
		
		# Navegar a la pantalla correspondiente
		if self.manager_ref:
			if hasattr(self.manager_ref, 'navigate_to_screen'):
				self.manager_ref.navigate_to_screen(category.screen_name)
			else:
				# Fallback para navegación básica
				if hasattr(self.manager_ref, 'current'):
					self.manager_ref.current = category.screen_name
		else:
			logging.warning("No hay referencia al gestor de pantallas disponible")
