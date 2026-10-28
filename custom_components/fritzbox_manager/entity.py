# SHA256 (Inhalt ab Zeile 2, d.h. dieser Datei ohne diese erste Zeile): 994f5baf30679758019ca4f56cdd3d35a6e90e1f9504b49f8a6e94ab2337fdb0
"""Gemeinsame Basisklasse der Entitäten."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .manager import FritzManager


class FritzEntity(CoordinatorEntity[FritzManager]):
    """Entität eines FRITZ!Box-Managers (ein Gerät je Eintrag)."""

    _attr_has_entity_name = True

    def __init__(self, manager: FritzManager, key: str) -> None:
        super().__init__(manager)
        self._attr_unique_id = f"{manager.config_entry.entry_id}_{key}"
        self._attr_translation_key = key

    @property
    def device_info(self) -> DeviceInfo:
        return self.coordinator.device_info

    def _section(self, name: str) -> dict:
        """Abschnitt der letzten Abfrage (leer, wenn die Box ihn nicht liefert)."""
        return (self.coordinator.data or {}).get(name) or {}
