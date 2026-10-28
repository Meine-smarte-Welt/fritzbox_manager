# SHA256 (Inhalt ab Zeile 2, d.h. dieser Datei ohne diese erste Zeile): a158e71b10ff288ffd0d8345812384d6211b6f3eed14401b3784b747200c389f
"""Versionsabfrage gegen GitHub (Pflicht laut Design-Master, Abschnitt 6).

Fragt beim ersten Aufruf und danach höchstens alle 12 Stunden
``api.github.com/repos/<Besitzer>/<Repo>/releases/latest`` ab, ersatzweise das
höchste Versions-Tag. Läuft eine Beta/ein Release Candidate, wird zusätzlich
die Liste der letzten Releases geprüft, weil ``releases/latest`` keine
Pre-releases liefert. Schlägt die Abfrage fehl, läuft die Integration normal
weiter (``check_failed`` = True).
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
import logging
import re
from typing import Any

import aiohttp

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import GITHUB_RELEASES_URL, GITHUB_REPO, VERSION

_LOGGER = logging.getLogger(__name__)

CHECK_INTERVAL = timedelta(hours=12)
_API = "https://api.github.com/repos/{repo}"
_VERSION_RE = re.compile(r"^v?(\d+(?:\.\d+)*)(?:(a|b|rc)(\d+))?")
_STAGE = {"a": 0, "b": 1, "rc": 2}


def version_tuple(text: str | None) -> tuple[int, ...]:
    """``"v0.0.1b0"`` → ``(0, 0, 1, 1, 0)``; unlesbar → ``()``.

    Beta und Release Candidate sortieren vor dem fertigen Release.
    """
    match = _VERSION_RE.match((text or "").strip())
    if not match:
        return ()
    numbers = [int(part) for part in match.group(1).split(".")]
    numbers = (numbers + [0, 0, 0])[: max(3, len(numbers))]
    stage = (_STAGE[match.group(2)], int(match.group(3))) if match.group(2) else (3, 0)
    return (*numbers, *stage)


def is_prerelease_version(text: str | None) -> bool:
    """True bei Versionen mit Beta-/RC-Kennung (z. B. ``0.0.1b0``)."""
    match = _VERSION_RE.match((text or "").strip())
    return bool(match and match.group(2))


def is_newer(latest: str | None, current: str | None) -> bool:
    """True, wenn ``latest`` eine höhere Version als ``current`` ist."""
    a, b = version_tuple(latest), version_tuple(current)
    return bool(a) and bool(b) and a > b


def safe_release_url(url: str | None) -> str:
    """Nur GitHub-Links anzeigen, sonst die feste Releases-Seite."""
    if isinstance(url, str) and url.startswith("https://github.com/"):
        return url
    return GITHUB_RELEASES_URL


class UpdateChecker:
    """Hält das Ergebnis der Versionsprüfung und aktualisiert es höchstens alle 12 h."""

    def __init__(self, hass: HomeAssistant) -> None:
        self._hass = hass
        self._info: dict[str, Any] = {
            "version": VERSION,
            "latest_version": None,
            "release_url": GITHUB_RELEASES_URL,
            "update_available": False,
            "checked_at": None,
            "check_failed": False,
        }
        self._last_try: datetime | None = None

    @property
    def info(self) -> dict[str, Any]:
        """Letztes bekanntes Ergebnis (ohne Netzwerkzugriff)."""
        return dict(self._info)

    async def async_info(self, force: bool = False) -> dict[str, Any]:
        """Info liefern; fragt GitHub nur, wenn nötig (oder ``force``)."""
        now = datetime.now(timezone.utc)
        if force or self._last_try is None or now - self._last_try >= CHECK_INTERVAL:
            self._last_try = now
            await self._async_check(now)
        return self.info

    async def _async_check(self, now: datetime) -> None:
        session = async_get_clientsession(self._hass)
        base = _API.format(repo=GITHUB_REPO)
        headers = {"Accept": "application/vnd.github+json"}
        latest: str | None = None
        url: str | None = None
        failed = False
        try:
            async with session.get(
                f"{base}/releases/latest",
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=15),
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    latest = str(data.get("tag_name") or "") or None
                    url = data.get("html_url")
                elif response.status == 404:
                    # Noch kein normales Release (z. B. nur Pre-releases).
                    latest, url = await self._async_latest_tag(session, base, headers)
                else:
                    failed = True
            if not failed and is_prerelease_version(VERSION):
                pre_latest, pre_url = await self._async_latest_release(session, base, headers)
                if pre_latest and version_tuple(pre_latest) > version_tuple(latest):
                    latest, url = pre_latest, pre_url
        except (aiohttp.ClientError, TimeoutError, ValueError) as ex:
            _LOGGER.debug("Versionsprüfung fehlgeschlagen: %s", ex)
            failed = True
        self._info.update(
            {
                "latest_version": latest.lstrip("v") if latest else self._info["latest_version"],
                "release_url": safe_release_url(url),
                "update_available": is_newer(latest, VERSION) if latest else False,
                "checked_at": now.isoformat(),
                "check_failed": failed or latest is None,
            }
        )

    @staticmethod
    async def _async_latest_release(
        session: aiohttp.ClientSession, base: str, headers: dict[str, str]
    ) -> tuple[str | None, str | None]:
        """Höchstes Release der letzten fünf (auch Pre-releases, keine Entwürfe)."""
        async with session.get(
            f"{base}/releases?per_page=5",
            headers=headers,
            timeout=aiohttp.ClientTimeout(total=15),
        ) as response:
            if response.status != 200:
                return None, None
            releases = [r for r in await response.json() if not r.get("draft")]
        releases = [r for r in releases if version_tuple(str(r.get("tag_name", "")))]
        if not releases:
            return None, None
        best = max(releases, key=lambda r: version_tuple(str(r["tag_name"])))
        return str(best["tag_name"]), best.get("html_url")

    @staticmethod
    async def _async_latest_tag(
        session: aiohttp.ClientSession, base: str, headers: dict[str, str]
    ) -> tuple[str | None, str | None]:
        """Ersatzweg: höchstes Versions-Tag, falls es kein Release gibt."""
        async with session.get(
            f"{base}/tags", headers=headers, timeout=aiohttp.ClientTimeout(total=15)
        ) as response:
            if response.status != 200:
                return None, None
            tags = [str(tag.get("name", "")) for tag in await response.json()]
        tags = [tag for tag in tags if version_tuple(tag)]
        if not tags:
            return None, None
        best = max(tags, key=version_tuple)
        return best, f"https://github.com/{GITHUB_REPO}/releases/tag/{best}"
