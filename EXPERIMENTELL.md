# Experimentelle Funktionen – FRITZ!Box Manager

Stand: Version 0.0.2b1. Experimentelle Funktionen sind **standardmäßig aus**, ändern bei ausgeschaltetem Zustand nichts am Verhalten und sind **nicht an einer echten FRITZ!Box geprüft**.

## So schaltest du sie ein

1. *Einstellungen → Geräte & Dienste → FRITZ!Box Manager → Konfigurieren*: **Experimentelle Funktionen** (Hauptschalter) einschalten, dazu die einzelne Funktion (z. B. **Backup**).
2. In der Karte (YAML oder grafischer Editor) `show_experimental: true` setzen. Erst dann erscheint im Einstellungs-Tab der Bereich *Experimentell*.

Das Backend arbeitet nur, wenn Hauptschalter **und** Einzelschalter an sind; sonst verweigert es die Aktion mit einem Hinweis.

## Übersicht

| Funktion | Seit | Schalter | Status |
|---|---|---|---|
| Backup der Box-Einstellungen | 0.0.2b1 | `backup_enabled` | experimentell, ungeprüft an echter Box |
| CPU-Temperatur | 0.0.1b0 | Option „CPU-Temperatur“ | experimentell, unverändert (hängt nicht am Hauptschalter) |

## Backup

**Was es tut:** Die Karte (Einstellungen → Experimentell → *Backup jetzt erstellen*) oder der Service `fritzbox_manager.create_backup` bittet die Box über TR-064 (`DeviceConfig1` / `X_AVM-DE_GetConfigFile`) um eine Sicherung der Einstellungen. Du vergibst dafür ein Kennwort; es wird nur für diesen Aufruf an die Box gesendet, **nicht gespeichert und nicht protokolliert**. Die Datei landet unter `config/fritzbox_manager_backups/` als `<Modell>_<Firmware>_<Datum>_<Zeit>.export` (Rechte 0600). Es werden höchstens so viele eigene Backups behalten, wie unter *Anzahl aufbewahrter Backups* (1–50, Standard 10) eingestellt ist; ältere eigene Dateien werden gelöscht.

**Was es nicht tut:** Es spielt nichts zurück. Das Einspielen geschieht an der Box unter *System → Sicherung*, mit dem vergebenen Kennwort. Das Dateiformat wird nicht geprüft (nur Größe und dass es keine HTML-Seite ist).

**Absicherung:** nur Administratoren; Download nur vom konfigurierten Host, ohne Weiterleitungen; Größenlimit 64 MiB; Dateiname bereinigt.

### Testschritte (bitte an deiner Box durchführen)

1. Schalter wie oben einschalten, Home Assistant ggf. neu laden, Browser mit Strg+F5.
2. Benutzer der Integration: Recht **FRITZ!Box Einstellungen** vorhanden? Ist eine Zwei-Faktor-Bestätigung für Einstellungsänderungen aktiv, halte das Bestätigungsgerät bereit.
3. Kennwort eintragen (die Box kann bestimmte Zeichen ablehnen; Fehlergründe siehe unten), *Backup jetzt erstellen*.
4. Erwartet: Banner „Backup läuft …“, danach Meldung und ein Eintrag in der Liste; Datei im Ordner `fritzbox_manager_backups`. Ereignis `fritzbox_manager_backup_created`.
5. Gegenprobe: Datei an der Box unter *System → Sicherung → Wiederherstellen* nur prüfen, wenn du das bewusst willst.
6. Bitte melden: Modell, FRITZ!OS, ob es klappte, sonst den angezeigten Fehlergrund und den Diagnose-Download.

### Mögliche Fehlergründe

Kennwort zu kurz/lang/ungültige Zeichen, fehlende Rechte, Dienst nicht unterstützt, Box lehnt ab („Internal Server Error“, z. B. wegen Zwei-Faktor oder Rechten), HTTP-Fehler, unerwarteter Inhalt, Datei zu groß oder leer.

## Offene Frage

Die CPU-Temperatur ist seit 0.0.1b0 experimentell, hängt aber an einer eigenen Option und nicht am neuen Hauptschalter. Soll sie in die Experimentell-Registry wechseln?
