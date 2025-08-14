"""
Pantalla de logros para SiKIdle - Sistema de UI completo.

Interfaz gráfica para visualizar y gestionar el progreso de logros
por categorías con animaciones y feedback visual.
"""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.progressbar import ProgressBar
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.popup import Popup
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.properties import ObjectProperty, StringProperty, NumericProperty, BooleanProperty
from kivy.graphics import Color, RoundedRectangle, Line
from kivy.uix.widget import Widget

from typing import Dict, List, Optional, Callable
from enum import Enum

from core.achievements import AchievementManager, AchievementCategory, Achievement


class AchievementFilterType(Enum):
	"""Tipos de filtros para logros."""
	ALL = "all"
	COMPLETED = "completed"
	IN_PROGRESS = "in_progress"
	LOCKED = "locked"


class CategoryColors:
	"""Colores temáticos por categoría de logros."""
	COMBAT = {
		'primary': (0.91, 0.30, 0.24, 1),    # #E74C3C
		'secondary': (0.75, 0.22, 0.17, 1),  # #C0392B
		'text': (1, 1, 1, 1)
	}
	EXPLORATION = {
		'primary': (0.15, 0.68, 0.38, 1),    # #27AE60
		'secondary': (0.13, 0.60, 0.33, 1),  # #229954
		'text': (1, 1, 1, 1)
	}
	LOOT = {
		'primary': (0.95, 0.61, 0.07, 1),    # #F39C12
		'secondary': (0.90, 0.49, 0.13, 1),  # #E67E22
		'text': (1, 1, 1, 1)
	}
	SURVIVAL = {
		'primary': (0.20, 0.60, 0.86, 1),    # #3498DB
		'secondary': (0.16, 0.50, 0.73, 1),  # #2980B9
		'text': (1, 1, 1, 1)
	}
	
	@classmethod
	def get_colors(cls, category: AchievementCategory) -> Dict:
		"""Obtiene los colores para una categoría específica."""
		return getattr(cls, category.name, cls.COMBAT)


class AchievementProgressBar(ProgressBar):
	"""Barra de progreso personalizada para logros."""
	
	category = ObjectProperty(None)
	
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.max = 100
		self.height = 8
		self.size_hint_y = None
		
	def on_category(self, instance, category):
		"""Actualiza los colores según la categoría."""
		if category:
			colors = CategoryColors.get_colors(category)
			with self.canvas.before:
				Color(*colors['secondary'])
				self.bg_rect = RoundedRectangle(
					pos=self.pos, 
					size=self.size, 
					radius=[4, 4, 4, 4]
				)
			
			with self.canvas.after:
				Color(*colors['primary'])
				self.progress_rect = RoundedRectangle(
					pos=self.pos,
					size=(self.size[0] * (self.value / self.max), self.size[1]),
					radius=[4, 4, 4, 4]
				)
	
	def animate_to_value(self, target_value: float, duration: float = 1.0):
		"""Anima la barra de progreso hasta el valor objetivo."""
		anim = Animation(value=target_value, duration=duration, t='out_expo')
		anim.start(self)


class AchievementCard(FloatLayout):
	"""Widget de tarjeta individual para un logro."""
	
	achievement = ObjectProperty(None)
	
	def __init__(self, achievement: Achievement, **kwargs):
		super().__init__(**kwargs)
		self.achievement = achievement
		self.size_hint_y = None
		self.height = 120
		
		self._build_ui()
		self._setup_colors()
		self._update_display()
	
	def _build_ui(self):
		"""Construye la interfaz de la tarjeta."""
		# Layout principal
		main_layout = BoxLayout(orientation='vertical', padding=16, spacing=8)
		
		# Header con título y estado
		header_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
		
		# Icono de categoría
		self.category_icon = Label(
			text=self._get_category_icon(),
			font_size='24sp',
			size_hint_x=None,
			width=40,
			halign='center'
		)
		
		# Información del logro
		info_layout = BoxLayout(orientation='vertical')
		
		self.title_label = Label(
			text=self.achievement.name,
			font_size='16sp',
			bold=True,
			halign='left',
			text_size=(None, None)
		)
		
		self.description_label = Label(
			text=self.achievement.description,
			font_size='12sp',
			halign='left',
			text_size=(None, None),
			opacity=0.8
		)
		
		# Estado del logro
		self.status_icon = Label(
			text=self._get_status_icon(),
			font_size='20sp',
			size_hint_x=None,
			width=40,
			halign='center'
		)
		
		# Progreso
		progress_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=20)
		
		self.progress_bar = AchievementProgressBar(category=self.achievement.category)
		
		self.progress_label = Label(
			text=self._get_progress_text(),
			font_size='12sp',
			size_hint_x=None,
			width=80,
			halign='center'
		)
		
		# Recompensas
		rewards_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=24)
		self.rewards_label = Label(
			text=self._get_rewards_text(),
			font_size='11sp',
			halign='left',
			text_size=(None, None),
			opacity=0.7
		)
		
		# Ensamblar layout
		info_layout.add_widget(self.title_label)
		info_layout.add_widget(self.description_label)
		
		header_layout.add_widget(self.category_icon)
		header_layout.add_widget(info_layout)
		header_layout.add_widget(self.status_icon)
		
		progress_layout.add_widget(self.progress_bar)
		progress_layout.add_widget(self.progress_label)
		
		rewards_layout.add_widget(self.rewards_label)
		
		main_layout.add_widget(header_layout)
		main_layout.add_widget(progress_layout)
		main_layout.add_widget(rewards_layout)
		
		self.add_widget(main_layout)
	
	def _setup_colors(self):
		"""Configura los colores según la categoría."""
		colors = CategoryColors.get_colors(self.achievement.category)
		
		with self.canvas.before:
			if self.achievement.completed:
				Color(*colors['primary'])
			else:
				Color(0.2, 0.2, 0.2, 1)  # Gris para incompletos
			
			self.bg_rect = RoundedRectangle(
				pos=self.pos,
				size=self.size,
				radius=[8, 8, 8, 8]
			)
		
		self.bind(pos=self._update_graphics, size=self._update_graphics)
	
	def _update_graphics(self, *args):
		"""Actualiza los gráficos cuando cambia la posición/tamaño."""
		if hasattr(self, 'bg_rect'):
			self.bg_rect.pos = self.pos
			self.bg_rect.size = self.size
	
	def _get_category_icon(self) -> str:
		"""Obtiene el icono según la categoría."""
		icons = {
			AchievementCategory.COMBAT: "⚔️",
			AchievementCategory.EXPLORATION: "🗺️",
			AchievementCategory.LOOT: "💎",
			AchievementCategory.SURVIVAL: "🛡️"
		}
		return icons.get(self.achievement.category, "🏆")
	
	def _get_status_icon(self) -> str:
		"""Obtiene el icono de estado del logro."""
		if self.achievement.completed:
			return "✅"
		elif self.achievement.current_progress > 0:
			return "⚡"
		else:
			return "🔒"
	
	def _get_progress_text(self) -> str:
		"""Obtiene el texto de progreso."""
		current = self.achievement.current_progress
		target = self.achievement.target_value
		percentage = self.achievement.progress_percentage
		
		return f"{current}/{target}\n({percentage:.1f}%)"
	
	def _get_rewards_text(self) -> str:
		"""Obtiene el texto de recompensas."""
		if not self.achievement.reward:
			return "Sin recompensas"
		
		reward = self.achievement.reward
		parts = []
		
		# Recompensas de gemas
		if hasattr(reward, 'gems_reward') and reward.gems_reward > 0:
			parts.append(f"💎 {reward.gems_reward} Gemas")
		
		# Recompensas de monedas
		if hasattr(reward, 'coins_reward') and reward.coins_reward > 0:
			parts.append(f"💰 {reward.coins_reward} Monedas")
		
		# Multiplicadores permanentes
		if hasattr(reward, 'coins_multiplier') and reward.coins_multiplier > 0:
			parts.append(f"📈 +{reward.coins_multiplier*100:.0f}% Monedas")
		
		if hasattr(reward, 'click_multiplier') and reward.click_multiplier > 0:
			parts.append(f"👆 +{reward.click_multiplier*100:.0f}% Clic")
		
		if hasattr(reward, 'building_multiplier') and reward.building_multiplier > 0:
			parts.append(f"🏭 +{reward.building_multiplier*100:.0f}% Edificios")
		
		if hasattr(reward, 'prestige_bonus') and reward.prestige_bonus > 0:
			parts.append(f"⭐ +{reward.prestige_bonus*100:.0f}% Prestigio")
		
		return " • ".join(parts) if parts else "Sin recompensas"
	
	def _update_display(self):
		"""Actualiza la visualización del progreso."""
		# Actualizar barra de progreso
		self.progress_bar.animate_to_value(self.achievement.progress_percentage)
		
		# Actualizar textos
		self.progress_label.text = self._get_progress_text()
		self.status_icon.text = self._get_status_icon()
	
	def play_completion_animation(self):
		"""Reproduce animación de logro completado."""
		if not self.achievement.completed:
			return
		
		# Animación de escala
		scale_anim = Animation(
			size=(self.width * 1.05, self.height * 1.05),
			duration=0.3,
			t='out_expo'
		) + Animation(
			size=(self.width, self.height),
			duration=0.3,
			t='in_expo'
		)
		
		scale_anim.start(self)
		
		# Cambiar colores a completado
		self._setup_colors()


class CategoryTabButton(Button):
	"""Botón de pestaña para categorías de logros."""
	
	category = ObjectProperty(None)
	is_active = BooleanProperty(False)
	
	def __init__(self, category: AchievementCategory, **kwargs):
		super().__init__(**kwargs)
		self.category = category
		self.text = self._get_category_text()
		self.size_hint_x = None
		self.width = 120
		self.height = 40
		
		self._setup_colors()
	
	def _get_category_text(self) -> str:
		"""Obtiene el texto del botón según la categoría."""
		texts = {
			AchievementCategory.COMBAT: "⚔️ Combate",
			AchievementCategory.EXPLORATION: "🗺️ Exploración", 
			AchievementCategory.LOOT: "💎 Loot",
			AchievementCategory.SURVIVAL: "🛡️ Supervivencia"
		}
		return texts.get(self.category, "🏆 General")
	
	def _setup_colors(self):
		"""Configura los colores del botón."""
		colors = CategoryColors.get_colors(self.category)
		
		if self.is_active:
			self.background_color = colors['primary']
		else:
			self.background_color = (0.3, 0.3, 0.3, 1)
	
	def on_is_active(self, instance, is_active):
		"""Actualiza colores cuando cambia el estado activo."""
		self._setup_colors()


class AchievementScreen(BoxLayout):
	"""Pantalla principal del sistema de logros."""
	
	def __init__(self, achievement_manager: AchievementManager, **kwargs):
		super().__init__(**kwargs)
		self.achievement_manager = achievement_manager
		self.orientation = 'vertical'
		self.padding = 16
		self.spacing = 16
		
		self.current_category = AchievementCategory.COMBAT
		self.current_filter = AchievementFilterType.ALL
		
		self._build_ui()
		self._load_achievements()
		
		# Suscribirse a completaciones de logros
		self.achievement_manager.add_completion_callback(self._on_achievement_completed)
	
	def _build_ui(self):
		"""Construye la interfaz principal."""
		# Header
		header_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=100)
		
		# Título
		title_label = Label(
			text="🏆 Sistema de Logros",
			font_size='24sp',
			bold=True,
			size_hint_y=None,
			height=40
		)
		
		# Navegación por categorías
		self.category_tabs = BoxLayout(orientation='horizontal', size_hint_y=None, height=50)
		
		self.tab_buttons = {}
		for category in AchievementCategory:
			btn = CategoryTabButton(category)
			btn.bind(on_press=lambda x, cat=category: self._switch_category(cat))
			self.tab_buttons[category] = btn
			self.category_tabs.add_widget(btn)
		
		# Activar primera pestaña
		self.tab_buttons[self.current_category].is_active = True
		
		# Filtros
		filter_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
		
		self.filter_buttons = {}
		filter_texts = {
			AchievementFilterType.ALL: "Todos",
			AchievementFilterType.COMPLETED: "Completados", 
			AchievementFilterType.IN_PROGRESS: "En Progreso",
			AchievementFilterType.LOCKED: "Bloqueados"
		}
		
		for filter_type, text in filter_texts.items():
			btn = Button(text=text, size_hint_x=None, width=100)
			btn.bind(on_press=lambda x, ft=filter_type: self._switch_filter(ft))
			self.filter_buttons[filter_type] = btn
			filter_layout.add_widget(btn)
		
		# Lista de logros con scroll
		self.scroll_view = ScrollView()
		self.achievements_container = GridLayout(
			cols=1,
			spacing=8,
			size_hint_y=None,
			padding=8
		)
		self.achievements_container.bind(minimum_height=self.achievements_container.setter('height'))
		
		self.scroll_view.add_widget(self.achievements_container)
		
		# Ensamblar header
		header_layout.add_widget(title_label)
		header_layout.add_widget(self.category_tabs)
		header_layout.add_widget(filter_layout)
		
		# Ensamblar pantalla principal
		self.add_widget(header_layout)
		self.add_widget(self.scroll_view)
	
	def _switch_category(self, category: AchievementCategory):
		"""Cambia la categoría activa."""
		# Desactivar botón anterior
		self.tab_buttons[self.current_category].is_active = False
		
		# Activar nuevo botón
		self.current_category = category
		self.tab_buttons[category].is_active = True
		
		# Recargar logros
		self._load_achievements()
	
	def _switch_filter(self, filter_type: AchievementFilterType):
		"""Cambia el filtro activo."""
		self.current_filter = filter_type
		
		# Actualizar colores de botones de filtro
		for ft, btn in self.filter_buttons.items():
			if ft == filter_type:
				btn.background_color = (0.2, 0.6, 0.9, 1)
			else:
				btn.background_color = (0.3, 0.3, 0.3, 1)
		
		# Recargar logros
		self._load_achievements()
	
	def _load_achievements(self):
		"""Carga y muestra los logros filtrados."""
		# Limpiar contenedor
		self.achievements_container.clear_widgets()
		
		# Obtener logros de la categoría actual
		category_achievements = self.achievement_manager.get_achievements_by_category(self.current_category)
		
		# Aplicar filtro
		filtered_achievements = self._apply_filter(category_achievements)
		
		# Crear cards para cada logro
		for achievement in filtered_achievements:
			card = AchievementCard(achievement)
			self.achievements_container.add_widget(card)
	
	def _apply_filter(self, achievements: List[Achievement]) -> List[Achievement]:
		"""Aplica el filtro actual a la lista de logros."""
		if self.current_filter == AchievementFilterType.ALL:
			return achievements
		elif self.current_filter == AchievementFilterType.COMPLETED:
			return [a for a in achievements if a.completed]
		elif self.current_filter == AchievementFilterType.IN_PROGRESS:
			return [a for a in achievements if a.current_progress > 0 and not a.completed]
		elif self.current_filter == AchievementFilterType.LOCKED:
			return [a for a in achievements if a.current_progress == 0]
		
		return achievements
	
	def _on_achievement_completed(self, achievement: Achievement):
		"""Callback ejecutado cuando se completa un logro."""
		# Mostrar notificación
		self._show_completion_notification(achievement)
		
		# Recargar vista si es necesario
		if achievement.category == self.current_category:
			self._load_achievements()
	
	def _show_completion_notification(self, achievement: Achievement):
		"""Muestra notificación de logro completado."""
		content = BoxLayout(orientation='vertical', spacing=10, padding=20)
		
		# Título
		title = Label(
			text=f"🏆 ¡Logro Desbloqueado!",
			font_size='20sp',
			bold=True,
			size_hint_y=None,
			height=40
		)
		
		# Información del logro
		info = Label(
			text=f"{achievement.name}\n{achievement.description}",
			font_size='16sp',
			halign='center',
			text_size=(300, None)
		)
		
		# Recompensas
		if achievement.reward:
			reward_text = f"Recompensas:\n"
			
			# Gemas
			if hasattr(achievement.reward, 'gems_reward') and achievement.reward.gems_reward > 0:
				reward_text += f"💎 {achievement.reward.gems_reward} Gemas\n"
			
			# Monedas
			if hasattr(achievement.reward, 'coins_reward') and achievement.reward.coins_reward > 0:
				reward_text += f"💰 {achievement.reward.coins_reward} Monedas\n"
			
			# Multiplicadores
			if hasattr(achievement.reward, 'coins_multiplier') and achievement.reward.coins_multiplier > 0:
				reward_text += f"📈 +{achievement.reward.coins_multiplier*100:.0f}% Multiplicador Monedas\n"
			
			if hasattr(achievement.reward, 'click_multiplier') and achievement.reward.click_multiplier > 0:
				reward_text += f"👆 +{achievement.reward.click_multiplier*100:.0f}% Multiplicador Clic\n"
			
			rewards = Label(
				text=reward_text,
				font_size='14sp',
				halign='center',
				text_size=(300, None)
			)
			content.add_widget(rewards)
		
		# Botón cerrar
		close_btn = Button(
			text="¡Genial!",
			size_hint_y=None,
			height=40
		)
		
		content.add_widget(title)
		content.add_widget(info)
		content.add_widget(close_btn)
		
		# Crear popup
		popup = Popup(
			title="",
			content=content,
			size_hint=(0.8, 0.6),
			auto_dismiss=False
		)
		
		close_btn.bind(on_press=popup.dismiss)
		popup.open()
	
	def refresh_display(self):
		"""Actualiza toda la visualización."""
		self._load_achievements()
	
	def get_category_progress_summary(self, category: AchievementCategory) -> Dict:
		"""Obtiene resumen de progreso para una categoría."""
		achievements = self.achievement_manager.get_achievements_by_category(category)
		total = len(achievements)
		completed = len([a for a in achievements if a.completed])
		
		return {
			'total': total,
			'completed': completed,
			'percentage': (completed / total * 100) if total > 0 else 0
		}
