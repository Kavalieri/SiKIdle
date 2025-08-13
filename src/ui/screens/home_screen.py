"""
Pantalla principal de inicio/dashboard del juego SiKIdle.

Dashboard central con resumen de progreso, acciones rápidas y estado general.
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.progressbar import ProgressBar
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from kivy.animation import Animation

from typing import Dict, Any, Optional
import logging

# Import para edificios
try:
	from core.buildings import BuildingType
except ImportError:
	BuildingType = None


class StatsCard(BoxLayout):
	"""Tarjeta de estadística individual."""

	def __init__(self, title: str, value: str, icon: str = "📊", **kwargs):
		super().__init__(**kwargs)
		self.orientation = "vertical"
		self.size_hint_y = None
		self.height = 100
		self.spacing = 4
		self.padding = [8, 8, 8, 8]

		self._setup_styling()
		self._build_content(title, value, icon)

	def _setup_styling(self):
		"""Configura el estilo de la tarjeta."""
		from kivy.graphics import Color, RoundedRectangle

		with self.canvas.before:
			Color(0.25, 0.25, 0.30, 1)  # Fondo gris oscuro
			self.bg_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[8, 8, 8, 8])

		self.bind(pos=self._update_bg, size=self._update_bg)

	def _update_bg(self, *args):
		"""Actualiza el fondo de la tarjeta."""
		if hasattr(self, "bg_rect"):
			self.bg_rect.pos = self.pos
			self.bg_rect.size = self.size

	def _build_content(self, title: str, value: str, icon: str):
		"""Construye el contenido de la tarjeta."""
		# Icono
		icon_label = Label(text=icon, font_size="24sp", size_hint_y=None, height=32)

		# Valor principal
		self.value_label = Label(
			text=value, font_size="18sp", bold=True, size_hint_y=None, height=24
		)

		# Título
		title_label = Label(text=title, font_size="12sp", opacity=0.8, size_hint_y=None, height=16)

		self.add_widget(icon_label)
		self.add_widget(self.value_label)
		self.add_widget(title_label)

	def update_value(self, new_value: str):
		"""Actualiza el valor mostrado."""
		self.value_label.text = new_value

		# Animación de actualización
		anim = Animation(opacity=0.5, duration=0.1) + Animation(opacity=1.0, duration=0.1)
		anim.start(self.value_label)


class QuickActionButton(Button):
	"""Botón de acción rápida personalizado."""

	def __init__(self, title: str, icon: str = "⚡", action_callback=None, **kwargs):
		super().__init__(**kwargs)
		self.text = f"{icon}\n{title}"
		self.font_size = "12sp"
		self.size_hint_y = None
		self.height = 80
		self.halign = "center"
		self.valign = "center"

		if action_callback:
			self.bind(on_press=lambda x: action_callback())

		self._setup_styling()

	def _setup_styling(self):
		"""Configura el estilo del botón."""
		self.background_color = (0.20, 0.60, 0.86, 1)

		# Efecto hover (simulado con bind)
		self.bind(on_press=self._on_press_effect)

	def _on_press_effect(self, *args):
		"""Efecto visual al presionar."""
		anim = Animation(background_color=(0.15, 0.45, 0.65, 1), duration=0.1) + Animation(
			background_color=(0.20, 0.60, 0.86, 1), duration=0.1
		)
		anim.start(self)


class ProgressSection(BoxLayout):
	"""Sección de progreso con barras y objetivos."""

	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.orientation = "vertical"
		self.size_hint_y = None
		self.height = 200
		self.spacing = 8
		self.padding = [16, 16, 16, 16]

		self._build_progress_section()
		self._setup_styling()

	def _setup_styling(self):
		"""Configura el estilo de la sección."""
		from kivy.graphics import Color, RoundedRectangle

		with self.canvas.before:
			Color(0.20, 0.25, 0.30, 1)
			self.bg_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[12, 12, 12, 12])

		self.bind(pos=self._update_bg, size=self._update_bg)

	def _update_bg(self, *args):
		"""Actualiza el fondo de la sección."""
		if hasattr(self, "bg_rect"):
			self.bg_rect.pos = self.pos
			self.bg_rect.size = self.size

	def _build_progress_section(self):
		"""Construye la sección de progreso."""
		# Título
		title_label = Label(
			text="📈 Progreso Actual",
			font_size="16sp",
			bold=True,
			size_hint_y=None,
			height=30,
			halign="left",
		)
		title_label.bind(texture_size=title_label.setter("text_size"))

		# Progreso de nivel
		level_layout = self._create_progress_item("Nivel del Jugador", 75, "Nivel 5 → 6")

		# Progreso de mazmorra
		dungeon_layout = self._create_progress_item("Mazmorra Actual", 45, "Cueva Oscura - Piso 3")

		# Progreso de logros
		achievement_layout = self._create_progress_item("Logros Completados", 30, "4/13 logros")

		self.add_widget(title_label)
		self.add_widget(level_layout)
		self.add_widget(dungeon_layout)
		self.add_widget(achievement_layout)

	def _create_progress_item(self, title: str, progress: int, subtitle: str) -> BoxLayout:
		"""Crea un item de progreso individual."""
		container = BoxLayout(orientation="vertical", size_hint_y=None, height=50, spacing=4)

		# Encabezado con título y porcentaje
		header = BoxLayout(orientation="horizontal", size_hint_y=None, height=20)

		title_label = Label(text=title, font_size="14sp", halign="left", size_hint_x=0.7)
		title_label.bind(texture_size=title_label.setter("text_size"))

		progress_label = Label(
			text=f"{progress}%", font_size="14sp", bold=True, halign="right", size_hint_x=0.3
		)
		progress_label.bind(texture_size=progress_label.setter("text_size"))

		header.add_widget(title_label)
		header.add_widget(progress_label)

		# Barra de progreso
		progress_bar = ProgressBar(max=100, value=progress, size_hint_y=None, height=8)

		# Subtítulo
		subtitle_label = Label(
			text=subtitle, font_size="12sp", opacity=0.7, size_hint_y=None, height=16, halign="left"
		)
		subtitle_label.bind(texture_size=subtitle_label.setter("text_size"))

		container.add_widget(header)
		container.add_widget(progress_bar)
		container.add_widget(subtitle_label)

		return container


class HomeScreen(Screen):
	"""Pantalla principal de inicio/dashboard."""

	def __init__(self, name="home", **kwargs):
		super().__init__(name=name, **kwargs)

		# Conectar con GameState real
		from core.game import get_game_state

		try:
			self.real_game_state = get_game_state()
			self.real_game_state.start_game()
		except Exception as e:
			logging.error(f"Error connecting to GameState: {e}")
			self.real_game_state = None

		# Estado actual del juego (placeholder para compatibilidad)
		self.game_state = {
			"level": 5,
			"coins": 1234,
			"health": 85,
			"experience": 2340,
			"dungeons_cleared": 3,
			"enemies_defeated": 147,
		}

		self._build_layout()
		self._setup_auto_refresh()

		logging.info("HomeScreen initialized")

	def _build_layout(self):
		"""Construye el layout principal de la pantalla."""
		# Layout principal container
		main_container = BoxLayout(orientation="vertical")

		# Layout principal con scroll (sin header redundante)
		scroll = ScrollView()
		main_layout = BoxLayout(
			orientation="vertical", spacing=12, padding=[16, 16, 16, 16], size_hint_y=None
		)
		main_layout.bind(minimum_height=main_layout.setter("height"))

		# Botón principal de clic (prominente y central)
		click_section = self._create_click_section()

		# Sección de prestigio (si está disponible)
		prestige_section = self._create_prestige_section()

		# Lista de edificios (corazón del idle clicker)
		buildings_section = self._create_buildings_section()

		# Sección de hints de gameplay
		hints_section = self._create_hints_section()

		# Ensamblar layout scrollable
		main_layout.add_widget(click_section)
		if hints_section:  # Solo añadir si hay hints
			main_layout.add_widget(hints_section)
		if prestige_section:  # Solo añadir si está disponible
			main_layout.add_widget(prestige_section)
		main_layout.add_widget(buildings_section)

		scroll.add_widget(main_layout)
		main_container.add_widget(scroll)
		self.add_widget(main_container)

	def _create_click_section(self) -> BoxLayout:
		"""Crea la sección del botón principal de clic."""
		container = BoxLayout(
			orientation="vertical", size_hint_y=None, height=180, spacing=8, padding=[8, 8, 8, 8]
		)

		# Botón principal de clic (más grande y prominente)
		self.main_click_button = Button(
			text="💰\n¡CLIC PARA GANAR!",
			font_size="24sp",
			bold=True,
			size_hint_y=None,
			height=140,
			background_color=(0.2, 0.8, 0.2, 1),  # Verde
		)
		self.main_click_button.bind(on_press=self._on_main_click)

		# Información de ganancias
		self.click_info_label = Label(
			text="+1 moneda por clic",
			font_size="16sp",
			size_hint_y=None,
			height=24,
			halign="center",
			color=(0.8, 0.8, 0.8, 1),
		)
		self.click_info_label.bind(texture_size=self.click_info_label.setter("text_size"))

		container.add_widget(self.main_click_button)
		container.add_widget(self.click_info_label)

		return container

	def _create_prestige_section(self) -> BoxLayout:
		"""Crea la sección de prestigio si está disponible."""
		if not self.real_game_state or not hasattr(self.real_game_state, "prestige_manager"):
			return None

		# Verificar si el prestigio está disponible
		total_coins = self.real_game_state.lifetime_coins + self.real_game_state.coins
		can_prestige = self.real_game_state.prestige_manager.can_prestige(total_coins)

		# Solo mostrar si está cerca del prestigio (75% del requisito) o ya puede
		min_for_display = 75000  # 75K monedas para mostrar la sección
		if total_coins < min_for_display:
			return None

		container = BoxLayout(
			orientation="vertical", size_hint_y=None, height=120, spacing=8, padding=[8, 8, 8, 8]
		)

		# Título
		title = Label(
			text="💎 Sistema de Prestigio",
			font_size="18sp",
			bold=True,
			size_hint_y=None,
			height=30,
			halign="center",
		)
		title.bind(texture_size=title.setter("text_size"))

		# Información y botón
		info_layout = BoxLayout(orientation="horizontal", size_hint_y=None, height=60, spacing=8)

		# Información del prestigio
		preview = self.real_game_state.prestige_manager.get_prestige_preview(total_coins)
		stats = self.real_game_state.prestige_manager.get_stats()

		if can_prestige:
			info_text = f"💎 Cristales actuales: {stats['prestige_crystals']}\n✨ Ganarás: {preview['crystals_gained']} cristales"
			button_text = "🔄 HACER PRESTIGIO"
			button_color = (0.8, 0.2, 0.8, 1)  # Morado
		else:
			needed = 100000 - total_coins
			info_text = f"💎 Cristales actuales: {stats['prestige_crystals']}\n⏳ Necesitas: {needed:,.0f} monedas más"
			button_text = "🔍 VER PRESTIGIO"
			button_color = (0.6, 0.4, 0.8, 1)  # Morado claro

		self.prestige_info_label = Label(
			text=info_text, font_size="14sp", size_hint_x=0.65, halign="left", valign="center"
		)
		self.prestige_info_label.bind(texture_size=self.prestige_info_label.setter("text_size"))

		# Botón de prestigio
		self.prestige_button = Button(
			text=button_text,
			font_size="16sp",
			bold=True,
			size_hint_x=0.35,
			background_color=button_color,
		)
		self.prestige_button.bind(on_press=self._on_prestige_button)

		info_layout.add_widget(self.prestige_info_label)
		info_layout.add_widget(self.prestige_button)

		container.add_widget(title)
		container.add_widget(info_layout)

		return container

	def _create_hints_section(self) -> Optional[BoxLayout]:
		"""Crea la sección de hints de gameplay si está disponible."""
		if not self.real_game_state or not hasattr(self.real_game_state, "gameplay_flow"):
			return None

		# Obtener hints actuales
		hints = self.real_game_state.gameplay_flow.get_current_hints()
		if not hints:
			return None

		# Mostrar solo el hint más importante
		hint = min(hints, key=lambda h: h.priority)

		container = BoxLayout(
			orientation="horizontal", size_hint_y=None, height=80, spacing=8, padding=[8, 8, 8, 8]
		)

		# Icono según prioridad
		priority_icons = {1: "💡", 2: "🎯", 3: "📝"}
		icon = priority_icons.get(hint.priority, "📝")

		# Información del hint
		self.hint_info_label = Label(
			text=f"{icon} {hint.title}\n{hint.message}",
			font_size="14sp",
			size_hint_x=0.75,
			halign="left",
			valign="center",
			color=(0.9, 0.9, 0.6, 1),  # Amarillo claro
		)
		self.hint_info_label.bind(texture_size=self.hint_info_label.setter("text_size"))

		# Botón de cerrar hint
		close_button = Button(
			text="✖", font_size="16sp", size_hint_x=0.25, background_color=(0.6, 0.3, 0.3, 1)
		)
		close_button.bind(on_press=lambda x: self._close_hint(hint.title))

		container.add_widget(self.hint_info_label)
		container.add_widget(close_button)

		# Guardar referencia para actualización
		self.current_hint = hint

		return container

	def _close_hint(self, hint_title: str):
		"""Cierra un hint y lo marca como mostrado."""
		if self.real_game_state and hasattr(self.real_game_state, "gameplay_flow"):
			self.real_game_state.gameplay_flow.mark_hint_shown(hint_title)
			logging.info(f"Hint closed: {hint_title}")

	def _create_buildings_section(self) -> BoxLayout:
		"""Crea la sección de edificios generadores."""
		container = BoxLayout(
			orientation="vertical", size_hint_y=None, height=400, spacing=8, padding=[8, 8, 8, 8]
		)

		# Título
		title = Label(
			text="🏭 Generadores Automáticos",
			font_size="18sp",
			bold=True,
			size_hint_y=None,
			height=30,
			halign="center",
		)
		title.bind(texture_size=title.setter("text_size"))

		# Lista de edificios
		buildings_layout = BoxLayout(
			orientation="vertical", spacing=4, size_hint_y=None, height=360
		)

		# Obtener edificios reales del BuildingManager
		if self.real_game_state and hasattr(self.real_game_state, "building_manager"):
			building_manager = self.real_game_state.building_manager
			unlocked_buildings = building_manager.get_unlocked_buildings(
				self.real_game_state.player_level
			)

			# Mostrar solo los primeros 4 edificios para la UI inicial
			from core.buildings import BuildingType

			main_buildings = [
				BuildingType.FARM,
				BuildingType.FACTORY,
				BuildingType.BANK,
				BuildingType.MINE,
			]

			self.building_widgets = {}
			for building_type in main_buildings:
				if building_type in unlocked_buildings:
					building_widget = self._create_building_widget(building_type)
					self.building_widgets[building_type] = building_widget
					buildings_layout.add_widget(building_widget)
		else:
			# Fallback si no hay BuildingManager
			placeholder_label = Label(
				text="Edificios no disponibles\n(BuildingManager no conectado)",
				font_size="14sp",
				color=(0.8, 0.4, 0.4, 1),
			)
			buildings_layout.add_widget(placeholder_label)

		container.add_widget(title)
		container.add_widget(buildings_layout)

		return container

	def _create_building_widget(self, building_type):
		"""Crea un widget individual para un edificio real."""
		if not self.real_game_state or not hasattr(self.real_game_state, "building_manager"):
			return Label(text="Error: BuildingManager no disponible")

		building_manager = self.real_game_state.building_manager
		building = building_manager.get_building(building_type)
		info = building_manager.get_building_info(building_type)

		widget = BoxLayout(
			orientation="horizontal", size_hint_y=None, height=80, spacing=8, padding=[8, 4, 8, 4]
		)

		# Información del edificio
		info_layout = BoxLayout(orientation="vertical", size_hint_x=0.7)

		# Nombre con cantidad actual
		name_label = Label(
			text=f"{info.emoji} {info.name} ({building.count})",
			font_size="16sp",
			bold=True,
			size_hint_y=0.5,
			halign="left",
			valign="center",
		)
		name_label.bind(texture_size=name_label.setter("text_size"))

		# Descripción con producción actual
		production_per_sec = building.get_total_production_per_second(info)
		desc_text = f"{info.description} | {production_per_sec:.1f}/seg"
		desc_label = Label(
			text=desc_text,
			font_size="12sp",
			color=(0.7, 0.7, 0.7, 1),
			size_hint_y=0.5,
			halign="left",
			valign="center",
		)
		desc_label.bind(texture_size=desc_label.setter("text_size"))

		info_layout.add_widget(name_label)
		info_layout.add_widget(desc_label)

		# Botón de compra funcional
		current_cost = building.get_current_cost(info)
		buy_button = Button(text=f"💰 {current_cost:,}", font_size="14sp", size_hint_x=0.3)

		# Verificar si se puede permitir
		can_afford = building.can_afford(info, building_manager.resource_manager)
		buy_button.background_color = (0.2, 0.8, 0.2, 1) if can_afford else (0.6, 0.3, 0.3, 1)
		buy_button.disabled = not can_afford

		# Conectar funcionalidad de compra
		buy_button.bind(on_press=lambda x: self._purchase_building(building_type))

		widget.add_widget(info_layout)
		widget.add_widget(buy_button)

		# Guardar referencias para actualización
		widget.name_label = name_label
		widget.desc_label = desc_label
		widget.buy_button = buy_button
		widget.building_type = building_type

		return widget

	def _setup_auto_refresh(self):
		"""Configura el auto-refresh de datos (optimizado)."""
		# Usar intervalos inteligentes para mejor performance
		Clock.schedule_interval(self._refresh_data_optimized, 0.1)  # 10 FPS para chequeos

		# La producción se maneja en GameState, no duplicar aquí

	def _collect_building_production(self, dt):
		"""Recolecta la producción automática de edificios."""
		if self.real_game_state and hasattr(self.real_game_state, "building_manager"):
			production = self.real_game_state.building_manager.collect_all_production()
			if production:
				# Log detallado de producción por edificio
				total_coins = production.get("coins", 0)
				if total_coins > 0.1:
					# Obtener info detallada de cada edificio
					buildings = self.real_game_state.building_manager.buildings
					building_details = []
					for building_type, building in buildings.items():
						if building.count > 0:
							individual_production = building.building_info.base_production
							total_building_production = individual_production * building.count
							building_details.append(
								f"{building_type.value}({building.count}): {total_building_production:.2f}/s"
							)

					buildings_str = " | ".join(building_details) if building_details else "Ninguno"
					logging.debug(
						f"🏭 Producción automática: +{total_coins:.2f} monedas/s [{buildings_str}]"
					)

	def _on_main_click(self, button):
		"""Maneja el clic en el botón principal."""
		if self.real_game_state:
			# Usar GameState real
			coins_earned = self.real_game_state.click()
			logging.info(f"Click! Earned {coins_earned} coins")

			# Efecto visual
			self._show_click_effect(coins_earned)

			# Forzar actualización inmediata del header
			self._force_header_update()
		else:
			# Fallback: simular clic
			self.game_state["coins"] += 1
			logging.info("Click! (simulated) Earned 1 coin")
			self._show_click_effect(1)

	def _show_click_effect(self, coins_earned):
		"""Muestra efecto visual del clic."""
		# Animación del botón
		original_color = self.main_click_button.background_color
		self.main_click_button.background_color = (0.3, 1.0, 0.3, 1)  # Verde más brillante

		# Actualizar texto temporalmente
		original_text = self.main_click_button.text
		self.main_click_button.text = f"💰\n+{coins_earned} MONEDAS!"

		def restore_button(dt):
			self.main_click_button.background_color = original_color
			self.main_click_button.text = original_text

		Clock.schedule_once(restore_button, 0.3)

	def _refresh_data_optimized(self, dt):
		"""Refresca los datos con optimizaciones de performance."""
		if not self.real_game_state:
			return

		# Obtener optimizador de performance
		performance_optimizer = getattr(self.real_game_state, "performance_optimizer", None)
		if not performance_optimizer:
			# Fallback al método original
			self._refresh_data(dt)
			return

		# Actualizar información de clic (prioridad alta)
		if performance_optimizer.should_update_ui("high"):
			if hasattr(self, "click_info_label"):
				multiplier = self.real_game_state.get_current_multiplier()
				base_coins = int(1 * multiplier)
				self.click_info_label.text = f"+{base_coins:,} monedas por clic"

		# Actualizar edificios (prioridad media)
		if performance_optimizer.should_update_ui("medium"):
			self._update_building_widgets()

		# Actualizar sección de prestigio (prioridad baja)
		if performance_optimizer.should_update_ui("low"):
			self._update_prestige_section()

		# Actualizar hints de gameplay (prioridad baja)
		if performance_optimizer.should_update_ui("background"):
			self._update_hints_section()

		# Actualizar información de combat boosts (prioridad baja)
		if performance_optimizer.should_update_ui("low"):
			self._update_combat_info()

	def _refresh_data(self, dt):
		"""Refresca los datos mostrados (método original como fallback)."""
		if self.real_game_state:
			# Actualizar información de clic
			if hasattr(self, "click_info_label"):
				multiplier = self.real_game_state.get_current_multiplier()
				base_coins = int(1 * multiplier)
				self.click_info_label.text = f"+{base_coins:,} monedas por clic"

			# Actualizar edificios reales
			self._update_building_widgets()

			# Actualizar sección de prestigio si existe
			self._update_prestige_section()

	def _update_building_widgets(self):
		"""Actualiza los widgets de edificios con datos actuales."""
		if not self.real_game_state or not hasattr(self.real_game_state, "building_manager"):
			return

		building_manager = self.real_game_state.building_manager

		for building_type, widget in getattr(self, "building_widgets", {}).items():
			building = building_manager.get_building(building_type)
			info = building_manager.get_building_info(building_type)

			# Actualizar nombre con cantidad
			widget.name_label.text = f"{info.emoji} {info.name} ({building.count})"

			# Actualizar descripción con producción
			production_per_sec = building.get_total_production_per_second(info)
			widget.desc_label.text = f"{info.description} | {production_per_sec:.1f}/seg"

			# Actualizar botón de compra
			current_cost = building.get_current_cost(info)
			widget.buy_button.text = f"💰 {current_cost:,}"

			# Actualizar estado del botón
			can_afford = building.can_afford(info, building_manager.resource_manager)
			widget.buy_button.background_color = (
				(0.2, 0.8, 0.2, 1) if can_afford else (0.6, 0.3, 0.3, 1)
			)
			widget.buy_button.disabled = not can_afford

	def _purchase_building(self, building_type):
		"""Maneja la compra de un edificio."""
		if not self.real_game_state or not hasattr(self.real_game_state, "building_manager"):
			return

		building_manager = self.real_game_state.building_manager
		success = building_manager.purchase_building(building_type, self.real_game_state)

		if success:
			info = building_manager.get_building_info(building_type)
			logging.info(f"Edificio {info.name} comprado exitosamente!")

			# Actualizar UI inmediatamente
			self._update_building_widgets()

			# Forzar actualización inmediata del header global
			self._force_header_update()

			# Efecto visual de compra exitosa
			self._show_purchase_effect(building_type)
		else:
			logging.warning(f"No se pudo comprar edificio {building_type}")

	def _force_header_update(self):
		"""Fuerza una actualización inmediata del header global."""
		try:
			from kivy.app import App

			app = App.get_running_app()
			if hasattr(app, "root") and hasattr(app.root, "header"):
				# Llamar directamente al método de actualización del header
				app.root.header._update_resources(0)
		except Exception as e:
			pass  # Silenciar errores si no se puede acceder al header

	def _show_purchase_effect(self, building_type):
		"""Muestra efecto visual de compra exitosa."""
		if building_type in getattr(self, "building_widgets", {}):
			widget = self.building_widgets[building_type]

			# Animación del botón
			original_color = widget.buy_button.background_color
			widget.buy_button.background_color = (0.3, 1.0, 0.3, 1)  # Verde brillante

			def restore_color(dt):
				widget.buy_button.background_color = original_color

			Clock.schedule_once(restore_color, 0.3)

	def _on_prestige_button(self, button):
		"""Maneja el clic en el botón de prestigio."""
		try:
			# Navegar a la pantalla de prestigio
			from kivy.app import App

			app = App.get_running_app()
			if hasattr(app, "navigate_to"):
				app.navigate_to("prestige")
			else:
				logging.warning("No se pudo navegar a la pantalla de prestigio")
		except Exception as e:
			logging.error(f"Error navegando a prestigio: {e}")

	def _update_prestige_section(self):
		"""Actualiza la información de la sección de prestigio."""
		if not hasattr(self, "prestige_info_label") or not hasattr(self, "prestige_button"):
			return

		if not self.real_game_state or not hasattr(self.real_game_state, "prestige_manager"):
			return

		total_coins = self.real_game_state.lifetime_coins + self.real_game_state.coins
		can_prestige = self.real_game_state.prestige_manager.can_prestige(total_coins)
		preview = self.real_game_state.prestige_manager.get_prestige_preview(total_coins)
		stats = self.real_game_state.prestige_manager.get_stats()

		if can_prestige:
			info_text = f"💎 Cristales actuales: {stats['prestige_crystals']}\n✨ Ganarás: {preview['crystals_gained']} cristales"
			button_text = "🔄 HACER PRESTIGIO"
			button_color = (0.8, 0.2, 0.8, 1)  # Morado
		else:
			needed = 100000 - total_coins
			info_text = f"💎 Cristales actuales: {stats['prestige_crystals']}\n⏳ Necesitas: {needed:,.0f} monedas más"
			button_text = "🔍 VER PRESTIGIO"
			button_color = (0.6, 0.4, 0.8, 1)  # Morado claro

		self.prestige_info_label.text = info_text
		self.prestige_button.text = button_text
		self.prestige_button.background_color = button_color

	def _update_hints_section(self):
		"""Actualiza la sección de hints de gameplay."""
		if not hasattr(self, "hint_info_label") or not hasattr(self, "current_hint"):
			return

		if not self.real_game_state or not hasattr(self.real_game_state, "gameplay_flow"):
			return

		# Verificar si hay nuevos hints
		hints = self.real_game_state.gameplay_flow.get_current_hints()
		if not hints:
			# No hay hints, ocultar sección si existe
			if hasattr(self, "hint_info_label"):
				self.hint_info_label.parent.remove_widget(self.hint_info_label.parent)
			return

		# Obtener hint más importante
		new_hint = min(hints, key=lambda h: h.priority)

		# Actualizar solo si es diferente
		if new_hint.title != self.current_hint.title:
			priority_icons = {1: "💡", 2: "🎯", 3: "📝"}
			icon = priority_icons.get(new_hint.priority, "📝")

			self.hint_info_label.text = f"{icon} {new_hint.title}\n{new_hint.message}"
			self.current_hint = new_hint

	def _update_combat_info(self):
		"""Actualiza información de combat boosts si están activos."""
		if not self.real_game_state or not hasattr(self.real_game_state, "combat_idle_integration"):
			return

		# Obtener multiplicadores activos de combat
		combat_multipliers = self.real_game_state.combat_idle_integration.get_active_multipliers()

		# Actualizar información de clic si hay boost activo
		if hasattr(self, "click_info_label") and combat_multipliers["click_multiplier"] > 1.0:
			multiplier = self.real_game_state.get_current_multiplier()
			base_coins = int(1 * multiplier)
			combat_bonus = combat_multipliers["click_multiplier"]
			self.click_info_label.text = f"+{base_coins:,} monedas por clic ⚔️ x{combat_bonus:.1f}"
			self.click_info_label.color = (0.8, 0.6, 1.0, 1)  # Morado para indicar boost

	def on_enter(self):
		"""Callback ejecutado cuando se entra en la pantalla."""
		logging.info("Entered HomeScreen")
		self._refresh_data(None)

	def on_leave(self):
		"""Callback ejecutado cuando se sale de la pantalla."""
		logging.info("Left HomeScreen")
