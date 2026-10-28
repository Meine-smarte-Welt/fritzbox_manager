# SHA256 (Inhalt ab Zeile 2, d.h. dieser Datei ohne diese erste Zeile): f86875fed6f43512c3473a1479ac8cab3604e120d37991c11d5a4ad0041585de
"""Manager: hält den Zustand der FRITZ!Box, fragt sie ab und meldet Änderungen."""

from __future__ import annotations

import asyncio
from collections import deque
from collections.abc import Callable
from datetime import datetime, timedelta, timezone
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_PORT, CONF_SSL, CONF_USERNAME
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import ConfigEntryAuthFailed, HomeAssistantError
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    CONF_CPU_TEMPERATURE,
    CONF_EVENTS_ENABLED,
    CONF_SCAN_INTERVAL,
    DEFAULT_CPU_TEMPERATURE,
    DEFAULT_EVENTS_ENABLED,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    EVENT_INTERNET_OFFLINE,
    EVENT_INTERNET_ONLINE,
    EVENT_IP_CHANGED,
    EVENT_UPDATE_AVAILABLE,
    MANUFACTURER,
    MAX_LOG_ENTRIES,
    MAX_SCAN_INTERVAL,
    MIN_SCAN_INTERVAL,
    SETTABLE_OPTIONS,
    VERSION,
)
from .fritz_client import (
    FritzActionFailed,
    FritzCannotConnect,
    FritzClient,
    FritzInvalidAuth,
)
from .update_check import UpdateChecker

_LOGGER = logging.getLogger(__name__)

# Nach einem Neustart ist die Box eine Weile nicht erreichbar. In dieser Zeit
# gilt das nicht als Verbindungsverlust.
REBOOT_GRACE = timedelta(minutes=4)


class FritzManager(DataUpdateCoordinator[dict[str, Any]]):
    """Ein Manager je Config Entry."""

    config_entry: ConfigEntry

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        super().__init__(
            hass,
            _LOGGER,
            config_entry=entry,
            name=f"{DOMAIN}_{entry.entry_id}",
            update_interval=timedelta(seconds=self._interval_from(entry)),
        )
        self.client = FritzClient(
            entry.data[CONF_HOST],
            entry.data.get(CONF_PORT),
            entry.data.get(CONF_USERNAME),
            entry.data.get(CONF_PASSWORD),
            entry.data.get(CONF_SSL, False),
        )
        self.update_checker = UpdateChecker(hass)
        self.log: deque[dict[str, Any]] = deque(maxlen=MAX_LOG_ENTRIES)
        self.jobs: dict[str, str] = {}
        self._response_listeners: set[Callable[[dict[str, Any]], None]] = set()
        self._baseline = False
        self._last_connected: bool | None = None
        self._last_ip: str | None = None
        self._last_update_version: str | None = None
        self._was_unreachable = False
        self._reboot_until: datetime | None = None
        self._tasks: set[asyncio.Task] = set()

    # --- Optionen ----------------------------------------------------------
    @staticmethod
    def _interval_from(entry: ConfigEntry) -> int:
        try:
            value = int(entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL))
        except (TypeError, ValueError):
            value = DEFAULT_SCAN_INTERVAL
        return max(MIN_SCAN_INTERVAL, min(MAX_SCAN_INTERVAL, value))

    @property
    def scan_interval(self) -> int:
        return self._interval_from(self.config_entry)

    @property
    def events_enabled(self) -> bool:
        return bool(self.config_entry.options.get(CONF_EVENTS_ENABLED, DEFAULT_EVENTS_ENABLED))

    @property
    def cpu_enabled(self) -> bool:
        return bool(self.config_entry.options.get(CONF_CPU_TEMPERATURE, DEFAULT_CPU_TEMPERATURE))

    @callback
    def apply_options(self) -> None:
        """Geänderte Optionen übernehmen, ohne den Eintrag neu zu laden."""
        self.update_interval = timedelta(seconds=self.scan_interval)
        self.async_update_listeners()

    @callback
    def async_set_option(self, option: str, value: Any) -> None:
        """Eine Option prüfen und speichern (Allowlist, Wertebereich)."""
        if option not in SETTABLE_OPTIONS:
            raise HomeAssistantError("Unbekannte Option.")
        if option == CONF_SCAN_INTERVAL:
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise HomeAssistantError("Ungültiges Intervall.")
            value = int(value)
            if not MIN_SCAN_INTERVAL <= value <= MAX_SCAN_INTERVAL:
                raise HomeAssistantError("Intervall außerhalb des erlaubten Bereichs.")
        elif not isinstance(value, bool):
            raise HomeAssistantError("Ungültiger Wert.")
        options = {**self.config_entry.options, option: value}
        self.hass.config_entries.async_update_entry(self.config_entry, options=options)
        self._log("option_changed", option=option)

    # --- Geräte-Registry -------------------------------------------------------
    @property
    def device_info(self) -> DeviceInfo:
        device = (self.data or {}).get("device", {})
        model = device.get("model") or "FRITZ!Box"
        scheme = "https" if self.config_entry.data.get(CONF_SSL) else "http"
        return DeviceInfo(
            identifiers={(DOMAIN, self.config_entry.entry_id)},
            manufacturer=MANUFACTURER,
            model=model,
            name=model if model.startswith("FRITZ!") else f"FRITZ!Box {model}",
            sw_version=device.get("firmware"),
            hw_version=device.get("hardware"),
            configuration_url=f"{scheme}://{self.config_entry.data[CONF_HOST]}",
        )

    # --- Abfrage -----------------------------------------------------------------
    async def _async_update_data(self) -> dict[str, Any]:
        try:
            data = await self.hass.async_add_executor_job(
                lambda: self.client.fetch(cpu_temperature=self.cpu_enabled)
            )
        except FritzInvalidAuth as ex:
            raise ConfigEntryAuthFailed("Anmeldung an der FRITZ!Box abgelehnt") from ex
        except FritzCannotConnect as ex:
            self._note_unreachable()
            raise UpdateFailed("FRITZ!Box nicht erreichbar") from ex
        data["fetched_at"] = datetime.now(timezone.utc).isoformat()
        self._detect_changes(data)
        await self._async_refresh_update_info()
        return data

    async def _async_refresh_update_info(self) -> None:
        """Version auf GitHub höchstens alle 12 h prüfen (der Prüfer bremst selbst)."""
        try:
            await self.update_checker.async_info()
        except Exception:  # noqa: BLE001 - darf die Abfrage der Box nie stören
            _LOGGER.debug("Versionsprüfung nicht möglich", exc_info=True)

    def _note_unreachable(self) -> None:
        expected = self._reboot_until is not None and datetime.now(timezone.utc) < self._reboot_until
        if self._baseline and not self._was_unreachable and not expected:
            self._log("connection_lost")
        self._was_unreachable = True

    def _detect_changes(self, data: dict[str, Any]) -> None:
        """Zustandswechsel erkennen: Protokoll immer, HA-Ereignis nur wenn eingeschaltet."""
        if self._was_unreachable:
            self._was_unreachable = False
            self._reboot_until = None
            self.jobs.pop("reboot", None)
            if self._baseline:
                self._log("connection_restored")
        wan = data.get("wan") or {}
        update = data.get("update") or {}
        connected = wan.get("connected") if wan.get("status") else None
        ip = wan.get("external_ip")
        new_version = update.get("new_version") if update.get("available") else None
        payload = {"entry_id": self.config_entry.entry_id}

        if self._baseline:
            if connected is False and self._last_connected is True:
                self._log("internet_offline")
                self._fire(EVENT_INTERNET_OFFLINE, payload)
            elif connected is True and self._last_connected is False:
                self._log("internet_online")
                self._fire(EVENT_INTERNET_ONLINE, payload)
            if ip and self._last_ip and ip != self._last_ip:
                self._log("ip_changed")
                self._fire(EVENT_IP_CHANGED, {**payload, "ip": ip, "previous_ip": self._last_ip})
            if new_version and new_version != self._last_update_version:
                self._log("firmware_update", version=new_version)
                self._fire(EVENT_UPDATE_AVAILABLE, {**payload, "version": new_version})
        # Ausgangszustand nach dem Start: nur merken, nichts melden.
        self._baseline = True
        if connected is not None:
            self._last_connected = connected
        if ip:
            self._last_ip = ip
        self._last_update_version = new_version

    def _fire(self, event: str, payload: dict[str, Any]) -> None:
        if self.events_enabled:
            self.hass.bus.async_fire(event, payload)

    def _log(self, kind: str, **params: Any) -> None:
        """Eintrag ins Protokoll (nur seit Start, im Speicher). Enthält keine Zugangsdaten."""
        self.log.appendleft(
            {
                "time": datetime.now(timezone.utc).isoformat(),
                "kind": kind,
                "params": {k: v for k, v in params.items() if v is not None},
            }
        )

    @callback
    def async_clear_log(self) -> None:
        self.log.clear()
        self.async_update_listeners()

    # --- Aktionen -----------------------------------------------------------------
    def network(self, key: str) -> dict[str, Any] | None:
        for net in ((self.data or {}).get("wlan") or {}).get("networks", []):
            if net.get("key") == key:
                return net
        return None

    async def async_set_wlan(self, key: str, enabled: bool) -> None:
        net = self.network(key)
        if net is None:
            raise HomeAssistantError("Unbekanntes WLAN-Netz.")
        try:
            await self.hass.async_add_executor_job(self.client.set_wlan, net["index"], enabled)
        except FritzActionFailed as ex:
            raise HomeAssistantError(f"Die FRITZ!Box hat die Aktion abgelehnt ({ex}).") from ex
        except (FritzCannotConnect, FritzInvalidAuth) as ex:
            raise HomeAssistantError("FRITZ!Box nicht erreichbar oder Anmeldung abgelehnt.") from ex
        self._log("wlan_changed", wlan=net.get("ssid") or key, enabled=enabled)
        # Die Box braucht einen Moment, bis der neue Zustand sichtbar ist.
        await asyncio.sleep(2)
        await self.async_request_refresh()

    async def async_reboot(self) -> None:
        self._reboot_until = datetime.now(timezone.utc) + REBOOT_GRACE
        self.jobs["reboot"] = datetime.now(timezone.utc).isoformat()
        try:
            await self.hass.async_add_executor_job(self.client.reboot)
        except (FritzActionFailed, FritzCannotConnect, FritzInvalidAuth) as ex:
            self._reboot_until = None
            self.jobs.pop("reboot", None)
            raise HomeAssistantError("Die FRITZ!Box hat den Neustart nicht angenommen.") from ex
        self._log("reboot_requested")
        self.async_update_listeners()

    async def async_reconnect(self) -> None:
        try:
            await self.hass.async_add_executor_job(self.client.reconnect)
        except (FritzActionFailed, FritzCannotConnect, FritzInvalidAuth) as ex:
            raise HomeAssistantError("Die FRITZ!Box hat die Aktion abgelehnt.") from ex
        self._log("reconnect_requested")
        await asyncio.sleep(3)
        await self.async_request_refresh()

    async def async_check_update(self) -> dict[str, Any]:
        info = await self.update_checker.async_info(force=True)
        self.async_update_listeners()
        return info

    # --- Hintergrundaufträge und Rückmeldungen -------------------------------------
    @callback
    def async_add_response_listener(self, listener: Callable[[dict[str, Any]], None]) -> Callable[[], None]:
        self._response_listeners.add(listener)
        return lambda: self._response_listeners.discard(listener)

    @callback
    def respond(self, topic: str, error: str | None = None) -> None:
        message = {"topic": topic, "status": "error" if error else "ok", "error": error}
        for listener in list(self._response_listeners):
            listener(message)

    def run_in_background(self, topic: str, coro_factory: Callable[[], Any]) -> None:
        """Langsame Aktion starten; das Ergebnis kommt als Rückmeldung (Toast in der Karte)."""

        async def _runner() -> None:
            try:
                await coro_factory()
            except HomeAssistantError as ex:
                self.respond(topic, str(ex))
            except Exception:  # noqa: BLE001 - ein Auftrag darf nie die Verbindung abbrechen
                _LOGGER.exception("Aktion %s fehlgeschlagen", topic)
                self.respond(topic, "Unerwarteter Fehler (siehe Protokoll).")
            else:
                self.respond(topic)

        task = self.hass.async_create_background_task(_runner(), f"{DOMAIN}_{topic}")
        self._tasks.add(task)
        task.add_done_callback(self._tasks.discard)

    # --- Momentaufnahme für die Karte --------------------------------------------
    def snapshot(self, *, is_admin: bool = False) -> dict[str, Any]:
        if self._reboot_until and datetime.now(timezone.utc) > self._reboot_until:
            # Die Box ist nach dem Neustart nie ausgefallen oder längst zurück.
            self._reboot_until = None
            self.jobs.pop("reboot", None)
        info = self.update_checker.info
        snap: dict[str, Any] = {
            "entry_id": self.config_entry.entry_id,
            "title": self.config_entry.title,
            "connected": bool(self.last_update_success),
            "reboot_pending": "reboot" in self.jobs,
            "jobs": sorted(self.jobs),
            "data": self.data or {},
            "app": {
                "version": VERSION,
                "latest_version": info.get("latest_version"),
                "release_url": info.get("release_url"),
                "update_available": bool(info.get("update_available")),
                "checked_at": info.get("checked_at"),
                "check_failed": bool(info.get("check_failed")),
            },
            "options": {
                CONF_SCAN_INTERVAL: self.scan_interval,
                CONF_EVENTS_ENABLED: self.events_enabled,
                CONF_CPU_TEMPERATURE: self.cpu_enabled,
            },
            "events": list(self.log),
        }
        if is_admin:
            snap["host"] = self.config_entry.data[CONF_HOST]
            snap["ssl"] = bool(self.config_entry.data.get(CONF_SSL))
        return snap
