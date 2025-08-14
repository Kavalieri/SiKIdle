"""
Pantalla de Prestigio Simple para SiKIdle.

Pantalla que permite al jugador hacer prestigio para ganar cristales
y multiplicadores permanentes.
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.clock import Clock

import logging


class PrestigeScreen(Screen):
    """Pantalla de prestigio simple."""
    
    def __init__(self, name='prestige', **kwargs):
        super().__init__(name=name, **kwargs)
        
        self.game_state = None
        self.update_event = None
        
        self._build_layout()
        logging.info("PrestigeScreen initialized")
    
    def _build_layout(self):
        """Construye el layout de la pantalla."""
        main_layout = BoxLayout(
            orientation='vertical',
            padding=[16, 16, 16, 16],
            spacing=16
        )
        
        # Header
        header_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=50
        )
        
        title_label = Label(
            text="💎 PRESTIGIO",
            font_size='20sp',
            bold=True,
            size_hint_x=0.8
        )
        
        header_layout.add_widget(title_label)
        
        # Información actual
        self.current_info_layout = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=120,
            spacing=8
        )
        
        self.current_crystals_label = Label(
            text="💎 Cristales: 0",
            font_size='16sp',
            size_hint_y=None,
            height=30
        )
        
        self.current_multiplier_label = Label(
            text="⚡ Multiplicador: 1.0x",
            font_size='16sp',
            size_hint_y=None,
            height=30
        )
        
        self.prestige_count_label = Label(
            text="🔄 Prestiges: 0",
            font_size='16sp',
            size_hint_y=None,
            height=30
        )
        
        self.lifetime_coins_label = Label(
            text="💰 Monedas Totales: 0",
            font_size='14sp',
            size_hint_y=None,
            height=30
        )
        
        self.current_info_layout.add_widget(self.current_crystals_label)
        self.current_info_layout.add_widget(self.current_multiplier_label)
        self.current_info_layout.add_widget(self.prestige_count_label)
        self.current_info_layout.add_widget(self.lifetime_coins_label)
        
        # Preview del prestigio
        self.preview_layout = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=150,
            spacing=8
        )
        
        preview_title = Label(
            text="📊 Preview del Prestigio:",
            font_size='18sp',
            bold=True,
            size_hint_y=None,
            height=30
        )
        
        self.crystals_gained_label = Label(
            text="💎 Cristales a ganar: 0",
            font_size='14sp',
            size_hint_y=None,
            height=25
        )
        
        self.new_multiplier_label = Label(
            text="⚡ Nuevo multiplicador: 1.0x",
            font_size='14sp',
            size_hint_y=None,
            height=25
        )
        
        self.multiplier_increase_label = Label(
            text="📈 Aumento: +0.0x",
            font_size='14sp',
            size_hint_y=None,
            height=25
        )
        
        self.requirement_label = Label(
            text="⚠️ Necesitas 100,000 monedas para prestigio",
            font_size='12sp',
            color=(0.8, 0.8, 0.2, 1),
            size_hint_y=None,
            height=25
        )
        
        self.preview_layout.add_widget(preview_title)
        self.preview_layout.add_widget(self.crystals_gained_label)
        self.preview_layout.add_widget(self.new_multiplier_label)
        self.preview_layout.add_widget(self.multiplier_increase_label)
        self.preview_layout.add_widget(self.requirement_label)
        
        # Botón de prestigio
        self.prestige_button = Button(
            text="🔄 HACER PRESTIGIO",
            font_size='18sp',
            size_hint_y=None,
            height=60,
            background_color=(0.8, 0.2, 0.2, 1)  # Rojo por defecto (deshabilitado)
        )
        self.prestige_button.bind(on_press=self._on_prestige_button)
        
        # Información sobre el prestigio
        info_label = Label(
            text="El prestigio resetea tu progreso pero te da cristales\nque proporcionan multiplicadores permanentes.",
            font_size='12sp',
            color=(0.7, 0.7, 0.7, 1),
            size_hint_y=None,
            height=40,
            halign='center'
        )
        info_label.bind(texture_size=info_label.setter('text_size'))
        
        # Ensamblar layout
        main_layout.add_widget(header_layout)
        main_layout.add_widget(self.current_info_layout)
        main_layout.add_widget(self.preview_layout)
        main_layout.add_widget(self.prestige_button)
        main_layout.add_widget(info_label)
        
        self.add_widget(main_layout)
    
    def _on_prestige_button(self, instance):
        """Maneja el clic en el botón de prestigio."""
        if not self.game_state:
            return
        
        # Obtener preview
        preview = self.game_state.prestige_manager.get_prestige_preview(
            self.game_state.lifetime_coins
        )
        
        if not preview['can_prestige']:
            popup = Popup(
                title="No se puede hacer prestigio",
                content=Label(text="Necesitas al menos 100,000 monedas\npara hacer prestigio."),
                size_hint=(0.6, 0.4)
            )
            popup.open()
            return
        
        # Confirmar prestigio
        self._show_prestige_confirmation(preview)
    
    def _show_prestige_confirmation(self, preview):
        """Muestra confirmación de prestigio."""
        content = BoxLayout(orientation='vertical', spacing=10)
        
        info_text = f"""¿Estás seguro de hacer prestigio?

Ganarás: {preview['crystals_gained']} cristales
Nuevo multiplicador: {preview['new_multiplier']:.2f}x
Aumento: +{preview['multiplier_increase']:.2f}x

⚠️ ESTO RESETEARÁ TODO TU PROGRESO ⚠️
(Edificios, monedas, etc.)"""
        
        info_label = Label(
            text=info_text,
            halign='center',
            valign='center'
        )
        info_label.bind(texture_size=info_label.setter('text_size'))
        
        buttons_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=50,
            spacing=10
        )
        
        confirm_button = Button(
            text="✅ SÍ, HACER PRESTIGIO",
            background_color=(0.2, 0.8, 0.2, 1)
        )
        
        cancel_button = Button(
            text="❌ Cancelar",
            background_color=(0.8, 0.2, 0.2, 1)
        )
        
        popup = Popup(
            title="Confirmar Prestigio",
            content=content,
            size_hint=(0.8, 0.6)
        )
        
        confirm_button.bind(on_press=lambda x: self._perform_prestige(popup))
        cancel_button.bind(on_press=popup.dismiss)
        
        buttons_layout.add_widget(confirm_button)
        buttons_layout.add_widget(cancel_button)
        
        content.add_widget(info_label)
        content.add_widget(buttons_layout)
        
        popup.open()
    
    def _perform_prestige(self, popup):
        """Realiza el prestigio."""
        popup.dismiss()
        
        if not self.game_state:
            return
        
        # Realizar prestigio
        result = self.game_state.prestige_manager.perform_prestige(
            self.game_state.lifetime_coins
        )
        
        if result['success']:
            # Resetear el juego
            self.game_state.reset_for_prestige()
            
            # Mostrar resultado
            result_popup = Popup(
                title="¡Prestigio Completado!",
                content=Label(
                    text=f"¡Prestigio exitoso!\n\n"
                         f"Cristales ganados: {result['crystals_gained']}\n"
                         f"Total cristales: {result['total_crystals']}\n"
                         f"Nuevo multiplicador: {result['new_multiplier']:.2f}x\n"
                         f"Prestiges totales: {result['prestige_count']}"
                ),
                size_hint=(0.7, 0.5)
            )
            result_popup.open()
            
            logging.info(f"Prestigio completado: {result}")
        else:
            error_popup = Popup(
                title="Error",
                content=Label(text=f"Error en prestigio: {result.get('reason', 'Error desconocido')}"),
                size_hint=(0.6, 0.4)
            )
            error_popup.open()
    
    def update_ui(self, dt=0):
        """Actualiza la interfaz con datos actuales."""
        if not self.game_state:
            return
        
        try:
            # Obtener estadísticas actuales
            stats = self.game_state.prestige_manager.get_stats()
            
            # Actualizar información actual
            self.current_crystals_label.text = f"💎 Cristales: {stats['prestige_crystals']}"
            self.current_multiplier_label.text = f"⚡ Multiplicador: {stats['income_multiplier']:.2f}x"
            self.prestige_count_label.text = f"🔄 Prestiges: {stats['prestige_count']}"
            self.lifetime_coins_label.text = f"💰 Monedas Totales: {self.game_state.lifetime_coins:,.0f}"
            
            # Obtener preview del prestigio
            preview = self.game_state.prestige_manager.get_prestige_preview(
                self.game_state.lifetime_coins
            )
            
            # Actualizar preview
            self.crystals_gained_label.text = f"💎 Cristales a ganar: {preview['crystals_gained']}"
            self.new_multiplier_label.text = f"⚡ Nuevo multiplicador: {preview['new_multiplier']:.2f}x"
            self.multiplier_increase_label.text = f"📈 Aumento: +{preview['multiplier_increase']:.2f}x"
            
            # Actualizar botón y requisitos
            if preview['can_prestige']:
                self.prestige_button.background_color = (0.2, 0.8, 0.2, 1)  # Verde
                self.prestige_button.disabled = False
                self.requirement_label.text = "✅ Puedes hacer prestigio"
                self.requirement_label.color = (0.2, 0.8, 0.2, 1)
            else:
                self.prestige_button.background_color = (0.8, 0.2, 0.2, 1)  # Rojo
                self.prestige_button.disabled = True
                needed = 100000 - self.game_state.lifetime_coins
                self.requirement_label.text = f"⚠️ Necesitas {needed:,.0f} monedas más"
                self.requirement_label.color = (0.8, 0.8, 0.2, 1)
                
        except Exception as e:
            logging.error(f"Error actualizando UI de prestigio: {e}")
    
    def on_enter(self):
        """Callback cuando se entra a la pantalla."""
        logging.info("Entered PrestigeScreen")
        
        # Obtener referencia al game state
        try:
            from core.game import get_game_state
            self.game_state = get_game_state()
        except Exception as e:
            logging.error(f"Error obteniendo game state: {e}")
        
        # Actualizar UI inmediatamente
        self.update_ui()
        
        # Programar actualizaciones
        if not self.update_event:
            self.update_event = Clock.schedule_interval(self.update_ui, 1.0)
    
    def on_leave(self):
        """Callback cuando se sale de la pantalla."""
        logging.info("Left PrestigeScreen")
        
        # Cancelar actualizaciones
        if self.update_event:
            Clock.unschedule(self.update_event)
            self.update_event = None