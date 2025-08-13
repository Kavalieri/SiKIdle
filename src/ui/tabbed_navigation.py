"""Sistema de pestañas avanzado para SiKIdle.

Proporciona una barra de navegación horizontal con pestañas
para un acceso más eficiente a las diferentes pantallas del juego.
"""

import logging

from kivy.uix.boxlayout import BoxLayout  # type: ignore
from kivy.uix.button import Button  # type: ignore
from kivy.uix.widget import Widget  # type: ignore


class TabButton(Button):
	"""Botón individual de pestaña con estado visual avanzado."""

	def __init__(self, tab_id: str, text: str, icon: str, callback=None, **kwargs):
		"""Inicializa un botón de pestaña.

		Args:
			tab_id: Identificador único de la pestaña
			text: Texto descriptivo de la pestaña
			icon: Icono emoji de la pestaña
			callback: Función a llamar cuando se toque la pestaña
		"""
		super().__init__(**kwargs)

		self.tab_id = tab_id
		self.tab_text = text
		self.tab_icon = icon
		self.callback = callback
		self.is_active = False
		self.has_notification = False

		# Configuración visual base
		self.text = f"{icon}\n{text}"
		self.font_size = "12sp"
		self.size_hint = (1, 1)
		self.background_color = [0.4, 0.4, 0.4, 0.8]  # Inactivo por defecto

		# Bind del evento de toque
		self.bind(on_press=self._on_press)

	def _on_press(self, instance):
		"""Maneja el evento de toque en la pestaña."""
		if self.callback:
			self.callback(self.tab_id)

	def set_active(self, active: bool):
		"""Establece el estado activo/inactivo de la pestaña.

		Args:
			active: True si la pestaña está activa
		"""
		self.is_active = active
		self._update_visual_state()

	def set_notification(self, has_notification: bool):
		"""Establece si la pestaña tiene notificaciones.

		Args:
			has_notification: True si hay notificaciones pendientes
		"""
		self.has_notification = has_notification
		self._update_visual_state()

	def _update_visual_state(self):
		"""Actualiza el estado visual según el estado de la pestaña."""
		if self.is_active:
			# Pestaña activa - color primario
			self.background_color = [0.2, 0.7, 0.9, 1.0]
			self.color = [1, 1, 1, 1]
		elif self.has_notification:
			# Tiene notificación - color de alerta
			self.background_color = [1, 0.5, 0, 0.9]
			self.color = [1, 1, 1, 1]
		else:
			# Inactiva normal - color neutro
			self.background_color = [0.4, 0.4, 0.4, 0.8]
			self.color = [0.8, 0.8, 0.8, 1]

		# Actualizar texto con indicador de notificación
		notification_indicator = " 🔴" if self.has_notification and not self.is_active else ""
		self.text = f"{self.tab_icon}\n{self.tab_text}{notification_indicator}"


class TabBar(BoxLayout):
	"""Barra de pestañas horizontal con gestión de estado avanzada."""

	def __init__(self, **kwargs):
		"""Inicializa la barra de pestañas."""
		super().__init__(**kwargs)

		self.orientation = "horizontal"
		self.size_hint = (1, None)
		self.height = "60dp"
		self.spacing = 2
		self.padding = [5, 5, 5, 5]

		# Estado interno
		self.tabs = {}
		self.active_tab = None
		self.on_tab_change = None

		# Configuración visual de la barra
		self.canvas.before.clear()
		with self.canvas.before:
			from kivy.graphics import Color, Rectangle  # type: ignore

			Color(0.2, 0.2, 0.2, 0.95)  # Fondo semi-transparente
			self.bg_rect = Rectangle(size=self.size, pos=self.pos)

		self.bind(size=self._update_bg, pos=self._update_bg)

	def _update_bg(self, *args):
		"""Actualiza el fondo de la barra."""
		if hasattr(self, "bg_rect"):
			self.bg_rect.size = self.size
			self.bg_rect.pos = self.pos

	def add_tab(self, tab_id: str, text: str, icon: str, callback=None):
		"""Añade una nueva pestaña a la barra.

		Args:
			tab_id: Identificador único de la pestaña
			text: Texto descriptivo
			icon: Icono emoji
			callback: Función de callback opcional

		Returns:
			El botón de pestaña creado
		"""
		if tab_id in self.tabs:
			logging.warning(f"Pestaña '{tab_id}' ya existe")
			return self.tabs[tab_id]

		tab_button = TabButton(tab_id=tab_id, text=text, icon=icon, callback=self._on_tab_selected)

		self.tabs[tab_id] = tab_button
		self.add_widget(tab_button)

		# Si es la primera pestaña, activarla
		if len(self.tabs) == 1:
			self.set_active_tab(tab_id)

		logging.debug(f"Pestaña '{tab_id}' añadida a la barra")
		return tab_button

	def _on_tab_selected(self, tab_id: str):
		"""Maneja la selección de una pestaña.

		Args:
			tab_id: ID de la pestaña seleccionada
		"""
		if tab_id == self.active_tab:
			return  # Ya está activa

		# Cambiar pestaña activa
		old_tab = self.active_tab
		self.set_active_tab(tab_id)

		# Llamar callback de cambio
		if self.on_tab_change:
			self.on_tab_change(tab_id)

		logging.info(f"Cambio de pestaña: {old_tab} → {tab_id}")

	def set_active_tab(self, tab_id: str):
		"""Establece la pestaña activa.

		Args:
			tab_id: ID de la pestaña a activar
		"""
		if tab_id not in self.tabs:
			logging.error(f"Pestaña '{tab_id}' no encontrada")
			return

		# Desactivar pestaña anterior
		if self.active_tab and self.active_tab in self.tabs:
			self.tabs[self.active_tab].set_active(False)

		# Activar nueva pestaña
		self.active_tab = tab_id
		self.tabs[tab_id].set_active(True)

		# Limpiar notificación si la tenía
		self.tabs[tab_id].set_notification(False)

	def set_tab_notification(self, tab_id: str, has_notification: bool):
		"""Establece el estado de notificación de una pestaña.

		Args:
			tab_id: ID de la pestaña
			has_notification: True si tiene notificaciones
		"""
		if tab_id in self.tabs:
			self.tabs[tab_id].set_notification(has_notification)
		else:
			logging.warning(f"Pestaña '{tab_id}' no encontrada para notificación")

	def get_active_tab(self):
		"""Obtiene el ID de la pestaña activa.

		Returns:
			ID de la pestaña activa o None
		"""
		return self.active_tab


class TabbedNavigationSystem:
	"""Sistema completo de navegación por pestañas."""

	def __init__(self):
		"""Inicializa el sistema de navegación."""
		self.tab_bar = None
		self.navigation_callbacks = {}

	def setup(self, tab_bar):
		"""Configura el sistema con los componentes necesarios.

		Args:
			tab_bar: Barra de pestañas
		"""
		self.tab_bar = tab_bar

		# Conectar callback de cambio de pestaña
		self.tab_bar.on_tab_change = self._handle_tab_change

		logging.info("Sistema de navegación por pestañas configurado")

	def register_tab(self, tab_id: str, text: str, icon: str, navigation_callback):
		"""Registra una nueva pestaña en el sistema.

		Args:
			tab_id: Identificador único
			text: Texto descriptivo
			icon: Icono emoji
			navigation_callback: Función a llamar al navegar a esta pestaña
		"""
		if not self.tab_bar:
			logging.error("Sistema no configurado - llamar setup() primero")
			return

		# Registrar callback
		self.navigation_callbacks[tab_id] = navigation_callback

		# Añadir pestaña a la barra
		self.tab_bar.add_tab(tab_id, text, icon)

		logging.info(f"Pestaña '{tab_id}' registrada en el sistema")

	def _handle_tab_change(self, tab_id: str):
		"""Maneja el cambio de pestaña ejecutando el callback apropiado.

		Args:
			tab_id: ID de la pestaña seleccionada
		"""
		if tab_id in self.navigation_callbacks:
			try:
				self.navigation_callbacks[tab_id]()
			except Exception as e:
				logging.error(f"Error ejecutando callback para pestaña '{tab_id}': {e}")
		else:
			logging.warning(f"No hay callback registrado para pestaña '{tab_id}'")

	def navigate_to_tab(self, tab_id: str):
		"""Navega programáticamente a una pestaña específica.

		Args:
			tab_id: ID de la pestaña de destino
		"""
		if self.tab_bar:
			self.tab_bar.set_active_tab(tab_id)
		else:
			logging.error("Sistema no configurado")

	def set_notification(self, tab_id: str, has_notification: bool = True):
		"""Establece una notificación en una pestaña.

		Args:
			tab_id: ID de la pestaña
			has_notification: True para mostrar notificación
		"""
		if self.tab_bar:
			self.tab_bar.set_tab_notification(tab_id, has_notification)
		else:
			logging.error("Sistema no configurado")
