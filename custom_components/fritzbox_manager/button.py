# SHA256 (Inhalt ab Zeile 2, d.h. dieser Datei ohne diese erste Zeile): 3c91b7eff3334634a460fc6dff77f674fae40a439ce3c68e955269629ef4be51
"""Schaltflächen: Neustart und Neu verbinden."""

from __future__ import annotations

from homeassistant.components.button import ButtonDeviceClass, ButtonEntity
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import FritzConfigEntry
from .entity import FritzEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: FritzConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    manager = entry.runtime_data
    async_add_entities([FritzRebootButton(manager), FritzReconnectButton(manager)])


class FritzRebootButton(FritzEntity, ButtonEntity):
    """Startet die FRITZ!Box neu."""

    _attr_device_class = ButtonDeviceClass.RESTART
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(self, manager) -> None:
        super().__init__(manager, "reboot")

    async def async_press(self) -> None:
        await self.coordinator.async_reboot()


class FritzReconnectButton(FritzEntity, ButtonEntity):
    """Baut die Internetverbindung neu auf (neue IP-Adresse)."""

    _attr_entity_category = EntityCategory.CONFIG

    def __init__(self, manager) -> None:
        super().__init__(manager, "reconnect")

    async def async_press(self) -> None:
        await self.coordinator.async_reconnect()
