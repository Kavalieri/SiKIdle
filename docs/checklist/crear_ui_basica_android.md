# Checklist: Crear UI Básica Android para SiKIdle

**Fecha de inicio**: 03 de agosto de 2025  
**Objetivo**: Desarrollar la versión inicial completa de un idle clicker 2D para Android con UI optimizada, sistema de guardado SQLite y arquitectura modular.

## 📋 Tareas por Módulo

### 🗄️ 1. Sistema de Base de Datos (SQLite)
- [ ] Crear `src/utils/db.py` con conexión y gestión de base de datos
- [ ] Crear `src/utils/save.py` con sistema de guardado automático
- [ ] Implementar tabla `player` (monedas, clics, multiplicador, último guardado)
- [ ] Implementar tabla `upgrades` (mejoras disponibles y niveles)
- [ ] Implementar tabla `settings` (configuración del usuario)
- [ ] Implementar tabla `stats` (estadísticas de juego)

### 🎮 2. Lógica de Juego (Core)
- [ ] Crear `src/core/game.py` con clase `GameState`
- [ ] Implementar sistema de monedas y clics
- [ ] Implementar multiplicadores y bonificaciones
- [ ] Crear `src/core/upgrade.py` con sistema de mejoras
- [ ] Crear `src/core/config.py` para gestión de configuración
- [ ] Implementar guardado automático cada 30 segundos

### 🖥️ 3. Interfaz de Usuario (UI Screens)
- [ ] Crear `src/ui/loading_screen.py` - Pantalla de carga con logo
- [ ] Crear `src/ui/start_screen.py` - Menú principal con botones
- [ ] Crear `src/ui/main_screen.py` - Pantalla de juego principal
- [ ] Crear `src/ui/settings_screen.py` - Configuración del juego
- [ ] Crear `src/ui/stats_screen.py` - Estadísticas y progreso
- [ ] Crear `src/ui/upgrades_screen.py` - Pantalla de mejoras

### 📱 4. Optimización para Android
- [ ] Implementar navegación por gestos y botones grandes
- [ ] Añadir espacios reservados para banners publicitarios
- [ ] Crear botón simulado de anuncio con recompensa
- [ ] Implementar vibración en dispositivos Android
- [ ] Optimizar layouts para diferentes tamaños de pantalla

### 💰 5. Preparación para Monetización
- [ ] Reservar espacio para banner superior en `StartScreen`
- [ ] Reservar espacio para banner inferior en `MainScreen` 
- [ ] Implementar botón "Ver anuncio" simulado (placeholder para AdMob)
- [ ] Crear sistema de recompensas por anuncio (x2 monedas 30s)
- [ ] Documentar puntos de integración AdMob con `# TODO: AdMob integration here`

### 🔗 6. Integración y Navegación
- [ ] Crear `src/ui/screen_manager.py` para gestión de pantallas
- [ ] Implementar transiciones suaves entre pantallas
- [ ] Conectar todas las pantallas con la lógica de juego
- [ ] Actualizar `src/main.py` para usar el sistema completo

### ✅ 7. Validación y Testing
- [ ] Validar código con `ruff check src`
- [ ] Validar tipos con `mypy src`
- [ ] Probar en diferentes resoluciones móviles
- [ ] Verificar guardado y carga de datos
- [ ] Probar navegación entre pantallas

### 📚 8. Documentación
- [ ] Actualizar README.md con instrucciones completas
- [ ] Crear documentación de arquitectura en `docs/`
- [ ] Documentar sistema de guardado y base de datos
- [ ] Crear guía de desarrollo para pantallas UI

## 🎯 Resultado Esperado

Al completar todas las tareas:

1. **Pantalla de carga** con logo y progreso
2. **Menú principal** con botones grandes y espacio para banner
3. **Juego principal** con botón de clic, contador de monedas y área de anuncios
4. **Sistema de mejoras** funcional con persistencia
5. **Configuración** completa con idioma, sonido y vibración
6. **Estadísticas** detalladas del progreso del jugador
7. **Guardado automático** cada 30 segundos en SQLite
8. **Estructura preparada** para integración AdMob futura

## 📐 Arquitectura Objetivo

```
src/
├── core/
│   ├── game.py          # Estado del juego y lógica principal
│   ├── upgrade.py       # Sistema de mejoras
│   └── config.py        # Gestión de configuración
├── ui/
│   ├── screen_manager.py # Gestión de navegación
│   ├── loading_screen.py # Pantalla de carga
│   ├── start_screen.py   # Menú principal
│   ├── main_screen.py    # Juego principal
│   ├── upgrades_screen.py # Mejoras
│   ├── settings_screen.py # Configuración
│   └── stats_screen.py   # Estadísticas
├── utils/
│   ├── db.py            # Conexión base de datos
│   ├── save.py          # Sistema de guardado
│   └── paths.py         # Gestión de rutas
└── config/
    └── mobile_config.py  # Configuración móvil
```

---

**Estado**: 🚀 **LISTO PARA COMENZAR**  
**Prioridad**: Alta - Base fundamental del juego  
**Tiempo estimado**: 4-6 horas de desarrollo
