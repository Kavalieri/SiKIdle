"""Pantalla principal del juego SiKIdle.

Contiene el botón de clic principal, contador de monedas,
área de mejoras y espacios para anuncios.
"""

import logging
import math
from typing import Any

from kivy.animation import Animation  # type: ignore
from kivy.clock import Clock  # type: ignore
from kivy.uix.boxlayout import BoxLayout  # type: ignore
from kivy.uix.button import Button  # type: ignore
from kivy.uix.label import Label  # type: ignore

from core.game import get_game_state
from core.resources import ResourceType
from ui.screen_manager import SiKIdleScreen


class MainScreen(SiKIdleScreen):
	"""Pantalla principal del juego donde ocurre toda la acción."""

	def __init__(self, **kwargs: Any):
		"""Inicializa la pantalla principal del juego."""
		super().__init__(**kwargs)

		self.game_state = get_game_state()
		self.update_scheduled = False

		# Referencias a widgets para actualización
		self.coins_label = None
		self.resources_panel = None
		self.click_button = None
		self.multiplier_label = None
		self.bonus_label = None
		self.ad_button = None
		self.production_label = None

		self.build_ui()

	def build_ui(self):
		"""Construye la interfaz de la pantalla principal."""
		# Layout principal
		main_layout = BoxLayout(
			orientation='vertical',
			padding=[20, 20, 20, 20],
			spacing=15
		)

		# Header con recursos múltiples y navegación
		header = self.create_header()
		main_layout.add_widget(header)

		# Panel de recursos múltiples
		resources_panel = self.create_resources_panel()
		main_layout.add_widget(resources_panel)

		# Área principal de juego
		game_area = self.create_game_area()
		main_layout.add_widget(game_area)

		# Área de mejoras y anuncios
		bottom_area = self.create_bottom_area()
		main_layout.add_widget(bottom_area)

		self.add_widget(main_layout)

		logging.info("Pantalla principal construida")

	def create_header(self) -> BoxLayout:
		"""Crea el header con monedas y navegación.
		
		Returns:
			BoxLayout con el header
		"""
		header = BoxLayout(
			orientation='horizontal',
			size_hint=(1, 0.1),
			spacing=10
		)

		# Botón menú lateral
		menu_button = Button(
			text='☰',
			font_size='24sp',
			size_hint=(0.15, 1),
			background_color=[0.3, 0.5, 0.8, 1]
		)
		menu_button.bind(on_press=self.on_menu_button)
		header.add_widget(menu_button)

		# Contador de monedas (centrado)
		self.coins_label = Label(
			text='💰 0 monedas',
			font_size='24sp',
			size_hint=(0.55, 1),
			bold=True,
			color=[1, 0.8, 0, 1]  # Dorado
		)
		header.add_widget(self.coins_label)

		# Botón volver
		back_button = Button(
			text='← Menú',
			font_size='16sp',
			size_hint=(0.3, 1),
			background_color=[0.6, 0.6, 0.6, 1]
		)
		back_button.bind(on_press=self.on_back_button)
		header.add_widget(back_button)

		return header

	def create_resources_panel(self) -> BoxLayout:
		"""Crea el panel de recursos múltiples.
		
		Returns:
			BoxLayout con información de recursos
		"""
		self.resources_panel = BoxLayout(
			orientation='horizontal',
			size_hint=(1, 0.08),
			spacing=5,
			padding=[10, 5, 10, 5]
		)

		# Obtener recursos desbloqueados
		player_level = 1  # Por ahora nivel fijo, luego será dinámico
		unlocked_resources = self.game_state.resource_manager.get_unlocked_resources(player_level)
		
		# Mostrar solo los 4 recursos principales iniciales
		main_resources = [ResourceType.COINS, ResourceType.EXPERIENCE, ResourceType.ENERGY]
		
		for resource_type in main_resources:
			if resource_type in unlocked_resources:
				resource_info = self.game_state.resource_manager.get_resource_info(resource_type)
				amount = self.game_state.resource_manager.get_resource(resource_type)
				
				resource_label = Label(
					text=f"{resource_info.symbol} {int(amount)}",
					font_size='14sp',
					size_hint=(1, 1),
					color=resource_info.color.replace('#', '').lower()  # Convertir color hex
				)
				resource_label.resource_type = resource_type  # Guardar referencia
				self.resources_panel.add_widget(resource_label)

		return self.resources_panel

	def create_game_area(self) -> BoxLayout:
		"""Crea el área principal de juego con el botón de clic.
		
		Returns:
			BoxLayout con el área de juego
		"""
		game_area = BoxLayout(
			orientation='vertical',
			size_hint=(1, 0.6),
			spacing=20
		)

		# Información del multiplicador
		self.multiplier_label = Label(
			text='Multiplicador: x1.0',
			font_size='18sp',
			size_hint=(1, 0.15),
			color=[0.8, 0.8, 1, 1]  # Azul claro
		)
		game_area.add_widget(self.multiplier_label)

		# Botón de clic principal (grande y centrado)
		self.click_button = Button(
			text='💎\n¡CLICK!',
			font_size='32sp',
			size_hint=(0.8, 0.7),
			pos_hint={'center_x': 0.5},
			background_color=[0.2, 0.8, 0.2, 1]  # Verde brillante
		)
		self.click_button.bind(on_press=self.on_click_button)
		game_area.add_widget(self.click_button)

		# Label de bonificación activa
		self.bonus_label = Label(
			text='',
			font_size='16sp',
			size_hint=(1, 0.15),
			color=[1, 0.6, 0, 1]  # Naranja
		)
		game_area.add_widget(self.bonus_label)

		return game_area

	def create_bottom_area(self) -> BoxLayout:
		"""Crea el área inferior con mejoras y anuncios.
		
		Returns:
			BoxLayout con el área inferior
		"""
		bottom_area = BoxLayout(
			orientation='vertical',
			size_hint=(1, 0.3),
			spacing=10
		)

		# Botones de acción en horizontal
		action_buttons = BoxLayout(
			orientation='horizontal',
			size_hint=(1, 0.5),
			spacing=10
		)

		# Botón de gestión principal (mejoras + edificios)
		management_button = Button(
			text='🏗️ Gestión\n(Mejoras & Edificios)',
			font_size='18sp',
			background_color=[0.2, 0.7, 0.9, 1]  # Azul principal
		)
		management_button.bind(on_press=self.on_management_button)
		action_buttons.add_widget(management_button)

		# Botón de estadísticas
		stats_button = Button(
			text='📊 Estadísticas',
			font_size='18sp',
			background_color=[0.6, 0.8, 0.4, 1]  # Verde
		)
		stats_button.bind(on_press=self.on_stats_button)
		action_buttons.add_widget(stats_button)

		# Botón de anuncio con recompensa
		self.ad_button = Button(
			text='📺 Ver Anuncio\n(x2 monedas 30s)',
			font_size='16sp',
			background_color=[1, 0.6, 0, 1]  # Naranja
		)
		self.ad_button.bind(on_press=self.on_ad_button)
		action_buttons.add_widget(self.ad_button)

		bottom_area.add_widget(action_buttons)

		# Indicador de producción automática
		self.production_label = Label(
			text='📈 Producción automática: 0 monedas/seg',
			font_size='12sp',
			size_hint=(1, 0.3),
			color=[0.7, 0.9, 0.7, 1]  # Verde claro
		)
		bottom_area.add_widget(self.production_label)

		# Espacio para banner publicitario inferior
		banner_bottom = Label(
			text='[ BANNER PUBLICITARIO INFERIOR ]',
			font_size='12sp',
			size_hint=(1, 0.2),
			color=[0.5, 0.5, 0.5, 1]
		)
		bottom_area.add_widget(banner_bottom)

		return bottom_area

	def on_click_button(self, instance: Button):
		"""Maneja el clic en el botón principal.
		
		Args:
			instance: Instancia del botón presionado
		"""
		# Procesar clic en el juego
		coins_earned = self.game_state.click()

		# Animar el botón para feedback visual
		self.animate_click_button()

		# Actualizar interfaz inmediatamente
		self.update_ui()

		logging.debug(f"Clic procesado: +{coins_earned} monedas")

	def animate_click_button(self):
		"""Anima el botón de clic para feedback visual."""
		if self.click_button:
			# Animación de escala (crecer y volver)
			anim = Animation(size_hint=(0.85, 0.75), duration=0.1) + Animation(size_hint=(0.8, 0.7), duration=0.1)
			anim.start(self.click_button)

	def on_ad_button(self, instance: Button):
		"""Maneja el clic en el botón de anuncio.
		
		Args:
			instance: Instancia del botón presionado
		"""
		# TODO: AdMob integration here - Mostrar anuncio real

		# Por ahora simular que el anuncio se vio correctamente
		success = self.game_state.apply_ad_bonus(multiplier=2.0, duration=30)

		if success:
			instance.text = '📺 Anuncio visto\n¡Bonificación activa!'
			instance.background_color = [0.2, 0.8, 0.2, 1]  # Verde

			# Deshabilitar botón temporalmente
			instance.disabled = True

			# Programar reactivación
			Clock.schedule_once(lambda dt: self.reactivate_ad_button(), 30)

			logging.info("Bonificación x2 aplicada por 30 segundos")
		else:
			logging.warning("No se pudo aplicar la bonificación de anuncio")

	def reactivate_ad_button(self):
		"""Reactiva el botón de anuncio después de la bonificación."""
		if self.ad_button:
			self.ad_button.text = '📺 Ver Anuncio\n(x2 monedas 30s)'
			self.ad_button.background_color = [1, 0.6, 0, 1]  # Naranja
			self.ad_button.disabled = False
			logging.info("Botón de anuncio reactivado")

	def on_management_button(self, instance: Button):
		"""Maneja el clic en el botón de gestión (mejoras + edificios).
		
		Args:
			instance: Instancia del botón presionado
		"""
		logging.info("Navegando a pantalla de gestión unificada")
		self.navigate_to('upgrades')  # La pantalla de mejoras ahora incluye edificios

	def on_stats_button(self, instance: Button):
		"""Maneja el clic en el botón de estadísticas.
		
		Args:
			instance: Instancia del botón presionado
		"""
		logging.info("Navegando a pantalla de estadísticas")
		self.navigate_to('stats')

	def on_upgrades_button(self, instance: Button):
		"""Maneja el clic en el botón de mejoras.
		
		Args:
			instance: Instancia del botón presionado
		"""
		logging.info("Navegando a pantalla de mejoras")
		self.navigate_to('upgrades')

	def on_buildings_button(self, instance: Button):
		"""Maneja el clic en el botón de edificios.
		
		Args:
			instance: Instancia del botón presionado
		"""
		logging.info("Navegando a pantalla de edificios")
		self.navigate_to('buildings')

	def on_back_button(self, instance: Button):
		"""Maneja el clic en el botón de volver.
		
		Args:
			instance: Instancia del botón presionado
		"""
		logging.info("Volviendo al menú principal")
		self.navigate_to('start')

	def update_ui(self, dt: float = 0):
		"""Actualiza la interfaz con los datos actuales del juego.
		
		Args:
			dt: Delta time (no usado)
		"""
		# Actualizar la producción automática de los edificios
		if hasattr(self.game_state, 'update_building_production'):
			self.game_state.update_building_production()

		stats = self.game_state.get_game_stats()

		# Actualizar contador de monedas tradicional
		if self.coins_label:
			self.coins_label.text = f"💰 {stats['coins']:,} monedas"

		# Actualizar indicador de producción por segundo
		if hasattr(self, 'production_label') and self.production_label:
			total_production = 0.0
			if hasattr(self.game_state, 'building_manager'):
				for building_type in self.game_state.building_manager.buildings:
					building = self.game_state.building_manager.buildings[building_type]
					if building.count > 0:
						building_info = self.game_state.building_manager.get_building_info(building_type)
						total_production += building_info.base_production * building.count

			self.production_label.text = f"Producción: {total_production:.1f} monedas/seg"

		# Actualizar panel de recursos múltiples
		if hasattr(self, 'resources_panel') and self.resources_panel:
			for child in self.resources_panel.children:
				if hasattr(child, 'resource_type'):
					resource_type = child.resource_type
					resource_info = self.game_state.resource_manager.get_resource_info(resource_type)
					amount = self.game_state.resource_manager.get_resource(resource_type)
					child.text = f"{resource_info.symbol} {int(amount)}"

		# Actualizar multiplicador
		if self.multiplier_label:
			current_mult = stats['current_multiplier']
			if current_mult > stats['multiplier']:
				self.multiplier_label.text = f"Multiplicador: x{current_mult:.1f} (¡BONUS!)"
				self.multiplier_label.color = [1, 0.6, 0, 1]  # Naranja para bonus
			else:
				self.multiplier_label.text = f"Multiplicador: x{current_mult:.1f}"
				self.multiplier_label.color = [0.8, 0.8, 1, 1]  # Azul normal

		# Actualizar estado de bonificación
		if self.bonus_label:
			if stats['bonus_active']:
				remaining = math.ceil(stats['bonus_time_remaining'])
				self.bonus_label.text = f"🔥 ¡BONIFICACIÓN ACTIVA! {remaining}s restantes"
			else:
				self.bonus_label.text = ''

	def on_menu_button(self, instance: Button):
		"""Maneja el clic en el botón del menú.
		
		Args:
			instance: Instancia del botón presionado
		"""
		logging.info("Botón de menú presionado - redirigiendo a configuración")
		# Como eliminamos el menú lateral, redirigimos a configuración
		self.navigate_to('settings')

	def on_enter(self, *args):
		"""Método llamado cuando se entra a la pantalla."""
		super().on_enter(*args)

		# Iniciar el juego si no está corriendo
		if not self.game_state.game_running:
			self.game_state.start_game()

		# Programar actualización de UI
		if not self.update_scheduled:
			Clock.schedule_interval(self.update_ui, 1.0)  # Actualizar cada segundo
			self.update_scheduled = True

		# Actualizar UI inmediatamente
		self.update_ui()

		logging.info("Entrada a pantalla principal de juego")

	def on_leave(self, *args):
		"""Método llamado cuando se sale de la pantalla."""
		super().on_leave(*args)

		# Cancelar actualización de UI
		if self.update_scheduled:
			Clock.unschedule(self.update_ui)
			self.update_scheduled = False

		# No detener el juego aquí, solo pausar la UI
		# El juego sigue corriendo en background

		logging.info("Salida de pantalla principal de juego")
