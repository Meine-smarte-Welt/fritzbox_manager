# SHA256 (Inhalt ab Zeile 2, d.h. dieser Datei ohne diese erste Zeile): d2155a2572ba72ade6b09ef9a7b1f84c2b1c66fc1edf66bb7bf946bfc2e84c7a
"""Binärsensoren: Internetverbindung, Leitung, Firmware-Update."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import FritzConfigEntry
from .entity import FritzEntity


@dataclass(frozen=True, kw_only=True)
class FritzBinaryDescription(BinarySensorEntityDescription):
    """Beschreibung eines Binärsensors."""

    section: str
    value_fn: Callable[[dict[str, Any]], bool | None]


BINARY_SENSORS: tuple[FritzBinaryDescription, ...] = (
    FritzBinaryDescription(
        key="internet_connected",
        section="wan",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
        value_fn=lambda wan: wan.get("connected") if wan.get("status") else None,
    ),
    FritzBinaryDescription(
        key="link_up",
        section="wan",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda wan: (wan.get("link_status") == "Up") if wan.get("link_status") else None,
    ),
    FritzBinaryDescription(
        key="firmware_update",
        section="update",
        device_class=BinarySensorDeviceClass.UPDATE,
        value_fn=lambda update: update.get("available") if update else None,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: FritzConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    async_add_entities(FritzBinarySensor(entry.runtime_data, d) for d in BINARY_SENSORS)


class FritzBinarySensor(FritzEntity, BinarySensorEntity):
    """Ein Binärsensor aus den Daten der FRITZ!Box."""

    entity_description: FritzBinaryDescription

    def __init__(self, manager, description: FritzBinaryDescription) -> None:
        super().__init__(manager, description.key)
        self.entity_description = description

    @property
    def is_on(self) -> bool | None:
        return self.entity_description.value_fn(self._section(self.entity_description.section))

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        if self.entity_description.key == "firmware_update":
            update = self._section("update")
            return {"new_version": update.get("new_version")} if update.get("new_version") else None
        return None
