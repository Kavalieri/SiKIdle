"""Sistema de navegación visual moderno para SiKIdle.

Proporciona una experiencia de navegación cohesiva y visualmente atractiva
inspirada en los mejores idle clickers del mercado.
"""

import logging
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.widget import Widget
from kivy.graphics import Color, RoundedRectangle, Ellipse, Line
from kivy.animation import Animation
from kivy.clock import Clock

from core.visual_assets import VisualAssetManager
from ui.visual_effects import VisualEffectsManager

logger = logging.getLogger(__name__)


@dataclass
class NavigationItem:
    """Elemento de navegación con información visual."""
    id: str
    title: str
    icon: str
    description: str
    color: str
    unlock_level: int = 1
    badge_count: int = 0
    is_premium: bool = False


class ModernNavButton(FloatLayout):
    """Botón de navegación moderno con efectos visuales."""
    
    def __init__(self, nav_item: NavigationItem, callback: Callable = None, **kwargs):
        super().__init__(**kwargs)
        self.nav_item = nav_item
        self.callback = callback
        self.size_hint = (None, None)
        self.size = (120, 100)
        
        self.is_unlocked = True  # Se actualizará según el nivel del jugador
        self.is_selected = False
        
        self._build_button()
        self._setup_animations()
    
    def _build_button(self):
        """Construye el botón visual."""
        # Fondo del botón
        with self.canvas.before:
            self.bg_color = Color(0.2, 0.2, 0.2, 0.8)
            self.bg_rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[15, 15, 15, 15]
            )
            
            # Borde de selección
            self.border_color = Color(0, 0, 0, 0)  # Invisible por defecto
            self.border_rect = RoundedRectangle(
                pos=(self.pos[0] - 2, self.pos[1] - 2),
                size=(self.size[0] + 4, self.size[1] + 4),
                radius=[17, 17, 17, 17]
            )
        
        self.bind(pos=self._update_graphics, size=self._update_graphics)
        
        # Icono principal
        self.icon_label = Label(
            text=self.nav_item.icon,
            font_size='32sp',
            size_hint=(1, 0.6),
            pos_hint={'center_x': 0.5, 'top': 0.85},
            halign='center',
            valign='middle'
        )
        self.add_widget(self.icon_label)
        
        # Título
        self.title_label = Label(
            text=self.nav_item.title,
            font_size='12sp',
            bold=True,
            color=(1, 1, 1, 1),
            size_hint=(1, 0.3),
            pos_hint={'center_x': 0.5, 'y': 0.05},
            halign='center',
            valign='middle',
            text_size=(110, None)
        )
        self.add_widget(self.title_label)
        
        # Badge de notificación
        if self.nav_item.badge_count > 0:
            self.badge = Label(
                text=str(self.nav_item.badge_count),
                font_size='10sp',
                bold=True,
                color=(1, 1, 1, 1),
                size_hint=(None, None),
                size=(20, 20),
                pos_hint={'right': 0.95, 'top': 0.95},
                halign='center',
                valign='middle'
            )
            
            with self.badge.canvas.before:
                Color(1, 0, 0, 1)  # Rojo para el badge
                Ellipse(pos=self.badge.pos, size=self.badge.size)
            
            self.add_widget(self.badge)
        
        # Indicador premium
        if self.nav_item.is_premium:
            self.premium_icon = Label(
                text="💎",
                font_size='16sp',
                size_hint=(None, None),
                size=(20, 20),
                pos_hint={'x': 0.05, 'top': 0.95}
            )
            self.add_widget(self.premium_icon)
        
        # Configurar interacción
        self.bind(on_touch_down=self._on_touch_down)
    
    def _update_graphics(self, *args):
        """Actualiza los gráficos del botón."""
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size
        self.border_rect.pos = (self.pos[0] - 2, self.pos[1] - 2)
        self.border_rect.size = (self.size[0] + 4, self.size[1] + 4)
    
    def _setup_animations(self):
        """Configura las animaciones del botón."""
        # Animación de hover/idle sutil
        self.idle_anim = (
            Animation(opacity=0.9, duration=2.0, transition='in_out_sine') +
            Animation(opacity=1.0, duration=2.0, transition='in_out_sine')
        )
        self.idle_anim.repeat = True
        self.idle_anim.start(self.icon_label)
    
    def _on_touch_down(self, widget, touch):
        """Maneja el toque en el botón."""
        if self.collide_point(*touch.pos) and self.is_unlocked:
            self._animate_press()
            if self.callback:
                Clock.schedule_once(lambda dt: self.callback(self.nav_item.id), 0.1)
            return True
        return False
    
    def _animate_press(self):
        """Animación de presión del botón."""
        # Efecto de escala
        scale_down = Animation(size=(115, 95), duration=0.1, transition='out_quad')
        scale_up = Animation(size=(120, 100), duration=0.1, transition='out_quad')
        
        (scale_down + scale_up).start(self)
        
        # Efecto de brillo
        original_color = self.bg_color.rgba
        bright_color = [min(1.0, c + 0.2) for c in original_color[:3]] + [original_color[3]]
        
        self.bg_color.rgba = bright_color
        Clock.schedule_once(lambda dt: setattr(self.bg_color, 'rgba', original_color), 0.2)
    
    def set_selected(self, selected: bool):
        """Establece el estado de selección del botón."""
        self.is_selected = selected
        
        if selected:
            # Mostrar borde de selección
            color_values = self._hex_to_rgba(self.nav_item.color)
            self.border_color.rgba = color_values + [1.0]
            
            # Cambiar color de fondo
            self.bg_color.rgba = color_values + [0.3]
        else:
            # Ocultar borde de selección
            self.border_color.rgba = [0, 0, 0, 0]
            self.bg_color.rgba = [0.2, 0.2, 0.2, 0.8]
    
    def set_unlocked(self, unlocked: bool):
        """Establece el estado de desbloqueo del botón."""
        self.is_unlocked = unlocked
        
        if unlocked:
            self.opacity = 1.0
            self.icon_label.color = (1, 1, 1, 1)
            self.title_label.color = (1, 1, 1, 1)
        else:
            self.opacity = 0.5
            self.icon_label.color = (0.5, 0.5, 0.5, 1)
            self.title_label.color = (0.5, 0.5, 0.5, 1)
    
    def _hex_to_rgba(self, hex_color: str) -> List[float]:
        """Convierte color hex a RGBA."""
        hex_color = hex_color.lstrip('#')
        return [int(hex_color[i:i+2], 16) / 255.0 for i in (0, 2, 4)]


class ModernNavigationBar(BoxLayout):
    """Barra de navegación moderna."""
    
    def __init__(self, navigation_callback: Callable = None, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint = (1, None)
        self.height = 120
        self.spacing = 10
        self.padding = [10, 10, 10, 10]
        
        self.navigation_callback = navigation_callback
        self.nav_buttons: Dict[str, ModernNavButton] = {}
        self.current_screen = None
        
        # Fondo de la barra de navegación
        with self.canvas.before:
            Color(0.1, 0.1, 0.1, 0.9)
            self.bg_rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[20, 20, 0, 0]
            )
        
        self.bind(pos=self._update_bg, size=self._update_bg)
        
        self._setup_navigation_items()
        
        logger.info("ModernNavigationBar inicializada")
    
    def _update_bg(self, *args):
        """Actualiza el fondo de la barra."""
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size
    
    def _setup_navigation_items(self):
        """Configura los elementos de navegación."""
        nav_items = [
            NavigationItem(
                id='combat',
                title='Combate',
                icon='⚔️',
                description='Lucha contra enemigos',
                color='#F44336',
                unlock_level=1
            ),
            NavigationItem(
                id='worlds',
                title='Mundos',
                icon='🌍',
                description='Explora nuevos mundos',
                color='#4CAF50',
                unlock_level=1
            ),
            NavigationItem(
                id='inventory',
                title='Inventario',
                icon='🎒',
                description='Gestiona tus objetos',
                color='#FF9800',
                unlock_level=3
            ),
            NavigationItem(
                id='upgrades',
                title='Mejoras',
                icon='⬆️',
                description='Mejora tus habilidades',
                color='#9C27B0',
                unlock_level=5
            ),
            NavigationItem(
                id='shop',
                title='Tienda',
                icon='🏪',
                description='Compra objetos especiales',
                color='#2196F3',
                unlock_level=10,
                is_premium=True
            )
        ]
        
        for item in nav_items:
            button = ModernNavButton(
                item,
                callback=self._on_nav_button_pressed
            )
            self.nav_buttons[item.id] = button
            self.add_widget(button)
    
    def _on_nav_button_pressed(self, screen_id: str):
        """Maneja la presión de un botón de navegación."""
        if self.navigation_callback:
            self.navigation_callback(screen_id)
        
        self.set_current_screen(screen_id)
        logger.info(f"Navegando a: {screen_id}")
    
    def set_current_screen(self, screen_id: str):
        """Establece la pantalla actual."""
        # Deseleccionar botón anterior
        if self.current_screen and self.current_screen in self.nav_buttons:
            self.nav_buttons[self.current_screen].set_selected(False)
        
        # Seleccionar nuevo botón
        if screen_id in self.nav_buttons:
            self.nav_buttons[screen_id].set_selected(True)
            self.current_screen = screen_id
    
    def update_unlock_status(self, player_level: int):
        """Actualiza el estado de desbloqueo según el nivel del jugador."""
        for button in self.nav_buttons.values():
            unlocked = player_level >= button.nav_item.unlock_level
            button.set_unlocked(unlocked)
    
    def set_badge_count(self, screen_id: str, count: int):
        """Establece el contador de badge para una pantalla."""
        if screen_id in self.nav_buttons:
            self.nav_buttons[screen_id].nav_item.badge_count = count
            # Actualizar visualmente el badge
            # (Implementación completa requeriría reconstruir el botón)


class ModernTopBar(BoxLayout):
    """Barra superior moderna con información del jugador."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint = (1, None)
        self.height = 60
        self.spacing = 15
        self.padding = [20, 10, 20, 10]
        
        # Fondo de la barra superior
        with self.canvas.before:
            Color(0.1, 0.1, 0.1, 0.9)
            self.bg_rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[0, 0, 20, 20]
            )
        
        self.bind(pos=self._update_bg, size=self._update_bg)
        
        self._build_top_bar()
        
        logger.info("ModernTopBar inicializada")
    
    def _update_bg(self, *args):
        """Actualiza el fondo de la barra."""
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size
    
    def _build_top_bar(self):
        """Construye la barra superior."""
        # Logo/Título del juego
        title_layout = BoxLayout(orientation='horizontal', size_hint=(0.3, 1), spacing=10)
        
        logo_label = Label(
            text="⚡",
            font_size='24sp',
            color=(1, 1, 0, 1),
            size_hint=(None, 1),
            width=40
        )
        title_layout.add_widget(logo_label)
        
        game_title = Label(
            text="SiKIdle",
            font_size='18sp',
            bold=True,
            color=(1, 1, 1, 1),
            size_hint=(1, 1),
            halign='left',
            valign='middle'
        )
        game_title.text_size = (None, None)
        title_layout.add_widget(game_title)
        
        self.add_widget(title_layout)
        
        # Recursos del jugador
        resources_layout = BoxLayout(orientation='horizontal', size_hint=(0.5, 1), spacing=20)
        
        # Nivel
        level_layout = BoxLayout(orientation='horizontal', size_hint=(None, 1), width=80, spacing=5)
        level_layout.add_widget(Label(
            text="🏆",
            font_size='16sp',
            size_hint=(None, 1),
            width=25
        ))
        self.level_label = Label(
            text="Nv.1",
            font_size='14sp',
            bold=True,
            color=(1, 1, 1, 1),
            size_hint=(1, 1)
        )
        level_layout.add_widget(self.level_label)
        resources_layout.add_widget(level_layout)
        
        # Oro
        gold_layout = BoxLayout(orientation='horizontal', size_hint=(None, 1), width=100, spacing=5)
        gold_layout.add_widget(Label(
            text="💰",
            font_size='16sp',
            size_hint=(None, 1),
            width=25
        ))
        self.gold_label = Label(
            text="0",
            font_size='14sp',
            bold=True,
            color=(1, 0.8, 0, 1),
            size_hint=(1, 1)
        )
        gold_layout.add_widget(self.gold_label)
        resources_layout.add_widget(gold_layout)
        
        # Gemas
        gems_layout = BoxLayout(orientation='horizontal', size_hint=(None, 1), width=80, spacing=5)
        gems_layout.add_widget(Label(
            text="💎",
            font_size='16sp',
            size_hint=(None, 1),
            width=25
        ))
        self.gems_label = Label(
            text="0",
            font_size='14sp',
            bold=True,
            color=(0.5, 0.8, 1, 1),
            size_hint=(1, 1)
        )
        gems_layout.add_widget(self.gems_label)
        resources_layout.add_widget(gems_layout)
        
        self.add_widget(resources_layout)
        
        # Botones de acción rápida
        actions_layout = BoxLayout(orientation='horizontal', size_hint=(0.2, 1), spacing=10)
        
        # Botón de configuración
        settings_btn = Button(
            text="⚙️",
            size_hint=(None, 1),
            width=40,
            font_size='18sp',
            background_color=(0.3, 0.3, 0.3, 0.8)
        )
        actions_layout.add_widget(settings_btn)
        
        # Botón de menú
        menu_btn = Button(
            text="☰",
            size_hint=(None, 1),
            width=40,
            font_size='18sp',
            background_color=(0.3, 0.3, 0.3, 0.8)
        )
        actions_layout.add_widget(menu_btn)
        
        self.add_widget(actions_layout)
    
    def update_resources(self, level: int, gold: int, gems: int):
        """Actualiza los recursos mostrados."""
        self.level_label.text = f"Nv.{level}"
        self.gold_label.text = self._format_number(gold)
        self.gems_label.text = str(gems)
    
    def _format_number(self, number: int) -> str:
        """Formatea números grandes."""
        if number >= 1_000_000:
            return f"{number/1_000_000:.1f}M"
        elif number >= 1_000:
            return f"{number/1_000:.1f}K"
        else:
            return str(number)


class ModernNavigationManager:
    """Gestor de navegación moderno."""
    
    def __init__(self, screen_manager, **kwargs):
        """Inicializa el gestor de navegación."""
        self.screen_manager = screen_manager
        self.top_bar = None
        self.nav_bar = None
        
        logger.info("ModernNavigationManager inicializado")
    
    def setup_navigation(self, parent_layout, navigation_callback):
        """Configura el sistema de navegación en un layout."""
        # Crear barra superior
        self.top_bar = ModernTopBar()
        parent_layout.add_widget(self.top_bar)
        
        # El área de contenido va en el medio (manejado externamente)
        
        # Crear barra de navegación inferior
        self.nav_bar = ModernNavigationBar(navigation_callback)
        parent_layout.add_widget(self.nav_bar)
        
        logger.info("Sistema de navegación configurado")
    
    def navigate_to(self, screen_id: str):
        """Navega a una pantalla específica."""
        if self.nav_bar:
            self.nav_bar.set_current_screen(screen_id)
        
        if hasattr(self.screen_manager, 'current'):
            self.screen_manager.current = screen_id
    
    def update_player_info(self, level: int, gold: int, gems: int):
        """Actualiza la información del jugador."""
        if self.top_bar:
            self.top_bar.update_resources(level, gold, gems)
        
        if self.nav_bar:
            self.nav_bar.update_unlock_status(level)
