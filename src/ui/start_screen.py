"""Pantalla de inicio para SiKIdle.

Menú principal con botones de navegación y espacio para publicidad.
"""

import logging
from typing import Any

from kivy.app import App  # type: ignore
from kivy.uix.boxlayout import BoxLayout  # type: ignore
from kivy.uix.button import Button  # type: ignore
from kivy.uix.label import Label  # type: ignore
from kivy.uix.popup import Popup  # type: ignore
from kivy.utils import platform  # type: ignore

from config.mobile_config import MobileConfig
from ui.screen_manager import SiKIdleScreen


class StartScreen(SiKIdleScreen):
	"""Pantalla de inicio/menú principal del juego."""

	def __init__(self, **kwargs: Any):
		"""Inicializa la pantalla de inicio."""
		super().__init__(**kwargs)
		self.build_ui()

	def build_ui(self):
		"""Construye la interfaz de la pantalla de inicio."""
		# Layout principal
		main_layout = BoxLayout(
			orientation='vertical',
			padding=[30, 40, 30, 20],
			spacing=25
		)

		# Espacio para banner superior (AdMob placeholder)
		banner_top = Label(
			text='[ ESPACIO PARA BANNER PUBLICITARIO ]',
			font_size='12sp',
			size_hint=(1, None),
			height='50dp',
			color=[0.5, 0.5, 0.5, 1]
		)
		main_layout.add_widget(banner_top)

		# Título principal
		title_label = Label(
			text='SiKIdle',
			font_size='72sp',
			size_hint=(1, 0.25),
			bold=True,
			color=[0.2, 0.8, 1, 1]  # Azul claro
		)
		main_layout.add_widget(title_label)

		# Subtítulo
		subtitle_label = Label(
			text='¡El idle clicker más adictivo!',
			font_size='18sp',
			size_hint=(1, 0.1),
			color=[0.9, 0.9, 0.9, 1]
		)
		main_layout.add_widget(subtitle_label)

		# Espacio
		main_layout.add_widget(Label(size_hint=(1, 0.1)))

		# Botón principal "Jugar"
		play_button = Button(
			text='🎮 ¡JUGAR!',
			font_size='24sp',
			size_hint=(1, 0.15),
			background_color=[0.2, 0.8, 0.2, 1]  # Verde
		)
		play_button.bind(on_press=self.on_play_button)
		main_layout.add_widget(play_button)

		# Espacio
		main_layout.add_widget(Label(size_hint=(1, 0.05)))

		# Botones secundarios en layout horizontal
		buttons_layout = BoxLayout(
			orientation='horizontal',
			size_hint=(1, 0.12),
			spacing=15
		)

		# Botón Estadísticas
		stats_button = Button(
			text='📊 Estadísticas',
			font_size='16sp',
			background_color=[0.8, 0.6, 0.2, 1]  # Naranja
		)
		stats_button.bind(on_press=self.on_stats_button)
		buttons_layout.add_widget(stats_button)

		# Botón Configuración
		settings_button = Button(
			text='⚙️ Configuración',
			font_size='16sp',
			background_color=[0.6, 0.6, 0.8, 1]  # Azul grisáceo
		)
		settings_button.bind(on_press=self.on_settings_button)
		buttons_layout.add_widget(settings_button)

		# Botón Salir
		exit_button = Button(
			text='❌ Salir',
			font_size='16sp',
			background_color=[0.8, 0.3, 0.3, 1]  # Rojo
		)
		exit_button.bind(on_press=self.on_exit_button)
		buttons_layout.add_widget(exit_button)

		main_layout.add_widget(buttons_layout)

		# Espacio
		main_layout.add_widget(Label(size_hint=(1, 0.1)))

		# Información del dispositivo
		config_info = MobileConfig.get_resolution_info()
		device_info = Label(
			text=f'Plataforma: {platform} | Resolución: {config_info["width"]}x{config_info["height"]}',
			font_size='12sp',
			size_hint=(1, 0.08),
			color=[0.6, 0.6, 0.6, 1]
		)
		main_layout.add_widget(device_info)

		# Versión del juego
		version_label = Label(
			text='v1.0.0 - Alpha',
			font_size='12sp',
			size_hint=(1, 0.05),
			color=[0.5, 0.5, 0.5, 1]
		)
		main_layout.add_widget(version_label)

		self.add_widget(main_layout)

		logging.info("Pantalla de inicio construida")

	def on_play_button(self, instance: Button):
		"""Maneja el clic en el botón Jugar.
		
		Args:
			instance: Instancia del botón presionado
		"""
		logging.info("Botón JUGAR presionado - Navegando al juego principal")
		self.navigate_to('main')

	def on_stats_button(self, instance: Button):
		"""Maneja el clic en el botón Estadísticas.
		
		Args:
			instance: Instancia del botón presionado
		"""
		logging.info("Botón ESTADÍSTICAS presionado")
		self.navigate_to('stats')

	def on_settings_button(self, instance: Button):
		"""Maneja el clic en el botón Configuración.
		
		Args:
			instance: Instancia del botón presionado
		"""
		logging.info("Botón CONFIGURACIÓN presionado")
		self.navigate_to('settings')

	def on_exit_button(self, instance: Button):
		"""Maneja el clic en el botón Salir.
		
		Args:
			instance: Instancia del botón presionado
		"""
		logging.info("Botón SALIR presionado - Mostrando confirmación")
		self.show_exit_confirmation()

	def show_exit_confirmation(self):
		"""Muestra un popup de confirmación para salir del juego."""
		# Layout del popup
		popup_layout = BoxLayout(
			orientation='vertical',
			padding=20,
			spacing=15
		)

		# Mensaje de confirmación
		message_label = Label(
			text='¿Estás seguro de que quieres salir?',
			font_size='18sp',
			size_hint=(1, 0.6),
			text_size=(300, None),
			halign='center',
			valign='middle'
		)
		popup_layout.add_widget(message_label)

		# Layout de botones
		buttons_layout = BoxLayout(
			orientation='horizontal',
			size_hint=(1, 0.4),
			spacing=10
		)

		# Botón Cancelar
		cancel_button = Button(
			text='Cancelar',
			font_size='16sp',
			background_color=[0.6, 0.6, 0.6, 1]
		)

		# Botón Salir
		confirm_button = Button(
			text='Salir',
			font_size='16sp',
			background_color=[0.8, 0.3, 0.3, 1]
		)

		buttons_layout.add_widget(cancel_button)
		buttons_layout.add_widget(confirm_button)
		popup_layout.add_widget(buttons_layout)

		# Crear popup
		exit_popup = Popup(
			title='Confirmar Salida',
			content=popup_layout,
			size_hint=(0.8, 0.4),
			auto_dismiss=False
		)

		# Vincular eventos
		cancel_button.bind(on_press=exit_popup.dismiss)
		confirm_button.bind(on_press=lambda x: self.confirm_exit(exit_popup))

		exit_popup.open()

	def confirm_exit(self, popup: Popup):
		"""Confirma la salida del juego.
		
		Args:
			popup: Instancia del popup a cerrar
		"""
		logging.info("Confirmada salida del juego")
		popup.dismiss()
		
		# Cerrar la aplicación
		app = App.get_running_app()
		if app:
			app.stop()

	def on_enter(self, *args):
		"""Método llamado cuando se entra a la pantalla."""
		super().on_enter(*args)

		# TODO: AdMob integration here - Cargar banner publicitario
		# Aquí se cargaría el banner real de AdMob cuando esté integrado

		logging.info("Entrada a pantalla de inicio")

	def on_leave(self, *args):
		"""Método llamado cuando se sale de la pantalla."""
		super().on_leave(*args)

		# TODO: AdMob integration here - Pausar/ocultar banner si es necesario

		logging.info("Salida de pantalla de inicio")
