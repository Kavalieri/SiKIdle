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

### Arquitectura de Interfaz Rediseñada:
1. **Pantalla Principal**: Área de clic + indicadores básicos + navegación directa
2. **Sistema de Pestañas Centralizadas**: Un menú principal organizado por categorías
3. **Menú Lateral Reservado**: Solo para eventos temporales y notificaciones futuras
4. **Sin Banners Intrusivos**: Interfaz limpia y centrada en gameplay

### Sistemas Principales a Implementar:
1. **Sistema de pestañas principal** con categorías organizadas
2. **Sistema de prestigio** y renacimiento
3. **Loot aleatorio** con rareza
4. **Árbol de talentos** especializable
5. **Múltiples monedas** y recursos
6. **Eventos temporales** (futuro)

---

## 📋 Tareas por Sistema

### 🎮 1. Sistema de Navegación Centralizada ✅ COMPLETADO
- [x] **Pantalla principal** limpia con área de clic optimizada
- [x] **Indicadores de recursos** en header sin saturar
- [x] **Navegación directa** desde pantalla principal simplificada
- [x] **Interfaz unificada** para mejoras y edificios en una sola pantalla
- [x] **Eliminación del menú lateral** - arquitectura simplificada
- [x] **Unificación de edificios y mejoras** en gestión principal
- [x] **Botón único de gestión** reemplazando botones separados
- [ ] **Transiciones suaves** entre pestañas con animaciones (futuro)

### 🏗️ 2. Sistema de Edificios/Generadores ✅ COMPLETADO
- [x] Crear `src/core/buildings.py` con generadores automáticos
- [x] **Granjas** (1 moneda/seg) → **Fábricas** (50 monedas/seg) → **Bancos** (1000 monedas/seg)
- [x] **Laboratorios** (investigación) → **Portales** (dimensiones)
- [x] **Pantalla de gestión de edificios** con compra manual
- [x] **Costos escalables** con fórmula base_cost * 1.15^cantidad
- [x] **Producción automática** integrada con sistema de recursos
- [x] **Guardado/carga** de estado de edificios
- [ ] **Gestores automáticos** para cada edificio (compra automática)
- [ ] **Sinergias entre edificios** (bonificaciones cruzadas)
- [ ] **Evoluciones de edificios** a versiones superiores

### 💎 3. Sistema de Mejoras Unificado ✅ COMPLETADO
- [x] Crear `src/core/upgrades.py` con mejoras permanentes
- [x] **Categorías de mejoras**:
  - [x] 💰 **Económicas**: +% ingresos por clic, +% ingresos edificios, +% ingresos globales
  - [x] ⚡ **Eficiencia**: -% costos edificios, +% velocidad producción
  - [x] 🎯 **Críticos**: +% probabilidad crítico, +% multiplicador crítico
  - [x] 📈 **Multiplicadores**: Bonificaciones exponenciales (ingresos y costos)
- [x] **Sistema de prerequisitos** para mejoras avanzadas
- [x] **Pantalla de mejoras** con pestañas por categoría
- [x] **Efectos permanentes** guardados e integrados con GameState
- [x] **9 tipos de mejoras** implementados y funcionales
- [x] **Integración con edificios** - gestión unificada en pantalla de mejoras

### 🌟 4. Árbol de Talentos ⏳ FUTURO
- [ ] Crear `src/core/talents.py` con sistema de especialización
- [ ] **Rama Económica**: Eficiencia, ingresos pasivos, multiplicadores
- [ ] **Rama Combate**: Daño crítico, velocidad de clic, armas especiales  
- [ ] **Rama Mística**: Magia, hechizos temporales, invocaciones
- [ ] **Rama Exploración**: Descubrimiento, loot raro, aventuras
- [ ] **Puntos de talento** ganados por niveles y logros
- [ ] **Respecs gratuitos** cada prestige

### 🔄 5. Sistema de Prestigio/Renacimiento ⏳ FUTURO
- [ ] Crear `src/core/prestige.py` con mecánica de reinicio
- [ ] **Moneda de prestigio**: Cristales de poder obtenidos al reiniciar
- [ ] **Bonificaciones permanentes**: Multiplicadores de base
- [ ] **Desbloqueo de contenido**: Nuevos edificios, talentos, zonas
- [ ] **Múltiples tipos de prestigio**: Suave (cada nivel 100), Duro (cada dimensión)
- [ ] **Cálculo automático** del beneficio del prestigio

### 💰 6. Múltiples Monedas y Recursos
- [x] Expandir `src/core/game.py` para múltiples recursos
- [x] **Monedas**: Oro (básico) → Platino (prestigio) → Diamantes (premium)
- [x] **Recursos especiales**: Energía (habilidades), Experiencia (niveles)
- [x] **Materiales de crafteo**: Hierro, Madera, Piedra, Cristales
- [ ] **Conversión entre recursos** con ratios dinámicos
- [ ] **Mercado interno** para intercambio

### 🏆 6. Sistema de Logros y Desafíos ⏳ FUTURO
- [ ] Crear `src/core/achievements.py` con logros complejos
- [ ] **Logros de progresión**: "Primer millón", "100 edificios"
- [ ] **Logros de tiempo**: "1 hora jugando", "Login diario 7 días"
- [ ] **Logros ocultos**: Descubrimientos especiales
- [ ] **Desafíos temporales**: Eventos con recompensas únicas
- [ ] **Rankings globales** (simulados localmente)

### 🎲 7. Sistema de Loot Aleatorio ⏳ FUTURO LEJANO
- [ ] Crear `src/core/loot.py` con sistema de drops
- [ ] **Rarezas**: Común (70%) → Raro (20%) → Épico (8%) → Legendario (2%)
- [ ] **Tipos de loot**: Armas, Artefactos, Gemas, Materiales
- [ ] **Efectos de armas**: +% monedas por clic, +% velocidad crítico
- [ ] **Artefactos pasivos**: +% ingresos globales, +% experiencia
- [ ] **Sistema de combinación** de materiales
- [ ] **Inventario visual** con filtros por rareza

### 🌐 8. Sistema de Eventos (Menú Lateral) ⏳ FUTURO LEJANO
- [ ] **Refactorizar menú lateral** para eventos únicamente
- [ ] **Eventos estacionales**: Navidad, Halloween, Verano
- [ ] **Multiplicadores temporales**: "Hora feliz de oro"
- [ ] **Misiones especiales**: Objetivos únicos con deadlines
- [ ] **Notificaciones push** para eventos importantes
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

## 🎯 Orden de Implementación Rediseñado

### 🥇 Prioridad 1 (Fundamentos Sólidos):
1. ✅ Sistema de edificios completo
2. ✅ Múltiples recursos funcionales
3. ✅ **Sistema de mejoras unificado** (económicas, eficiencia, críticos, multiplicadores)
4. ✅ **Interfaz unificada** para mejoras y edificios en una sola pantalla
5. ✅ **Eliminación del menú lateral** y simplificación de navegación

### 🥈 Prioridad 2 (Profundidad de Gameplay): ⏳ SIGUIENTE FASE
6. Sistema de logros fundamentales
7. Primera iteración de prestigio
8. Árbol de talentos (rama económica)
9. Sistema de pestañas principales avanzado

### 🥉 Prioridad 3 (Contenido Avanzado):
9. Sistema de loot aleatorio
10. Eventos temporales
11. Sinergias avanzadas entre sistemas
12. Elementos visuales premium

---

## �️ Arquitectura de Interfaz Objetivo

### Pantalla Principal:
```
[💰 1,234 coins] [⚡ 56 energy] [🔧 12 iron] [📊 Stats] [⚙️ Settings]
                                                                    
                    [GRAN ÁREA DE CLIC]                           
                   🎯 +1.5x multiplicador                         
                                                                    
[🏗️ Edificios] [⚡ Mejoras] [🌟 Talentos] [🎒 Inventario] [🏆 Logros] [🔄 Prestigio]
```

### Sistema de Pestañas:
- **Navegación horizontal** tipo tabs en la parte inferior
- **Contenido dinámico** en el área central
- **Contexto preservado** al cambiar pestañas
- **Indicadores de novedad** en pestañas con contenido nuevo

### Menú Lateral (Futuro):
- **Solo eventos temporales**
- **Notificaciones importantes**
- **Acceso rápido a ofertas especiales**
- **Calendario de recompensas**

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
