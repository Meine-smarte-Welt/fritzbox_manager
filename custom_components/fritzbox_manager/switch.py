# SHA256 (Inhalt ab Zeile 2, d.h. dieser Datei ohne diese erste Zeile): 50eba134abcfe42d07873b09bcea51f09ebd6aacea05fd549be5e06df256d93e
"""Schalter: WLAN-Netze (inkl. Gastnetz)."""

from __future__ import annotations

from typing import Any

from homeassistant.components.switch import SwitchEntity
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
    networks = ((manager.data or {}).get("wlan") or {}).get("networks", [])
    async_add_entities(FritzWlanSwitch(manager, net["key"]) for net in networks)


class FritzWlanSwitch(FritzEntity, SwitchEntity):
    """Schaltet ein WLAN-Netz der FRITZ!Box ein oder aus."""

    def __init__(self, manager, key: str) -> None:
        super().__init__(manager, "wlan")
        self._key = key
        self._attr_unique_id = f"{manager.config_entry.entry_id}_{key}"

    @property
    def _network(self) -> dict[str, Any]:
        return self.coordinator.network(self._key) or {}

    @property
    def translation_key(self) -> str:  # type: ignore[override]
        return "wlan_guest" if self._network.get("guest") else "wlan"

    @property
    def translation_placeholders(self) -> dict[str, str]:  # type: ignore[override]
        net = self._network
        return {"network": str(net.get("ssid") or net.get("key") or self._key)}

    @property
    def available(self) -> bool:
        return super().available and bool(self._network)

    @property
    def is_on(self) -> bool | None:
        net = self._network
        return net.get("enabled") if net else None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        net = self._network
        return {
            "ssid": net.get("ssid"),
            "guest": net.get("guest"),
            "band": net.get("band"),
            "channel": net.get("channel"),
            "clients": net.get("clients"),
        }

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self.coordinator.async_set_wlan(self._key, True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.coordinator.async_set_wlan(self._key, False)
