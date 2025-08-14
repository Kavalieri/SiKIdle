"""
Pantalla de combate renovada para SiKIdle.

Interfaz completamente rediseñada con fondos dinámicos, efectos visuales,
animaciones de daño y elementos UI modernos inspirados en los mejores idle clickers.
"""

import logging
import random
from typing import Dict, Any, Optional, Tuple

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.progressbar import ProgressBar
from kivy.uix.image import Image
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.graphics import Color, Rectangle, RoundedRectangle, Ellipse
from kivy.core.window import Window

from core.game import get_game_state
from core.visual_assets import VisualAssetManager, BackgroundType, EffectType
from core.worlds import WorldType
from ui.visual_effects import VisualEffectsManager, DamageNumberEffect, EnemyEffectRing

logger = logging.getLogger(__name__)


class ModernEnemyWidget(FloatLayout):
	"""Widget moderno para mostrar enemigos con efectos visuales."""

	def __init__(self, enemy_data: Dict, **kwargs):
		super().__init__(**kwargs)
		self.enemy_data = enemy_data
		self.visual_manager = VisualAssetManager()
		self.size_hint = (None, None)
		self.size = (200, 250)

		self._build_enemy_display()
		self._setup_animations()

	def _build_enemy_display(self):
		"""Construye la visualización del enemigo."""
		# Fondo del enemigo con bordes redondeados
		with self.canvas.before:
			Color(0.1, 0.1, 0.1, 0.7)
			self.bg_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[10, 10, 10, 10])

		self.bind(pos=self._update_bg, size=self._update_bg)

		# Imagen del enemigo (usar sprite real)
		self.enemy_image = Image(
			source="assets/enemies/orc.png",  # Sprite por defecto
			size_hint=(0.8, 0.6),
			pos_hint={"center_x": 0.5, "top": 0.9},
			allow_stretch=True,
			keep_ratio=True,
		)
		self.add_widget(self.enemy_image)

		# Nombre del enemigo
		self.name_label = Label(
			text=self.enemy_data.get("name", "Enemigo"),
			font_size="16sp",
			bold=True,
			color=(1, 1, 1, 1),
			size_hint=(1, None),
			height=30,
			pos_hint={"center_x": 0.5, "y": 0.55},
			halign="center",
		)
		self.add_widget(self.name_label)

		# Nivel del enemigo
		self.level_label = Label(
			text=f"Nivel {self.enemy_data.get('level', 1)}",
			font_size="12sp",
			color=(0.8, 0.8, 0.8, 1),
			size_hint=(1, None),
			height=20,
			pos_hint={"center_x": 0.5, "y": 0.45},
			halign="center",
		)
		self.add_widget(self.level_label)

		# Barra de vida
		hp_layout = BoxLayout(
			orientation="vertical",
			size_hint=(0.9, None),
			height=40,
			pos_hint={"center_x": 0.5, "y": 0.05},
			spacing=2,
		)

		hp_label = Label(
			text="HP", font_size="10sp", color=(1, 1, 1, 1), size_hint=(1, None), height=15
		)
		hp_layout.add_widget(hp_label)

		self.hp_bar = ProgressBar(
			max=self.enemy_data.get("max_hp", 100),
			value=self.enemy_data.get("current_hp", 100),
			size_hint=(1, None),
			height=20,
		)

		# Colorear la barra de vida
		with self.hp_bar.canvas.before:
			Color(0.8, 0.2, 0.2, 1)  # Rojo para la vida

		hp_layout.add_widget(self.hp_bar)
		self.add_widget(hp_layout)

	def _update_bg(self, *args):
		"""Actualiza el fondo del widget."""
		self.bg_rect.pos = self.pos
		self.bg_rect.size = self.size

	def _setup_animations(self):
		"""Configura animaciones idle del enemigo."""
		# Animación de respiración sutil
		self.breathing_anim = Animation(
			size=(205, 255), duration=2.0, transition="in_out_sine"
		) + Animation(size=(200, 250), duration=2.0, transition="in_out_sine")
		self.breathing_anim.repeat = True
		self.breathing_anim.start(self)

	def take_damage(self, damage: int, is_critical: bool = False):
		"""Aplica daño al enemigo con efectos visuales."""
		# Actualizar HP
		current_hp = max(0, self.hp_bar.value - damage)
		self.hp_bar.value = current_hp

		# Animación de daño (shake)
		original_pos = self.pos
		shake_anim = (
			Animation(pos=(original_pos[0] + 5, original_pos[1]), duration=0.05)
			+ Animation(pos=(original_pos[0] - 5, original_pos[1]), duration=0.05)
			+ Animation(pos=(original_pos[0] + 3, original_pos[1]), duration=0.05)
			+ Animation(pos=original_pos, duration=0.05)
		)
		shake_anim.start(self)

		# Flash rojo
		with self.canvas.after:
			Color(1, 0, 0, 0.5)
			self.damage_flash = Rectangle(pos=self.pos, size=self.size)

		# Desvanecer el flash
		flash_anim = Animation(opacity=0, duration=0.3)
		flash_anim.bind(on_complete=self._remove_flash)
		flash_anim.start(self)

		return current_hp <= 0  # Retorna True si el enemigo murió

	def _remove_flash(self, *args):
		"""Remueve el flash de daño."""
		if hasattr(self, "damage_flash"):
			try:
				self.canvas.after.remove(self.damage_flash)
			except ValueError:
				# El flash ya fue removido, ignorar
				pass

	def apply_visual_effect(self, effect_type: EffectType):
		"""Aplica un efecto visual al enemigo."""
		effect_ring = EnemyEffectRing(effect_type)
		self.parent.add_widget(effect_ring)
		effect_ring.play(self.center)


class ModernCombatHUD(BoxLayout):
	"""HUD moderno para la pantalla de combate."""

	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.orientation = "vertical"
		self.size_hint = (1, None)
		self.height = 120
		self.spacing = 10
		self.padding = [20, 10, 20, 10]

		# Fondo semi-transparente
		with self.canvas.before:
			Color(0, 0, 0, 0.7)
			self.bg_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[15, 15, 0, 0])

		self.bind(pos=self._update_bg, size=self._update_bg)

		self._build_hud()

	def _update_bg(self, *args):
		"""Actualiza el fondo del HUD."""
		self.bg_rect.pos = self.pos
		self.bg_rect.size = self.size

	def _build_hud(self):
		"""Construye los elementos del HUD."""
		# Información del jugador
		player_info = BoxLayout(orientation="horizontal", size_hint=(1, 0.5), spacing=20)

		# Nivel del jugador
		level_layout = BoxLayout(orientation="vertical", size_hint=(0.3, 1))
		level_layout.add_widget(
			Label(text="NIVEL", font_size="12sp", color=(0.8, 0.8, 0.8, 1), size_hint=(1, 0.4))
		)
		self.level_label = Label(
			text="1", font_size="20sp", bold=True, color=(1, 1, 1, 1), size_hint=(1, 0.6)
		)
		level_layout.add_widget(self.level_label)
		player_info.add_widget(level_layout)

		# Oro
		gold_layout = BoxLayout(orientation="vertical", size_hint=(0.35, 1))
		gold_layout.add_widget(
			Label(text="💰 ORO", font_size="12sp", color=(1, 0.8, 0, 1), size_hint=(1, 0.4))
		)
		self.gold_label = Label(
			text="0", font_size="18sp", bold=True, color=(1, 0.8, 0, 1), size_hint=(1, 0.6)
		)
		gold_layout.add_widget(self.gold_label)
		player_info.add_widget(gold_layout)

		# DPS
		dps_layout = BoxLayout(orientation="vertical", size_hint=(0.35, 1))
		dps_layout.add_widget(
			Label(text="⚔️ DPS", font_size="12sp", color=(1, 0.4, 0.4, 1), size_hint=(1, 0.4))
		)
		self.dps_label = Label(
			text="1", font_size="18sp", bold=True, color=(1, 0.4, 0.4, 1), size_hint=(1, 0.6)
		)
		dps_layout.add_widget(self.dps_label)
		player_info.add_widget(dps_layout)

		self.add_widget(player_info)

		# Información del mundo actual
		world_info = BoxLayout(orientation="horizontal", size_hint=(1, 0.5), spacing=10)

		# Mundo actual
		self.world_label = Label(
			text="🌲 Bosque Encantado - Nivel 1",
			font_size="16sp",
			bold=True,
			color=(0.4, 0.8, 0.4, 1),
			size_hint=(0.7, 1),
			halign="left",
			valign="middle",
		)
		self.world_label.text_size = (None, None)
		world_info.add_widget(self.world_label)

		# Progreso del mundo
		progress_layout = BoxLayout(orientation="vertical", size_hint=(0.3, 1))
		progress_layout.add_widget(
			Label(text="PROGRESO", font_size="10sp", color=(0.7, 0.7, 0.7, 1), size_hint=(1, 0.4))
		)

		self.world_progress = ProgressBar(max=50, value=1, size_hint=(1, 0.6))
		progress_layout.add_widget(self.world_progress)
		world_info.add_widget(progress_layout)

		self.add_widget(world_info)

	def update_player_stats(self, level: int, gold: int, dps: float):
		"""Actualiza las estadísticas del jugador."""
		self.level_label.text = str(level)
		self.gold_label.text = self._format_number(gold)
		self.dps_label.text = self._format_number(dps)

	def update_world_info(self, world_name: str, current_level: int, max_level: int):
		"""Actualiza la información del mundo."""
		self.world_label.text = f"🌍 {world_name} - Nivel {current_level}"
		self.world_progress.value = current_level
		self.world_progress.max = max_level

	def _format_number(self, number: float) -> str:
		"""Formatea números grandes de manera legible."""
		if number >= 1_000_000_000:
			return f"{number / 1_000_000_000:.1f}B"
		elif number >= 1_000_000:
			return f"{number / 1_000_000:.1f}M"
		elif number >= 1_000:
			return f"{number / 1_000:.1f}K"
		else:
			return str(int(number))


class EnhancedCombatScreen(Screen):
	"""Pantalla de combate completamente renovada."""

	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.name = "enhanced_combat"

		# Managers
		self.visual_manager = VisualAssetManager()
		self.effects_manager = None  # Se inicializa después

		# Estado del combate
		self.current_enemy = None
		self.auto_attack_event = None

		# Configurar fondo dinámico
		with self.canvas.before:
			self.bg_image = Rectangle(
				source=self.visual_manager.get_background_path(BackgroundType.FOREST),
				pos=self.pos,
				size=self.size,
			)

		self.bind(pos=self._update_bg, size=self._update_bg)

		self._build_interface()

		logger.info("EnhancedCombatScreen inicializada")

	def _update_bg(self, *args):
		"""Actualiza el fondo de la pantalla."""
		self.bg_image.pos = self.pos
		self.bg_image.size = self.size

	def _build_interface(self):
		"""Construye la interfaz de la pantalla."""
		main_layout = BoxLayout(orientation="vertical")

		# Área de combate principal
		combat_area = FloatLayout()

		# Área para enemigos (centro de la pantalla)
		self.enemy_area = FloatLayout(
			size_hint=(1, 0.6), pos_hint={"center_x": 0.5, "center_y": 0.6}
		)
		combat_area.add_widget(self.enemy_area)

		# Botón de ataque principal (grande y llamativo)
		self.attack_button = Button(
			text="⚔️ ATACAR",
			size_hint=(None, None),
			size=(150, 80),
			pos_hint={"center_x": 0.5, "y": 0.1},
			font_size="20sp",
			bold=True,
			background_color=(0.8, 0.2, 0.2, 1),
		)
		self.attack_button.bind(on_press=self._on_attack_button)
		combat_area.add_widget(self.attack_button)

		main_layout.add_widget(combat_area)

		# HUD moderno en la parte inferior
		self.hud = ModernCombatHUD()
		main_layout.add_widget(self.hud)

		self.add_widget(main_layout)

		# Inicializar manager de efectos
		self.effects_manager = VisualEffectsManager(combat_area)

	def _on_attack_button(self, button):
		"""Maneja el clic en el botón de ataque."""
		if not self.current_enemy:
			self._spawn_new_enemy()
			return

		# Calcular daño
		game_state = get_game_state()
		base_damage = 10  # Daño base
		is_critical = random.random() < 0.1  # 10% crítico

		damage = base_damage * (2 if is_critical else 1)

		# Aplicar daño al enemigo
		enemy_died = self.current_enemy.take_damage(damage, is_critical)

		# Mostrar número de daño
		enemy_pos = self.current_enemy.center
		self.effects_manager.show_damage_number(damage, enemy_pos, is_critical)

		if enemy_died:
			self._on_enemy_defeated()

	def _spawn_new_enemy(self):
		"""Genera un nuevo enemigo."""
		# Lista de enemigos disponibles con sus sprites
		enemy_types = [
			{"name": "Hormiga Gigante", "sprite": "assets/enemies/ant1.png"},
			{"name": "Escarabajo", "sprite": "assets/enemies/beetle.png"},
			{"name": "Ciempiés", "sprite": "assets/enemies/centipede.png"},
			{"name": "Orco", "sprite": "assets/enemies/orc.png"},
			{"name": "Esqueleto", "sprite": "assets/enemies/skeleton.png"},
			{"name": "Araña", "sprite": "assets/enemies/spider.png"},
		]

		# Seleccionar enemigo aleatorio
		selected_enemy = random.choice(enemy_types)

		# Datos del enemigo
		enemy_data = {
			"name": selected_enemy["name"],
			"level": 1,
			"max_hp": 100,
			"current_hp": 100,
			"sprite": selected_enemy["sprite"],
		}

		# Crear widget del enemigo
		self.current_enemy = ModernEnemyWidget(enemy_data)
		self.current_enemy.pos_hint = {"center_x": 0.5, "center_y": 0.5}

		self.enemy_area.add_widget(self.current_enemy)

		# Aplicar efecto visual según el mundo
		game_state = get_game_state()
		if hasattr(game_state, "world_manager"):
			active_world = game_state.world_manager.get_active_world()
			if active_world:
				effects = self.visual_manager.get_enemy_effects(
					active_world.world_type.value, "basic"
				)
				if effects:
					self.current_enemy.apply_visual_effect(effects[0])

		logger.info(f"Nuevo enemigo generado: {enemy_data['name']}")

	def _on_enemy_defeated(self):
		"""Maneja la derrota de un enemigo."""
		if self.current_enemy:
			# Remover enemigo actual
			self.enemy_area.remove_widget(self.current_enemy)
			self.current_enemy = None

			# Recompensas (placeholder)
			gold_reward = random.randint(5, 15)
			exp_reward = random.randint(8, 20)

			# Actualizar HUD
			self.hud.update_player_stats(1, gold_reward, 10)

			# Generar nuevo enemigo después de un breve delay
			Clock.schedule_once(lambda dt: self._spawn_new_enemy(), 0.5)

			logger.info(f"Enemigo derrotado. Recompensas: {gold_reward} oro, {exp_reward} exp")

	def on_enter(self):
		"""Se ejecuta cuando se entra a la pantalla."""
		# Actualizar fondo según el mundo activo
		game_state = get_game_state()
		if hasattr(game_state, "world_manager"):
			active_world = game_state.world_manager.get_active_world()
			if active_world:
				bg_path = game_state.world_manager.get_world_background_path(
					active_world.world_type
				)
				self.bg_image.source = bg_path

				# Actualizar información del mundo en el HUD
				world_info = game_state.world_manager.get_world_progress_info(
					active_world.world_type.value
				)
				self.hud.update_world_info(
					world_info.get(
						"name", "Mundo Desconocido"
					),  # Usar 'name' en lugar de 'world_name'
					world_info.get("current_level", 1),
					world_info.get("level_range", [1, 50])[1],
				)

		# Generar enemigo inicial si no hay uno
		if not self.current_enemy:
			self._spawn_new_enemy()

		logger.info("Entrando a EnhancedCombatScreen")

	def on_leave(self):
		"""Se ejecuta cuando se sale de la pantalla."""
		# Limpiar efectos visuales
		if self.effects_manager:
			self.effects_manager.clear_all_effects()

		logger.info("Saliendo de EnhancedCombatScreen")
