"""SiKIdle - Videojuego tipo idle clicker 2D.

Punto de entrada principal del juego.
Desarrollado en Python con Kivy, orientado principalmente a Android.
Optimizado para pantallas verticales (móviles).
"""

from config.mobile_config import MobileConfig

# Configurar la aplicación para móviles ANTES de importar Kivy
MobileConfig.configure_for_mobile()

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.utils import platform

from utils.paths import ensure_directories


class SiKIdleApp(App):
	"""Aplicación principal de SiKIdle optimizada para móviles."""
	
	def build(self):
		"""Construye la interfaz principal del juego.
		
		Returns:
			Widget: Widget raíz de la aplicación
		"""
		# Asegurar que existen los directorios necesarios
		ensure_directories()

		# Layout principal optimizado para móviles
		root = BoxLayout(
			orientation='vertical',
			padding=[20, 40, 20, 20],  # top padding mayor para móviles
			spacing=20
		)

		# Título del juego - más grande para móviles
		title_label = Label(
			text='SiKIdle',
			font_size='48sp',  # Más grande para pantallas móviles
			size_hint=(1, 0.2),
			halign='center'
		)

		# Mensaje de bienvenida
		welcome_label = Label(
			text='¡Bienvenido a SiKIdle!\n\nJuego idle clicker para móviles\nOptimizado para pantallas verticales',
			font_size='20sp',
			size_hint=(1, 0.4),
			halign='center',
			valign='middle'
		)
		# Configurar text_size usando ancho fijo móvil (320 píxeles para dejar margen)
		welcome_label.text_size = (320, None)

		# Botón de prueba para interacción táctil
		test_button = Button(
			text='¡Toca para comenzar!',
			size_hint=(0.8, None),
			height='60dp',  # Altura fija para botones móviles
			pos_hint={'center_x': 0.5},
			font_size='24sp'
		)
		test_button.bind(on_press=self.on_test_button_press)

		# Información del dispositivo con debug de ventana
		device_info_text = f'Plataforma: {platform}\nOptimizado para: Android/Móviles\nVentana: FIJA 360x640px (no redimensionable)'
		device_info = Label(
			text=device_info_text,
			font_size='14sp',
			size_hint=(1, 0.1),
			halign='center'
		)

		root.add_widget(title_label)
		root.add_widget(welcome_label)
		root.add_widget(test_button)
		root.add_widget(device_info)

		return root

	def on_test_button_press(self, instance: Button) -> None:
		"""Maneja el evento de presionar el botón de prueba."""
		instance.text = '¡Funciona perfectamente!'
	
	def get_application_name(self):
		"""Obtiene el nombre de la aplicación."""
		return 'SiKIdle'
	
	def get_application_icon(self):
		"""Obtiene el icono de la aplicación."""
		return ''


def main():
	"""Función principal de entrada del juego."""
	# Configurar para móviles antes de crear la app
	configure_for_mobile()
	
	# Crear y ejecutar la aplicación
	app = SiKIdleApp()
	app.title = 'SiKIdle - Mobile Idle Clicker'
	app.run()


if __name__ == '__main__':
	main()
