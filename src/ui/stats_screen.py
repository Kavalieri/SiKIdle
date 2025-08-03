"""Pantalla de estadísticas para SiKIdle.

Muestra estadísticas detalladas del progreso del jugador
como clicks totales, tiempo jugado, ingresos, etc.
"""

from kivy.uix.boxlayout import BoxLayout  # type: ignore
from kivy.uix.button import Button  # type: ignore
from kivy.uix.label import Label  # type: ignore
from kivy.uix.scrollview import ScrollView  # type: ignore
import logging
from typing import Any, Dict

from ui.screen_manager import SiKIdleScreen
from utils.save import get_save_manager
from core.game import get_game_state


class StatsScreen(SiKIdleScreen):
	"""Pantalla de estadísticas del juego."""
	
	def __init__(self, **kwargs: Any):
		"""Inicializa la pantalla de estadísticas."""
		super().__init__(**kwargs)
		
		self.save_manager = get_save_manager()
		self.game_state = get_game_state()
		
		# Referencias a labels de estadísticas para actualización
		self.stats_labels: Dict[str, Label] = {}
		
		self.build_ui()
		
	def build_ui(self):
		"""Construye la interfaz de la pantalla de estadísticas."""
		# Layout principal
		main_layout = BoxLayout(
			orientation='vertical',
			padding=[30, 40, 30, 30],
			spacing=25
		)
		
		# Header con título y botón volver
		header = BoxLayout(
			orientation='horizontal',
			size_hint=(1, 0.1),
			spacing=10
		)
		
		back_button = Button(
			text='← Volver',
			font_size='16sp',
			size_hint=(0.3, 1),
			background_color=[0.6, 0.6, 0.6, 1]
		)
		back_button.bind(on_press=self.on_back_button)
		header.add_widget(back_button)
		
		title_label = Label(
			text='📊 Estadísticas',
			font_size='28sp',
			size_hint=(0.7, 1),
			bold=True,
			color=[0.8, 0.8, 1, 1]
		)
		header.add_widget(title_label)
		
		main_layout.add_widget(header)
		
		# Área de estadísticas con scroll
		scroll = ScrollView(
			size_hint=(1, 0.9)
		)
		
		stats_layout = BoxLayout(
			orientation='vertical',
			spacing=15,
			size_hint_y=None
		)
		stats_layout.bind(minimum_height=stats_layout.setter('height'))
		
		# Crear secciones de estadísticas
		self.create_gameplay_stats(stats_layout)
		self.create_economy_stats(stats_layout)
		self.create_time_stats(stats_layout)
		self.create_achievement_stats(stats_layout)
		
		scroll.add_widget(stats_layout)
		main_layout.add_widget(scroll)
		
		self.add_widget(main_layout)
		
		logging.info("Pantalla de estadísticas construida")
	
	def create_gameplay_stats(self, parent: BoxLayout):
		"""Crea la sección de estadísticas de juego.
		
		Args:
			parent: Layout padre donde agregar la sección
		"""
		section = self.create_stats_section(
			'🎮 Estadísticas de Juego',
			[
				('total_clicks', 'Clicks totales'),
				('clicks_per_second', 'Clicks por segundo'),
				('highest_cps', 'Máximo CPS alcanzado'),
				('total_sessions', 'Sesiones de juego'),
			]
		)
		parent.add_widget(section)
	
	def create_economy_stats(self, parent: BoxLayout):
		"""Crea la sección de estadísticas económicas.
		
		Args:
			parent: Layout padre donde agregar la sección
		"""
		section = self.create_stats_section(
			'💰 Estadísticas Económicas',
			[
				('total_coins', 'Monedas totales ganadas'),
				('current_coins', 'Monedas actuales'),
				('coins_spent', 'Monedas gastadas'),
				('highest_balance', 'Balance máximo'),
			]
		)
		parent.add_widget(section)
	
	def create_time_stats(self, parent: BoxLayout):
		"""Crea la sección de estadísticas de tiempo.
		
		Args:
			parent: Layout padre donde agregar la sección
		"""
		section = self.create_stats_section(
			'⏰ Estadísticas de Tiempo',
			[
				('total_playtime', 'Tiempo total jugado'),
				('longest_session', 'Sesión más larga'),
				('days_played', 'Días jugados'),
				('first_play', 'Primera partida'),
			]
		)
		parent.add_widget(section)
	
	def create_achievement_stats(self, parent: BoxLayout):
		"""Crea la sección de estadísticas de logros.
		
		Args:
			parent: Layout padre donde agregar la sección
		"""
		section = self.create_stats_section(
			'🏆 Logros y Bonificaciones',
			[
				('ads_watched', 'Anuncios vistos'),
				('bonuses_earned', 'Bonificaciones ganadas'),
				('upgrades_bought', 'Mejoras compradas'),
				('achievements_unlocked', 'Logros desbloqueados'),
			]
		)
		parent.add_widget(section)
	
	def create_stats_section(self, title: str, stats: list) -> BoxLayout:
		"""Crea una sección de estadísticas.
		
		Args:
			title: Título de la sección
			stats: Lista de tuplas (clave, nombre_mostrar)
			
		Returns:
			BoxLayout con la sección de estadísticas
		"""
		section = BoxLayout(
			orientation='vertical',
			size_hint=(1, None),
			spacing=10
		)
		section.bind(minimum_height=section.setter('height'))
		
		# Título de la sección
		title_label = Label(
			text=title,
			font_size='22sp',
			size_hint=(1, None),
			height='40dp',
			bold=True,
			color=[0.9, 0.9, 1, 1],
			halign='left',
			valign='center'
		)
		title_label.text_size = (400, None)
		section.add_widget(title_label)
		
		# Estadísticas individuales
		for stat_key, display_name in stats:
			stat_row = self.create_stat_row(stat_key, display_name)
			section.add_widget(stat_row)
		
		# Separador
		separator = Label(
			text='─' * 40,
			font_size='14sp',
			size_hint=(1, None),
			height='20dp',
			color=[0.4, 0.4, 0.4, 1]
		)
		section.add_widget(separator)
		
		return section
	
	def create_stat_row(self, stat_key: str, display_name: str) -> BoxLayout:
		"""Crea una fila de estadística individual.
		
		Args:
			stat_key: Clave de la estadística
			display_name: Nombre a mostrar
			
		Returns:
			BoxLayout con la fila de estadística
		"""
		row = BoxLayout(
			orientation='horizontal',
			size_hint=(1, None),
			height='35dp'
		)
		
		# Nombre de la estadística
		name_label = Label(
			text=display_name + ':',
			font_size='16sp',
			size_hint=(0.6, 1),
			halign='left',
			valign='center',
			color=[0.8, 0.8, 0.8, 1]
		)
		name_label.text_size = (None, None)
		row.add_widget(name_label)
		
		# Valor de la estadística
		value_label = Label(
			text=self.get_stat_value(stat_key),
			font_size='16sp',
			size_hint=(0.4, 1),
			halign='right',
			valign='center',
			color=[0.9, 0.9, 1, 1],
			bold=True
		)
		value_label.text_size = (None, None)
		row.add_widget(value_label)
		
		# Guardar referencia para actualización
		self.stats_labels[stat_key] = value_label
		
		return row
	
	def get_stat_value(self, stat_key: str) -> str:
		"""Obtiene el valor formateado de una estadística.
		
		Args:
			stat_key: Clave de la estadística
			
		Returns:
			Valor formateado como string
		"""
		# Obtener estadísticas del juego
		game_stats = self.game_state.get_game_stats()
		
		# Mapeo de estadísticas
		stat_mapping = {
			# Estadísticas de juego
			'total_clicks': game_stats.get('total_clicks', 0),
			'clicks_per_second': f"{game_stats.get('clicks_per_second', 0):.1f}",
			'highest_cps': f"{game_stats.get('highest_cps', 0):.1f}",
			'total_sessions': self.save_manager.get_stat('total_sessions', 1),
			
			# Estadísticas económicas
			'total_coins': self.format_number(game_stats.get('total_coins_earned', 0)),
			'current_coins': self.format_number(self.game_state.coins),
			'coins_spent': self.format_number(game_stats.get('total_coins_spent', 0)),
			'highest_balance': self.format_number(game_stats.get('highest_balance', 0)),
			
			# Estadísticas de tiempo
			'total_playtime': self.format_time(game_stats.get('total_playtime', 0)),
			'longest_session': self.format_time(game_stats.get('longest_session', 0)),
			'days_played': game_stats.get('days_played', 1),
			'first_play': 'Hoy',  # TODO: Implementar fecha real
			
			# Logros y bonificaciones
			'ads_watched': game_stats.get('ads_watched', 0),
			'bonuses_earned': game_stats.get('bonuses_earned', 0),
			'upgrades_bought': game_stats.get('upgrades_bought', 0),
			'achievements_unlocked': '0/50',  # TODO: Sistema de logros
		}
		
		return str(stat_mapping.get(stat_key, '---'))
	
	def format_number(self, number: int) -> str:
		"""Formatea un número grande con sufijos.
		
		Args:
			number: Número a formatear
			
		Returns:
			Número formateado con sufijos (K, M, B, etc.)
		"""
		if number < 1000:
			return str(number)
		elif number < 1000000:
			return f"{number/1000:.1f}K"
		elif number < 1000000000:
			return f"{number/1000000:.1f}M"
		elif number < 1000000000000:
			return f"{number/1000000000:.1f}B"
		else:
			return f"{number/1000000000000:.1f}T"
	
	def format_time(self, seconds: float) -> str:
		"""Formatea tiempo en segundos a formato legible.
		
		Args:
			seconds: Tiempo en segundos
			
		Returns:
			Tiempo formateado como string
		"""
		if seconds < 60:
			return f"{int(seconds)}s"
		elif seconds < 3600:
			minutes = int(seconds // 60)
			return f"{minutes}m"
		elif seconds < 86400:
			hours = int(seconds // 3600)
			minutes = int((seconds % 3600) // 60)
			return f"{hours}h {minutes}m"
		else:
			days = int(seconds // 86400)
			hours = int((seconds % 86400) // 3600)
			return f"{days}d {hours}h"
	
	def update_stats(self):
		"""Actualiza todas las estadísticas mostradas."""
		for stat_key, label in self.stats_labels.items():
			label.text = self.get_stat_value(stat_key)
		
		logging.debug("Estadísticas actualizadas")
	
	def on_back_button(self, instance: Button):
		"""Maneja el clic en el botón de volver.
		
		Args:
			instance: Instancia del botón presionado
		"""
		logging.info("Volviendo desde estadísticas")
		self.go_back()
	
	def on_enter(self, *args):
		"""Método llamado cuando se entra a la pantalla."""
		super().on_enter(*args)
		
		# Actualizar estadísticas al entrar
		self.update_stats()
		
		logging.info("Entrada a pantalla de estadísticas")
