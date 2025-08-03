"""Script de desarrollo para cambiar resoluciones móviles.

Permite cambiar fácilmente entre diferentes resoluciones móviles
para probar la UI del juego en distintos tamaños de pantalla.
"""

import sys
from pathlib import Path

# Agregar src al path para importar los módulos
src_path = Path(__file__).parent.parent.parent / 'src'
sys.path.insert(0, str(src_path))

from config.mobile_config import MobileConfig


def show_current_resolution():
	"""Muestra la resolución actual configurada."""
	current = MobileConfig.get_resolution_info()
	print(f"\n📱 Resolución actual: {current['key']}")
	print(f"   Tamaño: {current['width']}x{current['height']}")
	print(f"   Descripción: {current['description']}")
	print(f"   Es por defecto: {'Sí' if current['is_default'] else 'No'}")


def show_available_resolutions():
	"""Muestra todas las resoluciones disponibles."""
	resolutions = MobileConfig.list_available_resolutions()
	
	print("\n📋 Resoluciones disponibles:")
	print("=" * 50)
	
	for key, info in resolutions.items():
		marker = "👑" if info['is_default'] else "  "
		print(f"{marker} {key}: {info['width']}x{info['height']}")
		print(f"      {info['description']}")
		print(f"      Aspecto: {info['aspect_ratio']}")
		print()


def change_resolution(new_resolution: str):
	"""Cambia la resolución por defecto.
	
	Args:
		new_resolution: Nueva resolución a configurar
	"""
	try:
		# Verificar que la resolución es válida
		info = MobileConfig.get_resolution_info(new_resolution)  # type: ignore
		
		# Modificar el archivo de configuración
		config_file = src_path / 'config' / 'mobile_config.py'
		
		with open(config_file, 'r', encoding='utf-8') as f:
			content = f.read()
		
		# Reemplazar la línea DEFAULT_RESOLUTION
		old_line = f"DEFAULT_RESOLUTION: ResolutionKey = '{MobileConfig.DEFAULT_RESOLUTION}'"
		new_line = f"DEFAULT_RESOLUTION: ResolutionKey = '{new_resolution}'"
		
		content = content.replace(old_line, new_line)
		
		with open(config_file, 'w', encoding='utf-8') as f:
			f.write(content)
		
		print(f"\n✅ Resolución cambiada a '{new_resolution}'")
		print(f"   Nuevo tamaño: {info['width']}x{info['height']}")
		print(f"   {info['description']}")
		print("\n🔄 Reinicia el juego para ver los cambios.")
		
	except ValueError as e:
		print(f"\n❌ Error: {e}")
	except Exception as e:
		print(f"\n❌ Error inesperado: {e}")


def main():
	"""Función principal del script."""
	print("🎮 SiKIdle - Configurador de Resolución Móvil")
	print("=" * 45)
	
	if len(sys.argv) == 1:
		# Sin argumentos: mostrar información
		show_current_resolution()
		show_available_resolutions()
		print("💡 Uso: python change_resolution.py <resolución>")
		print("   Ejemplo: python change_resolution.py medium")
		
	elif len(sys.argv) == 2:
		# Un argumento: cambiar resolución
		new_resolution = sys.argv[1].lower()
		
		if new_resolution in ['list', 'ls', 'show']:
			show_available_resolutions()
		elif new_resolution in ['current', 'now', 'actual']:
			show_current_resolution()
		else:
			change_resolution(new_resolution)
	else:
		print("❌ Demasiados argumentos.")
		print("💡 Uso: python change_resolution.py <resolución>")


if __name__ == '__main__':
	main()
