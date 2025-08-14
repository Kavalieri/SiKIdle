"""
UI del Sistema de Talentos para SiKIdle.

Este módulo proporciona la interfaz visual para la gestión del árbol de talentos,
permitiendo a los jugadores ver, desbloquear y gestionar sus especializaciones de combate.
"""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.graphics import Color, RoundedRectangle
from typing import Optional, Dict, List

from src.core.talents import TalentManager, TalentBranch, TalentType, TalentInfo


class TalentCard(BoxLayout):
	"""
	Widget individual para mostrar un talento específico.
	
	Muestra información del talento, estado actual y permite upgrades.
	"""
	
	def __init__(self, talent_type: TalentType, talent_manager: TalentManager, **kwargs):
		super().__init__(**kwargs)
		self.orientation = 'vertical'
		self.size_hint_y = None
		self.height = 120
		self.spacing = 5
		self.padding = [10, 5]
		
		self.talent_type = talent_type
		self.talent_manager = talent_manager
		self.talent_info = talent_manager.talent_info[talent_type]
		
		# Obtener nivel actual del talento
		self.current_level = talent_manager.get_talent_level(talent_type)
		self.can_upgrade = talent_manager.can_upgrade_talent(talent_type)
		
		self._setup_visual_style()
		self._create_widgets()
		self._update_visual_state()
	
	def _setup_visual_style(self):
		"""Configura el estilo visual del card según el estado del talento."""
		with self.canvas.before:
			self.color_instruction = Color()
			self.rect_instruction = RoundedRectangle(
				pos=self.pos,
				size=self.size,
				radius=[8]
			)
		
		self.bind(pos=self._update_graphics, size=self._update_graphics)
	
	def _update_graphics(self, *args):
		"""Actualiza las instrucciones gráficas cuando cambia posición/tamaño."""
		self.rect_instruction.pos = self.pos
		self.rect_instruction.size = self.size
	
	def _create_widgets(self):
		"""Crea los widgets internos del card."""
		# Header con nombre y nivel
		header_layout = BoxLayout(orientation='horizontal', size_hint_y=0.3)
		
		# Emoji e información básica
		self.name_label = Label(
			text=f"{self.talent_info.emoji} {self.talent_info.name}",
			font_size='14sp',
			bold=True,
			text_size=(None, None),
			halign='left'
		)
		header_layout.add_widget(self.name_label)
		
		# Nivel actual
		self.level_label = Label(
			text=f"Nv. {self.current_level}/{self.talent_info.max_level}",
			font_size='12sp',
			size_hint_x=0.3,
			halign='right'
		)
		header_layout.add_widget(self.level_label)
		
		self.add_widget(header_layout)
		
		# Descripción del talento
		self.description_label = Label(
			text=self.talent_info.description,
			font_size='11sp',
			text_size=(None, None),
			halign='left',
			valign='top',
			size_hint_y=0.4
		)
		self.add_widget(self.description_label)
		
		# Footer con botón de upgrade y costo
		footer_layout = BoxLayout(orientation='horizontal', size_hint_y=0.3)
		
		# Información de costo
		if self.current_level < self.talent_info.max_level:
			next_cost = self.talent_manager.talents[self.talent_type].get_upgrade_cost()
			self.cost_label = Label(
				text=f"Costo: {next_cost} pts",
				font_size='10sp',
				size_hint_x=0.6
			)
		else:
			self.cost_label = Label(
				text="MAX",
				font_size='10sp',
				size_hint_x=0.6
			)
		footer_layout.add_widget(self.cost_label)
		
		# Botón de upgrade
		self.upgrade_button = Button(
			text="⬆️ Mejorar",
			size_hint_x=0.4,
			font_size='11sp'
		)
		self.upgrade_button.bind(on_press=self._on_upgrade_pressed)
		footer_layout.add_widget(self.upgrade_button)
		
		self.add_widget(footer_layout)
	
	def _update_visual_state(self):
		"""Actualiza el estado visual según disponibilidad y nivel."""
		# Determinar color de fondo
		if self.current_level == 0:
			# Talento no desbloqueado
			if self.can_upgrade:
				self.color_instruction.rgba = (0.2, 0.4, 0.8, 0.3)  # Azul disponible
			else:
				self.color_instruction.rgba = (0.3, 0.3, 0.3, 0.3)  # Gris bloqueado
		elif self.current_level == self.talent_info.max_level:
			# Talento al máximo
			self.color_instruction.rgba = (0.8, 0.6, 0.2, 0.4)  # Dorado máximo
		else:
			# Talento parcialmente mejorado
			self.color_instruction.rgba = (0.2, 0.7, 0.3, 0.4)  # Verde mejorado
		
		# Actualizar estado del botón
		if self.current_level == self.talent_info.max_level:
			self.upgrade_button.text = "✅ MAX"
			self.upgrade_button.disabled = True
		elif self.can_upgrade:
			self.upgrade_button.text = "⬆️ Mejorar"
			self.upgrade_button.disabled = False
		else:
			self.upgrade_button.text = "🔒 Bloqueado"
			self.upgrade_button.disabled = True
	
	def _on_upgrade_pressed(self, button):
		"""Maneja el clic en el botón de upgrade."""
		if self.talent_manager.can_upgrade_talent(self.talent_type):
			success = self.talent_manager.upgrade_talent(self.talent_type)
			if success:
				# Actualizar información local
				self.current_level = self.talent_manager.get_talent_level(self.talent_type)
				self.can_upgrade = self.talent_manager.can_upgrade_talent(self.talent_type)
				
				# Actualizar UI
				self.level_label.text = f"Nv. {self.current_level}/{self.talent_info.max_level}"
				if self.current_level < self.talent_info.max_level:
					next_cost = self.talent_manager.talents[self.talent_type].get_upgrade_cost()
					self.cost_label.text = f"Costo: {next_cost} pts"
				else:
					self.cost_label.text = "MAX"
				
				self._update_visual_state()
				
				# Notificar a la pantalla padre para actualizar puntos disponibles
				if hasattr(self.parent.parent.parent, 'update_talent_points_display'):
					self.parent.parent.parent.update_talent_points_display()
	
	def refresh_state(self):
		"""Refresca el estado del talento desde el manager."""
		self.current_level = self.talent_manager.get_talent_level(self.talent_type)
		self.can_upgrade = self.talent_manager.can_upgrade_talent(self.talent_type)
		
		self.level_label.text = f"Nv. {self.current_level}/{self.talent_info.max_level}"
		if self.current_level < self.talent_info.max_level:
			next_cost = self.talent_manager.talents[self.talent_type].get_upgrade_cost()
			self.cost_label.text = f"Costo: {next_cost} pts"
		else:
			self.cost_label.text = "MAX"
		
		self._update_visual_state()


class TalentBranchSection(BoxLayout):
	"""
	Sección que muestra todos los talentos de una rama específica.
	"""
	
	def __init__(self, branch: TalentBranch, talent_manager: TalentManager, **kwargs):
		super().__init__(**kwargs)
		self.orientation = 'vertical'
		self.spacing = 10
		self.padding = [15, 10]
		
		self.branch = branch
		self.talent_manager = talent_manager
		
		self._create_branch_header()
		self._create_talent_cards()
	
	def _create_branch_header(self):
		"""Crea el header de la rama con título y descripción."""
		# Mapeo de información por rama
		branch_info = {
			TalentBranch.WARRIOR: {
				'emoji': '🗡️',
				'name': 'Guerrero',
				'description': 'Especialización en daño físico y combate cuerpo a cuerpo'
			},
			TalentBranch.EXPLORER: {
				'emoji': '🏹',
				'name': 'Explorador',
				'description': 'Maestro del loot y la exploración de mazmorras'
			},
			TalentBranch.MAGE: {
				'emoji': '🔮',
				'name': 'Mago',
				'description': 'Poder arcano y habilidades mágicas devastadoras'
			},
			TalentBranch.TANK: {
				'emoji': '🛡️',
				'name': 'Tanque',
				'description': 'Defensa impenetrable y resistencia suprema'
			}
		}
		
		info = branch_info[self.branch]
		
		# Título de la rama
		title_label = Label(
			text=f"{info['emoji']} {info['name']}",
			font_size='18sp',
			bold=True,
			size_hint_y=None,
			height=40,
			halign='center'
		)
		self.add_widget(title_label)
		
		# Descripción de la rama
		desc_label = Label(
			text=info['description'],
			font_size='12sp',
			italic=True,
			size_hint_y=None,
			height=25,
			halign='center',
			color=(0.7, 0.7, 0.7, 1)
		)
		self.add_widget(desc_label)
	
	def _create_talent_cards(self):
		"""Crea los cards de talentos para esta rama."""
		# Obtener talentos de la rama
		branch_talents = [
			(talent_type, talent_info) for talent_type, talent_info in self.talent_manager.talent_info.items()
			if talent_info.branch == self.branch
		]
		
		# Ordenar por tier y luego por nombre
		branch_talents.sort(key=lambda t: (t[1].tier.value, t[1].name))
		
		# Crear cards
		self.talent_cards: List[TalentCard] = []
		for talent_type, talent_info in branch_talents:
			card = TalentCard(talent_type, self.talent_manager)
			self.talent_cards.append(card)
			self.add_widget(card)
	
	def refresh_all_cards(self):
		"""Refresca el estado de todos los cards de esta rama."""
		for card in self.talent_cards:
			card.refresh_state()


class TalentInfoPopup(Popup):
	"""
	Popup que muestra información detallada de un talento específico.
	"""
	
	def __init__(self, talent_type: TalentType, talent_manager: TalentManager, **kwargs):
		self.talent_type = talent_type
		self.talent_manager = talent_manager
		self.talent_info = talent_manager.talent_info[talent_type]
		
		super().__init__(**kwargs)
		self.title = f"{self.talent_info.emoji} {self.talent_info.name}"
		self.size_hint = (0.8, 0.7)
		
		self._create_content()
	
	def _create_content(self):
		"""Crea el contenido del popup."""
		layout = BoxLayout(orientation='vertical', spacing=15, padding=20)
		
		# Descripción detallada
		desc_label = Label(
			text=self.talent_info.description,
			text_size=(None, None),
			halign='center',
			font_size='14sp'
		)
		layout.add_widget(desc_label)
		
		# Información de nivel actual
		current_level = self.talent_manager.get_talent_level(self.talent_type)
		level_info = Label(
			text=f"Nivel Actual: {current_level}/{self.talent_info.max_level}",
			font_size='16sp',
			bold=True
		)
		layout.add_widget(level_info)
		
		# Efectos por nivel
		if current_level > 0:
			current_effect = self.talent_manager.get_talent_effect(self.talent_type)
			effect_label = Label(
				text=f"Efecto Actual: {current_effect:.2f}",
				font_size='14sp',
				color=(0.3, 0.8, 0.3, 1)
			)
			layout.add_widget(effect_label)
		
		# Costo del siguiente nivel
		if current_level < self.talent_info.max_level:
			next_cost = self.talent_manager.talents[self.talent_type].get_upgrade_cost()
			cost_label = Label(
				text=f"Costo Siguiente Nivel: {next_cost} puntos",
				font_size='14sp'
			)
			layout.add_widget(cost_label)
		
		# Requisitos
		if self.talent_info.prerequisites:
			req_text = "Requisitos:\n"
			for req_talent in self.talent_info.prerequisites:
				req_level = self.talent_manager.get_talent_level(req_talent)
				req_info = self.talent_manager.talent_info[req_talent]
				status = "✅" if req_level > 0 else "❌"
				req_text += f"{status} {req_info.name} (Nivel {req_level})\n"
			
			req_label = Label(
				text=req_text,
				text_size=(None, None),
				halign='center',
				font_size='12sp'
			)
			layout.add_widget(req_label)
		
		# Botón de cerrar
		close_button = Button(
			text="Cerrar",
			size_hint_y=None,
			height=50
		)
		close_button.bind(on_press=self.dismiss)
		layout.add_widget(close_button)
		
		self.content = layout


class TalentsScreen(BoxLayout):
	"""
	Pantalla principal del sistema de talentos.
	
	Muestra el árbol completo de talentos organizado por ramas,
	permite gestionar puntos y realizar upgrades.
	"""
	
	def __init__(self, talent_manager: TalentManager, **kwargs):
		super().__init__(**kwargs)
		self.orientation = 'vertical'
		self.spacing = 10
		self.padding = [20, 20]
		
		self.talent_manager = talent_manager
		self.branch_sections: Dict[TalentBranch, TalentBranchSection] = {}
		
		self._create_header()
		self._create_talent_tree()
		self._create_footer()
		
		# Actualizar display inicial
		self.update_talent_points_display()
	
	def _create_header(self):
		"""Crea el header con información general."""
		header_layout = BoxLayout(
			orientation='horizontal',
			size_hint_y=None,
			height=60,
			spacing=20
		)
		
		# Título
		title_label = Label(
			text="🌟 Árbol de Talentos",
			font_size='20sp',
			bold=True,
			size_hint_x=0.6
		)
		header_layout.add_widget(title_label)
		
		# Puntos disponibles
		self.points_label = Label(
			text="Puntos: 0",
			font_size='16sp',
			size_hint_x=0.4,
			halign='right'
		)
		header_layout.add_widget(self.points_label)
		
		self.add_widget(header_layout)
	
	def _create_talent_tree(self):
		"""Crea el árbol de talentos con scroll."""
		# ScrollView para el contenido principal
		scroll_view = ScrollView()
		
		# Layout principal para las ramas
		main_layout = GridLayout(
			cols=2,
			spacing=20,
			padding=10,
			size_hint_y=None
		)
		main_layout.bind(minimum_height=main_layout.setter('height'))
		
		# Crear secciones por rama
		branches = [TalentBranch.WARRIOR, TalentBranch.EXPLORER, TalentBranch.MAGE, TalentBranch.TANK]
		
		for branch in branches:
			section = TalentBranchSection(branch, self.talent_manager)
			section.size_hint_y = None
			section.height = 600  # Altura fija para cada sección
			
			self.branch_sections[branch] = section
			main_layout.add_widget(section)
		
		scroll_view.add_widget(main_layout)
		self.add_widget(scroll_view)
	
	def _create_footer(self):
		"""Crea el footer con opciones adicionales."""
		footer_layout = BoxLayout(
			orientation='horizontal',
			size_hint_y=None,
			height=50,
			spacing=15
		)
		
		# Botón de reset de talentos
		reset_button = Button(
			text="🔄 Reset Talentos",
			size_hint_x=0.5
		)
		reset_button.bind(on_press=self._show_reset_confirmation)
		footer_layout.add_widget(reset_button)
		
		# Información de estadísticas
		stats_button = Button(
			text="📊 Ver Estadísticas",
			size_hint_x=0.5
		)
		stats_button.bind(on_press=self._show_talent_stats)
		footer_layout.add_widget(stats_button)
		
		self.add_widget(footer_layout)
	
	def update_talent_points_display(self):
		"""Actualiza el display de puntos disponibles."""
		available_points = self.talent_manager.talent_points
		self.points_label.text = f"Puntos: {available_points}"
		
		# Refrescar todos los cards
		for section in self.branch_sections.values():
			section.refresh_all_cards()
	
	def _show_reset_confirmation(self, button):
		"""Muestra confirmación para resetear talentos."""
		# Calcular puntos que se recuperarían
		total_spent = sum(
			self.talent_manager.get_talent_level(talent_type) 
			for talent_type in TalentType
		)
		
		if total_spent == 0:
			# No hay talentos para resetear
			popup = Popup(
				title="Sin Talentos",
				content=Label(text="No tienes talentos para resetear."),
				size_hint=(0.6, 0.4)
			)
			popup.open()
			return
		
		# Popup de confirmación
		layout = BoxLayout(orientation='vertical', spacing=15, padding=20)
		
		info_label = Label(
			text=f"¿Resetear todos los talentos?\n\nRecuperarás {total_spent} puntos de talento.",
			text_size=(None, None),
			halign='center'
		)
		layout.add_widget(info_label)
		
		button_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=50)
		
		confirm_button = Button(text="✅ Confirmar")
		cancel_button = Button(text="❌ Cancelar")
		
		button_layout.add_widget(confirm_button)
		button_layout.add_widget(cancel_button)
		layout.add_widget(button_layout)
		
		popup = Popup(
			title="Confirmar Reset",
			content=layout,
			size_hint=(0.7, 0.5)
		)
		
		def do_reset(btn):
			self.talent_manager.reset_all_talents()
			self.update_talent_points_display()
			popup.dismiss()
		
		confirm_button.bind(on_press=do_reset)
		cancel_button.bind(on_press=popup.dismiss)
		
		popup.open()
	
	def _show_talent_stats(self, button):
		"""Muestra estadísticas detalladas de talentos."""
		layout = BoxLayout(orientation='vertical', spacing=10, padding=20)
		
		# Calcular estadísticas
		total_levels = sum(
			self.talent_manager.get_talent_level(talent_type) 
			for talent_type in TalentType
		)
		
		talents_unlocked = sum(
			1 for talent_type in TalentType
			if self.talent_manager.get_talent_level(talent_type) > 0
		)
		
		# Estadísticas por rama
		branch_stats = {}
		for branch in TalentBranch:
			branch_talents = [
				talent for talent in self.talent_manager.talents.values()
				if talent.branch == branch
			]
			branch_levels = sum(
				self.talent_manager.get_talent_level(talent.talent_type)
				for talent in branch_talents
			)
			branch_stats[branch] = branch_levels
		
		# Labels informativos
		stats_text = f"📊 Estadísticas de Talentos\n\n"
		stats_text += f"Talentos Desbloqueados: {talents_unlocked}/{len(TalentType)}\n"
		stats_text += f"Niveles Totales: {total_levels}\n"
		stats_text += f"Puntos Disponibles: {self.talent_manager.talent_points}\n\n"
		
		stats_text += "Por Rama:\n"
		for branch, levels in branch_stats.items():
			branch_emoji = {'WARRIOR': '🗡️', 'EXPLORER': '🏹', 'MAGE': '🔮', 'TANK': '🛡️'}
			emoji = branch_emoji.get(branch.name, '⭐')
			stats_text += f"{emoji} {branch.name.title()}: {levels} niveles\n"
		
		stats_label = Label(
			text=stats_text,
			text_size=(None, None),
			halign='center'
		)
		layout.add_widget(stats_label)
		
		close_button = Button(
			text="Cerrar",
			size_hint_y=None,
			height=50
		)
		layout.add_widget(close_button)
		
		popup = Popup(
			title="Estadísticas de Talentos",
			content=layout,
			size_hint=(0.8, 0.8)
		)
		
		close_button.bind(on_press=popup.dismiss)
		popup.open()
	
	def add_talent_points(self, points: int):
		"""Añade puntos de talento y actualiza la UI."""
		self.talent_manager.add_talent_points(points)
		self.update_talent_points_display()
