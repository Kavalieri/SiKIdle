"""
Pantalla de Tienda Premium para SiKIdle.

Interfaz para comprar gemas, boosts temporales, aceleradores y cosméticos.
Diseño no intrusivo que enfatiza conveniencia sobre necesidad.
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.clock import Clock

import logging
from core.premium_shop import PremiumItemType, PremiumItem


class PremiumItemWidget(BoxLayout):
	"""Widget para mostrar un item premium."""
	
	def __init__(self, item: PremiumItem, shop_manager, **kwargs):
		super().__init__(**kwargs)
		self.item = item
		self.shop_manager = shop_manager
		self.orientation = 'vertical'
		self.size_hint_y = None
		self.height = 120
		self.spacing = 4
		self.padding = [8, 8, 8, 8]
		
		self._setup_styling()
		self._build_content()
	
	def _setup_styling(self):
		"""Configura el estilo del widget."""
		from kivy.graphics import Color, RoundedRectangle
		
		# Color según tipo de item
		colors = {
			PremiumItemType.GEM_PACK: (0.3, 0.2, 0.8, 0.8),      # Morado
			PremiumItemType.TEMPORARY_BOOST: (0.8, 0.6, 0.2, 0.8), # Dorado
			PremiumItemType.PROGRESS_ACCELERATOR: (0.2, 0.8, 0.3, 0.8), # Verde
			PremiumItemType.COSMETIC: (0.8, 0.2, 0.6, 0.8),      # Rosa
			PremiumItemType.CONVENIENCE: (0.2, 0.6, 0.8, 0.8)    # Azul
		}
		
		with self.canvas.before:
			Color(*colors.get(self.item.item_type, (0.4, 0.4, 0.4, 0.8)))
			self.bg_rect = RoundedRectangle(
				pos=self.pos,
				size=self.size,
				radius=[8, 8, 8, 8]
			)
		
		self.bind(pos=self._update_bg, size=self._update_bg)
	
	def _update_bg(self, *args):
		"""Actualiza el fondo del widget."""
		if hasattr(self, 'bg_rect'):
			self.bg_rect.pos = self.pos
			self.bg_rect.size = self.size
	
	def _build_content(self):
		"""Construye el contenido del widget."""
		# Header con icono y nombre
		header_layout = BoxLayout(
			orientation='horizontal',
			size_hint_y=None,
			height=30
		)
		
		name_label = Label(
			text=f"{self.item.icon} {self.item.name}",
			font_size='16sp',
			bold=True,
			size_hint_x=0.7,
			halign='left',
			valign='center'
		)
		name_label.bind(texture_size=name_label.setter('text_size'))
		
		# Precio
		price_text = self._get_price_text()
		price_label = Label(
			text=price_text,
			font_size='14sp',
			bold=True,
			size_hint_x=0.3,
			halign='right',
			valign='center',
			color=(1, 1, 0.6, 1)  # Amarillo
		)
		price_label.bind(texture_size=price_label.setter('text_size'))
		
		header_layout.add_widget(name_label)
		header_layout.add_widget(price_label)
		
		# Descripción
		desc_label = Label(
			text=self.item.description,
			font_size='12sp',
			size_hint_y=None,
			height=25,
			halign='left',
			valign='center',
			color=(0.9, 0.9, 0.9, 1)
		)
		desc_label.bind(texture_size=desc_label.setter('text_size'))
		
		# Botón de compra
		self.buy_button = Button(
			text=self._get_button_text(),
			font_size='14sp',
			size_hint_y=None,
			height=35
		)
		self.buy_button.bind(on_press=self._on_purchase)
		self._update_button_state()
		
		# Ensamblar
		self.add_widget(header_layout)
		self.add_widget(desc_label)
		self.add_widget(self.buy_button)
	
	def _get_price_text(self) -> str:
		"""Obtiene el texto del precio."""
		if self.item.real_money_cost:
			return f"{self.item.real_money_cost:.2f}€"
		else:
			return f"{self.item.gem_cost} 💎"
	
	def _get_button_text(self) -> str:
		"""Obtiene el texto del botón."""
		if self.item.item_type == PremiumItemType.GEM_PACK:
			return "💳 COMPRAR"
		else:
			return f"💎 {self.item.gem_cost}"
	
	def _update_button_state(self):
		"""Actualiza el estado del botón."""
		if self.item.item_type == PremiumItemType.GEM_PACK:
			self.buy_button.background_color = (0.2, 0.8, 0.2, 1)  # Verde
			self.buy_button.disabled = False
		else:
			can_afford = self.shop_manager.can_afford_gems(self.item.gem_cost)
			self.buy_button.background_color = (0.2, 0.8, 0.2, 1) if can_afford else (0.6, 0.3, 0.3, 1)
			self.buy_button.disabled = not can_afford
	
	def _on_purchase(self, button):
		"""Maneja la compra del item."""
		if self.item.item_type == PremiumItemType.GEM_PACK:
			self._purchase_gem_pack()
		else:
			self._purchase_with_gems()
	
	def _purchase_gem_pack(self):
		"""Compra un paquete de gemas."""
		# Mostrar confirmación
		content = BoxLayout(orientation='vertical', spacing=10)
		
		info_text = f"¿Comprar {self.item.name}?\n\n+{self.item.gem_cost} 💎 Gemas\nPrecio: {self.item.real_money_cost:.2f}€"
		
		info_label = Label(text=info_text, halign='center', valign='center')
		info_label.bind(texture_size=info_label.setter('text_size'))
		
		buttons_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, spacing=10)
		
		confirm_button = Button(text="✅ COMPRAR", background_color=(0.2, 0.8, 0.2, 1))
		cancel_button = Button(text="❌ Cancelar", background_color=(0.8, 0.2, 0.2, 1))
		
		popup = Popup(title="Comprar Gemas", content=content, size_hint=(0.8, 0.6))
		
		def on_confirm(btn):
			result = self.shop_manager.purchase_gem_pack(self.item.id)
			popup.dismiss()
			if result['success']:
				success_popup = Popup(
					title="¡Compra Exitosa!",
					content=Label(text=f"¡Has recibido {result['gems_added']} gemas!\nTotal: {result['total_gems']} 💎"),
					size_hint=(0.7, 0.4)
				)
				success_popup.open()
		
		confirm_button.bind(on_press=on_confirm)
		cancel_button.bind(on_press=popup.dismiss)
		
		buttons_layout.add_widget(confirm_button)
		buttons_layout.add_widget(cancel_button)
		content.add_widget(info_label)
		content.add_widget(buttons_layout)
		
		popup.open()
	
	def _purchase_with_gems(self):
		"""Compra un item con gemas."""
		result = self.shop_manager.purchase_with_gems(self.item.id)
		
		if result['success']:
			success_text = f"¡{self.item.name} activado!"
			if 'duration' in result:
				success_text += f"\nDuración: {result['duration']} minutos"
			
			popup = Popup(
				title="¡Compra Exitosa!",
				content=Label(text=success_text),
				size_hint=(0.7, 0.4)
			)
			popup.open()
		else:
			error_popup = Popup(
				title="Error",
				content=Label(text=f"No se pudo comprar: {result['reason']}"),
				size_hint=(0.6, 0.4)
			)
			error_popup.open()


class PremiumShopScreen(Screen):
	"""Pantalla de tienda premium."""
	
	def __init__(self, name='premium_shop', **kwargs):
		super().__init__(name=name, **kwargs)
		
		self.game_state = None
		self.update_event = None
		
		self._build_layout()
		logging.info("PremiumShopScreen initialized")
	
	def _build_layout(self):
		"""Construye el layout principal."""
		main_layout = BoxLayout(orientation='vertical')
		
		# Header con gemas
		header = self._create_header()
		main_layout.add_widget(header)
		
		# Scroll con categorías de items
		scroll = ScrollView()
		self.content_layout = BoxLayout(
			orientation='vertical',
			size_hint_y=None,
			spacing=16,
			padding=[16, 16, 16, 16]
		)
		self.content_layout.bind(minimum_height=self.content_layout.setter('height'))
		
		scroll.add_widget(self.content_layout)
		main_layout.add_widget(scroll)
		
		self.add_widget(main_layout)
	
	def _create_header(self) -> BoxLayout:
		"""Crea el header con información de gemas."""
		header = BoxLayout(
			orientation='horizontal',
			size_hint_y=None,
			height=80,
			padding=[16, 16, 16, 16],
			spacing=16
		)
		
		# Título
		title = Label(
			text="💎 TIENDA PREMIUM",
			font_size='24sp',
			bold=True,
			size_hint_x=0.6,
			color=(1, 0.8, 0, 1)  # Dorado
		)
		
		# Contador de gemas
		self.gems_label = Label(
			text="💎 0 Gemas",
			font_size='20sp',
			bold=True,
			size_hint_x=0.4,
			halign='right',
			color=(0.8, 0.6, 1, 1)  # Morado claro
		)
		self.gems_label.bind(texture_size=self.gems_label.setter('text_size'))
		
		header.add_widget(title)
		header.add_widget(self.gems_label)
		
		return header
	
	def _update_content(self):
		"""Actualiza el contenido de la tienda."""
		if not self.game_state or not hasattr(self.game_state, 'premium_shop'):
			return
		
		# Limpiar contenido anterior
		self.content_layout.clear_widgets()
		
		# Actualizar header
		self.gems_label.text = f"💎 {self.game_state.premium_shop.gems} Gemas"
		
		# Crear secciones por tipo
		categories = [
			(PremiumItemType.GEM_PACK, "💎 Paquetes de Gemas"),
			(PremiumItemType.TEMPORARY_BOOST, "⚡ Boosts Temporales"),
			(PremiumItemType.PROGRESS_ACCELERATOR, "🚀 Aceleradores"),
			(PremiumItemType.CONVENIENCE, "🛠️ Conveniencia"),
			(PremiumItemType.COSMETIC, "✨ Cosméticos")
		]
		
		for item_type, title in categories:
			items = self.game_state.premium_shop.get_catalog_by_type(item_type)
			if items:
				section = self._create_category_section(title, items)
				self.content_layout.add_widget(section)
	
	def _create_category_section(self, title: str, items: list) -> BoxLayout:
		"""Crea una sección de categoría."""
		section = BoxLayout(
			orientation='vertical',
			size_hint_y=None,
			spacing=8,
			padding=[8, 8, 8, 8]
		)
		
		# Título de categoría
		title_label = Label(
			text=title,
			font_size='18sp',
			bold=True,
			size_hint_y=None,
			height=30,
			halign='left',
			color=(1, 1, 0.8, 1)
		)
		title_label.bind(texture_size=title_label.setter('text_size'))
		
		section.add_widget(title_label)
		
		# Items de la categoría
		for item in items:
			item_widget = PremiumItemWidget(item, self.game_state.premium_shop)
			section.add_widget(item_widget)
		
		# Calcular altura
		section.height = 30 + (len(items) * 128)  # título + items + spacing
		
		return section
	
	def on_enter(self):
		"""Callback cuando se entra a la pantalla."""
		logging.info("Entered PremiumShopScreen")
		
		# Obtener referencia al game state
		try:
			from core.game import get_game_state
			self.game_state = get_game_state()
		except Exception as e:
			logging.error(f"Error getting game state: {e}")
		
		# Actualizar contenido
		self._update_content()
		
		# Programar actualizaciones periódicas
		if not self.update_event:
			self.update_event = Clock.schedule_interval(self._update_gems_display, 2.0)
	
	def _update_gems_display(self, dt):
		"""Actualiza solo el display de gemas."""
		if self.game_state and hasattr(self.game_state, 'premium_shop'):
			self.gems_label.text = f"💎 {self.game_state.premium_shop.gems} Gemas"
	
	def on_leave(self):
		"""Callback cuando se sale de la pantalla."""
		logging.info("Left PremiumShopScreen")
		
		# Cancelar actualizaciones
		if self.update_event:
			Clock.unschedule(self.update_event)
			self.update_event = None