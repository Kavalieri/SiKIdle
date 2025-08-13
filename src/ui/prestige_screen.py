"""
Pantalla de Ascensión Dimensional para SiKIdle.

Esta pantalla permite a los exploradores:
- Ver información sobre el sistema de ascensión dimensional
- Elegir entre los 3 tipos de ascensión (Menor/Mayor/Dimensional)
- Calcular fragmentos de esencia y bonificaciones antes de ascender
- Realizar ascensión épica con animaciones especiales
"""

import logging
from typing import Any, Optional
from kivy.uix.boxlayout import BoxLayout  # type: ignore
from kivy.uix.gridlayout import GridLayout  # type: ignore
from kivy.uix.label import Label  # type: ignore
from kivy.uix.button import Button  # type: ignore
from kivy.uix.popup import Popup  # type: ignore
from kivy.uix.scrollview import ScrollView  # type: ignore

from core.game import get_game_state, GameState
from core.dimensional_prestige import DimensionalPrestigeManager, AscensionType, DimensionalReward
from ui.screen_manager import SiKIdleScreen


class AscensionCard(BoxLayout):
    """Widget para mostrar una opción de ascensión dimensional."""
    
    def __init__(self, ascension_type: AscensionType, prestige_manager: DimensionalPrestigeManager, 
                 player_level: int, boss_defeated: bool = False, secret_completed: bool = False, **kwargs):
        super().__init__(orientation='vertical', spacing=10, **kwargs)
        
        self.ascension_type = ascension_type
        self.prestige_manager = prestige_manager
        self.player_level = player_level
        self.boss_defeated = boss_defeated
        self.secret_completed = secret_completed
        
        # Configuración por tipo
        self.config = {
            AscensionType.MINOR: {
                'title': '⬆️ Ascensión Menor',
                'color': [0.6, 0.8, 1.0, 1],
                'level_req': 50,
                'description': 'Tu primera ascensión dimensional\n+25% stats permanentes'
            },
            AscensionType.MAJOR: {
                'title': '🌟 Ascensión Mayor', 
                'color': [0.8, 0.6, 1.0, 1],
                'level_req': 100,
                'description': 'Ascensión de élite\n+50% stats + Mazmorra Secreta'
            },
            AscensionType.DIMENSION: {
                'title': '🌌 Ascensión Dimensional',
                'color': [1.0, 0.8, 0.2, 1],
                'level_req': 200,
                'description': 'Ascensión épica\n+100% stats + Nueva Dimensión'
            }
        }
        
        self._create_card()
    
    def _create_card(self):
        """Crea el contenido de la card de ascensión."""
        config = self.config[self.ascension_type]
        
        # Verificar si se puede realizar
        can_ascend, error_msg = self.prestige_manager.can_ascend(
            self.ascension_type, self.player_level, self.boss_defeated, self.secret_completed
        )
        
        # Header con título
        header = Label(
            text=config['title'],
            size_hint_y=None,
            height=40,
            font_size='18sp',
            color=config['color'],
            bold=True,
            halign='center'
        )
        header.text_size = (header.width, header.height)
        
        # Descripción
        desc = Label(
            text=config['description'],
            size_hint_y=None,
            height=60,
            font_size='14sp',
            color=[0.9, 0.9, 0.9, 1],
            halign='center'
        )
        desc.text_size = (desc.width, desc.height)
        
        # Requisitos
        req_text = f"Nivel {config['level_req']}+ | Boss Derrotado"
        if self.ascension_type == AscensionType.MAJOR:
            req_text += " | Mazmorra Secreta"
        
        requirements = Label(
            text=req_text,
            size_hint_y=None,
            height=30,
            font_size='12sp',
            color=[0.7, 0.7, 0.7, 1],
            halign='center'
        )
        requirements.text_size = (requirements.width, requirements.height)
        
        # Recompensas preview
        if can_ascend:
            preview = self.prestige_manager.get_ascension_preview(self.ascension_type, self.player_level)
            
            rewards_text = f"💎 +{preview['essence_fragments_gain']} Fragmentos de Esencia\n"
            rewards_text += f"⚡ +{preview['stat_bonus_percentage']:.0f}% Stats Permanentes"
            
            if preview['special_unlock']:
                rewards_text += f"\n🔓 {preview['special_unlock']}"
            
            rewards_color = [0, 1, 0, 1]  # Verde
        else:
            rewards_text = f"❌ {error_msg}"
            rewards_color = [1, 0.5, 0.5, 1]  # Rojo claro
        
        rewards = Label(
            text=rewards_text,
            size_hint_y=None,
            height=80,
            font_size='13sp',
            color=rewards_color,
            halign='center'
        )
        rewards.text_size = (rewards.width, rewards.height)
        
        # Botón de ascensión
        if can_ascend:
            button_text = f"🚀 Ascender"
            button_color = config['color']
            button_disabled = False
        else:
            button_text = "� No Disponible"
            button_color = [0.5, 0.5, 0.5, 1]
            button_disabled = True
        
        self.ascend_button = Button(
            text=button_text,
            size_hint_y=None,
            height=50,
            font_size='16sp',
            background_color=button_color,
            disabled=button_disabled
        )
        
        if can_ascend:
            self.ascend_button.bind(on_press=self.on_ascend_button)
        
        # Agregar widgets
        self.add_widget(header)
        self.add_widget(desc)
        self.add_widget(requirements)
        self.add_widget(rewards)
        self.add_widget(self.ascend_button)
    
    def on_ascend_button(self, instance):
        """Maneja el clic en el botón de ascensión."""
        # Delegar al screen parent para manejar la confirmación
        parent_screen = self.parent
        while parent_screen and not isinstance(parent_screen, DimensionalPrestigeScreen):
            parent_screen = parent_screen.parent
        
        if parent_screen:
            parent_screen.show_ascension_confirmation(self.ascension_type)


class DimensionalPrestigeScreen(SiKIdleScreen):
    """Pantalla de ascensión dimensional del juego."""
    
    def __init__(self, manager_ref, **kwargs: Any):
        super().__init__('dimensional_prestige', manager_ref, **kwargs)
        self.game_state: GameState = get_game_state()
        
        # Crear manager dimensional (mock por ahora)
        self.prestige_manager = self._create_mock_prestige_manager()
        
        # Crear la interfaz principal
        self._create_ui()
        
        logging.info("Pantalla de ascensión dimensional creada exitosamente")
    
    def _create_mock_prestige_manager(self) -> DimensionalPrestigeManager:
        """Crea un mock del prestige manager para la demo."""
        class MockDB:
            def execute(self, q, p=None):
                class MC:
                    def fetchone(self): return None
                    def fetchall(self): return []
                return MC()
        
        class MockRM:
            def __init__(self): pass
        
        return DimensionalPrestigeManager(MockRM(), MockDB())
    
    def _create_ui(self):
        """Crea la interfaz principal de ascensión dimensional."""
        main_layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # Header épico
        header = self._create_epic_header()
        main_layout.add_widget(header)
        
        # Estado actual del explorador dimensional
        current_status = self._create_current_status()
        main_layout.add_widget(current_status)
        
        # Scroll view con las opciones de ascensión
        ascension_options = self._create_ascension_options()
        main_layout.add_widget(ascension_options)
        
        # Botones de navegación
        navigation = self._create_navigation_buttons()
        main_layout.add_widget(navigation)
        
        self.add_widget(main_layout)
    
    def _create_epic_header(self) -> BoxLayout:
        """Crea el header épico de la pantalla."""
        header = BoxLayout(orientation='vertical', size_hint_y=None, height=120, spacing=5)
        
        # Título épico
        title_label = Label(
            text="🌌 ASCENSIÓN DIMENSIONAL 🌌",
            size_hint_y=None,
            height=50,
            font_size='32sp',
            color=[1, 0.8, 0.2, 1],
            bold=True,
            halign='center'
        )
        title_label.text_size = (title_label.width, title_label.height)
        
        # Subtítulo épico
        subtitle_label = Label(
            text="Trasciende las limitaciones de tu dimensión actual",
            size_hint_y=None,
            height=35,
            font_size='16sp',
            color=[0.8, 0.9, 1.0, 1],
            italic=True,
            halign='center'
        )
        subtitle_label.text_size = (subtitle_label.width, subtitle_label.height)
        
        # Descripción del sistema
        desc_label = Label(
            text="Reinicia tu aventura para acceder a poderes dimensionales superiores",
            size_hint_y=None,
            height=35,
            font_size='14sp',
            color=[0.7, 0.8, 0.9, 1],
            halign='center'
        )
        desc_label.text_size = (desc_label.width, desc_label.height)
        
        header.add_widget(title_label)
        header.add_widget(subtitle_label)
        header.add_widget(desc_label)
        
        return header
    
    def _create_current_status(self) -> BoxLayout:
        """Crea la sección de estado actual del explorador."""
        status_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=140, spacing=10)
        
        # Título de sección
        section_title = Label(
            text="📊 Estado del Explorador Dimensional",
            size_hint_y=None,
            height=35,
            font_size='18sp',
            color=[0.2, 1, 1, 1],
            bold=True,
            halign='center'
        )
        section_title.text_size = (section_title.width, section_title.height)
        
        # Grid de información 2x3
        info_grid = GridLayout(cols=3, rows=2, size_hint_y=None, height=95, spacing=10)
        
        # Información dimensional
        stats = self.prestige_manager.get_dimensional_stats()
        player_level = getattr(self.game_state, 'player_level', 75)  # Mock level
        
        info_items = [
            (f"💎 {stats['essence_fragments']}", "Fragmentos de Esencia"),
            (f"🌌 {stats['current_dimension']}", "Dimensión Actual"),
            (f"⬆️ {stats['total_ascensions']}", "Ascensiones Totales"),
            (f"👤 {player_level}", "Nivel Explorador"),
            (f"⚡ {stats['dimensional_stat_bonus']:.1f}x", "Bonus Dimensional"),
            (f"🔓 {len(stats['unlocked_dimensions'])}", "Dimensiones Abiertas")
        ]
        
        for value, label_text in info_items:
            item_layout = BoxLayout(orientation='vertical', spacing=2)
            
            value_label = Label(
                text=value,
                font_size='16sp',
                color=[1, 1, 1, 1],
                bold=True,
                halign='center'
            )
            value_label.text_size = (value_label.width, value_label.height)
            
            desc_label = Label(
                text=label_text,
                font_size='12sp',
                color=[0.7, 0.7, 0.7, 1],
                halign='center'
            )
            desc_label.text_size = (desc_label.width, desc_label.height)
            
            item_layout.add_widget(value_label)
            item_layout.add_widget(desc_label)
            info_grid.add_widget(item_layout)
        
        status_layout.add_widget(section_title)
        status_layout.add_widget(info_grid)
        
        return status_layout
    
    def _create_ascension_options(self) -> ScrollView:
        """Crea las opciones de ascensión disponibles."""
        scroll = ScrollView(size_hint_y=0.6)
        
        options_layout = BoxLayout(orientation='horizontal', spacing=20, size_hint_y=None)
        options_layout.bind(minimum_height=options_layout.setter('height'))
        
        # Simular datos del jugador
        player_level = getattr(self.game_state, 'player_level', 75)
        boss_defeated = True  # Simular boss derrotado
        secret_completed = True  # Simular mazmorra secreta completada
        
        # Crear cards para cada tipo de ascensión
        for ascension_type in [AscensionType.MINOR, AscensionType.MAJOR, AscensionType.DIMENSION]:
            card = AscensionCard(
                ascension_type, 
                self.prestige_manager, 
                player_level, 
                boss_defeated, 
                secret_completed,
                size_hint_x=None,
                width=300,
                size_hint_y=None,
                height=280
            )
            options_layout.add_widget(card)
        
        scroll.add_widget(options_layout)
        return scroll
    
    def _create_navigation_buttons(self) -> BoxLayout:
        """Crea los botones de navegación."""
        nav_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=60, spacing=20)
        
        # Botón de estadísticas detalladas
        stats_button = Button(
            text="� Estadísticas Detalladas",
            font_size='16sp',
            size_hint_x=0.4,
            background_color=[0.2, 0.6, 0.8, 1]
        )
        stats_button.bind(on_press=self.show_detailed_stats)
        
        # Espaciador
        spacer = Label(text="", size_hint_x=0.2)
        
        # Botón de cerrar
        close_button = Button(
            text="🔙 Volver al Juego",
            font_size='16sp',
            size_hint_x=0.4,
            background_color=[0.3, 0.3, 0.6, 1]
        )
        close_button.bind(on_press=self.on_close_button)
        
    
    def show_ascension_confirmation(self, ascension_type: AscensionType):
        """Muestra la confirmación épica de ascensión."""
        preview = self.prestige_manager.get_ascension_preview(ascension_type, getattr(self.game_state, 'player_level', 75))
        
        type_names = {
            AscensionType.MINOR: "Ascensión Menor",
            AscensionType.MAJOR: "Ascensión Mayor", 
            AscensionType.DIMENSION: "Ascensión Dimensional"
        }
        
        confirmation_popup = Popup(
            title=f'🌌 {type_names[ascension_type]} 🌌',
            size_hint=(0.9, 0.8)
        )
        
        content = BoxLayout(orientation='vertical', spacing=15)
        
        # Header épico
        epic_header = Label(
            text="⚡ PREPARÁNDOSE PARA LA ASCENSIÓN ⚡",
            font_size='24sp',
            color=[1, 0.8, 0.2, 1],
            bold=True,
            size_hint_y=None,
            height=50,
            halign='center'
        )
        epic_header.text_size = (epic_header.width, epic_header.height)
        
        # Información de la ascensión
        info_text = f"""
🌟 RECOMPENSAS DE ASCENSIÓN:

💎 Fragmentos de Esencia: +{preview['essence_fragments_gain']}
⚡ Bonificación de Stats: +{preview['stat_bonus_percentage']:.0f}% PERMANENTE
🔓 Desbloqueo Especial: {preview.get('special_unlock', 'Ninguno')}

📊 ESTADO DESPUÉS DE ASCENSIÓN:
💎 Total Fragmentos: {preview['new_total_essence']}
⚡ Nuevo Multiplicador: {preview['new_stat_bonus']:.2f}x

⚠️  LO QUE PERDERÁS AL ASCENDER:
🔄 Nivel del explorador (volverás a nivel 1)
💰 Todo el oro y recursos acumulados
🏗️  Progreso actual de mazmorras y combates
📦 Inventario y equipamiento actual

✅ LO QUE MANTENDRÁS:
🎯 Todos los talentos y sus mejoras
💎 Fragmentos de esencia y bonificaciones
🏆 Logros y estadísticas permanentes
🌌 Acceso a dimensiones desbloqueadas
        """
        
        info_label = Label(
            text=info_text.strip(),
            font_size='14sp',
            color=[1, 1, 1, 1],
            halign='center',
            text_size=(None, None)
        )
        
        # Botones épicos
        buttons_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=60, spacing=15)
        
        confirm_button = Button(
            text="� ¡ASCENDER A DIMENSIÓN SUPERIOR!",
            font_size='16sp',
            background_color=[0.2, 0.8, 1.0, 1],
            bold=True
        )
        confirm_button.bind(on_press=lambda x: self._perform_ascension(confirmation_popup, ascension_type))
        
        cancel_button = Button(
            text="🔙 Permanecer en Esta Dimensión",
            font_size='14sp',
            background_color=[0.6, 0.3, 0.3, 1]
        )
        cancel_button.bind(on_press=confirmation_popup.dismiss)
        
        buttons_layout.add_widget(confirm_button)
        buttons_layout.add_widget(cancel_button)
        
        content.add_widget(epic_header)
        content.add_widget(info_label)
        content.add_widget(buttons_layout)
        
        confirmation_popup.content = content
        confirmation_popup.open()
    
    def _perform_ascension(self, popup, ascension_type: AscensionType):
        """Realiza la ascensión dimensional."""
        popup.dismiss()
        
        # Simular datos para la ascensión
        player_level = getattr(self.game_state, 'player_level', 75)
        
        # Realizar ascensión
        reward = self.prestige_manager.perform_ascension(
            ascension_type, 
            player_level, 
            boss_defeated=True, 
            secret_dungeon_completed=True
        )
        
        if reward:
            self._show_ascension_success(reward, ascension_type)
        else:
            self._show_ascension_error()
    
    def _show_ascension_success(self, reward: DimensionalReward, ascension_type: AscensionType):
        """Muestra el resultado exitoso de la ascensión."""
        type_names = {
            AscensionType.MINOR: "Ascensión Menor",
            AscensionType.MAJOR: "Ascensión Mayor",
            AscensionType.DIMENSION: "Ascensión Dimensional"
        }
        
        success_popup = Popup(
            title='🌟 ¡ASCENSIÓN COMPLETADA! 🌟',
            size_hint=(0.8, 0.7)
        )
        
        content = BoxLayout(orientation='vertical', spacing=15)
        
        # Título épico
        success_header = Label(
            text=f"✨ {type_names[ascension_type]} Exitosa ✨",
            font_size='28sp',
            color=[0.2, 1, 0.2, 1],
            bold=True,
            size_hint_y=None,
            height=60,
            halign='center'
        )
        success_header.text_size = (success_header.width, success_header.height)
        
        # Resultados
        results_text = f"""
🎉 ¡HAS ASCENDIDO A UNA DIMENSIÓN SUPERIOR! 🎉

💎 Fragmentos de Esencia Ganados: +{reward.essence_fragments}
⚡ Bonificación Permanente: +{reward.stat_bonus * 100:.0f}% a todas las estadísticas

{f"🔓 Nuevo Contenido Desbloqueado: {reward.special_unlock}" if reward.special_unlock else ""}

🌌 Tu viaje como explorador dimensional continúa...
¡Con poderes mejorados para enfrentar nuevos desafíos!

� Estadísticas Actualizadas:
💎 Total Fragmentos: {self.prestige_manager.essence_fragments}
🌌 Dimensión Actual: {self.prestige_manager.current_dimension}
⬆️ Total Ascensiones: {self.prestige_manager.total_ascensions}
        """
        
        results_label = Label(
            text=results_text.strip(),
            font_size='16sp',
            color=[1, 1, 1, 1],
            halign='center',
            text_size=(None, None)
        )
        
        # Botón de continuar
        continue_button = Button(
            text="🚀 ¡Comenzar Nueva Aventura!",
            font_size='18sp',
            size_hint_y=None,
            height=60,
            background_color=[0.2, 1, 0.2, 1],
            bold=True
        )
        continue_button.bind(on_press=lambda x: self._finish_ascension(success_popup))
        
        content.add_widget(success_header)
        content.add_widget(results_label)
        content.add_widget(continue_button)
        
        success_popup.content = content
        success_popup.open()
    
    def _show_ascension_error(self):
        """Muestra error en la ascensión."""
        error_popup = Popup(
            title='❌ Error en Ascensión',
            size_hint=(0.6, 0.4)
        )
        
        error_text = """
❌ No fue posible completar la ascensión.

Verifica que cumples todos los requisitos:
• Nivel mínimo requerido
• Boss de dimensión derrotado
• Mazmorra secreta completada (para Ascensión Mayor)
        """
        
        error_label = Label(
            text=error_text.strip(),
            font_size='14sp',
            color=[1, 0.5, 0.5, 1],
            halign='center'
        )
        error_label.text_size = (error_label.width, error_label.height)
        
        ok_button = Button(
            text="� Entendido",
            size_hint_y=None,
            height=50,
            font_size='16sp',
            background_color=[0.6, 0.3, 0.3, 1]
        )
        ok_button.bind(on_press=error_popup.dismiss)
        
        content = BoxLayout(orientation='vertical', spacing=10)
        content.add_widget(error_label)
        content.add_widget(ok_button)
        
        error_popup.content = content
        error_popup.open()
    
    def _finish_ascension(self, popup):
        """Finaliza la ascensión y regresa al juego."""
        popup.dismiss()
        
        # Actualizar UI
        self.clear_widgets()
        self._create_ui()
        
        # Volver al juego principal
        self.navigate_to('main')
    
    def show_detailed_stats(self, instance):
        """Muestra estadísticas detalladas del sistema dimensional."""
        stats = self.prestige_manager.get_dimensional_stats()
        
        stats_popup = Popup(
            title='📊 Estadísticas Dimensionales',
            size_hint=(0.8, 0.8)
        )
        
        stats_text = f"""
🌌 ESTADO DEL EXPLORADOR DIMENSIONAL 🌌

📈 ASCENSIONES REALIZADAS:
⬆️ Total: {stats['total_ascensions']}
🔹 Ascensiones Menores: {stats['minor_ascensions']}
🔸 Ascensiones Mayores: {stats['major_ascensions']}
🔷 Ascensiones Dimensionales: {stats['dimension_ascensions']}

💎 FRAGMENTOS DE ESENCIA:
💎 Total Fragmentos: {stats['essence_fragments']}
⚡ Bonificación de Stats: {stats['dimensional_stat_bonus']:.2f}x
🗺️  Bonificación de Exploración: {stats['exploration_bonus']:.2f}x
📚 Bonificación de Experiencia: {stats['experience_bonus']:.2f}x
💫 Bonificación de Ganancia de Esencia: {stats['essence_gain_bonus']:.2f}x

🌌 CONTENIDO DESBLOQUEADO:
🌍 Dimensión Actual: {stats['current_dimension']}
🌌 Dimensiones Totales: {len(stats['unlocked_dimensions'])}
🏰 Mazmorras Secretas: {len(stats['unlocked_secret_dungeons'])}

🔮 Dimensiones Disponibles: {', '.join(map(str, stats['unlocked_dimensions']))}
🗝️  Mazmorras Secretas: {', '.join(stats['unlocked_secret_dungeons']) or 'Ninguna'}
        """
        
        stats_label = Label(
            text=stats_text.strip(),
            font_size='14sp',
            color=[1, 1, 1, 1],
            halign='center',
            text_size=(None, None)
        )
        
        close_button = Button(
            text="🔙 Cerrar",
            size_hint_y=None,
            height=50,
            font_size='16sp',
            background_color=[0.3, 0.3, 0.6, 1]
        )
        close_button.bind(on_press=stats_popup.dismiss)
        
        content = BoxLayout(orientation='vertical', spacing=10)
        content.add_widget(stats_label)
        content.add_widget(close_button)
        
        stats_popup.content = content
        stats_popup.open()
    
    def on_close_button(self, instance):
        """Maneja el clic en el botón de cerrar."""
        logging.info("Cerrando pantalla de ascensión dimensional")
        self.go_back()
    
    def update_ui(self, dt: float = 0):
        """Actualiza la interfaz con los datos actuales."""
        try:
            # Recrear la interfaz para reflejar cambios
            self.clear_widgets()
            self._create_ui()
            
            logging.debug("UI de ascensión dimensional actualizada")
        except Exception as e:
            logging.error(f"Error actualizando UI de ascensión dimensional: {e}")
    
    def on_enter(self, *args):
        """Se ejecuta cuando se entra a la pantalla."""
        super().on_enter(*args)
        logging.info("Entrando a pantalla de ascensión dimensional")
        
        # Actualizar UI inmediatamente
        self.update_ui()
    
    def on_leave(self, *args):
        """Se ejecuta cuando se sale de la pantalla."""
        super().on_leave(*args)
        logging.info("Saliendo de pantalla de ascensión dimensional")
