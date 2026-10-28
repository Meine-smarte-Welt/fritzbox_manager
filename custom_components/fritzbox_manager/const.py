# SHA256 (Inhalt ab Zeile 2, d.h. dieser Datei ohne diese erste Zeile): aad760e8ad0451e8337ed069035396edb6f66ad5ac0f8b6fc86d41bdf7a7fd1c
"""Konstanten der Integration FRITZ!Box Manager."""

from __future__ import annotations

from typing import Final

from homeassistant.const import Platform

DOMAIN: Final = "fritzbox_manager"

# Version dieser Integration. MUSS mit manifest.json und CARD_VERSION in der
# Karte (www/fritzbox-manager-card.js) identisch sein (Prüfung vor dem Release).
VERSION: Final = "0.0.1b0"
GITHUB_REPO: Final = "Meine-smarte-Welt/fritzbox_manager"
GITHUB_RELEASES_URL: Final = f"https://github.com/{GITHUB_REPO}/releases"
MANUFACTURER: Final = "AVM"

PLATFORMS: Final = [
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    Platform.SWITCH,
    Platform.BUTTON,
]

# --- Verbindung -------------------------------------------------------------
DEFAULT_HOST: Final = "fritz.box"
DEFAULT_USERNAME: Final = "admin"
REQUEST_TIMEOUT: Final = 10

# --- Optionen ---------------------------------------------------------------
CONF_SCAN_INTERVAL: Final = "scan_interval"
CONF_EVENTS_ENABLED: Final = "events_enabled"
CONF_CPU_TEMPERATURE: Final = "cpu_temperature"
DEFAULT_SCAN_INTERVAL: Final = 30
MIN_SCAN_INTERVAL: Final = 10
MAX_SCAN_INTERVAL: Final = 600
DEFAULT_EVENTS_ENABLED: Final = True
# Experimentell: nutzt die nicht öffentlich dokumentierte query.lua der Box.
DEFAULT_CPU_TEMPERATURE: Final = False

# --- Home-Assistant-Ereignisse (abschaltbar, beim Start nur Ausgangszustand) --
EVENT_INTERNET_OFFLINE: Final = f"{DOMAIN}_internet_offline"
EVENT_INTERNET_ONLINE: Final = f"{DOMAIN}_internet_online"
EVENT_IP_CHANGED: Final = f"{DOMAIN}_ip_changed"
EVENT_UPDATE_AVAILABLE: Final = f"{DOMAIN}_update_available"

# --- Karte / Frontend -------------------------------------------------------
CARD_URL_BASE: Final = f"/{DOMAIN}_files"
CARD_FILENAME: Final = "fritzbox-manager-card.js"
CARD_STATIC_URL: Final = f"{CARD_URL_BASE}/{CARD_FILENAME}"

# --- WebSocket --------------------------------------------------------------
WS_SUBSCRIBE: Final = f"{DOMAIN}/subscribe"
WS_ACTION: Final = f"{DOMAIN}/action"

ACTION_SET_WLAN: Final = "set_wlan"
ACTION_REBOOT: Final = "reboot"
ACTION_RECONNECT: Final = "reconnect"
ACTION_CHECK_UPDATE: Final = "check_update"
ACTION_SET_OPTION: Final = "set_option"
ACTION_CLEAR_EVENTS: Final = "clear_events"
ACTIONS: Final = (
    ACTION_SET_WLAN,
    ACTION_REBOOT,
    ACTION_RECONNECT,
    ACTION_CHECK_UPDATE,
    ACTION_SET_OPTION,
    ACTION_CLEAR_EVENTS,
)
# Optionen, die die Karte über ``set_option`` ändern darf (Allowlist).
SETTABLE_OPTIONS: Final = (CONF_SCAN_INTERVAL, CONF_EVENTS_ENABLED, CONF_CPU_TEMPERATURE)

# --- Services ---------------------------------------------------------------
SERVICE_REBOOT: Final = "reboot"
SERVICE_RECONNECT: Final = "reconnect"
SERVICE_SET_WLAN: Final = "set_wlan"
SERVICE_CHECK_UPDATE: Final = "check_for_update"

ATTR_ENTRY_ID: Final = "entry_id"
ATTR_WLAN: Final = "wlan"
ATTR_ENABLED: Final = "enabled"

# Maximale Zahl gemerkter Ereignisse im Protokoll (seit Start).
MAX_LOG_ENTRIES: Final = 100
