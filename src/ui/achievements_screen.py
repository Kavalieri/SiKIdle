"""
Pantalla de logros para el juego SiKIdle.

Esta pantalla permite a los jugadores:
- Ver todos los logros disponibles organizados por categoría
- Revisar su progreso en logros no completados
- Ver las recompensas obtenidas por logros desbloqueados
- Filtrar logros por estado (completados, en progreso, ocultos)
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
from kivy.uix.progressbar import ProgressBar  # type: ignore

from core.game import get_game_state, GameState
from core.achievements import AchievementCategory, Achievement
from kivy.uix.screenmanager import Screen


class AchievementWidget(BoxLayout):
	"""Widget personalizado para mostrar información de un logro."""
	
	def __init__(self, achievement: Achievement, **kwargs: Any):
		super().__init__(**kwargs)
		self.orientation = 'horizontal'
		self.size_hint_y = None
		self.height = 80
		self.spacing = 10
		
		self.achievement = achievement
		
		self._create_widget()
	
	def _create_widget(self):
		"""Crea los elementos visuales del widget de logro."""
		# Icono del logro
		icon_label = Label(
			text=self.achievement.get_symbol(),
			size_hint_x=None,
			width=60,
			font_size='24sp',
			halign='center',
			valign='middle'
		)
		icon_label.text_size = (icon_label.width, None)
		
		# Información del logro
		info_layout = BoxLayout(orientation='vertical', size_hint_x=0.6)
		
		# Nombre del logro
		name_color = [0, 1, 0, 1] if self.achievement.completed else [1, 1, 1, 1]
		name_label = Label(
			text=self.achievement.name,
			size_hint_y=None,
			height=30,
			font_size='16sp',
			color=name_color,
			halign='left',
			valign='middle'
		)
		name_label.text_size = (name_label.width, name_label.height)
		
		# Descripción del logro
		description_label = Label(
			text=self.achievement.description,
			size_hint_y=None,
			height=25,
			font_size='12sp',
			color=[0.8, 0.8, 0.8, 1],
			halign='left',
			valign='middle'
		)
		description_label.text_size = (description_label.width, description_label.height)
		
		info_layout.add_widget(name_label)
		info_layout.add_widget(description_label)
		
		# Progreso o estado
		progress_layout = BoxLayout(orientation='vertical', size_hint_x=0.3)
		
		if self.achievement.completed:
			# Logro completado
			status_label = Label(
				text="✅ COMPLETADO",
				size_hint_y=None,
				height=30,
				font_size='14sp',
				color=[0, 1, 0, 1],
				halign='center',
				valign='middle'
			)
			status_label.text_size = (status_label.width, status_label.height)
			
			# Recompensa obtenida
			reward_text = f"💰 {self.achievement.reward.talent_points} pts"
			reward_label = Label(
				text=reward_text,
				size_hint_y=None,
				height=25,
				font_size='12sp',
				color=[1, 0.8, 0, 1],
				halign='center',
				valign='middle'
			)
			reward_label.text_size = (reward_label.width, reward_label.height)
			
			progress_layout.add_widget(status_label)
			progress_layout.add_widget(reward_label)
		else:
			# Progreso del logro
			progress_pct = self.achievement.get_progress_percentage() / 100.0
			progress_text = f"{self.achievement.current_progress:,.0f}/{self.achievement.target_value:,.0f}"
			
			progress_label = Label(
				text=progress_text,
				size_hint_y=None,
				height=20,
				font_size='12sp',
				color=[0.9, 0.9, 0.9, 1],
				halign='center',
				valign='middle'
			)
			progress_label.text_size = (progress_label.width, progress_label.height)
			
			progress_bar = ProgressBar(
				max=1.0,
				value=progress_pct,
				size_hint_y=None,
				height=15
			)
			
			percentage_label = Label(
				text=f"{progress_pct*100:.1f}%",
				size_hint_y=None,
				height=20,
				font_size='10sp',
				color=[0.7, 0.7, 0.7, 1],
				halign='center',
				valign='middle'
			)
			percentage_label.text_size = (percentage_label.width, percentage_label.height)
			
			progress_layout.add_widget(progress_label)
			progress_layout.add_widget(progress_bar)
			progress_layout.add_widget(percentage_label)
		
		# Agregar todos los elementos al layout principal
		self.add_widget(icon_label)
		self.add_widget(info_layout)
		self.add_widget(progress_layout)


class AchievementsScreen(Screen):
	"""Pantalla de logros del juego."""
	
	def __init__(self, name='achievements', **kwargs: Any):
		super().__init__(name=name, **kwargs)
		try:
			self.game_state: GameState = get_game_state()
		except Exception as e:
			logging.error(f"Error getting game state: {e}")
			self.game_state = None
		self.update_event = None
		
		# Crear la interfaz principal
		self._create_ui()
		
		logging.info("Pantalla de logros creada exitosamente")
	
	def _create_ui(self):
		"""Crea la interfaz principal de logros."""
		main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
		
		# Título
		title_label = Label(
			text="🏆 SISTEMA DE LOGROS",
			font_size='24sp',
			bold=True,
			size_hint_y=None,
			height=60,
			color=[1, 0.8, 0, 1]
		)
		main_layout.add_widget(title_label)
		
		# Mensaje de estado
		if self.game_state is None:
			status_label = Label(
				text="Sistema de logros en desarrollo...\n\nPronto podrás desbloquear logros\ny obtener recompensas especiales!",
				font_size='16sp',
				halign='center'
			)
			status_label.bind(texture_size=status_label.setter('text_size'))
			main_layout.add_widget(status_label)
		else:
			# Header con estadísticas generales
			header = self._create_header()
			main_layout.add_widget(header)
			
			# Panel de pestañas por categorías
			tabs_panel = self._create_tabs_panel()
			main_layout.add_widget(tabs_panel)
		
		# Botón de cerrar
		close_button = Button(
			text="🔙 Volver",
			size_hint_y=None,
			height=50,
			font_size='16sp'
		)
		close_button.bind(on_press=self.on_close_button)
		main_layout.add_widget(close_button)
		
		self.add_widget(main_layout)
	
	def _create_header(self) -> BoxLayout:
		"""Crea el header con estadísticas generales."""
		header = BoxLayout(orientation='horizontal', size_hint_y=None, height=60, spacing=10)
		
		# Título
		title_label = Label(
			text="🏆 LOGROS",
			size_hint_x=0.4,
			font_size='24sp',
			color=[1, 0.8, 0, 1],
			halign='center',
			valign='middle'
		)
		title_label.text_size = (title_label.width, title_label.height)
		
		# Estadísticas
		if self.game_state and hasattr(self.game_state, 'achievement_manager'):
			completed_achievements = self.game_state.achievement_manager.get_completed_achievements()
			all_achievements = self.game_state.achievement_manager.get_all_achievements()
			unlocked_count = len(completed_achievements)
			total_count = len(all_achievements)
			completion_pct = (unlocked_count / total_count * 100) if total_count > 0 else 0
		else:
			unlocked_count = 0
			total_count = 0
			completion_pct = 0
		
		stats_label = Label(
			text=f"Completado: {unlocked_count}/{total_count} ({completion_pct:.1f}%)",
			size_hint_x=0.6,
			font_size='16sp',
			color=[0.9, 0.9, 0.9, 1],
			halign='center',
			valign='middle'
		)
		stats_label.text_size = (stats_label.width, stats_label.height)
		
		header.add_widget(title_label)
		header.add_widget(stats_label)
		
		return header
	
	def _create_tabs_panel(self) -> TabbedPanel:
		"""Crea el panel de pestañas con categorías de logros."""
		tabs_panel = TabbedPanel(do_default_tab=False)
		
		# Pestaña de Combate
		combat_tab = TabbedPanelItem(text='⚔️ Combate')
		combat_content = self._create_category_content(AchievementCategory.COMBAT)
		combat_tab.add_widget(combat_content)
		tabs_panel.add_widget(combat_tab)
		
		# Pestaña de Exploración
		exploration_tab = TabbedPanelItem(text='🗺️ Exploración')
		exploration_content = self._create_category_content(AchievementCategory.EXPLORATION)
		exploration_tab.add_widget(exploration_content)
		tabs_panel.add_widget(exploration_tab)
		
		# Pestaña de Loot
		loot_tab = TabbedPanelItem(text='💰 Loot')
		loot_content = self._create_category_content(AchievementCategory.LOOT)
		loot_tab.add_widget(loot_content)
		tabs_panel.add_widget(loot_tab)
		
		# Pestaña de Especiales
		special_tab = TabbedPanelItem(text='⭐ Especiales')
		special_content = self._create_category_content(AchievementCategory.SPECIAL)
		special_tab.add_widget(special_content)
		tabs_panel.add_widget(special_tab)
		
		return tabs_panel
	
	def _create_category_content(self, category: AchievementCategory) -> ScrollView:
		"""Crea el contenido de una categoría de logros."""
		# Layout principal scrolleable
		scroll_view = ScrollView()
		content_layout = BoxLayout(orientation='vertical', spacing=5, size_hint_y=None)
		content_layout.bind(minimum_height=content_layout.setter('height'))
		
		# Obtener logros de esta categoría
		if self.game_state and hasattr(self.game_state, 'achievement_manager'):
			achievements_in_category = self.game_state.achievement_manager.get_achievements_by_category(category)
		else:
			achievements_in_category = []
		
		if not achievements_in_category:
			# Sin logros en esta categoría
			no_achievements_label = Label(
				text=f"No hay logros en la categoría {category.value}",
				size_hint_y=None,
				height=100,
				font_size='16sp',
				color=[0.6, 0.6, 0.6, 1],
				halign='center',
				valign='middle'
			)
			no_achievements_label.text_size = (no_achievements_label.width, no_achievements_label.height)
			content_layout.add_widget(no_achievements_label)
		else:
			# Agregar widgets de logros
			for achievement in achievements_in_category:
				achievement_widget = AchievementWidget(achievement)
				content_layout.add_widget(achievement_widget)
		
		scroll_view.add_widget(content_layout)
		return scroll_view
	
	def update_ui(self, dt: float = 0):
		"""Actualiza la interfaz con los datos actuales."""
		try:
			# Recrear la interfaz para reflejar cambios en logros
			self.clear_widgets()
			self._create_ui()
			
			logging.debug("UI de logros actualizada")
		except Exception as e:
			logging.error(f"Error actualizando UI de logros: {e}")
	
	def on_close_button(self, instance):
		"""Maneja el clic en el botón de cerrar."""
		logging.info("Cerrando pantalla de logros")
		if self.manager:
			self.manager.current = 'home'
	
	def on_enter(self, *args):
		"""Se ejecuta cuando se entra a la pantalla."""
		logging.info("Entrando a pantalla de logros")
		
		# Actualizar UI inmediatamente
		self.update_ui()
		
		# Programar actualizaciones periódicas (menos frecuentes)
		if not self.update_event:
			self.update_event = Clock.schedule_interval(self.update_ui, 5.0)  # Cada 5 segundos
	
	def on_leave(self, *args):
		"""Se ejecuta cuando se sale de la pantalla."""
		logging.info("Saliendo de pantalla de logros")
		
		# Cancelar actualizaciones periódicas
		if self.update_event:
			Clock.unschedule(self.update_event)
			self.update_event = None
