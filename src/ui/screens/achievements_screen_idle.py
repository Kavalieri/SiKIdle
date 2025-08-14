"""
Pantalla de Achievements para Idle Clicker - SiKIdle.

Pantalla completa de logros con:
- Categorías organizadas (Idle, Combat, Prestigio, Especiales)
- Progreso visual con barras
- Recompensas detalladas
- Estadísticas de completado
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.progressbar import ProgressBar
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock

import logging
from core.achievements_idle import IdleAchievementCategory


class AchievementWidget(BoxLayout):
	"""Widget individual para mostrar un logro."""
	
	def __init__(self, achievement, **kwargs):
		super().__init__(**kwargs)
		self.achievement = achievement
		self.orientation = 'vertical'
		self.size_hint_y = None
		self.height = 120
		self.spacing = 4
		self.padding = [8, 8, 8, 8]
		
		self._setup_styling()
		self._build_content()
	
	def _setup_styling(self):
		"""Configura el estilo del widget."""
		from kivy.graphics import Color, RoundedRectangle
		
		with self.canvas.before:
			# Color según estado
			if self.achievement.completed:
				Color(0.2, 0.6, 0.2, 0.8)  # Verde si completado
			else:
				Color(0.3, 0.3, 0.35, 0.8)  # Gris si no completado
			
			self.bg_rect = RoundedRectangle(
				pos=self.pos,
				size=self.size,
				radius=[8, 8, 8, 8]
			)
		
		self.bind(pos=self._update_bg, size=self._update_bg)
	
	def _update_bg(self, *args):
		"""Actualiza el fondo del widget."""
		if hasattr(self, 'bg_rect'):
			self.bg_rect.pos = self.pos
			self.bg_rect.size = self.size
	
	def _build_content(self):
		"""Construye el contenido del widget."""
		# Header con icono y nombre
		header_layout = BoxLayout(
			orientation='horizontal',
			size_hint_y=None,
			height=30
		)
		
		# Icono y nombre
		icon_name_label = Label(
			text=f"{self.achievement.get_symbol()} {self.achievement.name}",
			font_size='16sp',
			bold=True,
			size_hint_x=0.7,
			halign='left',
			valign='center'
		)
		icon_name_label.bind(texture_size=icon_name_label.setter('text_size'))
		
		# Estado
		status_text = "✅ COMPLETADO" if self.achievement.completed else f"{self.achievement.current_progress}/{self.achievement.target_value}"
		status_label = Label(
			text=status_text,
			font_size='12sp',
			size_hint_x=0.3,
			halign='right',
			valign='center',
			color=(0.2, 0.8, 0.2, 1) if self.achievement.completed else (0.8, 0.8, 0.8, 1)
		)
		status_label.bind(texture_size=status_label.setter('text_size'))
		
		header_layout.add_widget(icon_name_label)
		header_layout.add_widget(status_label)
		
		# Descripción
		desc_label = Label(
			text=self.achievement.description,
			font_size='14sp',
			size_hint_y=None,
			height=25,
			halign='left',
			valign='center',
			color=(0.9, 0.9, 0.9, 1)
		)
		desc_label.bind(texture_size=desc_label.setter('text_size'))
		
		# Barra de progreso
		progress_bar = ProgressBar(
			max=100,
			value=self.achievement.get_progress_percentage(),
			size_hint_y=None,
			height=8
		)
		
		# Recompensas
		reward_text = self._format_rewards()
		reward_label = Label(
			text=reward_text,
			font_size='12sp',
			size_hint_y=None,
			height=25,
			halign='left',
			valign='center',
			color=(0.8, 0.6, 0.2, 1)  # Dorado para recompensas
		)
		reward_label.bind(texture_size=reward_label.setter('text_size'))
		
		# Ensamblar
		self.add_widget(header_layout)
		self.add_widget(desc_label)
		self.add_widget(progress_bar)
		self.add_widget(reward_label)
	
	def _format_rewards(self) -> str:
		"""Formatea las recompensas para mostrar."""
		reward = self.achievement.reward
		parts = []
		
		if reward.coins_reward > 0:
			parts.append(f"💰 {reward.coins_reward:,}")
		if reward.coins_multiplier > 0:
			parts.append(f"💰 +{reward.coins_multiplier:.1%}")
		if reward.click_multiplier > 0:
			parts.append(f"👆 +{reward.click_multiplier:.1%}")
		if reward.building_multiplier > 0:
			parts.append(f"🏭 +{reward.building_multiplier:.1%}")
		if reward.prestige_bonus > 0:
			parts.append(f"💎 +{reward.prestige_bonus:.1%}")
		
		return "🎁 " + " | ".join(parts) if parts else "🎁 Sin recompensas"


class CategorySection(BoxLayout):
	"""Sección de una categoría de logros."""
	
	def __init__(self, category, achievements, **kwargs):
		super().__init__(**kwargs)
		self.category = category
		self.achievements = achievements
		self.orientation = 'vertical'
		self.size_hint_y = None
		self.spacing = 8
		self.padding = [8, 8, 8, 8]
		
		self._build_section()
		self._calculate_height()
	
	def _build_section(self):
		"""Construye la sección de categoría."""
		# Título de categoría
		category_names = {
			IdleAchievementCategory.IDLE: "💰 Logros de Idle",
			IdleAchievementCategory.COMBAT: "⚔️ Logros de Combat",
			IdleAchievementCategory.PRESTIGE: "💎 Logros de Prestigio",
			IdleAchievementCategory.SPECIAL: "⭐ Logros Especiales"
		}
		
		title = Label(
			text=category_names.get(self.category, "🏆 Logros"),
			font_size='18sp',
			bold=True,
			size_hint_y=None,
			height=40,
			halign='left',
			valign='center'
		)
		title.bind(texture_size=title.setter('text_size'))
		
		# Estadísticas de la categoría
		completed = len([a for a in self.achievements if a.completed])
		total = len(self.achievements)
		percentage = (completed / total * 100) if total > 0 else 0
		
		stats_label = Label(
			text=f"Completados: {completed}/{total} ({percentage:.0f}%)",
			font_size='14sp',
			size_hint_y=None,
			height=25,
			halign='left',
			valign='center',
			color=(0.7, 0.7, 0.7, 1)
		)
		stats_label.bind(texture_size=stats_label.setter('text_size'))
		
		self.add_widget(title)
		self.add_widget(stats_label)
		
		# Añadir logros
		for achievement in self.achievements:
			achievement_widget = AchievementWidget(achievement)
			self.add_widget(achievement_widget)
	
	def _calculate_height(self):
		"""Calcula la altura total de la sección."""
		# Título + stats + logros + spacing + padding
		base_height = 40 + 25 + 16  # título + stats + padding
		achievements_height = len(self.achievements) * 120  # cada logro = 120px
		spacing_height = (len(self.achievements) + 1) * 8  # spacing
		
		self.height = base_height + achievements_height + spacing_height


class AchievementsScreenIdle(Screen):
	"""Pantalla de logros para idle clicker."""
	
	def __init__(self, name='achievements', **kwargs):
		super().__init__(name=name, **kwargs)
		
		self.game_state = None
		self.update_event = None
		
		self._build_layout()
		logging.info("AchievementsScreenIdle initialized")
	
	def _build_layout(self):
		"""Construye el layout principal."""
		main_layout = BoxLayout(orientation='vertical')
		
		# Header con estadísticas generales
		header = self._create_header()
		main_layout.add_widget(header)
		
		# Scroll con logros por categorías
		scroll = ScrollView()
		self.content_layout = BoxLayout(
			orientation='vertical',
			size_hint_y=None,
			spacing=16,
			padding=[16, 16, 16, 16]
		)
		self.content_layout.bind(minimum_height=self.content_layout.setter('height'))
		
		scroll.add_widget(self.content_layout)
		main_layout.add_widget(scroll)
		
		self.add_widget(main_layout)
	
	def _create_header(self) -> BoxLayout:
		"""Crea el header con estadísticas generales."""
		header = BoxLayout(
			orientation='vertical',
			size_hint_y=None,
			height=120,
			padding=[16, 16, 16, 16],
			spacing=8
		)
		
		# Título principal
		title = Label(
			text="🏆 SISTEMA DE LOGROS",
			font_size='24sp',
			bold=True,
			size_hint_y=None,
			height=40,
			color=(1, 0.8, 0, 1)  # Dorado
		)
		
		# Estadísticas generales
		self.stats_label = Label(
			text="Cargando estadísticas...",
			font_size='16sp',
			size_hint_y=None,
			height=30,
			color=(0.8, 0.8, 0.8, 1)
		)
		
		# Multiplicadores activos
		self.multipliers_label = Label(
			text="Cargando multiplicadores...",
			font_size='14sp',
			size_hint_y=None,
			height=25,
			color=(0.6, 0.8, 0.6, 1)  # Verde claro
		)
		
		header.add_widget(title)
		header.add_widget(self.stats_label)
		header.add_widget(self.multipliers_label)
		
		return header
	
	def _update_content(self):
		"""Actualiza el contenido de la pantalla."""
		if not self.game_state:
			return
		
		# Limpiar contenido anterior
		self.content_layout.clear_widgets()
		
		# Actualizar estadísticas del header
		self._update_header_stats()
		
		# Crear secciones por categoría
		categories = [
			IdleAchievementCategory.IDLE,
			IdleAchievementCategory.PRESTIGE,
			IdleAchievementCategory.SPECIAL
		]
		
		for category in categories:
			achievements = self.game_state.achievement_manager.get_achievements_by_category(category)
			if achievements:  # Solo mostrar categorías con logros
				section = CategorySection(category, achievements)
				self.content_layout.add_widget(section)
	
	def _update_header_stats(self):
		"""Actualiza las estadísticas del header."""
		if not self.game_state:
			return
		
		try:
			# Estadísticas generales
			stats = self.game_state.achievement_manager.get_completion_stats()
			self.stats_label.text = (
				f"Completados: {stats['completed_achievements']}/{stats['total_achievements']} "
				f"({stats['completion_percentage']:.1f}%)"
			)
			
			# Multiplicadores activos
			multipliers = self.game_state.achievement_manager.get_achievement_multipliers()
			multiplier_parts = []
			
			if multipliers['coins_multiplier'] > 1.0:
				bonus = (multipliers['coins_multiplier'] - 1.0) * 100
				multiplier_parts.append(f"💰 +{bonus:.0f}%")
			
			if multipliers['click_multiplier'] > 1.0:
				bonus = (multipliers['click_multiplier'] - 1.0) * 100
				multiplier_parts.append(f"👆 +{bonus:.0f}%")
			
			if multipliers['building_multiplier'] > 1.0:
				bonus = (multipliers['building_multiplier'] - 1.0) * 100
				multiplier_parts.append(f"🏭 +{bonus:.0f}%")
			
			if multipliers['prestige_bonus'] > 0:
				bonus = multipliers['prestige_bonus'] * 100
				multiplier_parts.append(f"💎 +{bonus:.0f}%")
			
			if multiplier_parts:
				self.multipliers_label.text = f"Bonificaciones activas: {' | '.join(multiplier_parts)}"
			else:
				self.multipliers_label.text = "Sin bonificaciones activas"
			
		except Exception as e:
			logging.error(f"Error updating header stats: {e}")
	
	def _update_header_stats_optimized(self, dt):
		"""Actualiza las estadísticas del header con optimizaciones."""
		if not self.game_state:
			return
		
		# Usar optimizador si está disponible
		performance_optimizer = getattr(self.game_state, 'performance_optimizer', None)
		if performance_optimizer and not performance_optimizer.should_update_ui('low'):
			return  # Saltar actualización si no es necesaria
		
		# Actualizar con el método original
		self._update_header_stats()
	
	def on_enter(self):
		"""Callback cuando se entra a la pantalla."""
		logging.info("Entered AchievementsScreenIdle")
		
		# Obtener referencia al game state
		try:
			from core.game import get_game_state
			self.game_state = get_game_state()
		except Exception as e:
			logging.error(f"Error getting game state: {e}")
		
		# Actualizar contenido
		self._update_content()
		
		# Programar actualizaciones periódicas optimizadas
		if not self.update_event:
			self.update_event = Clock.schedule_interval(self._update_header_stats_optimized, 0.5)
	
	def on_leave(self):
		"""Callback cuando se sale de la pantalla."""
		logging.info("Left AchievementsScreenIdle")
		
		# Cancelar actualizaciones
		if self.update_event:
			Clock.unschedule(self.update_event)
			self.update_event = None