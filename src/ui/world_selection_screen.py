"""Pantalla de selección de mundos con interfaz visual premium.

Inspirada en los mejores idle clickers como AFK Arena y Tap Titans 2.
Incluye previews visuales, información de progreso y elementos de gamificación.
"""

import logging
from typing import Dict, List, Optional

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.progressbar import ProgressBar
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.animation import Animation
from kivy.clock import Clock

from core.game import get_game_state
from core.visual_assets import VisualAssetManager, BackgroundType
from core.worlds import WorldType

logger = logging.getLogger(__name__)


class PremiumWorldCard(BoxLayout):
	"""Tarjeta visual premium para mostrar información de un mundo."""

	def __init__(self, world_info: Dict, **kwargs):
		super().__init__(**kwargs)
		self.orientation = "vertical"
		self.size_hint = (None, None)
		self.size = (320, 450)
		self.spacing = 12
		self.padding = 20

		self.world_info = world_info
		self.visual_manager = VisualAssetManager()
		self.is_unlocked = False
		self.is_completed = False

		# Configurar fondo de la tarjeta con gradiente
		with self.canvas.before:
			# Fondo principal
			Color(0.15, 0.15, 0.15, 0.95)
			self.bg_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[20, 20, 20, 20])

			# Borde brillante para mundos desbloqueados
			self.border_color = Color(0, 0, 0, 0)  # Invisible por defecto
			self.border_rect = RoundedRectangle(
				pos=(self.pos[0] - 3, self.pos[1] - 3),
				size=(self.size[0] + 6, self.size[1] + 6),
				radius=[23, 23, 23, 23],
			)

		self.bind(pos=self._update_bg, size=self._update_bg)

		self._build_card()
		self._setup_animations()

	def _update_bg(self, *args):
		"""Actualiza el fondo de la tarjeta."""
		self.bg_rect.pos = self.pos
		self.bg_rect.size = self.size
		self.border_rect.pos = (self.pos[0] - 3, self.pos[1] - 3)
		self.border_rect.size = (self.size[0] + 6, self.size[1] + 6)

	def _setup_animations(self):
		"""Configura animaciones de la tarjeta."""
		# Animación de hover sutil
		self.hover_anim = Animation(
			opacity=0.95, duration=3.0, transition="in_out_sine"
		) + Animation(opacity=1.0, duration=3.0, transition="in_out_sine")
		self.hover_anim.repeat = True
		self.hover_anim.start(self)

	def _build_card(self):
		"""Construye el contenido visual de la tarjeta."""
		# Imagen de preview del mundo
		self.world_image = Image(
			source=self.visual_manager.get_background_path(
				BackgroundType(self.world_info["background"])
			),
			size_hint=(1, 0.5),
			allow_stretch=True,
			keep_ratio=False,
		)
		self.add_widget(self.world_image)

		# Información del mundo
		info_layout = BoxLayout(orientation="vertical", size_hint=(1, 0.3), spacing=5)

		# Nombre del mundo
		name_label = Label(
			text=self.world_info["name"],
			font_size="18sp",
			bold=True,
			color=(1, 1, 1, 1),
			size_hint=(1, None),
			height=30,
			text_size=(None, None),
		)
		info_layout.add_widget(name_label)

		# Descripción
		desc_label = Label(
			text=self.world_info["description"],
			font_size="12sp",
			color=(0.8, 0.8, 0.8, 1),
			size_hint=(1, None),
			height=40,
			text_size=(280, None),
			halign="center",
			valign="middle",
		)
		info_layout.add_widget(desc_label)

		# Barra de progreso
		progress_layout = BoxLayout(
			orientation="vertical", size_hint=(1, None), height=40, spacing=2
		)

		progress_label = Label(
			text="Progreso: 0/50",
			font_size="10sp",
			color=(0.7, 0.7, 0.7, 1),
			size_hint=(1, None),
			height=15,
		)
		progress_layout.add_widget(progress_label)

		self.progress_bar = ProgressBar(max=50, value=0, size_hint=(1, None), height=20)
		progress_layout.add_widget(self.progress_bar)

		info_layout.add_widget(progress_layout)
		self.add_widget(info_layout)

		# Botón de acción
		self.action_button = Button(
			text="🔒 BLOQUEADO",
			size_hint=(1, 0.2),
			background_color=(0.3, 0.3, 0.3, 1),
			color=(0.6, 0.6, 0.6, 1),
			font_size="14sp",
			bold=True,
		)
		self.action_button.bind(on_press=self._on_action_button_press)
		self.add_widget(self.action_button)

		# Actualizar estado inicial
		self._update_card_state()

	def _update_card_state(self):
		"""Actualiza el estado visual de la tarjeta."""
		game_state = get_game_state()
		world_id = self.world_info["id"]

		# Obtener información de progreso del mundo
		if hasattr(game_state, "world_manager"):
			progress_info = game_state.world_manager.get_world_progress_info(world_id)

			if progress_info.get("unlocked", True):  # Por defecto desbloqueado
				# Mundo desbloqueado
				self.action_button.text = "🌟 EXPLORAR"
				self.action_button.background_color = (0.2, 0.7, 0.2, 1)
				self.action_button.color = (1, 1, 1, 1)

				# Actualizar progreso
				current_level = progress_info.get("current_level", 1)
				max_level = progress_info.get("level_range", [1, 50])[1]
				self.progress_bar.value = current_level
				self.progress_bar.max = max_level

				# Actualizar texto de progreso
				progress_text = f"Progreso: {current_level}/{max_level}"
				if progress_info.get("completed", False):
					progress_text += " ✅"

				for child in self.children:
					if isinstance(child, BoxLayout):
						for subchild in child.children:
							if isinstance(subchild, BoxLayout):
								for label in subchild.children:
									if isinstance(label, Label) and "Progreso:" in label.text:
										label.text = progress_text
										break
			else:
				# Mundo bloqueado
				self.action_button.text = "🔒 BLOQUEADO"
				self.action_button.background_color = (0.3, 0.3, 0.3, 1)
				self.action_button.color = (0.6, 0.6, 0.6, 1)

				# Mostrar requisitos
				unlock_level = progress_info.get("unlock_level", 1)
				player_level = game_state.player_stats.get_level()

				if player_level < unlock_level:
					self.action_button.text = f"🔒 Nivel {unlock_level} requerido"

	def _on_action_button_press(self, button):
		"""Maneja el clic en el botón de acción."""
		game_state = get_game_state()
		world_id = self.world_info["id"]

		if hasattr(game_state, "world_manager"):
			progress_info = game_state.world_manager.get_world_progress_info(world_id)

			if progress_info.get("unlocked", True):
				# Cambiar al mundo seleccionado
				if game_state.world_manager.set_active_world(WorldType(world_id)):
					# Navegar a la pantalla de combate
					from ui.navigation import get_navigation_manager

					nav_manager = get_navigation_manager()
					if nav_manager:
						nav_manager.navigate_to("combat")
						logger.info(f"Navegando al mundo: {self.world_info['name']}")
			else:
				# Intentar desbloquear el mundo
				result = game_state.attempt_world_unlock(WorldType(world_id))
				if result.get("success"):
					self._update_card_state()
					# Animación de desbloqueo
					self._animate_unlock()
				else:
					logger.info(
						f"No se pudo desbloquear: {result.get('message', 'Requisitos no cumplidos')}"
					)

	def _animate_unlock(self):
		"""Animación cuando se desbloquea un mundo."""
		# Efecto de brillo
		anim = Animation(opacity=0.5, duration=0.2) + Animation(opacity=1.0, duration=0.2)
		anim.repeat = True
		anim.start(self.world_image)

		# Detener animación después de 1 segundo
		Clock.schedule_once(lambda dt: anim.stop(self.world_image), 1.0)


class WorldSelectionScreen(Screen):
	"""Pantalla principal de selección de mundos."""

	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.name = "world_selection"
		self.visual_manager = VisualAssetManager()

		# Configurar fondo
		with self.canvas.before:
			self.bg_image = Rectangle(
				source=self.visual_manager.get_background_path(BackgroundType.MAIN),
				pos=self.pos,
				size=self.size,
			)

		self.bind(pos=self._update_bg, size=self._update_bg)

		self._build_interface()

		logger.info("WorldSelectionScreen inicializada")

	def _update_bg(self, *args):
		"""Actualiza el fondo de la pantalla."""
		self.bg_image.pos = self.pos
		self.bg_image.size = self.size

	def _build_interface(self):
		"""Construye la interfaz de la pantalla."""
		main_layout = BoxLayout(orientation="vertical", padding=20, spacing=20)

		# Título
		title_label = Label(
			text="🌍 SELECCIONA TU MUNDO",
			font_size="24sp",
			bold=True,
			color=(1, 1, 1, 1),
			size_hint=(1, None),
			height=60,
		)
		main_layout.add_widget(title_label)

		# Scroll view para las tarjetas de mundos
		scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False, do_scroll_y=True)

		# Grid layout para las tarjetas
		self.worlds_grid = GridLayout(
			cols=2, spacing=20, size_hint_y=None, row_default_height=420, row_force_default=True
		)
		self.worlds_grid.bind(minimum_height=self.worlds_grid.setter("height"))

		scroll.add_widget(self.worlds_grid)
		main_layout.add_widget(scroll)

		# Botón de regreso
		back_button = Button(
			text="⬅️ REGRESAR",
			size_hint=(1, None),
			height=50,
			background_color=(0.2, 0.2, 0.2, 0.8),
			color=(1, 1, 1, 1),
			font_size="16sp",
		)
		back_button.bind(on_press=self._on_back_button)
		main_layout.add_widget(back_button)

		self.add_widget(main_layout)

		# Cargar mundos
		self._load_worlds()

	def _load_worlds(self):
		"""Carga y muestra las tarjetas de todos los mundos."""
		worlds = self.visual_manager.get_all_available_worlds()

		for world_info in worlds:
			world_card = PremiumWorldCard(world_info)
			self.worlds_grid.add_widget(world_card)

		logger.info(f"Cargados {len(worlds)} mundos en la interfaz")

	def _on_back_button(self, button):
		"""Maneja el botón de regreso."""
		from ui.navigation import get_navigation_manager

		nav_manager = get_navigation_manager()
		if nav_manager:
			nav_manager.navigate_to("main_menu")

	def on_enter(self):
		"""Se ejecuta cuando se entra a la pantalla."""
		# Actualizar estado de todas las tarjetas
		for child in self.worlds_grid.children:
			if isinstance(child, PremiumWorldCard):
				child._update_card_state()

		# Precargar assets del mundo activo
		game_state = get_game_state()
		if hasattr(game_state, "world_manager"):
			active_world = game_state.world_manager.get_active_world()
			if active_world:
				self.visual_manager.preload_world_assets(active_world.world_type.value)

		logger.info("Entrando a WorldSelectionScreen")

	def on_leave(self):
		"""Se ejecuta cuando se sale de la pantalla."""
		# Limpiar assets no utilizados
		self.visual_manager.cleanup_unused_assets()
		logger.info("Saliendo de WorldSelectionScreen")
