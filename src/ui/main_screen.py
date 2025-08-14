"""Pantalla principal del juego SiKIdle.

Contiene el área de combate, contador de recursos,
área de mejoras y espacios para anuncios.
"""

import logging
import math
from typing import Any, Optional

from kivy.animation import Animation  # type: ignore
from kivy.clock import Clock  # type: ignore
from kivy.uix.boxlayout import BoxLayout  # type: ignore
from kivy.uix.button import Button  # type: ignore
from kivy.uix.label import Label  # type: ignore
from kivy.uix.progressbar import ProgressBar  # type: ignore
from kivy.graphics import Color, Rectangle  # type: ignore

from core.game import get_game_state
from core.resources import ResourceType
from core.combat import CombatState
from core.enemies import EnemyFactory, EnemyType
from ui.screen_manager import SiKIdleScreen
from ui.tabbed_navigation import TabBar, TabbedNavigationSystem


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
		
		# UI de combate
		self.player_hp_bar = None
		self.player_hp_label = None
		self.enemy_hp_bar = None
		self.enemy_hp_label = None
		self.enemy_info_label = None
		self.combat_log_label = None
		self.start_combat_button = None
		
		# UI legacy (para compatibilidad)
		self.click_button = None
		self.multiplier_label = None
		self.bonus_label = None
		self.ad_button = None
		self.production_label = None

		# Sistema de navegación por pestañas
		self.tab_bar = None
		self.navigation_system = TabbedNavigationSystem()

		self.build_ui()
		self.setup_tabbed_navigation()
		self.setup_loot_notifications()
		
		# Inicializar combate si existe combat_manager
		if hasattr(self.game_state, 'combat_manager') and self.game_state.combat_manager:
			# Programar actualizaciones de combate
			Clock.schedule_interval(self.update_combat, 0.5)

	def build_ui(self):
		"""Construye la interfaz de la pantalla principal."""
		# Layout principal
		main_layout = BoxLayout(orientation="vertical", padding=[20, 20, 20, 20], spacing=15)

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
		header = BoxLayout(orientation="horizontal", size_hint=(1, 0.1), spacing=10)

		# Botón menú lateral
		menu_button = Button(
			text="☰", font_size="24sp", size_hint=(0.15, 1), background_color=[0.3, 0.5, 0.8, 1]
		)
		menu_button.bind(on_press=self.on_menu_button)
		header.add_widget(menu_button)

		# Contador de monedas (centrado)
		self.coins_label = Label(
			text="💰 0 monedas",
			font_size="24sp",
			size_hint=(0.55, 1),
			bold=True,
			color=[1, 0.8, 0, 1],  # Dorado
		)
		header.add_widget(self.coins_label)

		# Botón volver
		back_button = Button(
			text="← Menú", font_size="16sp", size_hint=(0.3, 1), background_color=[0.6, 0.6, 0.6, 1]
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
			orientation="horizontal", size_hint=(1, 0.08), spacing=5, padding=[10, 5, 10, 5]
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
					font_size="14sp",
					size_hint=(1, 1),
					color=resource_info.color.replace("#", "").lower(),  # Convertir color hex
				)
				resource_label.resource_type = resource_type  # Guardar referencia
				self.resources_panel.add_widget(resource_label)

		return self.resources_panel

	def create_game_area(self) -> BoxLayout:
		"""Crea el área principal de combate con selector de mazmorras.

		Returns:
			BoxLayout con el área de combate y mazmorras
		"""
		main_area = BoxLayout(orientation="vertical", size_hint=(1, 0.6), spacing=20)

		# Selector de mazmorras
		dungeon_section = self.create_dungeon_selector()
		main_area.add_widget(dungeon_section)

		# Área de combate
		combat_area = self.create_combat_area()
		main_area.add_widget(combat_area)

		return main_area

	def create_dungeon_selector(self) -> BoxLayout:
		"""Crea el selector de mazmorras.
		
		Returns:
			BoxLayout con información y controles de mazmorras
		"""
		dungeon_section = BoxLayout(orientation="vertical", size_hint=(1, 0.3), spacing=10)

		# Título y información de mazmorra activa
		header_layout = BoxLayout(orientation="horizontal", size_hint=(1, 0.4), spacing=10)
		
		dungeon_title = Label(
			text="🏰 Mazmorra Activa",
			font_size="14sp",
			size_hint=(0.3, 1),
			color=[0.9, 0.7, 0.2, 1]  # Dorado
		)
		header_layout.add_widget(dungeon_title)
		
		self.active_dungeon_label = Label(
			text="🌲 Bosque Encantado",
			font_size="14sp",
			size_hint=(0.4, 1),
			color=[0.2, 0.8, 0.2, 1]  # Verde
		)
		header_layout.add_widget(self.active_dungeon_label)
		
		# Botón cambiar mazmorra
		change_dungeon_button = Button(
			text="🔄 Cambiar",
			font_size="12sp",
			size_hint=(0.3, 1),
			background_color=[0.5, 0.5, 0.8, 1]
		)
		change_dungeon_button.bind(on_press=self.on_change_dungeon)
		header_layout.add_widget(change_dungeon_button)
		
		dungeon_section.add_widget(header_layout)
		
		# Progreso de exploración
		progress_layout = BoxLayout(orientation="horizontal", size_hint=(1, 0.3), spacing=10)
		
		progress_label = Label(
			text="Progreso:",
			font_size="12sp",
			size_hint=(0.2, 1),
			color=[1, 1, 1, 1]
		)
		progress_layout.add_widget(progress_label)
		
		self.exploration_progress = Label(
			text="0.0% explorado",
			font_size="12sp",
			size_hint=(0.4, 1),
			color=[0.7, 0.7, 1, 1]  # Azul claro
		)
		progress_layout.add_widget(self.exploration_progress)
		
		self.enemies_defeated_label = Label(
			text="0 enemigos derrotados",
			font_size="12sp",
			size_hint=(0.4, 1),
			color=[0.8, 0.8, 0.8, 1]  # Gris claro
		)
		progress_layout.add_widget(self.enemies_defeated_label)
		
		dungeon_section.add_widget(progress_layout)
		
		# Bonificaciones del bioma
		bonuses_layout = BoxLayout(orientation="horizontal", size_hint=(1, 0.3), spacing=5)
		
		bonuses_title = Label(
			text="Bonificaciones:",
			font_size="11sp",
			size_hint=(0.25, 1),
			color=[1, 1, 1, 1]
		)
		bonuses_layout.add_widget(bonuses_title)
		
		self.biome_bonuses_label = Label(
			text="+15% Velocidad | +10% Loot",
			font_size="10sp",
			size_hint=(0.75, 1),
			color=[0.2, 1, 0.2, 1]  # Verde brillante
		)
		bonuses_layout.add_widget(self.biome_bonuses_label)
		
		dungeon_section.add_widget(bonuses_layout)
		
		return dungeon_section

	def create_combat_area(self) -> BoxLayout:
		"""Crea el área específica de combate.
		
		Returns:
			BoxLayout con la interfaz de combate
		"""
		combat_area = BoxLayout(orientation="vertical", size_hint=(1, 0.7), spacing=15)

		# Información del jugador
		player_section = BoxLayout(orientation="vertical", size_hint=(1, 0.4), spacing=5)
		
		player_info_label = Label(
			text="🧙‍♂️ Jugador - Nivel 1",
			font_size="16sp",
			size_hint=(1, 0.3),
			color=[0.2, 0.8, 0.2, 1]  # Verde
		)
		player_section.add_widget(player_info_label)
		
		# Barra de HP del jugador
		player_hp_container = BoxLayout(orientation="horizontal", size_hint=(1, 0.4), spacing=10)
		
		player_hp_bg = Label(
			text="",
			size_hint=(1, 1),
			color=[0.8, 0.2, 0.2, 1]  # Rojo de fondo
		)
		player_hp_bg.canvas.before.add(Color(0.2, 0.2, 0.2, 1))  # Fondo gris
		player_hp_bg.canvas.before.add(Rectangle(pos=player_hp_bg.pos, size=player_hp_bg.size))
		
		self.player_hp_label = Label(
			text="HP: 100/100",
			font_size="14sp",
			size_hint=(0.3, 1),
			color=[1, 1, 1, 1]
		)
		
		player_hp_container.add_widget(player_hp_bg)
		player_hp_container.add_widget(self.player_hp_label)
		player_section.add_widget(player_hp_container)
		
		combat_area.add_widget(player_section)

		# Separador visual
		vs_label = Label(
			text="⚔️ VS ⚔️",
			font_size="24sp",
			size_hint=(1, 0.1),
			color=[1, 1, 0, 1]  # Amarillo
		)
		combat_area.add_widget(vs_label)

		# Información del enemigo
		enemy_section = BoxLayout(orientation="vertical", size_hint=(1, 0.4), spacing=5)
		
		self.enemy_info_label = Label(
			text="👹 Sin enemigo activo",
			font_size="16sp",
			size_hint=(1, 0.3),
			color=[0.8, 0.2, 0.2, 1]  # Rojo
		)
		enemy_section.add_widget(self.enemy_info_label)
		
		# Barra de HP del enemigo
		enemy_hp_container = BoxLayout(orientation="horizontal", size_hint=(1, 0.4), spacing=10)
		
		enemy_hp_bg = Label(
			text="",
			size_hint=(1, 1),
			color=[0.8, 0.2, 0.2, 1]  # Rojo de fondo
		)
		
		self.enemy_hp_label = Label(
			text="HP: --/--",
			font_size="14sp",
			size_hint=(0.3, 1),
			color=[1, 1, 1, 1]
		)
		
		enemy_hp_container.add_widget(enemy_hp_bg)
		enemy_hp_container.add_widget(self.enemy_hp_label)
		enemy_section.add_widget(enemy_hp_container)
		
		combat_area.add_widget(enemy_section)

		# Botón para iniciar combate
		self.start_combat_button = Button(
			text="🗡️ Buscar Enemigo",
			font_size="18sp",
			size_hint=(0.8, 0.1),
			pos_hint={'center_x': 0.5},
			background_color=[0.8, 0.2, 0.2, 1]
		)
		self.start_combat_button.bind(on_press=self.on_start_combat)
		combat_area.add_widget(self.start_combat_button)

		return combat_area

	def on_change_dungeon(self, button):
		"""Maneja el cambio de mazmorra activa."""
		try:
			if not hasattr(self.game_state, 'dungeon_manager'):
				print("Sistema de mazmorras no disponible")
				return
			
			dungeon_manager = self.game_state.dungeon_manager
			unlocked_dungeons = dungeon_manager.get_unlocked_dungeons()
			
			if len(unlocked_dungeons) <= 1:
				print("Solo hay una mazmorra disponible")
				button.text = "❌ Sin opciones"
				from kivy.clock import Clock
				Clock.schedule_once(lambda dt: setattr(button, 'text', '🔄 Cambiar'), 2)
				return
			
			# Rotar entre mazmorras desbloqueadas
			current_active = dungeon_manager.active_dungeon
			current_index = unlocked_dungeons.index(current_active) if current_active in unlocked_dungeons else 0
			next_index = (current_index + 1) % len(unlocked_dungeons)
			next_dungeon = unlocked_dungeons[next_index]
			
			# Cambiar mazmorra activa
			if dungeon_manager.set_active_dungeon(next_dungeon):
				self.update_dungeon_info()
				print(f"Cambiado a: {dungeon_manager.get_dungeon_info(next_dungeon).name}")
			
		except Exception as e:
			print(f"Error cambiando mazmorra: {e}")

	def update_dungeon_info(self):
		"""Actualiza la información de la mazmorra activa en la UI."""
		try:
			if not hasattr(self.game_state, 'dungeon_manager'):
				return
			
			dungeon_manager = self.game_state.dungeon_manager
			active_info = dungeon_manager.get_active_dungeon_info()
			
			if not active_info:
				self.active_dungeon_label.text = "❌ Sin mazmorra activa"
				self.exploration_progress.text = "0.0% explorado"
				self.enemies_defeated_label.text = "0 enemigos derrotados"
				self.biome_bonuses_label.text = "Sin bonificaciones"
				return
			
			dungeon_type, dungeon, info = active_info
			
			# Actualizar BiomeManager para la mazmorra activa
			dungeon_manager.update_biome_manager_for_active_dungeon()
			
			# Actualizar nombre de mazmorra
			self.active_dungeon_label.text = f"{info.emoji} {info.name}"
			
			# Actualizar progreso de exploración
			progress_percent = dungeon.exploration_progress * 100
			self.exploration_progress.text = f"{progress_percent:.1f}% explorado"
			
			# Actualizar enemigos derrotados
			self.enemies_defeated_label.text = f"{dungeon.total_enemies_defeated} enemigos derrotados"
			
			# Actualizar bonificaciones del bioma usando BiomeManager
			biome_bonuses = dungeon_manager.get_active_biome_bonuses()
			bonuses = []
			
			if biome_bonuses["attack_speed"] != 1.0:
				bonus_pct = (biome_bonuses["attack_speed"] - 1.0) * 100
				sign = "+" if bonus_pct > 0 else ""
				bonuses.append(f"{sign}{bonus_pct:.0f}% Velocidad")
			
			if biome_bonuses["defense"] != 1.0:
				bonus_pct = (biome_bonuses["defense"] - 1.0) * 100
				sign = "+" if bonus_pct > 0 else ""
				bonuses.append(f"{sign}{bonus_pct:.0f}% Defensa")
			
			if biome_bonuses["damage"] != 1.0:
				bonus_pct = (biome_bonuses["damage"] - 1.0) * 100
				sign = "+" if bonus_pct > 0 else ""
				bonuses.append(f"{sign}{bonus_pct:.0f}% Daño")
			
			if biome_bonuses["experience"] != 1.0:
				bonus_pct = (biome_bonuses["experience"] - 1.0) * 100
				sign = "+" if bonus_pct > 0 else ""
				bonuses.append(f"{sign}{bonus_pct:.0f}% EXP")
			
			if biome_bonuses["loot_rarity"] > 0:
				bonus_pct = biome_bonuses["loot_rarity"] * 100
				bonuses.append(f"+{bonus_pct:.0f}% Loot")
			
			self.biome_bonuses_label.text = " | ".join(bonuses) if bonuses else "Sin bonificaciones"
			
			# Aplicar tema visual del bioma
			self.apply_biome_visual_theme()
			
		except Exception as e:
			print(f"Error actualizando info de mazmorra: {e}")
	
	def apply_biome_visual_theme(self):
		"""
		Aplica el tema visual del bioma activo a la interfaz.
		
		Cambia los colores de fondo y elementos según el bioma
		de la mazmorra actualmente activa.
		"""
		try:
			if not hasattr(self.game_state, 'dungeon_manager'):
				return
			
			dungeon_manager = self.game_state.dungeon_manager
			biome_colors = dungeon_manager.get_active_biome_colors()
			visual_theme = dungeon_manager.get_active_biome_visual_theme()
			
			if not biome_colors or not visual_theme:
				return
			
			# Aplicar color primario del bioma como color de fondo
			# (esto se puede expandir para cambiar más elementos visuales)
			primary_color = biome_colors["primary"]
			
			# Aplicar tema a elementos de combate si existen
			if hasattr(self, 'combat_area') and self.combat_area:
				# Cambiar color de fondo del área de combate
				with self.combat_area.canvas.before:
					Color(*primary_color)
					Rectangle(pos=self.combat_area.pos, size=self.combat_area.size)
			
			# Log del cambio de tema (para debugging)
			print(f"🎨 Tema visual aplicado: {visual_theme.ambient_description}")
			
		except Exception as e:
			print(f"Error aplicando tema visual de bioma: {e}")
		
		player_hp_bg = Label(
			text="",
			size_hint=(1, 1),
			color=[0.8, 0.2, 0.2, 1]  # Rojo de fondo
		)
		player_hp_bg.canvas.before.add(Color(0.2, 0.2, 0.2, 1))  # Fondo gris
		player_hp_bg.canvas.before.add(Rectangle(pos=player_hp_bg.pos, size=player_hp_bg.size))
		
		self.player_hp_label = Label(
			text="HP: 100/100",
			font_size="14sp",
			size_hint=(0.3, 1),
			color=[1, 1, 1, 1]
		)
		
		player_hp_container.add_widget(player_hp_bg)
		player_hp_container.add_widget(self.player_hp_label)
		player_section.add_widget(player_hp_container)
		
		combat_area.add_widget(player_section)

		# Separador visual
		vs_label = Label(
			text="⚔️ VS ⚔️",
			font_size="24sp",
			size_hint=(1, 0.1),
			color=[1, 1, 0, 1]  # Amarillo
		)
		combat_area.add_widget(vs_label)

		# Información del enemigo
		enemy_section = BoxLayout(orientation="vertical", size_hint=(1, 0.4), spacing=5)
		
		self.enemy_info_label = Label(
			text="� Sin enemigo activo",
			font_size="16sp",
			size_hint=(1, 0.3),
			color=[0.8, 0.2, 0.2, 1]  # Rojo
		)
		enemy_section.add_widget(self.enemy_info_label)
		
		# Barra de HP del enemigo
		enemy_hp_container = BoxLayout(orientation="horizontal", size_hint=(1, 0.4), spacing=10)
		
		enemy_hp_bg = Label(
			text="",
			size_hint=(1, 1),
			color=[0.8, 0.2, 0.2, 1]  # Rojo de fondo
		)
		
		self.enemy_hp_label = Label(
			text="HP: --/--",
			font_size="14sp",
			size_hint=(0.3, 1),
			color=[1, 1, 1, 1]
		)
		
		enemy_hp_container.add_widget(enemy_hp_bg)
		enemy_hp_container.add_widget(self.enemy_hp_label)
		enemy_section.add_widget(enemy_hp_container)
		
		combat_area.add_widget(enemy_section)

		# Botón para iniciar combate
		self.start_combat_button = Button(
			text="🗡️ Buscar Enemigo",
			font_size="18sp",
			size_hint=(0.8, 0.1),
			pos_hint={'center_x': 0.5},
			background_color=[0.8, 0.2, 0.2, 1]
		)
		self.start_combat_button.bind(on_press=self.on_start_combat)
		combat_area.add_widget(self.start_combat_button)

		return combat_area

	def create_bottom_area(self) -> BoxLayout:
		"""Crea el área inferior con barra de pestañas de navegación.

		Returns:
			BoxLayout con la barra de pestañas y elementos adicionales
		"""
		bottom_area = BoxLayout(orientation="vertical", size_hint=(1, 0.25), spacing=5)

		# Crear barra de pestañas de navegación
		self.tab_bar = TabBar()
		bottom_area.add_widget(self.tab_bar)

		# Indicador de producción automática (más pequeño)
		self.production_label = Label(
			text="📈 Producción automática: 0 monedas/seg",
			font_size="10sp",
			size_hint=(1, 0.3),
			color=[0.7, 0.9, 0.7, 1],  # Verde claro
		)
		bottom_area.add_widget(self.production_label)

		return bottom_area

	def on_start_combat(self, button):
		"""Maneja el inicio de combate usando el sistema de mazmorras."""
		try:
			# Verificar sistemas disponibles
			if not hasattr(self.game_state, 'combat_manager') or not self.game_state.combat_manager:
				print("No hay sistema de combate disponible")
				button.text = "❌ Sistema no disponible"
				return
			
			if not hasattr(self.game_state, 'dungeon_manager') or not self.game_state.dungeon_manager:
				print("No hay sistema de mazmorras disponible")
				button.text = "❌ Mazmorras no disponibles"
				return
				
			combat_manager = self.game_state.combat_manager
			dungeon_manager = self.game_state.dungeon_manager
			
			# Verificar si ya hay combate activo
			from core.combat import CombatState
			if combat_manager.combat_state == CombatState.FIGHTING:
				print("Ya hay un combate en curso")
				return
			
			# Generar enemigo desde la mazmorra activa
			enemy_info = dungeon_manager.generate_enemy_for_active_dungeon()
			if not enemy_info:
				print("No se pudo generar enemigo de la mazmorra activa")
				button.text = "❌ Sin mazmorra"
				return
			
			enemy_type, enemy_level = enemy_info
			
			# Crear enemigo con factory
			from core.enemies import EnemyFactory
			enemy_factory = EnemyFactory()
			enemy = enemy_factory.create_enemy(enemy_type, enemy_level)
			
			# Iniciar combate
			combat_manager.start_combat(enemy)
			button.text = "⚔️ Combatiendo..."
			button.disabled = True
			
			# Obtener info de mazmorra para mostrar contexto
			active_info = dungeon_manager.get_active_dungeon_info()
			if active_info:
				_, _, dungeon_info = active_info
				print(f"Combate iniciado en {dungeon_info.name}: {enemy.name} Nivel {enemy_level}")
			
		except Exception as e:
			print(f"Error al iniciar combate: {e}")
			button.text = "❌ Error"

	def update_combat(self, dt):
		"""Actualiza la UI de combate y maneja recompensas de mazmorra."""
		try:
			if not hasattr(self.game_state, 'combat_manager') or not self.game_state.combat_manager:
				return False
			
			combat_manager = self.game_state.combat_manager
			dungeon_manager = getattr(self.game_state, 'dungeon_manager', None)
			
			# Actualizar lógica de combate
			result = combat_manager.update_combat(dt)
			
			# Actualizar información del jugador
			if combat_manager.player:
				player_stats = combat_manager.player.get_effective_stats()
				player_level = 1
				if combat_manager.player.stats_manager:
					player_level = combat_manager.player.stats_manager.level_system.level
				
				if self.player_hp_label:
					self.player_hp_label.text = f"HP: {player_stats.current_hp}/{player_stats.max_hp}"
			
			# Actualizar información del enemigo
			if combat_manager.current_enemy:
				enemy = combat_manager.current_enemy
				if self.enemy_info_label:
					self.enemy_info_label.text = f"👹 {enemy.name} (Nv.{enemy.level})"
				if self.enemy_hp_label:
					self.enemy_hp_label.text = f"HP: {enemy.stats.current_hp}/{enemy.stats.max_hp}"
			else:
				if self.enemy_info_label:
					self.enemy_info_label.text = "👹 Sin enemigo activo"
				if self.enemy_hp_label:
					self.enemy_hp_label.text = "HP: --/--"
			
			# Manejar fin de combate
			if result:
				from core.combat import CombatState
				if self.start_combat_button:
					if result.state == CombatState.PLAYER_VICTORY:
						self.start_combat_button.text = "🗡️ Buscar Enemigo"
						
						# Procesar recompensas de mazmorra
						if dungeon_manager and combat_manager.current_enemy:
							dungeon_result = dungeon_manager.on_enemy_defeated(combat_manager.current_enemy.level)
							if dungeon_result:
								progress_gain = dungeon_result.get('progress_gained', 0) * 100
								total_enemies = dungeon_result.get('total_enemies_defeated', 0)
								print(f"¡Victoria! Progreso: +{progress_gain:.1f}% | Total enemigos: {total_enemies}")
								
								# Actualizar UI de mazmorras
								self.update_dungeon_info()
								
								# Verificar completación de mazmorra
								if dungeon_result.get('dungeon_completed', False):
									print(f"¡Mazmorra {dungeon_result['dungeon_name']} completada!")
						
						print(f"Ganaste {result.experience_gained} XP")
						
					elif result.state == CombatState.PLAYER_DEFEATED:
						self.start_combat_button.text = "💀 Derrotado - Buscar Enemigo"
						print("Has sido derrotado")
					
					self.start_combat_button.disabled = False
			
			return True
			
		except Exception as e:
			print(f"Error en update_combat: {e}")
			return False

	def setup_tabbed_navigation(self):
		"""Configura el sistema de navegación por pestañas."""
		if not self.tab_bar:
			logging.warning("Tab bar no inicializada")
			return

		# Configurar el sistema de navegación
		self.navigation_system.setup(self.tab_bar)

		# Registrar todas las pestañas principales
		self.navigation_system.register_tab("upgrades", "Gestión", "🏗️", self.navigate_to_upgrades)
		self.navigation_system.register_tab("dungeons", "Mazmorras", "🏰", self.navigate_to_dungeons)
		self.navigation_system.register_tab(
			"achievements", "Logros", "🏆", self.navigate_to_achievements
		)
		self.navigation_system.register_tab("talents", "Talentos", "🌟", self.navigate_to_talents)
		self.navigation_system.register_tab(
			"prestige", "Prestigio", "💎", self.navigate_to_prestige
		)
		self.navigation_system.register_tab("stats", "Stats", "📊", self.navigate_to_stats)
		self.navigation_system.register_tab("settings", "Config", "⚙️", self.navigate_to_settings)

		logging.info("Sistema de navegación por pestañas configurado correctamente")

	# Métodos de navegación para las pestañas
	def navigate_to_upgrades(self):
		"""Navega a la pantalla de gestión (mejoras + edificios)."""
		logging.info("Navegando a gestión desde pestañas")
		self.navigate_to("upgrades")

	def navigate_to_dungeons(self):
		"""Navega a la pantalla de mazmorras."""
		logging.info("Navegando a mazmorras desde pestañas")
		self.navigate_to("dungeons")

	def navigate_to_achievements(self):
		"""Navega a la pantalla de logros."""
		logging.info("Navegando a logros desde pestañas")
		self.navigate_to("achievements")

	def navigate_to_talents(self):
		"""Navega a la pantalla de talentos."""
		logging.info("Navegando a talentos desde pestañas")
		self.navigate_to("talents")

	def navigate_to_prestige(self):
		"""Navega a la pantalla de prestigio."""
		logging.info("Navegando a prestigio desde pestañas")
		self.navigate_to("prestige")

	def navigate_to_stats(self):
		"""Navega a la pantalla de estadísticas."""
		logging.info("Navegando a estadísticas desde pestañas")
		self.navigate_to("stats")

	def navigate_to_settings(self):
		"""Navega a la pantalla de configuración."""
		logging.info("Navegando a configuración desde pestañas")
		self.navigate_to("settings")

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
			anim = Animation(size_hint=(0.85, 0.75), duration=0.1) + Animation(
				size_hint=(0.8, 0.7), duration=0.1
			)
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
			instance.text = "📺 Anuncio visto\n¡Bonificación activa!"
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
			self.ad_button.text = "📺 Ver Anuncio\n(x2 monedas 30s)"
			self.ad_button.background_color = [1, 0.6, 0, 1]  # Naranja
			self.ad_button.disabled = False
			logging.info("Botón de anuncio reactivado")

	def on_back_button(self, instance: Button):
		"""Maneja el clic en el botón de volver.

		Args:
			instance: Instancia del botón presionado
		"""
		logging.info("Volviendo al menú principal")
		self.navigate_to("start")

	def update_ui(self, dt: float = 0):
		"""Actualiza la interfaz con los datos actuales del juego.

		Args:
			dt: Delta time (no usado)
		"""
		# Actualizar la producción automática de los edificios
		if hasattr(self.game_state, "update_building_production"):
			self.game_state.update_building_production()

		stats = self.game_state.get_game_stats()

		# Actualizar contador de monedas tradicional
		if self.coins_label:
			self.coins_label.text = f"💰 {stats['coins']:,} monedas"

		# Actualizar indicador de producción por segundo
		if hasattr(self, "production_label") and self.production_label:
			total_production = 0.0
			if hasattr(self.game_state, "building_manager"):
				for building_type in self.game_state.building_manager.buildings:
					building = self.game_state.building_manager.buildings[building_type]
					if building.count > 0:
						building_info = self.game_state.building_manager.get_building_info(
							building_type
						)
						total_production += building_info.base_production * building.count

			self.production_label.text = f"Producción: {total_production:.1f} monedas/seg"

		# Actualizar panel de recursos múltiples
		if hasattr(self, "resources_panel") and self.resources_panel:
			for child in self.resources_panel.children:
				if hasattr(child, "resource_type"):
					resource_type = child.resource_type
					resource_info = self.game_state.resource_manager.get_resource_info(
						resource_type
					)
					amount = self.game_state.resource_manager.get_resource(resource_type)
					child.text = f"{resource_info.symbol} {int(amount)}"

		# Actualizar multiplicador
		if self.multiplier_label:
			current_mult = stats["current_multiplier"]
			if current_mult > stats["multiplier"]:
				self.multiplier_label.text = f"Multiplicador: x{current_mult:.1f} (¡BONUS!)"
				self.multiplier_label.color = [1, 0.6, 0, 1]  # Naranja para bonus
			else:
				self.multiplier_label.text = f"Multiplicador: x{current_mult:.1f}"
				self.multiplier_label.color = [0.8, 0.8, 1, 1]  # Azul normal

		# Actualizar estado de bonificación
		if self.bonus_label:
			if stats["bonus_active"]:
				remaining = math.ceil(stats["bonus_time_remaining"])
				self.bonus_label.text = f"🔥 ¡BONIFICACIÓN ACTIVA! {remaining}s restantes"
			else:
				self.bonus_label.text = ""

	def on_menu_button(self, instance: Button):
		"""Maneja el clic en el botón del menú.

		Args:
			instance: Instancia del botón presionado
		"""
		logging.info("Botón de menú presionado - redirigiendo a configuración")
		# Como eliminamos el menú lateral, redirigimos a configuración
		self.navigate_to("settings")

	def on_enter(self, *args):
		"""Método llamado cuando se entra a la pantalla."""
		super().on_enter(*args)

		# Iniciar el juego si no está corriendo
		if not self.game_state.game_running:
			self.game_state.start_game()

		# Inicializar UI de mazmorras
		self.update_dungeon_info()

		# Programar actualización de UI
		if not self.update_scheduled:
			Clock.schedule_interval(self.update_ui, 1.0)  # Actualizar cada segundo
			Clock.schedule_interval(self.update_combat, 0.5)  # Actualizar combate más frecuentemente
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

	def setup_loot_notifications(self):
		"""Configura las notificaciones de loot en la interfaz"""
		if hasattr(self.game_state, 'loot_combat_integration'):
			integration = self.game_state.loot_combat_integration
			integration.set_loot_obtained_callback(self._on_loot_obtained)
			integration.set_rare_loot_obtained_callback(self._on_rare_loot_obtained)
			logging.info("Notificaciones de loot configuradas en MainScreen")

	def _on_loot_obtained(self, item, enemy_type: str, is_boss: bool):
		"""
		Callback ejecutado cuando se obtiene loot
		
		Args:
		    item: Ítem obtenido
		    enemy_type: Tipo de enemigo que dropeo el ítem
		    is_boss: Si era un boss
		"""
		try:
			# Mostrar notificación en el log de combate
			boss_text = " (BOSS)" if is_boss else ""
			notification_text = f"¡Loot obtenido de {enemy_type}{boss_text}!\n{item.get_display_name()}"
			
			if self.combat_log_label:
				self.combat_log_label.text = notification_text
			
			# Programar que desaparezca después de 3 segundos
			Clock.schedule_once(lambda dt: self._clear_loot_notification(), 3.0)
			
		except Exception as e:
			logging.error("Error mostrando notificación de loot: %s", e)

	def _on_rare_loot_obtained(self, item, enemy_type: str, is_boss: bool):
		"""
		Callback ejecutado cuando se obtiene loot raro/épico/legendario
		
		Args:
		    item: Ítem raro obtenido
		    enemy_type: Tipo de enemigo que dropeo el ítem
		    is_boss: Si era un boss
		"""
		try:
			# Para loot raro, mostrar notificación más prominente
			boss_text = " (BOSS)" if is_boss else ""
			rarity_emoji = {"rare": "💚", "epic": "💙", "legendary": "🟣"}.get(item.rarity.value, "⭐")
			
			notification_text = f"{rarity_emoji} ¡LOOT RARO DE {enemy_type.upper()}{boss_text}! {rarity_emoji}\n{item.get_display_name()}"
			
			if self.combat_log_label:
				self.combat_log_label.text = notification_text
				
				# Animación especial para loot raro
				anim = Animation(opacity=0.5, duration=0.3) + Animation(opacity=1.0, duration=0.3)
				anim.repeat = True
				anim.start(self.combat_log_label)
				
				# Detener animación después de 2 segundos
				Clock.schedule_once(lambda dt: anim.stop(self.combat_log_label), 2.0)
			
			# Programar que desaparezca después de 5 segundos (más tiempo para loot raro)
			Clock.schedule_once(lambda dt: self._clear_loot_notification(), 5.0)
			
		except Exception as e:
			logging.error("Error mostrando notificación de loot raro: %s", e)

	def _clear_loot_notification(self):
		"""Limpia las notificaciones de loot del log de combate"""
		if self.combat_log_label:
			self.combat_log_label.text = "Preparado para combate"
