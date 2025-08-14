"""
Pantalla de Exploración de Mazmorras para SiKIdle.

Sistema de exploración donde compras acceso a mazmorras que generan recursos automáticamente.
Cada mazmorra tiene su propia temática, recursos que genera, y costos de exploración.
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.progressbar import ProgressBar
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock

from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class MazmorraCard(BoxLayout):
	"""Tarjeta individual de una mazmorra explorable."""

	def __init__(self, mazmorra_data: Dict[str, Any], **kwargs):
		super().__init__(**kwargs)
		self.orientation = "vertical"
		self.size_hint_y = None
		self.height = 180
		self.spacing = 8
		self.padding = [12, 12, 12, 12]

		self.mazmorra_data = mazmorra_data

		self._setup_styling()
		self._build_content()

	def _setup_styling(self):
		"""Configura el estilo visual de la mazmorra."""
		from kivy.graphics import Color, RoundedRectangle

		# Color según rareza/tipo de mazmorra
		rarity_colors = {
			"común": (0.3, 0.3, 0.35, 1),  # Gris
			"rara": (0.2, 0.4, 0.3, 1),  # Verde oscuro
			"épica": (0.3, 0.2, 0.5, 1),  # Púrpura
			"legendaria": (0.5, 0.3, 0.1, 1),  # Dorado oscuro
		}

		color = rarity_colors.get(self.mazmorra_data.get("rareza", "común"), (0.3, 0.3, 0.35, 1))

		with self.canvas.before:
			Color(*color)
			self.bg_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[12, 12, 12, 12])

		self.bind(pos=self._update_bg, size=self._update_bg)

	def _update_bg(self, *args):
		"""Actualiza el fondo de la mazmorra."""
		if hasattr(self, "bg_rect"):
			self.bg_rect.pos = self.pos
			self.bg_rect.size = self.size

	def _build_content(self):
		"""Construye el contenido de la tarjeta de mazmorra."""
		# Header con nombre e icono
		header = BoxLayout(orientation="horizontal", size_hint_y=None, height=40, spacing=8)

		name_label = Label(
			text=f"{self.mazmorra_data['icono']} {self.mazmorra_data['nombre']}",
			font_size="16sp",
			bold=True,
			text_size=(None, None),
			halign="left",
		)
		header.add_widget(name_label)

		# Info de la mazmorra
		info_layout = BoxLayout(orientation="vertical", spacing=4)

		# Descripción
		desc_label = Label(
			text=self.mazmorra_data["descripcion"],
			font_size="12sp",
			text_size=(None, None),
			halign="left",
			color=(0.8, 0.8, 0.8, 1),
		)

		# Recursos que genera
		recursos_text = f"🎁 Genera: {self.mazmorra_data['genera_recurso']} ({self.mazmorra_data['cantidad_por_hora']}/h)"
		recursos_label = Label(
			text=recursos_text,
			font_size="12sp",
			text_size=(None, None),
			halign="left",
			color=(0.6, 1.0, 0.6, 1),
		)

		# Costo de exploración
		costo_text = (
			f"💰 Costo: {self.mazmorra_data['costo']} {self.mazmorra_data['recurso_costo']}"
		)
		costo_label = Label(
			text=costo_text,
			font_size="12sp",
			text_size=(None, None),
			halign="left",
			color=(1.0, 0.8, 0.6, 1),
		)

		info_layout.add_widget(desc_label)
		info_layout.add_widget(recursos_label)
		info_layout.add_widget(costo_label)

		# Botón de exploración/mejora
		button_text = self._get_button_text()
		self.action_button = Button(text=button_text, size_hint_y=None, height=40, font_size="14sp")
		self.action_button.bind(on_press=self._on_action_button)

		# Ensamblar
		self.add_widget(header)
		self.add_widget(info_layout)
		self.add_widget(self.action_button)

	def _get_button_text(self) -> str:
		"""Obtiene el texto del botón según el estado de la mazmorra."""
		if not self.mazmorra_data.get("desbloqueada", False):
			return "🔒 Bloqueada"
		elif self.mazmorra_data.get("explorando", False):
			nivel = self.mazmorra_data.get("nivel", 1)
			return f"⚡ Explorando (Nv.{nivel}) - Mejorar"
		else:
			return "🗺️ Comenzar Exploración"

	def _on_action_button(self, button):
		"""Maneja el clic en el botón de acción."""
		if not self.mazmorra_data.get("desbloqueada", False):
			# Mostrar requisitos para desbloquear
			logger.info(f"Mazmorra {self.mazmorra_data['nombre']} aún no desbloqueada")
			return

		# Aquí iría la lógica de exploración/mejora
		from core.game import get_game_state

		game_state = get_game_state()

		if self.mazmorra_data.get("explorando", False):
			# Mejorar mazmorra existente
			self._upgrade_mazmorra(game_state)
		else:
			# Comenzar exploración
			self._start_exploration(game_state)

	def _start_exploration(self, game_state):
		"""Inicia la exploración de una mazmorra."""
		costo = self.mazmorra_data["costo"]
		recurso_costo = self.mazmorra_data["recurso_costo"]

		# Verificar si tiene recursos suficientes
		from core.resources import ResourceType

		recurso_enum = self._get_resource_enum(recurso_costo)

		if game_state.resource_manager.get_resource(recurso_enum) >= costo:
			# Consumir recursos
			game_state.resource_manager.subtract_resource(recurso_enum, costo)

			# Iniciar exploración
			self.mazmorra_data["explorando"] = True
			self.mazmorra_data["nivel"] = 1

			# Actualizar botón
			self.action_button.text = self._get_button_text()

			logger.info(f"¡Comenzada exploración de {self.mazmorra_data['nombre']}!")
		else:
			logger.warning(f"Recursos insuficientes para explorar {self.mazmorra_data['nombre']}")

	def _get_resource_enum(self, recurso_string: str):
		"""Convierte un string de recurso a su ResourceType enum correspondiente."""
		from core.resources import ResourceType

		resource_mapping = {
			"coins": ResourceType.COINS,
			"Cristales": ResourceType.CRYSTALS,
			"Alimentos": ResourceType.ALIMENTOS,
			"Madera Mágica": ResourceType.MADERA_MAGICA,
			"Hierro": ResourceType.HIERRO,
			"Esencia Arcana": ResourceType.ESENCIA_ARCANA,
			"Oro del Dragón": ResourceType.ORO_DRAGON,
		}

		return resource_mapping.get(recurso_string, ResourceType.COINS)

	def _upgrade_mazmorra(self, game_state):
		"""Mejora una mazmorra en exploración."""
		nivel_actual = self.mazmorra_data.get("nivel", 1)
		costo_mejora = self.mazmorra_data["costo"] * (nivel_actual * 2)
		recurso_costo = self.mazmorra_data["recurso_costo"]

		from core.resources import ResourceType

		recurso_enum = self._get_resource_enum(recurso_costo)

		if game_state.resource_manager.get_resource(recurso_enum) >= costo_mejora:
			# Consumir recursos
			game_state.resource_manager.subtract_resource(recurso_enum, costo_mejora)

			# Mejorar nivel
			self.mazmorra_data["nivel"] = nivel_actual + 1
			self.mazmorra_data["cantidad_por_hora"] = int(
				self.mazmorra_data["cantidad_por_hora"] * 1.5
			)

			# Actualizar botón
			self.action_button.text = self._get_button_text()

			logger.info(
				f"¡{self.mazmorra_data['nombre']} mejorada a nivel {self.mazmorra_data['nivel']}!"
			)
		else:
			logger.warning(f"Recursos insuficientes para mejorar {self.mazmorra_data['nombre']}")


class ExplorationScreen(Screen):
	"""Pantalla principal de exploración de mazmorras."""

	def __init__(self, name: str = "exploration", **kwargs):
		super().__init__(name=name, **kwargs)

		# Datos de mazmorras disponibles
		self.mazmorras_data = self._init_mazmorras_data()

		self._build_ui()

		# Programar actualización de recursos
		Clock.schedule_interval(self._update_exploration_resources, 1.0)

		logger.info("ExplorationScreen initialized")

	def _init_mazmorras_data(self) -> Dict[str, Dict[str, Any]]:
		"""Inicializa los datos de todas las mazmorras disponibles."""
		return {
			"praderas_verdes": {
				"nombre": "Praderas Verdes",
				"icono": "🌾",
				"descripcion": "Vastas praderas llenas de recursos naturales",
				"genera_recurso": "Alimentos",
				"cantidad_por_hora": 10,
				"costo": 50,
				"recurso_costo": "coins",
				"rareza": "común",
				"desbloqueada": True,
				"explorando": False,
				"nivel": 1,
			},
			"cavernas_cristal": {
				"nombre": "Cavernas de Cristal",
				"icono": "💎",
				"descripcion": "Profundas cavernas con cristales de energía",
				"genera_recurso": "Cristales",
				"cantidad_por_hora": 5,
				"costo": 100,
				"recurso_costo": "coins",
				"rareza": "rara",
				"desbloqueada": True,
				"explorando": False,
				"nivel": 1,
			},
			"bosque_ancestral": {
				"nombre": "Bosque Ancestral",
				"icono": "🌲",
				"descripcion": "Bosque milenario con madera mágica y hierbas raras",
				"genera_recurso": "Madera Mágica",
				"cantidad_por_hora": 8,
				"costo": 200,
				"recurso_costo": "coins",
				"rareza": "rara",
				"desbloqueada": False,
				"explorando": False,
				"nivel": 1,
			},
			"minas_hierro": {
				"nombre": "Minas de Hierro Profundo",
				"icono": "⛏️",
				"descripcion": "Minas abandonadas con vetas de hierro puro",
				"genera_recurso": "Hierro",
				"cantidad_por_hora": 15,
				"costo": 150,
				"recurso_costo": "coins",
				"rareza": "común",
				"desbloqueada": False,
				"explorando": False,
				"nivel": 1,
			},
			"ruinas_arcanas": {
				"nombre": "Ruinas Arcanas",
				"icono": "🔮",
				"descripcion": "Ruinas de una civilización mágica antigua",
				"genera_recurso": "Esencia Arcana",
				"cantidad_por_hora": 3,
				"costo": 500,
				"recurso_costo": "Cristales",
				"rareza": "épica",
				"desbloqueada": False,
				"explorando": False,
				"nivel": 1,
			},
			"fortaleza_dragon": {
				"nombre": "Fortaleza del Dragón",
				"icono": "🐉",
				"descripcion": "Fortaleza de un dragón legendario llena de tesoros",
				"genera_recurso": "Oro del Dragón",
				"cantidad_por_hora": 1,
				"costo": 1000,
				"recurso_costo": "Esencia Arcana",
				"rareza": "legendaria",
				"desbloqueada": False,
				"explorando": False,
				"nivel": 1,
			},
		}

	def _build_ui(self):
		"""Construye la interfaz de usuario."""
		main_layout = BoxLayout(orientation="vertical", spacing=10, padding=[10, 10, 10, 10])

		# Header
		header = self._create_header()
		main_layout.add_widget(header)

		# Scroll de mazmorras
		scroll = ScrollView()

		mazmorras_container = GridLayout(cols=1, spacing=10, size_hint_y=None, padding=[5, 5, 5, 5])
		mazmorras_container.bind(minimum_height=mazmorras_container.setter("height"))

		# Añadir tarjetas de mazmorras
		for mazmorra_id, mazmorra_data in self.mazmorras_data.items():
			card = MazmorraCard(mazmorra_data)
			mazmorras_container.add_widget(card)

		scroll.add_widget(mazmorras_container)
		main_layout.add_widget(scroll)

		self.add_widget(main_layout)

	def _create_header(self) -> BoxLayout:
		"""Crea el header de la pantalla."""
		header = BoxLayout(orientation="vertical", size_hint_y=None, height=80, spacing=5)

		title_label = Label(
			text="🗺️ Exploración de Mazmorras",
			font_size="20sp",
			bold=True,
			size_hint_y=None,
			height=40,
		)

		subtitle_label = Label(
			text="Envía expediciones para obtener recursos automáticamente",
			font_size="14sp",
			color=(0.8, 0.8, 0.8, 1),
			size_hint_y=None,
			height=30,
		)

		header.add_widget(title_label)
		header.add_widget(subtitle_label)

		return header

	def _update_exploration_resources(self, dt):
		"""Actualiza los recursos generados por exploraciones activas."""
		try:
			from core.game import get_game_state

			game_state = get_game_state()

			for mazmorra_data in self.mazmorras_data.values():
				if mazmorra_data.get("explorando", False):
					# Generar recursos por segundo (cantidad_por_hora / 3600)
					recursos_por_segundo = mazmorra_data["cantidad_por_hora"] / 3600.0
					recursos_generados = recursos_por_segundo * dt

					# Añadir al resource manager
					recurso_tipo = mazmorra_data["genera_recurso"]
					recurso_enum = self._get_exploration_resource_enum(recurso_tipo)
					game_state.resource_manager.add_resource(recurso_enum, recursos_generados)

		except Exception as e:
			logger.error(f"Error updating exploration resources: {e}")

	def _get_exploration_resource_enum(self, recurso_string: str):
		"""Convierte un string de recurso generado a su ResourceType enum correspondiente."""
		from core.resources import ResourceType

		resource_mapping = {
			"Alimentos": ResourceType.ALIMENTOS,
			"Cristales": ResourceType.CRYSTALS,
			"Madera Mágica": ResourceType.MADERA_MAGICA,
			"Hierro": ResourceType.HIERRO,
			"Esencia Arcana": ResourceType.ESENCIA_ARCANA,
			"Oro del Dragón": ResourceType.ORO_DRAGON,
		}

		return resource_mapping.get(recurso_string, ResourceType.CRYSTALS)

	def on_enter(self):
		"""Llamado cuando se entra a la pantalla."""
		logger.info("Entered ExplorationScreen")

	def on_leave(self):
		"""Llamado cuando se sale de la pantalla."""
		logger.info("Left ExplorationScreen")
