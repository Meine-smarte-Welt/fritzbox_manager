# Experimentelle Funktionen – FRITZ!Box Manager

Stand: Version 0.0.3b1. Experimentelle Funktionen sind **standardmäßig aus**, ändern bei ausgeschaltetem Zustand nichts am Verhalten und sind **nicht an einer echten FRITZ!Box geprüft**.

## So schaltest du sie ein

1. *Einstellungen → Geräte & Dienste → FRITZ!Box Manager → Konfigurieren*: **Experimentelle Funktionen** (Hauptschalter) einschalten, dazu die einzelne Funktion (z. B. **Backup**).
2. In der Karte (YAML oder grafischer Editor) `show_experimental: true` setzen. Erst dann erscheint im Einstellungs-Tab der Bereich *Experimentell*.

Das Backend arbeitet nur, wenn Hauptschalter **und** Einzelschalter an sind; sonst verweigert es die Aktion mit einem Hinweis.

## Übersicht

| Funktion | Seit | Schalter | Status |
|---|---|---|---|
| Backup der Box-Einstellungen | 0.0.2b1 | `backup_enabled` | experimentell, ungeprüft an echter Box |
| CPU-Temperatur | 0.0.1b0 | Option „CPU-Temperatur“ (Abschnitt *Optionale Einstellungen*) | experimentell, in 0.0.3b1 umgebaut (Weboberfläche statt TR-064), ungeprüft in diesem Projekt; hängt nicht am Hauptschalter |
| WLAN im HTTP-Modus (Änderung, kein Schalter) | 0.0.3b1 | – | ungeprüft: tolerantere Abfrage und Rückfall auf die verschlüsselte TR-064-Schnittstelle |

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

## CPU-Temperatur (umgebaut in 0.0.3b1)

**Was sich geändert hat:** Der Wert kommt nicht mehr aus TR-064 (`get_cpu_temperatures`), sondern wie bei *FRITZ!Box Netzwerk* aus der Weboberfläche der Box (`login_sid.lua`, `data.lua`, Seite `ecoStat`, Reihe `cputemp`). Die Sitzungs-ID wird bis zu 15 Minuten wiederverwendet, damit die Box nicht bei jeder Abfrage eine Anmeldung meldet. Es wird zuerst `http://<Adresse>` genutzt, bei eingeschalteter verschlüsselter Verbindung zuerst `https://<Adresse>`.

**Warum ungeprüft:** Anmeldung und Auswertung sind aus der Netzwerk-Integration übernommen, bei der der Wert an einer echten Box funktioniert. In diesem Projekt wurde er nur gegen eine simulierte Weboberfläche geprüft.

### Testschritte

1. *Konfigurieren → Optionale Einstellungen → CPU-Temperatur* einschalten (oder in der Karte unter *Einstellungen → Optionen → Optionale Einstellungen*).
2. Nach spätestens einem Abfrageintervall erscheint in der Karte (*Box → Informationen*) die CPU-Temperatur und der Sensor *CPU-Temperatur*.
3. Zeigt die Karte unter *Einstellungen → Verbindung* einen Eintrag `cpu: …`: `web_login` = Anmeldung abgelehnt (Benutzer braucht Zugriff auf die Weboberfläche), `web_blocked` = Anmeldung vorübergehend gesperrt, `web_unreachable` = Weboberfläche nicht erreichbar, `web_http` / `web_no_data` = unerwartete Antwort.
4. Bitte melden: Modell, FRITZ!OS, ob der Wert stimmt (Vergleich mit *FRITZ!Box Netzwerk*).

## WLAN im HTTP-Modus (Änderung in 0.0.3b1)

**Beobachtung:** Mit „Verschlüsselte Verbindung (HTTPS)“ lädt die WLAN-Liste, ohne nicht. Die genaue Ursache ist **nicht bestätigt**.

**Änderung:** Pflicht ist nur noch die Grundabfrage je Netz (`GetInfo`); Zusatzangaben (Geräteanzahl, Band) dürfen fehlen, ohne dass die ganze Liste leer wird. Verweigert die Box die unverschlüsselte Abfrage, wird einmal über die verschlüsselte Schnittstelle (Port 49443, gleiche Adresse und Zugangsdaten) gelesen; dasselbe gilt für das Ein-/Ausschalten.

### Testschritte

1. Verbindung **ohne** HTTPS einrichten, Karte → *WLAN* öffnen.
2. Erwartet: alle Netze erscheinen. Sonst: Grund unter *Einstellungen → Verbindung* (`wlan: …`) und Diagnose-Download melden.
3. Ein Gastnetz aus- und wieder einschalten (HTTP-Modus).

## Backup und Zwei-Faktor-Bestätigung

Die Backup-Funktion ist unverändert. Verlangt die Box für die Sicherung eine zusätzliche Bestätigung (Zwei-Faktor, z. B. per Authenticator-App, DECT-Telefon oder Tastendruck an der Box), wird die Anfrage von der Box abgelehnt; die Karte zeigt dann in der Regel den Grund *refused* (genau prüfbar ist das nur an der echten Box). Eine Bestätigung über die Schnittstelle der Box (`X_AVM-DE_Auth`) ist **nicht** eingebaut, weil die Beschreibung von AVM hier nicht abrufbar war. Eine Freigabe deines Routers für Claude ist dafür nicht nötig.

## Offene Frage

Die CPU-Temperatur ist seit 0.0.1b0 experimentell, hängt aber an einer eigenen Option und nicht am Hauptschalter. Soll sie in die Experimentell-Registry wechseln? Außerdem: Du hast geschrieben, dass das WLAN im HTTPS-Modus funktioniert und die CPU-Temperatur in *FRITZ!Box Netzwerk*. Soll die WLAN-Anzeige im HTTPS-Modus als „geprüft“ geführt werden?
