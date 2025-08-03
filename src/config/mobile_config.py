"""Configuración móvil para SiKIdle.

Contiene las diferentes opciones de resolución y configuraciones
para simulación móvil en desktop y configuración real en Android.
"""

from typing import Literal, Any
from kivy.utils import platform  # type: ignore
from kivy.config import Config  # type: ignore

# Tipos para las resoluciones
ResolutionKey = Literal['small', 'medium', 'large', 'extra']

class MobileConfig:
	"""Gestiona la configuración móvil del juego."""
	
	# Opciones de resolución móvil (ancho x alto)
	MOBILE_RESOLUTIONS: dict[ResolutionKey, tuple[int, int]] = {
		'small': (360, 640),    # Móviles antiguos/básicos - perfecto para pruebas básicas
		'medium': (414, 736),   # iPhone 8 Plus - buen balance para desarrollo
		'large': (428, 926),    # iPhone 12 Pro Max - moderna, más espacio vertical
		'extra': (480, 854),    # Resolución personalizada - máximo espacio para UI compleja
	}
	
	# Resolución por defecto (cambiar aquí para ajustar globalmente)
	DEFAULT_RESOLUTION: ResolutionKey = 'large'
	
	@classmethod
	def configure_for_mobile(cls, resolution: ResolutionKey | None = None) -> None:
		"""Configura la aplicación para dispositivos móviles.
		
		Args:
			resolution: Clave de resolución a usar. Si es None, usa DEFAULT_RESOLUTION.
		"""
		if resolution is None:
			resolution = cls.DEFAULT_RESOLUTION
			
		if resolution not in cls.MOBILE_RESOLUTIONS:
			raise ValueError(f"Resolución '{resolution}' no válida. Opciones: {list(cls.MOBILE_RESOLUTIONS.keys())}")
			
		width, height = cls.MOBILE_RESOLUTIONS[resolution]
		
		# Configuración específica para Android/móviles
		if platform == 'android':
			# En Android, la ventana se ajusta automáticamente
			pass
		else:
			# En desktop, simular una pantalla móvil vertical FIJA
			Config.set('graphics', 'width', str(width))
			Config.set('graphics', 'height', str(height))
			Config.set('graphics', 'resizable', False)  # Ventana NO redimensionable
			Config.set('graphics', 'borderless', False)  # Mantener borde para desarrollo
			Config.set('graphics', 'position', 'custom')  # Posición personalizada
			Config.set('graphics', 'left', '100')  # Posición desde la izquierda
			Config.set('graphics', 'top', '50')   # Posición desde arriba
			
		# Configurar entrada táctil para móviles
		Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
		
		# Forzar orientación vertical
		Config.set('graphics', 'orientation', 'portrait')
		
		print(f"[MOBILE CONFIG] Configurado para resolución '{resolution}': {width}x{height}")
	
	@classmethod
	def get_resolution_info(cls, resolution: ResolutionKey | None = None) -> dict[str, Any]:
		"""Obtiene información detallada sobre una resolución.
		
		Args:
			resolution: Clave de resolución. Si es None, usa DEFAULT_RESOLUTION.
			
		Returns:
			Diccionario con información de la resolución.
		"""
		if resolution is None:
			resolution = cls.DEFAULT_RESOLUTION
			
		if resolution not in cls.MOBILE_RESOLUTIONS:
			raise ValueError(f"Resolución '{resolution}' no válida. Opciones: {list(cls.MOBILE_RESOLUTIONS.keys())}")
			
		width, height = cls.MOBILE_RESOLUTIONS[resolution]
		
		# Información descriptiva de cada resolución
		descriptions = {
			'small': 'Móviles antiguos/básicos - ideal para UI minimalista',
			'medium': 'iPhone 8 Plus - balance entre espacio y compatibilidad',
			'large': 'iPhone 12 Pro Max - moderna con mucho espacio vertical',
			'extra': 'Resolución personalizada - máximo espacio para UI compleja'
		}
		
		return {
			'key': resolution,
			'width': width,
			'height': height,
			'aspect_ratio': round(width / height, 3),
			'description': descriptions[resolution],
			'is_default': resolution == cls.DEFAULT_RESOLUTION
		}
	
	@classmethod
	def list_available_resolutions(cls) -> dict[ResolutionKey, dict[str, Any]]:
		"""Lista todas las resoluciones disponibles con su información."""
		return {key: cls.get_resolution_info(key) for key in cls.MOBILE_RESOLUTIONS.keys()}
