"""
Pantalla de gestión de mejoras para el juego SiKIdle.

Esta pantalla permite a los jugadores:
- Ver todas las mejoras disponibles organizadas por categoría
- Comprar mejoras permanentes para incrementar eficiencia
- Ver efectos acumulados de las mejoras
- Gestionar el progreso de especialización
"""

import logging
from typing import Any
from kivy.uix.gridlayout import GridLayout  # type: ignore
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem  # type: ignore
from kivy.clock import Clock  # type: ignore
from kivy.uix.boxlayout import BoxLayout  # type: ignore
from kivy.uix.label import Label  # type: ignore
from kivy.uix.button import Button  # type: ignore
from kivy.uix.scrollview import ScrollView  # type: ignore

from core.game import get_game_state, GameState
from core.upgrades import UpgradeType, UpgradeCategory, UpgradeInfo
from ui.screen_manager import SiKIdleScreen


class UpgradeButton(Button):
	"""Botón personalizado para representar una mejora."""
	
	def __init__(self, upgrade_type: UpgradeType, upgrade_info: UpgradeInfo, game_state: GameState, **kwargs: Any):
		super().__init__(**kwargs)
		self.upgrade_type = upgrade_type
		self.upgrade_info = upgrade_info
		self.game_state = game_state
		self.update_display()
		
	def update_display(self):
		"""Actualiza la información mostrada de la mejora."""
		upgrade = self.game_state.upgrade_manager.get_upgrade(self.upgrade_type)
		cost = upgrade.get_current_cost(self.upgrade_info)
		
		# Verificar si se puede permitir
		can_afford = True
		if cost != float('inf'):
			if self.game_state.resource_manager.get_resource(self.upgrade_info.cost_resource) < cost:
				can_afford = False
		else:
			can_afford = False
		
		# Configurar texto del botón
		if cost == float('inf'):
			cost_text = "MAX"
		else:
			cost_text = f"{cost:,.0f}"
		
		total_effect = upgrade.get_total_effect(self.upgrade_info)
		effect_text = f"+{total_effect * 100:.1f}%" if self.upgrade_info.upgrade_type.value.endswith(('income', 'chance', 'reduction')) else f"+{total_effect:.1f}x"
		
		self.text = (f"{self.upgrade_info.emoji} {self.upgrade_info.name}\n"
					f"Nivel: {upgrade.level}/{self.upgrade_info.max_level if self.upgrade_info.max_level > 0 else '∞'}\n"
					f"Efecto: {effect_text}\n"
					f"Costo: {cost_text}")
		
		# Configurar colores
		if can_afford and cost != float('inf'):
			self.background_color = [0.2, 0.8, 0.2, 1]  # Verde si se puede permitir
		elif cost == float('inf'):
			self.background_color = [0.8, 0.8, 0.2, 1]  # Amarillo si está al máximo
		else:
			self.background_color = [0.8, 0.2, 0.2, 1]  # Rojo si no se puede permitir
			
		# Desactivar si no se puede permitir
		self.disabled = not can_afford or cost == float('inf')


class UpgradesScreen(SiKIdleScreen):
	"""Pantalla principal de gestión de mejoras."""
	
	def __init__(self, **kwargs: Any):
		super().__init__(**kwargs)
		self.game_state = get_game_state()
		self.upgrade_buttons: dict[UpgradeType, UpgradeButton] = {}
		self.stats_labels: dict[str, Label] = {}
		self.update_event = None
		
		self.build_ui()
		
	def build_ui(self):
		"""Construye la interfaz de usuario de la pantalla de mejoras."""
		# Layout principal
		main_layout = BoxLayout(orientation='vertical', padding=[10, 10, 10, 10], spacing=10)
		
		# Header con título y botón de cerrar
		header_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=60)
		
		title_label = Label(
			text="🏗️ GESTIÓN PRINCIPAL",
			font_size='24sp',
			bold=True,
			size_hint_x=0.8,
			color=[1, 1, 1, 1]
		)
		
		close_button = Button(
			text="❌ Cerrar",
			size_hint_x=0.2,
			background_color=[0.8, 0.2, 0.2, 1]
		)
		close_button.bind(on_press=self.on_close_button)
		
		header_layout.add_widget(title_label)
		header_layout.add_widget(close_button)
		
		# Panel de estadísticas globales
		stats_layout = BoxLayout(
			orientation='horizontal',
			size_hint_y=None,
			height=60,
			spacing=10
		)
		
		self.stats_labels['click_multiplier'] = Label(
			text="Multiplicador Clic: 1.0x",
			size_hint_x=0.33
		)
		self.stats_labels['building_multiplier'] = Label(
			text="Multiplicador Edificios: 1.0x",
			size_hint_x=0.33
		)
		self.stats_labels['total_spent'] = Label(
			text="💰 Gastado: 0",
			size_hint_x=0.34
		)
		
		for label in self.stats_labels.values():
			stats_layout.add_widget(label)
		
		# Crear panel con pestañas para categorías + edificios
		tab_panel = TabbedPanel(do_default_tab=False, tab_width=120)
		
		# Pestaña de edificios (primera pestaña)
		buildings_tab = TabbedPanelItem(text="🏗️ Edificios")
		buildings_content = self._create_buildings_content()
		buildings_tab.add_widget(buildings_content)
		tab_panel.add_widget(buildings_tab)
		
		# Crear pestañas para cada categoría de mejoras
		for category in UpgradeCategory:
			tab_item = TabbedPanelItem(text=self._get_category_display_name(category))
			tab_content = self._create_category_content(category)
			tab_item.add_widget(tab_content)
			tab_panel.add_widget(tab_item)
		
		# Ensamblar layout principal
		main_layout.add_widget(header_layout)
		main_layout.add_widget(stats_layout)
		main_layout.add_widget(tab_panel)
		
		self.add_widget(main_layout)
	
	def _create_buildings_content(self):
		"""Crea el contenido para la pestaña de edificios."""
		# Crear scroll view para los edificios
		scroll = ScrollView()
		buildings_layout = GridLayout(
			cols=1,
			spacing=10,
			size_hint_y=None,
			padding=[10, 10, 10, 10]
		)
		buildings_layout.bind(minimum_height=buildings_layout.setter('height'))
		
		# Obtener edificios disponibles
		from core.buildings import BuildingType
		for building_type in BuildingType:
			building_info = self.game_state.building_manager.get_building_info(building_type)
			building = self.game_state.building_manager.get_building(building_type)
			
			# Crear widget para el edificio
			building_widget = self._create_building_widget(building_type, building_info, building)
			buildings_layout.add_widget(building_widget)
		
		scroll.add_widget(buildings_layout)
		return scroll
	
	def _create_building_widget(self, building_type, building_info, building):
		"""Crea el widget para un edificio individual."""
		# Widget principal del edificio
		widget = BoxLayout(
			orientation='horizontal',
			size_hint_y=None,
			height=100,
			spacing=10,
			padding=[5, 5, 5, 5]
		)
		
		# Información del edificio (lado izquierdo)
		info_layout = BoxLayout(
			orientation='vertical',
			size_hint_x=0.7
		)
		
		# Nombre y cantidad
		name_label = Label(
			text=f"{building_info.emoji} {building_info.name} ({building.count})",
			font_size='18sp',
			bold=True,
			size_hint_y=0.4,
			halign='left',
			valign='center'
		)
		name_label.text_size = (None, None)
		info_layout.add_widget(name_label)
		
		# Descripción
		desc_label = Label(
			text=building_info.description,
			font_size='14sp',
			color=[0.7, 0.7, 0.7, 1],
			size_hint_y=0.3,
			halign='left',
			valign='center'
		)
		desc_label.text_size = (None, None)
		info_layout.add_widget(desc_label)
		
		# Producción
		production_label = Label(
			text=f"Produce: {building_info.base_production} monedas/seg",
			font_size='14sp',
			color=[0.6, 1, 0.6, 1],
			size_hint_y=0.3,
			halign='left',
			valign='center'
		)
		production_label.text_size = (None, None)
		info_layout.add_widget(production_label)
		
		widget.add_widget(info_layout)
		
		# Botón de compra (lado derecho)
		cost = building.get_current_cost(building_info)
		can_afford = self.game_state.resource_manager.get_resource(building_info.cost_resource) >= cost
		
		buy_button = Button(
			text=f"💰 {cost:,.0f}\nComprar",
			font_size='16sp',
			size_hint_x=0.3,
			background_color=[0.2, 0.8, 0.2, 1] if can_afford else [0.8, 0.2, 0.2, 1]
		)
		buy_button.disabled = not can_afford
		buy_button.bind(on_press=lambda x: self.on_building_button(building_type))
		
		widget.add_widget(buy_button)
		
		return widget
	
	def on_building_button(self, building_type):
		"""Maneja el clic en un botón de edificio para comprarlo."""
		try:
			success = self.game_state.building_manager.purchase_building(building_type, self.game_state)
			if success:
				logging.info(f"Edificio {building_type} comprado exitosamente")
				self.update_ui()
			else:
				logging.warning(f"No se pudo comprar edificio {building_type}")
		except Exception as e:
			logging.error(f"Error comprando edificio: {e}")
	
	def _get_category_display_name(self, category: UpgradeCategory) -> str:
		"""Obtiene el nombre para mostrar de una categoría."""
		names = {
			UpgradeCategory.ECONOMIC: "💰 Económicas",
			UpgradeCategory.EFFICIENCY: "⚡ Eficiencia", 
			UpgradeCategory.CRITICAL: "🍀 Críticos",
			UpgradeCategory.MULTIPLIER: "🌟 Multiplicadores"
		}
		return names.get(category, category.value.title())
	
	def _create_category_content(self, category: UpgradeCategory):
		"""Crea el contenido para una categoría de mejoras."""
		# Crear scroll view para las mejoras
		scroll = ScrollView()
		upgrades_layout = GridLayout(
			cols=2,
			spacing=10,
			size_hint_y=None,
			padding=[5, 5, 5, 5]
		)
		upgrades_layout.bind(minimum_height=upgrades_layout.setter('height'))
		
		# Obtener mejoras de esta categoría
		category_upgrades = self.game_state.upgrade_manager.get_upgrades_by_category(category)
		
		# Crear botones para cada mejora en esta categoría
		for upgrade_type in category_upgrades:
			upgrade_info = self.game_state.upgrade_manager.get_upgrade_info(upgrade_type)
			
			upgrade_button = UpgradeButton(
				upgrade_type=upgrade_type,
				upgrade_info=upgrade_info,
				game_state=self.game_state,
				size_hint_y=None,
				height=120,
				halign='center',
				valign='middle'
			)
			upgrade_button.bind(on_press=self.on_upgrade_button)
			
			self.upgrade_buttons[upgrade_type] = upgrade_button
			upgrades_layout.add_widget(upgrade_button)
		
		scroll.add_widget(upgrades_layout)
		return scroll
		
	def on_upgrade_button(self, instance: UpgradeButton):
		"""Maneja el clic en un botón de mejora para comprarla."""
		try:
			success = self.game_state.upgrade_manager.purchase_upgrade(instance.upgrade_type, self.game_state)
			if success:
				logging.info(f"Mejora {instance.upgrade_type} comprada exitosamente")
				self.update_ui()
			else:
				logging.warning(f"No se pudo comprar mejora {instance.upgrade_type}")
		except Exception as e:
			logging.error(f"Error comprando mejora: {e}")
	
	def on_close_button(self, instance):
		"""Maneja el clic en el botón de cerrar."""
		logging.info("Cerrando pantalla de mejoras")
		self.go_back()
	
	def update_ui(self, dt: float = 0):
		"""Actualiza la interfaz con los datos actuales."""
		try:
			# Actualizar estadísticas globales
			stats = self.game_state.upgrade_manager.get_upgrade_stats()
			
			self.stats_labels['click_multiplier'].text = f"Multiplicador Clic: {stats['click_multiplier']:.1f}x"
			self.stats_labels['building_multiplier'].text = f"Multiplicador Edificios: {stats['building_multiplier']:.1f}x"
			self.stats_labels['total_spent'].text = f"💰 Gastado: {stats['total_spent']:,.0f}"
			
			# Actualizar botones de mejoras
			for upgrade_button in self.upgrade_buttons.values():
				upgrade_button.update_display()
				
		except Exception as e:
			logging.error(f"Error actualizando UI de mejoras: {e}")
	
	def on_enter(self, *args):
		"""Se ejecuta cuando se entra a la pantalla."""
		super().on_enter(*args)
		logging.info("Entrando a pantalla de mejoras")
		
		# Actualizar UI inmediatamente
		self.update_ui()
		
		# Programar actualizaciones periódicas
		if not self.update_event:
			self.update_event = Clock.schedule_interval(self.update_ui, 1.0)
	
	def on_leave(self, *args):
		"""Se ejecuta cuando se sale de la pantalla."""
		super().on_leave(*args)
		logging.info("Saliendo de pantalla de mejoras")
		
		# Cancelar actualizaciones periódicas
		if self.update_event:
			Clock.unschedule(self.update_event)
			self.update_event = None
