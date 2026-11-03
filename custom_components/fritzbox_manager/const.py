# SHA256 (Inhalt ab Zeile 2, d.h. dieser Datei ohne diese erste Zeile): d0f0585f49848600606c23ee8872d4b4a40c8ad8dd51129089e4dd3f6336c13b
"""Konstanten der Integration FRITZ!Box Manager."""

from __future__ import annotations

from typing import Final

from homeassistant.const import Platform

DOMAIN: Final = "fritzbox_manager"

# Version dieser Integration. MUSS mit manifest.json und CARD_VERSION in der
# Karte (www/fritzbox-manager-card.js) identisch sein (Prüfung vor dem Release).
VERSION: Final = "0.0.2b1"
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

# --- Experimentelle Funktionen (ungeprüft, standardmäßig ausgeblendet) --------------
# Hauptschalter: solange er aus ist, bleibt das Backend für alle Funktionen dieser
# Registry still (keine Aktionen, keine Ereignisse). Jede Funktion hat zusätzlich
# einen eigenen Schalter (Standard aus). Registry und Karte (EXPERIMENTAL) müssen
# schlüsselgleich sein.
CONF_EXPERIMENTAL_ENABLED: Final = "experimental_enabled"
DEFAULT_EXPERIMENTAL_ENABLED: Final = False
CONF_BACKUP_ENABLED: Final = "backup_enabled"
DEFAULT_BACKUP_ENABLED: Final = False
CONF_BACKUP_KEEP: Final = "backup_keep"
DEFAULT_BACKUP_KEEP: Final = 10
MIN_BACKUP_KEEP: Final = 1
MAX_BACKUP_KEEP: Final = 50
EXPERIMENTAL_FEATURES: Final = {
    "backup": {"since": "0.0.2b1", "icon": "mdi:backup-restore", "option": CONF_BACKUP_ENABLED},
}

# --- Backup der FRITZ!Box-Einstellungen --------------------------------------------
# Ordner innerhalb des Home-Assistant-Konfigurationsordners. Der Name ist fest
# (kein frei wählbarer Pfad), damit nie außerhalb davon geschrieben wird.
BACKUP_DIR_NAME: Final = "fritzbox_manager_backups"
BACKUP_SUFFIX: Final = ".export"
BACKUP_MAX_BYTES: Final = 64 * 1024 * 1024
BACKUP_PASSWORD_MAX: Final = 128

# --- Home-Assistant-Ereignisse (abschaltbar, beim Start nur Ausgangszustand) --
EVENT_INTERNET_OFFLINE: Final = f"{DOMAIN}_internet_offline"
EVENT_INTERNET_ONLINE: Final = f"{DOMAIN}_internet_online"
EVENT_IP_CHANGED: Final = f"{DOMAIN}_ip_changed"
EVENT_UPDATE_AVAILABLE: Final = f"{DOMAIN}_update_available"
# Experimentell (nur mit Hauptschalter und Backup-Schalter): Backup gespeichert.
EVENT_BACKUP_CREATED: Final = f"{DOMAIN}_backup_created"

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
ACTION_CREATE_BACKUP: Final = "create_backup"
ACTIONS: Final = (
    ACTION_SET_WLAN,
    ACTION_REBOOT,
    ACTION_RECONNECT,
    ACTION_CHECK_UPDATE,
    ACTION_SET_OPTION,
    ACTION_CLEAR_EVENTS,
    ACTION_CREATE_BACKUP,
)
# Optionen, die die Karte über ``set_option`` ändern darf (Allowlist).
SETTABLE_OPTIONS: Final = (
    CONF_SCAN_INTERVAL,
    CONF_EVENTS_ENABLED,
    CONF_CPU_TEMPERATURE,
    CONF_EXPERIMENTAL_ENABLED,
    CONF_BACKUP_ENABLED,
    CONF_BACKUP_KEEP,
)

# --- Services ---------------------------------------------------------------
SERVICE_REBOOT: Final = "reboot"
SERVICE_RECONNECT: Final = "reconnect"
SERVICE_SET_WLAN: Final = "set_wlan"
SERVICE_CHECK_UPDATE: Final = "check_for_update"
SERVICE_CREATE_BACKUP: Final = "create_backup"

ATTR_ENTRY_ID: Final = "entry_id"
ATTR_WLAN: Final = "wlan"
ATTR_ENABLED: Final = "enabled"
ATTR_PASSWORD: Final = "password"

# Maximale Zahl gemerkter Ereignisse im Protokoll (seit Start).
MAX_LOG_ENTRIES: Final = 100
