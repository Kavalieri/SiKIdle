"""
Pantalla de Equipamiento para SiKIdle
Interfaz de usuario para gestionar equipamiento e inventario
"""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen
from kivy.clock import Clock
from kivy.app import App

from core.equipment import Equipment, EquipmentType, Rarity
from core.equipment_manager import EquipmentManager


class EquipmentSlot(Button):
	"""Widget que representa un slot de equipamiento."""

	def __init__(self, equipment_type: EquipmentType, **kwargs):
		super().__init__(**kwargs)
		self.equipment_type = equipment_type
		self.equipped_item: Equipment | None = None
		self.size_hint = (1, None)
		self.height = 80
		self.bind(on_press=self._on_slot_press)
		self._update_display()

	def set_equipment(self, equipment: Equipment | None):
		"""Establece el equipamiento en este slot."""
		self.equipped_item = equipment
		self._update_display()

	def _update_display(self):
		"""Actualiza la visualización del slot."""
		if self.equipped_item is None:
			self.text = f"[size=14][color=888888]{self._get_slot_name()}\n[Vacío][/color][/size]"
			self.background_color = (0.3, 0.3, 0.3, 1)
		else:
			rarity_colors = {
				Rarity.COMMON: "[color=ffffff]",
				Rarity.RARE: "[color=4488ff]",
				Rarity.EPIC: "[color=aa44ff]",
				Rarity.LEGENDARY: "[color=ffaa44]",
			}
			color = rarity_colors.get(self.equipped_item.rarity, "[color=ffffff]")

			self.text = (
				f"[size=12]{color}{self.equipped_item.name}[/color]\n"
				f"[size=10][color=cccccc]Nivel {self.equipped_item.level}[/color][/size]"
			)

			# Color de fondo según rareza
			bg_colors = {
				Rarity.COMMON: (0.4, 0.4, 0.4, 1),
				Rarity.RARE: (0.2, 0.3, 0.6, 1),
				Rarity.EPIC: (0.4, 0.2, 0.6, 1),
				Rarity.LEGENDARY: (0.6, 0.4, 0.2, 1),
			}
			self.background_color = bg_colors.get(self.equipped_item.rarity, (0.4, 0.4, 0.4, 1))

		self.markup = True

	def _get_slot_name(self) -> str:
		"""Obtiene el nombre del slot."""
		names = {
			EquipmentType.WEAPON: "⚔️ Arma",
			EquipmentType.ARMOR: "🛡️ Armadura",
			EquipmentType.JEWELRY: "💍 Joya",
		}
		return names.get(self.equipment_type, "Equipamiento")

	def _on_slot_press(self, instance):
		"""Maneja el clic en el slot."""
		app = App.get_running_app()
		if hasattr(app, "equipment_screen"):
			app.equipment_screen._show_slot_options(self)


class InventoryItem(Button):
	"""Widget que representa un ítem del inventario."""

	def __init__(self, equipment: Equipment, **kwargs):
		super().__init__(**kwargs)
		self.equipment = equipment
		self.size_hint = (1, None)
		self.height = 60
		self.bind(on_press=self._on_item_press)
		self._update_display()

	def _update_display(self):
		"""Actualiza la visualización del ítem."""
		rarity_colors = {
			Rarity.COMMON: "[color=ffffff]",
			Rarity.RARE: "[color=4488ff]",
			Rarity.EPIC: "[color=aa44ff]",
			Rarity.LEGENDARY: "[color=ffaa44]",
		}
		color = rarity_colors.get(self.equipment.rarity, "[color=ffffff]")

		power = self.equipment.stats.get_total_power()

		self.text = (
			f"[size=11]{color}{self.equipment.name}[/color]\n"
			f"[size=9][color=cccccc]Nivel {self.equipment.level} | Poder: {power:.0f}[/color][/size]"
		)

		# Color de fondo según rareza
		bg_colors = {
			Rarity.COMMON: (0.35, 0.35, 0.35, 1),
			Rarity.RARE: (0.15, 0.25, 0.5, 1),
			Rarity.EPIC: (0.3, 0.15, 0.5, 1),
			Rarity.LEGENDARY: (0.5, 0.3, 0.15, 1),
		}
		self.background_color = bg_colors.get(self.equipment.rarity, (0.35, 0.35, 0.35, 1))
		self.markup = True

	def _on_item_press(self, instance):
		"""Maneja el clic en el ítem."""
		app = App.get_running_app()
		if hasattr(app, "equipment_screen"):
			app.equipment_screen._show_item_options(self)


class EquipmentTooltip(Popup):
	"""Popup que muestra información detallada del equipamiento."""

	def __init__(self, equipment: Equipment, **kwargs):
		super().__init__(**kwargs)
		self.equipment = equipment
		self.title = equipment.get_display_name()
		self.size_hint = (0.8, 0.8)

		content = BoxLayout(orientation="vertical", spacing=10, padding=10)

		# Información del ítem
		info_label = Label(
			text=equipment.get_tooltip_text(),
			text_size=(None, None),
			halign="left",
			valign="top",
			markup=True,
		)
		content.add_widget(info_label)

		# Botón cerrar
		close_btn = Button(text="Cerrar", size_hint=(1, 0.2))
		close_btn.bind(on_press=self.dismiss)
		content.add_widget(close_btn)

		self.content = content


class EquipmentScreen(Screen):
	"""Pantalla principal del sistema de equipamiento."""

	def __init__(self, equipment_manager: EquipmentManager, **kwargs):
		super().__init__(**kwargs)
		self.equipment_manager = equipment_manager

		# Crear layout principal
		main_layout = BoxLayout(orientation="horizontal", spacing=10, padding=10)
		self.add_widget(main_layout)

		# Referencias a widgets
		self.equipment_slots = {}
		self.inventory_layout = None
		self.stats_label = None

		self._create_layout()
		self._schedule_updates()

	def _create_layout(self):
		"""Crea el layout principal."""
		# Obtener el layout principal
		main_layout = self.children[0]  # El BoxLayout que agregamos en __init__

		# Panel izquierdo - Equipamiento y estadísticas
		left_panel = BoxLayout(orientation="vertical", size_hint=(0.4, 1), spacing=10)

		# Título
		title_label = Label(
			text="[size=20][b]🎒 Equipamiento[/b][/size]",
			markup=True,
			size_hint=(1, 0.1),
			halign="center",
		)
		left_panel.add_widget(title_label)

		# Slots de equipamiento
		equipment_layout = BoxLayout(orientation="vertical", size_hint=(1, 0.5), spacing=5)

		for eq_type in EquipmentType:
			slot = EquipmentSlot(eq_type)
			self.equipment_slots[eq_type] = slot
			equipment_layout.add_widget(slot)

		left_panel.add_widget(equipment_layout)

		# Estadísticas del jugador
		self.stats_label = Label(
			text="Estadísticas...",
			text_size=(None, None),
			halign="left",
			valign="top",
			size_hint=(1, 0.4),
		)
		left_panel.add_widget(self.stats_label)

		main_layout.add_widget(left_panel)

		# Panel derecho - Inventario
		right_panel = BoxLayout(orientation="vertical", size_hint=(0.6, 1), spacing=10)

		# Título del inventario
		inv_title = Label(
			text="[size=18][b]📦 Inventario[/b][/size]",
			markup=True,
			size_hint=(1, 0.1),
			halign="center",
		)
		right_panel.add_widget(inv_title)

		# Controles del inventario
		controls_layout = BoxLayout(orientation="horizontal", size_hint=(1, 0.1), spacing=5)

		sort_buttons = [
			("Poder", "power"),
			("Rareza", "rarity"),
			("Nivel", "level"),
			("Tipo", "type"),
		]

		for btn_text, sort_key in sort_buttons:
			btn = Button(text=btn_text, size_hint=(0.25, 1))
			btn.bind(on_press=lambda x, key=sort_key: self._sort_inventory(key))
			controls_layout.add_widget(btn)

		right_panel.add_widget(controls_layout)

		# Lista del inventario
		scroll = ScrollView(size_hint=(1, 0.8))
		self.inventory_layout = GridLayout(cols=1, spacing=2, size_hint_y=None)
		self.inventory_layout.bind(minimum_height=self.inventory_layout.setter("height"))
		scroll.add_widget(self.inventory_layout)
		right_panel.add_widget(scroll)

		main_layout.add_widget(right_panel)

	def _schedule_updates(self):
		"""Programa las actualizaciones periódicas."""
		Clock.schedule_interval(self._update_display, 1.0)  # Actualizar cada segundo

	def _update_display(self, dt=None):
		"""Actualiza toda la interfaz."""
		self._update_equipment_slots()
		self._update_inventory()
		self._update_stats()

	def _update_equipment_slots(self):
		"""Actualiza los slots de equipamiento."""
		for eq_type, slot in self.equipment_slots.items():
			equipped_item = self.equipment_manager.equipped_items.get(eq_type)
			slot.set_equipment(equipped_item)

	def _update_inventory(self):
		"""Actualiza la lista del inventario."""
		self.inventory_layout.clear_widgets()

		for item in self.equipment_manager.inventory:
			item_widget = InventoryItem(item)
			self.inventory_layout.add_widget(item_widget)

		# Añadir info de espacio
		used_slots = len(self.equipment_manager.inventory)
		max_slots = self.equipment_manager.max_inventory_size

		info_label = Label(
			text=f"[size=12][color=888888]Espacio usado: {used_slots}/{max_slots}[/color][/size]",
			markup=True,
			size_hint=(1, None),
			height=30,
		)
		self.inventory_layout.add_widget(info_label)

	def _update_stats(self):
		"""Actualiza las estadísticas del jugador."""
		stats = self.equipment_manager.player_stats

		stats_text = (
			"[size=14][b]📊 Estadísticas[/b][/size]\n\n"
			f"⚔️ Ataque: [color=ff6666]{stats.get_total_attack():.1f}[/color]\n"
			f"🛡️ Defensa: [color=6666ff]{stats.get_total_defense():.1f}[/color]\n"
			f"❤️ Vida: [color=66ff66]{stats.get_total_health():.0f}[/color]\n"
			f"🍀 Crítico: [color=ffff66]{stats.get_total_critical_chance() * 100:.1f}%[/color]\n"
			f"💥 Daño Crítico: [color=ff66ff]{stats.get_total_critical_damage() * 100:.0f}%[/color]\n"
			f"📈 Bonus Producción: [color=66ffff]{stats.get_total_production_bonus() * 100:.1f}%[/color]\n\n"
			f"[size=12][color=888888]Poder equipado: {self.equipment_manager.get_equipped_value():.0f}[/color][/size]"
		)

		self.stats_label.text = stats_text
		self.stats_label.markup = True

	def _sort_inventory(self, sort_by: str):
		"""Ordena el inventario según el criterio especificado."""
		self.equipment_manager.sort_inventory(sort_by)
		self._update_inventory()

	def _show_slot_options(self, slot: EquipmentSlot):
		"""Muestra las opciones para un slot de equipamiento."""
		content = BoxLayout(orientation="vertical", spacing=10, padding=10)

		if slot.equipped_item is not None:
			# Mostrar información del ítem equipado
			info_btn = Button(text="Ver Información", size_hint=(1, 0.3))
			info_btn.bind(on_press=lambda x: self._show_equipment_info(slot.equipped_item))
			content.add_widget(info_btn)

			# Opción de desequipar
			unequip_btn = Button(text="Desequipar", size_hint=(1, 0.3))
			unequip_btn.bind(on_press=lambda x: self._unequip_item(slot.equipment_type))
			content.add_widget(unequip_btn)
		else:
			# Mostrar ítems equipables del inventario
			equipable_items = [
				item
				for item in self.equipment_manager.inventory
				if item.equipment_type == slot.equipment_type
			]

			if equipable_items:
				scroll = ScrollView(size_hint=(1, 0.8))
				items_layout = GridLayout(cols=1, spacing=5, size_hint_y=None)
				items_layout.bind(minimum_height=items_layout.setter("height"))

				for item in equipable_items[:5]:  # Mostrar solo los primeros 5
					btn = Button(
						text=f"{item.get_display_name()}\nPoder: {item.stats.get_total_power():.0f}",
						size_hint=(1, None),
						height=60,
						markup=True,
					)
					btn.bind(on_press=lambda x, it=item: self._equip_item_from_popup(it))
					items_layout.add_widget(btn)

				scroll.add_widget(items_layout)
				content.add_widget(scroll)
			else:
				no_items_label = Label(text="No hay ítems equipables de este tipo")
				content.add_widget(no_items_label)

		# Botón cerrar
		close_btn = Button(text="Cerrar", size_hint=(1, 0.2))

		popup = Popup(
			title=f"Opciones - {slot._get_slot_name()}", content=content, size_hint=(0.6, 0.7)
		)
		close_btn.bind(on_press=popup.dismiss)
		content.add_widget(close_btn)

		popup.open()

	def _show_item_options(self, item_widget: InventoryItem):
		"""Muestra las opciones para un ítem del inventario."""
		content = BoxLayout(orientation="vertical", spacing=10, padding=10)

		# Información del ítem
		info_btn = Button(text="Ver Información", size_hint=(1, 0.25))
		info_btn.bind(on_press=lambda x: self._show_equipment_info(item_widget.equipment))
		content.add_widget(info_btn)

		# Equipar ítem
		equip_btn = Button(text="Equipar", size_hint=(1, 0.25))
		equip_btn.bind(on_press=lambda x: self._equip_item_from_popup(item_widget.equipment))
		content.add_widget(equip_btn)

		# Eliminar ítem
		delete_btn = Button(text="Eliminar", size_hint=(1, 0.25))
		delete_btn.bind(on_press=lambda x: self._delete_item(item_widget.equipment))
		content.add_widget(delete_btn)

		# Botón cerrar
		close_btn = Button(text="Cerrar", size_hint=(1, 0.25))

		popup = Popup(
			title=item_widget.equipment.get_display_name(), content=content, size_hint=(0.5, 0.6)
		)
		close_btn.bind(on_press=popup.dismiss)
		content.add_widget(close_btn)

		popup.open()

	def _show_equipment_info(self, equipment: Equipment):
		"""Muestra información detallada del equipamiento."""
		tooltip = EquipmentTooltip(equipment)
		tooltip.open()

	def _equip_item_from_popup(self, equipment: Equipment):
		"""Equipa un ítem y cierra el popup."""
		self.equipment_manager.equip_item(equipment)
		# Cerrar cualquier popup abierto
		for child in self.get_root_window().children[:]:
			if isinstance(child, Popup):
				child.dismiss()

	def _unequip_item(self, equipment_type: EquipmentType):
		"""Desequipa un ítem."""
		self.equipment_manager.unequip_item(equipment_type)
		# Cerrar cualquier popup abierto
		for child in self.get_root_window().children[:]:
			if isinstance(child, Popup):
				child.dismiss()

	def _delete_item(self, equipment: Equipment):
		"""Elimina un ítem del inventario."""
		self.equipment_manager.remove_from_inventory(equipment)
		# Cerrar cualquier popup abierto
		for child in self.get_root_window().children[:]:
			if isinstance(child, Popup):
				child.dismiss()

	def add_generated_loot(self, loot: list[Equipment]):
		"""Añade loot generado al inventario."""
		added_items = []
		for item in loot:
			if self.equipment_manager.add_to_inventory(item):
				added_items.append(item)

				# Auto-equipar si es mejor
				if self.equipment_manager.auto_equip_if_better(item):
					continue  # Ya está equipado, no necesita estar en inventario

		# Mostrar notificación de loot si se añadieron ítems
		if added_items:
			self._show_loot_notification(added_items)

	def _show_loot_notification(self, items: list[Equipment]):
		"""Muestra una notificación de loot obtenido."""
		content = BoxLayout(orientation="vertical", spacing=10, padding=10)

		title_label = Label(
			text="[size=16][b]🎉 ¡Loot Obtenido![/b][/size]", markup=True, size_hint=(1, 0.2)
		)
		content.add_widget(title_label)

		scroll = ScrollView(size_hint=(1, 0.7))
		items_layout = GridLayout(cols=1, spacing=5, size_hint_y=None)
		items_layout.bind(minimum_height=items_layout.setter("height"))

		for item in items:
			item_label = Label(
				text=f"{item.get_display_name()}\nPoder: {item.stats.get_total_power():.0f}",
				markup=True,
				size_hint=(1, None),
				height=50,
			)
			items_layout.add_widget(item_label)

		scroll.add_widget(items_layout)
		content.add_widget(scroll)

		close_btn = Button(text="Continuar", size_hint=(1, 0.1))

		popup = Popup(
			title="Nuevos Ítems", content=content, size_hint=(0.6, 0.7), auto_dismiss=False
		)
		close_btn.bind(on_press=popup.dismiss)
		content.add_widget(close_btn)

		popup.open()

		# Auto-cerrar después de 3 segundos
		Clock.schedule_once(lambda dt: popup.dismiss(), 3.0)
