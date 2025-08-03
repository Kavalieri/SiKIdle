"""SiKIdle - Videojuego tipo idle clicker 2D.

Punto de entrada principal del juego.
Desarrollado en Python con Kivy, orientado principalmente a Android.
Optimizado para pantallas verticales (móviles).
"""

from config.mobile_config import MobileConfig

# Configurar la aplicación para móviles ANTES de importar Kivy
MobileConfig.configure_for_mobile()

from kivy.app import App  # type: ignore
from kivy.uix.boxlayout import BoxLayout  # type: ignore
from kivy.uix.button import Button  # type: ignore
from kivy.uix.label import Label  # type: ignore
from kivy.utils import platform  # type: ignore

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
			bold=True,
			color=[0.2, 0.8, 1, 1]  # Azul claro
		)

		# Mensaje de bienvenida con ajuste de texto
		welcome_label = Label(
			text='¡Bienvenido al juego idle clicker más adictivo! Toca, mejora y automatiza tu imperio.',
			font_size='16sp',
			size_hint=(1, 0.3),
			color=[0.9, 0.9, 0.9, 1],  # Gris claro
			halign='center',
			valign='center'
		)
		# Ajustar el texto al ancho del label (crítico para móviles)
		welcome_label.text_size = (400, None)  # Ajustado para resolución más grande

		# Botón de prueba táctil
		test_button = Button(
			text='¡Toca aquí para probar!',
			font_size='18sp',
			size_hint=(1, 0.15),
			background_color=[1, 0.6, 0, 1]  # Naranja
		)
		test_button.bind(on_press=self.on_test_button_press)

		# Información del dispositivo/configuración móvil
		config_info = MobileConfig.get_resolution_info()
		device_info_text = (
			f'Plataforma: {platform}\n'
			f'Resolución: {config_info["width"]}x{config_info["height"]} ({config_info["key"]})\n'
			f'Descripción: {config_info["description"]}'
		)
		device_info = Label(
			text=device_info_text,
			font_size='12sp',
			size_hint=(1, 0.35),
			color=[0.7, 0.7, 0.7, 1]  # Gris
		)

		# Agregar todos los widgets al layout
		root.add_widget(title_label)
		root.add_widget(welcome_label)
		root.add_widget(test_button)
		root.add_widget(device_info)

		return root

	def on_test_button_press(self, instance: Button) -> None:
		"""Maneja el evento de presionar el botón de prueba."""
		instance.text = '¡Funciona perfectamente!'
	
	def get_application_name(self) -> str:
		"""Obtiene el nombre de la aplicación."""
		return 'SiKIdle'
	
	def get_application_icon(self) -> str:
		"""Obtiene el icono de la aplicación."""
		return ''


def main() -> None:
	"""Función principal de entrada del juego."""	
	# Crear y ejecutar la aplicación
	app = SiKIdleApp()
	app.title = 'SiKIdle - Mobile Idle Clicker'
	app.run()


if __name__ == '__main__':
	main()
