# SHA256 (Inhalt ab Zeile 2, d.h. dieser Datei ohne diese erste Zeile): f62b1c2a5c34e09bea7df7fcae447373c6ea544a3262e7938330a3f4242a3ab5
"""Lesender Zugriff auf die FRITZ!Box-Weboberfläche (nur CPU-Temperatur). EXPERIMENTELL.

Dieses Modul spricht NICHT TR-064, sondern die Weboberfläche der Box
(``login_sid.lua`` und ``data.lua``, Seite ``ecoStat``). Das ist von AVM nicht für
Dritte dokumentiert und kann sich mit jeder FRITZ!OS-Version ändern. Anmeldeablauf
und Auswertung sind aus der Integration „FRITZ!Box Netzwerk“ übernommen, bei der die
CPU-Temperatur an einer echten Box funktioniert. Fehler führen nur dazu, dass der
Wert fehlt.

Die Sitzungs-ID wird wiederverwendet: Jede neue Anmeldung an der Weboberfläche
meldet die Box sonst als „Änderungsnotiz - Anmeldung“ (Push/E-Mail).

Das Modul enthält weder Home-Assistant- noch fritzconnection-Importe und ist mit
Attrappen prüfbar. Alle Methoden blockieren und gehören in den Executor.
"""

from __future__ import annotations

import hashlib
import logging
import re
import threading
import time
import xml.etree.ElementTree as ET
from typing import Any
from urllib.parse import urlsplit

import requests

_LOGGER = logging.getLogger(__name__)

EMPTY_SID = "0000000000000000"
TIMEOUT = 10
# Die Box beendet ungenutzte Sitzungen nach 20 Minuten; darunter bleibt die Wiederverwendung
# (``login_sid.lua`` sagt vor jeder Nutzung, ob die Sitzung noch gilt).
SESSION_REUSE_SECONDS = 15 * 60


class WebUiError(Exception):
    """Die Weboberfläche lieferte nichts Brauchbares. ``reason`` ist ein Kurzschlüssel."""

    def __init__(self, reason: str) -> None:
        super().__init__(reason)
        self.reason = reason


def web_bases(host: str, ssl: bool) -> list[str]:
    """Adressen der Weboberfläche (Standardports 80/443; der TR-064-Port gehört nicht dazu).

    Bei eingeschalteter verschlüsselter Verbindung zuerst HTTPS, dann HTTP; sonst nur HTTP.
    """
    if host.count(":") > 1 and "[" not in host and "//" not in host:
        name = host  # nackte IPv6-Adresse
    else:
        name = urlsplit(host if "//" in host else f"//{host}").hostname or host
    authority = f"[{name}]" if ":" in name else name
    http = f"http://{authority}"
    https = f"https://{authority}"
    return [https, http] if ssl else [http]


def solve_challenge(challenge: str, password: str) -> str:
    """Antwort auf eine ``login_sid.lua``-Challenge.

    Neues Verfahren (FRITZ!OS 7.24+): ``2$iter1$salt1$iter2$salt2`` mit zwei PBKDF2-Runden.
    Altes Verfahren: MD5 über ``challenge-password`` in UTF-16LE (Zeichen über U+00FF
    werden dort durch ``.`` ersetzt).
    """
    if challenge.startswith("2$"):
        try:
            _, iter1, salt1, iter2, salt2 = challenge.split("$")
            hash1 = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt1), int(iter1))
            hash2 = hashlib.pbkdf2_hmac("sha256", hash1, bytes.fromhex(salt2), int(iter2))
        except (ValueError, TypeError) as err:
            raise ValueError("Unbekanntes Challenge-Format") from err
        return f"{salt2}${hash2.hex()}"
    cleaned = "".join(ch if ord(ch) <= 255 else "." for ch in password)
    digest = hashlib.md5(f"{challenge}-{cleaned}".encode("utf-16le")).hexdigest()
    return f"{challenge}-{digest}"


def parse_session_info(text: str) -> dict[str, str]:
    """``SID``, ``Challenge`` und ``BlockTime`` aus der SessionInfo-XML."""
    try:
        root = ET.fromstring(text)
    except ET.ParseError as err:
        raise ValueError("Ungültige SessionInfo") from err
    return {tag: (root.findtext(tag) or "").strip() for tag in ("SID", "Challenge", "BlockTime")}


def _last_number(series: Any) -> float | None:
    """Letzter numerische Wert einer Zeitreihe (``None``, wenn keiner vorhanden)."""
    if not isinstance(series, (list, tuple)):
        return None
    for value in reversed(series):
        if isinstance(value, bool):
            continue
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str) and re.fullmatch(r"-?\d+(\.\d+)?", value.strip()):
            return float(value)
    return None


def parse_cpu_temperature(payload: Any) -> float | None:
    """CPU-Temperatur in °C aus der JSON-Antwort von ``data.lua`` (Seite ``ecoStat``).

    ``data.cputemp.series[0]`` ist der Verlauf, der letzte Wert der jüngste. Passt die
    Form nicht, ist das Ergebnis ``None``.
    """
    data = payload.get("data") if isinstance(payload, dict) else None
    block = data.get("cputemp") if isinstance(data, dict) else None
    series = block.get("series") if isinstance(block, dict) else None
    if not isinstance(series, list) or not series:
        return None
    value = _last_number(series[0])
    if value is None or not -40 <= value <= 150:
        return None
    return value


class WebUi:
    """Eine wiederverwendete, angemeldete Sitzung an der Weboberfläche einer Box."""

    def __init__(self, host: str, username: str | None, password: str | None, ssl: bool) -> None:
        self._bases = web_bases(host, ssl)
        self._user = username or ""
        self._password = password or ""
        self._session = requests.Session()
        # Wie fritzconnection: Boxen nutzen meist ein selbstsigniertes Zertifikat.
        self._session.verify = False
        self._lock = threading.Lock()
        self._base: str | None = None
        self._sid: str | None = None
        self._seen = 0.0

    # --- Anmeldung -----------------------------------------------------------------
    def _valid(self, base: str, sid: str) -> bool:
        response = self._session.get(
            f"{base}/login_sid.lua", params={"version": "2", "sid": sid}, timeout=TIMEOUT
        )
        if not response.ok:
            return False
        try:
            return parse_session_info(response.text)["SID"] == sid
        except ValueError:
            return False

    def _login_fresh(self, base: str) -> str:
        first = self._session.get(f"{base}/login_sid.lua", params={"version": "2"}, timeout=TIMEOUT)
        if not first.ok:
            raise WebUiError("web_http")
        info = parse_session_info(first.text)
        if info["SID"] and info["SID"] != EMPTY_SID:
            return info["SID"]
        if info["BlockTime"] not in ("", "0"):
            raise WebUiError("web_blocked")
        if not info["Challenge"]:
            raise WebUiError("web_login")
        answer = solve_challenge(info["Challenge"], self._password)
        second = self._session.post(
            f"{base}/login_sid.lua",
            params={"version": "2"},
            data={"username": self._user, "response": answer},
            timeout=TIMEOUT,
        )
        if not second.ok:
            raise WebUiError("web_http")
        sid = parse_session_info(second.text)["SID"]
        if not sid or sid == EMPTY_SID:
            raise WebUiError("web_login")
        return sid

    def _ensure(self, base: str) -> str:
        """Gemerkte Sitzung, wenn die Box sie noch kennt, sonst eine frische Anmeldung."""
        if (
            self._sid
            and self._base == base
            and time.monotonic() - self._seen < SESSION_REUSE_SECONDS
            and self._valid(base, self._sid)
        ):
            self._seen = time.monotonic()
            return self._sid
        self._sid = None
        sid = self._login_fresh(base)
        self._sid, self._base, self._seen = sid, base, time.monotonic()
        return sid

    # --- Abfrage -------------------------------------------------------------------
    def cpu_temperature(self) -> float | None:
        """CPU-Temperatur in °C. Wirft ``WebUiError`` mit Kurzschlüssel, sonst ``None`` ohne Wert."""
        with self._lock:
            error: WebUiError | None = None
            # Zuerst die zuletzt funktionierende Adresse.
            bases = sorted(self._bases, key=lambda b: 0 if b == self._base else 1)
            for base in bases:
                try:
                    sid = self._ensure(base)
                    form = {"xhr": "1", "sid": sid, "lang": "de", "page": "ecoStat", "no_sidrenew": ""}
                    response = self._session.post(f"{base}/data.lua", data=form, timeout=TIMEOUT)
                    if not response.ok:
                        self._sid = None
                        raise WebUiError("web_http")
                    try:
                        payload = response.json()
                    except ValueError as err:
                        self._sid = None
                        raise WebUiError("web_no_data") from err
                    value = parse_cpu_temperature(payload)
                    if value is None:
                        raise WebUiError("web_no_data")
                    return value
                except WebUiError as err:
                    error = err
                    if err.reason in ("web_login", "web_blocked", "web_no_data"):
                        # Die Box antwortet, der Fehler liegt nicht an der Adresse.
                        break
                except (requests.RequestException, OSError, ValueError) as err:
                    self._sid = None
                    _LOGGER.debug("Weboberfläche %s nicht lesbar: %s", base, type(err).__name__)
                    error = WebUiError("web_unreachable")
            raise error or WebUiError("web_unreachable")

    def close(self) -> None:
        """Sitzung beenden (best effort) und verwerfen."""
        with self._lock:
            sid, base = self._sid, self._base
            self._sid = None
            if sid and base:
                try:
                    self._session.get(
                        f"{base}/home/home.lua", params={"sid": sid, "logout": "1"}, timeout=TIMEOUT
                    )
                except Exception:  # noqa: BLE001 - Abmelden darf nie etwas kippen
                    pass
            self._session.close()
