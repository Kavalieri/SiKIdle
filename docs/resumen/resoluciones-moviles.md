# Resoluciones Móviles para SiKIdle

## Descripción

SiKIdle ahora incluye un sistema de configuración de resoluciones móviles que permite:

1. **Desarrollo optimizado**: Simular diferentes tamaños de pantalla móvil en desktop
2. **Configuración flexible**: Cambiar fácilmente entre resoluciones sin modificar código
3. **Gestión centralizada**: Toda la configuración móvil en una sola clase

## Resoluciones Disponibles

| Clave | Resolución | Descripción | Uso Recomendado |
|-------|------------|-------------|------------------|
| `small` | 360x640 | Móviles antiguos/básicos | Pruebas de UI minimalista |
| `medium` | 414x736 | iPhone 8 Plus | Balance desarrollo/compatibilidad |
| `large` | 428x926 | iPhone 12 Pro Max | **Por defecto** - Moderna con espacio |
| `extra` | 480x854 | Personalizada | UI compleja con muchos elementos |

## Características

### ✅ Configuración por Defecto: `large` (428x926)
- Resolución moderna que ofrece mucho espacio vertical
- Ideal para idle clickers con múltiples elementos de UI
- Compatible con móviles actuales

### ✅ Ventana Fija para Desarrollo
- No redimensionable en desktop para consistencia
- Posición fija para evitar saltos entre pruebas
- Simula perfectamente la experiencia móvil

### ✅ Script de Cambio Rápido
```bash
# Ver configuración actual
python dev-tools/scripts/change_resolution.py

# Cambiar resolución
python dev-tools/scripts/change_resolution.py medium
python dev-tools/scripts/change_resolution.py large
python dev-tools/scripts/change_resolution.py extra
```

## Uso para Desarrollo

### 1. Cambiar Resolución
```bash
cd dev-tools/scripts
python change_resolution.py large
```

### 2. Ejecutar el Juego
```bash
cd ../../
python src/main.py
```

### 3. Desarrollar UI
- La ventana será FIJA en la resolución seleccionada
- Todos los elementos se dimensionan automáticamente
- Perfect simulation de experiencia móvil

## Ventajas para Idle Clickers

### 📱 Resolución `large` (428x926) - **Recomendada**
- **Más espacio vertical**: Ideal para múltiples botones de mejoras
- **UI compleja**: Permite paneles de estadísticas detalladas
- **Experiencia moderna**: Se siente como app móvil actual

### 📱 Resolución `medium` (414x736)
- **Compatibilidad**: Funciona bien en móviles medios
- **Balance**: Buen espacio sin ser abrumador

### 📱 Resolución `small` (360x640)
- **Minimalismo**: Fuerza a diseño simple y claro
- **Compatibilidad antigua**: Para móviles básicos

## Implementación Técnica

### Configuración Modular
```python
# src/config/mobile_config.py
class MobileConfig:
	DEFAULT_RESOLUTION: ResolutionKey = 'large'
	
	@classmethod
	def configure_for_mobile(cls, resolution=None):
		# Configuración automática antes de Kivy
```

### Integración Automática
```python
# src/main.py
from config.mobile_config import MobileConfig

# Se configura ANTES de importar Kivy
MobileConfig.configure_for_mobile()
```

## Próximos Pasos

Con la base de resoluciones establecida, el proyecto está listo para:

1. **UI de gameplay**: Botones de click, contadores, mejoras
2. **Sistema de progresión**: Niveles, multiplicadores, prestigio
3. **Persistencia**: Guardar progreso entre sesiones
4. **Optimizaciones móviles**: Animaciones fluidas, feedback táctil

## Recomendación

**Usar resolución `large` (428x926)** para el desarrollo principal:
- Da suficiente espacio para UI compleja de idle clicker
- Representa bien los móviles modernos
- Permite crear una experiencia rica sin saturar
