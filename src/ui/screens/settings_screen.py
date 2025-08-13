"""
Pantalla de configuración del juego SiKIdle.

Configuración de audio, idioma, controles y otras opciones del juego.
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.slider import Slider
from kivy.uix.switch import Switch
from kivy.uix.spinner import Spinner
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput

from typing import Dict, Any, Callable, Optional
import logging


class SettingRow(BoxLayout):
	"""Fila de configuración individual."""
	
	def __init__(self, title: str, description: str = "", **kwargs):
		super().__init__(**kwargs)
		self.orientation = 'horizontal'
		self.size_hint_y = None
		self.height = 60
		self.spacing = 16
		self.padding = [16, 8, 16, 8]
		
		self._setup_styling()
		self._build_content(title, description)
	
	def _setup_styling(self):
		"""Configura el estilo de la fila."""
		from kivy.graphics import Color, RoundedRectangle
		
		with self.canvas.before:
			Color(0.25, 0.25, 0.30, 0.8)
			self.bg_rect = RoundedRectangle(
				pos=self.pos,
				size=self.size,
				radius=[8, 8, 8, 8]
			)
		
		self.bind(pos=self._update_bg, size=self._update_bg)
	
	def _update_bg(self, *args):
		"""Actualiza el fondo de la fila."""
		if hasattr(self, 'bg_rect'):
			self.bg_rect.pos = self.pos
			self.bg_rect.size = self.size
	
	def _build_content(self, title: str, description: str):
		"""Construye el contenido de la fila."""
		# Layout de texto
		text_layout = BoxLayout(
			orientation='vertical',
			size_hint_x=0.7,
			spacing=2
		)
		
		# Título
		title_label = Label(
			text=title,
			font_size='14sp',
			bold=True,
			halign='left',
			valign='center',
			size_hint_y=0.6
		)
		title_label.bind(texture_size=title_label.setter('text_size'))
		
		# Descripción (si existe)
		if description:
			desc_label = Label(
				text=description,
				font_size='11sp',
				opacity=0.7,
				halign='left',
				valign='center',
				size_hint_y=0.4
			)
			desc_label.bind(texture_size=desc_label.setter('text_size'))
			text_layout.add_widget(desc_label)
		
		text_layout.add_widget(title_label)
		
		# Container para el control
		self.control_container = BoxLayout(
			orientation='horizontal',
			size_hint_x=0.3,
			spacing=8
		)
		
		self.add_widget(text_layout)
		self.add_widget(self.control_container)
	
	def add_control(self, control_widget):
		"""Añade un widget de control a la fila."""
		self.control_container.add_widget(control_widget)


class SettingSection(BoxLayout):
	"""Sección de configuración con título."""
	
	def __init__(self, title: str, **kwargs):
		super().__init__(**kwargs)
		self.orientation = 'vertical'
		self.size_hint_y = None
		self.spacing = 8
		self.padding = [0, 16, 0, 8]
		
		self._build_section(title)
	
	def _build_section(self, title: str):
		"""Construye la sección."""
		# Título de sección
		title_label = Label(
			text=title,
			font_size='16sp',
			bold=True,
			size_hint_y=None,
			height=30,
			halign='left',
			color=(0.20, 0.60, 0.86, 1)
		)
		title_label.bind(texture_size=title_label.setter('text_size'))
		
		# Container para las filas
		self.rows_container = BoxLayout(
			orientation='vertical',
			size_hint_y=None,
			spacing=4
		)
		self.rows_container.bind(minimum_height=self.rows_container.setter('height'))
		
		self.add_widget(title_label)
		self.add_widget(self.rows_container)
		
		# Calcular altura
		self.bind(minimum_height=self.setter('height'))
	
	def add_setting_row(self, setting_row: SettingRow):
		"""Añade una fila de configuración."""
		self.rows_container.add_widget(setting_row)


class VolumeSlider(BoxLayout):
	"""Slider de volumen personalizado."""
	
	def __init__(self, initial_value: float = 1.0, on_change: Callable = None, **kwargs):
		super().__init__(**kwargs)
		self.orientation = 'horizontal'
		self.spacing = 8
		self.on_change_callback = on_change
		
		# Slider
		self.slider = Slider(
			min=0,
			max=1,
			value=initial_value,
			step=0.1,
			size_hint_x=0.8
		)
		self.slider.bind(value=self._on_value_change)
		
		# Label de valor
		self.value_label = Label(
			text=f"{int(initial_value * 100)}%",
			font_size='12sp',
			size_hint_x=0.2
		)
		
		self.add_widget(self.slider)
		self.add_widget(self.value_label)
	
	def _on_value_change(self, instance, value):
		"""Callback cuando cambia el valor."""
		self.value_label.text = f"{int(value * 100)}%"
		
		if self.on_change_callback:
			self.on_change_callback(value)


class SettingsScreen(Screen):
	"""Pantalla de configuración del juego."""
	
	def __init__(self, name='settings', **kwargs):
		super().__init__(name=name, **kwargs)
		
		# Configuración actual (placeholder)
		self.current_settings = {
			'audio': {
				'master_volume': 1.0,
				'music_volume': 0.8,
				'sfx_volume': 0.9,
				'muted': False
			},
			'game': {
				'auto_save': True,
				'notifications': True,
				'language': 'español',
				'difficulty': 'normal'
			},
			'interface': {
				'animations': True,
				'tooltips': True,
				'screen_shake': True,
				'font_size': 'normal'
			},
			'data': {
				'analytics': False,
				'cloud_save': False
			},
			'debug': {
				'mode_enabled': False,
				'password': 'dev2025'
			}
		}
		
		self._build_layout()
		logging.info("SettingsScreen initialized")
	
	def _build_layout(self):
		"""Construye el layout principal."""
		# Scroll view principal
		scroll = ScrollView()
		
		main_layout = BoxLayout(
			orientation='vertical',
			spacing=24,
			padding=[16, 16, 16, 16],
			size_hint_y=None
		)
		main_layout.bind(minimum_height=main_layout.setter('height'))
		
		# Secciones de configuración
		audio_section = self._create_audio_section()
		game_section = self._create_game_section()
		interface_section = self._create_interface_section()
		data_section = self._create_data_section()
		debug_section = self._create_debug_section()
		actions_section = self._create_actions_section()
		
		# Ensamblar layout
		main_layout.add_widget(audio_section)
		main_layout.add_widget(game_section)
		main_layout.add_widget(interface_section)
		main_layout.add_widget(data_section)
		main_layout.add_widget(debug_section)
		main_layout.add_widget(actions_section)
		
		scroll.add_widget(main_layout)
		self.add_widget(scroll)
	
	def _create_audio_section(self) -> SettingSection:
		"""Crea la sección de configuración de audio."""
		section = SettingSection("🔊 Configuración de Audio")
		
		# Volumen maestro
		master_row = SettingRow(
			"Volumen Maestro",
			"Controla el volumen general del juego"
		)
		master_slider = VolumeSlider(
			self.current_settings['audio']['master_volume'],
			self._on_master_volume_change
		)
		master_row.add_control(master_slider)
		section.add_setting_row(master_row)
		
		# Volumen de música
		music_row = SettingRow(
			"Volumen de Música",
			"Controla la música de fondo"
		)
		music_slider = VolumeSlider(
			self.current_settings['audio']['music_volume'],
			self._on_music_volume_change
		)
		music_row.add_control(music_slider)
		section.add_setting_row(music_row)
		
		# Volumen de efectos
		sfx_row = SettingRow(
			"Volumen de Efectos",
			"Controla los sonidos de efectos"
		)
		sfx_slider = VolumeSlider(
			self.current_settings['audio']['sfx_volume'],
			self._on_sfx_volume_change
		)
		sfx_row.add_control(sfx_slider)
		section.add_setting_row(sfx_row)
		
		# Silenciar todo
		mute_row = SettingRow(
			"Silenciar Audio",
			"Desactiva completamente todos los sonidos"
		)
		mute_switch = Switch(
			active=self.current_settings['audio']['muted']
		)
		mute_switch.bind(active=self._on_mute_change)
		mute_row.add_control(mute_switch)
		section.add_setting_row(mute_row)
		
		return section
	
	def _create_game_section(self) -> SettingSection:
		"""Crea la sección de configuración de juego."""
		section = SettingSection("🎮 Configuración de Juego")
		
		# Auto guardado
		autosave_row = SettingRow(
			"Guardado Automático",
			"Guarda automáticamente el progreso"
		)
		autosave_switch = Switch(
			active=self.current_settings['game']['auto_save']
		)
		autosave_switch.bind(active=self._on_autosave_change)
		autosave_row.add_control(autosave_switch)
		section.add_setting_row(autosave_row)
		
		# Notificaciones
		notifications_row = SettingRow(
			"Notificaciones",
			"Muestra notificaciones de logros y eventos"
		)
		notifications_switch = Switch(
			active=self.current_settings['game']['notifications']
		)
		notifications_switch.bind(active=self._on_notifications_change)
		notifications_row.add_control(notifications_switch)
		section.add_setting_row(notifications_row)
		
		# Idioma
		language_row = SettingRow(
			"Idioma",
			"Selecciona el idioma del juego"
		)
		language_spinner = Spinner(
			text=self.current_settings['game']['language'],
			values=['español', 'english', 'français'],
			size_hint_x=None,
			width=120
		)
		language_spinner.bind(text=self._on_language_change)
		language_row.add_control(language_spinner)
		section.add_setting_row(language_row)
		
		# Dificultad
		difficulty_row = SettingRow(
			"Dificultad",
			"Ajusta la dificultad del juego"
		)
		difficulty_spinner = Spinner(
			text=self.current_settings['game']['difficulty'],
			values=['fácil', 'normal', 'difícil', 'extrema'],
			size_hint_x=None,
			width=120
		)
		difficulty_spinner.bind(text=self._on_difficulty_change)
		difficulty_row.add_control(difficulty_spinner)
		section.add_setting_row(difficulty_row)
		
		return section
	
	def _create_interface_section(self) -> SettingSection:
		"""Crea la sección de configuración de interfaz."""
		section = SettingSection("🖥️ Configuración de Interfaz")
		
		# Animaciones
		animations_row = SettingRow(
			"Animaciones",
			"Activa/desactiva las animaciones de la UI"
		)
		animations_switch = Switch(
			active=self.current_settings['interface']['animations']
		)
		animations_switch.bind(active=self._on_animations_change)
		animations_row.add_control(animations_switch)
		section.add_setting_row(animations_row)
		
		# Tooltips
		tooltips_row = SettingRow(
			"Tooltips",
			"Muestra información adicional al pasar el cursor"
		)
		tooltips_switch = Switch(
			active=self.current_settings['interface']['tooltips']
		)
		tooltips_switch.bind(active=self._on_tooltips_change)
		tooltips_row.add_control(tooltips_switch)
		section.add_setting_row(tooltips_row)
		
		# Screen shake
		shake_row = SettingRow(
			"Vibración de Pantalla",
			"Efectos de vibración en combate"
		)
		shake_switch = Switch(
			active=self.current_settings['interface']['screen_shake']
		)
		shake_switch.bind(active=self._on_screen_shake_change)
		shake_row.add_control(shake_switch)
		section.add_setting_row(shake_row)
		
		# Tamaño de fuente
		font_row = SettingRow(
			"Tamaño de Fuente",
			"Ajusta el tamaño del texto"
		)
		font_spinner = Spinner(
			text=self.current_settings['interface']['font_size'],
			values=['pequeño', 'normal', 'grande', 'extra grande'],
			size_hint_x=None,
			width=120
		)
		font_spinner.bind(text=self._on_font_size_change)
		font_row.add_control(font_spinner)
		section.add_setting_row(font_row)
		
		return section
	
	def _create_data_section(self) -> SettingSection:
		"""Crea la sección de configuración de datos."""
		section = SettingSection("💾 Configuración de Datos")
		
		# Analytics
		analytics_row = SettingRow(
			"Análisis de Uso",
			"Envía datos anónimos para mejorar el juego"
		)
		analytics_switch = Switch(
			active=self.current_settings['data']['analytics']
		)
		analytics_switch.bind(active=self._on_analytics_change)
		analytics_row.add_control(analytics_switch)
		section.add_setting_row(analytics_row)
		
		# Cloud save
		cloud_row = SettingRow(
			"Guardado en la Nube",
			"Sincroniza tu progreso en múltiples dispositivos"
		)
		cloud_switch = Switch(
			active=self.current_settings['data']['cloud_save']
		)
		cloud_switch.bind(active=self._on_cloud_save_change)
		cloud_row.add_control(cloud_switch)
		section.add_setting_row(cloud_row)
		
		return section
	
	def _create_debug_section(self) -> SettingSection:
		"""Crea la sección de modo debug."""
		section = SettingSection("🔧 Modo Debug (Desarrollo)")
		
		# Campo de contraseña
		password_row = SettingRow(
			"Contraseña Debug",
			"Introduce la contraseña para activar modo debug"
		)
		
		password_layout = BoxLayout(orientation='horizontal', spacing=8)
		
		self.password_input = TextInput(
			text='',
			password=True,
			multiline=False,
			size_hint_x=0.7,
			height=30,
			size_hint_y=None
		)
		
		activate_btn = Button(
			text="Activar",
			size_hint_x=0.3,
			height=30,
			size_hint_y=None
		)
		activate_btn.bind(on_press=self._toggle_debug_mode)
		
		password_layout.add_widget(self.password_input)
		password_layout.add_widget(activate_btn)
		password_row.add_control(password_layout)
		section.add_setting_row(password_row)
		
		# Estado del modo debug
		status_row = SettingRow(
			"Estado Debug",
			"Muestra si el modo debug está activo"
		)
		
		self.debug_status_label = Label(
			text="❌ Desactivado",
			font_size='12sp',
			color=(0.8, 0.2, 0.2, 1)
		)
		status_row.add_control(self.debug_status_label)
		section.add_setting_row(status_row)
		
		return section
	
	def _create_actions_section(self) -> BoxLayout:
		"""Crea la sección de acciones."""
		container = BoxLayout(
			orientation='vertical',
			size_hint_y=None,
			height=200,
			spacing=16,
			padding=[0, 24, 0, 24]
		)
		
		# Título
		title_label = Label(
			text="⚙️ Acciones",
			font_size='16sp',
			bold=True,
			size_hint_y=None,
			height=30,
			halign='left',
			color=(0.20, 0.60, 0.86, 1)
		)
		title_label.bind(texture_size=title_label.setter('text_size'))
		
		# Grid de botones
		actions_grid = GridLayout(
			cols=2,
			spacing=12,
			size_hint_y=None,
			height=140
		)
		
		# Botones de acción
		export_btn = Button(
			text="📤 Exportar Datos",
			size_hint_y=None,
			height=60
		)
		export_btn.bind(on_press=self._export_data)
		
		import_btn = Button(
			text="📥 Importar Datos", 
			size_hint_y=None,
			height=60
		)
		import_btn.bind(on_press=self._import_data)
		
		reset_btn = Button(
			text="🔄 Restablecer Config",
			size_hint_y=None,
			height=60
		)
		reset_btn.bind(on_press=self._reset_settings)
		
		about_btn = Button(
			text="ℹ️ Acerca de",
			size_hint_y=None,
			height=60
		)
		about_btn.bind(on_press=self._show_about)
		
		actions_grid.add_widget(export_btn)
		actions_grid.add_widget(import_btn)
		actions_grid.add_widget(reset_btn)
		actions_grid.add_widget(about_btn)
		
		container.add_widget(title_label)
		container.add_widget(actions_grid)
		
		return container
	
	# Callbacks de configuración de audio
	def _on_master_volume_change(self, value: float):
		"""Callback para cambio de volumen maestro."""
		self.current_settings['audio']['master_volume'] = value
		logging.info(f"Master volume changed to: {value}")
	
	def _on_music_volume_change(self, value: float):
		"""Callback para cambio de volumen de música."""
		self.current_settings['audio']['music_volume'] = value
		logging.info(f"Music volume changed to: {value}")
	
	def _on_sfx_volume_change(self, value: float):
		"""Callback para cambio de volumen de efectos."""
		self.current_settings['audio']['sfx_volume'] = value
		logging.info(f"SFX volume changed to: {value}")
	
	def _on_mute_change(self, instance, active: bool):
		"""Callback para silenciar audio."""
		self.current_settings['audio']['muted'] = active
		logging.info(f"Audio muted: {active}")
	
	# Callbacks de configuración de juego
	def _on_autosave_change(self, instance, active: bool):
		"""Callback para auto guardado."""
		self.current_settings['game']['auto_save'] = active
		logging.info(f"Auto save: {active}")
	
	def _on_notifications_change(self, instance, active: bool):
		"""Callback para notificaciones."""
		self.current_settings['game']['notifications'] = active
		logging.info(f"Notifications: {active}")
	
	def _on_language_change(self, instance, text: str):
		"""Callback para cambio de idioma."""
		self.current_settings['game']['language'] = text
		logging.info(f"Language changed to: {text}")
	
	def _on_difficulty_change(self, instance, text: str):
		"""Callback para cambio de dificultad."""
		self.current_settings['game']['difficulty'] = text
		logging.info(f"Difficulty changed to: {text}")
	
	# Callbacks de configuración de interfaz
	def _on_animations_change(self, instance, active: bool):
		"""Callback para animaciones."""
		self.current_settings['interface']['animations'] = active
		logging.info(f"Animations: {active}")
	
	def _on_tooltips_change(self, instance, active: bool):
		"""Callback para tooltips."""
		self.current_settings['interface']['tooltips'] = active
		logging.info(f"Tooltips: {active}")
	
	def _on_screen_shake_change(self, instance, active: bool):
		"""Callback para vibración de pantalla."""
		self.current_settings['interface']['screen_shake'] = active
		logging.info(f"Screen shake: {active}")
	
	def _on_font_size_change(self, instance, text: str):
		"""Callback para tamaño de fuente."""
		self.current_settings['interface']['font_size'] = text
		logging.info(f"Font size changed to: {text}")
	
	# Callbacks de configuración de datos
	def _on_analytics_change(self, instance, active: bool):
		"""Callback para analytics."""
		self.current_settings['data']['analytics'] = active
		logging.info(f"Analytics: {active}")
	
	def _on_cloud_save_change(self, instance, active: bool):
		"""Callback para guardado en la nube."""
		self.current_settings['data']['cloud_save'] = active
		logging.info(f"Cloud save: {active}")
	
	def _toggle_debug_mode(self, instance):
		"""Activa/desactiva el modo debug."""
		password = self.password_input.text.strip()
		
		if password == self.current_settings['debug']['password']:
			self.current_settings['debug']['mode_enabled'] = not self.current_settings['debug']['mode_enabled']
			
			if self.current_settings['debug']['mode_enabled']:
				self.debug_status_label.text = "✅ Activado"
				self.debug_status_label.color = (0.2, 0.8, 0.2, 1)
				logging.info("DEBUG MODE ENABLED")
				self._enable_debug_mode()
			else:
				self.debug_status_label.text = "❌ Desactivado"
				self.debug_status_label.color = (0.8, 0.2, 0.2, 1)
				logging.info("DEBUG MODE DISABLED")
				self._disable_debug_mode()
			
			self.password_input.text = ''
		else:
			popup = Popup(
				title="Contraseña Incorrecta",
				content=Label(text="Contraseña incorrecta"),
				size_hint=(0.5, 0.3)
			)
			popup.open()
			self.password_input.text = ''
	
	def _enable_debug_mode(self):
		"""Activa el modo debug."""
		try:
			from kivy.app import App
			app = App.get_running_app()
			if hasattr(app, 'main_layout') and app.main_layout:
				tab_navigator = app.main_layout.tab_navigator
				if hasattr(tab_navigator, 'enable_debug_mode'):
					tab_navigator.enable_debug_mode()
		except Exception as e:
			logging.error(f"Error enabling debug mode: {e}")
	
	def _disable_debug_mode(self):
		"""Desactiva el modo debug."""
		try:
			from kivy.app import App
			app = App.get_running_app()
			if hasattr(app, 'main_layout') and app.main_layout:
				tab_navigator = app.main_layout.tab_navigator
				if hasattr(tab_navigator, 'disable_debug_mode'):
					tab_navigator.disable_debug_mode()
		except Exception as e:
			logging.error(f"Error disabling debug mode: {e}")
	
	# Acciones
	def _export_data(self, instance):
		"""Exporta los datos del juego."""
		popup = Popup(
			title="Exportar Datos",
			content=Label(text="Funcionalidad de exportación\npronto disponible..."),
			size_hint=(0.6, 0.4)
		)
		popup.open()
		logging.info("Export data requested")
	
	def _import_data(self, instance):
		"""Importa datos del juego."""
		popup = Popup(
			title="Importar Datos",
			content=Label(text="Funcionalidad de importación\npronto disponible..."),
			size_hint=(0.6, 0.4)
		)
		popup.open()
		logging.info("Import data requested")
	
	def _reset_settings(self, instance):
		"""Restablece la configuración por defecto."""
		popup = Popup(
			title="Confirmar Restablecimiento",
			content=Label(text="¿Estás seguro de que quieres\nrestablecer toda la configuración?"),
			size_hint=(0.6, 0.4)
		)
		popup.open()
		logging.info("Reset settings requested")
	
	def _show_about(self, instance):
		"""Muestra información sobre el juego."""
		about_text = """SiKIdle v1.0.0

Un videojuego idle clicker dungeon crawler
desarrollado con Python y Kivy.

© 2025 - Desarrollado por IA
Proyecto de código abierto"""
		
		popup = Popup(
			title="Acerca de SiKIdle",
			content=Label(text=about_text, halign='center'),
			size_hint=(0.7, 0.6)
		)
		popup.open()
		logging.info("About dialog shown")
	
	def save_settings(self):
		"""Guarda la configuración actual."""
		# TODO: Implementar guardado real en base de datos
		logging.info("Settings saved")
	
	def load_settings(self):
		"""Carga la configuración guardada."""
		# TODO: Implementar carga real desde base de datos
		logging.info("Settings loaded")
	
	def on_enter(self):
		"""Callback ejecutado cuando se entra en la pantalla."""
		logging.info("Entered SettingsScreen")
		self.load_settings()
	
	def on_leave(self):
		"""Callback ejecutado cuando se sale de la pantalla."""
		logging.info("Left SettingsScreen")
		self.save_settings()
