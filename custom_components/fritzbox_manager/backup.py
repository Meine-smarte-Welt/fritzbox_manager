# SHA256 (Inhalt ab Zeile 2, d.h. dieser Datei ohne diese erste Zeile): 20fd16914b861997995a5928308ae7c79020d819fa9655021d960b7c0261c305
"""Ablage der FRITZ!Box-Backups (EXPERIMENTELL).

Die Dateien liegen in einem festen Unterordner des Home-Assistant-Konfigurations-
ordners. Es werden nur eigene Dateien angelegt, gelistet und (beim Aufräumen) gelöscht:
Namen sind bereinigt, ein Pfad lässt sich nicht einschleusen, Verknüpfungen werden
ignoriert und gelöscht wird nur, was dem eigenen Namensschema entspricht.
Alle Funktionen blockieren und gehören in den Executor.
"""

from __future__ import annotations

from datetime import datetime, timezone
import logging
import os
from pathlib import Path
import re
from typing import Any

from .const import BACKUP_SUFFIX

_LOGGER = logging.getLogger(__name__)

_UNSAFE = re.compile(r"[^A-Za-z0-9._-]+")
# <Modell>_<Firmware>_<JJJJ-MM-TT>_<HH-MM-SS>[_<Zähler>].export
_OWN_NAME = re.compile(
    r"^[A-Za-z0-9._-]+_\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}(?:_\d{1,3})?" + re.escape(BACKUP_SUFFIX) + r"$"
)
MAX_LISTED = 200


def _part(text: str | None, fallback: str) -> str:
    cleaned = _UNSAFE.sub("_", (text or "").strip()).strip("._-")
    return cleaned[:40] or fallback


def backup_filename(model: str | None, firmware: str | None, when: datetime) -> str:
    """Dateiname aus Modell, Firmware und Zeit (nur sichere Zeichen)."""
    stamp = when.strftime("%Y-%m-%d_%H-%M-%S")
    return f"{_part(model, 'FRITZBox')}_{_part(firmware, 'fw')}_{stamp}{BACKUP_SUFFIX}"


def _free_name(directory: Path, filename: str) -> str:
    """Bei gleicher Sekunde einen Zähler anhängen, damit nie etwas überschrieben wird."""
    if not (directory / filename).exists():
        return filename
    stem = filename[: -len(BACKUP_SUFFIX)]
    for counter in range(2, 1000):
        candidate = f"{stem}_{counter}{BACKUP_SUFFIX}"
        if not (directory / candidate).exists():
            return candidate
    raise OSError("Kein freier Dateiname")


def write_backup(directory: Path, filename: str, data: bytes) -> str:
    """Backup anlegen (Rechte 0600, Ordner 0700). Gibt den tatsächlichen Dateinamen zurück."""
    if Path(filename).name != filename or not filename.endswith(BACKUP_SUFFIX):
        raise OSError("Ungültiger Dateiname")
    directory.mkdir(mode=0o700, parents=True, exist_ok=True)
    name = _free_name(directory, filename)
    target = directory / name
    temp = directory / f".{name}.tmp"
    fd = os.open(temp, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp, target)
    except BaseException:
        try:
            temp.unlink()
        except OSError:
            pass
        raise
    return name


def list_backups(directory: Path) -> list[dict[str, Any]]:
    """Vorhandene Backups, neueste zuerst. Ein fehlender Ordner ergibt eine leere Liste."""
    result: list[dict[str, Any]] = []
    try:
        entries = list(os.scandir(directory))
    except FileNotFoundError:
        return []
    except OSError as ex:
        _LOGGER.debug("Backup-Ordner nicht lesbar: %s", type(ex).__name__)
        return []
    for entry in entries:
        if not entry.name.endswith(BACKUP_SUFFIX) or entry.is_symlink() or not entry.is_file():
            continue
        try:
            stat = entry.stat()
        except OSError:
            continue
        result.append(
            {
                "name": entry.name,
                "size": stat.st_size,
                "modified": datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat(),
                "_mtime": stat.st_mtime,
            }
        )
    result.sort(key=lambda item: (item["_mtime"], item["name"]), reverse=True)
    for item in result:
        del item["_mtime"]
    return result[:MAX_LISTED]


def prune_backups(directory: Path, keep: int) -> int:
    """Älteste eigene Backups löschen, sodass höchstens ``keep`` bleiben. Gibt die Anzahl zurück."""
    keep = max(1, int(keep))
    own = [item for item in list_backups(directory) if _OWN_NAME.match(item["name"])]
    removed = 0
    for item in own[keep:]:
        try:
            (directory / item["name"]).unlink()
            removed += 1
        except OSError as ex:
            _LOGGER.debug("Altes Backup nicht löschbar: %s", type(ex).__name__)
    return removed
