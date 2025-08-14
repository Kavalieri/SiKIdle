"""
Pantalla de combate principal para SiKIdle.
Aquí ocurre la mecánica principal del idle clicker: click para atacar enemigos.
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.progressbar import ProgressBar
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.graphics import Color, Rectangle
from kivy.core.window import Window

import os
import random
import logging
from typing import Dict, Any, Optional
from pathlib import Path

from core.combat import CombatStats, DamageType
from utils.paths import get_assets_path


class Enemy:
	"""Clase para representar un enemigo en combate."""

	def __init__(self, name: str, sprite_file: str, level: int = 1):
		self.name = name
		self.sprite_file = sprite_file
		self.level = level

		# Stats escalados por nivel
		base_hp = 10 + (level * 5)
		base_attack = 2 + (level * 1)
		base_defense = 1 + (level // 3)

		self.stats = CombatStats(
			max_hp=base_hp,
			current_hp=base_hp,
			attack=base_attack,
			defense=base_defense,
			speed=1.0,
			critical_chance=0.02,
		)

		# Recompensas escaladas por nivel
		self.gold_reward = 3 + (level * 2)
		self.exp_reward = 5 + (level * 3)

	def get_sprite_path(self) -> str:
		"""Obtiene la ruta completa del sprite del enemigo."""
		assets_path = get_assets_path()
		return str(assets_path / "enemies" / self.sprite_file)


class CombatScreen(Screen):
	"""Pantalla principal de combate donde ocurre el juego."""

	def __init__(self, name="combat", **kwargs):
		super().__init__(name=name, **kwargs)

		# Estado del combate
		self.current_enemy: Optional[Enemy] = None
		self.dungeon_level = 1
		self.auto_combat_active = True
		self.enemies_defeated_in_level = 0
		self.enemies_needed_for_next_level = 5  # Enemigos necesarios para subir nivel

		# Stats del jugador
		self.player_max_hp = 100
		self.player_current_hp = 100
		self.player_damage = 10
		self.player_defense = 2
		self.player_attack_speed = 2.0  # Ataques por segundo

		# Referencias a widgets
		self.enemy_image = None
		self.enemy_name_label = None
		self.enemy_hp_bar = None
		self.enemy_hp_label = None
		self.level_label = None
		self.gold_label = None
		self.exp_label = None
		self.damage_label = None
		self.player_hp_bar = None
		self.player_hp_label = None
		self.level_progress_label = None

		# Conectar con GameState real
		from core.game import get_game_state

		try:
			self.real_game_state = get_game_state()
			# Obtener referencia al combat_manager si está disponible
			if hasattr(self.real_game_state, "combat_manager"):
				self.combat_manager = self.real_game_state.combat_manager
				logging.info(
					f"DEBUG: CombatScreen using CombatManager ID: {id(self.combat_manager)}"
				)
			else:
				self.combat_manager = None
				logging.warning("No combat_manager found in game_state")
		except Exception as e:
			logging.error(f"Error connecting to GameState: {e}")
			self.real_game_state = None
			self.combat_manager = None

		# Estado de recursos del jugador (fallback)
		self.player_gold = 0
		self.player_exp = 0
		self.player_level = 1

		# Timers de combate
		self.last_player_attack = 0
		self.last_enemy_attack = 0

		# Enemigos disponibles con sus sprites
		self.enemy_types = [
			("Hormiga Gigante", "ant1.png"),
			("Escarabajo", "beetle.png"),
			("Ciempiés", "centipede.png"),
			("Orco", "orc.png"),
			("Esqueleto", "skeleton.png"),
			("Araña", "spider.png"),
		]

		self._build_ui()
		self._spawn_enemy()

		# Iniciar combat loop más frecuente
		Clock.schedule_interval(self._combat_tick, 0.1)  # Cada 100ms para combate fluido

		logging.info("CombatScreen initialized")

	def _build_ui(self):
		"""Construye la interfaz de la pantalla de combate."""
		main_layout = BoxLayout(orientation="vertical", padding=20, spacing=10)

		# Header con información del nivel y recursos
		header = self._create_header()
		main_layout.add_widget(header)

		# Sub-navegación interna (Combat / Talentos)
		subnav = self._create_subnav()
		main_layout.add_widget(subnav)

		# Contenido dinámico (Combat o Talentos)
		self.content_area = BoxLayout(orientation="vertical")
		self.current_tab = "combat"
		self._show_combat_content()
		main_layout.add_widget(self.content_area)

		self.add_widget(main_layout)

	def _create_subnav(self) -> BoxLayout:
		"""Crea la sub-navegación interna."""
		subnav = BoxLayout(orientation="horizontal", size_hint_y=None, height=50, spacing=4)

		self.combat_tab_btn = Button(
			text="⚔️ Combate", size_hint_x=0.33, background_color=(0.2, 0.6, 0.8, 1)
		)
		self.combat_tab_btn.bind(on_press=lambda x: self._switch_tab("combat"))

		self.equipment_tab_btn = Button(
			text="🎒 Equipo", size_hint_x=0.33, background_color=(0.5, 0.5, 0.5, 1)
		)
		self.equipment_tab_btn.bind(on_press=lambda x: self._switch_tab("equipment"))

		self.talents_tab_btn = Button(
			text="🌟 Talentos", size_hint_x=0.33, background_color=(0.5, 0.5, 0.5, 1)
		)
		self.talents_tab_btn.bind(on_press=lambda x: self._switch_tab("talents"))

		subnav.add_widget(self.combat_tab_btn)
		subnav.add_widget(self.equipment_tab_btn)
		subnav.add_widget(self.talents_tab_btn)

		return subnav

	def _switch_tab(self, tab_name):
		"""Cambia entre pestañas de combat, equipamiento y talentos."""
		self.current_tab = tab_name
		self.content_area.clear_widgets()

		# Reset de colores
		self.combat_tab_btn.background_color = (0.5, 0.5, 0.5, 1)
		self.equipment_tab_btn.background_color = (0.5, 0.5, 0.5, 1)
		self.talents_tab_btn.background_color = (0.5, 0.5, 0.5, 1)

		# Cambiar modo del header según la pestaña
		self._update_header_mode_for_tab(tab_name)

		if tab_name == "combat":
			self.combat_tab_btn.background_color = (0.2, 0.6, 0.8, 1)
			self._show_combat_content()
		elif tab_name == "equipment":
			self.equipment_tab_btn.background_color = (0.2, 0.6, 0.8, 1)
			self._show_equipment_content()
		else:  # talents
			self.talents_tab_btn.background_color = (0.2, 0.6, 0.8, 1)
			self._show_talents_content()

	def _update_header_mode_for_tab(self, tab_name):
		"""Actualiza el modo del header según la pestaña activa en combate."""
		try:
			from kivy.app import App

			app = App.get_running_app()
			if hasattr(app, "root") and hasattr(app.root, "header"):
				if tab_name == "equipment":
					app.root.header.set_mode("equipment")
				else:
					app.root.header.set_mode("combat")
		except Exception:
			pass

	def _show_combat_content(self):
		"""Muestra el contenido de combate."""
		# Área central de combate
		combat_area = self._create_combat_area()
		self.content_area.add_widget(combat_area)

		# Footer con controles
		footer = self._create_footer()
		self.content_area.add_widget(footer)

	def _show_talents_content(self):
		"""Muestra el contenido de talentos de combate."""
		talents_area = self._create_talents_area()
		self.content_area.add_widget(talents_area)

	def _create_talents_area(self) -> BoxLayout:
		"""Crea el área de talentos de combate."""
		talents_layout = BoxLayout(orientation="vertical", spacing=10)

		# Título y puntos disponibles
		header = BoxLayout(orientation="horizontal", size_hint_y=None, height=40)
		title = Label(text="🌟 Talentos de Combate", font_size="18sp", bold=True, size_hint_x=0.7)

		# Obtener puntos de talento del GameState
		talent_points = 0
		if self.real_game_state:
			talent_points = self.real_game_state.talent_points

		points_label = Label(text=f"Puntos: {talent_points}", font_size="16sp", size_hint_x=0.3)
		header.add_widget(title)
		header.add_widget(points_label)

		# Lista de talentos de combate
		talents_scroll = ScrollView()
		talents_grid = GridLayout(cols=1, spacing=8, size_hint_y=None, padding=10)
		talents_grid.bind(minimum_height=talents_grid.setter("height"))

		# Solo talentos relacionados con combate
		combat_talents = [
			(
				"critical_chance",
				"🍀 Probabilidad Crítica",
				"Aumenta la probabilidad de golpes críticos",
			),
			("critical_damage", "💥 Daño Crítico", "Aumenta el daño de los golpes críticos"),
			("combat_speed", "⚡ Velocidad de Ataque", "Aumenta la velocidad de ataque"),
			("combat_defense", "🛡️ Resistencia", "Reduce el daño recibido de enemigos"),
		]

		for talent_id, name, desc in combat_talents:
			talent_widget = self._create_talent_widget(talent_id, name, desc, talent_points)
			talents_grid.add_widget(talent_widget)

		talents_scroll.add_widget(talents_grid)

		talents_layout.add_widget(header)
		talents_layout.add_widget(talents_scroll)

		return talents_layout

	def _create_talent_widget(self, talent_id, name, desc, available_points):
		"""Crea un widget individual para un talento."""
		widget = BoxLayout(
			orientation="horizontal", size_hint_y=None, height=80, spacing=10, padding=[8, 4]
		)

		# Información del talento
		info_layout = BoxLayout(orientation="vertical", size_hint_x=0.7)

		# Obtener nivel actual del talento
		current_level = 0
		if self.real_game_state:
			current_level = self.real_game_state.talents.get(talent_id, 0)

		max_level = 10
		costs = [1, 2, 3, 5, 8, 13, 21, 34, 55, 89]
		cost = costs[current_level] if current_level < len(costs) else 89

		name_label = Label(
			text=f"{name} (Nivel {current_level}/{max_level})",
			font_size="14sp",
			bold=True,
			size_hint_y=0.5,
			halign="left",
			valign="center",
		)
		name_label.bind(texture_size=name_label.setter("text_size"))

		desc_label = Label(
			text=desc,
			font_size="12sp",
			color=(0.7, 0.7, 0.7, 1),
			size_hint_y=0.5,
			halign="left",
			valign="center",
		)
		desc_label.bind(texture_size=desc_label.setter("text_size"))

		info_layout.add_widget(name_label)
		info_layout.add_widget(desc_label)

		# Botón de mejora
		can_upgrade = available_points >= cost and current_level < max_level
		upgrade_btn = Button(
			text=f"Mejorar\n({cost} pts)" if current_level < max_level else "MAX",
			font_size="12sp",
			size_hint_x=0.3,
			disabled=not can_upgrade,
			background_color=(0.2, 0.8, 0.2, 1) if can_upgrade else (0.5, 0.5, 0.5, 1),
		)
		upgrade_btn.bind(on_press=lambda x, tid=talent_id: self._upgrade_talent(tid))

		widget.add_widget(info_layout)
		widget.add_widget(upgrade_btn)

		return widget

	def _upgrade_talent(self, talent_id):
		"""Mejora un talento específico."""
		if self.real_game_state and self.real_game_state.upgrade_talent(talent_id):
			logging.info(f"Combat talent {talent_id} upgraded")
			# Refrescar la pestaña de talentos
			if self.current_tab == "talents":
				self._switch_tab("talents")
		else:
			logging.warning(f"Could not upgrade talent {talent_id}")

	def _show_equipment_content(self):
		"""Muestra el contenido de equipamiento dentro del combate."""
		# Obtener el equipment_manager del GameState
		if self.real_game_state and hasattr(self.real_game_state, "equipment_manager"):
			equipment_manager = self.real_game_state.equipment_manager

			# Crear una instancia de EquipmentScreen embebida
			from ui.screens.equipment_screen import EquipmentScreen

			# Crear la pantalla de equipamiento sin el layout de Screen
			equipment_content = self._create_embedded_equipment_screen(equipment_manager)
			self.content_area.add_widget(equipment_content)
		else:
			# Fallback: mensaje de error
			error_label = Label(
				text="Sistema de equipamiento no disponible.\nAsegúrate de estar en una partida válida.",
				font_size="16sp",
				text_size=(400, None),
				halign="center",
				valign="middle",
			)
			self.content_area.add_widget(error_label)

	def _create_embedded_equipment_screen(self, equipment_manager):
		"""Crea el contenido de equipamiento embebido en combate."""
		# Importar las clases necesarias
		from ui.screens.equipment_screen import EquipmentSlot, InventoryItem
		from core.equipment import EquipmentType, Rarity

		main_layout = BoxLayout(orientation="horizontal", spacing=10, padding=10)

		# Panel izquierdo - Equipamiento y estadísticas
		left_panel = BoxLayout(orientation="vertical", size_hint=(0.4, 1), spacing=10)

		# Título con botón volver (opcional en el futuro)
		title_layout = BoxLayout(orientation="horizontal", size_hint=(1, 0.1))
		title_label = Label(
			text="[size=20][b]🎒 Equipamiento[/b][/size]",
			markup=True,
			halign="center",
		)
		title_layout.add_widget(title_label)
		left_panel.add_widget(title_layout)

		# Slots de equipamiento
		equipment_layout = BoxLayout(orientation="vertical", size_hint=(1, 0.5), spacing=5)

		for eq_type in EquipmentType:
			slot = EquipmentSlot(eq_type)
			# Establecer equipamiento actual si existe
			equipped_item = equipment_manager.equipped_items.get(eq_type)
			if equipped_item:
				slot.set_equipment(equipped_item)
			equipment_layout.add_widget(slot)

		left_panel.add_widget(equipment_layout)

		# Estadísticas del jugador
		stats_label = Label(
			text=self._get_player_stats_text(equipment_manager),
			text_size=(None, None),
			halign="left",
			valign="top",
			size_hint=(1, 0.4),
		)
		left_panel.add_widget(stats_label)

		main_layout.add_widget(left_panel)

		# Panel derecho - Inventario simplificado
		right_panel = BoxLayout(orientation="vertical", size_hint=(0.6, 1), spacing=10)

		# Título del inventario
		inv_title = Label(
			text="[size=18][b]📦 Inventario[/b][/size]",
			markup=True,
			size_hint=(1, 0.1),
			halign="center",
		)
		right_panel.add_widget(inv_title)

		# Lista del inventario
		scroll = ScrollView(size_hint=(1, 0.9))
		inventory_layout = GridLayout(cols=1, spacing=2, size_hint_y=None)
		inventory_layout.bind(minimum_height=inventory_layout.setter("height"))

		# Mostrar items del inventario
		for item in equipment_manager.inventory:
			item_widget = self._create_simple_inventory_item(item, equipment_manager)
			inventory_layout.add_widget(item_widget)

		scroll.add_widget(inventory_layout)
		right_panel.add_widget(scroll)

		main_layout.add_widget(right_panel)

		return main_layout

	def _get_player_stats_text(self, equipment_manager):
		"""Obtiene el texto de estadísticas del jugador."""
		stats = equipment_manager.player_stats

		return f"""[b]Estadísticas del Jugador[/b]

[color=ffaa44]⚔️ Ataque:[/color] {stats.get_total_attack():.1f}
[color=4488ff]🛡️ Defensa:[/color] {stats.get_total_defense():.1f}
[color=ff4444]❤️ Vida:[/color] {stats.get_total_health():.1f}
[color=ffff44]🍀 Crítico:[/color] {stats.get_total_critical_chance() * 100:.1f}%
[color=ff8844]💥 Daño Crítico:[/color] {stats.get_total_critical_damage() * 100:.1f}%
[color=44ff44]📈 Bonus Producción:[/color] {stats.equipment_production_bonus * 100:.1f}%"""

	def _create_simple_inventory_item(self, equipment, equipment_manager):
		"""Crea un widget simple para un item del inventario."""
		from core.equipment import Rarity

		item_layout = BoxLayout(
			orientation="horizontal", size_hint_y=None, height=60, spacing=10, padding=5
		)

		# Color de fondo según rareza
		rarity_colors = {
			Rarity.COMMON: (0.4, 0.4, 0.4, 0.3),
			Rarity.RARE: (0.2, 0.3, 0.6, 0.3),
			Rarity.EPIC: (0.4, 0.2, 0.6, 0.3),
			Rarity.LEGENDARY: (0.6, 0.4, 0.2, 0.3),
		}

		# Información del item
		info_text = (
			f"[b]{equipment.name}[/b]\nNivel {equipment.level} | {equipment.rarity.value.title()}"
		)
		info_label = Label(
			text=info_text,
			markup=True,
			text_size=(300, None),
			halign="left",
			valign="center",
			size_hint_x=0.7,
		)

		# Botón de equipar
		equip_btn = Button(text="Equipar", size_hint_x=0.3, size_hint_y=1)
		equip_btn.bind(
			on_press=lambda x: self._equip_item_from_combat(equipment, equipment_manager)
		)

		item_layout.add_widget(info_label)
		item_layout.add_widget(equip_btn)

		return item_layout

	def _equip_item_from_combat(self, equipment, equipment_manager):
		"""Equipa un item desde la pantalla de combate."""
		success = equipment_manager.equip_item(equipment)
		if success:
			# Refrescar la pantalla de equipamiento
			if self.current_tab == "equipment":
				self._switch_tab("equipment")
		else:
			logging.warning(f"No se pudo equipar {equipment.name}")

	def _create_header(self) -> BoxLayout:
		"""Crea el header con stats del jugador."""
		header = BoxLayout(orientation="vertical", size_hint_y=0.2, spacing=10)

		# Primera fila: Level, Oro, XP, Daño
		stats_row = BoxLayout(orientation="horizontal", size_hint_y=0.5, spacing=20)

		# Nivel de mazmorra
		self.level_label = Label(
			text=f"Nivel: {self.dungeon_level}",
			font_size="18sp",
			bold=True,
			color=(1, 1, 0, 1),  # Amarillo
		)
		stats_row.add_widget(self.level_label)

		# Oro
		self.gold_label = Label(
			text=f"Oro: {self.player_gold}",
			font_size="16sp",
			color=(1, 0.8, 0, 1),  # Dorado
		)
		stats_row.add_widget(self.gold_label)

		# Experiencia
		self.exp_label = Label(
			text=f"XP: {self.player_exp}",
			font_size="16sp",
			color=(0.5, 1, 0.5, 1),  # Verde claro
		)
		stats_row.add_widget(self.exp_label)

		# Daño del jugador
		self.damage_label = Label(
			text=f"Daño: {self.player_damage}",
			font_size="16sp",
			color=(1, 0.3, 0.3, 1),  # Rojo
		)
		stats_row.add_widget(self.damage_label)

		header.add_widget(stats_row)

		# Segunda fila: HP del jugador y progreso del nivel
		hp_row = BoxLayout(orientation="horizontal", size_hint_y=0.5, spacing=20)

		# HP del jugador
		player_hp_container = BoxLayout(orientation="horizontal", size_hint_x=0.6, spacing=10)

		player_hp_label = Label(text="Vida:", font_size="14sp", size_hint_x=0.2)
		player_hp_container.add_widget(player_hp_label)

		self.player_hp_bar = ProgressBar(
			max=self.player_max_hp, value=self.player_current_hp, size_hint_x=0.6
		)
		player_hp_container.add_widget(self.player_hp_bar)

		self.player_hp_label = Label(
			text=f"{self.player_current_hp}/{self.player_max_hp}", font_size="14sp", size_hint_x=0.2
		)
		player_hp_container.add_widget(self.player_hp_label)

		hp_row.add_widget(player_hp_container)

		# Progreso del nivel de mazmorra
		self.level_progress_label = Label(
			text=f"Progreso: {self.enemies_defeated_in_level}/{self.enemies_needed_for_next_level}",
			font_size="14sp",
			size_hint_x=0.4,
			color=(0.7, 0.7, 1, 1),  # Azul claro
		)
		hp_row.add_widget(self.level_progress_label)

		header.add_widget(hp_row)

		return header

	def _create_combat_area(self) -> BoxLayout:
		"""Crea el área central donde aparece el enemigo."""
		combat_area = BoxLayout(orientation="vertical", size_hint_y=0.7, spacing=15)

		# Nombre del enemigo
		self.enemy_name_label = Label(text="", font_size="24sp", bold=True, size_hint_y=0.1)
		combat_area.add_widget(self.enemy_name_label)

		# Imagen del enemigo (clickeable)
		self.enemy_image = Button(text="", size_hint=(0.6, 0.6), pos_hint={"center_x": 0.5})
		self.enemy_image.bind(on_press=self._on_enemy_clicked)
		combat_area.add_widget(self.enemy_image)

		# Barra de vida del enemigo
		hp_container = BoxLayout(orientation="vertical", size_hint_y=0.2, spacing=5)

		self.enemy_hp_label = Label(text="", font_size="16sp", size_hint_y=0.4)
		hp_container.add_widget(self.enemy_hp_label)

		self.enemy_hp_bar = ProgressBar(max=100, value=100, size_hint_y=0.6)
		hp_container.add_widget(self.enemy_hp_bar)

		combat_area.add_widget(hp_container)

		return combat_area

	def _create_footer(self) -> BoxLayout:
		"""Crea el footer con controles."""
		footer = BoxLayout(orientation="horizontal", size_hint_y=0.1, spacing=20)

		# Botón de auto-combat toggle
		auto_combat_btn = Button(
			text="Auto-Combat: ON" if self.auto_combat_active else "Auto-Combat: OFF",
			size_hint_x=0.5,
		)
		auto_combat_btn.bind(on_press=self._toggle_auto_combat)
		footer.add_widget(auto_combat_btn)

		# Información del estado
		status_label = Label(
			text="Haz click en el enemigo para atacar", size_hint_x=0.5, font_size="14sp"
		)
		footer.add_widget(status_label)

		return footer

	def _spawn_enemy(self):
		"""Genera un nuevo enemigo aleatorio."""
		enemy_data = random.choice(self.enemy_types)
		enemy_name, enemy_sprite = enemy_data

		self.current_enemy = Enemy(enemy_name, enemy_sprite, self.dungeon_level)
		self._update_enemy_display()

		logging.info(f"Spawned enemy: {enemy_name} (Level {self.dungeon_level})")

	def _update_enemy_display(self):
		"""Actualiza la visualización del enemigo actual."""
		if not self.current_enemy:
			return

		enemy = self.current_enemy

		# Actualizar nombre
		self.enemy_name_label.text = f"{enemy.name} (Nivel {enemy.level})"

		# Actualizar imagen del enemigo
		sprite_path = enemy.get_sprite_path()
		if os.path.exists(sprite_path):
			# Crear background para la imagen
			with self.enemy_image.canvas.before:
				Color(0.2, 0.2, 0.3, 1)
				Rectangle(pos=self.enemy_image.pos, size=self.enemy_image.size)

			# Cargar imagen como background
			try:
				self.enemy_image.background_normal = sprite_path
			except Exception as e:
				logging.warning(f"Could not load enemy sprite {sprite_path}: {e}")
				self.enemy_image.text = enemy.name[:3].upper()
		else:
			self.enemy_image.text = enemy.name[:3].upper()

		# Actualizar barra de vida
		hp_percentage = (enemy.stats.current_hp / enemy.stats.max_hp) * 100
		self.enemy_hp_bar.value = hp_percentage
		self.enemy_hp_label.text = f"HP: {enemy.stats.current_hp}/{enemy.stats.max_hp}"

	def _on_enemy_clicked(self, button):
		"""Maneja el click en el enemigo para atacar."""
		if not self.current_enemy or not self.current_enemy.stats.is_alive():
			return

		# Aplicar daño
		damage_dealt = self._deal_damage_to_enemy(self.player_damage)

		# Efecto visual de daño
		self._show_damage_effect(damage_dealt)

		# Verificar si el enemigo murió
		if not self.current_enemy.stats.is_alive():
			self._enemy_defeated()

	def _deal_damage_to_enemy(self, damage: int) -> int:
		"""Aplica daño al enemigo actual."""
		if not self.current_enemy:
			return 0

		# Calcular crítico
		is_critical = random.random() < 0.1  # 10% de crítico para jugador
		if is_critical:
			damage = int(damage * 2.0)

		actual_damage = self.current_enemy.stats.take_damage(damage)
		self._update_enemy_display()

		return actual_damage

	def _show_damage_effect(self, damage: int):
		"""Muestra efectos visuales de daño."""
		# Animación simple: flash del botón del enemigo
		original_color = self.enemy_image.background_color

		# Flash rojo
		self.enemy_image.background_color = (1, 0.5, 0.5, 1)

		def restore_color(dt):
			self.enemy_image.background_color = original_color

		Clock.schedule_once(restore_color, 0.2)

		logging.debug(f"Dealt {damage} damage to enemy")

	def _enemy_defeated(self):
		"""Maneja la derrota de un enemigo."""
		if not self.current_enemy:
			return

		enemy = self.current_enemy

		# NUEVO: Llamar al callback del CombatManager si está disponible
		logging.info(f"DEBUG: _enemy_defeated - self.combat_manager: {self.combat_manager}")
		if self.combat_manager:
			logging.info(
				f"DEBUG: _enemy_defeated - has on_enemy_defeated_callback attr: {hasattr(self.combat_manager, 'on_enemy_defeated_callback')}"
			)
			if hasattr(self.combat_manager, "on_enemy_defeated_callback"):
				logging.info(
					f"DEBUG: _enemy_defeated - callback value: {self.combat_manager.on_enemy_defeated_callback}"
				)
				if self.combat_manager.on_enemy_defeated_callback:
					try:
						logging.info("DEBUG: CombatScreen triggering combat manager callback")
						# Determinar si es un boss
						is_boss = enemy.level > 50 or any(
							boss_keyword in enemy.name.lower()
							for boss_keyword in ["boss", "chief", "lord", "king", "dragon", "lich"]
						)
						self.combat_manager.on_enemy_defeated_callback(
							enemy_type=enemy.name,
							enemy_level=enemy.level,
							is_boss=is_boss,
						)
					except Exception as e:
						logging.error(f"Error calling combat manager callback: {e}")
				else:
					logging.warning("DEBUG: Callback is None")
			else:
				logging.warning("DEBUG: No on_enemy_defeated_callback attribute")
		else:
			logging.warning("DEBUG: No combat_manager")

		# Otorgar recompensas al GameState real si está disponible
		if self.real_game_state:
			# Añadir recursos al GameState
			from core.resources import ResourceType

			self.real_game_state.resource_manager.add_resource(
				ResourceType.COINS, enemy.gold_reward
			)
			self.real_game_state.add_experience(enemy.exp_reward)

			# Sincronizar coins tradicionales
			self.real_game_state.coins += enemy.gold_reward
			self.real_game_state.lifetime_coins += enemy.gold_reward

			# Obtener valores actualizados para UI
			self.player_gold = self.real_game_state.coins
			self.player_exp = self.real_game_state.player_experience
			self.player_level = self.real_game_state.player_level
		else:
			# Fallback: usar sistema local
			self.player_gold += enemy.gold_reward
			self.player_exp += enemy.exp_reward

		# Verificar level up
		self._check_level_up()

		# Actualizar UI
		self._update_player_stats_display()

		logging.info(f"Enemy defeated! +{enemy.gold_reward} gold, +{enemy.exp_reward} exp")

		# Spawn nuevo enemigo
		Clock.schedule_once(lambda dt: self._spawn_enemy(), 0.5)

	def _check_level_up(self):
		"""Verifica y maneja el level up del jugador."""
		exp_needed = self.player_level * 100  # 100 XP por nivel

		if self.player_exp >= exp_needed:
			self.player_level += 1
			self.player_exp -= exp_needed
			self.player_damage += 5  # +5 daño por nivel

			logging.info(f"Player leveled up! Now level {self.player_level}")

			# Efecto visual de level up
			self._show_level_up_effect()

	def _show_level_up_effect(self):
		"""Muestra efectos visuales de level up."""
		# Animación de brillo en las stats
		original_color = self.damage_label.color
		self.damage_label.color = (1, 1, 0, 1)  # Amarillo brillante

		def restore_color(dt):
			self.damage_label.color = original_color

		Clock.schedule_once(restore_color, 1.0)

	def _update_player_stats_display(self):
		"""Actualiza la visualización de las stats del jugador."""
		if self.gold_label:
			self.gold_label.text = f"Oro: {self.player_gold}"
		if self.exp_label:
			self.exp_label.text = f"XP: {self.player_exp}"
		if self.damage_label:
			self.damage_label.text = f"Daño: {self.player_damage}"
		if self.level_label:
			self.level_label.text = f"Nivel: {self.dungeon_level}"

	def _toggle_auto_combat(self, button):
		"""Alterna el auto-combat."""
		self.auto_combat_active = not self.auto_combat_active
		button.text = "Auto-Combat: ON" if self.auto_combat_active else "Auto-Combat: OFF"

		logging.info(f"Auto-combat {'enabled' if self.auto_combat_active else 'disabled'}")

	def on_enter(self, *args):
		"""Se ejecuta al entrar a la pantalla."""
		logging.info("Entered CombatScreen")

	def on_leave(self, *args):
		"""Se ejecuta al salir de la pantalla."""
		logging.info("Left CombatScreen")

	def _combat_tick(self, dt):
		"""Tick principal del combate - maneja ataques automáticos de ambos lados."""
		if not self.current_enemy or not self.current_enemy.stats.is_alive():
			return

		if self.player_current_hp <= 0:
			return  # Jugador muerto, no puede combatir

		import time

		current_time = time.time()

		# Auto-ataque del jugador (si está activado)
		if self.auto_combat_active:
			time_since_last_attack = current_time - self.last_player_attack
			attack_cooldown = 1.0 / self.player_attack_speed  # Tiempo entre ataques

			if time_since_last_attack >= attack_cooldown:
				auto_damage = max(1, self.player_damage // 2)  # 50% del daño manual
				self._deal_damage_to_enemy(auto_damage)
				self.last_player_attack = current_time

				if not self.current_enemy.stats.is_alive():
					self._enemy_defeated()
					return

		# Ataque del enemigo al jugador
		enemy_attack_speed = self.current_enemy.stats.speed
		time_since_enemy_attack = current_time - self.last_enemy_attack
		enemy_attack_cooldown = 1.0 / enemy_attack_speed

		if time_since_enemy_attack >= enemy_attack_cooldown:
			self._enemy_attacks_player()
			self.last_enemy_attack = current_time

	def _enemy_attacks_player(self):
		"""El enemigo ataca al jugador."""
		if not self.current_enemy or self.player_current_hp <= 0:
			return

		enemy_damage = max(1, self.current_enemy.stats.attack - self.player_defense)
		self.player_current_hp = max(0, self.player_current_hp - enemy_damage)

		# Actualizar UI de vida del jugador
		self._update_player_hp_display()

		# Efecto visual de daño recibido
		self._show_player_damage_effect()

		logging.debug(
			f"Player took {enemy_damage} damage. HP: {self.player_current_hp}/{self.player_max_hp}"
		)

		# Verificar si el jugador murió
		if self.player_current_hp <= 0:
			self._player_died()

	def _update_player_hp_display(self):
		"""Actualiza la visualización de la vida del jugador."""
		if self.player_hp_bar and self.player_hp_label:
			self.player_hp_bar.value = self.player_current_hp
			self.player_hp_label.text = f"{self.player_current_hp}/{self.player_max_hp}"

			# Cambiar color según el % de vida
			hp_percentage = self.player_current_hp / self.player_max_hp
			if hp_percentage > 0.6:
				color = (0, 1, 0, 1)  # Verde
			elif hp_percentage > 0.3:
				color = (1, 1, 0, 1)  # Amarillo
			else:
				color = (1, 0, 0, 1)  # Rojo

			self.player_hp_label.color = color

	def _show_player_damage_effect(self):
		"""Muestra efectos visuales cuando el jugador recibe daño."""
		# Flash rojo en toda la pantalla sería ideal, pero por simplicidad usamos el label
		if self.player_hp_label:
			original_color = self.player_hp_label.color
			self.player_hp_label.color = (1, 0, 0, 1)  # Rojo

			def restore_color(dt):
				hp_percentage = self.player_current_hp / self.player_max_hp
				if hp_percentage > 0.6:
					color = (0, 1, 0, 1)  # Verde
				elif hp_percentage > 0.3:
					color = (1, 1, 0, 1)  # Amarillo
				else:
					color = (1, 0, 0, 1)  # Rojo
				self.player_hp_label.color = color

			Clock.schedule_once(restore_color, 0.3)

	def _player_died(self):
		"""Maneja la muerte del jugador."""
		logging.info("Player died!")

		# Penalizaciones por muerte
		levels_to_lose = min(3, self.dungeon_level - 1)  # Retroceder máximo 3 niveles
		gold_to_lose = int(self.player_gold * 0.2)  # Perder 20% del oro

		self.dungeon_level = max(1, self.dungeon_level - levels_to_lose)
		self.player_gold = max(0, self.player_gold - gold_to_lose)

		# Regenerar vida del jugador
		self.player_current_hp = self.player_max_hp

		# Reset progreso del nivel actual
		self.enemies_defeated_in_level = 0

		# Spawn nuevo enemigo del nivel actual
		self._spawn_enemy()

		# Actualizar UI
		self._update_all_displays()

		logging.info(f"Player respawned at level {self.dungeon_level}, lost {gold_to_lose} gold")

	def _enemy_defeated(self):
		"""Maneja la derrota de un enemigo."""
		if not self.current_enemy:
			return

		enemy = self.current_enemy

		# NUEVO: Llamar al callback del CombatManager si está disponible
		logging.info(
			f"DEBUG: _enemy_defeated (second method) - self.combat_manager: {self.combat_manager}"
		)
		if self.combat_manager:
			logging.info(
				f"DEBUG: _enemy_defeated - has on_enemy_defeated_callback attr: {hasattr(self.combat_manager, 'on_enemy_defeated_callback')}"
			)
			if hasattr(self.combat_manager, "on_enemy_defeated_callback"):
				logging.info(
					f"DEBUG: _enemy_defeated - callback value: {self.combat_manager.on_enemy_defeated_callback}"
				)
				if self.combat_manager.on_enemy_defeated_callback:
					try:
						logging.info("DEBUG: CombatScreen triggering combat manager callback")
						# Determinar si es un boss
						is_boss = enemy.level > 50 or any(
							boss_keyword in enemy.name.lower()
							for boss_keyword in ["boss", "chief", "lord", "king", "dragon", "lich"]
						)
						self.combat_manager.on_enemy_defeated_callback(
							enemy_type=enemy.name,
							enemy_level=enemy.level,
							is_boss=is_boss,
						)
					except Exception as e:
						logging.error(f"Error calling combat manager callback: {e}")
				else:
					logging.warning("DEBUG: Callback is None")
			else:
				logging.warning("DEBUG: No on_enemy_defeated_callback attribute")
		else:
			logging.warning("DEBUG: No combat_manager")

		# Otorgar recompensas
		self.player_gold += enemy.gold_reward
		self.player_exp += enemy.exp_reward

		# Incrementar progreso del nivel
		self.enemies_defeated_in_level += 1

		# Verificar level up del jugador
		self._check_level_up()

		# Verificar si debe subir nivel de mazmorra
		if self.enemies_defeated_in_level >= self.enemies_needed_for_next_level:
			self._advance_dungeon_level()

		# Actualizar UI
		self._update_all_displays()

		logging.info(f"Enemy defeated! +{enemy.gold_reward} gold, +{enemy.exp_reward} exp")

		# Spawn nuevo enemigo
		Clock.schedule_once(lambda dt: self._spawn_enemy(), 0.5)

	def _advance_dungeon_level(self):
		"""Avanza automáticamente al siguiente nivel de mazmorra."""
		self.dungeon_level += 1
		self.enemies_defeated_in_level = 0

		# Aumentar dificultad: más enemigos necesarios para niveles altos
		if self.dungeon_level % 10 == 0:  # Cada 10 niveles
			self.enemies_needed_for_next_level += 2

		logging.info(f"Advanced to dungeon level {self.dungeon_level}")

	def _update_all_displays(self):
		"""Actualiza todas las visualizaciones de stats."""
		self._update_player_stats_display()
		self._update_player_hp_display()
		self._update_level_progress_display()

	def _update_level_progress_display(self):
		"""Actualiza la visualización del progreso del nivel."""
		if self.level_progress_label:
			self.level_progress_label.text = (
				f"Progreso: {self.enemies_defeated_in_level}/{self.enemies_needed_for_next_level}"
			)
