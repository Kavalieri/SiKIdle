"""SiKIdle - Videojuego tipo idle clicker 2D.

Punto de entrada principal del juego.
Desarrollado en Python con Kivy, orientado principalmente a Android.
Optimizado para pantallas verticales (móviles).
"""

from kivy.app import App
from kivy.config import Config
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.utils import platform

from utils.paths import ensure_directories


# Configuración para móviles antes de importar otros módulos de Kivy
def configure_for_mobile():
	"""Configura la aplicación para dispositivos móviles."""
	# Configuración específica para Android/móviles
	if platform == 'android':
		# En Android, la ventana se ajusta automáticamente
		pass
	else:
		# En desktop, simular una pantalla móvil vertical
		Config.set('graphics', 'width', '360')   # Ancho típico de móvil
		Config.set('graphics', 'height', '640')  # Alto típico de móvil
		Config.set('graphics', 'resizable', True)
	
	# Configuraciones generales para móviles
	Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
	Config.write()


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
		welcome_label.text_size = (Window.width * 0.9, None)

		# Botón de prueba para interacción táctil
		test_button = Button(
			text='¡Toca para comenzar!',
			size_hint=(0.8, None),
			height='60dp',  # Altura fija para botones móviles
			pos_hint={'center_x': 0.5},
			font_size='24sp'
		)
		test_button.bind(on_press=self.on_test_button_press)

		# Información del dispositivo
		device_info = Label(
			text=f'Plataforma: {platform}\nOptimizado para: Android/Móviles',
			font_size='14sp',
			size_hint=(1, 0.1),
			halign='center'
		)

		root.add_widget(title_label)
		root.add_widget(welcome_label)
		root.add_widget(test_button)
		root.add_widget(device_info)

		return root
	
	def on_test_button_press(self, instance):
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
