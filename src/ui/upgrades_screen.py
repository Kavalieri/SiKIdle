"""Pantalla de mejoras para SiKIdle.

Permite al jugador comprar mejoras que aumentan su
eficiencia de clicks y generación de monedas.
"""

import logging
from typing import Any

from kivy.clock import Clock  # type: ignore
from kivy.uix.boxlayout import BoxLayout  # type: ignore
from kivy.uix.button import Button  # type: ignore
from kivy.uix.label import Label  # type: ignore
from kivy.uix.scrollview import ScrollView  # type: ignore

from core.game import get_game_state
from ui.screen_manager import SiKIdleScreen
from utils.save import get_save_manager


class UpgradesScreen(SiKIdleScreen):
	"""Pantalla de mejoras del juego."""

	def __init__(self, **kwargs: Any):
		"""Inicializa la pantalla de mejoras."""
		super().__init__(**kwargs)

		self.save_manager = get_save_manager()
		self.game_state = get_game_state()

		# Referencias a elementos UI para actualización
		self.upgrade_buttons: dict[str, Button] = {}
		self.upgrade_labels: dict[str, Label] = {}
		self.coins_label = None

		# Definir mejoras disponibles
		self.upgrades = self.define_upgrades()

		self.build_ui()

		# Programar actualización de UI
		self.update_event = Clock.schedule_interval(self.update_ui, 1.0)

	def define_upgrades(self) -> dict[str, dict]:
		"""Define las mejoras disponibles en el juego.
		
		Returns:
			Diccionario con definiciones de mejoras
		"""
		return {
			'cursor': {
				'name': '👆 Cursor Mejorado',
				'description': 'Aumenta las monedas por click',
				'base_cost': 15,
				'cost_multiplier': 1.15,
				'base_effect': 1,
				'effect_multiplier': 1.0,
				'max_level': 100,
				'category': 'click'
			},
			'auto_clicker': {
				'name': '🤖 Auto-Clicker',
				'description': 'Genera clicks automáticos',
				'base_cost': 100,
				'cost_multiplier': 1.20,
				'base_effect': 1,
				'effect_multiplier': 1.1,
				'max_level': 50,
				'category': 'auto'
			},
			'multiplier': {
				'name': '✨ Multiplicador',
				'description': 'Multiplica todas las ganancias',
				'base_cost': 500,
				'cost_multiplier': 1.50,
				'base_effect': 0.1,
				'effect_multiplier': 1.0,
				'max_level': 25,
				'category': 'multiplier'
			},
			'efficiency': {
				'name': '⚡ Eficiencia',
				'description': 'Reduce costos de otras mejoras',
				'base_cost': 250,
				'cost_multiplier': 1.30,
				'base_effect': 0.02,
				'effect_multiplier': 1.0,
				'max_level': 20,
				'category': 'utility'
			},
			'prestige': {
				'name': '👑 Prestigio',
				'description': 'Bonificación permanente post-reinicio',
				'base_cost': 10000,
				'cost_multiplier': 2.0,
				'base_effect': 0.05,
				'effect_multiplier': 1.0,
				'max_level': 10,
				'category': 'prestige'
			},
			'luck': {
				'name': '🍀 Suerte',
				'description': 'Probabilidad de clicks críticos',
				'base_cost': 750,
				'cost_multiplier': 1.35,
				'base_effect': 0.01,
				'effect_multiplier': 1.0,
				'max_level': 30,
				'category': 'special'
			}
		}

	def build_ui(self):
		"""Construye la interfaz de la pantalla de mejoras."""
		# Layout principal
		main_layout = BoxLayout(
			orientation='vertical',
			padding=[30, 40, 30, 30],
			spacing=25
		)

		# Header con título, monedas y botón volver
		header = self.build_header()
		main_layout.add_widget(header)

		# Área de mejoras con scroll
		scroll = ScrollView(
			size_hint=(1, 0.85)
		)

		upgrades_layout = BoxLayout(
			orientation='vertical',
			spacing=15,
			size_hint_y=None
		)
		upgrades_layout.bind(minimum_height=upgrades_layout.setter('height'))

		# Crear mejoras por categoría
		self.create_upgrades_by_category(upgrades_layout)

		scroll.add_widget(upgrades_layout)
		main_layout.add_widget(scroll)

		self.add_widget(main_layout)

		logging.info("Pantalla de mejoras construida")

	def build_header(self) -> BoxLayout:
		"""Construye el header de la pantalla.
		
		Returns:
			BoxLayout con el header
		"""
		header = BoxLayout(
			orientation='vertical',
			size_hint=(1, 0.15),
			spacing=10
		)

		# Fila superior: botón volver y título
		top_row = BoxLayout(
			orientation='horizontal',
			size_hint=(1, 0.6),
			spacing=10
		)

		back_button = Button(
			text='← Volver',
			font_size='16sp',
			size_hint=(0.25, 1),
			background_color=[0.6, 0.6, 0.6, 1]
		)
		back_button.bind(on_press=self.on_back_button)
		top_row.add_widget(back_button)

		title_label = Label(
			text='🛠️ Mejoras',
			font_size='28sp',
			size_hint=(0.75, 1),
			bold=True,
			color=[0.8, 0.8, 1, 1]
		)
		top_row.add_widget(title_label)

		header.add_widget(top_row)

		# Fila inferior: monedas disponibles
		coins_row = BoxLayout(
			orientation='horizontal',
			size_hint=(1, 0.4)
		)

		coins_icon = Label(
			text='💰',
			font_size='24sp',
			size_hint=(0.15, 1)
		)
		coins_row.add_widget(coins_icon)

		self.coins_label = Label(
			text=f'{self.game_state.coins:,} monedas',
			font_size='20sp',
			size_hint=(0.85, 1),
			color=[1, 1, 0.6, 1],
			bold=True,
			halign='left',
			valign='center'
		)
		self.coins_label.text_size = (None, None)
		coins_row.add_widget(self.coins_label)

		header.add_widget(coins_row)

		return header

	def create_upgrades_by_category(self, parent: BoxLayout):
		"""Crea las mejoras organizadas por categoría.
		
		Args:
			parent: Layout padre donde agregar las mejoras
		"""
		categories = {
			'click': '👆 Mejoras de Click',
			'auto': '🤖 Automatización',
			'multiplier': '✨ Multiplicadores',
			'utility': '⚡ Utilidades',
			'special': '🍀 Especiales',
			'prestige': '👑 Prestigio'
		}

		for category_key, category_name in categories.items():
			# Obtener mejoras de esta categoría
			category_upgrades = [
				(upgrade_id, upgrade_data)
				for upgrade_id, upgrade_data in self.upgrades.items()
				if upgrade_data['category'] == category_key
			]

			if not category_upgrades:
				continue

			# Crear sección de categoría
			category_section = self.create_category_section(category_name, category_upgrades)
			parent.add_widget(category_section)

	def create_category_section(self, title: str, upgrades: list[tuple[str, dict]]) -> BoxLayout:
		"""Crea una sección de categoría de mejoras.
		
		Args:
			title: Título de la categoría
			upgrades: Lista de mejoras en la categoría
			
		Returns:
			BoxLayout con la sección de categoría
		"""
		section = BoxLayout(
			orientation='vertical',
			size_hint=(1, None),
			spacing=10
		)

		# Título de la categoría
		title_label = Label(
			text=title,
			font_size='20sp',
			size_hint=(1, None),
			height='35dp',
			bold=True,
			color=[0.9, 0.9, 1, 1],
			halign='left',
			valign='center'
		)
		title_label.text_size = (400, None)
		section.add_widget(title_label)

		# Mejoras individuales
		for upgrade_id, upgrade_data in upgrades:
			upgrade_widget = self.create_upgrade_widget(upgrade_id, upgrade_data)
			section.add_widget(upgrade_widget)

		# Separador
		separator = Label(
			text='─' * 40,
			font_size='14sp',
			size_hint=(1, None),
			height='15dp',
			color=[0.4, 0.4, 0.4, 1]
		)
		section.add_widget(separator)

		# Calcular altura total
		total_height = 35 + (len(upgrades) * 100) + 15 + (len(upgrades) * 10)
		section.height = total_height

		return section

	def create_upgrade_widget(self, upgrade_id: str, upgrade_data: dict) -> BoxLayout:
		"""Crea el widget para una mejora individual.
		
		Args:
			upgrade_id: ID de la mejora
			upgrade_data: Datos de la mejora
			
		Returns:
			BoxLayout con el widget de mejora
		"""
		# Obtener nivel actual
		current_level = self.save_manager.get_upgrade_level(upgrade_id)
		cost = self.calculate_cost(upgrade_id, current_level)
		can_afford = self.game_state.coins >= cost
		max_level_reached = current_level >= upgrade_data['max_level']

		# Widget principal
		widget = BoxLayout(
			orientation='horizontal',
			size_hint=(1, None),
			height='90dp',
			spacing=10
		)

		# Información de la mejora (lado izquierdo)
		info_layout = BoxLayout(
			orientation='vertical',
			size_hint=(0.7, 1),
			spacing=2
		)

		# Nombre y nivel
		name_label = Label(
			text=f"{upgrade_data['name']} (Nv. {current_level})",
			font_size='18sp',
			size_hint=(1, 0.4),
			bold=True,
			color=[0.9, 0.9, 0.9, 1],
			halign='left',
			valign='center'
		)
		name_label.text_size = (300, None)
		info_layout.add_widget(name_label)

		# Descripción
		desc_label = Label(
			text=upgrade_data['description'],
			font_size='14sp',
			size_hint=(1, 0.3),
			color=[0.7, 0.7, 0.7, 1],
			halign='left',
			valign='center'
		)
		desc_label.text_size = (300, None)
		info_layout.add_widget(desc_label)

		# Efecto actual
		effect_text = self.get_effect_text(upgrade_id, current_level)
		effect_label = Label(
			text=f"Efecto: {effect_text}",
			font_size='14sp',
			size_hint=(1, 0.3),
			color=[0.6, 1, 0.6, 1],
			halign='left',
			valign='center'
		)
		effect_label.text_size = (300, None)
		info_layout.add_widget(effect_label)

		widget.add_widget(info_layout)

		# Botón de compra (lado derecho)
		button_layout = BoxLayout(
			orientation='vertical',
			size_hint=(0.3, 1),
			spacing=5
		)

		if max_level_reached:
			buy_button = Button(
				text='MAX',
				font_size='16sp',
				size_hint=(1, 0.6),
				background_color=[0.4, 0.4, 0.4, 1]
			)
			buy_button.disabled = True
		else:
			buy_button = Button(
				text=f'💰 {cost:,}',
				font_size='16sp',
				size_hint=(1, 0.6),
				background_color=[0.2, 0.8, 0.2, 1] if can_afford else [0.6, 0.2, 0.2, 1]
			)
			buy_button.bind(on_press=lambda x: self.buy_upgrade(upgrade_id))
			buy_button.disabled = not can_afford

		button_layout.add_widget(buy_button)

		# Label con próximo nivel
		if not max_level_reached:
			next_effect = self.get_effect_text(upgrade_id, current_level + 1)
			next_label = Label(
				text=f'→ {next_effect}',
				font_size='12sp',
				size_hint=(1, 0.4),
				color=[0.8, 0.8, 1, 1],
				halign='center',
				valign='center'
			)
			next_label.text_size = (100, None)
			button_layout.add_widget(next_label)
		else:
			spacer = Label(size_hint=(1, 0.4))
			button_layout.add_widget(spacer)

		widget.add_widget(button_layout)

		# Guardar referencias
		self.upgrade_buttons[upgrade_id] = buy_button
		self.upgrade_labels[upgrade_id] = name_label

		return widget

	def calculate_cost(self, upgrade_id: str, level: int) -> int:
		"""Calcula el costo de una mejora en un nivel específico.
		
		Args:
			upgrade_id: ID de la mejora
			level: Nivel para el cual calcular el costo
			
		Returns:
			Costo de la mejora
		"""
		upgrade_data = self.upgrades[upgrade_id]
		base_cost = upgrade_data['base_cost']
		multiplier = upgrade_data['cost_multiplier']

		# Aplicar descuento por eficiencia
		efficiency_level = self.save_manager.get_upgrade_level('efficiency')
		efficiency_discount = 1.0 - (efficiency_level * 0.02)

		cost = int(base_cost * (multiplier ** level) * efficiency_discount)
		return max(cost, 1)  # Mínimo 1 moneda

	def get_effect_text(self, upgrade_id: str, level: int) -> str:
		"""Obtiene el texto del efecto de una mejora en un nivel.
		
		Args:
			upgrade_id: ID de la mejora
			level: Nivel de la mejora
			
		Returns:
			Texto describiendo el efecto
		"""
		if level == 0:
			return "Sin efecto"

		upgrade_data = self.upgrades[upgrade_id]
		base_effect = upgrade_data['base_effect']
		multiplier = upgrade_data['effect_multiplier']

		effect_value = base_effect * (multiplier ** (level - 1)) * level

		effect_mapping = {
			'cursor': f"+{effect_value:.0f} monedas/click",
			'auto_clicker': f"{effect_value:.1f} clicks/seg",
			'multiplier': f"x{1 + effect_value:.1f} ganancias",
			'efficiency': f"-{effect_value*100:.0f}% costos",
			'prestige': f"+{effect_value*100:.1f}% permanente",
			'luck': f"{effect_value*100:.1f}% crítico"
		}

		return effect_mapping.get(upgrade_id, f"{effect_value:.2f}")

	def buy_upgrade(self, upgrade_id: str):
		"""Compra una mejora.
		
		Args:
			upgrade_id: ID de la mejora a comprar
		"""
		current_level = self.save_manager.get_upgrade_level(upgrade_id)
		cost = self.calculate_cost(upgrade_id, current_level)
		upgrade_data = self.upgrades[upgrade_id]

		# Verificar si se puede comprar
		if (self.game_state.coins >= cost and
			current_level < upgrade_data['max_level']):

			# Realizar compra
			self.game_state.spend_coins(cost)
			self.save_manager.set_upgrade_level(upgrade_id, current_level + 1)

			# Actualizar estadísticas
			self.save_manager.increment_stat('upgrades_bought', 1)
			self.save_manager.increment_stat('total_coins_spent', cost)

			# Aplicar efecto inmediatamente
			self.apply_upgrade_effect(upgrade_id, current_level + 1)

			logging.info(f"Mejora comprada: {upgrade_id} nivel {current_level + 1}")

			# Actualizar UI inmediatamente
			self.update_ui()

	def apply_upgrade_effect(self, upgrade_id: str, level: int):
		"""Aplica el efecto de una mejora al estado del juego.
		
		Args:
			upgrade_id: ID de la mejora
			level: Nivel de la mejora
		"""
		# Los efectos se aplicarán en el GameState cuando se recalculen
		# los multiplicadores en el próximo tick
		pass

	def update_ui(self, dt=None):
		"""Actualiza la interfaz de usuario.
		
		Args:
			dt: Delta time (no usado)
		"""
		# Actualizar monedas
		if self.coins_label:
			self.coins_label.text = f'{self.game_state.coins:,} monedas'

		# Actualizar botones de mejoras
		for upgrade_id, button in self.upgrade_buttons.items():
			current_level = self.save_manager.get_upgrade_level(upgrade_id)
			cost = self.calculate_cost(upgrade_id, current_level)
			can_afford = self.game_state.coins >= cost
			max_level_reached = current_level >= self.upgrades[upgrade_id]['max_level']

			if max_level_reached:
				button.text = 'MAX'
				button.background_color = [0.4, 0.4, 0.4, 1]
				button.disabled = True
			else:
				button.text = f'💰 {cost:,}'
				button.background_color = [0.2, 0.8, 0.2, 1] if can_afford else [0.6, 0.2, 0.2, 1]
				button.disabled = not can_afford

		# Actualizar labels de nivel
		for upgrade_id, label in self.upgrade_labels.items():
			current_level = self.save_manager.get_upgrade_level(upgrade_id)
			upgrade_data = self.upgrades[upgrade_id]
			label.text = f"{upgrade_data['name']} (Nv. {current_level})"

	def on_back_button(self, instance: Button):
		"""Maneja el clic en el botón de volver.
		
		Args:
			instance: Instancia del botón presionado
		"""
		logging.info("Volviendo desde mejoras")
		self.go_back()

	def on_enter(self, *args):
		"""Método llamado cuando se entra a la pantalla."""
		super().on_enter(*args)

		# Actualizar UI al entrar
		self.update_ui()

		logging.info("Entrada a pantalla de mejoras")

	def on_leave(self, *args):
		"""Método llamado cuando se sale de la pantalla."""
		super().on_leave(*args)

		# Cancelar actualizaciones
		if self.update_event:
			self.update_event.cancel()

		logging.info("Salida de pantalla de mejoras")
