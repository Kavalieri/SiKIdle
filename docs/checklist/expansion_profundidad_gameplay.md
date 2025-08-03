# Checklist: Expansión de Profundidad y Gameplay - SiKIdle

**Fecha de inicio**: 03 de enero de 2025  
**Objetivo**: Transformar SiKIdle de un clicker básico en un idle game complejo con múltiples sistemas de progresión, inspirado en los mejores del género.

## 🎯 Visión General del Diseño

### Inspiración de Juegos Exitosos:
- **Cookie Clicker**: Sistema de edificios y logros
- **Clicker Heroes**: Héroes, niveles y prestigio
- **Adventure Capitalist**: Múltiples negocios y gestores
- **Realm Grinder**: Ramas de facción y especialización
- **Tap Titans**: Armas, artefactos y progresión infinita

### Sistemas Principales a Implementar:
1. **Menú lateral deslizable** con múltiples categorías
2. **Sistema de prestigio** y renacimiento
3. **Loot aleatorio** con rareza
4. **Árbol de talentos** especializable
5. **Múltiples monedas** y recursos
6. **Eventos temporales** y desafíos

---

## 📋 Tareas por Sistema

### 🎮 1. Interfaz Principal Mejorada
- [ ] **Botón de salida** en StartScreen con confirmación
- [ ] **Menú lateral deslizable** que se abre desde cualquier pantalla
- [ ] **Animaciones suaves** para apertura/cierre del menú lateral
- [ ] **Header dinámico** que muestre múltiples recursos
- [ ] **Notificaciones emergentes** para logros y loot
- [ ] **Efecto de partículas** en clics importantes

### 🏗️ 2. Sistema de Edificios/Generadores
- [ ] Crear `src/core/buildings.py` con generadores automáticos
- [ ] **Granjas** (1 moneda/seg) → **Fábricas** (50 monedas/seg) → **Bancos** (1000 monedas/seg)
- [ ] **Laboratorios** (investigación) → **Portales** (dimensiones)
- [ ] **Gestores automáticos** para cada edificio (compra automática)
- [ ] **Sinergias entre edificios** (bonificaciones cruzadas)
- [ ] **Evoluciones de edificios** a versiones superiores

### 💎 3. Sistema de Loot Aleatorio
- [ ] Crear `src/core/loot.py` con sistema de drops
- [ ] **Rarezas**: Común (70%) → Raro (20%) → Épico (8%) → Legendario (2%)
- [ ] **Tipos de loot**: Armas, Artefactos, Gemas, Materiales
- [ ] **Efectos de armas**: +% monedas por clic, +% velocidad crítico
- [ ] **Artefactos pasivos**: +% ingresos globales, +% experiencia
- [ ] **Sistema de combinación** de materiales
- [ ] **Inventario visual** con filtros por rareza

### 🌟 4. Árbol de Talentos
- [ ] Crear `src/core/talents.py` con sistema de especialización
- [ ] **Rama Económica**: Eficiencia, ingresos pasivos, multiplicadores
- [ ] **Rama Combate**: Daño crítico, velocidad de clic, armas especiales
- [ ] **Rama Mística**: Magia, hechizos temporales, invocaciones
- [ ] **Rama Exploración**: Descubrimiento, loot raro, aventuras
- [ ] **Puntos de talento** ganados por niveles y logros
- [ ] **Respecs gratuitos** cada prestige

### 🔄 5. Sistema de Prestigio/Renacimiento
- [ ] Crear `src/core/prestige.py` con mecánica de reinicio
- [ ] **Moneda de prestigio**: Cristales de poder obtenidos al reiniciar
- [ ] **Bonificaciones permanentes**: Multiplicadores de base
- [ ] **Desbloqueo de contenido**: Nuevos edificios, talentos, zonas
- [ ] **Múltiples tipos de prestigio**: Suave (cada nivel 100), Duro (cada dimensión)
- [ ] **Cálculo automático** del beneficio del prestigio

### 💰 6. Múltiples Monedas y Recursos
- [ ] Expandir `src/core/game.py` para múltiples recursos
- [ ] **Monedas**: Oro (básico) → Platino (prestigio) → Diamantes (premium)
- [ ] **Recursos especiales**: Energía (habilidades), Experiencia (niveles)
- [ ] **Materiales de crafteo**: Hierro, Madera, Piedra, Cristales
- [ ] **Conversión entre recursos** con ratios dinámicos
- [ ] **Mercado interno** para intercambio

### 🏆 7. Sistema de Logros y Desafíos
- [ ] Crear `src/core/achievements.py` con logros complejos
- [ ] **Logros de progresión**: "Primer millón", "100 edificios"
- [ ] **Logros de tiempo**: "1 hora jugando", "Login diario 7 días"
- [ ] **Logros ocultos**: Descubrimientos especiales
- [ ] **Desafíos temporales**: Eventos con recompensas únicas
- [ ] **Rankings globales** (simulados localmente)

### ⚔️ 8. Sistema de Combate/Aventuras
- [ ] Crear `src/core/combat.py` con sistema de batalla
- [ ] **Zonas de aventura**: Bosques → Cuevas → Montañas → Dimensiones
- [ ] **Enemigos automáticos**: HP escalable, recompensas proporcionales
- [ ] **Habilidades especiales**: Bola de fuego, Lluvia de monedas, Escudo
- [ ] **Jefes semanales**: Encuentros únicos con loot especial
- [ ] **Progresión automática** cuando se está offline

### 🎨 9. Menú Lateral Categorizado
- [ ] Crear `src/ui/side_menu.py` con navegación expandida
- [ ] **Categoría Edificios**: Lista de todos los generadores
- [ ] **Categoría Mejoras**: Upgrades tradicionales organizadas
- [ ] **Categoría Talentos**: Árbol de especialización
- [ ] **Categoría Inventario**: Loot, armas, artefactos
- [ ] **Categoría Logros**: Progreso y desafíos
- [ ] **Categoría Aventura**: Combate y exploración
- [ ] **Categoría Prestigio**: Información y opciones de renacimiento

### 🌐 10. Eventos y Contenido Temporal
- [ ] Crear `src/core/events.py` con sistema de eventos
- [ ] **Eventos estacionales**: Navidad, Halloween, Verano
- [ ] **Multiplicadores temporales**: "Hora feliz de oro"
- [ ] **Misiones especiales**: Objetivos únicos con deadlines
- [ ] **Coleccionables limitados**: Skins, títulos, decoraciones
- [ ] **Calendario de recompensas**: Login diario mejorado

---

## 🎮 Mecánicas de Profundidad

### 📈 Progresión Exponencial
- **Niveles de jugador**: Experiencia ganada por todas las actividades
- **Multiplicadores escalonados**: x2 cada 25 niveles
- **Soft caps inteligentes**: Progresión que se ralentiza pero no se detiene
- **Meta-progresión**: Cada prestigio desbloquea nuevas posibilidades

### 🔀 Sinergias Complejas
- **Edificios que se potencian mutuamente**
- **Talentos que modifican el comportamiento de edificios**
- **Artefactos que crean nuevas mecánicas**
- **Combinaciones de habilidades** que generan efectos únicos

### 🎲 Elementos de Aleatoriedad Controlada
- **Críticos en clics** con animaciones especiales
- **Eventos aleatorios** durante el juego (encuentro de tesoro, mercader)
- **Loot con stats aleatorios** pero rangos predecibles
- **Mutaciones de edificios** que cambian sus efectos

---

## 📱 Adaptaciones para Android

### 🎮 Controles Táctiles Mejorados
- [ ] **Gestos de deslizamiento** para abrir menús
- [ ] **Toque y mantener** para información detallada
- [ ] **Pellizco para zoom** en árboles de talentos
- [ ] **Doble toque** para acciones rápidas
- [ ] **Vibración háptica** en acciones importantes

### 📊 UI Responsive Avanzada
- [ ] **Paneles redimensionables** según orientación
- [ ] **Modo compacto** para pantallas pequeñas
- [ ] **Notificaciones push** para eventos offline
- [ ] **Widget de progreso** para la pantalla de inicio

---

## 🗄️ Expansión de Base de Datos

### Nuevas Tablas Requeridas:
- [ ] **`buildings`**: Nivel, cantidad, ingresos, gestores
- [ ] **`talents`**: Rama, nivel, puntos invertidos
- [ ] **`inventory`**: Ítem, rareza, stats, cantidad
- [ ] **`achievements`**: ID, completado, fecha, progreso
- [ ] **`prestige_data`**: Cristales, bonificaciones, historia
- [ ] **`events`**: Activos, progreso, recompensas reclamadas
- [ ] **`combat_progress`**: Zona actual, estadísticas de batalla

---

## 🎯 Orden de Implementación Sugerido

### 🥇 Prioridad 1 (Base Expandida):
1. Botón de salida en StartScreen
2. Menú lateral básico con categorías
3. Sistema de múltiples monedas
4. Edificios básicos (primeros 3-4 tipos)

### 🥈 Prioridad 2 (Profundidad):
5. Sistema de loot aleatorio
6. Árbol de talentos (rama básica)
7. Logros fundamentales
8. Primera iteración de prestigio

### 🥉 Prioridad 3 (Complejidad):
9. Sistema de combate
10. Eventos temporales
11. Sinergias avanzadas
12. Elementos visuales premium

---

## 📊 Métricas de Éxito

Al completar esta expansión, SiKIdle tendrá:

- **8+ horas de gameplay** sin repetición
- **50+ logros** únicos y desafiantes
- **15+ tipos de edificios** con sinergias
- **100+ ítems** de loot con rareza
- **3 ramas de talentos** completamente funcionales
- **Sistema de prestigio** que triplique la rejugabilidad
- **Contenido procedural** para longevidad infinita

---

**Estado**: 🚀 **LISTO PARA EXPANSIÓN**  
**Prioridad**: Alta - Evolución a juego completo  
**Tiempo estimado**: 15-20 horas de desarrollo intensivo
