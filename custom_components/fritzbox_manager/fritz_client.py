# SHA256 (Inhalt ab Zeile 2, d.h. dieser Datei ohne diese erste Zeile): e6a28968e8e7781c04b543dcd68072266bdc9e7462f4419dc202f4a60c474b1a
"""Blockierender TR-064-Zugriff auf die FRITZ!Box (fritzconnection).

Alle Methoden blockieren und müssen aus dem Executor aufgerufen werden.
Die Verbindung wird einmal aufgebaut und wiederverwendet (der Aufbau liest die
komplette Schnittstellenbeschreibung der Box und ist teuer).

Jeder Abschnitt der Abfrage ist für sich abgesichert: Unterstützt eine Box
einen Dienst nicht (z. B. DSL-Werte bei einem Kabel-Modell), fehlt nur dieser
Abschnitt - der Rest wird weiter geliefert.
"""

from __future__ import annotations

import logging
import threading
from typing import Any, Callable
from urllib.parse import urlsplit, urlunsplit

from fritzconnection import FritzConnection
from fritzconnection.core.exceptions import (
    FritzActionError,
    FritzArgumentCharacterError,
    FritzArgumentError,
    FritzArgumentStringToLongError,
    FritzArgumentStringToShortError,
    FritzArrayIndexError,
    FritzAuthorizationError,
    FritzConnectionException,
    FritzInternalError,
    FritzLookUpError,
    FritzSecurityError,
    FritzServiceError,
)
from requests.exceptions import RequestException

from .const import BACKUP_MAX_BYTES, REQUEST_TIMEOUT
from .webui import WebUi, WebUiError

_LOGGER = logging.getLogger(__name__)

MAX_WLAN_NETWORKS = 6

# Fehler, die bedeuten: "Diese Box kann das nicht" (kein Fehler der Verbindung).
_UNSUPPORTED = (
    FritzServiceError,
    FritzActionError,
    FritzArgumentError,
    FritzLookUpError,
    FritzArrayIndexError,
)
# Fehler, bei denen die Box antwortet, die Aktion aber nicht ausführt.
_REFUSED = (FritzInternalError, FritzSecurityError)


class FritzClientError(Exception):
    """Basisklasse der Fehler dieses Moduls."""


class FritzCannotConnect(FritzClientError):
    """Die Box ist nicht erreichbar oder antwortet nicht wie eine FRITZ!Box."""


class FritzInvalidAuth(FritzClientError):
    """Benutzername oder Kennwort wurden abgelehnt."""


class FritzActionFailed(FritzClientError):
    """Die Box hat eine Aktion abgelehnt oder nicht ausgeführt."""


class FritzBackupError(FritzActionFailed):
    """Das Backup der Einstellungen ist fehlgeschlagen. ``reason`` nennt den Grund (Kurzschlüssel)."""

    def __init__(self, reason: str) -> None:
        super().__init__(reason)
        self.reason = reason


class _SectionFailed(Exception):
    """Ein Abschnitt lieferte nichts, obwohl die Box den Dienst anbietet (Grund in ``str(ex)``)."""


def _int(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _float(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _band_from_channel(channel: int | None) -> str | None:
    """Heuristik: 1-14 = 2,4 GHz, 36-177 = 5 GHz. 6 GHz lässt sich so nicht erkennen."""
    if channel is None or channel <= 0:
        return None
    if channel <= 14:
        return "2.4"
    if 32 <= channel <= 177:
        return "5"
    return None


def _band_from_text(value: Any) -> str | None:
    text = (_text(value) or "").lower().replace(" ", "")
    if text.startswith("2.4") or text.startswith("2,4"):
        return "2.4"
    if text.startswith("5"):
        return "5"
    if text.startswith("6"):
        return "6"
    return None


class FritzClient:
    """Dünne, abgesicherte Hülle um ``FritzConnection``."""

    def __init__(
        self,
        host: str,
        port: int | None,
        username: str | None,
        password: str | None,
        ssl: bool,
    ) -> None:
        self._host = host
        self._port = port or None
        self._username = username or None
        self._password = password or None
        self._ssl = bool(ssl)
        self._fc: FritzConnection | None = None
        self._fc_tls: FritzConnection | None = None
        self._web: WebUi | None = None
        self._lock = threading.Lock()
        self.serial: str | None = None

    # --- Verbindung ---------------------------------------------------
    def connect(self) -> dict[str, Any]:
        """Verbindung aufbauen und prüfen. Liefert die Geräteinformationen."""
        with self._lock:
            return self._connect_locked()

    def _connect_locked(self) -> dict[str, Any]:
        self._fc = None
        try:
            fc = FritzConnection(
                address=self._host,
                port=self._port,
                user=self._username,
                password=self._password,
                timeout=REQUEST_TIMEOUT,
                use_tls=self._ssl,
            )
            info = fc.call_action("DeviceInfo1", "GetInfo")
        except FritzAuthorizationError as ex:
            raise FritzInvalidAuth(str(ex)) from ex
        except (RequestException, OSError, FritzConnectionException, ValueError) as ex:
            # ``ValueError`` deckt u. a. Antworten ab, die keine FRITZ!Box sind.
            raise FritzCannotConnect(str(ex)) from ex
        self._fc = fc
        self.serial = _text(info.get("NewSerialNumber"))
        return {
            "model": _text(info.get("NewModelName")) or _text(getattr(fc, "modelname", None)),
            "firmware": _text(info.get("NewSoftwareVersion")),
            "serial": self.serial,
        }

    def close(self) -> None:
        """Verbindung verwerfen (die nächste Abfrage baut sie neu auf)."""
        with self._lock:
            self._fc = None
            self._fc_tls = None

    def close_web(self) -> None:
        """Sitzung an der Weboberfläche beenden (blockiert, gehört in den Executor)."""
        web, self._web = self._web, None
        if web is not None:
            web.close()

    # --- Abfrage -------------------------------------------------------
    def fetch(self, *, cpu_temperature: bool = False) -> dict[str, Any]:
        """Alle Systemdaten in einem Durchlauf holen."""
        with self._lock:
            if self._fc is None:
                self._connect_locked()
            errors: dict[str, str] = {}
            try:
                data = {
                    "device": self._section("device", errors, self._read_device) or {},
                    "update": self._section("update", errors, self._read_update),
                    "wan": self._section("wan", errors, self._read_wan) or {},
                    "dsl": self._section("dsl", errors, self._read_dsl),
                    "wlan": self._section("wlan", errors, self._read_wlan)
                    or {"networks": [], "clients_total": None},
                    "lan": self._section("lan", errors, self._read_lan) or {"hosts_total": None},
                    "system": {},
                }
                if cpu_temperature:
                    data["system"] = (
                        self._section("cpu", errors, self._read_cpu, quiet=True) or {}
                    )
            except FritzCannotConnect:
                self._fc = None
                raise
            data["errors"] = errors
            return data

    def _section(
        self,
        name: str,
        errors: dict[str, str],
        reader: Callable[[], Any],
        *,
        quiet: bool = False,
    ) -> Any:
        """Einen Abschnitt lesen; Fehler werden notiert, nicht geworfen."""
        try:
            return reader()
        except FritzAuthorizationError as ex:
            self._fc = None
            raise FritzInvalidAuth(str(ex)) from ex
        except _SectionFailed as ex:
            errors[name] = str(ex)
            _LOGGER.debug("Abschnitt %s lieferte nichts: %s", name, ex)
            return None
        except _UNSUPPORTED as ex:
            _LOGGER.debug("Abschnitt %s wird von dieser Box nicht unterstützt: %s", name, ex)
            return None
        except _REFUSED as ex:
            errors[name] = type(ex).__name__
            _LOGGER.debug("Abschnitt %s wurde von der Box abgelehnt: %s", name, ex)
            return None
        except (RequestException, OSError) as ex:
            if name in ("device", "wan"):
                raise FritzCannotConnect(str(ex)) from ex
            errors[name] = type(ex).__name__
            _LOGGER.debug("Abschnitt %s nicht lesbar: %s", name, ex)
            return None
        except FritzConnectionException as ex:
            errors[name] = type(ex).__name__
            _LOGGER.debug("Abschnitt %s nicht lesbar: %s", name, ex)
            return None
        except (KeyError, ValueError, TypeError) as ex:
            if not quiet:
                _LOGGER.debug("Abschnitt %s hat ein unerwartetes Format: %s", name, ex)
            errors[name] = type(ex).__name__
            return None

    def _call(self, service: str, action: str, **arguments: Any) -> dict[str, Any]:
        assert self._fc is not None
        return self._fc.call_action(service, action, arguments=arguments or None)

    def _has_service(self, service: str) -> bool:
        return self._fc is not None and service in self._fc.services

    def _wan_service(self) -> str:
        """Dienst der Internetverbindung: IP-Verbindung, sonst PPPoE (ältere Konfigurationen)."""
        if not self._has_service("WANIPConn1") and self._has_service("WANPPPConnection1"):
            return "WANPPPConnection1"
        return "WANIPConn1"

    # --- Abschnitte -----------------------------------------------------
    def _read_device(self) -> dict[str, Any]:
        info = self._call("DeviceInfo1", "GetInfo")
        self.serial = _text(info.get("NewSerialNumber")) or self.serial
        return {
            "model": _text(info.get("NewModelName")),
            "firmware": _text(info.get("NewSoftwareVersion")),
            "hardware": _text(info.get("NewHardwareVersion")),
            "uptime": _int(info.get("NewUpTime")),
        }

    def _read_update(self) -> dict[str, Any]:
        info = self._call("UserInterface1", "GetInfo")
        available = bool(info.get("NewUpgradeAvailable"))
        return {
            "available": available,
            "new_version": _text(info.get("NewX_AVM-DE_Version")) if available else None,
            "state": _text(info.get("NewX_AVM-DE_UpdateState")),
            "build_type": _text(info.get("NewX_AVM-DE_BuildType")),
        }

    def _read_wan(self) -> dict[str, Any]:
        wan: dict[str, Any] = {}
        service = self._wan_service()
        status = self._call(service, "GetStatusInfo")
        wan["status"] = _text(status.get("NewConnectionStatus"))
        wan["connected"] = wan["status"] == "Connected"
        wan["uptime"] = _int(status.get("NewUptime"))
        wan["last_error"] = _text(status.get("NewLastConnectionError"))
        if wan["last_error"] == "ERROR_NONE":
            wan["last_error"] = None

        wan["external_ip"] = None
        wan["external_ipv6"] = None
        wan["ipv6_prefix"] = None
        try:
            ip = _text(self._call(service, "GetExternalIPAddress").get("NewExternalIPAddress"))
            wan["external_ip"] = ip if ip and ip != "0.0.0.0" else None
        except _UNSUPPORTED + _REFUSED:
            pass
        try:
            v6 = self._call(service, "X_AVM_DE_GetExternalIPv6Address")
            wan["external_ipv6"] = _text(v6.get("NewExternalIPv6Address"))
        except _UNSUPPORTED + _REFUSED:
            pass
        try:
            prefix = self._call(service, "X_AVM_DE_GetIPv6Prefix")
            text = _text(prefix.get("NewIPv6Prefix"))
            length = _int(prefix.get("NewPrefixLength"))
            wan["ipv6_prefix"] = f"{text}/{length}" if text and length else text
        except _UNSUPPORTED + _REFUSED:
            pass

        wan.update(
            {
                "link_status": None,
                "access_type": None,
                "max_down": None,
                "max_up": None,
                "rate_down": None,
                "rate_up": None,
                "bytes_received": None,
                "bytes_sent": None,
            }
        )
        try:
            link = self._call("WANCommonIFC1", "GetCommonLinkProperties")
            wan["link_status"] = _text(link.get("NewPhysicalLinkStatus"))
            wan["access_type"] = _text(link.get("NewWANAccessType"))
            wan["max_down"] = _int(link.get("NewLayer1DownstreamMaxBitRate"))
            wan["max_up"] = _int(link.get("NewLayer1UpstreamMaxBitRate"))
        except _UNSUPPORTED + _REFUSED:
            pass
        try:
            addon = self._call("WANCommonIFC1", "GetAddonInfos")
            down = _int(addon.get("NewByteReceiveRate"))
            up = _int(addon.get("NewByteSendRate"))
            # Die Box meldet Byte pro Sekunde; angezeigt wird Bit pro Sekunde.
            wan["rate_down"] = down * 8 if down is not None else None
            wan["rate_up"] = up * 8 if up is not None else None
            received = _int(addon.get("NewX_AVM_DE_TotalBytesReceived64"))
            sent = _int(addon.get("NewX_AVM_DE_TotalBytesSent64"))
            wan["bytes_received"] = received if received is not None else _int(
                addon.get("NewTotalBytesReceived")
            )
            wan["bytes_sent"] = sent if sent is not None else _int(addon.get("NewTotalBytesSent"))
        except _UNSUPPORTED + _REFUSED:
            pass
        return wan

    def _read_dsl(self) -> dict[str, Any] | None:
        if not self._has_service("WANDSLInterfaceConfig1"):
            return None
        info = self._call("WANDSLInterfaceConfig1", "GetInfo")
        status = _text(info.get("NewStatus"))
        # Der Dienst existiert auch bei Boxen ohne DSL-Leitung (Kabel, Glasfaser, hinter
        # einem anderen Router) und liefert dann lauter Nullen. Echte Werte gibt es nur,
        # wenn die Leitung steht; sonst bleiben sie leer, damit keine 0 angezeigt wird.
        up = (status or "").lower() == "up"

        def tenth(key: str) -> float | None:
            value = _float(info.get(key))
            return round(value / 10, 1) if value is not None and up else None

        def rate(key: str) -> int | None:
            value = _int(info.get(key))
            return value * 1000 if value and up else None

        return {
            "status": status,
            "noise_margin_down": tenth("NewDownstreamNoiseMargin"),
            "noise_margin_up": tenth("NewUpstreamNoiseMargin"),
            "attenuation_down": tenth("NewDownstreamAttenuation"),
            "attenuation_up": tenth("NewUpstreamAttenuation"),
            "rate_down": rate("NewDownstreamCurrRate"),
            "rate_up": rate("NewUpstreamCurrRate"),
        }

    def _read_wlan(self) -> dict[str, Any]:
        """WLAN-Netze lesen. Nur ``GetInfo`` ist Pflicht; alles andere fehlt notfalls einfach."""
        assert self._fc is not None
        raw, first_error = self._collect_wlan(self._fc)
        if not raw and first_error is not None and not self._ssl:
            # Manche Boxen verweigern die WLAN-Abfrage über die unverschlüsselte Schnittstelle
            # (Port 49000). Dann einmal über die verschlüsselte (Port 49443) versuchen.
            tls = self._tls_connection()
            if tls is not None:
                raw, _tls_error = self._collect_wlan(tls)
                if raw:
                    _LOGGER.debug(
                        "WLAN über HTTPS gelesen, über HTTP verweigert (%s)", type(first_error).__name__
                    )
                    first_error = None
        if not raw and first_error is not None:
            # Die Box bietet WLAN-Dienste an, hat aber jede Abfrage abgelehnt (meist fehlt dem
            # Benutzer das Recht "FRITZ!Box Einstellungen"). Das wird gemeldet statt verschwiegen.
            raise _SectionFailed(type(first_error).__name__)
        # Gastnetz: bevorzugt die Angabe der Box; sonst - wie in fritzconnection -
        # bei mindestens drei Netzen das mit der höchsten Nummer (Heuristik).
        for position, network in enumerate(raw):
            ap_type = (network.pop("_ap_type") or "").lower()
            if ap_type:
                network["guest"] = ap_type == "guest"
            else:
                network["guest"] = len(raw) >= 3 and position == len(raw) - 1
        total: int | None = None
        counts = [n["clients"] for n in raw if n["clients"] is not None]
        if counts:
            total = sum(counts)
        return {"networks": raw, "clients_total": total}

    @staticmethod
    def _collect_wlan(fc: FritzConnection) -> tuple[list[dict[str, Any]], Exception | None]:
        """Alle WLAN-Dienste einer Verbindung lesen. Gibt (Netze, erster Fehler von GetInfo) zurück."""
        raw: list[dict[str, Any]] = []
        first_error: Exception | None = None

        def optional(service: str, action: str) -> dict[str, Any]:
            """Zusatzangabe: jeder Fehler außer abgelehnter Anmeldung ergibt nur „keine Angabe“."""
            try:
                return fc.call_action(service, action) or {}
            except FritzAuthorizationError:
                raise
            except (FritzConnectionException, RequestException, OSError, KeyError, ValueError, TypeError) as ex:
                _LOGGER.debug("%s.%s nicht lesbar: %s", service, action, type(ex).__name__)
                return {}

        for index in range(1, MAX_WLAN_NETWORKS + 1):
            service = f"WLANConfiguration{index}"
            if service not in fc.services:
                break
            try:
                info = fc.call_action(service, "GetInfo")
            except FritzAuthorizationError:
                raise
            except (FritzConnectionException, RequestException, OSError, ValueError, TypeError) as ex:
                first_error = first_error or ex
                _LOGGER.debug("%s.GetInfo nicht lesbar: %s", service, type(ex).__name__)
                continue
            clients = _int(optional(service, "GetTotalAssociations").get("NewTotalAssociations"))
            ext = optional(service, "X_AVM-DE_GetWLANExtInfo")
            channel = _int(info.get("NewChannel"))
            raw.append(
                {
                    "index": index,
                    "key": f"wlan{index}",
                    "ssid": _text(info.get("NewSSID")),
                    "enabled": bool(info.get("NewEnable")),
                    "status": _text(info.get("NewStatus")),
                    "channel": channel if channel else None,
                    "standard": _text(info.get("NewStandard")),
                    "band": _band_from_text(ext.get("NewX_AVM-DE_FrequencyBand"))
                    or _band_from_channel(channel),
                    "clients": clients,
                    "_ap_type": _text(ext.get("NewX_AVM-DE_APType")),
                }
            )
        return raw, first_error

    def _tls_connection(self) -> FritzConnection | None:
        """Verschlüsselte TR-064-Verbindung (Standardport 49443) zur selben Box, einmalig aufgebaut."""
        if self._fc_tls is not None:
            return self._fc_tls
        try:
            self._fc_tls = FritzConnection(
                address=self._host,
                port=None,
                user=self._username,
                password=self._password,
                timeout=REQUEST_TIMEOUT,
                use_tls=True,
            )
        except (FritzConnectionException, RequestException, OSError, ValueError) as ex:
            _LOGGER.debug("Verschlüsselte TR-064-Verbindung nicht möglich: %s", type(ex).__name__)
            return None
        return self._fc_tls

    def _read_lan(self) -> dict[str, Any]:
        info = self._call("Hosts1", "GetHostNumberOfEntries")
        return {"hosts_total": _int(info.get("NewHostNumberOfEntries"))}

    def _read_cpu(self) -> dict[str, Any]:
        """CPU-Temperatur über die Weboberfläche (``ecoStat``, experimentell, wie FRITZ!Box Netzwerk)."""
        if self._web is None:
            self._web = WebUi(self._host, self._username, self._password, self._ssl)
        try:
            return {"cpu_temperature": self._web.cpu_temperature()}
        except WebUiError as ex:
            raise _SectionFailed(ex.reason) from ex

    # --- Aktionen -------------------------------------------------------
    def set_wlan(self, index: int, enabled: bool) -> None:
        """WLAN-Netz ein-/ausschalten (bei verweigerter HTTP-Verbindung einmal über HTTPS)."""
        service = f"WLANConfiguration{int(index)}"
        try:
            self._action(service, "SetEnable", NewEnable=bool(enabled))
        except FritzActionFailed:
            if self._ssl:
                raise
            with self._lock:
                tls = self._tls_connection()
                if tls is None:
                    raise
                try:
                    tls.call_action(service, "SetEnable", arguments={"NewEnable": bool(enabled)})
                except FritzAuthorizationError as ex:
                    raise FritzInvalidAuth(str(ex)) from ex
                except FritzConnectionException as ex:
                    raise FritzActionFailed(type(ex).__name__) from ex
                except (RequestException, OSError) as ex:
                    raise FritzCannotConnect(str(ex)) from ex

    def reboot(self) -> None:
        """FRITZ!Box neu starten."""
        self._action("DeviceConfig1", "Reboot")

    def reconnect(self) -> None:
        """Internetverbindung trennen und neu aufbauen (neue IP-Adresse)."""
        self._action(self._wan_service(), "ForceTermination")

    def export_config(self, password: str, max_bytes: int = BACKUP_MAX_BYTES) -> bytes:
        """Einstellungen der Box (mit ``password`` verschlüsselt) per TR-064 holen. EXPERIMENTELL.

        Ablauf nach der Beschreibung von AVM (DeviceConfig, ``X_AVM-DE_GetConfigFile``): Die Box
        liefert eine kurzlebige Download-Adresse (HTTPS, unter 30 Sekunden gültig, Digest-
        Anmeldung mit dem TR-064-Benutzer). Das Kennwort schützt die Datei; es wird nicht
        gespeichert und nicht protokolliert.
        """
        with self._lock:
            if self._fc is None:
                self._connect_locked()
            fc = self._fc
            assert fc is not None
            try:
                result = self._call(
                    "DeviceConfig1", "X_AVM-DE_GetConfigFile", **{"NewX_AVM-DE_Password": password}
                )
                url = _text(result.get("NewX_AVM-DE_ConfigFileUrl"))
                if not url:
                    raise FritzBackupError("no_url")
                return self._download(fc, url, max_bytes)
            except FritzBackupError:
                raise
            except FritzAuthorizationError as ex:
                self._fc = None
                raise FritzInvalidAuth(str(ex)) from ex
            except FritzArgumentStringToShortError as ex:
                raise FritzBackupError("password_short") from ex
            except FritzArgumentStringToLongError as ex:
                raise FritzBackupError("password_long") from ex
            except FritzArgumentCharacterError as ex:
                raise FritzBackupError("password_chars") from ex
            except FritzArgumentError as ex:
                raise FritzBackupError("password_invalid") from ex
            except FritzSecurityError as ex:
                raise FritzBackupError("no_permission") from ex
            except (FritzServiceError, FritzActionError, FritzLookUpError) as ex:
                raise FritzBackupError("unsupported") from ex
            except FritzInternalError as ex:
                raise FritzBackupError("refused") from ex
            except (RequestException, OSError) as ex:
                self._fc = None
                raise FritzCannotConnect(type(ex).__name__) from ex
            except FritzConnectionException as ex:
                raise FritzBackupError("refused") from ex

    def _download(self, fc: FritzConnection, url: str, max_bytes: int) -> bytes:
        """Download-Adresse der Box abrufen (nur bei der eingerichteten Box, ohne Weiterleitungen)."""
        try:
            parts = urlsplit(url)
            port = parts.port
        except ValueError as ex:
            raise FritzBackupError("bad_url") from ex
        if parts.scheme not in ("http", "https") or not parts.hostname:
            raise FritzBackupError("bad_url")
        # Es wird nur mit der eingerichteten Adresse gesprochen: der Rechnername aus der
        # Antwort der Box wird durch den eigenen ersetzt (kein Abruf fremder Ziele).
        host = self._host
        host_part = f"[{host}]" if ":" in host and not host.startswith("[") else host
        netloc = f"{host_part}:{port}" if port else host_part
        target = urlunsplit((parts.scheme, netloc, parts.path, parts.query, ""))
        chunks: list[bytes] = []
        total = 0
        with fc.session.get(
            target,
            timeout=(REQUEST_TIMEOUT, 30),
            stream=True,
            verify=False,
            allow_redirects=False,
        ) as response:
            if response.status_code != 200:
                raise FritzBackupError("http_error")
            if "html" in (response.headers.get("Content-Type") or "").lower():
                raise FritzBackupError("unexpected_content")
            for chunk in response.iter_content(65536):
                total += len(chunk)
                if total > max_bytes:
                    raise FritzBackupError("too_large")
                chunks.append(chunk)
        data = b"".join(chunks)
        if len(data) < 16:
            raise FritzBackupError("empty")
        return data

    def _action(self, service: str, action: str, **arguments: Any) -> None:
        with self._lock:
            if self._fc is None:
                self._connect_locked()
            try:
                self._call(service, action, **arguments)
            except FritzAuthorizationError as ex:
                self._fc = None
                raise FritzInvalidAuth(str(ex)) from ex
            except (RequestException, OSError) as ex:
                # Beim Neustart bricht die Verbindung oft mitten in der Antwort ab.
                if action == "Reboot":
                    self._fc = None
                    return
                self._fc = None
                raise FritzCannotConnect(str(ex)) from ex
            except _UNSUPPORTED + _REFUSED as ex:
                raise FritzActionFailed(type(ex).__name__) from ex
            except FritzConnectionException as ex:
                raise FritzActionFailed(type(ex).__name__) from ex
