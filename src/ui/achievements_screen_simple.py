"""
Pantalla de logros simplificada para SiKIdle.
Versión temporal que no depende de GameState.
"""

import logging
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button


class AchievementsScreen(Screen):
	"""Pantalla de logros simplificada."""
	
	def __init__(self, name='achievements', **kwargs):
		super().__init__(name=name, **kwargs)
		self._create_ui()
		logging.info("AchievementsScreen (simple) initialized")
	
	def _create_ui(self):
		"""Crea la interfaz simplificada."""
		main_layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
		
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
		status_label = Label(
			text="Sistema de logros en desarrollo...\n\nPronto podrás desbloquear logros\ny obtener recompensas especiales!\n\n🎯 Derrota enemigos\n🏆 Completa desafíos\n💎 Obtén recompensas",
			font_size='16sp',
			halign='center'
		)
		status_label.bind(texture_size=status_label.setter('text_size'))
		main_layout.add_widget(status_label)
		
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
	
	def on_close_button(self, instance):
		"""Maneja el clic en el botón de cerrar."""
		logging.info("Cerrando pantalla de logros")
		if self.manager:
			self.manager.current = 'home'
	
	def on_enter(self, *args):
		"""Se ejecuta cuando se entra a la pantalla."""
		logging.info("Entrando a pantalla de logros")
	
	def on_leave(self, *args):
		"""Se ejecuta cuando se sale de la pantalla."""
		logging.info("Saliendo de pantalla de logros")