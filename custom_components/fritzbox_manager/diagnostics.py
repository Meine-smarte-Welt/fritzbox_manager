# SHA256 (Inhalt ab Zeile 2, d.h. dieser Datei ohne diese erste Zeile): 27d96db2ee41025e769aaf11eda84fcb3eec70a6f12604e1a7c157c0a6cddafa
"""Anonymisierter Diagnose-Download."""

from __future__ import annotations

from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_PORT, CONF_USERNAME
from homeassistant.core import HomeAssistant

from . import FritzConfigEntry
from .const import VERSION

TO_REDACT = {CONF_HOST, CONF_PASSWORD, CONF_USERNAME, CONF_PORT, "unique_id", "title"}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: FritzConfigEntry
) -> dict[str, Any]:
    """Nur Struktur und Verfügbarkeit - keine Adressen, Namen oder Zugangsdaten."""
    manager = entry.runtime_data
    data = manager.data or {}
    wlan = data.get("wlan") or {}
    return {
        "integration_version": VERSION,
        "entry": async_redact_data(dict(entry.data), TO_REDACT),
        "options": dict(entry.options),
        "connected": manager.last_update_success,
        "model": (data.get("device") or {}).get("model"),
        "firmware": (data.get("device") or {}).get("firmware"),
        "sections": {
            name: bool(data.get(name)) for name in ("device", "update", "wan", "dsl", "wlan", "lan", "system")
        },
        "section_errors": data.get("errors", {}),
        "wlan_networks": [
            {k: net.get(k) for k in ("key", "enabled", "guest", "band", "channel", "standard")}
            for net in wlan.get("networks", [])
        ],
        "experimental": {
            "enabled": manager.experimental_enabled,
            "backup_active": manager.backup_enabled,
            "backup_files": len(manager.backups),
        },
        "log_entries": len(manager.log),
        "update_info": {
            k: v
            for k, v in manager.update_checker.info.items()
            if k in ("version", "latest_version", "update_available", "check_failed")
        },
    }
