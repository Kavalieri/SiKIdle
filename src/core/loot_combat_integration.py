"""
Integración entre Sistema de Combate y Sistema de Loot
"""

import logging
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from core.combat import CombatManager
    from core.loot import LootGenerator, LootItem
    from core.inventory import Inventory
    from core.biomes import BiomeManager

logger = logging.getLogger(__name__)


class LootCombatIntegration:
    """Maneja la integración entre sistemas de combate y loot"""

    def __init__(
        self,
        combat_manager: "CombatManager",
        loot_generator: "LootGenerator",
        inventory: "Inventory",
        biome_manager: Optional["BiomeManager"] = None,
    ):
        self.combat_manager = combat_manager
        self.loot_generator = loot_generator
        self.inventory = inventory
        self.biome_manager = biome_manager

        self.auto_loot_enabled = True
        self.loot_notifications_enabled = True

        self.on_loot_obtained_callback = None
        self.on_rare_loot_obtained_callback = None

        self.combat_manager.set_enemy_defeat_callback(self._on_enemy_defeated)
        logger.info("Integración combate-loot inicializada")

    def _on_enemy_defeated(self, enemy_type: str, enemy_level: int, is_boss: bool) -> None:
        """Callback ejecutado cuando un enemigo es derrotado"""
        try:
            player_level = self.combat_manager.player.get_level()
            biome_bonus = 1.2 if self.biome_manager else 1.0

            dropped_items = self.loot_generator.drop_loot_from_enemy(
                enemy_type=enemy_type,
                enemy_level=enemy_level,
                player_level=player_level,
                is_boss=is_boss,
                biome_bonus=biome_bonus,
            )

            if dropped_items:
                self._process_dropped_items(dropped_items, enemy_type, is_boss)

        except Exception as e:
            logger.error("Error procesando loot de enemigo %s: %s", enemy_type, e)

    def _process_dropped_items(
        self, items: list["LootItem"], enemy_type: str, is_boss: bool
    ) -> None:
        """Procesa los ítems dropeados por un enemigo"""
        for item in items:
            if self.auto_loot_enabled:
                success = self.inventory.add_item(item)
                if success:
                    logger.info("Loot auto-recogido: %s", item.get_display_name())
                    if self.loot_notifications_enabled:
                        self._notify_loot_obtained(item, enemy_type, is_boss)

    def _notify_loot_obtained(
        self, item: "LootItem", enemy_type: str, is_boss: bool
    ) -> None:
        """Notifica que se ha obtenido loot"""
        if self.on_loot_obtained_callback:
            try:
                self.on_loot_obtained_callback(item, enemy_type, is_boss)
            except Exception as e:
                logger.error("Error en callback de loot obtenido: %s", e)

        if item.rarity.value in ["rare", "epic", "legendary"]:
            if self.on_rare_loot_obtained_callback:
                try:
                    self.on_rare_loot_obtained_callback(item, enemy_type, is_boss)
                except Exception as e:
                    logger.error("Error en callback de loot raro: %s", e)

        boss_text = " (BOSS)" if is_boss else ""
        logger.info(
            "¡Loot obtenido de %s%s: %s!",
            enemy_type,
            boss_text,
            item.get_display_name(),
        )

    def set_auto_loot(self, enabled: bool) -> None:
        """Configura el auto-loot"""
        self.auto_loot_enabled = enabled
        status = "activado" if enabled else "desactivado"
        logger.info("Auto-loot %s", status)

    def set_loot_notifications(self, enabled: bool) -> None:
        """Configura las notificaciones de loot"""
        self.loot_notifications_enabled = enabled
        status = "activadas" if enabled else "desactivadas"
        logger.info("Notificaciones de loot %s", status)

    def set_loot_obtained_callback(self, callback) -> None:
        """Establece callback para cuando se obtiene loot"""
        self.on_loot_obtained_callback = callback

    def set_rare_loot_obtained_callback(self, callback) -> None:
        """Establece callback especial para loot raro"""
        self.on_rare_loot_obtained_callback = callback

    def get_loot_stats(self) -> dict:
        """Obtiene estadísticas de loot"""
        return {
            "auto_loot_enabled": self.auto_loot_enabled,
            "notifications_enabled": self.loot_notifications_enabled,
            "biome_bonus_active": self.biome_manager is not None,
        }
