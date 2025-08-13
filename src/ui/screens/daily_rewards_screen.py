"""
Pantalla de Daily Rewards y Metas Diarias para SiKIdle.

Interfaz simple para:
- Reclamar recompensas diarias
- Ver progreso de metas diarias
- Mostrar racha actual
"""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.progressbar import ProgressBar
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.clock import Clock
import logging


class DailyRewardsScreen(BoxLayout):
	"""Pantalla de recompensas diarias."""
	
	def __init__(self, game_state, **kwargs):
		super().__init__(**kwargs)
		self.game_state = game_state
		self.orientation = 'vertical'
		self.padding = 16
		self.spacing = 12
		
		self._build_ui()
		self._update_display()
		
		# Actualizar cada 30 segundos
		Clock.schedule_interval(self._update_display, 30.0)
	
	def _build_ui(self):
		"""Construye la interfaz."""
		# Título
		title = Label(
			text="🎁 Recompensas Diarias",
			font_size='20sp',
			bold=True,
			size_hint_y=None,
			height=40
		)
		
		# Racha actual
		self.streak_label = Label(
			text="",
			font_size='16sp',
			size_hint_y=None,
			height=30
		)
		
		# Scroll para recompensas
		scroll = ScrollView()
		self.rewards_container = GridLayout(
			cols=1,
			spacing=8,
			size_hint_y=None,
			padding=8
		)
		self.rewards_container.bind(minimum_height=self.rewards_container.setter('height'))
		scroll.add_widget(self.rewards_container)
		
		# Metas diarias
		goals_title = Label(
			text="🎯 Metas Diarias",
			font_size='18sp',
			bold=True,
			size_hint_y=None,
			height=35
		)
		
		self.goals_container = GridLayout(
			cols=1,
			spacing=6,
			size_hint_y=None,
			height=200
		)
		
		self.add_widget(title)
		self.add_widget(self.streak_label)
		self.add_widget(scroll)
		self.add_widget(goals_title)
		self.add_widget(self.goals_container)
	
	def _update_display(self, dt=None):
		"""Actualiza la visualización."""
		if not hasattr(self.game_state, 'engagement_system'):
			return
		
		engagement = self.game_state.engagement_system
		
		# Actualizar racha
		self.streak_label.text = f"🔥 Racha actual: {engagement.current_streak} días"
		
		# Actualizar recompensas diarias
		self._update_daily_rewards()
		
		# Actualizar metas diarias
		self._update_daily_goals()
	
	def _update_daily_rewards(self):
		"""Actualiza las recompensas diarias."""
		self.rewards_container.clear_widgets()
		
		engagement = self.game_state.engagement_system
		
		# Mostrar hasta 7 días de recompensas
		for day in range(1, 8):
			reward_widget = self._create_reward_widget(day)
			self.rewards_container.add_widget(reward_widget)
	
	def _create_reward_widget(self, day):
		"""Crea widget para una recompensa diaria."""
		engagement = self.game_state.engagement_system
		can_claim = engagement.can_claim_daily_reward(day)
		
		# Obtener recompensa del ciclo
		reward_index = (day - 1) % len(engagement.daily_reward_cycle)
		reward = engagement.daily_reward_cycle[reward_index]
		
		# Layout horizontal
		layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50)
		
		# Día
		day_label = Label(
			text=f"Día {day}",
			size_hint_x=None,
			width=60,
			font_size='14sp'
		)
		
		# Descripción de recompensa
		reward_text = self._get_reward_text(reward)
		reward_label = Label(
			text=reward_text,
			font_size='12sp',
			halign='left',
			text_size=(200, None)
		)
		
		# Botón o estado
		if day <= engagement.current_streak:
			if can_claim:
				btn = Button(
					text="Reclamar",
					size_hint_x=None,
					width=80,
					background_color=(0.2, 0.8, 0.2, 1)
				)
				btn.bind(on_press=lambda x, d=day: self._claim_reward(d))
			else:
				btn = Label(
					text="✅",
					size_hint_x=None,
					width=80,
					font_size='20sp'
				)
		else:
			btn = Label(
				text="🔒",
				size_hint_x=None,
				width=80,
				font_size='20sp',
				opacity=0.5
			)
		
		layout.add_widget(day_label)
		layout.add_widget(reward_label)
		layout.add_widget(btn)
		
		return layout
	
	def _get_reward_text(self, reward):
		"""Obtiene texto descriptivo de la recompensa."""
		if reward.reward_type.value == "coins":
			return f"💰 {reward.amount} Monedas"
		elif reward.reward_type.value == "gems":
			return f"💎 {reward.amount} Gemas"
		elif reward.reward_type.value == "multiplier":
			return f"📈 {reward.amount}x Monedas ({reward.duration_minutes}min)"
		elif reward.reward_type.value == "boost":
			return f"🚀 {reward.amount}x Mega Boost ({reward.duration_minutes}min)"
		return "🎁 Recompensa especial"
	
	def _claim_reward(self, day):
		"""Reclama una recompensa diaria."""
		engagement = self.game_state.engagement_system
		reward = engagement.claim_daily_reward(day)
		
		if reward:
			# Mostrar notificación
			self._show_reward_notification(reward)
			# Actualizar display
			self._update_display()
		else:
			logging.warning(f"No se pudo reclamar recompensa del día {day}")
	
	def _show_reward_notification(self, reward):
		"""Muestra notificación de recompensa reclamada."""
		# Animación simple con el animation manager
		if hasattr(self.game_state, 'animation_manager'):
			# Aquí se podría añadir una animación de recompensa
			pass
		
		logging.info(f"Daily reward claimed: {reward.reward_type.value} x{reward.amount}")
	
	def _update_daily_goals(self):
		"""Actualiza las metas diarias."""
		self.goals_container.clear_widgets()
		
		if not hasattr(self.game_state, 'engagement_system'):
			return
		
		engagement = self.game_state.engagement_system
		
		for goal in engagement.daily_goals.values():
			goal_widget = self._create_goal_widget(goal)
			self.goals_container.add_widget(goal_widget)
	
	def _create_goal_widget(self, goal):
		"""Crea widget para una meta diaria."""
		layout = BoxLayout(orientation='vertical', size_hint_y=None, height=60)
		
		# Header con nombre y estado
		header = BoxLayout(orientation='horizontal', size_hint_y=None, height=25)
		
		name_label = Label(
			text=goal.name,
			font_size='14sp',
			bold=True,
			halign='left',
			text_size=(200, None)
		)
		
		status_icon = Label(
			text="✅" if goal.completed else "⏳",
			size_hint_x=None,
			width=30,
			font_size='16sp'
		)
		
		header.add_widget(name_label)
		header.add_widget(status_icon)
		
		# Progreso
		progress_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=20)
		
		progress_bar = ProgressBar(
			max=goal.target_value,
			value=goal.current_progress,
			size_hint_x=0.7
		)
		
		progress_text = Label(
			text=f"{goal.current_progress}/{goal.target_value}",
			size_hint_x=0.3,
			font_size='12sp'
		)
		
		progress_layout.add_widget(progress_bar)
		progress_layout.add_widget(progress_text)
		
		# Recompensas
		reward_text = f"🎁 {goal.reward_coins} monedas"
		if goal.reward_gems > 0:
			reward_text += f", {goal.reward_gems} gemas"
		
		reward_label = Label(
			text=reward_text,
			font_size='11sp',
			size_hint_y=None,
			height=15,
			opacity=0.8
		)
		
		layout.add_widget(header)
		layout.add_widget(progress_layout)
		layout.add_widget(reward_label)
		
		return layout