"""
Pantalla de gestión de edificios para el juego SiKIdle.

Esta pantalla permite a los jugadores:
- Ver todos los edificios disponibles y desbloqueados
- Comprar nuevos edificios para generar recursos automáticamente
- Ver estadísticas de producción de cada tipo de edificio
- Gestionar el progreso de construcciones
"""

import logging
from typing import Optional, Dict, List
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.progressbar import ProgressBar
from kivy.clock import Clock

from core.game import GameState
from core.buildings import BuildingType


class BuildingButton(Button):
	"""Botón personalizado para representar un edificio."""
	
	def __init__(self, building_type: BuildingType, building_info, game_state: GameState, **kwargs):
		super().__init__(**kwargs)
		self.building_type = building_type
		self.building_info = building_info
		self.game_state = game_state
		self.update_display()
		
	def update_display(self):
		"""Actualiza la información mostrada del edificio."""
		building = self.game_state.building_manager.get_building(self.building_type)
		cost = self.game_state.building_manager.get_building_cost(self.building_type)
		
		# Verificar si se puede permitir
		can_afford = True
		for resource_type, amount in cost.items():
			if self.game_state.resource_manager.get_resource(resource_type) < amount:
				can_afford = False
				break
		
		# Configurar texto del botón
		self.text = (f"{self.building_info.name}\n"
					f"Cantidad: {building.count}\n"
					f"Producción: {self.building_info.base_production:.1f}/seg\n"
					f"Costo: {cost}")
		
		# Configurar colores
		if can_afford:
			self.background_color = [0.2, 0.8, 0.2, 1]  # Verde si se puede permitir
		else:
			self.background_color = [0.8, 0.2, 0.2, 1]  # Rojo si no se puede permitir
			
		# Desactivar si no se puede permitir
		self.disabled = not can_afford


class BuildingsScreen(Screen):
	"""Pantalla principal de gestión de edificios."""
	
	def __init__(self, game_state: GameState, manager_ref=None, **kwargs):
		super().__init__(**kwargs)
		self.game_state = game_state
		self.manager_ref = manager_ref
		self.building_buttons: Dict[BuildingType, BuildingButton] = {}
		self.stats_labels: Dict[str, Label] = {}
		self.update_event = None
		
		self.build_ui()
		
	def build_ui(self):
		"""Construye la interfaz de usuario de la pantalla de edificios."""
		# Layout principal
		main_layout = BoxLayout(orientation='vertical', padding=[10, 10, 10, 10], spacing=10)
		
		# Header con título y botón de cerrar
		header_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=60)
		
		title_label = Label(
			text="🏭 EDIFICIOS Y GENERADORES",
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
		
		self.stats_labels['total_buildings'] = Label(
			text="Total edificios: 0",
			size_hint_x=0.33
		)
		self.stats_labels['total_production'] = Label(
			text="Producción total: 0.0/seg",
			size_hint_x=0.33
		)
		self.stats_labels['resources'] = Label(
			text="💰 0",
			size_hint_x=0.34
		)
		
		for label in self.stats_labels.values():
			stats_layout.add_widget(label)
		
		# Crear scroll view para edificios
		scroll = ScrollView()
		buildings_layout = GridLayout(
			cols=2,
			spacing=10,
			size_hint_y=None,
			padding=[5, 5, 5, 5]
		)
		buildings_layout.bind(minimum_height=buildings_layout.setter('height'))
		
		# Crear botones para cada tipo de edificio
		for building_type in BuildingType:
			building_info = self.game_state.building_manager.get_building_info(building_type)
			
			building_button = BuildingButton(
				building_type=building_type,
				building_info=building_info,
				game_state=self.game_state,
				size_hint_y=None,
				height=120,
				halign='center',
				valign='middle'
			)
			building_button.bind(on_press=self.on_building_button)
			
			self.building_buttons[building_type] = building_button
			buildings_layout.add_widget(building_button)
		
		scroll.add_widget(buildings_layout)
		
		# Ensamblar layout principal
		main_layout.add_widget(header_layout)
		main_layout.add_widget(stats_layout)
		main_layout.add_widget(scroll)
		
		self.add_widget(main_layout)
		
	def on_building_button(self, instance: BuildingButton):
		"""Maneja el clic en un botón de edificio para comprarlo."""
		try:
			success = self.game_state.building_manager.purchase_building(instance.building_type, self.game_state)
			if success:
				logging.info(f"Edificio {instance.building_type} comprado exitosamente")
				self.update_ui()
			else:
				logging.warning(f"No se pudo comprar edificio {instance.building_type}")
		except Exception as e:
			logging.error(f"Error comprando edificio: {e}")
	
	def on_close_button(self, instance):
		"""Maneja el clic en el botón de cerrar."""
		logging.info("Cerrando pantalla de edificios")
		if self.manager_ref:
			self.manager_ref.current = 'main'
	
	def update_ui(self, dt: float = 0):
		"""Actualiza la interfaz con los datos actuales."""
		try:
			# Actualizar estadísticas globales
			total_buildings = sum(building.count 
								for building in self.game_state.building_manager.buildings.values())
			
			total_production = 0.0
			for building_type in self.game_state.building_manager.buildings:
				building = self.game_state.building_manager.buildings[building_type]
				if building.count > 0:
					building_info = self.game_state.building_manager.get_building_info(building_type)
					total_production += building_info.base_production * building.count
			
			coins = self.game_state.resource_manager.get_resource('coins')
			
			self.stats_labels['total_buildings'].text = f"Total edificios: {total_buildings}"
			self.stats_labels['total_production'].text = f"Producción total: {total_production:.1f}/seg"
			self.stats_labels['resources'].text = f"💰 {coins:,.0f}"
			
			# Actualizar botones de edificios
			for building_button in self.building_buttons.values():
				building_button.update_display()
				
		except Exception as e:
			logging.error(f"Error actualizando UI de edificios: {e}")
	
	def on_enter(self, *args):
		"""Se ejecuta cuando se entra a la pantalla."""
		super().on_enter(*args)
		logging.info("Entrando a pantalla de edificios")
		
		# Actualizar UI inmediatamente
		self.update_ui()
		
		# Programar actualizaciones periódicas
		if not self.update_event:
			self.update_event = Clock.schedule_interval(self.update_ui, 1.0)
	
	def on_leave(self, *args):
		"""Se ejecuta cuando se sale de la pantalla."""
		super().on_leave(*args)
		logging.info("Saliendo de pantalla de edificios")
		
		# Cancelar actualizaciones periódicas
		if self.update_event:
			Clock.unschedule(self.update_event)
			self.update_event = None
