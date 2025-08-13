"""
Pantalla de inventario para el sistema de loot.
Proporciona interfaz visual para gestionar ítems, equipamiento y comparaciones.
"""


from kivy.graphics import Color, Rectangle
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput

from core.equipment_integration import EquipmentIntegration
from core.loot import LootItem, LootRarity, LootType


class InventoryItemWidget(BoxLayout):
	"""Widget individual para mostrar un ítem del inventario."""

	def __init__(self, item: LootItem, inventory_screen: "InventoryScreen", **kwargs):
		super().__init__(**kwargs)
		self.item = item
		self.inventory_screen = inventory_screen
		self.orientation = "horizontal"
		self.size_hint_y = None
		self.height = 80
		self.spacing = 10
		self.padding = [10, 5, 10, 5]

		# Color de fondo según rareza
		rarity_colors = {
			LootRarity.COMMON: (0.8, 0.8, 0.8, 0.3),
			LootRarity.RARE: (0.3, 0.8, 0.3, 0.3),
			LootRarity.EPIC: (0.8, 0.3, 0.8, 0.3),
			LootRarity.LEGENDARY: (1.0, 0.6, 0.0, 0.3),
		}

		with self.canvas.before:
			Color(*rarity_colors.get(item.rarity, (0.5, 0.5, 0.5, 0.3)))
			self.rect = Rectangle(pos=self.pos, size=self.size)

		self.bind(pos=self._update_rect, size=self._update_rect)

		# Información del ítem
		info_layout = BoxLayout(orientation="vertical", size_hint_x=0.7)

		name_label = Label(
			text=f"[b]{item.name}[/b]",
			markup=True,
			color=self._get_rarity_color(item.rarity),
			halign="left",
			valign="center",
			text_size=(None, None),
		)
		name_label.bind(size=name_label.setter("text_size"))

		stats_text = self._format_stats(item)
		stats_label = Label(
			text=stats_text, halign="left", valign="center", font_size=12, text_size=(None, None)
		)
		stats_label.bind(size=stats_label.setter("text_size"))

		info_layout.add_widget(name_label)
		info_layout.add_widget(stats_label)

		# Botones de acción
		button_layout = BoxLayout(orientation="vertical", size_hint_x=0.3, spacing=5)

		view_button = Button(text="Ver", size_hint_y=0.5, background_color=(0.3, 0.6, 1.0, 1.0))
		view_button.bind(on_press=self._on_view_item)

		equip_button = Button(
			text="Equipar",
			size_hint_y=0.5,
			background_color=(0.3, 1.0, 0.3, 1.0) if self._can_equip() else (0.5, 0.5, 0.5, 1.0),
		)
		equip_button.bind(on_press=self._on_equip_item)
		equip_button.disabled = not self._can_equip()

		button_layout.add_widget(view_button)
		button_layout.add_widget(equip_button)

		self.add_widget(info_layout)
		self.add_widget(button_layout)

	def _update_rect(self, instance, value):
		"""Actualiza el rectángulo de fondo."""
		self.rect.pos = instance.pos
		self.rect.size = instance.size

	def _get_rarity_color(self, rarity: LootRarity) -> tuple:
		"""Obtiene el color del texto según la rareza."""
		colors = {
			LootRarity.COMMON: (0.7, 0.7, 0.7, 1.0),
			LootRarity.RARE: (0.3, 1.0, 0.3, 1.0),
			LootRarity.EPIC: (1.0, 0.3, 1.0, 1.0),
			LootRarity.LEGENDARY: (1.0, 0.8, 0.0, 1.0),
		}
		return colors.get(rarity, (1.0, 1.0, 1.0, 1.0))

	def _format_stats(self, item: LootItem) -> str:
		"""Formatea las estadísticas del ítem para mostrar."""
		stats_parts = []

		# Mostrar tipo y rareza
		type_names = {
			LootType.WEAPON: "Arma",
			LootType.ARTIFACT: "Artefacto",
			LootType.GEM: "Gema",
			LootType.MATERIAL: "Material",
		}

		rarity_names = {
			LootRarity.COMMON: "Común",
			LootRarity.RARE: "Raro",
			LootRarity.EPIC: "Épico",
			LootRarity.LEGENDARY: "Legendario",
		}

		stats_parts.append(
			f"{type_names.get(item.loot_type, 'Desconocido')} {rarity_names.get(item.rarity, 'Común')}"
		)

		# Mostrar estadísticas principales
		if hasattr(item, "stats") and item.stats:
			main_stats = []
			for stat, value in item.stats.items():
				if value > 0:
					if stat == "damage_multiplier":
						main_stats.append(f"Daño: +{(value - 1) * 100:.0f}%")
					elif stat == "click_multiplier":
						main_stats.append(f"Click: +{(value - 1) * 100:.0f}%")
					elif stat == "gold_multiplier":
						main_stats.append(f"Oro: +{(value - 1) * 100:.0f}%")
					elif stat == "xp_multiplier":
						main_stats.append(f"XP: +{(value - 1) * 100:.0f}%")

			if main_stats:
				stats_parts.append(" | ".join(main_stats[:2]))  # Mostrar máximo 2 stats

		return " - ".join(stats_parts)

	def _can_equip(self) -> bool:
		"""Verifica si el ítem se puede equipar."""
		return self.item.loot_type in [LootType.WEAPON, LootType.ARTIFACT]

	def _on_view_item(self, button):
		"""Maneja el evento de ver detalles del ítem."""
		self.inventory_screen.show_item_details(self.item)

	def _on_equip_item(self, button):
		"""Maneja el evento de equipar el ítem."""
		if self._can_equip():
			self.inventory_screen.equip_item(self.item)


class ItemDetailsPopup(Popup):
	"""Popup para mostrar los detalles completos de un ítem."""

	def __init__(self, item: LootItem, inventory_screen: "InventoryScreen", **kwargs):
		super().__init__(**kwargs)
		self.item = item
		self.inventory_screen = inventory_screen
		self.title = f"Detalles: {item.name}"
		self.size_hint = (0.8, 0.8)

		main_layout = BoxLayout(orientation="vertical", spacing=10, padding=10)

		# Información básica
		info_layout = GridLayout(cols=2, size_hint_y=None, spacing=10)
		info_layout.bind(minimum_height=info_layout.setter("height"))

		# Tipo y rareza
		type_names = {
			LootType.WEAPON: "Arma",
			LootType.ARTIFACT: "Artefacto",
			LootType.GEM: "Gema",
			LootType.MATERIAL: "Material",
		}

		rarity_names = {
			LootRarity.COMMON: "Común",
			LootRarity.RARE: "Raro",
			LootRarity.EPIC: "Épico",
			LootRarity.LEGENDARY: "Legendario",
		}

		info_layout.add_widget(Label(text="Tipo:", halign="right", size_hint_y=None, height=30))
		info_layout.add_widget(
			Label(
				text=type_names.get(item.loot_type, "Desconocido"),
				halign="left",
				size_hint_y=None,
				height=30,
			)
		)

		info_layout.add_widget(Label(text="Rareza:", halign="right", size_hint_y=None, height=30))
		rarity_label = Label(
			text=rarity_names.get(item.rarity, "Común"), halign="left", size_hint_y=None, height=30
		)
		rarity_label.color = self._get_rarity_color(item.rarity)
		info_layout.add_widget(rarity_label)

		# Estadísticas detalladas
		if hasattr(item, "stats") and item.stats:
			info_layout.add_widget(
				Label(text="Estadísticas:", halign="right", size_hint_y=None, height=30)
			)
			stats_text = self._format_detailed_stats(item)
			info_layout.add_widget(
				Label(
					text=stats_text,
					halign="left",
					size_hint_y=None,
					height=60,
					text_size=(None, None),
				)
			)

		main_layout.add_widget(info_layout)

		# Comparación con equipado (si aplica)
		if item.loot_type in [LootType.WEAPON, LootType.ARTIFACT]:
			comparison_widget = self._create_comparison_widget(item)
			if comparison_widget:
				main_layout.add_widget(comparison_widget)

		# Botones de acción
		button_layout = BoxLayout(orientation="horizontal", size_hint_y=None, height=50, spacing=10)

		close_button = Button(text="Cerrar", background_color=(0.5, 0.5, 0.5, 1.0))
		close_button.bind(on_press=self.dismiss)

		if item.loot_type in [LootType.WEAPON, LootType.ARTIFACT]:
			equip_button = Button(text="Equipar", background_color=(0.3, 1.0, 0.3, 1.0))
			equip_button.bind(on_press=lambda x: self._equip_and_close())
			button_layout.add_widget(equip_button)

		button_layout.add_widget(close_button)

		main_layout.add_widget(button_layout)
		self.content = main_layout

	def _get_rarity_color(self, rarity: LootRarity) -> tuple:
		"""Obtiene el color según la rareza."""
		colors = {
			LootRarity.COMMON: (0.7, 0.7, 0.7, 1.0),
			LootRarity.RARE: (0.3, 1.0, 0.3, 1.0),
			LootRarity.EPIC: (1.0, 0.3, 1.0, 1.0),
			LootRarity.LEGENDARY: (1.0, 0.8, 0.0, 1.0),
		}
		return colors.get(rarity, (1.0, 1.0, 1.0, 1.0))

	def _format_detailed_stats(self, item: LootItem) -> str:
		"""Formatea todas las estadísticas del ítem."""
		if not hasattr(item, "stats") or not item.stats:
			return "Sin estadísticas"

		stat_lines = []
		stat_names = {
			"damage_multiplier": "Multiplicador de Daño",
			"click_multiplier": "Multiplicador de Click",
			"gold_multiplier": "Multiplicador de Oro",
			"xp_multiplier": "Multiplicador de XP",
		}

		for stat, value in item.stats.items():
			if value > 0:
				display_name = stat_names.get(stat, stat.replace("_", " ").title())
				if "multiplier" in stat:
					percentage = (value - 1) * 100
					stat_lines.append(f"{display_name}: +{percentage:.1f}%")
				else:
					stat_lines.append(f"{display_name}: {value}")

		return "\n".join(stat_lines) if stat_lines else "Sin estadísticas"

	def _create_comparison_widget(self, item: LootItem) -> BoxLayout | None:
		"""Crea widget de comparación con ítem equipado."""
		equipped_item = None

		# Obtener ítem equipado del mismo tipo
		equipment = self.inventory_screen.game_state.inventory.equipment
		if item.loot_type == LootType.WEAPON:
			equipped_item = equipment.weapon
		elif item.loot_type == LootType.ARTIFACT:
			equipped_item = equipment.artifact

		if not equipped_item:
			return None

		comparison_layout = BoxLayout(
			orientation="vertical", size_hint_y=None, height=120, spacing=5
		)

		title = Label(text="Comparación con equipado:", size_hint_y=None, height=25, halign="left")
		comparison_layout.add_widget(title)

		# Crear comparación de stats
		comparison_grid = GridLayout(cols=3, size_hint_y=None, height=90, spacing=5)

		comparison_grid.add_widget(Label(text="Estadística", size_hint_y=None, height=30))
		comparison_grid.add_widget(Label(text="Actual", size_hint_y=None, height=30))
		comparison_grid.add_widget(Label(text="Nuevo", size_hint_y=None, height=30))

		# Comparar estadísticas principales
		all_stats = set()
		if hasattr(equipped_item, "stats") and equipped_item.stats:
			all_stats.update(equipped_item.stats.keys())
		if hasattr(item, "stats") and item.stats:
			all_stats.update(item.stats.keys())

		for stat in sorted(all_stats):
			current_value = (
				equipped_item.stats.get(stat, 1.0) if hasattr(equipped_item, "stats") else 1.0
			)
			new_value = item.stats.get(stat, 1.0) if hasattr(item, "stats") else 1.0

			stat_name = stat.replace("_multiplier", "").replace("_", " ").title()
			comparison_grid.add_widget(Label(text=stat_name, size_hint_y=None, height=20))

			if "multiplier" in stat:
				current_text = f"+{(current_value - 1) * 100:.1f}%"
				new_text = f"+{(new_value - 1) * 100:.1f}%"
			else:
				current_text = str(current_value)
				new_text = str(new_value)

			comparison_grid.add_widget(Label(text=current_text, size_hint_y=None, height=20))

			# Color según si es mejor o peor
			color = (
				(0.3, 1.0, 0.3, 1.0)
				if new_value > current_value
				else (1.0, 0.3, 0.3, 1.0)
				if new_value < current_value
				else (1.0, 1.0, 1.0, 1.0)
			)
			new_label = Label(text=new_text, size_hint_y=None, height=20, color=color)
			comparison_grid.add_widget(new_label)

		comparison_layout.add_widget(comparison_grid)
		return comparison_layout

	def _equip_and_close(self):
		"""Equipa el ítem y cierra el popup."""
		self.inventory_screen.equip_item(self.item)
		self.dismiss()


class InventoryScreen(Screen):
	"""Pantalla principal del inventario."""

	def __init__(self, game_state, **kwargs):
		super().__init__(**kwargs)
		self.name = "inventory"
		self.game_state = game_state

		# Integración con equipamiento
		self.equipment_integration = EquipmentIntegration(self.game_state, self.game_state.inventory)

		# Filtros activos
		self.active_rarity_filter: LootRarity | None = None
		self.active_type_filter: LootType | None = None
		self.search_text: str = ""

		self._build_interface()
		self._update_display()

	def _build_interface(self):
		"""Construye la interfaz del inventario."""
		main_layout = BoxLayout(orientation="vertical", spacing=10, padding=10)

		# Título
		title = Label(
			text="[size=24][b]Inventario[/b][/size]", markup=True, size_hint_y=None, height=40
		)
		main_layout.add_widget(title)

		# Barra de filtros
		filter_layout = self._create_filter_bar()
		main_layout.add_widget(filter_layout)

		# Lista de ítems
		self.items_scroll = ScrollView()
		self.items_layout = BoxLayout(orientation="vertical", spacing=5, size_hint_y=None)
		self.items_layout.bind(minimum_height=self.items_layout.setter("height"))
		self.items_scroll.add_widget(self.items_layout)

		main_layout.add_widget(self.items_scroll)

		# Información del inventario
		info_layout = BoxLayout(orientation="horizontal", size_hint_y=None, height=30)
		self.inventory_info = Label(text="", halign="left")
		info_layout.add_widget(self.inventory_info)
		main_layout.add_widget(info_layout)

		self.add_widget(main_layout)

	def _create_filter_bar(self) -> BoxLayout:
		"""Crea la barra de filtros."""
		filter_layout = BoxLayout(orientation="vertical", size_hint_y=None, height=120, spacing=5)

		# Búsqueda por texto
		search_layout = BoxLayout(orientation="horizontal", size_hint_y=None, height=35, spacing=5)
		search_layout.add_widget(Label(text="Buscar:", size_hint_x=None, width=60))

		self.search_input = TextInput(multiline=False, size_hint_y=None, height=35)
		self.search_input.bind(text=self._on_search_text_change)
		search_layout.add_widget(self.search_input)

		clear_search_btn = Button(text="X", size_hint_x=None, width=35, size_hint_y=None, height=35)
		clear_search_btn.bind(on_press=self._clear_search)
		search_layout.add_widget(clear_search_btn)

		filter_layout.add_widget(search_layout)

		# Filtros por rareza
		rarity_layout = BoxLayout(orientation="horizontal", size_hint_y=None, height=40, spacing=5)
		rarity_layout.add_widget(Label(text="Rareza:", size_hint_x=None, width=60))

		all_rarity_btn = Button(text="Todos", background_color=(0.3, 0.6, 1.0, 1.0))
		all_rarity_btn.bind(on_press=lambda x: self._set_rarity_filter(None))
		rarity_layout.add_widget(all_rarity_btn)

		rarity_buttons = {
			LootRarity.COMMON: ("Común", (0.7, 0.7, 0.7, 1.0)),
			LootRarity.RARE: ("Raro", (0.3, 1.0, 0.3, 1.0)),
			LootRarity.EPIC: ("Épico", (1.0, 0.3, 1.0, 1.0)),
			LootRarity.LEGENDARY: ("Legendario", (1.0, 0.8, 0.0, 1.0)),
		}

		for rarity, (text, color) in rarity_buttons.items():
			btn = Button(text=text, background_color=color)
			btn.bind(on_press=lambda x, r=rarity: self._set_rarity_filter(r))
			rarity_layout.add_widget(btn)

		filter_layout.add_widget(rarity_layout)

		# Filtros por tipo
		type_layout = BoxLayout(orientation="horizontal", size_hint_y=None, height=40, spacing=5)
		type_layout.add_widget(Label(text="Tipo:", size_hint_x=None, width=60))

		all_type_btn = Button(text="Todos", background_color=(0.3, 0.6, 1.0, 1.0))
		all_type_btn.bind(on_press=lambda x: self._set_type_filter(None))
		type_layout.add_widget(all_type_btn)

		type_buttons = {
			LootType.WEAPON: "Armas",
			LootType.ARTIFACT: "Artefactos",
			LootType.GEM: "Gemas",
			LootType.MATERIAL: "Materiales",
		}

		for item_type, text in type_buttons.items():
			btn = Button(text=text, background_color=(0.6, 0.6, 0.6, 1.0))
			btn.bind(on_press=lambda x, t=item_type: self._set_type_filter(t))
			type_layout.add_widget(btn)

		filter_layout.add_widget(type_layout)

		return filter_layout

	def _on_search_text_change(self, instance, text):
		"""Maneja el cambio en el texto de búsqueda."""
		self.search_text = text.lower()
		self._update_display()

	def _clear_search(self, button):
		"""Limpia el texto de búsqueda."""
		self.search_input.text = ""
		self.search_text = ""
		self._update_display()

	def _set_rarity_filter(self, rarity: LootRarity | None):
		"""Establece el filtro por rareza."""
		self.active_rarity_filter = rarity
		self._update_display()

	def _set_type_filter(self, item_type: LootType | None):
		"""Establece el filtro por tipo."""
		self.active_type_filter = item_type
		self._update_display()

	def _update_display(self):
		"""Actualiza la visualización del inventario."""
		self.items_layout.clear_widgets()

		# Obtener ítems filtrados
		filtered_items = self._get_filtered_items()

		# Crear widgets para cada ítem
		for item in filtered_items:
			item_widget = InventoryItemWidget(item, self)
			self.items_layout.add_widget(item_widget)

		# Actualizar información del inventario
		total_items = len(self.game_state.inventory.items)
		displayed_items = len(filtered_items)
		max_slots = self.game_state.inventory.max_slots

		self.inventory_info.text = f"Mostrando {displayed_items} de {total_items} ítems ({max_slots - total_items} espacios libres)"

	def _get_filtered_items(self) -> list[LootItem]:
		"""Obtiene los ítems filtrados según los criterios activos."""
		items = list(self.game_state.inventory.items)

		# Filtro por rareza
		if self.active_rarity_filter is not None:
			items = [item for item in items if item.rarity == self.active_rarity_filter]

		# Filtro por tipo
		if self.active_type_filter is not None:
			items = [item for item in items if item.loot_type == self.active_type_filter]

		# Filtro por texto de búsqueda
		if self.search_text:
			items = [item for item in items if self.search_text in item.name.lower()]

		return items

	def show_item_details(self, item: LootItem):
		"""Muestra los detalles completos de un ítem."""
		popup = ItemDetailsPopup(item, self)
		popup.open()

	def equip_item(self, item: LootItem):
		"""Equipa un ítem."""
		if item.loot_type not in [LootType.WEAPON, LootType.ARTIFACT]:
			return

		# Equipar el ítem
		equipment = self.game_state.inventory.equipment
		if item.loot_type == LootType.WEAPON:
			equipment.weapon = item
		elif item.loot_type == LootType.ARTIFACT:
			equipment.artifact = item

		# Actualizar bonificaciones en el estado del juego
		integration = EquipmentIntegration(self.game_state)
		integration.update_equipment_bonuses()

		# Actualizar display
		self._update_display()

		print(f"Equipado: {item.name}")

	def on_enter(self):
		"""Se ejecuta al entrar en la pantalla."""
		self._update_display()
