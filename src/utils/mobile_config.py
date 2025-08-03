"""Configuración móvil para SiKIdle.

Sistema de configuración optimizado para dispositivos móviles
con soporte para diferentes resoluciones y orientaciones.
"""

import logging
import os
from typing import Any


def setup_mobile_environment():
	"""Configura el entorno para dispositivos móviles."""
	try:
		# Configuración de Kivy para móviles
		os.environ['KIVY_WINDOW'] = 'sdl2'
		os.environ['KIVY_GL_BACKEND'] = 'angle_sdl2'
		os.environ['USE_OPENGL_MOCK'] = '1'  # Para desarrollo/testing

		# Configurar resolución por defecto
		from kivy.config import Config
		Config.set('graphics', 'width', '428')
		Config.set('graphics', 'height', '926')
		Config.set('graphics', 'resizable', '0')

		# Configuración para Android
		Config.set('kivy', 'keyboard_mode', 'systemandmulti')
		Config.set('graphics', 'orientation', 'portrait')

		logging.info("Entorno móvil configurado correctamente")

	except Exception as e:
		logging.error(f"Error configurando entorno móvil: {e}")


def get_mobile_config() -> dict[str, Any]:
	"""Obtiene la configuración móvil actual.
	
	Returns:
		Diccionario con configuración móvil
	"""
	return {
		'width': 428,
		'height': 926,
		'orientation': 'portrait',
		'touch_optimized': True,
		'android_ready': True
	}
