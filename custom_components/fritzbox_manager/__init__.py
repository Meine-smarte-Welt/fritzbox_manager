# SHA256 (Inhalt ab Zeile 2, d.h. dieser Datei ohne diese erste Zeile): fc658021c453b9dee889c91cb3cfec02a848a76ba3cbad0158963a23f7864833
"""Die Integration FRITZ!Box Manager."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import voluptuous as vol

from homeassistant.components.http import StaticPathConfig
from homeassistant.components.lovelace.const import LOVELACE_DATA
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.service import async_register_admin_service
from homeassistant.helpers.typing import ConfigType
from homeassistant.loader import async_get_integration

from . import websocket_api
from .const import (
    ATTR_ENABLED,
    ATTR_ENTRY_ID,
    ATTR_WLAN,
    CARD_STATIC_URL,
    CARD_URL_BASE,
    DOMAIN,
    PLATFORMS,
    SERVICE_CHECK_UPDATE,
    SERVICE_REBOOT,
    SERVICE_RECONNECT,
    SERVICE_SET_WLAN,
)
from .manager import FritzManager

_LOGGER = logging.getLogger(__name__)

type FritzConfigEntry = ConfigEntry[FritzManager]

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)

_CARD_DIR = Path(__file__).parent / "www"
_FRONTEND_REGISTERED_KEY = f"{DOMAIN}_frontend_registered"

_ENTRY_SCHEMA = {vol.Optional(ATTR_ENTRY_ID): cv.string}


def get_manager(hass: HomeAssistant, entry_id: str | None = None) -> FritzManager | None:
    """Manager eines geladenen Eintrags; ohne ``entry_id`` der einzige/erste."""
    entries = [
        entry
        for entry in hass.config_entries.async_entries(DOMAIN)
        if getattr(entry, "runtime_data", None) is not None
    ]
    if entry_id:
        entries = [entry for entry in entries if entry.entry_id == entry_id]
    return entries[0].runtime_data if entries else None


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Dienste und WebSocket-Befehle einmalig registrieren."""
    websocket_api.async_register(hass)

    def _manager(call: ServiceCall) -> FritzManager:
        manager = get_manager(hass, call.data.get(ATTR_ENTRY_ID))
        if manager is None:
            raise ServiceValidationError("Keine geladene FRITZ!Box gefunden.")
        return manager

    async def _reboot(call: ServiceCall) -> None:
        await _manager(call).async_reboot()

    async def _reconnect(call: ServiceCall) -> None:
        await _manager(call).async_reconnect()

    async def _set_wlan(call: ServiceCall) -> None:
        manager = _manager(call)
        key = call.data[ATTR_WLAN]
        if manager.network(key) is None:
            raise ServiceValidationError("Unbekanntes WLAN-Netz.")
        await manager.async_set_wlan(key, call.data[ATTR_ENABLED])

    async def _check_update(call: ServiceCall) -> None:
        await _manager(call).async_check_update()

    async_register_admin_service(
        hass, DOMAIN, SERVICE_REBOOT, _reboot, vol.Schema(_ENTRY_SCHEMA)
    )
    async_register_admin_service(
        hass, DOMAIN, SERVICE_RECONNECT, _reconnect, vol.Schema(_ENTRY_SCHEMA)
    )
    async_register_admin_service(
        hass,
        DOMAIN,
        SERVICE_SET_WLAN,
        _set_wlan,
        vol.Schema(
            {
                **_ENTRY_SCHEMA,
                vol.Required(ATTR_WLAN): vol.Match(r"^wlan[1-9]$"),
                vol.Required(ATTR_ENABLED): cv.boolean,
            }
        ),
    )
    async_register_admin_service(
        hass, DOMAIN, SERVICE_CHECK_UPDATE, _check_update, vol.Schema(_ENTRY_SCHEMA)
    )
    return True


async def async_setup_entry(hass: HomeAssistant, entry: FritzConfigEntry) -> bool:
    """Eintrag einrichten."""
    manager = FritzManager(hass, entry)
    await manager.async_config_entry_first_refresh()
    entry.runtime_data = manager

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_async_options_updated))
    await _async_register_frontend_card(hass)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: FritzConfigEntry) -> bool:
    """Eintrag entladen."""
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unloaded:
        entry.runtime_data.client.close()
    return unloaded


async def _async_options_updated(hass: HomeAssistant, entry: FritzConfigEntry) -> None:
    """Optionen übernehmen, ohne neu zu laden (nur das Intervall ändert sich live)."""
    entry.runtime_data.apply_options()


# --- Mitgelieferte Karte (fritzbox-manager-card.js) -------------------------------
#
# Wird direkt aus dem Ordner "www" ausgeliefert und über genau EINEN Weg im
# Frontend angemeldet: einen gespeicherten Lovelace-Ressourceneintrag. (Das
# zusätzliche Einbetten per add_extra_js_url hat sich bei den Schwester-
# Integrationen als schädlich erwiesen und wird deshalb nicht verwendet.)
async def _async_register_frontend_card(hass: HomeAssistant) -> None:
    """Karte ausliefern und als Lovelace-Ressource eintragen (höchstens einmal)."""
    if hass.data.get(_FRONTEND_REGISTERED_KEY):
        return
    try:
        await hass.http.async_register_static_paths(
            [StaticPathConfig(CARD_URL_BASE, str(_CARD_DIR), False)]
        )
    except RuntimeError:
        _LOGGER.debug("Statischer Pfad %s ist bereits registriert", CARD_URL_BASE)
    except Exception as ex:  # noqa: BLE001 - darf das Setup nicht blockieren
        _LOGGER.warning(
            "Konnte den statischen Pfad für die Dashboard-Karte (%s) nicht registrieren (%s)."
            " Beim nächsten Start wird es erneut versucht.",
            CARD_URL_BASE,
            ex,
        )
        return
    await _async_ensure_lovelace_resource(hass)
    hass.data[_FRONTEND_REGISTERED_KEY] = True


async def _async_ensure_lovelace_resource(hass: HomeAssistant) -> None:
    """Karte als gespeicherte Lovelace-Ressource eintragen oder aktualisieren.

    Die URL trägt ``?v=<Version>``, damit Browser nach einem Update keine alte
    Kopie ausliefern. Im YAML-Modus sind Ressourcen schreibgeschützt, dort muss
    die Karte manuell eingetragen werden (siehe README). Wirft nie.
    """
    lovelace_data = hass.data.get(LOVELACE_DATA)
    if lovelace_data is None:
        _LOGGER.debug("Lovelace-Daten nicht gefunden - Ressource %s bitte manuell eintragen", CARD_STATIC_URL)
        return
    resources: Any = lovelace_data.resources
    if not hasattr(resources, "async_create_item"):
        _LOGGER.debug("Lovelace läuft im YAML-Modus - %s bitte manuell als Ressource eintragen", CARD_STATIC_URL)
        return
    try:
        if not getattr(resources, "loaded", True):
            await resources.async_load()
        integration = await async_get_integration(hass, DOMAIN)
        target_url = f"{CARD_STATIC_URL}?v={integration.version}"
        existing = next(
            (
                item
                for item in resources.async_items()
                if item.get("url", "").split("?", 1)[0] == CARD_STATIC_URL
            ),
            None,
        )
        if existing is None:
            await resources.async_create_item({"res_type": "module", "url": target_url})
        elif existing.get("url") != target_url:
            await resources.async_update_item(
                existing["id"], {"res_type": "module", "url": target_url}
            )
    except Exception as ex:  # noqa: BLE001 - best effort
        _LOGGER.warning(
            "Konnte %s nicht automatisch als Lovelace-Ressource eintragen (%s)."
            " Bitte unter Einstellungen -> Dashboards -> Ressourcen hinzufügen (Typ 'module').",
            CARD_STATIC_URL,
            ex,
        )
