"""Pantalla de configuración para SiKIdle.

Permite al usuario ajustar configuraciones del juego como
idioma, sonido, vibración y otras opciones.
"""

from kivy.uix.boxlayout import BoxLayout  # type: ignore
from kivy.uix.button import Button  # type: ignore
from kivy.uix.label import Label  # type: ignore
from kivy.uix.switch import Switch  # type: ignore
import logging
from typing import Any

from ui.screen_manager import SiKIdleScreen
from utils.save import get_save_manager


class SettingsScreen(SiKIdleScreen):
	"""Pantalla de configuración del juego."""
	
	def __init__(self, **kwargs: Any):
		"""Inicializa la pantalla de configuración."""
		super().__init__(**kwargs)
		
		self.save_manager = get_save_manager()
		
		# Referencias a controles
		self.sound_switch = None
		self.vibration_switch = None
		
		self.build_ui()
		
	def build_ui(self):
		"""Construye la interfaz de la pantalla de configuración."""
		# Layout principal
		main_layout = BoxLayout(
			orientation='vertical',
			padding=[30, 40, 30, 30],
			spacing=25
		)
		
		# Header con título y botón volver
		header = BoxLayout(
			orientation='horizontal',
			size_hint=(1, 0.1),
			spacing=10
		)
		
		back_button = Button(
			text='← Volver',
			font_size='16sp',
			size_hint=(0.3, 1),
			background_color=[0.6, 0.6, 0.6, 1]
		)
		back_button.bind(on_press=self.on_back_button)
		header.add_widget(back_button)
		
		title_label = Label(
			text='⚙️ Configuración',
			font_size='28sp',
			size_hint=(0.7, 1),
			bold=True,
			color=[0.8, 0.8, 1, 1]
		)
		header.add_widget(title_label)
		
		main_layout.add_widget(header)
		
		# Área de configuraciones
		settings_area = BoxLayout(
			orientation='vertical',
			size_hint=(1, 0.7),
			spacing=20
		)
		
		# Configuración de sonido
		sound_setting = self.create_setting_row(
			'🔊 Sonido',
			'Activar/desactivar sonidos del juego',
			'sound_enabled'
		)
		settings_area.add_widget(sound_setting)
		
		# Configuración de vibración
		vibration_setting = self.create_setting_row(
			'📳 Vibración',
			'Activar vibración en dispositivos móviles',
			'vibration_enabled'
		)
		settings_area.add_widget(vibration_setting)
		
		# Configuración de idioma (placeholder)
		language_setting = self.create_language_setting()
		settings_area.add_widget(language_setting)
		
		main_layout.add_widget(settings_area)
		
		# Área de botones de acción
		action_area = BoxLayout(
			orientation='vertical',
			size_hint=(1, 0.2),
			spacing=15
		)
		
		# Botón de reiniciar progreso (peligroso)
		reset_button = Button(
			text='🔄 REINICIAR PROGRESO',
			font_size='18sp',
			size_hint=(1, 0.5),
			background_color=[0.8, 0.2, 0.2, 1]  # Rojo
		)
		reset_button.bind(on_press=self.on_reset_button)
		action_area.add_widget(reset_button)
		
		# Información de versión
		version_info = Label(
			text='SiKIdle v1.0.0 - Alpha\nDesarrollado para Android',
			font_size='14sp',
			size_hint=(1, 0.5),
			color=[0.6, 0.6, 0.6, 1],
			halign='center'
		)
		action_area.add_widget(version_info)
		
		main_layout.add_widget(action_area)
		
		self.add_widget(main_layout)
		
		logging.info("Pantalla de configuración construida")
	
	def create_setting_row(self, title: str, description: str, setting_key: str) -> BoxLayout:
		"""Crea una fila de configuración con switch.
		
		Args:
			title: Título de la configuración
			description: Descripción de la configuración
			setting_key: Clave en el sistema de guardado
			
		Returns:
			BoxLayout con la fila de configuración
		"""
		row = BoxLayout(
			orientation='vertical',
			size_hint=(1, None),
			height='80dp',
			spacing=5
		)
		
		# Fila principal con título y switch
		main_row = BoxLayout(
			orientation='horizontal',
			size_hint=(1, 0.6)
		)
		
		title_label = Label(
			text=title,
			font_size='20sp',
			size_hint=(0.7, 1),
			halign='left',
			valign='center',
			color=[0.9, 0.9, 0.9, 1]
		)
		title_label.text_size = (None, None)
		main_row.add_widget(title_label)
		
		# Switch
		switch = Switch(
			size_hint=(0.3, 1),
			active=self.save_manager.get_setting(setting_key, 'true') == 'true'
		)
		switch.bind(active=lambda instance, value: self.on_setting_changed(setting_key, value))
		main_row.add_widget(switch)
		
		# Guardar referencia al switch
		if setting_key == 'sound_enabled':
			self.sound_switch = switch
		elif setting_key == 'vibration_enabled':
			self.vibration_switch = switch
		
		row.add_widget(main_row)
		
		# Descripción
		desc_label = Label(
			text=description,
			font_size='14sp',
			size_hint=(1, 0.4),
			color=[0.6, 0.6, 0.6, 1],
			halign='left',
			valign='top'
		)
		desc_label.text_size = (400, None)
		row.add_widget(desc_label)
		
		return row
	
	def create_language_setting(self) -> BoxLayout:
		"""Crea la configuración de idioma (placeholder).
		
		Returns:
			BoxLayout con la configuración de idioma
		"""
		row = BoxLayout(
			orientation='vertical',
			size_hint=(1, None),
			height='80dp',
			spacing=5
		)
		
		# Fila principal
		main_row = BoxLayout(
			orientation='horizontal',
			size_hint=(1, 0.6)
		)
		
		title_label = Label(
			text='🌐 Idioma',
			font_size='20sp',
			size_hint=(0.7, 1),
			halign='left',
			valign='center',
			color=[0.9, 0.9, 0.9, 1]
		)
		main_row.add_widget(title_label)
		
		language_button = Button(
			text='Español',
			font_size='16sp',
			size_hint=(0.3, 1),
			background_color=[0.4, 0.4, 0.6, 1]
		)
		language_button.bind(on_press=self.on_language_button)
		main_row.add_widget(language_button)
		
		row.add_widget(main_row)
		
		# Descripción
		desc_label = Label(
			text='Seleccionar idioma del juego (próximamente)',
			font_size='14sp',
			size_hint=(1, 0.4),
			color=[0.6, 0.6, 0.6, 1],
			halign='left',
			valign='top'
		)
		desc_label.text_size = (400, None)
		row.add_widget(desc_label)
		
		return row
	
	def on_setting_changed(self, setting_key: str, value: bool):
		"""Maneja cambios en las configuraciones.
		
		Args:
			setting_key: Clave de la configuración
			value: Nuevo valor
		"""
		self.save_manager.save_setting(setting_key, 'true' if value else 'false')
		logging.info(f"Configuración cambiada: {setting_key} = {value}")
	
	def on_language_button(self, instance: Button):
		"""Maneja el clic en el botón de idioma.
		
		Args:
			instance: Instancia del botón presionado
		"""
		# TODO: Implementar selector de idioma
		logging.info("Botón de idioma presionado (no implementado)")
	
	def on_reset_button(self, instance: Button):
		"""Maneja el clic en el botón de reiniciar progreso.
		
		Args:
			instance: Instancia del botón presionado
		"""
		# TODO: Implementar diálogo de confirmación
		logging.warning("Botón de reinicio presionado - Implementar confirmación")
		
		# Por ahora solo mostrar en el botón que se presionó
		instance.text = '⚠️ CONFIRMAR REINICIO'
		instance.background_color = [1, 0.4, 0.4, 1]
	
	def on_back_button(self, instance: Button):
		"""Maneja el clic en el botón de volver.
		
		Args:
			instance: Instancia del botón presionado
		"""
		logging.info("Volviendo desde configuración")
		self.go_back()
	
	def on_enter(self, *args):
		"""Método llamado cuando se entra a la pantalla."""
		super().on_enter(*args)
		
		# Actualizar switches con valores actuales
		if self.sound_switch:
			self.sound_switch.active = self.save_manager.get_setting('sound_enabled', 'true') == 'true'
		if self.vibration_switch:
			self.vibration_switch.active = self.save_manager.get_setting('vibration_enabled', 'true') == 'true'
		
		logging.info("Entrada a pantalla de configuración")
