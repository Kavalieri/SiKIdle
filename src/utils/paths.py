"""Sistema centralizado para gestionar rutas del sistema."""

import os
import sys
from pathlib import Path


def get_user_data_dir():
	"""Obtiene el directorio de datos del usuario."""
	if sys.platform == "win32":
		return Path(os.environ.get("APPDATA", "")) / "SiKIdle"
	elif sys.platform == "darwin":
		return Path.home() / "Library" / "Application Support" / "SiKIdle"
	else:
		return Path.home() / ".local" / "share" / "SiKIdle"


def ensure_directories():
	"""Crea todos los directorios necesarios si no existen."""
	base_dir = get_user_data_dir()
	directories = [
		base_dir,
		base_dir / "config",
		base_dir / "savegames",
		base_dir / "data",
		base_dir / "logs",
		base_dir / "cache"
	]

	for directory in directories:
		directory.mkdir(parents=True, exist_ok=True)


def get_assets_path():
	"""Obtiene el directorio de assets del juego."""
	# Obtener directorio del script actual
	current_dir = Path(__file__).parent.parent
	return current_dir / "assets"
