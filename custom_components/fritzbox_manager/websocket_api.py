# SHA256 (Inhalt ab Zeile 2, d.h. dieser Datei ohne diese erste Zeile): b57f3e880021810803d82cc8b617382d74c85dd52ab1cea88382b4748ea47de1
"""WebSocket-Schnittstelle für die Karte (subscribe / action)."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.components import websocket_api as ha_ws
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError

from .const import (
    ACTION_CHECK_UPDATE,
    ACTION_CLEAR_EVENTS,
    ACTION_REBOOT,
    ACTION_RECONNECT,
    ACTION_SET_OPTION,
    ACTION_SET_WLAN,
    ACTIONS,
    DOMAIN,
    SETTABLE_OPTIONS,
    WS_ACTION,
    WS_SUBSCRIBE,
)


def async_register(hass: HomeAssistant) -> None:
    """Befehle registrieren (einmalig)."""
    ha_ws.async_register_command(hass, ws_subscribe)
    ha_ws.async_register_command(hass, ws_action)


def _manager(hass: HomeAssistant, connection: Any, msg: dict[str, Any]):
    from . import get_manager  # späte Einbindung: vermeidet den Import-Zirkel

    manager = get_manager(hass, msg.get("entry_id"))
    if manager is None:
        connection.send_error(msg["id"], ha_ws.ERR_NOT_FOUND, "Keine geladene FRITZ!Box gefunden.")
    return manager


@ha_ws.websocket_command(
    {
        vol.Required("type"): WS_SUBSCRIBE,
        vol.Optional("entry_id"): str,
    }
)
@ha_ws.async_response
async def ws_subscribe(hass: HomeAssistant, connection: Any, msg: dict[str, Any]) -> None:
    """Momentaufnahme senden und danach bei jeder Änderung erneut."""
    manager = _manager(hass, connection, msg)
    if manager is None:
        return
    is_admin = bool(connection.user and connection.user.is_admin)

    @callback
    def _send_snapshot() -> None:
        connection.send_message(
            ha_ws.event_message(
                msg["id"], {"type": "snapshot", "data": manager.snapshot(is_admin=is_admin)}
            )
        )

    @callback
    def _send_response(message: dict[str, Any]) -> None:
        connection.send_message(ha_ws.event_message(msg["id"], {"type": "response", **message}))

    unsub_data = manager.async_add_listener(_send_snapshot)
    unsub_response = manager.async_add_response_listener(_send_response)

    @callback
    def _unsubscribe() -> None:
        unsub_data()
        unsub_response()

    connection.subscriptions[msg["id"]] = _unsubscribe
    connection.send_result(msg["id"])
    _send_snapshot()


@ha_ws.require_admin
@ha_ws.websocket_command(
    {
        vol.Required("type"): WS_ACTION,
        vol.Optional("entry_id"): str,
        vol.Required("action"): vol.In(ACTIONS),
        # Bewusst kein Feld "id" oder "timeout" (kollidiert mit der Nachrichten-ID).
        vol.Optional("wlan"): vol.Match(r"^wlan[1-9]$"),
        vol.Optional("enabled"): bool,
        vol.Optional("option"): vol.In(SETTABLE_OPTIONS),
        vol.Optional("value"): vol.Any(bool, int, float),
    }
)
@ha_ws.async_response
async def ws_action(hass: HomeAssistant, connection: Any, msg: dict[str, Any]) -> None:
    """Aktion ausführen (nur Administratoren). Langsame laufen im Hintergrund."""
    manager = _manager(hass, connection, msg)
    if manager is None:
        return
    action = msg["action"]
    try:
        if action == ACTION_SET_WLAN:
            wlan, enabled = msg.get("wlan"), msg.get("enabled")
            if wlan is None or enabled is None or manager.network(wlan) is None:
                raise HomeAssistantError("Unbekanntes WLAN-Netz oder fehlende Angabe.")
            manager.run_in_background(action, lambda: manager.async_set_wlan(wlan, enabled))
        elif action == ACTION_REBOOT:
            manager.run_in_background(action, manager.async_reboot)
        elif action == ACTION_RECONNECT:
            manager.run_in_background(action, manager.async_reconnect)
        elif action == ACTION_CHECK_UPDATE:
            manager.run_in_background(action, manager.async_check_update)
        elif action == ACTION_SET_OPTION:
            if "option" not in msg or "value" not in msg:
                raise HomeAssistantError("Option oder Wert fehlt.")
            manager.async_set_option(msg["option"], msg["value"])
            manager.respond(action)
        elif action == ACTION_CLEAR_EVENTS:
            manager.async_clear_log()
            manager.respond(action)
    except HomeAssistantError as ex:
        connection.send_error(msg["id"], ha_ws.ERR_INVALID_FORMAT, str(ex))
        return
    connection.send_result(msg["id"], {"accepted": True, "domain": DOMAIN})
