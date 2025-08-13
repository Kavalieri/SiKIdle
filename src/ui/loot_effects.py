"""
Efectos Visuales para Sistema de Loot

Este módulo implementa efectos visuales mejorados para la obtención de loot,
incluyendo popups, animaciones y sonidos diferenciados por rareza.
"""

import logging
from typing import Optional, Callable
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.graphics import Color, Rectangle
from kivy.uix.widget import Widget

logger = logging.getLogger(__name__)


class LootNotificationPopup(Popup):
	"""
	Popup especializado para mostrar notificaciones de loot obtenido

	Características:
	- Colores según rareza del ítem
	- Auto-close después de tiempo determinado
	- Animaciones de entrada y salida
	"""

	def __init__(self, item, enemy_type: str, is_boss: bool, **kwargs):
		"""
		Inicializa el popup de notificación de loot

		Args:
		    item: Ítem obtenido
		    enemy_type: Tipo de enemigo que dropeo el ítem
		    is_boss: Si el enemigo era un boss
		"""
		# Configurar tamaño y posición
		super().__init__(
			title="¡Loot Obtenido!",
			size_hint=(0.4, 0.3),
			pos_hint={"center_x": 0.5, "center_y": 0.7},
			auto_dismiss=True,
			**kwargs,
		)

		self.item = item
		self.enemy_type = enemy_type
		self.is_boss = is_boss

		# Configurar colores según rareza
		self.rarity_colors = {
			"common": (0.8, 0.8, 0.8, 0.9),  # Gris claro
			"rare": (0.3, 0.8, 0.3, 0.9),  # Verde
			"epic": (0.6, 0.3, 0.8, 0.9),  # Púrpura
			"legendary": (1.0, 0.6, 0.0, 0.9),  # Dorado
		}

		self.rarity_emojis = {"common": "🤍", "rare": "💚", "epic": "💙", "legendary": "🟣"}

		self.setup_content()
		self.setup_auto_close()

	def setup_content(self):
		"""Configura el contenido visual del popup"""
		content = BoxLayout(orientation="vertical", spacing=10, padding=[20, 20, 20, 20])

		# Color de fondo según rareza
		rarity_value = getattr(self.item.rarity, "value", "common")
		bg_color = self.rarity_colors.get(rarity_value, self.rarity_colors["common"])

		# Widget de fondo con color
		with content.canvas.before:
			Color(*bg_color)
			self.bg_rect = Rectangle(pos=content.pos, size=content.size)
		content.bind(pos=self._update_bg_rect, size=self._update_bg_rect)

		# Emoji y título de rareza
		emoji = self.rarity_emojis.get(rarity_value, "⭐")
		boss_text = " (BOSS)" if self.is_boss else ""

		title_label = Label(
			text=f"{emoji} {rarity_value.upper()} {emoji}",
			font_size="20sp",
			size_hint_y=0.3,
			bold=True,
		)
		content.add_widget(title_label)

		# Información del ítem
		item_name = getattr(self.item, "name", "Ítem Desconocido")
		item_info = Label(
			text=f"[b]{item_name}[/b]\n\nDropeado por:\n{self.enemy_type}{boss_text}",
			markup=True,
			text_size=(None, None),
			halign="center",
			size_hint_y=0.7,
		)
		content.add_widget(item_info)

		self.content = content

	def _update_bg_rect(self, instance, value):
		"""Actualiza el rectángulo de fondo"""
		self.bg_rect.pos = instance.pos
		self.bg_rect.size = instance.size

	def setup_auto_close(self):
		"""Configura el cierre automático del popup"""
		# Tiempo de cierre según rareza
		rarity_value = getattr(self.item.rarity, "value", "common")
		close_times = {"common": 2.0, "rare": 3.0, "epic": 4.0, "legendary": 5.0}

		close_time = close_times.get(rarity_value, 2.0)
		Clock.schedule_once(lambda dt: self.dismiss(), close_time)

	def open_with_animation(self):
		"""Abre el popup con animación de entrada"""
		self.opacity = 0
		self.open()

		# Animación de entrada
		anim = Animation(opacity=1.0, duration=0.3)
		anim.start(self)

		# Efecto especial para loot legendario
		rarity_value = getattr(self.item.rarity, "value", "common")
		if rarity_value == "legendary":
			# Efecto de parpadeo para legendarios
			blink = Animation(opacity=0.7, duration=0.2) + Animation(opacity=1.0, duration=0.2)
			blink.repeat = True
			blink.start(self)
			Clock.schedule_once(lambda dt: blink.stop(self), 3.0)


class LootFloatingText(Widget):
	"""
	Texto flotante que aparece sobre el área de combate cuando se obtiene loot

	Características:
	- Texto que se mueve hacia arriba y desaparece
	- Colores según rareza
	- Múltiples instancias simultáneas
	"""

	def __init__(self, text: str, rarity: str = "common", **kwargs):
		super().__init__(**kwargs)

		self.text = text
		self.rarity = rarity

		# Configurar colores
		self.colors = {
			"common": (0.8, 0.8, 0.8, 1.0),
			"rare": (0.3, 0.8, 0.3, 1.0),
			"epic": (0.6, 0.3, 0.8, 1.0),
			"legendary": (1.0, 0.6, 0.0, 1.0),
		}

		# Crear label flotante
		self.label = Label(
			text=text,
			color=self.colors.get(rarity, self.colors["common"]),
			font_size="16sp",
			bold=True,
			markup=True,
		)

		self.add_widget(self.label)

	def start_animation(self, start_pos=(0, 0)):
		"""
		Inicia la animación de texto flotante

		Args:
		    start_pos: Posición inicial del texto
		"""
		# Posición inicial
		self.pos = start_pos
		self.opacity = 1.0

		# Animación de movimiento hacia arriba y fade out
		end_y = start_pos[1] + 100  # Mover 100 píxeles hacia arriba

		move_anim = Animation(y=end_y, duration=2.0)
		fade_anim = Animation(opacity=0.0, duration=2.0)

		# Ejecutar ambas animaciones en paralelo
		move_anim.start(self)
		fade_anim.start(self)

		# Remover el widget después de la animación
		Clock.schedule_once(
			lambda dt: self.parent.remove_widget(self) if self.parent else None, 2.1
		)


class LootEffectsManager:
	"""
	Gestor central de efectos visuales de loot

	Coordina todos los efectos visuales relacionados con loot:
	- Popups de notificación
	- Textos flotantes
	- Efectos de sonido (preparado para futuras implementaciones)
	"""

	def __init__(self, combat_area_widget=None):
		"""
		Inicializa el gestor de efectos de loot

		Args:
		    combat_area_widget: Widget del área de combate para efectos
		"""
		self.combat_area = combat_area_widget
		self.popup_enabled = True
		self.floating_text_enabled = True
		self.sound_effects_enabled = True  # Para futuras implementaciones

		logger.info("Gestor de efectos visuales de loot inicializado")

	def show_loot_notification(self, item, enemy_type: str, is_boss: bool):
		"""
		Muestra notificación visual completa de loot obtenido

		Args:
		    item: Ítem obtenido
		    enemy_type: Tipo de enemigo
		    is_boss: Si era un boss
		"""
		try:
			rarity_value = getattr(item.rarity, "value", "common")

			# Mostrar popup si está habilitado
			if self.popup_enabled:
				popup = LootNotificationPopup(item, enemy_type, is_boss)
				popup.open_with_animation()

			# Mostrar texto flotante si está habilitado
			if self.floating_text_enabled and self.combat_area:
				item_name = getattr(item, "name", "Ítem")
				emoji = {"common": "🤍", "rare": "💚", "epic": "💙", "legendary": "🟣"}.get(
					rarity_value, "⭐"
				)

				floating_text = LootFloatingText(text=f"{emoji} {item_name}", rarity=rarity_value)

				self.combat_area.add_widget(floating_text)

				# Posición aleatoria en el área de combate
				import random

				start_x = random.randint(50, max(100, int(self.combat_area.width) - 50))
				start_y = random.randint(50, max(100, int(self.combat_area.height) - 50))

				floating_text.start_animation((start_x, start_y))

			# Efectos de sonido (placeholder para futuras implementaciones)
			if self.sound_effects_enabled:
				self._play_loot_sound(rarity_value)

			logger.info("Efectos visuales mostrados para loot %s", rarity_value)

		except Exception as e:
			logger.error("Error mostrando efectos visuales de loot: %s", e)

	def _play_loot_sound(self, rarity: str):
		"""
		Reproduce sonido de loot (placeholder para futuras implementaciones)

		Args:
		    rarity: Rareza del ítem para seleccionar sonido apropiado
		"""
		# TODO: Implementar sonidos cuando se añada sistema de audio
		sound_files = {
			"common": "loot_common.wav",
			"rare": "loot_rare.wav",
			"epic": "loot_epic.wav",
			"legendary": "loot_legendary.wav",
		}

		sound_file = sound_files.get(rarity, sound_files["common"])
		logger.debug("Debería reproducir sonido: %s", sound_file)

	def set_popup_enabled(self, enabled: bool):
		"""Habilita/deshabilita popups de loot"""
		self.popup_enabled = enabled
		status = "habilitados" if enabled else "deshabilitados"
		logger.info("Popups de loot %s", status)

	def set_floating_text_enabled(self, enabled: bool):
		"""Habilita/deshabilita textos flotantes"""
		self.floating_text_enabled = enabled
		status = "habilitados" if enabled else "deshabilitados"
		logger.info("Textos flotantes de loot %s", status)

	def set_sound_effects_enabled(self, enabled: bool):
		"""Habilita/deshabilita efectos de sonido"""
		self.sound_effects_enabled = enabled
		status = "habilitados" if enabled else "deshabilitados"
		logger.info("Efectos de sonido de loot %s", status)


def test_loot_effects():
	"""Función de testing para efectos visuales de loot"""
	print("🧪 Testing: Efectos Visuales de Loot")

	# Test de manager
	manager = LootEffectsManager()
	assert manager.popup_enabled == True
	assert manager.floating_text_enabled == True
	assert manager.sound_effects_enabled == True

	# Test de configuración
	manager.set_popup_enabled(False)
	assert manager.popup_enabled == False

	manager.set_floating_text_enabled(False)
	assert manager.floating_text_enabled == False

	print("✅ LootEffectsManager funcional")
	print("✅ Configuración de efectos funcional")
	print("✅ Sistema preparado para integración con UI")


if __name__ == "__main__":
	test_loot_effects()
