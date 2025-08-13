"""
Pantalla de gestión de mejoras para el juego SiKIdle.

Sistema de mejoras reorganizado para idle clicker tradicional:
- Idle: Multiplicadores de clic, eficiencia de edificios
- Combat: Mejoras para sistema de combate
- Mixtos: Bonificaciones que afectan ambos sistemas
- PowerUps: Bonificaciones temporales

NOTA: Los edificios se han movido completamente a HomeScreen
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
		# Layout principal optimizado para móvil
		main_layout = BoxLayout(orientation='vertical', padding=[8, 8, 8, 8], spacing=8)
		
		# Header compacto para móvil
		header_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50)
		
		title_label = Label(
			text="⬆️ MEJORAS",
			font_size='20sp',
			bold=True,
			size_hint_x=0.8,
			color=[1, 1, 1, 1]
		)
		
		header_layout.add_widget(title_label)
		
		# Panel de estadísticas compacto
		stats_layout = BoxLayout(
			orientation='horizontal',
			size_hint_y=None,
			height=40,
			spacing=5
		)
		
		self.stats_labels['total_spent'] = Label(
			text="💰 Gastado: 0",
			font_size='12sp',
			size_hint_x=0.5
		)
		self.stats_labels['active_upgrades'] = Label(
			text="⚡ Activas: 0",
			font_size='12sp',
			size_hint_x=0.5
		)
		
		for label in self.stats_labels.values():
			stats_layout.add_widget(label)
		
		# Crear panel con sub-pestañas específicas para idle clicker
		tab_panel = TabbedPanel(do_default_tab=False, tab_width=80, tab_height=40)
		
		# Sub-pestañas específicas para idle clicker
		self._create_idle_tab(tab_panel)
		self._create_combat_tab(tab_panel)
		self._create_mixed_tab(tab_panel)
		self._create_powerups_tab(tab_panel)
		
		# Ensamblar layout principal
		main_layout.add_widget(header_layout)
		main_layout.add_widget(stats_layout)
		main_layout.add_widget(tab_panel)
		
		self.add_widget(main_layout)
	
	def _create_idle_tab(self, tab_panel):
		"""Crea la pestaña de mejoras para idle clicker."""
		idle_tab = TabbedPanelItem(text="🏠 Idle")
		idle_content = self._create_upgrade_content([
			# Mejoras específicas para idle clicker
			('click_power', '👆 Poder de Clic', 'Aumenta monedas por clic', 10),
			('building_efficiency', '🏗️ Eficiencia', 'Mejora producción de edificios', 50),
			('offline_earnings', '💤 Ingresos Offline', 'Gana mientras no juegas', 100),
			('auto_clicker', '🤖 Auto-Clic', 'Clics automáticos por segundo', 500)
		])
		idle_tab.add_widget(idle_content)
		tab_panel.add_widget(idle_tab)
	
	def _create_combat_tab(self, tab_panel):
		"""Crea la pestaña de mejoras para combate."""
		combat_tab = TabbedPanelItem(text="⚔️ Combat")
		combat_content = self._create_upgrade_content([
			# Mejoras específicas para combate
			('damage_boost', '⚔️ Daño', 'Aumenta daño en combate', 25),
			('critical_chance', '🍀 Crítico', 'Probabilidad de golpe crítico', 75),
			('health_regen', '❤️ Regeneración', 'Recupera HP automáticamente', 40),
			('combat_speed', '⚡ Velocidad', 'Ataques más rápidos', 60)
		])
		combat_tab.add_widget(combat_content)
		tab_panel.add_widget(combat_tab)
	
	def _create_mixed_tab(self, tab_panel):
		"""Crea la pestaña de mejoras mixtas."""
		mixed_tab = TabbedPanelItem(text="🌟 Mixtos")
		mixed_content = self._create_upgrade_content([
			# Mejoras que afectan ambos sistemas
			('global_multiplier', '🌟 Multiplicador Global', 'Bonifica todo el progreso', 200),
			('prestige_bonus', '💎 Bonus Prestigio', 'Mejora cristales de prestigio', 150),
			('luck_factor', '🍀 Factor Suerte', 'Mejora todas las probabilidades', 100),
			('experience_boost', '📚 Boost XP', 'Más experiencia en todo', 80)
		])
		mixed_tab.add_widget(mixed_content)
		tab_panel.add_widget(mixed_tab)
	
	def _create_powerups_tab(self, tab_panel):
		"""Crea la pestaña de power-ups temporales."""
		powerups_tab = TabbedPanelItem(text="⏰ PowerUps")
		powerups_content = self._create_powerup_content([
			# Power-ups temporales
			('double_coins', '💰x2', '2x monedas por 1 hora', 50, 3600),
			('triple_click', '👆x3', '3x poder de clic por 30min', 30, 1800),
			('speed_boost', '⚡x5', '5x velocidad por 15min', 75, 900),
			('mega_luck', '🍀x10', '10x suerte por 10min', 100, 600)
		])
		powerups_tab.add_widget(powerups_content)
		tab_panel.add_widget(powerups_tab)
	
	def _create_upgrade_content(self, upgrades_data):
		"""Crea contenido para mejoras permanentes."""
		scroll = ScrollView()
		upgrades_layout = GridLayout(
			cols=1,
			spacing=5,
			size_hint_y=None,
			padding=[5, 5, 5, 5]
		)
		upgrades_layout.bind(minimum_height=upgrades_layout.setter('height'))
		
		for upgrade_id, name, desc, cost in upgrades_data:
			upgrade_widget = self._create_upgrade_widget(upgrade_id, name, desc, cost)
			upgrades_layout.add_widget(upgrade_widget)
		
		scroll.add_widget(upgrades_layout)
		return scroll
	
	def _create_powerup_content(self, powerups_data):
		"""Crea contenido para power-ups temporales."""
		scroll = ScrollView()
		powerups_layout = GridLayout(
			cols=1,
			spacing=5,
			size_hint_y=None,
			padding=[5, 5, 5, 5]
		)
		powerups_layout.bind(minimum_height=powerups_layout.setter('height'))
		
		for powerup_id, name, desc, cost, duration in powerups_data:
			powerup_widget = self._create_powerup_widget(powerup_id, name, desc, cost, duration)
			powerups_layout.add_widget(powerup_widget)
		
		scroll.add_widget(powerups_layout)
		return scroll
	
	def _create_upgrade_widget(self, upgrade_id, name, desc, cost):
		"""Crea widget para mejora permanente."""
		widget = BoxLayout(
			orientation='horizontal',
			size_hint_y=None,
			height=60,
			spacing=8,
			padding=[4, 4, 4, 4]
		)
		
		# Información de la mejora
		info_layout = BoxLayout(orientation='vertical', size_hint_x=0.7)
		
		name_label = Label(
			text=name,
			font_size='14sp',
			bold=True,
			size_hint_y=0.6,
			halign='left',
			valign='center'
		)
		name_label.bind(texture_size=name_label.setter('text_size'))
		
		desc_label = Label(
			text=desc,
			font_size='11sp',
			color=[0.7, 0.7, 0.7, 1],
			size_hint_y=0.4,
			halign='left',
			valign='center'
		)
		desc_label.bind(texture_size=desc_label.setter('text_size'))
		
		info_layout.add_widget(name_label)
		info_layout.add_widget(desc_label)
		
		# Botón de compra
		can_afford = self.game_state.coins >= cost
		buy_button = Button(
			text=f"💰 {cost}",
			font_size='12sp',
			size_hint_x=0.3,
			background_color=[0.2, 0.8, 0.2, 1] if can_afford else [0.8, 0.2, 0.2, 1]
		)
		buy_button.disabled = not can_afford
		buy_button.bind(on_press=lambda x: self.on_upgrade_purchase(upgrade_id, cost))
		
		widget.add_widget(info_layout)
		widget.add_widget(buy_button)
		return widget
	
	def _create_powerup_widget(self, powerup_id, name, desc, cost, duration):
		"""Crea widget para power-up temporal."""
		widget = BoxLayout(
			orientation='horizontal',
			size_hint_y=None,
			height=60,
			spacing=8,
			padding=[4, 4, 4, 4]
		)
		
		# Información del power-up
		info_layout = BoxLayout(orientation='vertical', size_hint_x=0.7)
		
		name_label = Label(
			text=f"{name} ({duration//60}min)",
			font_size='14sp',
			bold=True,
			size_hint_y=0.6,
			halign='left',
			valign='center'
		)
		name_label.bind(texture_size=name_label.setter('text_size'))
		
		desc_label = Label(
			text=desc,
			font_size='11sp',
			color=[0.7, 0.7, 0.7, 1],
			size_hint_y=0.4,
			halign='left',
			valign='center'
		)
		desc_label.bind(texture_size=desc_label.setter('text_size'))
		
		info_layout.add_widget(name_label)
		info_layout.add_widget(desc_label)
		
		# Botón de activación
		can_afford = self.game_state.coins >= cost
		activate_button = Button(
			text=f"⚡ {cost}",
			font_size='12sp',
			size_hint_x=0.3,
			background_color=[0.8, 0.6, 0.2, 1] if can_afford else [0.8, 0.2, 0.2, 1]
		)
		activate_button.disabled = not can_afford
		activate_button.bind(on_press=lambda x: self.on_powerup_activate(powerup_id, cost, duration))
		
		widget.add_widget(info_layout)
		widget.add_widget(activate_button)
		return widget
	
	def on_upgrade_purchase(self, upgrade_id, cost):
		"""Maneja la compra de una mejora permanente."""
		if self.game_state.coins >= cost:
			self.game_state.coins -= cost
			logging.info(f"Mejora {upgrade_id} comprada por {cost} monedas")
			self.update_ui()
	
	def on_powerup_activate(self, powerup_id, cost, duration):
		"""Maneja la activación de un power-up temporal."""
		if self.game_state.coins >= cost:
			self.game_state.coins -= cost
			logging.info(f"Power-up {powerup_id} activado por {duration} segundos")
			# TODO: Implementar sistema de power-ups temporales
			self.update_ui()
	
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
	

	
	def update_ui(self, dt: float = 0):
		"""Actualiza la interfaz con los datos actuales."""
		try:
			# Actualizar estadísticas simplificadas
			self.stats_labels['total_spent'].text = f"💰 Gastado: {0:,.0f}"  # TODO: Implementar tracking
			self.stats_labels['active_upgrades'].text = f"⚡ Activas: {0}"  # TODO: Contar mejoras activas
			
		except Exception as e:
			logging.error(f"Error actualizando UI de mejoras: {e}")
	
	def on_enter(self, *args):
		"""Se ejecuta cuando se entra a la pantalla."""
		super().on_enter(*args)
		logging.info("Entrando a pantalla de mejoras rediseñada")
		
		# Actualizar UI inmediatamente
		self.update_ui()
		
		# Programar actualizaciones periódicas
		if not self.update_event:
			self.update_event = Clock.schedule_interval(self.update_ui, 2.0)
	
	def on_leave(self, *args):
		"""Se ejecuta cuando se sale de la pantalla."""
		super().on_leave(*args)
		logging.info("Saliendo de pantalla de mejoras")
		
		# Cancelar actualizaciones periódicas
		if self.update_event:
			Clock.unschedule(self.update_event)
			self.update_event = None
