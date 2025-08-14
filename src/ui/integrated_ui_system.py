"""Sistema de UI integrado para SiKIdle.

Unifica todos los componentes visuales en una experiencia cohesiva:
- Navegación moderna
- Efectos visuales
- Feedback system
- Gestión de assets
- Temas dinámicos
"""

import logging
from typing import Dict, Optional, Callable, Any

from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.clock import Clock

from core.game import get_game_state
from core.visual_assets import VisualAssetManager
from ui.modern_navigation import ModernNavigationManager, ModernTopBar, ModernNavigationBar
from ui.visual_effects import VisualEffectsManager
from ui.feedback_system import FeedbackSystem, FeedbackType
from ui.world_selection_screen import WorldSelectionScreen
from ui.screens.enhanced_combat_screen import EnhancedCombatScreen

logger = logging.getLogger(__name__)


class IntegratedUIManager:
    """Gestor principal del sistema de UI integrado."""
    
    def __init__(self):
        """Inicializa el gestor de UI integrado."""
        # Managers principales
        self.visual_manager = VisualAssetManager()
        self.navigation_manager = None
        self.effects_manager = None
        self.feedback_system = None
        
        # Componentes UI
        self.screen_manager = ScreenManager()
        self.main_layout = None
        self.top_bar = None
        self.nav_bar = None
        
        # Estado
        self.current_theme = None
        self.is_initialized = False
        
        logger.info("IntegratedUIManager inicializado")
    
    def initialize(self, root_widget) -> BoxLayout:
        """Inicializa el sistema completo de UI."""
        if self.is_initialized:
            logger.warning("UI ya inicializada")
            return self.main_layout
        
        # Crear layout principal
        self.main_layout = BoxLayout(orientation='vertical')
        
        # Crear barra superior
        self.top_bar = ModernTopBar()
        self.main_layout.add_widget(self.top_bar)
        
        # Crear área de contenido principal
        content_area = FloatLayout()
        
        # Inicializar managers de efectos
        self.effects_manager = VisualEffectsManager(content_area)
        self.feedback_system = FeedbackSystem(content_area)
        
        # Agregar screen manager al área de contenido
        content_area.add_widget(self.screen_manager)
        self.main_layout.add_widget(content_area)
        
        # Crear barra de navegación inferior
        self.nav_bar = ModernNavigationBar(self._on_navigation_request)
        self.main_layout.add_widget(self.nav_bar)
        
        # Inicializar pantallas
        self._initialize_screens()
        
        # Configurar tema inicial
        self._update_theme_for_current_world()
        
        # Configurar actualizaciones periódicas
        Clock.schedule_interval(self._update_ui, 1.0)
        
        self.is_initialized = True
        logger.info("Sistema de UI integrado inicializado completamente")
        
        return self.main_layout
    
    def _initialize_screens(self):
        """Inicializa todas las pantallas del juego."""
        # Pantalla de combate mejorada
        combat_screen = EnhancedCombatScreen()
        self.screen_manager.add_widget(combat_screen)
        
        # Pantalla de selección de mundos
        worlds_screen = WorldSelectionScreen()
        self.screen_manager.add_widget(worlds_screen)
        
        # Pantallas adicionales (placeholder por ahora)
        self._create_placeholder_screens()
        
        # Establecer pantalla inicial
        self.screen_manager.current = 'enhanced_combat'
        self.nav_bar.set_current_screen('combat')
        
        logger.info("Pantallas inicializadas")
    
    def _create_placeholder_screens(self):
        """Crea pantallas placeholder para desarrollo futuro."""
        placeholder_screens = [
            ('inventory', 'Inventario', '🎒'),
            ('upgrades', 'Mejoras', '⬆️'),
            ('shop', 'Tienda', '🏪')
        ]
        
        for screen_id, title, icon in placeholder_screens:
            screen = Screen(name=screen_id)
            
            # Layout simple con mensaje
            layout = BoxLayout(orientation='vertical', padding=50, spacing=20)
            
            from kivy.uix.label import Label
            title_label = Label(
                text=f"{icon} {title}",
                font_size='32sp',
                bold=True,
                color=(1, 1, 1, 1),
                size_hint=(1, 0.3)
            )
            layout.add_widget(title_label)
            
            message_label = Label(
                text="Esta pantalla estará disponible pronto...",
                font_size='18sp',
                color=(0.8, 0.8, 0.8, 1),
                size_hint=(1, 0.7)
            )
            layout.add_widget(message_label)
            
            screen.add_widget(layout)
            self.screen_manager.add_widget(screen)
    
    def _on_navigation_request(self, screen_id: str):
        """Maneja solicitudes de navegación."""
        # Mapear IDs de navegación a nombres de pantalla
        screen_mapping = {
            'combat': 'enhanced_combat',
            'worlds': 'world_selection',
            'inventory': 'inventory',
            'upgrades': 'upgrades',
            'shop': 'shop'
        }
        
        target_screen = screen_mapping.get(screen_id, screen_id)
        
        if target_screen in [screen.name for screen in self.screen_manager.screens]:
            # Efecto de transición
            if self.effects_manager:
                current_screen_name = self.screen_manager.current
                # Aquí podrías agregar efectos de transición personalizados
            
            self.screen_manager.current = target_screen
            logger.info(f"Navegando a pantalla: {target_screen}")
        else:
            logger.warning(f"Pantalla no encontrada: {target_screen}")
    
    def _update_theme_for_current_world(self):
        """Actualiza el tema visual según el mundo activo."""
        game_state = get_game_state()
        if not hasattr(game_state, 'world_manager'):
            return
        
        active_world = game_state.world_manager.get_active_world()
        if not active_world:
            return
        
        world_theme = self.visual_manager.get_world_theme(active_world.world_type.value)
        if not world_theme or world_theme == self.current_theme:
            return
        
        self.current_theme = world_theme
        
        # Actualizar colores de la UI
        theme_colors = world_theme.color_scheme
        
        # Aquí podrías actualizar los colores de los componentes UI
        # Por ejemplo, cambiar colores de la barra de navegación
        
        logger.info(f"Tema actualizado para mundo: {world_theme.name}")
    
    def _update_ui(self, dt):
        """Actualización periódica de la UI."""
        game_state = get_game_state()
        if not game_state:
            return
        
        try:
            # Actualizar información del jugador en la barra superior
            if self.top_bar:
                level = game_state.player_stats.get_level()
                gold = game_state.resource_manager.get_resource(game_state.resource_manager.ResourceType.GOLD)
                gems = game_state.resource_manager.get_resource(game_state.resource_manager.ResourceType.GEMS)
                
                self.top_bar.update_resources(level, gold, gems)
            
            # Actualizar estado de desbloqueo en la navegación
            if self.nav_bar:
                player_level = game_state.player_stats.get_level()
                self.nav_bar.update_unlock_status(player_level)
            
            # Actualizar tema si cambió el mundo
            self._update_theme_for_current_world()
            
        except Exception as e:
            logger.error(f"Error actualizando UI: {e}")
    
    # Métodos de conveniencia para efectos
    def show_damage_effect(self, damage: int, pos: tuple, is_critical: bool = False):
        """Muestra efecto de daño."""
        if self.feedback_system:
            self.feedback_system.show_damage_number(damage, pos, is_critical)
    
    def show_gold_gain_effect(self, amount: int, pos: tuple):
        """Muestra efecto de ganancia de oro."""
        if self.feedback_system:
            self.feedback_system.show_gold_gain(amount, pos)
    
    def show_level_up_effect(self, new_level: int, pos: tuple):
        """Muestra efecto de subida de nivel."""
        if self.feedback_system:
            self.feedback_system.show_level_up(new_level, pos)
        
        if self.effects_manager:
            self.effects_manager.show_level_up(new_level, pos)
    
    def show_world_transition_effect(self, from_world: str, to_world: str):
        """Muestra efecto de transición entre mundos."""
        if self.effects_manager:
            self.effects_manager.show_world_transition(from_world, to_world)
    
    def show_achievement_notification(self, achievement_data: dict):
        """Muestra notificación de logro."""
        if self.feedback_system:
            # Posición en la parte superior de la pantalla
            pos = (50, 500)  # Ajustar según el tamaño de pantalla
            self.feedback_system.show_achievement(achievement_data, pos)
    
    def navigate_to_screen(self, screen_id: str):
        """Navega a una pantalla específica."""
        self._on_navigation_request(screen_id)
    
    def get_current_screen_name(self) -> str:
        """Obtiene el nombre de la pantalla actual."""
        return self.screen_manager.current
    
    def cleanup(self):
        """Limpia recursos del sistema de UI."""
        if self.effects_manager:
            self.effects_manager.clear_all_effects()
        
        if self.feedback_system:
            self.feedback_system.clear_all_effects()
        
        if self.visual_manager:
            self.visual_manager.cleanup_unused_assets()
        
        # Cancelar actualizaciones programadas
        Clock.unschedule(self._update_ui)
        
        logger.info("Sistema de UI limpiado")


# Instancia global del gestor de UI
_ui_manager_instance = None


def get_ui_manager() -> IntegratedUIManager:
    """Obtiene la instancia global del gestor de UI."""
    global _ui_manager_instance
    if _ui_manager_instance is None:
        _ui_manager_instance = IntegratedUIManager()
    return _ui_manager_instance


def initialize_ui_system(root_widget) -> BoxLayout:
    """Inicializa el sistema completo de UI."""
    ui_manager = get_ui_manager()
    return ui_manager.initialize(root_widget)


class ModernGameApp:
    """Aplicación principal con UI moderna integrada."""
    
    def __init__(self):
        """Inicializa la aplicación."""
        self.ui_manager = get_ui_manager()
        self.game_state = None
        
    def build(self):
        """Construye la aplicación."""
        # Inicializar estado del juego
        from core.game import GameState
        self.game_state = GameState()
        
        # Inicializar sistema de UI
        main_layout = self.ui_manager.initialize(None)
        
        logger.info("Aplicación moderna inicializada")
        return main_layout
    
    def on_stop(self):
        """Se ejecuta al cerrar la aplicación."""
        if self.ui_manager:
            self.ui_manager.cleanup()
        
        logger.info("Aplicación cerrada")
