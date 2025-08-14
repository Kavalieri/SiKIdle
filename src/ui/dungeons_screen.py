"""
Pantalla de gestión de mazmorras para SiKIdle.

Esta pantalla permite al jugador ver todas las mazmorras disponibles,
sus condiciones de desbloqueo, progreso de exploración, y cambiar
la mazmorra activa.

Autor: GitHub Copilot
Fecha: 04 de agosto de 2025 - 20:45
"""

import logging
from typing import Any, Dict, List, Optional

from kivy.clock import Clock  # type: ignore
from kivy.uix.boxlayout import BoxLayout  # type: ignore
from kivy.uix.button import Button  # type: ignore
from kivy.uix.gridlayout import GridLayout  # type: ignore
from kivy.uix.label import Label  # type: ignore
from kivy.uix.progressbar import ProgressBar  # type: ignore
from kivy.uix.scrollview import ScrollView  # type: ignore

from core.game import get_game_state
from core.dungeons import DungeonType
from ui.screen_manager import SiKIdleScreen


class DungeonCard(BoxLayout):
	"""Widget que representa una mazmorra individual."""
	
	def __init__(self, dungeon_type: DungeonType, **kwargs: Any):
		"""
		Inicializa una tarjeta de mazmorra.
		
		Args:
			dungeon_type: Tipo de mazmorra a representar
			**kwargs: Argumentos adicionales para BoxLayout
		"""
		super().__init__(orientation="vertical", size_hint=(None, None), 
						size=(280, 350), spacing=8, **kwargs)
		
		self.dungeon_type = dungeon_type
		self.game_state = get_game_state()
		self.dungeon_manager = self.game_state.dungeon_manager
		
		# Obtener información de la mazmorra
		self.dungeon_info = self.dungeon_manager.get_dungeon_info(dungeon_type)
		self.dungeon = self.dungeon_manager.get_dungeon(dungeon_type)
		
		self._create_widgets()
		self._update_state()
	
	def _create_widgets(self) -> None:
		"""Crea todos los widgets de la tarjeta."""
		# Header con emoji y nombre
		header_layout = BoxLayout(orientation="horizontal", size_hint=(1, 0.2), spacing=5)
		
		emoji_label = Label(
			text=self.dungeon_info.emoji,
			font_size="20sp",
			size_hint=(0.2, 1)
		)
		header_layout.add_widget(emoji_label)
		
		self.name_label = Label(
			text=self.dungeon_info.name,
			font_size="14sp",
			size_hint=(0.8, 1),
			color=[1, 1, 1, 1],
			text_size=(200, None),
			halign="left"
		)
		header_layout.add_widget(self.name_label)
		
		self.add_widget(header_layout)
		
		# Descripción
		self.description_label = Label(
			text=self.dungeon_info.description,
			font_size="11sp",
			size_hint=(1, 0.25),
			color=[0.9, 0.9, 0.9, 1],
			text_size=(260, None),
			halign="left",
			valign="top"
		)
		self.add_widget(self.description_label)
		
		# Información de nivel y bioma
		info_layout = BoxLayout(orientation="vertical", size_hint=(1, 0.2), spacing=3)
		
		level_label = Label(
			text=f"🎯 Nivel: {self.dungeon_info.base_enemy_level}-{self.dungeon_info.max_enemy_level}",
			font_size="11sp",
			size_hint=(1, 0.5),
			color=[0.8, 0.8, 1, 1]
		)
		info_layout.add_widget(level_label)
		
		biome_label = Label(
			text=f"🌍 {self.dungeon_info.biome.value.replace('_', ' ').title()}",
			font_size="11sp",
			size_hint=(1, 0.5),
			color=[0.6, 0.8, 0.6, 1]
		)
		info_layout.add_widget(biome_label)
		
		self.add_widget(info_layout)
		
		# Estado y progreso
		self.status_label = Label(
			text="Estado: Cargando...",
			font_size="11sp",
			size_hint=(1, 0.15),
			color=[0.8, 0.8, 0.8, 1]
		)
		self.add_widget(self.status_label)
		
		# Barra de progreso
		progress_layout = BoxLayout(orientation="vertical", size_hint=(1, 0.1), spacing=2)
		
		self.progress_bar = ProgressBar(
			min=0,
			max=100,
			value=0,
			size_hint=(1, 1)
		)
		progress_layout.add_widget(self.progress_bar)
		
		self.add_widget(progress_layout)
		
		# Botón de acción
		self.action_button = Button(
			text="Seleccionar",
			size_hint=(1, 0.1),
			background_color=[0.2, 0.6, 0.8, 1]
		)
		self.action_button.bind(on_press=self._on_action_button)
		self.add_widget(self.action_button)
	
	def _update_state(self) -> None:
		"""Actualiza el estado visual de la tarjeta."""
		# Actualizar progreso de exploración
		if self.dungeon and self.dungeon.unlocked:
			progress_percent = self.dungeon.exploration_progress * 100
			self.progress_bar.value = progress_percent
			
			# Estado desbloqueado
			stats_text = f"✅ Desbloqueada | 👹 Enemigos: {self.dungeon.total_enemies_defeated}"
			if self.dungeon.boss_defeated:
				stats_text += " | 👑 Boss ✅"
			else:
				stats_text += " | 👑 Boss ⏳"
			
			self.status_label.text = stats_text
			self.status_label.color = [0.2, 0.8, 0.2, 1]
		else:
			self.progress_bar.value = 0
			
			# Estado bloqueado
			unlock_text = f"🔒 Bloqueada | Requisitos: Nivel {self.dungeon_info.unlock_level}"
			if self.dungeon_info.unlock_cost > 0:
				unlock_text += f", {self.dungeon_info.unlock_cost} monedas"
			
			self.status_label.text = unlock_text
			self.status_label.color = [0.8, 0.2, 0.2, 1]
		
		# Verificar si es la mazmorra activa
		if self.dungeon_manager.active_dungeon == self.dungeon_type:
			self.action_button.text = "🎯 ACTIVA"
			self.action_button.background_color = [0.2, 0.8, 0.2, 1]
			self.action_button.disabled = True
		elif self.dungeon and self.dungeon.unlocked:
			self.action_button.text = "⚔️ Explorar"
			self.action_button.background_color = [0.2, 0.6, 0.8, 1]
			self.action_button.disabled = False
		else:
			# Verificar si puede ser desbloqueada (simplificado)
			player_level = self.game_state.player_stats.level_system.level
			has_resources = self.game_state.resource_manager.can_afford(
				self.dungeon_info.unlock_resource, 
				self.dungeon_info.unlock_cost
			)
			
			if player_level >= self.dungeon_info.unlock_level and has_resources:
				self.action_button.text = "🔓 Desbloquear"
				self.action_button.background_color = [0.8, 0.6, 0.2, 1]
				self.action_button.disabled = False
			else:
				self.action_button.text = "🔒 Bloqueada"
				self.action_button.background_color = [0.5, 0.5, 0.5, 1]
				self.action_button.disabled = True
	
	def _on_action_button(self, button: Button) -> None:
		"""
		Maneja el clic en el botón de acción.
		
		Args:
			button: Botón presionado
		"""
		try:
			if self.dungeon and self.dungeon.unlocked:
				# Cambiar a esta mazmorra
				success = self.dungeon_manager.set_active_dungeon(self.dungeon_type)
				if success:
					logging.info(f"Cambiando a mazmorra: {self.dungeon_info.name}")
				else:
					logging.warning(f"No se pudo cambiar a: {self.dungeon_info.name}")
			else:
				# Intentar desbloquear (simplificado)
				if self.dungeon:
					success = self.dungeon.unlock(self.dungeon_info, self.game_state.resource_manager)
					if success:
						logging.info(f"Mazmorra desbloqueada: {self.dungeon_info.name}")
					else:
						logging.warning(f"No se pudo desbloquear: {self.dungeon_info.name}")
		except Exception as e:
			logging.error(f"Error en acción de mazmorra: {e}")
		
		# Actualizar estado visual
		self._update_state()


class DungeonsScreen(SiKIdleScreen):
	"""Pantalla principal de gestión de mazmorras."""
	
	def __init__(self, **kwargs: Any):
		"""Inicializa la pantalla de mazmorras."""
		super().__init__(**kwargs)
		
		self.game_state = get_game_state()
		self.dungeon_cards: Dict[DungeonType, DungeonCard] = {}
		
		self._create_layout()
		self._schedule_updates()
	
	def _create_layout(self) -> None:
		"""Crea el layout principal de la pantalla."""
		main_layout = BoxLayout(orientation="vertical", spacing=15, padding=[15, 15, 15, 15])
		
		# Header
		header = self._create_header()
		main_layout.add_widget(header)
		
		# Área de mazmorras con scroll
		dungeons_scroll = self._create_dungeons_area()
		main_layout.add_widget(dungeons_scroll)
		
		# Footer con información actual
		footer = self._create_footer()
		main_layout.add_widget(footer)
		
		self.add_widget(main_layout)
	
	def _create_header(self) -> BoxLayout:
		"""
		Crea el header de la pantalla.
		
		Returns:
			BoxLayout con el header
		"""
		header = BoxLayout(orientation="vertical", size_hint=(1, 0.15), spacing=8)
		
		title = Label(
			text="🏰 MAZMORRAS Y EXPLORACIÓN",
			font_size="20sp",
			size_hint=(1, 0.6),
			color=[0.9, 0.7, 0.2, 1]  # Dorado
		)
		header.add_widget(title)
		
		subtitle = Label(
			text="Explora diferentes biomas, derrota enemigos únicos y desbloquea nuevas áreas",
			font_size="12sp",
			size_hint=(1, 0.4),
			color=[0.8, 0.8, 0.8, 1]
		)
		header.add_widget(subtitle)
		
		return header
	
	def _create_dungeons_area(self) -> ScrollView:
		"""
		Crea el área principal con las tarjetas de mazmorras.
		
		Returns:
			ScrollView con las mazmorras
		"""
		# GridLayout para organizar las tarjetas
		dungeons_grid = GridLayout(
			cols=2,
			spacing=15,
			size_hint_y=None,
			row_default_height=370,
			row_force_default=True
		)
		dungeons_grid.bind(minimum_height=dungeons_grid.setter('height'))
		
		# Crear tarjetas para todas las mazmorras
		for dungeon_type in DungeonType:
			card = DungeonCard(dungeon_type)
			self.dungeon_cards[dungeon_type] = card
			dungeons_grid.add_widget(card)
		
		# ScrollView para permitir desplazamiento
		scroll = ScrollView(size_hint=(1, 0.7))
		scroll.add_widget(dungeons_grid)
		
		return scroll
	
	def _create_footer(self) -> BoxLayout:
		"""
		Crea el footer con información de la mazmorra actual.
		
		Returns:
			BoxLayout con el footer
		"""
		footer = BoxLayout(orientation="horizontal", size_hint=(1, 0.15), spacing=15)
		
		# Información de mazmorra activa
		active_info = BoxLayout(orientation="vertical", size_hint=(0.5, 1), spacing=3)
		
		self.active_dungeon_label = Label(
			text="🎯 Mazmorra Activa: Cargando...",
			font_size="12sp",
			size_hint=(1, 0.5),
			color=[0.2, 0.8, 0.2, 1]
		)
		active_info.add_widget(self.active_dungeon_label)
		
		self.biome_bonus_label = Label(
			text="🌍 Bonificaciones: Cargando...",
			font_size="11sp",
			size_hint=(1, 0.5),
			color=[0.6, 0.8, 0.6, 1]
		)
		active_info.add_widget(self.biome_bonus_label)
		
		footer.add_widget(active_info)
		
		# Estadísticas generales
		stats_info = BoxLayout(orientation="vertical", size_hint=(0.5, 1), spacing=3)
		
		self.total_dungeons_label = Label(
			text="📊 Mazmorras Desbloqueadas: 0/5",
			font_size="12sp",
			size_hint=(1, 0.5),
			color=[0.8, 0.6, 0.2, 1]
		)
		stats_info.add_widget(self.total_dungeons_label)
		
		self.exploration_label = Label(
			text="🗺️ Exploración Total: 0%",
			font_size="11sp",
			size_hint=(1, 0.5),
			color=[0.6, 0.6, 0.8, 1]
		)
		stats_info.add_widget(self.exploration_label)
		
		footer.add_widget(stats_info)
		
		return footer
	
	def _schedule_updates(self) -> None:
		"""Programa las actualizaciones automáticas de la UI."""
		Clock.schedule_interval(self.update_ui, 2.0)  # Actualizar cada 2 segundos
	
	def update_ui(self, dt: float = 0) -> None:
		"""
		Actualiza toda la interfaz de usuario.
		
		Args:
			dt: Delta time (no usado)
		"""
		try:
			# Actualizar todas las tarjetas
			for card in self.dungeon_cards.values():
				card._update_state()
			
			# Actualizar footer
			self._update_footer()
			
		except Exception as e:
			logging.error(f"Error actualizando UI de mazmorras: {e}")
	
	def _update_footer(self) -> None:
		"""Actualiza la información del footer."""
		try:
			# Información de mazmorra activa
			if self.game_state.dungeon_manager.active_dungeon:
				active_info = self.game_state.dungeon_manager.get_active_dungeon_info()
				if active_info:
					dungeon_type, dungeon_info, dungeon = active_info
					self.active_dungeon_label.text = f"🎯 Mazmorra Activa: {dungeon_info.name}"
					
					# Bonificaciones del bioma (simplificado)
					bonuses = []
					if dungeon_info.damage_bonus > 0:
						bonuses.append(f"⚔️ +{int(dungeon_info.damage_bonus * 100)}% Daño")
					if dungeon_info.defense_bonus > 0:
						bonuses.append(f"🛡️ +{int(dungeon_info.defense_bonus * 100)}% Defensa")
					if dungeon_info.speed_bonus > 0:
						bonuses.append(f"⚡ +{int(dungeon_info.speed_bonus * 100)}% Velocidad")
					if dungeon_info.exp_bonus > 0:
						bonuses.append(f"📈 +{int(dungeon_info.exp_bonus * 100)}% EXP")
					
					if bonuses:
						self.biome_bonus_label.text = f"🌍 Bonificaciones: {', '.join(bonuses[:2])}"
					else:
						self.biome_bonus_label.text = "🌍 Bonificaciones: Ninguna"
				else:
					self.active_dungeon_label.text = "🎯 Mazmorra Activa: Error"
					self.biome_bonus_label.text = "🌍 Bonificaciones: Error"
			else:
				self.active_dungeon_label.text = "🎯 Mazmorra Activa: Ninguna"
				self.biome_bonus_label.text = "🌍 Bonificaciones: Ninguna"
			
			# Estadísticas generales
			total_dungeons = len(DungeonType)
			unlocked_count = 0
			total_exploration = 0.0
			
			for dungeon_type in DungeonType:
				dungeon = self.game_state.dungeon_manager.get_dungeon(dungeon_type)
				if dungeon and dungeon.unlocked:
					unlocked_count += 1
					total_exploration += dungeon.exploration_progress
			
			self.total_dungeons_label.text = f"📊 Mazmorras Desbloqueadas: {unlocked_count}/{total_dungeons}"
			
			# Exploración promedio
			if unlocked_count > 0:
				avg_exploration = (total_exploration / unlocked_count) * 100
				self.exploration_label.text = f"🗺️ Exploración Promedio: {avg_exploration:.1f}%"
			else:
				self.exploration_label.text = "🗺️ Exploración Total: 0%"
			
		except Exception as e:
			logging.error(f"Error actualizando footer de mazmorras: {e}")
	
	def on_pre_enter(self, *args: Any) -> None:
		"""Se llama antes de mostrar la pantalla."""
		super().on_pre_enter(*args)
		# Forzar actualización inmediata al entrar
		self.update_ui()
	
	def on_leave(self, *args: Any) -> None:
		"""Se llama al salir de la pantalla."""
		super().on_leave(*args)
		# Cancelar actualizaciones cuando no está visible
		Clock.unschedule(self.update_ui)

import logging
from typing import Any, Dict, List, Optional

from kivy.animation import Animation  # type: ignore
from kivy.clock import Clock  # type: ignore
from kivy.uix.boxlayout import BoxLayout  # type: ignore
from kivy.uix.button import Button  # type: ignore
from kivy.uix.gridlayout import GridLayout  # type: ignore
from kivy.uix.label import Label  # type: ignore
from kivy.uix.progressbar import ProgressBar  # type: ignore
from kivy.uix.scrollview import ScrollView  # type: ignore
from kivy.uix.widget import Widget  # type: ignore
from kivy.graphics import Color, Rectangle  # type: ignore

from core.game import get_game_state
from core.dungeons import DungeonType, DungeonManager
from core.dungeon_unlock import DungeonUnlockManager
from core.biomes import BiomeType
from ui.screen_manager import SiKIdleScreen


class DungeonCard(BoxLayout):
	"""Widget que representa una mazmorra individual."""
	
	def __init__(self, dungeon_type: DungeonType, **kwargs: Any):
		"""
		Inicializa una tarjeta de mazmorra.
		
		Args:
			dungeon_type: Tipo de mazmorra a representar
			**kwargs: Argumentos adicionales para BoxLayout
		"""
		super().__init__(orientation="vertical", size_hint=(None, None), 
						size=(300, 400), spacing=10, **kwargs)
		
		self.dungeon_type = dungeon_type
		self.game_state = get_game_state()
		self.dungeon_manager = self.game_state.dungeon_manager
		self.unlock_manager = self.game_state.unlock_manager
		
		# Obtener información de la mazmorra
		self.dungeon_info = self.dungeon_manager.get_dungeon_info(dungeon_type)
		self.dungeon = self.dungeon_manager.get_dungeon(dungeon_type)
		
		# Configurar fondo de la tarjeta con color del bioma
		with self.canvas.before:
			self.bg_color = Color(*self._get_biome_color())
			self.bg_rect = Rectangle(pos=self.pos, size=self.size)
		
		self.bind(pos=self._update_background, size=self._update_background)
		
		self._create_widgets()
		self._update_state()
	
	def _get_biome_color(self) -> List[float]:
		"""
		Obtiene el color de fondo según el bioma.
		
		Returns:
			Lista con RGBA del color del bioma
		"""
		biome_colors = {
			"enchanted_forest": [0.2, 0.5, 0.2, 0.8],      # Verde bosque
			"deep_caves": [0.4, 0.3, 0.2, 0.8],            # Marrón tierra
			"ancient_ruins": [0.5, 0.4, 0.3, 0.8],         # Beige piedra
			"orc_fortress": [0.3, 0.3, 0.3, 0.8],          # Gris metal
			"shadow_dimension": [0.2, 0.1, 0.4, 0.8],      # Púrpura místico
		}
		biome_value = self.dungeon_info.biome.value
		return biome_colors.get(biome_value, [0.3, 0.3, 0.3, 0.8])
	
	def _update_background(self, *args: Any) -> None:
		"""Actualiza el fondo cuando cambia la posición o tamaño."""
		self.bg_rect.pos = self.pos
		self.bg_rect.size = self.size
	
	def _create_widgets(self) -> None:
		"""Crea todos los widgets de la tarjeta."""
		# Header con emoji y nombre
		header_layout = BoxLayout(orientation="horizontal", size_hint=(1, 0.15), spacing=5)
		
		emoji_label = Label(
			text=self.dungeon_info.emoji,
			font_size="24sp",
			size_hint=(0.2, 1)
		)
		header_layout.add_widget(emoji_label)
		
		self.name_label = Label(
			text=self.dungeon_info.name,
			font_size="16sp",
			size_hint=(0.8, 1),
			color=[1, 1, 1, 1],
			text_size=(None, None),
			halign="left"
		)
		header_layout.add_widget(self.name_label)
		
		self.add_widget(header_layout)
		
		# Descripción
		self.description_label = Label(
			text=self.dungeon_info.description,
			font_size="12sp",
			size_hint=(1, 0.2),
			color=[0.9, 0.9, 0.9, 1],
			text_size=(280, None),
			halign="left",
			valign="top"
		)
		self.add_widget(self.description_label)
		
		# Información de nivel
		level_layout = BoxLayout(orientation="horizontal", size_hint=(1, 0.1), spacing=5)
		
		level_info = Label(
			text=f"🎯 Nivel: {self.dungeon_info.base_enemy_level}-{self.dungeon_info.max_enemy_level}",
			font_size="12sp",
			size_hint=(0.7, 1),
			color=[0.8, 0.8, 1, 1]
		)
		level_layout.add_widget(level_info)
		
		self.biome_label = Label(
			text=f"🌍 {self.dungeon_info.biome.value.title()}",
			font_size="12sp",
			size_hint=(0.3, 1),
			color=[0.6, 0.8, 0.6, 1]
		)
		level_layout.add_widget(self.biome_label)
		
		self.add_widget(level_layout)
		
		# Barra de progreso de exploración
		progress_layout = BoxLayout(orientation="vertical", size_hint=(1, 0.15), spacing=2)
		
		progress_label = Label(
			text="📊 Progreso de Exploración",
			font_size="10sp",
			size_hint=(1, 0.4),
			color=[0.7, 0.9, 0.7, 1]
		)
		progress_layout.add_widget(progress_label)
		
		self.progress_bar = ProgressBar(
			min=0,
			max=100,
			value=0,
			size_hint=(1, 0.6)
		)
		progress_layout.add_widget(self.progress_bar)
		
		self.add_widget(progress_layout)
		
		# Estado de desbloqueo y condiciones
		self.status_layout = BoxLayout(orientation="vertical", size_hint=(1, 0.25), spacing=5)
		self.add_widget(self.status_layout)
		
		# Botón de acción
		self.action_button = Button(
			text="Seleccionar",
			size_hint=(1, 0.15),
			background_color=[0.2, 0.6, 0.8, 1]
		)
		self.action_button.bind(on_press=self._on_action_button)
		self.add_widget(self.action_button)
	
	def _update_state(self) -> None:
		"""Actualiza el estado visual de la tarjeta."""
		# Actualizar progreso de exploración
		if self.dungeon and self.dungeon.unlocked:
			progress_percent = self.dungeon.exploration_progress * 100
			self.progress_bar.value = progress_percent
		else:
			self.progress_bar.value = 0
		
		# Limpiar layout de estado
		self.status_layout.clear_widgets()
		
		# Verificar si está desbloqueada
		if self.dungeon and self.dungeon.unlocked:
			self._show_unlocked_status()
		else:
			self._show_locked_status()
		
		# Verificar si es la mazmorra activa
		if self.dungeon_manager.current_dungeon == self.dungeon_type:
			self.action_button.text = "🎯 ACTIVA"
			self.action_button.background_color = [0.2, 0.8, 0.2, 1]
			self.action_button.disabled = True
		elif self.dungeon and self.dungeon.unlocked:
			self.action_button.text = "⚔️ Explorar"
			self.action_button.background_color = [0.2, 0.6, 0.8, 1]
			self.action_button.disabled = False
		else:
			# Verificar si puede ser desbloqueada usando el método correcto
			can_unlock = self.unlock_manager.check_unlock_conditions(
				self.dungeon_type, 
				self.game_state.player_stats.level,
				self.game_state.resource_manager
			)
			if can_unlock:
				self.action_button.text = "🔓 Desbloquear"
				self.action_button.background_color = [0.8, 0.6, 0.2, 1]
				self.action_button.disabled = False
			else:
				self.action_button.text = "🔒 Bloqueada"
				self.action_button.background_color = [0.5, 0.5, 0.5, 1]
				self.action_button.disabled = True
	
	def _show_unlocked_status(self) -> None:
		"""Muestra información para mazmorras desbloqueadas."""
		status_label = Label(
			text="✅ Desbloqueada",
			font_size="12sp",
			size_hint=(1, 0.3),
			color=[0.2, 0.8, 0.2, 1]
		)
		self.status_layout.add_widget(status_label)
		
		# Mostrar estadísticas
		if self.dungeon:
			stats_text = f"👹 Enemigos: {self.dungeon.total_enemies_defeated}\n"
			if self.dungeon.boss_defeated:
				stats_text += "👑 Boss Derrotado ✅"
			else:
				stats_text += "👑 Boss Pendiente ⏳"
			
			stats_label = Label(
				text=stats_text,
				font_size="10sp",
				size_hint=(1, 0.7),
				color=[0.8, 0.8, 0.8, 1],
				text_size=(280, None),
				halign="left",
				valign="top"
			)
			self.status_layout.add_widget(stats_label)
	
	def _show_locked_status(self) -> None:
		"""Muestra condiciones de desbloqueo para mazmorras bloqueadas."""
		status_label = Label(
			text="🔒 Bloqueada",
			font_size="12sp",
			size_hint=(1, 0.2),
			color=[0.8, 0.2, 0.2, 1]
		)
		self.status_layout.add_widget(status_label)
		
		# Obtener condiciones de desbloqueo
		unlock_info = self.unlock_manager.get_unlock_requirements(self.dungeon_type)
		if unlock_info:
			conditions_text = "📋 Requisitos:\n"
			for requirement in unlock_info.requirements:
				for condition in requirement.conditions:
					# Verificar si la condición está cumplida
					is_met = self.unlock_manager._check_condition(condition)
					status_icon = "✅" if is_met else "❌"
					conditions_text += f"{status_icon} {condition.description}\n"
			
			conditions_label = Label(
				text=conditions_text.strip(),
				font_size="9sp",
				size_hint=(1, 0.8),
				color=[0.9, 0.9, 0.9, 1],
				text_size=(280, None),
				halign="left",
				valign="top"
			)
			self.status_layout.add_widget(conditions_label)
		else:
			# Condiciones básicas de nivel y recursos
			basic_text = f"📋 Requisitos:\n"
			basic_text += f"🎯 Nivel {self.dungeon_info.unlock_level}\n"
			basic_text += f"💰 {self.dungeon_info.unlock_cost} monedas"
			
			basic_label = Label(
				text=basic_text,
				font_size="10sp",
				size_hint=(1, 0.8),
				color=[0.9, 0.9, 0.9, 1],
				text_size=(280, None),
				halign="left",
				valign="top"
			)
			self.status_layout.add_widget(basic_label)
	
	def _on_action_button(self, button: Button) -> None:
		"""
		Maneja el clic en el botón de acción.
		
		Args:
			button: Botón presionado
		"""
		if self.dungeon and self.dungeon.unlocked:
			# Cambiar a esta mazmorra
			self.dungeon_manager.set_current_dungeon(self.dungeon_type)
			logging.info(f"Cambiando a mazmorra: {self.dungeon_info.name}")
		else:
			# Intentar desbloquear
			success = self.unlock_manager.attempt_unlock_dungeon(self.dungeon_type)
			if success:
				logging.info(f"Mazmorra desbloqueada: {self.dungeon_info.name}")
			else:
				logging.warning(f"No se pudo desbloquear: {self.dungeon_info.name}")
		
		# Actualizar estado visual
		self._update_state()


class DungeonsScreen(SiKIdleScreen):
	"""Pantalla principal de gestión de mazmorras."""
	
	def __init__(self, **kwargs: Any):
		"""Inicializa la pantalla de mazmorras."""
		super().__init__(**kwargs)
		
		self.game_state = get_game_state()
		self.dungeon_cards: Dict[DungeonType, DungeonCard] = {}
		
		self._create_layout()
		self._schedule_updates()
	
	def _create_layout(self) -> None:
		"""Crea el layout principal de la pantalla."""
		main_layout = BoxLayout(orientation="vertical", spacing=20, padding=[20, 20, 20, 20])
		
		# Header
		header = self._create_header()
		main_layout.add_widget(header)
		
		# Área de mazmorras con scroll
		dungeons_scroll = self._create_dungeons_area()
		main_layout.add_widget(dungeons_scroll)
		
		# Footer con información actual
		footer = self._create_footer()
		main_layout.add_widget(footer)
		
		self.add_widget(main_layout)
	
	def _create_header(self) -> BoxLayout:
		"""
		Crea el header de la pantalla.
		
		Returns:
			BoxLayout con el header
		"""
		header = BoxLayout(orientation="vertical", size_hint=(1, 0.15), spacing=10)
		
		# Título principal
		title = Label(
			text="🏰 MAZMORRAS Y EXPLORACIÓN",
			font_size="24sp",
			size_hint=(1, 0.5),
			color=[0.9, 0.7, 0.2, 1]  # Dorado
		)
		header.add_widget(title)
		
		# Subtítulo con información
		subtitle = Label(
			text="Explora diferentes biomas, derrota enemigos únicos y desbloquea nuevas áreas",
			font_size="14sp",
			size_hint=(1, 0.5),
			color=[0.8, 0.8, 0.8, 1]
		)
		header.add_widget(subtitle)
		
		return header
	
	def _create_dungeons_area(self) -> ScrollView:
		"""
		Crea el área principal con las tarjetas de mazmorras.
		
		Returns:
			ScrollView con las mazmorras
		"""
		# GridLayout para organizar las tarjetas
		dungeons_grid = GridLayout(
			cols=2,
			spacing=20,
			size_hint_y=None,
			row_default_height=420,
			row_force_default=True
		)
		dungeons_grid.bind(minimum_height=dungeons_grid.setter('height'))
		
		# Crear tarjetas para todas las mazmorras
		for dungeon_type in DungeonType:
			card = DungeonCard(dungeon_type)
			self.dungeon_cards[dungeon_type] = card
			dungeons_grid.add_widget(card)
		
		# ScrollView para permitir desplazamiento
		scroll = ScrollView(size_hint=(1, 0.7))
		scroll.add_widget(dungeons_grid)
		
		return scroll
	
	def _create_footer(self) -> BoxLayout:
		"""
		Crea el footer con información de la mazmorra actual.
		
		Returns:
			BoxLayout con el footer
		"""
		footer = BoxLayout(orientation="horizontal", size_hint=(1, 0.15), spacing=20)
		
		# Información de mazmorra activa
		active_info = BoxLayout(orientation="vertical", size_hint=(0.5, 1), spacing=5)
		
		self.active_dungeon_label = Label(
			text="🎯 Mazmorra Activa: Cargando...",
			font_size="14sp",
			size_hint=(1, 0.5),
			color=[0.2, 0.8, 0.2, 1]
		)
		active_info.add_widget(self.active_dungeon_label)
		
		self.biome_bonus_label = Label(
			text="🌍 Bonificaciones: Cargando...",
			font_size="12sp",
			size_hint=(1, 0.5),
			color=[0.6, 0.8, 0.6, 1]
		)
		active_info.add_widget(self.biome_bonus_label)
		
		footer.add_widget(active_info)
		
		# Estadísticas generales
		stats_info = BoxLayout(orientation="vertical", size_hint=(0.5, 1), spacing=5)
		
		self.total_dungeons_label = Label(
			text="📊 Mazmorras Desbloqueadas: 0/5",
			font_size="14sp",
			size_hint=(1, 0.5),
			color=[0.8, 0.6, 0.2, 1]
		)
		stats_info.add_widget(self.total_dungeons_label)
		
		self.exploration_label = Label(
			text="🗺️ Exploración Total: 0%",
			font_size="12sp",
			size_hint=(1, 0.5),
			color=[0.6, 0.6, 0.8, 1]
		)
		stats_info.add_widget(self.exploration_label)
		
		footer.add_widget(stats_info)
		
		return footer
	
	def _schedule_updates(self) -> None:
		"""Programa las actualizaciones automáticas de la UI."""
		Clock.schedule_interval(self.update_ui, 1.0)  # Actualizar cada segundo
	
	def update_ui(self, dt: float = 0) -> None:
		"""
		Actualiza toda la interfaz de usuario.
		
		Args:
			dt: Delta time (no usado)
		"""
		try:
			# Actualizar todas las tarjetas
			for card in self.dungeon_cards.values():
				card._update_state()
			
			# Actualizar footer
			self._update_footer()
			
		except Exception as e:
			logging.error(f"Error actualizando UI de mazmorras: {e}")
	
	def _update_footer(self) -> None:
		"""Actualiza la información del footer."""
		try:
			# Información de mazmorra activa
			current_type = self.game_state.dungeon_manager.current_dungeon_type
			if current_type:
				dungeon_info = self.game_state.dungeon_manager.get_dungeon_info(current_type)
				self.active_dungeon_label.text = f"🎯 Mazmorra Activa: {dungeon_info.name}"
				
				# Bonificaciones del bioma
				biome_manager = self.game_state.dungeon_manager.biome_manager
				current_biome = biome_manager.current_biome
				if current_biome:
					bonuses = []
					biome_data = biome_manager.get_biome_data(current_biome)
					if biome_data.damage_multiplier > 1.0:
						bonuses.append(f"⚔️ +{int((biome_data.damage_multiplier - 1) * 100)}% Daño")
					if biome_data.defense_multiplier > 1.0:
						bonuses.append(f"🛡️ +{int((biome_data.defense_multiplier - 1) * 100)}% Defensa")
					if biome_data.speed_multiplier > 1.0:
						bonuses.append(f"⚡ +{int((biome_data.speed_multiplier - 1) * 100)}% Velocidad")
					if biome_data.exp_multiplier > 1.0:
						bonuses.append(f"📈 +{int((biome_data.exp_multiplier - 1) * 100)}% EXP")
					
					if bonuses:
						self.biome_bonus_label.text = f"🌍 Bonificaciones: {', '.join(bonuses)}"
					else:
						self.biome_bonus_label.text = "🌍 Bonificaciones: Ninguna"
			else:
				self.active_dungeon_label.text = "🎯 Mazmorra Activa: Ninguna"
				self.biome_bonus_label.text = "🌍 Bonificaciones: Ninguna"
			
			# Estadísticas generales
			total_dungeons = len(DungeonType)
			unlocked_count = sum(1 for dungeon_type in DungeonType 
							   if self.game_state.dungeon_manager.get_dungeon(dungeon_type) 
							   and self.game_state.dungeon_manager.get_dungeon(dungeon_type).unlocked)
			
			self.total_dungeons_label.text = f"📊 Mazmorras Desbloqueadas: {unlocked_count}/{total_dungeons}"
			
			# Exploración promedio
			if unlocked_count > 0:
				total_exploration = sum(
					self.game_state.dungeon_manager.get_dungeon(dungeon_type).exploration_progress
					for dungeon_type in DungeonType
					if self.game_state.dungeon_manager.get_dungeon(dungeon_type) 
					and self.game_state.dungeon_manager.get_dungeon(dungeon_type).unlocked
				)
				avg_exploration = (total_exploration / unlocked_count) * 100
				self.exploration_label.text = f"🗺️ Exploración Promedio: {avg_exploration:.1f}%"
			else:
				self.exploration_label.text = "🗺️ Exploración Total: 0%"
			
		except Exception as e:
			logging.error(f"Error actualizando footer de mazmorras: {e}")
	
	def on_pre_enter(self, *args: Any) -> None:
		"""Se llama antes de mostrar la pantalla."""
		super().on_pre_enter(*args)
		# Forzar actualización inmediata al entrar
		self.update_ui()
	
	def on_leave(self, *args: Any) -> None:
		"""Se llama al salir de la pantalla."""
		super().on_leave(*args)
		# Cancelar actualizaciones cuando no está visible
		Clock.unschedule(self.update_ui)
