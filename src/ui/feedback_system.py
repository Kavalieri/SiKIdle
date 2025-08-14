"""Sistema de feedback visual y efectos para SiKIdle.

Proporciona feedback visual inmediato para todas las acciones del jugador,
incluyendo progreso, logros, recompensas y eventos especiales.
"""

import logging
import random
from typing import Dict, List, Optional, Tuple, Callable
from dataclasses import dataclass
from enum import Enum

from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import Color, Rectangle, Ellipse, Line, PushMatrix, PopMatrix, Rotate
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.vector import Vector

from core.visual_assets import VisualAssetManager, EffectType
from ui.visual_effects import VisualEffectsManager

logger = logging.getLogger(__name__)


class FeedbackType(Enum):
    """Tipos de feedback visual disponibles."""
    DAMAGE = "damage"
    CRITICAL_DAMAGE = "critical_damage"
    HEAL = "heal"
    GOLD_GAIN = "gold_gain"
    EXP_GAIN = "exp_gain"
    LEVEL_UP = "level_up"
    ITEM_FOUND = "item_found"
    ACHIEVEMENT = "achievement"
    WORLD_COMPLETE = "world_complete"
    BOSS_DEFEATED = "boss_defeated"
    SKILL_UNLOCK = "skill_unlock"
    UPGRADE_PURCHASED = "upgrade_purchased"


@dataclass
class FeedbackConfig:
    """Configuración para un tipo de feedback."""
    color: Tuple[float, float, float, float]
    font_size: str
    duration: float
    movement_distance: float
    scale_effect: bool = False
    particle_count: int = 0
    sound_effect: Optional[str] = None


class FloatingTextEffect(Widget):
    """Efecto de texto flotante con animaciones."""
    
    def __init__(self, text: str, config: FeedbackConfig, **kwargs):
        super().__init__(**kwargs)
        self.text = text
        self.config = config
        self.size_hint = (None, None)
        self.size = (200, 50)
        
        # Crear label del texto
        self.text_label = Label(
            text=text,
            font_size=config.font_size,
            bold=True,
            color=config.color,
            size_hint=(None, None),
            size=self.size,
            halign='center',
            valign='middle'
        )
        self.text_label.text_size = self.size
        self.add_widget(self.text_label)
        
        # Efectos de partículas si están configurados
        self.particles = []
        if config.particle_count > 0:
            self._create_particles()
    
    def _create_particles(self):
        """Crea partículas para el efecto."""
        for i in range(self.config.particle_count):
            particle = Widget(size=(4, 4))
            with particle.canvas:
                Color(*self.config.color[:3], 0.8)
                Ellipse(pos=particle.pos, size=particle.size)
            
            self.particles.append(particle)
            self.add_widget(particle)
    
    def play(self, start_pos: Tuple[float, float], callback: Callable = None):
        """Reproduce el efecto de texto flotante."""
        self.pos = start_pos
        
        # Posición final
        end_pos = (
            start_pos[0] + random.randint(-30, 30),
            start_pos[1] + self.config.movement_distance
        )
        
        # Animación principal del texto
        move_anim = Animation(
            pos=end_pos,
            duration=self.config.duration,
            transition='out_quart'
        )
        
        fade_anim = Animation(
            opacity=0,
            duration=self.config.duration * 0.8,
            transition='out_quad'
        )
        
        # Efecto de escala si está habilitado
        if self.config.scale_effect:
            scale_anim = (
                Animation(size=(220, 60), duration=0.2, transition='out_back') +
                Animation(size=(200, 50), duration=0.3, transition='in_back')
            )
            scale_anim.start(self.text_label)
        
        # Animación de partículas
        for i, particle in enumerate(self.particles):
            particle.pos = start_pos
            
            # Dirección aleatoria para cada partícula
            angle = random.uniform(0, 360)
            distance = random.uniform(50, 100)
            particle_end_pos = (
                start_pos[0] + distance * Vector(1, 0).rotate(angle).x,
                start_pos[1] + distance * Vector(1, 0).rotate(angle).y
            )
            
            particle_anim = Animation(
                pos=particle_end_pos,
                opacity=0,
                duration=self.config.duration * 0.9,
                transition='out_quad'
            )
            particle_anim.start(particle)
        
        move_anim.start(self)
        fade_anim.start(self)
        
        # Programar limpieza
        Clock.schedule_once(lambda dt: self._cleanup(callback), self.config.duration)
    
    def _cleanup(self, callback: Callable):
        """Limpia el efecto."""
        if self.parent:
            self.parent.remove_widget(self)
        if callback:
            callback()


class ProgressBarEffect(Widget):
    """Efecto de barra de progreso animada."""
    
    def __init__(self, current_value: float, max_value: float, **kwargs):
        super().__init__(**kwargs)
        self.current_value = current_value
        self.max_value = max_value
        self.size_hint = (None, None)
        self.size = (200, 20)
        
        # Crear elementos visuales
        with self.canvas:
            # Fondo de la barra
            Color(0.3, 0.3, 0.3, 0.8)
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
            
            # Barra de progreso
            Color(0.2, 0.8, 0.2, 1)
            progress_width = (current_value / max_value) * self.size[0]
            self.progress_rect = Rectangle(
                pos=self.pos,
                size=(progress_width, self.size[1])
            )
        
        self.bind(pos=self._update_graphics, size=self._update_graphics)
    
    def _update_graphics(self, *args):
        """Actualiza los gráficos de la barra."""
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size
        
        progress_width = (self.current_value / self.max_value) * self.size[0]
        self.progress_rect.pos = self.pos
        self.progress_rect.size = (progress_width, self.size[1])
    
    def animate_to_value(self, new_value: float, duration: float = 1.0):
        """Anima la barra hacia un nuevo valor."""
        if new_value > self.max_value:
            new_value = self.max_value
        
        # Animación del valor
        anim = Animation(current_value=new_value, duration=duration, transition='out_quart')
        anim.bind(on_progress=self._on_progress_update)
        anim.start(self)
    
    def _on_progress_update(self, animation, widget, progress):
        """Actualiza la barra durante la animación."""
        self._update_graphics()


class AchievementNotification(FloatLayout):
    """Notificación de logro desbloqueado."""
    
    def __init__(self, achievement_data: Dict, **kwargs):
        super().__init__(**kwargs)
        self.achievement_data = achievement_data
        self.size_hint = (None, None)
        self.size = (350, 80)
        
        # Fondo de la notificación
        with self.canvas.before:
            Color(0.1, 0.1, 0.1, 0.95)
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
            
            # Borde dorado
            Color(1, 0.8, 0, 1)
            self.border_line = Line(
                rectangle=(self.pos[0], self.pos[1], self.size[0], self.size[1]),
                width=2
            )
        
        self.bind(pos=self._update_graphics, size=self._update_graphics)
        
        self._build_notification()
    
    def _update_graphics(self, *args):
        """Actualiza los gráficos de la notificación."""
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size
        self.border_line.rectangle = (self.pos[0], self.pos[1], self.size[0], self.size[1])
    
    def _build_notification(self):
        """Construye el contenido de la notificación."""
        # Icono del logro
        icon_label = Label(
            text="🏆",
            font_size='32sp',
            size_hint=(None, 1),
            width=60,
            pos_hint={'x': 0, 'center_y': 0.5}
        )
        self.add_widget(icon_label)
        
        # Información del logro
        info_layout = BoxLayout(
            orientation='vertical',
            size_hint=(1, 1),
            pos_hint={'x': 0.17, 'center_y': 0.5},
            spacing=2
        )
        
        # Título "¡Logro Desbloqueado!"
        title_label = Label(
            text="¡LOGRO DESBLOQUEADO!",
            font_size='14sp',
            bold=True,
            color=(1, 0.8, 0, 1),
            size_hint=(1, 0.4),
            halign='left',
            valign='bottom'
        )
        title_label.text_size = (250, None)
        info_layout.add_widget(title_label)
        
        # Nombre del logro
        name_label = Label(
            text=self.achievement_data.get('name', 'Logro Misterioso'),
            font_size='16sp',
            bold=True,
            color=(1, 1, 1, 1),
            size_hint=(1, 0.6),
            halign='left',
            valign='top'
        )
        name_label.text_size = (250, None)
        info_layout.add_widget(name_label)
        
        self.add_widget(info_layout)
    
    def show(self, callback: Callable = None):
        """Muestra la notificación con animación."""
        # Empezar fuera de la pantalla
        original_pos = self.pos
        self.pos = (self.pos[0], -self.size[1])
        
        # Animación de entrada
        enter_anim = Animation(
            pos=original_pos,
            duration=0.5,
            transition='out_back'
        )
        
        # Mantener visible
        hold_anim = Animation(
            pos=original_pos,
            duration=3.0
        )
        
        # Animación de salida
        exit_anim = Animation(
            pos=(self.pos[0], -self.size[1]),
            duration=0.3,
            transition='in_back'
        )
        
        full_anim = enter_anim + hold_anim + exit_anim
        full_anim.bind(on_complete=lambda *args: self._cleanup(callback))
        full_anim.start(self)
    
    def _cleanup(self, callback: Callable):
        """Limpia la notificación."""
        if self.parent:
            self.parent.remove_widget(self)
        if callback:
            callback()


class FeedbackSystem:
    """Sistema central de feedback visual."""
    
    def __init__(self, parent_widget: Widget):
        """Inicializa el sistema de feedback."""
        self.parent_widget = parent_widget
        self.active_effects: List[Widget] = []
        
        # Configuraciones de feedback
        self.feedback_configs = {
            FeedbackType.DAMAGE: FeedbackConfig(
                color=(1, 1, 1, 1),
                font_size='18sp',
                duration=1.2,
                movement_distance=80
            ),
            FeedbackType.CRITICAL_DAMAGE: FeedbackConfig(
                color=(1, 1, 0, 1),
                font_size='24sp',
                duration=1.5,
                movement_distance=100,
                scale_effect=True,
                particle_count=8
            ),
            FeedbackType.GOLD_GAIN: FeedbackConfig(
                color=(1, 0.8, 0, 1),
                font_size='16sp',
                duration=1.0,
                movement_distance=60,
                particle_count=5
            ),
            FeedbackType.EXP_GAIN: FeedbackConfig(
                color=(0.5, 0.8, 1, 1),
                font_size='14sp',
                duration=1.0,
                movement_distance=50
            ),
            FeedbackType.LEVEL_UP: FeedbackConfig(
                color=(1, 1, 0, 1),
                font_size='28sp',
                duration=2.0,
                movement_distance=120,
                scale_effect=True,
                particle_count=15
            ),
            FeedbackType.ACHIEVEMENT: FeedbackConfig(
                color=(1, 0.8, 0, 1),
                font_size='20sp',
                duration=2.5,
                movement_distance=100,
                scale_effect=True,
                particle_count=12
            )
        }
        
        logger.info("FeedbackSystem inicializado")
    
    def show_floating_text(self, text: str, pos: Tuple[float, float], 
                          feedback_type: FeedbackType = FeedbackType.DAMAGE):
        """Muestra texto flotante con el tipo de feedback especificado."""
        config = self.feedback_configs.get(feedback_type, self.feedback_configs[FeedbackType.DAMAGE])
        
        effect = FloatingTextEffect(text, config)
        self.parent_widget.add_widget(effect)
        self.active_effects.append(effect)
        
        effect.play(pos, lambda: self._remove_effect(effect))
    
    def show_damage_number(self, damage: int, pos: Tuple[float, float], is_critical: bool = False):
        """Muestra número de daño."""
        feedback_type = FeedbackType.CRITICAL_DAMAGE if is_critical else FeedbackType.DAMAGE
        text = f"CRÍTICO! {damage}" if is_critical else str(damage)
        self.show_floating_text(text, pos, feedback_type)
    
    def show_gold_gain(self, amount: int, pos: Tuple[float, float]):
        """Muestra ganancia de oro."""
        self.show_floating_text(f"+{amount} 💰", pos, FeedbackType.GOLD_GAIN)
    
    def show_exp_gain(self, amount: int, pos: Tuple[float, float]):
        """Muestra ganancia de experiencia."""
        self.show_floating_text(f"+{amount} EXP", pos, FeedbackType.EXP_GAIN)
    
    def show_level_up(self, new_level: int, pos: Tuple[float, float]):
        """Muestra subida de nivel."""
        self.show_floating_text(f"¡NIVEL {new_level}!", pos, FeedbackType.LEVEL_UP)
    
    def show_achievement(self, achievement_data: Dict, pos: Tuple[float, float]):
        """Muestra notificación de logro."""
        notification = AchievementNotification(achievement_data)
        notification.pos = pos
        
        self.parent_widget.add_widget(notification)
        self.active_effects.append(notification)
        
        notification.show(lambda: self._remove_effect(notification))
    
    def show_progress_bar(self, current: float, maximum: float, pos: Tuple[float, float]):
        """Muestra barra de progreso animada."""
        progress_bar = ProgressBarEffect(current, maximum)
        progress_bar.pos = pos
        
        self.parent_widget.add_widget(progress_bar)
        self.active_effects.append(progress_bar)
        
        # Auto-remover después de 3 segundos
        Clock.schedule_once(lambda dt: self._remove_effect(progress_bar), 3.0)
        
        return progress_bar
    
    def _remove_effect(self, effect: Widget):
        """Remueve un efecto de la lista activa."""
        if effect in self.active_effects:
            self.active_effects.remove(effect)
    
    def clear_all_effects(self):
        """Limpia todos los efectos activos."""
        for effect in self.active_effects[:]:
            if effect.parent:
                effect.parent.remove_widget(effect)
        
        self.active_effects.clear()
        logger.info("Todos los efectos de feedback limpiados")
