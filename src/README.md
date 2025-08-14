# SiKIdle - Source Code

Código fuente principal del idle clicker SiKIdle.

## 📁 Estructura

### `core/` - Lógica Principal
- `game.py` - GameState principal con todos los sistemas integrados
- `achievements_idle.py` - Sistema de logros con recompensas de gemas
- `prestige_simple.py` - Sistema de prestigio con cristales
- `premium_shop.py` - Tienda premium y monetización
- `engagement_system.py` - Daily rewards, metas diarias, offline progress
- `gameplay_flow.py` - Flujo de gameplay tradicional con hints
- `combat_idle_integration.py` - Integración combat-idle balanceada
- `balance_manager.py` - Balanceo y detección de estancamiento

### `ui/` - Interfaz de Usuario
- `navigation/` - Sistema de navegación con desbloqueo progresivo
- `screens/` - Pantallas principales (home, achievements, prestige, shop, etc.)
- `widgets/` - Widgets reutilizables optimizados para móvil

### `utils/` - Utilidades
- `mobile_optimization.py` - Optimización UX móvil (touch, haptic, performance)
- `visual_feedback.py` - Efectos visuales y notación científica
- `performance.py` - Optimización de performance con batch processing
- `save.py` - Sistema de guardado SQLite
- `paths.py` - Gestión de rutas multiplataforma

### `assets/` - Recursos
- Imágenes, sonidos y fuentes del juego

## 🎮 Características Principales

- **Idle Clicker Tradicional**: Clic manual + edificios generadores
- **Progresión Guiada**: 7 fases desde tutorial hasta post-prestigio
- **Monetización Ética**: Pay-to-accelerate, 315 gemas gratuitas
- **Optimización Móvil**: Touch targets, haptic feedback, 60fps
- **Engagement Systems**: Daily rewards, metas diarias, progreso offline
- **Performance Optimizada**: Batch processing, update scheduling

## 🚀 Punto de Entrada

```bash
python src/main.py
```

El archivo `main.py` inicializa el juego con todos los sistemas integrados.